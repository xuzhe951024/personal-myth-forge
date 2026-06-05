import Foundation
import PersonalMythForgeMobileCore

do {
    try testDecodesObjectCaptureFixture()
    try testDecodesMythSessionFixture()
    try testCaptureIDValidation()
    try testMultipartBodyIncludesMetadataAndFileWithoutLocalPaths()
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

private enum FixtureLoader {
    static func decode<T: Decodable>(_ type: T.Type, from name: String) throws -> T {
        guard let url = Bundle.module.url(forResource: name, withExtension: "json") else {
            throw ContractTestError.fixtureMissing(name)
        }
        let data = try Data(contentsOf: url)
        return try PMFJSON.decoder.decode(T.self, from: data)
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
