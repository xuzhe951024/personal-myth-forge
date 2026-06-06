import Foundation

public struct DemoRunSnapshot: Codable, Equatable, Sendable {
    public static let currentSchemaVersion = 1
    public static let maximumStoredTicks = 12

    public var schemaVersion: Int
    public var savedAt: String
    public var session: MythSession
    public var npcTicks: [NPCAgentTick]

    public var latestTick: NPCAgentTick? {
        npcTicks.last
    }

    public init(
        schemaVersion: Int = DemoRunSnapshot.currentSchemaVersion,
        savedAt: String,
        session: MythSession,
        npcTicks: [NPCAgentTick] = []
    ) {
        self.schemaVersion = schemaVersion
        self.savedAt = savedAt
        self.session = session
        self.npcTicks = Self.normalizedTicks(npcTicks, sessionId: session.sessionId)
    }

    public init(history: MythSessionHistory, savedAt: String) {
        self.init(
            savedAt: savedAt,
            session: history.session,
            npcTicks: history.npcTicks
        )
    }

    public func appending(_ tick: NPCAgentTick, savedAt: String) -> DemoRunSnapshot {
        DemoRunSnapshot(
            schemaVersion: schemaVersion,
            savedAt: savedAt,
            session: session,
            npcTicks: npcTicks + [tick]
        )
    }

    private static func normalizedTicks(_ ticks: [NPCAgentTick], sessionId: String) -> [NPCAgentTick] {
        let matchingTicks = ticks
            .filter { $0.sessionId == sessionId }
            .sorted { lhs, rhs in
                if lhs.tickIndex == rhs.tickIndex {
                    return lhs.agentRuntime < rhs.agentRuntime
                }
                return lhs.tickIndex < rhs.tickIndex
            }
        return Array(matchingTicks.suffix(maximumStoredTicks))
    }
}

public final class DemoRunSnapshotFileStore: @unchecked Sendable {
    public let snapshotURL: URL

    public init(snapshotURL: URL) {
        self.snapshotURL = snapshotURL
    }

    public static func live(fileManager: FileManager = .default) -> DemoRunSnapshotFileStore {
        let baseDirectory = fileManager.urls(for: .applicationSupportDirectory, in: .userDomainMask).first
            ?? fileManager.temporaryDirectory
        return DemoRunSnapshotFileStore(
            snapshotURL: baseDirectory
                .appendingPathComponent("PersonalMythForge", isDirectory: true)
                .appendingPathComponent("demo-run-snapshot.json")
        )
    }

    public func load() throws -> DemoRunSnapshot? {
        guard FileManager.default.fileExists(atPath: snapshotURL.path) else {
            return nil
        }
        let data = try Data(contentsOf: snapshotURL)
        return try PMFJSON.decoder.decode(DemoRunSnapshot.self, from: data)
    }

    public func save(_ snapshot: DemoRunSnapshot) throws {
        let directory = snapshotURL.deletingLastPathComponent()
        try FileManager.default.createDirectory(
            at: directory,
            withIntermediateDirectories: true,
            attributes: nil
        )
        let data = try PMFJSON.encoder.encode(snapshot)
        try data.write(to: snapshotURL, options: [.atomic])
    }

    public func clear() throws {
        guard FileManager.default.fileExists(atPath: snapshotURL.path) else {
            return
        }
        try FileManager.default.removeItem(at: snapshotURL)
    }
}
