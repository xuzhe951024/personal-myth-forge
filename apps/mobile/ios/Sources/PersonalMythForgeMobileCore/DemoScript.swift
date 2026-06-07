import Foundation

public enum DemoScriptStepStatus: String, Codable, Equatable, Sendable {
    case waiting
    case current
    case complete
    case optional
    case blocked
}

public struct DemoScriptStep: Codable, Equatable, Sendable {
    public var id: String
    public var label: String
    public var status: DemoScriptStepStatus
    public var detail: String

    public init(id: String, label: String, status: DemoScriptStepStatus, detail: String) {
        self.id = id
        self.label = label
        self.status = status
        self.detail = detail
    }
}

public struct DemoScript: Codable, Equatable, Sendable {
    public var title: String
    public var nextAction: String
    public var steps: [DemoScriptStep]

    public init(title: String, nextAction: String, steps: [DemoScriptStep]) {
        self.title = title
        self.nextAction = nextAction
        self.steps = steps
    }

    public func step(id: String) -> DemoScriptStep? {
        steps.first { $0.id == id }
    }
}

public enum DemoScriptBuilder {
    public static func build(
        captureSelection: CaptureMediaSelection?,
        session: MythSession?,
        npcTickHistoryCount: Int,
        printQuote: PrintQuote?,
        providerReadiness: ProviderReadinessResponse?,
        providerReadinessError: String?,
        finalLaunchSummary: FinalLaunchMobileSummary? = nil
    ) -> DemoScript {
        let captureReady = captureSelection?.isReadyForUpload == true
        let sceneDetail = sceneStatus(for: session)
        let npcComplete = npcTickHistoryCount >= 3
        let resources = resourcesStatus(readiness: providerReadiness, error: providerReadinessError)

        var steps = [
            step(
                "capture",
                "Capture Object",
                captureReady ? .complete : .current,
                captureReady ? captureSelection?.summary.title ?? "Media ready." : "Choose a photo or guided scan."
            ),
            step(
                "forge",
                "Forge Myth",
                forgeStatus(captureReady: captureReady, session: session),
                session == nil ? "Upload capture and create session." : "Myth session is ready."
            ),
            step(
                "three_d_scene",
                "Load 3D Scene",
                threeDStatus(session: session, sceneReady: sceneDetail.isReady),
                sceneDetail.detail
            ),
            step(
                "npc_autonomy",
                "Run NPC Autonomy",
                npcStatus(session: session, sceneReady: sceneDetail.isReady, tickCount: npcTickHistoryCount),
                npcDetail(session: session, tickCount: npcTickHistoryCount)
            ),
            step(
                "print_quote",
                "Request Print Quote",
                printStatus(session: session, npcComplete: npcComplete, quote: printQuote),
                printDetail(session: session, quote: printQuote)
            ),
            step("resources", "Check Resources", resources.status, resources.detail),
        ]

        if let finalLaunchSummary {
            steps.append(threeDEvaluationStep(finalLaunchSummary))
            steps.append(npcEvaluationStep(finalLaunchSummary))
            steps.append(finalLaunchStep(finalLaunchSummary))
        }

        return DemoScript(
            title: "Live Demo Script",
            nextAction: nextAction(
                captureReady: captureReady,
                session: session,
                sceneReady: sceneDetail.isReady,
                npcComplete: npcComplete,
                printQuote: printQuote,
                resourcesStatus: resources.status,
                threeDEvaluationStatus: steps.first { $0.id == "three_d_evaluation" }?.status,
                npcEvaluationStatus: steps.first { $0.id == "npc_evaluation" }?.status,
                finalLaunchStatus: steps.first { $0.id == "final_launch" }?.status
            ),
            steps: steps
        )
    }

    private static func forgeStatus(captureReady: Bool, session: MythSession?) -> DemoScriptStepStatus {
        if session != nil {
            return .complete
        }
        return captureReady ? .current : .waiting
    }

