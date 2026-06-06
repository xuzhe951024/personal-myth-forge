import Foundation
import PersonalMythForgeMobileCore

do {
    try testDecodesObjectCaptureFixture()
    try testDecodesMythSessionFixture()
    try testCaptureIDValidation()
    try testMultipartBodyIncludesMetadataAndFileWithoutLocalPaths()
    try testMultipartBuilderSanitizesHeaderValues()
    try await testUploadObjectCaptureBuildsMultipartRequest()
    try await testCreateMythSessionFromCaptureBuildsJSONRequest()
    try await testInvalidCaptureIDFailsBeforeNetwork()
    try await testHTTPStatusErrorIncludesStatusAndBody()
    try await testHTTPStatusErrorSanitizesSecretsAndTruncatesBody()
    try await testUploadObjectCaptureUsesGeneratedFilenamesWithoutLocalPaths()
    try await testUploadObjectCaptureRejectsUnsafeContentTypeBeforeNetwork()
    try await testUploadObjectCaptureBuildsARKitScanMultipartRequest()
    try testCaptureDraftBuildsSinglePhotoPayload()
    try testCaptureDraftBuildsPhotoSetPayload()
    try testCaptureDraftBuildsARKitScanPayload()
    try testCaptureDraftRejectsInvalidMedia()
    try testCaptureDraftRejectsOversizedMedia()
    try testCaptureMediaSelectionSummarizesSinglePhoto()
    try testCaptureMediaSelectionRequiresPhotoSetCount()
    try testCaptureMediaSelectionBuildsARKitDraft()
    try testCaptureMediaSelectionClearsWhenModeChanges()
    try testArtifactPreviewStateMarksRemoteGLBAsGeneratedAsset()
    try testArtifactPreviewStateMarksLocalUSDZAsSceneLoadable()
    try testArtifactPreviewStateHandlesMissingURI()
    try testArtifactPreviewStateHandlesMissingFormat()
    try await testArtifactAssetPreparerUsesLocalSceneURL()
    try await testArtifactAssetPreparerDownloadsRemoteUSDZForSceneKit()
    try await testArtifactAssetPreparerCachesRemoteGLBButRequiresConversion()
    try await testArtifactAssetPreparerRejectsInvalidRemoteURI()
    try testForgeFlowReducerTransitionsThroughReadyAndReset()
    try await testForgeFlowServiceUploadsCaptureThenCreatesSession()
    try await testForgeFlowServiceStopsBeforeSessionWhenUploadFails()
    try await testForgeFlowServiceRejectsInvalidDraftBeforeNetwork()
    try testSwiftUIScaffoldIncludesWorldResolution()
    print("PersonalMythForgeMobileCoreContractTests passed")
} catch {
    fputs("Contract test failed: \(error)\n", stderr)
    exit(1)
}

private func testDecodesObjectCaptureFixture() throws {
    let capture = try FixtureLoader.decode(ObjectCapture.self, from: "object-capture-response")

    try expectEqual(capture.captureId, "cap_ba02a3816bd145b4")
    try expectEqual(capture.mediaItems.first?.uri, "local-capture://cap_ba02a3816bd145b4/media_0.jpg")
    try expectEqual(capture.objectObservation.label, "old brass key")
}

private func testDecodesMythSessionFixture() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")

    try expectEqual(session.status, "ready_for_review")
    try expectEqual(session.objectCard.label, "old brass key")
    try expectEqual(session.npcReactions.count, 3)
    try expectEqual(session.worldResolution.acceptedActions.count, 2)
    try expectEqual(session.printCandidate.requiresUserApproval, true)
}

private func testCaptureIDValidation() throws {
    try expectTrue(CaptureID.isValid("cap_0123456789abcdef"))
    try expectFalse(CaptureID.isValid("cap_example"))
    try expectFalse(CaptureID.isValid(".."))
    try expectFalse(CaptureID.isValid("cap_0123456789abcdeg"))
}

private func testMultipartBodyIncludesMetadataAndFileWithoutLocalPaths() throws {
    var builder = MultipartFormDataBuilder(boundary: "pmf-boundary")
    let metadata = ObjectCaptureMetadata(
        label: "old brass key",
        materials: ["metal", "brass"],
        source: "phone_capture",
        captureMode: "single_photo",
        visualNotes: "worn teeth"
    )
    try builder.appendJSONField(name: "metadata_json", value: metadata)
    builder.appendFile(
        fieldName: "files",
        filename: "media_0.jpg",
        contentType: "image/jpeg",
        data: Data("fake-jpeg".utf8)
    )

    let body = String(decoding: builder.build(), as: UTF8.self)

    try expectContains(body, "name=\"metadata_json\"")
    try expectContains(body, "\"capture_mode\":\"single_photo\"")
    try expectContains(body, "filename=\"media_0.jpg\"")
    try expectContains(body, "Content-Type: image/jpeg")
    try expectNotContains(body, "/Users/")
}

