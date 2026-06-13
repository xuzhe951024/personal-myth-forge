import Foundation

public enum ShowcaseAutopilotAction: String, Codable, Equatable, Sendable {
    case blocked
    case waiting
    case forge
    case runAutonomy
    case advanceNPC
    case requestQuote
    case complete
}

public struct ShowcaseAutopilotPlan: Codable, Equatable, Sendable {
    public var action: ShowcaseAutopilotAction
    public var buttonTitle: String
    public var detail: String
    public var isExecutable: Bool

    public init(
        action: ShowcaseAutopilotAction,
        buttonTitle: String,
        detail: String,
        isExecutable: Bool
    ) {
        self.action = action
        self.buttonTitle = buttonTitle
        self.detail = detail
        self.isExecutable = isExecutable
    }
}

public enum ShowcaseAutopilotPlanner {
    public static func plan(
        script: DemoScript,
        phase: ForgeFlowPhase,
        session: MythSession?,
        npcTickHistoryCount: Int,
        printQuote: PrintQuote?,
        providerReadiness: ProviderReadinessResponse?,
        providerReadinessError: String?,
        isAdvancingNPCTick: Bool,
        isRunningAutonomy: Bool,
        isLoadingPrintQuote: Bool
    ) -> ShowcaseAutopilotPlan {
        if isForgeBusy(phase) {
            return waiting("Run Forge", "Forge is already running.")
        }
        if isRunningAutonomy {
            return waiting("Run NPCs", "NPC autonomy is already running.")
        }
        if isAdvancingNPCTick {
            return waiting("Advance NPC", "NPC tick advance is already running.")
        }
        if isLoadingPrintQuote {
            return waiting("Get Quote", "Print quote request is already running.")
        }
        guard script.step(id: "capture")?.status == .complete else {
            return blocked("Capture First", "Capture object first.")
        }
        guard let session else {
            if script.step(id: "forge")?.status == .current {
                return executable(.forge, "Run Forge", "Forge the myth session.")
            }
            return waiting("Run Forge", "Myth session is not ready yet.")
        }
        guard script.step(id: "three_d_scene")?.status == .complete else {
            return waiting("Load 3D", "Wait for the generated 3D scene.")
        }
        if npcTickHistoryCount < 3 {
            if MythSessionID.isValid(session.sessionId) {
                return executable(.runAutonomy, "Run NPCs", "Run NPC autonomy for 3 ticks.")
            }
            return executable(.advanceNPC, "Advance NPC", "Advance one legacy NPC tick.")
        }
        if printQuote == nil {
            return executable(.requestQuote, "Get Quote", "Request a print quote.")
        }
        if let providerReadinessError {
            return blocked("Check Resources", providerReadinessError)
        }
        guard let providerReadiness else {
            return waiting("Check Resources", "Backend readiness has not loaded.")
        }
        guard providerReadiness.overallDemoReady else {
            return blocked("Check Resources", missingProviderDetail(providerReadiness))
        }
        if let threeDEvaluationStep = script.step(id: "three_d_evaluation") {
            switch threeDEvaluationStep.status {
            case .complete:
                break
            case .blocked:
                return blocked("Check 3D Eval", "Review 3D evaluation blockers: \(threeDEvaluationStep.detail)")
            case .waiting:
                return waiting("Check 3D Eval", "Load 3D evaluation readiness: \(threeDEvaluationStep.detail)")
            case .current, .optional:
                return waiting("Check 3D Eval", "Review 3D evaluation readiness: \(threeDEvaluationStep.detail)")
            }
        }
        if let npcEvaluationStep = script.step(id: "npc_evaluation") {
            switch npcEvaluationStep.status {
            case .complete:
                break
            case .blocked:
                return blocked("Check NPC Eval", "Review NPC evaluation blockers: \(npcEvaluationStep.detail)")
            case .waiting:
                return waiting("Check NPC Eval", "Load NPC evaluation readiness: \(npcEvaluationStep.detail)")
            case .current, .optional:
                return waiting("Check NPC Eval", "Review NPC evaluation readiness: \(npcEvaluationStep.detail)")
            }
        }
        if let externalActionsStep = script.step(id: "external_actions") {
            switch externalActionsStep.status {
            case .complete:
                break
            case .blocked:
                return blocked("Check Actions", "Review external action blockers: \(externalActionsStep.detail)")
            case .waiting:
                return waiting("Check Actions", "Load external action readiness: \(externalActionsStep.detail)")
            case .current, .optional:
                return waiting("Check Actions", "Review external action readiness: \(externalActionsStep.detail)")
            }
        }
        if let launchStep = script.step(id: "final_launch") {
            switch launchStep.status {
            case .complete:
                return ShowcaseAutopilotPlan(
                    action: .complete,
                    buttonTitle: "Ready",
                    detail: "Final launch is ready.",
                    isExecutable: false
                )
            case .blocked:
                return blocked("Check Launch", "Review final launch blockers: \(launchStep.detail)")
            case .waiting:
                return waiting("Check Launch", "Load final launch readiness: \(launchStep.detail)")
            case .current, .optional:
                return waiting("Check Launch", "Review final launch readiness: \(launchStep.detail)")
            }
        }
        return ShowcaseAutopilotPlan(
            action: .complete,
            buttonTitle: "Ready",
            detail: "Local demo loop is ready.",
            isExecutable: false
        )
    }

    private static func isForgeBusy(_ phase: ForgeFlowPhase) -> Bool {
        switch phase {
        case .uploadingCapture, .creatingSession:
            return true
        case .idle, .editingObject, .ready, .failed:
            return false
        }
    }

    private static func executable(
        _ action: ShowcaseAutopilotAction,
        _ buttonTitle: String,
        _ detail: String
    ) -> ShowcaseAutopilotPlan {
        ShowcaseAutopilotPlan(
            action: action,
            buttonTitle: sanitize(buttonTitle),
            detail: sanitize(detail),
            isExecutable: true
        )
    }

    private static func waiting(_ buttonTitle: String, _ detail: String) -> ShowcaseAutopilotPlan {
        ShowcaseAutopilotPlan(
            action: .waiting,
            buttonTitle: sanitize(buttonTitle),
            detail: sanitize(detail),
            isExecutable: false
        )
    }

    private static func blocked(_ buttonTitle: String, _ detail: String) -> ShowcaseAutopilotPlan {
        ShowcaseAutopilotPlan(
            action: .blocked,
            buttonTitle: sanitize(buttonTitle),
            detail: sanitize(detail),
            isExecutable: false
        )
    }

    private static func missingProviderDetail(_ readiness: ProviderReadinessResponse) -> String {
        let missing = readiness.providers.flatMap(\.missingEnv)
        if missing.isEmpty {
            return "Provider setup needed."
        }
        return "Missing \(missing.joined(separator: ", "))"
    }

    private static func sanitize(_ value: String) -> String {
        let lowered = value.lowercased()
        let apiKeyMarker = "api" + "_key"
        let bearerMarker = "Bearer" + " "
        if value.contains("sk-")
            || value.contains("/Users/")
            || value.contains("file://")
            || value.contains("local-capture://")
            || value.contains("Authorization")
            || value.contains(bearerMarker)
            || lowered.contains(apiKeyMarker)
            || lowered.contains("checkout")
        {
            return "[withheld]"
        }
        return value
    }
}
