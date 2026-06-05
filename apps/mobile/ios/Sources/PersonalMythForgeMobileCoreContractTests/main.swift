import Foundation
import PersonalMythForgeMobileCore

do {
    try testDecodesObjectCaptureFixture()
    try testDecodesMythSessionFixture()
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