private func testMultipartBuilderSanitizesHeaderValues() throws {
    var builder = MultipartFormDataBuilder(boundary: "pmf-boundary")
    builder.appendFile(
        fieldName: "files\r\nX-Injected: 1",
        filename: "../../secret.jpg\r\nX-Injected: 1",
        contentType: "image/jpeg\r\nX-Injected: 1",
        data: Data("fake-jpeg".utf8)
    )

    let body = String(decoding: builder.build(), as: UTF8.self)

    try expectContains(body, "name=\"files\"")
    try expectContains(body, "filename=\"secret.jpg\"")
    try expectContains(body, "Content-Type: application/octet-stream")
    try expectNotContains(body, "X-Injected")
    try expectNotContains(body, "../")
    try expectNotContains(body, "\r\nX-Injected")
}

private func testUploadObjectCaptureBuildsMultipartRequest() async throws {
    let transport = RecordingTransport(
        responses: [
            try HTTPResponse(statusCode: 200, data: FixtureLoader.data(from: "object-capture-response"))
        ]
    )
    let client = PersonalMythForgeAPIClient(
        baseURL: URL(string: "http://127.0.0.1:8080")!,
        transport: transport,
        boundaryFactory: { "test-boundary" }
    )

    let capture = try await client.uploadObjectCapture(
        metadata: sampleMetadata(),
        media: [
            CaptureUpload(
                filename: "media_0.jpg",
                contentType: "image/jpeg",
                data: Data("fake-jpeg".utf8)
            )
        ]
    )

    try expectEqual(capture.captureId, "cap_ba02a3816bd145b4")
    try expectEqual(transport.requests.count, 1)
    let request = try require(transport.requests.first, "missing upload request")
    try expectEqual(request.httpMethod, "POST")
    try expectEqual(request.url?.path, "/v1/object-captures")
    try expectContains(request.value(forHTTPHeaderField: "Content-Type") ?? "", "multipart/form-data; boundary=test-boundary")
    try expectContains(String(decoding: request.httpBody ?? Data(), as: UTF8.self), "\"label\":\"old brass key\"")
}

private func testCreateMythSessionFromCaptureBuildsJSONRequest() async throws {
    let transport = RecordingTransport(
        responses: [
            try HTTPResponse(statusCode: 200, data: FixtureLoader.data(from: "myth-session-response"))
        ]
    )
    let client = PersonalMythForgeAPIClient(
        baseURL: URL(string: "http://127.0.0.1:8080")!,
        transport: transport
    )

    let session = try await client.createMythSessionFromCapture(
        captureId: "cap_ba02a3816bd145b4",
        context: sampleContext()
    )

    try expectEqual(session.status, "ready_for_review")
    let request = try require(transport.requests.first, "missing session request")
    try expectEqual(request.httpMethod, "POST")
    try expectEqual(request.url?.path, "/v1/myth-sessions/from-capture")
    try expectEqual(request.value(forHTTPHeaderField: "Content-Type"), "application/json")
    try expectContains(String(decoding: request.httpBody ?? Data(), as: UTF8.self), "\"capture_id\":\"cap_ba02a3816bd145b4\"")
}

private func testInvalidCaptureIDFailsBeforeNetwork() async throws {
    let transport = RecordingTransport(responses: [])
    let client = PersonalMythForgeAPIClient(
        baseURL: URL(string: "http://127.0.0.1:8080")!,
        transport: transport
    )

    do {
        _ = try await client.createMythSessionFromCapture(captureId: "..", context: sampleContext())
        throw ContractTestError.expectationFailed("Expected invalid capture id error")
    } catch ForgeFlowError.invalidCaptureID("..") {
        try expectEqual(transport.requests.count, 0)
    }
}

private func testHTTPStatusErrorIncludesStatusAndBody() async throws {
    let transport = RecordingTransport(
        responses: [
            HTTPResponse(statusCode: 500, data: Data("provider failed".utf8))
        ]
    )
    let client = PersonalMythForgeAPIClient(
        baseURL: URL(string: "http://127.0.0.1:8080")!,
        transport: transport
    )

    do {
        _ = try await client.createMythSessionFromCapture(
            captureId: "cap_ba02a3816bd145b4",
            context: sampleContext()
        )
        throw ContractTestError.expectationFailed("Expected HTTP status error")
    } catch ForgeFlowError.httpStatus(500, "provider failed") {
        try expectEqual(transport.requests.count, 1)
    }
}

private func testHTTPStatusErrorSanitizesSecretsAndTruncatesBody() async throws {
    let secret = "test-secret"
    let oversized = String(repeating: "x", count: 900)
    let body = "Authorization=Bearer \(secret) raw=\(secret) \(oversized)"
    let transport = RecordingTransport(
        responses: [
            HTTPResponse(statusCode: 502, data: Data(body.utf8))
        ]
    )
    let client = PersonalMythForgeAPIClient(
        baseURL: URL(string: "http://127.0.0.1:8080")!,
        transport: transport
    )

    do {
        _ = try await client.createMythSessionFromCapture(
            captureId: "cap_ba02a3816bd145b4",
            context: sampleContext()
        )
        throw ContractTestError.expectationFailed("Expected sanitized HTTP status error")
    } catch ForgeFlowError.httpStatus(502, let sanitizedBody) {
        try expectFalse(sanitizedBody.contains(secret))
        try expectContains(sanitizedBody, "Authorization=Bearer [redacted]")
        try expectContains(sanitizedBody, "raw=[redacted]")
        try expectContains(sanitizedBody, "[truncated]")
        try expectTrue(sanitizedBody.count <= 530)
    }
}