    private static func threeDStatus(session: MythSession?, sceneReady: Bool) -> DemoScriptStepStatus {
        guard session != nil else {
            return .waiting
        }
        return sceneReady ? .complete : .current
    }

    private static func npcStatus(
        session: MythSession?,
        sceneReady: Bool,
        tickCount: Int
    ) -> DemoScriptStepStatus {
        guard session != nil else {
            return .waiting
        }
        guard sceneReady else {
            return .waiting
        }
        return tickCount >= 3 ? .complete : .current
    }

    private static func printStatus(
        session: MythSession?,
        npcComplete: Bool,
        quote: PrintQuote?
    ) -> DemoScriptStepStatus {
        guard session != nil else {
            return .waiting
        }
        if quote != nil {
            return .complete
        }
        return npcComplete ? .optional : .waiting
    }

    private static func sceneStatus(for session: MythSession?) -> (isReady: Bool, detail: String) {
        guard let session else {
            return (false, "Scene appears after forging.")
        }
        if let variant = session.generatedAsset.preferredSceneVariant {
            return (true, "\(variant.format.uppercased()) scene asset ready.")
        }
        if !session.generatedAsset.uri.isEmpty {
            return (false, "Generated asset is ready; scene import is pending.")
        }
        return (false, "Generated asset metadata is incomplete.")
    }

    private static func npcDetail(session: MythSession?, tickCount: Int) -> String {
        guard session != nil else {
            return "NPCs start after the artifact exists."
        }
        if tickCount >= 3 {
            return "\(tickCount) ticks saved."
        }
        if tickCount == 1 {
            return "1 tick saved; run autonomy."
        }
        return "Run autonomy for 3 ticks."
    }

    private static func printDetail(session: MythSession?, quote: PrintQuote?) -> String {
        guard session != nil else {
            return "Print candidate appears after forging."
        }
        guard let quote else {
            return "Quote can be requested after NPC autonomy."
        }
        let dollars = Double(quote.estimatedPriceCents) / 100.0
        return "\(quote.currency) \(String(format: "%.2f", dollars)) \(quote.status)"
    }

    private static func resourcesStatus(
        readiness: ProviderReadinessResponse?,
        error: String?
    ) -> (status: DemoScriptStepStatus, detail: String) {
        if let error {
            return (.blocked, sanitize(error))
        }
        guard let readiness else {
            return (.waiting, "Backend readiness has not loaded.")
        }
        if readiness.overallDemoReady {
            return (.complete, readiness.overallRealReady ? "Real providers ready." : "Local demo providers ready.")
        }
        let missing = readiness.providers.flatMap(\.missingEnv).joined(separator: ", ")
        return (.blocked, missing.isEmpty ? "Provider setup needed." : "Missing \(missing)")
    }

    private static func finalLaunchStep(_ summary: FinalLaunchMobileSummary) -> DemoScriptStep {
        step(
            "final_launch",
            "Final Launch",
            finalLaunchStatus(summary.overallStatus),
            finalLaunchDetail(summary)
        )
    }

    private static func threeDEvaluationStep(_ summary: FinalLaunchMobileSummary) -> DemoScriptStep {
        step(
            "three_d_evaluation",
            "3D Evaluation",
            threeDEvaluationStatus(summary.threeDEvaluationRows),
            threeDEvaluationDetail(summary.threeDEvaluationRows)
        )
    }

    private static func npcEvaluationStep(_ summary: FinalLaunchMobileSummary) -> DemoScriptStep {
        step(
            "npc_evaluation",
            "NPC Evaluation",
            npcEvaluationStatus(summary.npcEvaluationRows),
            npcEvaluationDetail(summary.npcEvaluationRows)
        )
    }

    private static func threeDEvaluationStatus(_ rows: [String]) -> DemoScriptStepStatus {
        let text = rows.joined(separator: " ").lowercased()
        if rows.first?.hasPrefix("3D evaluation ready:") == true {
            return .complete
        }
        if text.contains("blocked")
            || text.contains("failed")
            || text.contains("three_d_evaluation_failed")
        {
            return .blocked
        }
        return .waiting
    }

