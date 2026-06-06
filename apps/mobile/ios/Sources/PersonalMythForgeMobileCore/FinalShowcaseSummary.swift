import Foundation

public enum FinalShowcaseSummaryStatus: String, Codable, Equatable, Sendable {
    case waiting
    case readyForLocalDemo
    case needsAttention
}

public enum FinalShowcaseStageStatus: String, Codable, Equatable, Sendable {
    case waiting
    case ready
    case needsAttention
    case optional
}

public struct FinalShowcaseSummaryStage: Codable, Equatable, Sendable {
    public var id: String
    public var label: String
    public var status: FinalShowcaseStageStatus
    public var detail: String

    public init(id: String, label: String, status: FinalShowcaseStageStatus, detail: String) {
        self.id = id
        self.label = label
        self.status = status
        self.detail = detail
    }
}

public struct FinalShowcaseSummary: Codable, Equatable, Sendable {
    public var overallStatus: FinalShowcaseSummaryStatus
    public var title: String
    public var stages: [FinalShowcaseSummaryStage]
    public var privacyNotes: [String]

    public init(
        overallStatus: FinalShowcaseSummaryStatus,
        title: String,
        stages: [FinalShowcaseSummaryStage],
        privacyNotes: [String]
    ) {
        self.overallStatus = overallStatus
        self.title = title
        self.stages = stages
        self.privacyNotes = privacyNotes
    }

    public func stage(id: String) -> FinalShowcaseSummaryStage? {
        stages.first { $0.id == id }
    }
}

public enum FinalShowcaseSummaryBuilder {
    public static func build(
        captureSelection: CaptureMediaSelection?,
        session: MythSession?,
        npcTickHistoryCount: Int,
        printQuote: PrintQuote?,
        providerReadiness: ProviderReadinessResponse?,
        providerReadinessError: String?
    ) -> FinalShowcaseSummary {
        let stages = [
            captureStage(captureSelection),
            threeDStage(session),
            npcStage(session: session, npcTickHistoryCount: npcTickHistoryCount),
            printStage(session: session, printQuote: printQuote),
            resourcesStage(readiness: providerReadiness, error: providerReadinessError),
        ]
        return FinalShowcaseSummary(
            overallStatus: overallStatus(session: session, stages: stages),
            title: sanitize(session?.mythSeed.title ?? "Waiting for first myth session"),
            stages: stages,
            privacyNotes: [
                "Raw capture media stays out of the summary.",
                "Provider keys remain backend-only.",
                "Checkout links are not surfaced in the demo summary.",
                "Local file paths are withheld.",
            ]
        )
    }

    private static func captureStage(_ selection: CaptureMediaSelection?) -> FinalShowcaseSummaryStage {
        guard let selection else {
            return stage("capture", "Capture", .waiting, "Choose a photo, guided scan, upload, or scan asset.")
        }
        if selection.isReadyForUpload {
            return stage("capture", "Capture", .ready, selection.summary.title)
        }
        return stage("capture", "Capture", .waiting, selection.summary.detail)
    }

    private static func threeDStage(_ session: MythSession?) -> FinalShowcaseSummaryStage {
        guard let session else {
            return stage("three_d", "3D Asset", .waiting, "Forge a myth session to create the game asset.")
        }
        let asset = session.generatedAsset
        guard !asset.uri.isEmpty, !asset.format.isEmpty else {
            return stage("three_d", "3D Asset", .needsAttention, "Generated asset metadata is incomplete.")
        }
        let inputMode = asset.generationProvenance?.inputMode ?? "prompt"
        return stage("three_d", "3D Asset", .ready, "\(asset.provider) \(asset.format) via \(inputMode)")
    }

    private static func npcStage(
        session: MythSession?,
        npcTickHistoryCount: Int
    ) -> FinalShowcaseSummaryStage {
        guard let session else {
            return stage("npc_agent", "NPC Agent", .waiting, "NPC agents start after the artifact exists.")
        }
        let hasNPCOutput = !session.npcAgentTraces.isEmpty || session.npcReactions.count >= 3
        guard hasNPCOutput else {
            return stage("npc_agent", "NPC Agent", .needsAttention, "No NPC agent output returned.")
        }
        let tickText = npcTickHistoryCount == 1 ? "1 saved tick" : "\(npcTickHistoryCount) saved ticks"
        let runtime = session.npcAgentRuntime.isEmpty ? session.npcDirector : session.npcAgentRuntime
        return stage("npc_agent", "NPC Agent", .ready, "\(runtime), \(tickText)")
    }

    private static func printStage(session: MythSession?, printQuote: PrintQuote?) -> FinalShowcaseSummaryStage {
        guard session != nil else {
            return stage("print", "Print", .waiting, "Print candidate appears after the myth session.")
        }
        if let printQuote {
            let dollars = Double(printQuote.estimatedPriceCents) / 100.0
            return stage(
                "print",
                "Print",
                .ready,
                "\(printQuote.currency) \(String(format: "%.2f", dollars)) \(printQuote.status)"
            )
        }
        return stage("print", "Print", .optional, "Print candidate ready; quote not requested yet.")
    }

    private static func resourcesStage(
        readiness: ProviderReadinessResponse?,
        error: String?
    ) -> FinalShowcaseSummaryStage {
        if let error {
            return stage("resources", "Resources", .needsAttention, sanitize(error))
        }
        guard let readiness else {
            return stage("resources", "Resources", .waiting, "Backend readiness has not loaded.")
        }
        if readiness.overallDemoReady {
            let mode = readiness.overallRealReady ? "real providers ready" : "local demo providers ready"
            return stage("resources", "Resources", .ready, mode)
        }
        let missing = readiness.providers.flatMap(\.missingEnv).joined(separator: ", ")
        return stage(
            "resources",
            "Resources",
            .needsAttention,
            missing.isEmpty ? "Provider setup needed." : "Missing \(missing)"
        )
    }

    private static func overallStatus(
        session: MythSession?,
        stages: [FinalShowcaseSummaryStage]
    ) -> FinalShowcaseSummaryStatus {
        guard session != nil else {
            return .waiting
        }
        if stages.contains(where: { $0.status == .needsAttention }) {
            return .needsAttention
        }
        let requiredReady = ["capture", "three_d", "npc_agent", "resources"].allSatisfy { id in
            stages.first(where: { $0.id == id })?.status == .ready
        }
        return requiredReady ? .readyForLocalDemo : .waiting
    }

    private static func stage(
        _ id: String,
        _ label: String,
        _ status: FinalShowcaseStageStatus,
        _ detail: String
    ) -> FinalShowcaseSummaryStage {
        FinalShowcaseSummaryStage(id: id, label: label, status: status, detail: sanitize(detail))
    }

    private static func sanitize(_ value: String) -> String {
        if value.contains("sk-")
            || value.contains("/Users/")
            || value.contains("file://")
            || value.lowercased().contains("checkout")
        {
            return "[withheld]"
        }
        return value
    }
}