private func testUploadObjectCaptureUsesGeneratedFilenamesWithoutLocalPaths() async throws {
    let transport = RecordingTransport(
        responses: [
            try HTTPResponse(statusCode: 200, data: FixtureLoader.data(from: "object-capture-response"))
        ]
    )
    let client = PersonalMythForgeAPIClient(
        baseURL: URL(string: "http://127.0.0.1:8080")!,
        transport: transport,
        boundaryFactory: { "test-boundary" }
    )

    _ = try await client.uploadObjectCapture(
        metadata: sampleMetadata(),
        media: [
            CaptureUpload(
                filename: "/Users/zhexu/Desktop/../../secret.jpg",
                contentType: "image/jpeg",
                data: Data("fake-jpeg".utf8)
            )
        ]
    )

    let request = try require(transport.requests.first, "missing upload request")
    let body = String(decoding: request.httpBody ?? Data(), as: UTF8.self)
    try expectContains(body, "filename=\"media_0.jpg\"")
    try expectNotContains(body, "/Users/")
    try expectNotContains(body, "../")
    try expectNotContains(body, "secret.jpg")
}

private func testUploadObjectCaptureRejectsUnsafeContentTypeBeforeNetwork() async throws {
    let transport = RecordingTransport(responses: [])
    let client = PersonalMythForgeAPIClient(
        baseURL: URL(string: "http://127.0.0.1:8080")!,
        transport: transport
    )

    do {
        _ = try await client.uploadObjectCapture(
            metadata: sampleMetadata(),
            media: [
                CaptureUpload(
                    filename: "media_0.jpg",
                    contentType: "image/jpeg\r\nX-Injected: 1",
                    data: Data("fake-jpeg".utf8)
                )
            ]
        )
        throw ContractTestError.expectationFailed("Expected unsafe content type error")
    } catch ForgeFlowError.encodingFailed(let message) {
        try expectContains(message, "Unsupported capture content type")
        try expectEqual(transport.requests.count, 0)
    }
}

private func testUploadObjectCaptureBuildsARKitScanMultipartRequest() async throws {
    let transport = RecordingTransport(
        responses: [
            try HTTPResponse(statusCode: 200, data: FixtureLoader.data(from: "object-capture-response"))
        ]
    )
    let client = PersonalMythForgeAPIClient(
        baseURL: URL(string: "http://127.0.0.1:8080")!,
        transport: transport,
        boundaryFactory: { "test-boundary" }
    )
    let draft = CaptureDraft(
        label: "small idol",
        materialsText: "stone",
        visualNotes: "rough LiDAR mesh",
        source: "phone_capture",
        mode: .arkitScan,
        media: [
            captureMedia(
                filename: "/Users/zhexu/Desktop/idol mesh.glb",
                contentType: "model/gltf-binary",
                kind: .scanAsset
            )
        ]
    )
    let payload = try draft.validatedUploadPayload()

    _ = try await client.uploadObjectCapture(
        metadata: payload.metadata,
        media: payload.uploads
    )

    let request = try require(transport.requests.first, "missing upload request")
    let body = String(decoding: request.httpBody ?? Data(), as: UTF8.self)
    try expectContains(body, "\"capture_mode\":\"arkit_scan\"")
    try expectContains(body, "filename=\"scan_0.glb\"")
    try expectContains(body, "Content-Type: model/gltf-binary")
    try expectNotContains(body, "/Users/")
    try expectNotContains(body, "idol mesh.glb")
}

private func testCaptureDraftBuildsSinglePhotoPayload() throws {
    let draft = CaptureDraft(
        label: " old brass key ",
        materialsText: " metal, brass,  ",
        visualNotes: " worn teeth ",
        source: "phone_capture",
        mode: .singlePhoto,
        media: [
            captureMedia(filename: "/Users/zhexu/key.jpg", contentType: "image/jpeg", kind: .image)
        ]
    )

    let payload = try draft.validatedUploadPayload()

    try expectEqual(payload.metadata.label, "old brass key")
    try expectEqual(payload.metadata.materials, ["metal", "brass"])
    try expectEqual(payload.metadata.captureMode, "single_photo")
    try expectEqual(payload.metadata.visualNotes, "worn teeth")
    try expectEqual(payload.uploads.count, 1)
    try expectEqual(payload.uploads[0].contentType, "image/jpeg")
}