    private static func threeDEvaluationDetail(_ rows: [String]) -> String {
        rows.first ?? "3D evaluation readiness has not loaded."
    }

    private static func npcEvaluationStatus(_ rows: [String]) -> DemoScriptStepStatus {
        let text = rows.joined(separator: " ").lowercased()
        if rows.first?.hasPrefix("NPC Agent evaluation ready:") == true {
            return .complete
        }
        if text.contains("blocked")
            || text.contains("failed")
            || text.contains("npc_agent_evaluation_failed")
        {
            return .blocked
        }
        return .waiting
    }

    private static func npcEvaluationDetail(_ rows: [String]) -> String {
        rows.first ?? "NPC evaluation readiness has not loaded."
    }

    private static func finalLaunchStatus(_ status: FinalLaunchMobileStatus) -> DemoScriptStepStatus {
        switch status {
        case .ready:
            return .complete
        case .waiting:
            return .waiting
        case .blocked:
            return .blocked
        }
    }

    private static func finalLaunchDetail(_ summary: FinalLaunchMobileSummary) -> String {
        let firstProblem = summary.phaseRows.first { $0.status != .ready }?.detail
            ?? summary.acceptanceRows.first
            ?? summary.handoffRows.first
            ?? summary.subtitle
        return "\(summary.title): \(firstProblem)"
    }

    private static func nextAction(
        captureReady: Bool,
        session: MythSession?,
        sceneReady: Bool,
        npcComplete: Bool,
        printQuote: PrintQuote?,
        resourcesStatus: DemoScriptStepStatus,
        threeDEvaluationStatus: DemoScriptStepStatus?,
        npcEvaluationStatus: DemoScriptStepStatus?,
        finalLaunchStatus: DemoScriptStepStatus?
    ) -> String {
        if !captureReady {
            return "Capture or import an object."
        }
        guard session != nil else {
            return "Forge the myth session."
        }
        if !sceneReady {
            return "Open the 3D preview."
        }
        if !npcComplete {
            return "Run NPC autonomy."
        }
        if printQuote == nil {
            return "Request a print quote when ready."
        }
        if resourcesStatus == .blocked {
            return "Check backend resources."
        }
        if resourcesStatus == .waiting {
            return "Check backend resources."
        }
        if let threeDEvaluationStatus {
            switch threeDEvaluationStatus {
            case .complete:
                break
            case .blocked:
                return "Review 3D evaluation blockers."
            case .waiting:
                return "Load 3D evaluation readiness."
            case .current, .optional:
                return "Review 3D evaluation readiness."
            }
        }
        if let npcEvaluationStatus {
            switch npcEvaluationStatus {
            case .complete:
                break
            case .blocked:
                return "Review NPC evaluation blockers."
            case .waiting:
                return "Load NPC evaluation readiness."
            case .current, .optional:
                return "Review NPC evaluation readiness."
            }
        }
        if let finalLaunchStatus {
            switch finalLaunchStatus {
            case .complete:
                return "Final launch is ready."
            case .blocked:
                return "Review final launch blockers."
            case .waiting:
                return "Load final launch readiness."
            case .current, .optional:
                return "Review final launch readiness."
            }
        }
        return "Local demo loop is ready."
    }

    private static func step(
        _ id: String,
        _ label: String,
        _ status: DemoScriptStepStatus,
        _ detail: String
    ) -> DemoScriptStep {
        DemoScriptStep(id: id, label: label, status: status, detail: sanitize(detail))
    }

    private static func sanitize(_ value: String) -> String {
        let lowered = value.lowercased()
        let apiKeyMarker = "api" + "_key"
        let bearerMarker = "Bearer" + " "
        if value.contains("sk-")
            || value.contains("/Users/")
            || value.contains("file://")
            || lowered.contains("checkout")
            || lowered.contains(apiKeyMarker)
            || value.contains("Authorization")
            || value.contains(bearerMarker)
            || value.contains("local-capture://")
        {
            return "[withheld]"
        }
        return value
    }
}
