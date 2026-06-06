import Foundation
import PersonalMythForgeMobileCore

do {
    try testDecodesObjectCaptureFixture()
    try testDecodesMythSessionFixture()
    try testDecodesMythSessionWithoutGeneratedAssetVariants()
    try testDecodesMythSessionWithoutNPCAgentTraceFields()
    try testDecodesNPCAgentTickPayload()
    try testDemoRunSnapshotKeepsMatchingTicksSortedAndBounded()
    try testDemoRunSnapshotEncodesSnakeCaseJSONWithoutRawMediaOrSecrets()
    try testDemoRunSnapshotFileStoreSavesLoadsOverwritesAndClears()
    try testDecodesProviderReadinessPayload()
    try testCaptureIDValidation()
    try testMultipartBodyIncludesMetadataAndFileWithoutLocalPaths()
    try testMultipartBuilderSanitizesHeaderValues()
    try await testUploadObjectCaptureBuildsMultipartRequest()
    try await testCreateMythSessionFromCaptureBuildsJSONRequest()
    try await testInvalidCaptureIDFailsBeforeNetwork()
    try await testHTTPStatusErrorIncludesStatusAndBody()
    try await testHTTPStatusErrorSanitizesSecretsAndTruncatesBody()
    try await testGetProviderReadinessBuildsGETRequest()
    try await testGetProviderReadinessSanitizesHTTPErrorBody()
    try await testCreateNPCAgentTickBuildsJSONRequest()
    try await testCreateNPCAgentTickSanitizesHTTPErrorBody()
    try await testUploadObjectCaptureUsesGeneratedFilenamesWithoutLocalPaths()
    try await testUploadObjectCaptureRejectsUnsafeContentTypeBeforeNetwork()
    try await testUploadObjectCaptureBuildsARKitScanMultipartRequest()
    try testCaptureModeIncludesGuidedScan()
    try testCaptureDraftBuildsSinglePhotoPayload()
    try testCaptureDraftBuildsPhotoSetPayload()
    try testCaptureDraftBuildsARKitScanPayload()
    try testCaptureDraftBuildsGuidedScanPayload()
    try testCaptureDraftRejectsInvalidMedia()
    try testCaptureDraftRejectsInvalidGuidedScanMedia()
    try testCaptureDraftRejectsOversizedMedia()
    try testCaptureMediaSelectionSummarizesSinglePhoto()
    try testCaptureMediaSelectionRequiresPhotoSetCount()
    try testCaptureMediaSelectionBuildsARKitDraft()
    try testCaptureMediaSelectionSummarizesGuidedScan()
    try testCaptureMediaSelectionClearsWhenModeChanges()
    try testGuidedScanPhotoSetBuilderBuildsSortedImageDrafts()
    try testGuidedScanPhotoSetBuilderTruncatesToTwelveImages()
    try testGuidedScanPhotoSetBuilderRejectsTooFewImages()
    try testGuidedScanPhotoSetBuilderRejectsUnsupportedContentType()
    try testGuidedScanPhotoSetBuilderRejectsOversizedMedia()
    try testArtifactPreviewStateMarksRemoteGLBAsGeneratedAsset()
    try testArtifactPreviewStateMarksLocalUSDZAsSceneLoadable()
    try testArtifactPreviewStateHandlesMissingURI()
    try testArtifactPreviewStateHandlesMissingFormat()
    try await testArtifactAssetPreparerUsesLocalSceneURL()
    try await testArtifactAssetPreparerDownloadsRemoteUSDZForSceneKit()
    try await testArtifactAssetPreparerCachesRemoteGLBButRequiresConversion()
    try await testArtifactAssetPreparerPrefersSceneVariantOverPrimaryGLB()
    try await testArtifactAssetPreparerReportsLocalSceneVariantSourceURI()
    try await testArtifactAssetPreparerRejectsInvalidRemoteURI()
    try await testArtifactAssetPreparerSkipsDownloadWhenFormatMissing()
    try await testArtifactAssetPreparerTreatsCancellationAsCancelled()
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
    try expectEqual(session.npcAgentRuntime, "local_agent_runtime")
    try expectEqual(session.npcAgentTraces.count, 3)
    try expectEqual(session.npcAgentTraces[0].npcId, "npc_archivist")
    try expectEqual(session.npcAgentTraces[0].belief, "The key belongs to a door that remembers who knocked.")
    try expectEqual(session.npcAgentTraces[0].proposedAction, "catalog the key")
    try expectEqual(session.npcAgentTraces[0].confidence, 0.81)
    try expectEqual(session.worldResolution.acceptedActions.count, 2)
    try expectEqual(session.generatedAsset.variants.count, 2)
    try expectEqual(session.generatedAsset.variants[0].role, "game_asset")
    try expectEqual(session.generatedAsset.variants[0].format, "glb")
    try expectEqual(session.generatedAsset.variants[1].role, "ios_scene_asset")
    try expectEqual(session.generatedAsset.variants[1].format, "usdz")
    try expectTrue(session.generatedAsset.variants[1].isSceneLoadable)
    try expectEqual(session.printCandidate.requiresUserApproval, true)
}