private func testCaptureDraftBuildsPhotoSetPayload() throws {
    let draft = CaptureDraft(
        label: "moon cup",
        materialsText: "ceramic, glaze",
        visualNotes: "",
        source: "phone_capture",
        mode: .photoSet,
        media: [
            captureMedia(filename: "front.heic", contentType: "image/heic", kind: .image),
            captureMedia(filename: "side.png", contentType: "image/png", kind: .image),
        ]
    )

    let payload = try draft.validatedUploadPayload()

    try expectEqual(payload.metadata.captureMode, "photo_set")
    try expectTrue(payload.metadata.visualNotes == nil)
    try expectEqual(payload.uploads.count, 2)
    try expectEqual(payload.uploads.map(\.contentType), ["image/heic", "image/png"])
}

private func testCaptureDraftBuildsARKitScanPayload() throws {
    let draft = CaptureDraft(
        label: "small idol",
        materialsText: "stone",
        visualNotes: "rough LiDAR mesh with one reference photo",
        source: "phone_capture",
        mode: .arkitScan,
        media: [
            captureMedia(filename: "idol.glb", contentType: "model/gltf-binary", kind: .scanAsset),
            captureMedia(filename: "reference.jpg", contentType: "image/jpeg", kind: .image),
        ]
    )

    let payload = try draft.validatedUploadPayload()

    try expectEqual(payload.metadata.captureMode, "arkit_scan")
    try expectEqual(payload.uploads.count, 2)
    try expectEqual(payload.uploads[0].contentType, "model/gltf-binary")
    try expectEqual(payload.uploads[1].contentType, "image/jpeg")
}

private func testCaptureDraftRejectsInvalidMedia() throws {
    try expectCaptureDraftError(
        CaptureDraft(
            label: " ",
            materialsText: "",
            visualNotes: "",
            source: "phone_capture",
            mode: .singlePhoto,
            media: [captureMedia(filename: "key.jpg", contentType: "image/jpeg", kind: .image)]
        ),
        .missingLabel
    )
    try expectCaptureDraftError(
        CaptureDraft(
            label: "key",
            materialsText: "",
            visualNotes: "",
            source: "phone_capture",
            mode: .arkitScan,
            media: [captureMedia(filename: "reference.jpg", contentType: "image/jpeg", kind: .image)]
        ),
        .missingScanAsset
    )
    try expectCaptureDraftError(
        CaptureDraft(
            label: "key",
            materialsText: "",
            visualNotes: "",
            source: "phone_capture",
            mode: .photoSet,
            media: [captureMedia(filename: "front.jpg", contentType: "image/jpeg", kind: .image)]
        ),
        .invalidMediaCount(.photoSet, 1)
    )
    try expectCaptureDraftError(
        CaptureDraft(
            label: "key",
            materialsText: "",
            visualNotes: "",
            source: "phone_capture",
            mode: .singlePhoto,
            media: [captureMedia(filename: "key.txt", contentType: "text/plain", kind: .image)]
        ),
        .unsupportedContentType("text/plain")
    )
}

private func testCaptureDraftRejectsOversizedMedia() throws {
    let limit = CaptureDraft.maxFileBytes
    try expectCaptureDraftError(
        CaptureDraft(
            label: "small idol",
            materialsText: "stone",
            visualNotes: "",
            source: "phone_capture",
            mode: .arkitScan,
            media: [
                captureMedia(
                    filename: "oversized.glb",
                    contentType: "model/gltf-binary",
                    kind: .scanAsset,
                    data: Data(repeating: 0, count: limit + 1)
                )
            ]
        ),
        .mediaTooLarge(limit + 1, limit)
    )
}

private func testCaptureMediaSelectionSummarizesSinglePhoto() throws {
    let selection = CaptureMediaSelection(
        mode: .singlePhoto,
        media: [captureMedia(filename: "key.jpg", contentType: "image/jpeg", kind: .image)]
    )

    try expectTrue(selection.isReadyForUpload)
    try expectEqual(selection.imageCount, 1)
    try expectEqual(selection.scanAssetCount, 0)
    try expectEqual(selection.summary.title, "1 photo selected")
    try expectContains(selection.summary.detail, "key.jpg")
}

private func testCaptureMediaSelectionRequiresPhotoSetCount() throws {
    let onePhoto = CaptureMediaSelection(
        mode: .photoSet,
        media: [captureMedia(filename: "front.jpg", contentType: "image/jpeg", kind: .image)]
    )
    let twoPhotos = CaptureMediaSelection(
        mode: .photoSet,
        media: [
            captureMedia(filename: "front.jpg", contentType: "image/jpeg", kind: .image),
            captureMedia(filename: "side.png", contentType: "image/png", kind: .image),
        ]
    )

    try expectFalse(onePhoto.isReadyForUpload)
    try expectTrue(twoPhotos.isReadyForUpload)
    try expectEqual(twoPhotos.summary.title, "2 photos selected")
}

