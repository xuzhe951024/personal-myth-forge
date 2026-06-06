import Foundation

public enum NPCAgentTickSummaryStatus: String, Codable, Equatable, Sendable {
    case waiting
    case running
    case ready
    case needsAttention
}

public struct NPCAgentTickSummary: Codable, Equatable, Sendable {
    public let status: NPCAgentTickSummaryStatus
    public let title: String
    public let detail: String
    public let runtimeLabel: String
    public let tickLabel: String
    public let decisionLabel: String
    public let rows: [String]
    public let privacyNotes: [String]

    public init(
        status: NPCAgentTickSummaryStatus,
        title: String,
        detail: String,
        runtimeLabel: String,
        tickLabel: String,
        decisionLabel: String,
        rows: [String],
        privacyNotes: [String]
    ) {
        self.status = status
        self.title = title
        self.detail = detail
        self.runtimeLabel = runtimeLabel
        self.tickLabel = tickLabel
        self.decisionLabel = decisionLabel
        self.rows = rows
        self.privacyNotes = privacyNotes
    }
}

public struct NPCAgentActionGate: Codable, Equatable, Sendable {
    public let canAdvanceVillage: Bool
    public let canRunAutonomy: Bool
    public let advanceTitle: String
    public let autonomyTitle: String
    public let detail: String
    public let disabledReason: String?
}

public enum NPCAgentActionGateBuilder {
    public static func build(
        session: MythSession?,
        npcAgentModeSummary: NPCAgentModeSummary,
        npcAgentTickSummary: NPCAgentTickSummary,
        isAdvancingTick: Bool,
        isRunningAutonomy: Bool
    ) -> NPCAgentActionGate {
        guard session != nil else {
            return gate(
                canRun: false,
                detail: "Forge a myth session before NPC agents can act.",
                disabledReason: "session_required"
            )
        }

        if isAdvancingTick || isRunningAutonomy || npcAgentTickSummary.status == .running {
            return gate(
                canRun: false,
                detail: npcAgentTickSummary.detail,
                disabledReason: "npc_action_running"
            )
        }

        if npcAgentModeSummary.status == .needsSetup {
            return gate(
                canRun: false,
                detail: npcAgentModeSummary.detail,
                disabledReason: "npc_setup_required"
            )
        }

        if npcAgentTickSummary.status == .needsAttention {
            return gate(
                canRun: false,
                detail: npcAgentTickSummary.detail,
                disabledReason: "npc_recovery_required"
            )
        }

        return gate(
            canRun: true,
            detail: "\(npcAgentModeSummary.providerLabel) NPC actions are ready.",
            disabledReason: nil
        )
    }

    private static func gate(
        canRun: Bool,
        detail: String,
        disabledReason: String?
    ) -> NPCAgentActionGate {
        NPCAgentActionGate(
            canAdvanceVillage: canRun,
            canRunAutonomy: canRun,
            advanceTitle: "Advance Village",
            autonomyTitle: "Run Autonomy",
            detail: sanitize(detail),
            disabledReason: disabledReason
        )
    }

    private static func sanitize(_ text: String) -> String {
        var sanitized = text
        let patterns = [
            #"sk-[A-Za-z0-9._-]+"#,
            #"Bearer\s+[A-Za-z0-9._~+/\-=:-]+"#,
            #"Authorization"#,
            #"api[_-]?key\s*[=:]\s*[^\s,;"']+"#,
            #"local-capture://[^\s,;"']+"#,
            #"file://[^\s,;"']+"#,
            #"/Users/[^\s,;"']+"#,
            #"/tmp/[^\s,;"']+"#,
            #"checkout_url"#,
            #"https?://checkout\.[^\s,;"']+"#,
            #"https?://pay\.[^\s,;"']+"#,
        ]
        for pattern in patterns {
            sanitized = sanitized.replacingOccurrences(
                of: pattern,
                with: "[withheld]",
                options: .regularExpression
            )
        }
        return sanitized
    }
}

public enum NPCAgentTickSummaryBuilder {
    public static func build(
        session: MythSession?,
        latestTick: NPCAgentTick?,
        tickHistoryCount: Int,
        isAdvancingTick: Bool,
        isRunningAutonomy: Bool,
        errorMessage: String?
    ) -> NPCAgentTickSummary {
        if let errorMessage, !errorMessage.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            return summary(
                status: .needsAttention,
                title: "NPC Agent tick needs attention",
                detail: sanitize(errorMessage),
                runtimeLabel: runtimeLabel(session: session, latestTick: latestTick),
                tickLabel: tickLabel(latestTick: latestTick),
                decisionLabel: "waiting for recovery",
                rows: baseRows(session: session, latestTick: latestTick, tickHistoryCount: tickHistoryCount)
            )
        }

        guard let session else {
            return summary(
                status: .waiting,
                title: "NPC Agent waiting",
                detail: "Forge a myth session before NPC agents can act around the artifact.",
                runtimeLabel: "not started",
                tickLabel: "not started",
                decisionLabel: "no session",
                rows: ["Saved ticks: 0"]
            )
        }