private func testDecodesMythSessionWithoutGeneratedAssetVariants() throws {
    var payload = try require(
        try JSONSerialization.jsonObject(with: FixtureLoader.data(from: "myth-session-response")) as? [String: Any],
        "expected myth session fixture object"
    )
    var generatedAsset = try require(
        payload["generated_asset"] as? [String: Any],
        "expected generated asset object"
    )
    generatedAsset.removeValue(forKey: "variants")
    payload["generated_asset"] = generatedAsset

    let data = try JSONSerialization.data(withJSONObject: payload)
    let session = try PMFJSON.decoder.decode(MythSession.self, from: data)

    try expectEqual(session.generatedAsset.variants, [])
}

private func testDecodesMythSessionWithoutNPCAgentTraceFields() throws {
    var payload = try require(
        try JSONSerialization.jsonObject(with: FixtureLoader.data(from: "myth-session-response")) as? [String: Any],
        "expected myth session fixture object"
    )
    payload.removeValue(forKey: "npc_agent_runtime")
    payload.removeValue(forKey: "npc_agent_traces")

    let data = try JSONSerialization.data(withJSONObject: payload)
    let session = try PMFJSON.decoder.decode(MythSession.self, from: data)

    try expectEqual(session.npcAgentRuntime, "")
    try expectEqual(session.npcAgentTraces, [])
}

private func testDecodesNPCAgentTickPayload() throws {
    let data = Data(
        """
        {
          "session_id": "myth_0123456789abcdef",
          "tick_index": 1,
          "agent_runtime": "local_tick_runtime",
          "npc_agent_traces": [
            {
              "npc_id": "mara",
              "name": "Mara",
              "belief": "The relic is becoming a public promise.",
              "intention": "turn awe into shared witness",
              "proposed_action": "invite_neighbors_to_witness",
              "rationale": "Mara reacts to 1 recent village event.",
              "confidence": 0.82
            }
          ],
          "npc_reactions": [
            {
              "npc_id": "mara",
              "name": "Mara",
              "emotion": "awe",
              "interpretation": "The relic is becoming a public promise.",
              "plan": ["invite_neighbors_to_witness"],
              "world_change": "faith_in_player_increases"
            }
          ],
          "world_resolution": {
            "arbitrator": "local_rules",
            "summary": "The village accepts 1 ritual actions around the relic.",
            "accepted_actions": [
              {
                "npc_id": "mara",
                "action": "invite_neighbors_to_witness",
                "status": "accepted",
                "reason": "safe ritual or debate action"
              }
            ],
            "rejected_actions": [],
            "world_state_delta": {
              "faith": 1,
              "artifact_renown": 1
            },
            "visible_changes": ["Mara prepares to invite neighbors to witness."]
          }
        }
        """.utf8
    )

    let tick = try PMFJSON.decoder.decode(NPCAgentTick.self, from: data)

    try expectEqual(tick.sessionId, "myth_0123456789abcdef")
    try expectEqual(tick.tickIndex, 1)
    try expectEqual(tick.agentRuntime, "local_tick_runtime")
    try expectEqual(tick.npcAgentTraces[0].proposedAction, "invite_neighbors_to_witness")
    try expectEqual(tick.npcReactions[0].emotion, "awe")
    try expectEqual(tick.worldResolution.acceptedActions[0].status, "accepted")
}