private func testCaptureMediaSelectionBuildsARKitDraft() throws {
    let selection = CaptureMediaSelection(
        mode: .arkitScan,
        media: [
            captureMedia(filename: "idol.glb", contentType: "model/gltf-binary", kind: .scanAsset),
            captureMedia(filename: "reference.jpg", contentType: "image/jpeg", kind: .image),
        ]
    )

    let draft = selection.captureDraft(
        label: "small idol",
        materialsText: "stone",
        visualNotes: "rough mesh",
        source: "phone_capture"
    )
    let payload = try draft.validatedUploadPayload()

    try expectTrue(selection.isReadyForUpload)
    try expectEqual(selection.scanAssetCount, 1)
    try expectEqual(selection.imageCount, 1)
    try expectEqual(payload.metadata.captureMode, "arkit_scan")
    try expectEqual(payload.uploads.map(\.contentType), ["model/gltf-binary", "image/jpeg"])
}

private func testCaptureMediaSelectionClearsWhenModeChanges() throws {
    let selection = CaptureMediaSelection(
        mode: .singlePhoto,
        media: [captureMedia(filename: "key.jpg", contentType: "image/jpeg", kind: .image)]
    )

    let changed = selection.changingMode(to: .manualUpload)

    try expectEqual(changed.mode, .manualUpload)
    try expectEqual(changed.media.count, 0)
    try expectFalse(changed.isReadyForUpload)
}

private func testForgeFlowReducerTransitionsThroughReadyAndReset() throws {
    let metadata = sampleMetadata()
    let context = sampleContext()
    let capture = try FixtureLoader.decode(ObjectCapture.self, from: "object-capture-response")
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")

    var state = ForgeFlowState()
    state = ForgeFlowReducer.reduce(state: state, event: .setObjectMetadata(metadata))
    try expectEqual(state.phase, .editingObject)
    try expectEqual(state.metadata, metadata)

    state = ForgeFlowReducer.reduce(state: state, event: .setContextCapsule(context))
    try expectEqual(state.phase, .editingObject)
    try expectEqual(state.context, context)

    state = ForgeFlowReducer.reduce(state: state, event: .beginUpload)
    try expectEqual(state.phase, .uploadingCapture)

    state = ForgeFlowReducer.reduce(state: state, event: .captureUploaded(capture))
    try expectEqual(state.phase, .creatingSession)
    try expectEqual(state.capture, capture)

    state = ForgeFlowReducer.reduce(state: state, event: .sessionCreated(session))
    try expectEqual(state.phase, .ready(session))

    state = ForgeFlowReducer.reduce(state: state, event: .requestFailed(.httpStatus(500, "redacted")))
    try expectEqual(state.phase, .failed(.httpStatus(500, "redacted")))

    state = ForgeFlowReducer.reduce(state: state, event: .reset)
    try expectEqual(state.phase, .idle)
    try expectTrue(state.metadata == nil)
    try expectTrue(state.context == nil)
    try expectTrue(state.capture == nil)
}

private func testForgeFlowServiceUploadsCaptureThenCreatesSession() async throws {
    let capture = try FixtureLoader.decode(ObjectCapture.self, from: "object-capture-response")
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let api = FakeForgeFlowAPI(uploadResult: .success(capture), sessionResult: .success(session))
    let service = ForgeFlowService(api: api)
    let snapshots = SnapshotRecorder()

    let finalState = await service.forge(
        draft: sampleCaptureDraft(),
        context: sampleContext()
    ) { state in
        snapshots.append(state)
    }

    try expectEqual(finalState.phase, .ready(session))
    try expectEqual(api.uploadedMetadata, sampleMetadata())
    try expectEqual(api.uploadedMedia.map(\.contentType), ["image/jpeg"])
    try expectEqual(api.sessionCaptureIds, ["cap_ba02a3816bd145b4"])
    try expectEqual(api.sessionContexts, [sampleContext()])
    try expectEqual(snapshots.values.map(\.phase), [
        .editingObject,
        .editingObject,
        .uploadingCapture,
        .creatingSession,
        .ready(session),
    ])
}

private func testForgeFlowServiceStopsBeforeSessionWhenUploadFails() async throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let api = FakeForgeFlowAPI(
        uploadResult: .failure(ForgeFlowError.httpStatus(413, "too large")),
        sessionResult: .success(session)
    )
    let service = ForgeFlowService(api: api)
    let snapshots = SnapshotRecorder()

    let finalState = await service.forge(
        draft: sampleCaptureDraft(),
        context: sampleContext()
    ) { state in
        snapshots.append(state)
    }

    try expectEqual(finalState.phase, .failed(.httpStatus(413, "too large")))
    try expectEqual(api.uploadedMedia.count, 1)
    try expectEqual(api.sessionCaptureIds, [])
    try expectEqual(snapshots.values.map(\.phase), [
        .editingObject,
        .editingObject,
        .uploadingCapture,
        .failed(.httpStatus(413, "too large")),
    ])
}