        if isRunningAutonomy {
            return summary(
                status: .running,
                title: "NPC autonomy running",
                detail: "Running a 3-step autonomy batch through the NPC Agent runtime.",
                runtimeLabel: runtimeLabel(session: session, latestTick: latestTick),
                tickLabel: tickLabel(latestTick: latestTick),
                decisionLabel: "world arbitration in progress",
                rows: baseRows(session: session, latestTick: latestTick, tickHistoryCount: tickHistoryCount)
            )
        }

        if isAdvancingTick {
            return summary(
                status: .running,
                title: "NPC Agent tick running",
                detail: "Running a single NPC tick through the Agent runtime.",
                runtimeLabel: runtimeLabel(session: session, latestTick: latestTick),
                tickLabel: tickLabel(latestTick: latestTick),
                decisionLabel: "world arbitration in progress",
                rows: baseRows(session: session, latestTick: latestTick, tickHistoryCount: tickHistoryCount)
            )
        }

        if let latestTick {
            let resolution = latestTick.worldResolution
            let acceptedCount = resolution.acceptedActions.count
            let rejectedCount = resolution.rejectedActions.count
            return summary(
                status: .ready,
                title: "NPC Agent tick resolved",
                detail: sanitize(resolution.summary),
                runtimeLabel: runtimeLabel(session: session, latestTick: latestTick),
                tickLabel: tickLabel(latestTick: latestTick),
                decisionLabel: "\(acceptedCount) accepted / \(rejectedCount) rejected",
                rows: baseRows(session: session, latestTick: latestTick, tickHistoryCount: tickHistoryCount)
            )
        }

        return summary(
            status: .ready,
            title: "Initial NPC Agent traces",
            detail: "Initial NPC beliefs and intentions are ready. Advance the village to resolve actions.",
            runtimeLabel: runtimeLabel(session: session, latestTick: nil),
            tickLabel: "initial",
            decisionLabel: "\(session.npcAgentTraces.count) initial traces",
            rows: [
                "Agent traces: \(session.npcAgentTraces.count)",
                "Visible changes: \(session.worldResolution.visibleChanges.count)",
                "Saved ticks: \(max(0, tickHistoryCount))",
            ]
        )
    }

    private static func runtimeLabel(session: MythSession?, latestTick: NPCAgentTick?) -> String {
        let tickRuntime = latestTick?.agentRuntime.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        if !tickRuntime.isEmpty {
            return sanitize(tickRuntime)
        }
        let sessionRuntime = session?.npcAgentRuntime.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        if !sessionRuntime.isEmpty {
            return sanitize(sessionRuntime)
        }
        let director = session?.npcDirector.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        return sanitize(director.isEmpty ? "not started" : director)
    }

    private static func tickLabel(latestTick: NPCAgentTick?) -> String {
        guard let latestTick else {
            return "initial"
        }
        return "tick \(max(0, latestTick.tickIndex))"
    }

    private static func baseRows(
        session: MythSession?,
        latestTick: NPCAgentTick?,
        tickHistoryCount: Int
    ) -> [String] {
        let traceCount = latestTick?.npcAgentTraces.count ?? session?.npcAgentTraces.count ?? 0
        let resolution = latestTick?.worldResolution ?? session?.worldResolution
        return [
            "Agent traces: \(traceCount)",
            "Accepted actions: \(resolution?.acceptedActions.count ?? 0)",
            "Rejected actions: \(resolution?.rejectedActions.count ?? 0)",
            "Visible changes: \(resolution?.visibleChanges.count ?? 0)",
            "Saved ticks: \(max(0, tickHistoryCount))",
        ]
    }

    private static func summary(
        status: NPCAgentTickSummaryStatus,
        title: String,
        detail: String,
        runtimeLabel: String,
        tickLabel: String,
        decisionLabel: String,
        rows: [String]
    ) -> NPCAgentTickSummary {
        NPCAgentTickSummary(
            status: status,
            title: sanitize(title),
            detail: sanitize(detail),
            runtimeLabel: sanitize(runtimeLabel),
            tickLabel: sanitize(tickLabel),
            decisionLabel: sanitize(decisionLabel),
            rows: rows.map(sanitize).filter { !$0.isEmpty },
            privacyNotes: [
                "NPC Agent summaries use approved myth session context only.",
                "Provider keys, raw capture media, and private source text stay hidden.",
            ]
        )
    }

    private static func sanitize(_ text: String) -> String {
        var sanitized = text
        let patterns = [
            #"sk-[A-Za-z0-9._-]+"#,
            #"Bearer\s+[A-Za-z0-9._~+/\-=:-]+"#,
            #"Authorization"#,
            #"api[_-]?key\s*[=:]\s*[^\s,;"']+"#,
            #"local-capture://[^\s,;"']+"#,
            #"file://[^\s,;"']+"#,
            #"/Users/[^\s,;"']+"#,
            #"/tmp/[^\s,;"']+"#,
            #"checkout_url"#,
            #"https?://checkout\.[^\s,;"']+"#,
            #"https?://pay\.[^\s,;"']+"#,
        ]
        for pattern in patterns {
            sanitized = sanitized.replacingOccurrences(
                of: pattern,
                with: "[withheld]",
                options: .regularExpression
            )
        }
        return sanitized
    }
}
