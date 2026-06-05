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
    try testForgeFlowReducerTransitionsThroughReadyAndReset()
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

private final class RecordingTransport: HTTPTransport {
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