private func testForgeFlowServiceRejectsInvalidDraftBeforeNetwork() async throws {
    let capture = try FixtureLoader.decode(ObjectCapture.self, from: "object-capture-response")
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let api = FakeForgeFlowAPI(uploadResult: .success(capture), sessionResult: .success(session))
    let service = ForgeFlowService(api: api)

    let finalState = await service.forge(
        draft: CaptureDraft(
            label: " ",
            materialsText: "",
            visualNotes: "",
            source: "phone_capture",
            mode: .singlePhoto,
            media: [captureMedia(filename: "key.jpg", contentType: "image/jpeg", kind: .image)]
        ),
        context: sampleContext()
    )

    try expectEqual(api.uploadedMedia.count, 0)
    try expectEqual(api.sessionCaptureIds, [])
    if case let .failed(.invalidCaptureDraft(message)) = finalState.phase {
        try expectContains(message, "missingLabel")
    } else {
        throw ContractTestError.expectationFailed("Expected invalid capture draft failure, got \(finalState.phase)")
    }
}

private func testSwiftUIScaffoldIncludesWorldResolution() throws {
    let appRoot = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
        .appendingPathComponent("apps/mobile/ios/App")
    let rootView = try sourceFile("ForgeRootView.swift", in: appRoot)
    let worldView = try sourceFile("WorldResolutionView.swift", in: appRoot)

    try expectContains(rootView, "WorldResolutionView(session: readySession)")
    try expectContains(worldView, "session.worldResolution")
    try expectContains(worldView, "acceptedActions")
    try expectContains(worldView, "rejectedActions")
    try expectContains(worldView, "visibleChanges")
}

private func testArtifactPreviewStateMarksRemoteGLBAsGeneratedAsset() throws {
    let state = ArtifactPreviewState(
        session: mythSession(
            asset: generatedAsset(format: "glb", uri: "https://cdn.example.com/relic.glb")
        )
    )

    try expectEqual(state.title, "The Key That Remembered")
    try expectEqual(state.providerLabel, "meshy")
    try expectEqual(state.formatLabel, "GLB")
    try expectFalse(state.isSceneLoadable)
    try expectEqual(state.statusTitle, "Generated 3D asset ready")
    try expectContains(state.statusDetail, "download/import step")
}

private func testArtifactPreviewStateMarksLocalUSDZAsSceneLoadable() throws {
    let state = ArtifactPreviewState(
        session: mythSession(
            asset: generatedAsset(format: "usdz", uri: "file:///tmp/relic.usdz")
        )
    )

    try expectTrue(state.isSceneLoadable)
    try expectEqual(state.statusTitle, "Local scene asset ready")
    try expectContains(state.statusDetail, "SceneKit")
}

private func testArtifactPreviewStateHandlesMissingURI() throws {
    let state = ArtifactPreviewState(
        session: mythSession(
            asset: generatedAsset(format: "", uri: "")
        )
    )

    try expectFalse(state.isSceneLoadable)
    try expectEqual(state.formatLabel, "Unknown")
    try expectEqual(state.statusTitle, "Awaiting 3D asset")
}

private func testArtifactPreviewStateHandlesMissingFormat() throws {
    let state = ArtifactPreviewState(
        session: mythSession(
            asset: generatedAsset(format: "", uri: "https://cdn.example.com/relic")
        )
    )

    try expectFalse(state.isSceneLoadable)
    try expectEqual(state.formatLabel, "Unknown")
    try expectEqual(state.statusTitle, "Awaiting 3D asset format")
    try expectContains(state.statusDetail, "format")
}

private func testArtifactAssetPreparerUsesLocalSceneURL() async throws {
    let downloader = RecordingArtifactAssetDownloader()
    let cache = RecordingArtifactAssetCache(rootURL: URL(fileURLWithPath: "/tmp/pmf-assets"))
    let session = mythSession(
        asset: generatedAsset(format: "usdz", uri: "file:///tmp/relic.usdz")
    )
    let prepared = await ArtifactAssetPreparer(downloader: downloader, cache: cache)
        .prepare(session: session)

    try expectEqual(prepared.status, .localSceneReady)
    try expectEqual(prepared.sceneURL, URL(string: "file:///tmp/relic.usdz"))
    try expectEqual(prepared.cachedURL, URL(string: "file:///tmp/relic.usdz"))
    try expectEqual(await downloader.requestedURLs(), [])
    try expectEqual(await cache.storedFilenames(), [])
}

private func testArtifactAssetPreparerDownloadsRemoteUSDZForSceneKit() async throws {
    let downloader = RecordingArtifactAssetDownloader(data: Data("usdz-bytes".utf8))
    let cache = RecordingArtifactAssetCache(rootURL: URL(fileURLWithPath: "/tmp/pmf-assets"))
    let session = mythSession(
        asset: generatedAsset(format: "usdz", uri: "https://cdn.example.com/relic.usdz")
    )
    let prepared = await ArtifactAssetPreparer(downloader: downloader, cache: cache)
        .prepare(session: session)

    try expectEqual(prepared.status, .cachedSceneReady)
    try expectEqual(prepared.cachedURL, URL(fileURLWithPath: "/tmp/pmf-assets/myth_test-meshy.usdz"))
    try expectEqual(prepared.sceneURL, prepared.cachedURL)
    try expectEqual(await downloader.requestedURLs(), [URL(string: "https://cdn.example.com/relic.usdz")!])
    try expectEqual(await cache.storedFilenames(), ["myth_test-meshy.usdz"])
    try expectEqual(await cache.storedData(), [Data("usdz-bytes".utf8)])
}