private func testDemoRunSnapshotKeepsMatchingTicksSortedAndBounded() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let ticks = (0..<16).map { index in
        npcTick(sessionId: index == 3 ? "other_session" : session.sessionId, tickIndex: index)
    }.reversed()

    let snapshot = DemoRunSnapshot(savedAt: "2026-06-06T12:00:00Z", session: session, npcTicks: Array(ticks))

    try expectEqual(snapshot.schemaVersion, DemoRunSnapshot.currentSchemaVersion)
    try expectEqual(snapshot.npcTicks.count, DemoRunSnapshot.maximumStoredTicks)
    try expectEqual(snapshot.npcTicks.map(\.sessionId).filter { $0 != session.sessionId }, [])
    try expectEqual(snapshot.npcTicks.map(\.tickIndex), Array(4...15))
    try expectEqual(snapshot.latestTick?.tickIndex, 15)
}

private func testDemoRunSnapshotEncodesSnakeCaseJSONWithoutRawMediaOrSecrets() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let snapshot = DemoRunSnapshot(
        savedAt: "2026-06-06T12:00:00Z",
        session: session,
        npcTicks: [npcTick(sessionId: session.sessionId, tickIndex: 1)]
    )

    let data = try PMFJSON.encoder.encode(snapshot)
    let body = String(decoding: data, as: UTF8.self)

    try expectContains(body, #""schema_version":1"#)
    try expectContains(body, #""npc_ticks":"#)
    try expectNotContains(body, "raw-photo-bytes")
    try expectNotContains(body, "Authorization=Bearer")
    try expectNotContains(body, "api_key=")
    try expectNotContains(body, "file:///")

    let decoded = try PMFJSON.decoder.decode(DemoRunSnapshot.self, from: data)
    try expectEqual(decoded, snapshot)
}

private func testDemoRunSnapshotFileStoreSavesLoadsOverwritesAndClears() throws {
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")
    let temporaryDirectory = FileManager.default.temporaryDirectory
        .appendingPathComponent("pmf-demo-snapshot-\(UUID().uuidString)", isDirectory: true)
    let store = DemoRunSnapshotFileStore(
        snapshotURL: temporaryDirectory.appendingPathComponent("demo-run-snapshot.json")
    )
    defer {
        try? FileManager.default.removeItem(at: temporaryDirectory)
    }

    try expectTrue(try store.load() == nil)

    let first = DemoRunSnapshot(savedAt: "2026-06-06T12:00:00Z", session: session)
    try store.save(first)
    try expectEqual(try store.load(), first)

    let second = first.appending(
        npcTick(sessionId: session.sessionId, tickIndex: 1),
        savedAt: "2026-06-06T12:01:00Z"
    )
    try store.save(second)
    try expectEqual(try store.load(), second)

    try store.clear()
    try expectTrue(try store.load() == nil)
}

private func testDecodesProviderReadinessPayload() throws {
    let data = Data(
        """
        {
          "overall_demo_ready": true,
          "overall_real_ready": false,
          "providers": [
            {
              "kind": "three_d",
              "selected_provider": "local",
              "status": "local_stub",
              "is_demo_ready": true,
              "is_real_provider_ready": false,
              "missing_env": [],
              "capabilities": ["text_to_3d_stub"],
              "notes": ["Local 3D provider is deterministic."]
            },
            {
              "kind": "npc",
              "selected_provider": "openai",
              "status": "missing_configuration",
              "is_demo_ready": false,
              "is_real_provider_ready": false,
              "missing_env": ["OPENAI_API_KEY"],
              "capabilities": ["structured_agent_traces"],
              "notes": ["OPENAI_API_KEY is required."]
            }
          ]
        }
        """.utf8
    )

    let readiness = try PMFJSON.decoder.decode(ProviderReadinessResponse.self, from: data)

    try expectTrue(readiness.overallDemoReady)
    try expectFalse(readiness.overallRealReady)
    try expectEqual(readiness.providers.count, 2)
    try expectEqual(readiness.providers[0].kind, "three_d")
    try expectEqual(readiness.providers[0].status, "local_stub")
    try expectTrue(readiness.providers[0].isDemoReady)
    try expectFalse(readiness.providers[0].isRealProviderReady)
    try expectEqual(readiness.providers[1].missingEnv, ["OPENAI_API_KEY"])
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

private func testGetProviderReadinessBuildsGETRequest() async throws {
    let data = Data(
        """
        {
          "overall_demo_ready": true,
          "overall_real_ready": false,
          "providers": []
        }
        """.utf8
    )
    let transport = RecordingTransport(
        responses: [HTTPResponse(statusCode: 200, data: data)]
    )
    let client = PersonalMythForgeAPIClient(
        baseURL: URL(string: "http://127.0.0.1:8080")!,
        transport: transport
    )

    let readiness = try await client.getProviderReadiness()

    try expectTrue(readiness.overallDemoReady)
    let request = try require(transport.requests.first, "missing readiness request")
    try expectEqual(request.httpMethod, "GET")
    try expectEqual(request.url?.path, "/v1/provider-readiness")
    try expectEqual(request.httpBody, nil)
}

private func testGetProviderReadinessSanitizesHTTPErrorBody() async throws {
    let secret = "test-secret"
    let body = "Authorization=Bearer \(secret) api_key=\(secret)"
    let transport = RecordingTransport(
        responses: [HTTPResponse(statusCode: 502, data: Data(body.utf8))]
    )
    let client = PersonalMythForgeAPIClient(
        baseURL: URL(string: "http://127.0.0.1:8080")!,
        transport: transport
    )

    do {
        _ = try await client.getProviderReadiness()
        throw ContractTestError.expectationFailed("Expected sanitized readiness error")
    } catch ForgeFlowError.httpStatus(502, let sanitizedBody) {
        try expectFalse(sanitizedBody.contains(secret))
        try expectContains(sanitizedBody, "Authorization=Bearer [redacted]")
        try expectContains(sanitizedBody, "api_key=[redacted]")
    }
}

private func testCreateNPCAgentTickBuildsJSONRequest() async throws {
    let responseData = Data(
        """
        {
          "session_id": "myth_0123456789abcdef",
          "tick_index": 1,
          "agent_runtime": "local_tick_runtime",
          "npc_agent_traces": [],
          "npc_reactions": [],
          "world_resolution": {
            "arbitrator": "local_rules",
            "summary": "The village holds.",
            "accepted_actions": [],
            "rejected_actions": [],
            "world_state_delta": {},
            "visible_changes": ["The village studies the relic."]
          }
        }
        """.utf8
    )
    let transport = RecordingTransport(responses: [HTTPResponse(statusCode: 200, data: responseData)])
    let client = PersonalMythForgeAPIClient(
        baseURL: URL(string: "http://127.0.0.1:8080")!,
        transport: transport
    )
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")

    let tick = try await client.createNPCAgentTick(
        session: session,
        tickIndex: 1,
        recentEvents: ["The village debate grows louder."]
    )

    try expectEqual(tick.agentRuntime, "local_tick_runtime")
    let request = try require(transport.requests.first, "missing npc tick request")
    try expectEqual(request.httpMethod, "POST")
    try expectEqual(request.url?.path, "/v1/npc-ticks")
    try expectEqual(request.value(forHTTPHeaderField: "Content-Type"), "application/json")
    let body = String(decoding: request.httpBody ?? Data(), as: UTF8.self)
    try expectContains(body, "\"session_id\":\"session_cap_ba02a3816bd145b4\"")
    try expectContains(body, "\"tick_index\":1")
    try expectContains(body, "\"recent_events\":[\"The village debate grows louder.\"]")
}

private func testCreateNPCAgentTickSanitizesHTTPErrorBody() async throws {
    let body = "Authorization=Bearer test-secret api_key=test-secret"
    let transport = RecordingTransport(
        responses: [HTTPResponse(statusCode: 502, data: Data(body.utf8))]
    )
    let client = PersonalMythForgeAPIClient(
        baseURL: URL(string: "http://127.0.0.1:8080")!,
        transport: transport
    )
    let session = try FixtureLoader.decode(MythSession.self, from: "myth-session-response")

    do {
        _ = try await client.createNPCAgentTick(
            session: session,
            tickIndex: 1,
            recentEvents: []
        )
        throw ContractTestError.expectationFailed("Expected npc tick HTTP status error")
    } catch let ForgeFlowError.httpStatus(status, sanitizedBody) {
        try expectEqual(status, 502)
        try expectContains(sanitizedBody, "Authorization=Bearer [redacted]")
        try expectContains(sanitizedBody, "api_key=[redacted]")
        try expectNotContains(sanitizedBody, "test-secret")
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

private func testCaptureModeIncludesGuidedScan() throws {
    try expectEqual(CaptureMode.guidedScan.rawValue, "guided_scan")
    try expectTrue(CaptureMode.allCases.contains(.guidedScan))
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

private func testCaptureDraftBuildsGuidedScanPayload() throws {
    let draft = CaptureDraft(
        label: "wooden fox",
        materialsText: "wood, paint",
        visualNotes: "guided scan image set",
        source: "phone_capture",
        mode: .guidedScan,
        media: [
            captureMedia(filename: "front.jpg", contentType: "image/jpeg", kind: .image),
            captureMedia(filename: "side.png", contentType: "image/png", kind: .image),
        ]
    )

    let payload = try draft.validatedUploadPayload()

    try expectEqual(payload.metadata.captureMode, "guided_scan")
    try expectEqual(payload.uploads.count, 2)
    try expectEqual(payload.uploads.map(\.contentType), ["image/jpeg", "image/png"])
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

private func testCaptureDraftRejectsInvalidGuidedScanMedia() throws {
    try expectCaptureDraftError(
        CaptureDraft(
            label: "wooden fox",
            materialsText: "",
            visualNotes: "",
            source: "phone_capture",
            mode: .guidedScan,
            media: [captureMedia(filename: "front.jpg", contentType: "image/jpeg", kind: .image)]
        ),
        .invalidMediaCount(.guidedScan, 1)
    )
    try expectCaptureDraftError(
        CaptureDraft(
            label: "wooden fox",
            materialsText: "",
            visualNotes: "",
            source: "phone_capture",
            mode: .guidedScan,
            media: [
                captureMedia(filename: "fox.glb", contentType: "model/gltf-binary", kind: .scanAsset)
            ]
        ),
        .invalidMediaCount(.guidedScan, 1)
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

private func testCaptureMediaSelectionSummarizesGuidedScan() throws {
    let emptySelection = CaptureMediaSelection(mode: .guidedScan)
    let onePhoto = CaptureMediaSelection(
        mode: .guidedScan,
        media: [captureMedia(filename: "front.jpg", contentType: "image/jpeg", kind: .image)]
    )
    let twoPhotos = CaptureMediaSelection(
        mode: .guidedScan,
        media: [
            captureMedia(filename: "front.jpg", contentType: "image/jpeg", kind: .image),
            captureMedia(filename: "side.png", contentType: "image/png", kind: .image),
        ]
    )

    try expectFalse(emptySelection.isReadyForUpload)
    try expectEqual(emptySelection.summary.title, "Choose guided scan photos")
    try expectEqual(emptySelection.summary.detail, "Choose at least 2 guided scan photos")
    try expectFalse(onePhoto.isReadyForUpload)
    try expectTrue(twoPhotos.isReadyForUpload)
    try expectEqual(twoPhotos.summary.title, "2 guided scan photos selected")
    try expectContains(twoPhotos.summary.detail, "front.jpg")
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

private func testGuidedScanPhotoSetBuilderBuildsSortedImageDrafts() throws {
    let media = try GuidedScanPhotoSetBuilder.mediaDrafts(
        from: [
            guidedScanImage(filename: "scan_003.heic", contentType: "image/heic"),
            guidedScanImage(filename: "scan_001.jpg", contentType: "image/jpeg"),
            guidedScanImage(filename: "scan_002.png", contentType: "image/png"),
        ]
    )

    try expectEqual(media.map(\.originalFilename), ["scan_001.jpg", "scan_002.png", "scan_003.heic"])
    try expectEqual(media.map(\.contentType), ["image/jpeg", "image/png", "image/heic"])
    try expectTrue(media.allSatisfy { $0.kind == .image })
}

private func testGuidedScanPhotoSetBuilderTruncatesToTwelveImages() throws {
    let images = (0..<14).map { index in
        guidedScanImage(filename: String(format: "scan_%02d.jpg", index), contentType: "image/jpeg")
    }

    let media = try GuidedScanPhotoSetBuilder.mediaDrafts(from: images)

    try expectEqual(media.count, 12)
    try expectEqual(media.first?.originalFilename, "scan_00.jpg")
    try expectEqual(media.last?.originalFilename, "scan_11.jpg")
}

private func testGuidedScanPhotoSetBuilderRejectsTooFewImages() throws {
    try expectGuidedScanPhotoSetBuilderError(
        [guidedScanImage(filename: "scan_001.jpg", contentType: "image/jpeg")],
        .tooFewImages(1)
    )
}

private func testGuidedScanPhotoSetBuilderRejectsUnsupportedContentType() throws {
    try expectGuidedScanPhotoSetBuilderError(
        [
            guidedScanImage(filename: "scan_001.jpg", contentType: "image/jpeg"),
            guidedScanImage(filename: "scan_002.gif", contentType: "image/gif"),
        ],
        .unsupportedContentType("image/gif")
    )
}

private func testGuidedScanPhotoSetBuilderRejectsOversizedMedia() throws {
    let oversizedBytes = CaptureDraft.maxFileBytes + 1
    try expectGuidedScanPhotoSetBuilderError(
        [
            guidedScanImage(filename: "scan_001.jpg", contentType: "image/jpeg"),
            guidedScanImage(
                filename: "scan_002.jpg",
                contentType: "image/jpeg",
                data: Data(repeating: 0, count: oversizedBytes)
            ),
        ],
        .mediaTooLarge(oversizedBytes, CaptureDraft.maxFileBytes)
    )
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

private func testArtifactAssetPreparerPrefersSceneVariantOverPrimaryGLB() async throws {
    let downloader = RecordingArtifactAssetDownloader(data: Data("usdz-bytes".utf8))
    let cache = RecordingArtifactAssetCache(rootURL: URL(fileURLWithPath: "/tmp/pmf-assets"))
    let session = mythSession(
        asset: generatedAsset(
            format: "glb",
            uri: "https://cdn.example.com/relic.glb",
            variants: [
                GeneratedAssetVariant(
                    role: "game_asset",
                    format: "glb",
                    uri: "https://cdn.example.com/relic.glb",
                    isSceneLoadable: false
                ),
                GeneratedAssetVariant(
                    role: "ios_scene_asset",
                    format: "usdz",
                    uri: "https://cdn.example.com/relic.usdz",
                    isSceneLoadable: true
                ),
            ]
        )
    )
    let prepared = await ArtifactAssetPreparer(downloader: downloader, cache: cache)
        .prepare(session: session)

    try expectEqual(prepared.status, .cachedSceneReady)
    try expectEqual(prepared.sourceURI, "https://cdn.example.com/relic.usdz")
    try expectEqual(prepared.cachedURL, URL(fileURLWithPath: "/tmp/pmf-assets/myth_test-meshy.usdz"))
    try expectEqual(prepared.sceneURL, prepared.cachedURL)
    try expectEqual(await downloader.requestedURLs(), [URL(string: "https://cdn.example.com/relic.usdz")!])
    try expectEqual(await cache.storedFilenames(), ["myth_test-meshy.usdz"])
    try expectEqual(await cache.storedData(), [Data("usdz-bytes".utf8)])
}

private func testArtifactAssetPreparerReportsLocalSceneVariantSourceURI() async throws {
    let downloader = RecordingArtifactAssetDownloader()
    let cache = RecordingArtifactAssetCache(rootURL: URL(fileURLWithPath: "/tmp/pmf-assets"))
    let session = mythSession(
        asset: generatedAsset(
            format: "glb",
            uri: "file:///tmp/relic.glb",
            variants: [
                GeneratedAssetVariant(
                    role: "ios_scene_asset",
                    format: "usdz",
                    uri: "file:///tmp/relic.usdz",
                    isSceneLoadable: true
                ),
            ]
        )
    )
    let prepared = await ArtifactAssetPreparer(downloader: downloader, cache: cache)
        .prepare(session: session)

    try expectEqual(prepared.status, .localSceneReady)
    try expectEqual(prepared.sourceURI, "file:///tmp/relic.usdz")
    try expectEqual(prepared.cachedURL, URL(string: "file:///tmp/relic.usdz"))
    try expectEqual(prepared.sceneURL, URL(string: "file:///tmp/relic.usdz"))
    try expectEqual(await downloader.requestedURLs(), [])
    try expectEqual(await cache.storedFilenames(), [])
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

private func testArtifactAssetPreparerSkipsDownloadWhenFormatMissing() async throws {
    let downloader = RecordingArtifactAssetDownloader()
    let cache = RecordingArtifactAssetCache(rootURL: URL(fileURLWithPath: "/tmp/pmf-assets"))
    let session = mythSession(
        asset: generatedAsset(format: "", uri: "https://cdn.example.com/relic")
    )
    let prepared = await ArtifactAssetPreparer(downloader: downloader, cache: cache)
        .prepare(session: session)

    try expectEqual(prepared.status, .awaitingFormat)
    try expectEqual(prepared.statusTitle, "Awaiting 3D asset format")
    try expectEqual(prepared.cachedURL, nil)
    try expectEqual(prepared.sceneURL, nil)
    try expectEqual(await downloader.requestedURLs(), [])
    try expectEqual(await cache.storedFilenames(), [])
}

private func testArtifactAssetPreparerTreatsCancellationAsCancelled() async throws {
    let downloader = RecordingArtifactAssetDownloader(error: CancellationError())
    let cache = RecordingArtifactAssetCache(rootURL: URL(fileURLWithPath: "/tmp/pmf-assets"))
    let session = mythSession(
        asset: generatedAsset(format: "usdz", uri: "https://cdn.example.com/relic.usdz")
    )
    let prepared = await ArtifactAssetPreparer(downloader: downloader, cache: cache)
        .prepare(session: session)

    try expectEqual(prepared.status, .cancelled)
    try expectEqual(prepared.statusTitle, "Asset preparation cancelled")
    try expectEqual(prepared.cachedURL, nil)
    try expectEqual(prepared.sceneURL, nil)
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

private func guidedScanImage(
    filename: String,
    contentType: String,
    data: Data = Data("scan-image".utf8)
) -> GuidedScanImageFile {
    GuidedScanImageFile(
        filename: filename,
        contentType: contentType,
        data: data
    )
}

private func generatedAsset(
    format: String,
    uri: String,
    variants: [GeneratedAssetVariant] = []
) -> GeneratedAsset {
    GeneratedAsset(
        kind: "game_asset",
        provider: "meshy",
        format: format,
        uri: uri,
        prompt: "a brass key relic",
        moderationStatus: "approved",
        variants: variants
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

private func npcTick(sessionId: String, tickIndex: Int) -> NPCAgentTick {
    NPCAgentTick(
        sessionId: sessionId,
        tickIndex: tickIndex,
        agentRuntime: "local_tick_runtime",
        npcAgentTraces: [
            NPCAgentTrace(
                npcId: "mara",
                name: "Mara",
                belief: "The relic remembers prior runs.",
                intention: "Keep the ritual continuous.",
                proposedAction: "move closer to the relic",
                rationale: "A restored village should not feel reset.",
                confidence: 0.82
            )
        ],
        npcReactions: [],
        worldResolution: WorldResolution(
            arbitrator: "local_world_arbitrator",
            summary: "The village preserves continuity.",
            acceptedActions: [
                ResolvedNPCAction(
                    npcId: "mara",
                    action: "move closer to the relic",
                    status: "accepted",
                    reason: "Safe visible action"
                )
            ],
            rejectedActions: [],
            worldStateDelta: ["tick_index": .int(tickIndex)],
            visibleChanges: ["Mara marks restored tick \(tickIndex)."]
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
    private let error: Error?
    private var urls: [URL] = []

    init(data: Data = Data("asset-bytes".utf8), error: Error? = nil) {
        self.data = data
        self.error = error
    }

    func download(from url: URL) async throws -> Data {
        urls.append(url)
        if let error {
            throw error
        }
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

private func expectGuidedScanPhotoSetBuilderError(
    _ images: [GuidedScanImageFile],
    _ expected: GuidedScanPhotoSetBuilderError
) throws {
    do {
        _ = try GuidedScanPhotoSetBuilder.mediaDrafts(from: images)
        throw ContractTestError.expectationFailed("Expected guided scan builder error \(expected)")
    } catch let error as GuidedScanPhotoSetBuilderError {
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