private func testArtifactAssetPreparerCachesRemoteGLBButRequiresConversion() async throws {
    let downloader = RecordingArtifactAssetDownloader(data: Data("glb-bytes".utf8))
    let cache = RecordingArtifactAssetCache(rootURL: URL(fileURLWithPath: "/tmp/pmf-assets"))
    let session = mythSession(
        asset: generatedAsset(format: "glb", uri: "https://cdn.example.com/relic.glb")
    )
    let prepared = await ArtifactAssetPreparer(downloader: downloader, cache: cache)
        .prepare(session: session)

    try expectEqual(prepared.status, .cachedRequiresConversion)
    try expectEqual(prepared.cachedURL, URL(fileURLWithPath: "/tmp/pmf-assets/myth_test-meshy.glb"))
    try expectEqual(prepared.sceneURL, nil)
    try expectContains(prepared.statusDetail, "conversion")
    try expectEqual(await cache.storedFilenames(), ["myth_test-meshy.glb"])
}

private func testArtifactAssetPreparerRejectsInvalidRemoteURI() async throws {
    let downloader = RecordingArtifactAssetDownloader()
    let cache = RecordingArtifactAssetCache(rootURL: URL(fileURLWithPath: "/tmp/pmf-assets"))
    let session = mythSession(
        asset: generatedAsset(format: "usdz", uri: "not-a-remote-uri")
    )
    let prepared = await ArtifactAssetPreparer(downloader: downloader, cache: cache)
        .prepare(session: session)

    try expectEqual(prepared.status, .unsupportedURI)
    try expectEqual(prepared.cachedURL, nil)
    try expectEqual(prepared.sceneURL, nil)
    try expectEqual(await downloader.requestedURLs(), [])
    try expectEqual(await cache.storedFilenames(), [])
}

private func sampleCaptureDraft() -> CaptureDraft {
    CaptureDraft(
        label: "old brass key",
        materialsText: "metal, brass",
        visualNotes: "worn teeth",
        source: "phone_capture",
        mode: .singlePhoto,
        media: [captureMedia(filename: "key.jpg", contentType: "image/jpeg", kind: .image)]
    )
}

private func sampleMetadata() -> ObjectCaptureMetadata {
    ObjectCaptureMetadata(
        label: "old brass key",
        materials: ["metal", "brass"],
        source: "phone_capture",
        captureMode: "single_photo",
        visualNotes: "worn teeth"
    )
}

private func sampleContext() -> ContextCapsule {
    ContextCapsule(
        currentTheme: "deadline pressure",
        desiredTone: "tender, strange",
        recentMilestone: "finished a difficult project draft"
    )
}

private func captureMedia(
    filename: String,
    contentType: String,
    kind: CaptureMediaKind,
    data: Data = Data("capture-data".utf8)
) -> CaptureMediaDraft {
    CaptureMediaDraft(
        originalFilename: filename,
        contentType: contentType,
        data: data,
        kind: kind
    )
}

private func generatedAsset(format: String, uri: String) -> GeneratedAsset {
    GeneratedAsset(
        kind: "game_asset",
        provider: "meshy",
        format: format,
        uri: uri,
        prompt: "a brass key relic",
        moderationStatus: "approved"
    )
}

private func mythSession(asset: GeneratedAsset) -> MythSession {
    MythSession(
        sessionId: "myth_test",
        status: "ready",
        objectCard: ObjectCard(
            label: "old brass key",
            materials: ["brass"],
            source: "phone_capture",
            affordances: ["opens"],
            symbolicReading: "memory"
        ),
        mythSeed: MythSeed(
            title: "The Key That Remembered",
            personalResonance: "It holds a small deadline in its teeth.",
            generationPrompt: "a brass key relic"
        ),
        generatedAsset: asset,
        npcDirector: "local",
        npcReactions: [],
        worldResolution: WorldResolution(
            arbitrator: "local",
            summary: "The village gathers.",
            acceptedActions: [],
            rejectedActions: [],
            worldStateDelta: [:],
            visibleChanges: []
        ),
        printCandidate: PrintCandidate(
            kind: "print_asset",
            sourceAssetUri: asset.uri,
            provider: "local",
            format: "stl",
            uri: "local://print.stl",
            requiresUserApproval: true,
            approvalReason: "review",
            printabilityNotes: []
        )
    )
}

private enum FixtureLoader {
    static func data(from name: String) throws -> Data {
        guard let url = Bundle.module.url(forResource: name, withExtension: "json") else {
            throw ContractTestError.fixtureMissing(name)
        }
        return try Data(contentsOf: url)
    }

    static func decode<T: Decodable>(_ type: T.Type, from name: String) throws -> T {
        return try PMFJSON.decoder.decode(T.self, from: data(from: name))
    }
}

private final class RecordingTransport: HTTPTransport, @unchecked Sendable {
    private(set) var requests: [URLRequest] = []
    private var responses: [HTTPResponse]

    init(responses: [HTTPResponse]) {
        self.responses = responses
    }

    func send(_ request: URLRequest) async throws -> HTTPResponse {
        requests.append(request)
        if responses.isEmpty {
            throw ContractTestError.expectationFailed("No fake response queued")
        }
        return responses.removeFirst()
    }
}

private final class FakeForgeFlowAPI: ForgeFlowAPI, @unchecked Sendable {
    private let uploadResult: Result<ObjectCapture, Error>
    private let sessionResult: Result<MythSession, Error>
    private(set) var uploadedMetadata: ObjectCaptureMetadata?
    private(set) var uploadedMedia: [CaptureUpload] = []
    private(set) var sessionCaptureIds: [String] = []
    private(set) var sessionContexts: [ContextCapsule] = []

    init(uploadResult: Result<ObjectCapture, Error>, sessionResult: Result<MythSession, Error>) {
        self.uploadResult = uploadResult
        self.sessionResult = sessionResult
    }

    func uploadObjectCapture(metadata: ObjectCaptureMetadata, media: [CaptureUpload]) async throws -> ObjectCapture {
        uploadedMetadata = metadata
        uploadedMedia = media
        return try uploadResult.get()
    }

    func createMythSessionFromCapture(captureId: String, context: ContextCapsule) async throws -> MythSession {
        sessionCaptureIds.append(captureId)
        sessionContexts.append(context)
        return try sessionResult.get()
    }
}

private actor RecordingArtifactAssetDownloader: ArtifactAssetDownloader {
    private let data: Data
    private var urls: [URL] = []

    init(data: Data = Data("asset-bytes".utf8)) {
        self.data = data
    }

    func download(from url: URL) async throws -> Data {
        urls.append(url)
        return data
    }

    func requestedURLs() -> [URL] {
        urls
    }
}

private actor RecordingArtifactAssetCache: ArtifactAssetCache {
    private let rootURL: URL
    private var filenames: [String] = []
    private var dataValues: [Data] = []

    init(rootURL: URL) {
        self.rootURL = rootURL
    }

    func store(data: Data, filename: String) async throws -> URL {
        filenames.append(filename)
        dataValues.append(data)
        return rootURL.appendingPathComponent(filename)
    }

    func storedFilenames() -> [String] {
        filenames
    }

    func storedData() -> [Data] {
        dataValues
    }
}

private final class SnapshotRecorder: @unchecked Sendable {
    private(set) var values: [ForgeFlowState] = []

    func append(_ state: ForgeFlowState) {
        values.append(state)
    }
}

private func expectEqual<T: Equatable>(_ actual: T, _ expected: T) throws {
    if actual != expected {
        throw ContractTestError.expectationFailed("Expected \(expected), got \(actual)")
    }
}

private func expectTrue(_ value: Bool) throws {
    if !value {
        throw ContractTestError.expectationFailed("Expected true")
    }
}

private func expectFalse(_ value: Bool) throws {
    if value {
        throw ContractTestError.expectationFailed("Expected false")
    }
}

private func expectContains(_ haystack: String, _ needle: String) throws {
    if !haystack.contains(needle) {
        throw ContractTestError.expectationFailed("Expected body to contain \(needle)")
    }
}

private func expectNotContains(_ haystack: String, _ needle: String) throws {
    if haystack.contains(needle) {
        throw ContractTestError.expectationFailed("Expected body not to contain \(needle)")
    }
}

private func require<T>(_ value: T?, _ message: String) throws -> T {
    guard let value else {
        throw ContractTestError.expectationFailed(message)
    }
    return value
}

private func expectCaptureDraftError(_ draft: CaptureDraft, _ expected: CaptureDraftValidationError) throws {
    do {
        _ = try draft.validatedUploadPayload()
        throw ContractTestError.expectationFailed("Expected capture draft error \(expected)")
    } catch let error as CaptureDraftValidationError {
        try expectEqual(error, expected)
    }
}

private func sourceFile(_ name: String, in directory: URL) throws -> String {
    let url = directory.appendingPathComponent(name)
    guard FileManager.default.fileExists(atPath: url.path) else {
        throw ContractTestError.expectationFailed("Missing source file: \(name)")
    }
    return try String(contentsOf: url, encoding: .utf8)
}

private enum ContractTestError: Error, CustomStringConvertible {
    case fixtureMissing(String)
    case expectationFailed(String)

    var description: String {
        switch self {
        case let .fixtureMissing(name):
            return "Fixture missing: \(name).json"
        case let .expectationFailed(message):
            return message
        }
    }
}
