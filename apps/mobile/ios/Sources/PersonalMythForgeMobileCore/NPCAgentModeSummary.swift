import Foundation

public enum NPCAgentModeStatus: String, Codable, Equatable, Sendable {
    case waiting
    case localDemo
    case aiReady
    case needsSetup
}

public struct NPCAgentModeSummary: Codable, Equatable, Sendable {
    public var status: NPCAgentModeStatus
    public var title: String
    public var detail: String
    public var providerLabel: String
    public var runtimeLabel: String
    public var traceCount: Int
    public var tickHistoryCount: Int
    public var missingEnv: [String]
    public var privacyNotes: [String]

    public init(
        status: NPCAgentModeStatus,
        title: String,
        detail: String,
        providerLabel: String,
        runtimeLabel: String,
        traceCount: Int,
        tickHistoryCount: Int,
        missingEnv: [String],
        privacyNotes: [String]
    ) {
        self.status = status
        self.title = title
        self.detail = detail
        self.providerLabel = providerLabel
        self.runtimeLabel = runtimeLabel
        self.traceCount = traceCount
        self.tickHistoryCount = tickHistoryCount
        self.missingEnv = missingEnv
        self.privacyNotes = privacyNotes
    }
}

public enum NPCAgentModeSummaryBuilder {
    public static func build(
        session: MythSession?,
        latestTick: NPCAgentTick?,
        tickHistoryCount: Int,
        providerReadiness: ProviderReadinessResponse?,
        providerReadinessError: String?
    ) -> NPCAgentModeSummary {
        guard let session else {
            return makeSummary(
                status: .waiting,
                title: "NPC agents waiting",
                detail: "Forge a myth session before NPC agents can interpret the artifact.",
                providerLabel: "unknown",
                runtimeLabel: "not started",
                traceCount: 0,
                tickHistoryCount: 0,
                missingEnv: []
            )
        }

        let npcProvider = providerReadiness?.providers.first { provider in
            provider.kind.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() == "npc"
        }
        let runtime = runtimeLabel(session: session, latestTick: latestTick)
        let provider = providerLabel(session: session, npcProvider: npcProvider)
        let traceCount = latestTick?.npcAgentTraces.count ?? session.npcAgentTraces.count
        let missingEnv = (npcProvider?.missingEnv ?? []).map(sanitize).filter { !$0.isEmpty }

        if providerReadinessError != nil || !missingEnv.isEmpty || npcProvider?.isDemoReady == false {
            return makeSummary(
                status: .needsSetup,
                title: "NPC Agent setup needed",
                detail: setupDetail(missingEnv: missingEnv, error: providerReadinessError),
                providerLabel: provider,
                runtimeLabel: runtime,
                traceCount: traceCount,
                tickHistoryCount: tickHistoryCount,
                missingEnv: missingEnv
            )
        }

        if isOpenAIMode(provider: provider, runtime: runtime, npcProvider: npcProvider) {
            return makeSummary(
                status: .aiReady,
                title: "OpenAI NPC Agent ready",
                detail: "NPC traces and ticks are ready to use the OpenAI structured agent runtime.",
                providerLabel: provider,
                runtimeLabel: runtime,
                traceCount: traceCount,
                tickHistoryCount: tickHistoryCount,
                missingEnv: []
            )
        }

        return makeSummary(
            status: .localDemo,
            title: "Local NPC agent mode",
            detail: "NPC behavior is running through the deterministic local agent runtime.",
            providerLabel: provider,
            runtimeLabel: runtime,
            traceCount: traceCount,
            tickHistoryCount: tickHistoryCount,
            missingEnv: []
        )
    }

    private static func runtimeLabel(session: MythSession, latestTick: NPCAgentTick?) -> String {
        let latestRuntime = latestTick?.agentRuntime.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        if !latestRuntime.isEmpty {
            return sanitize(latestRuntime)
        }
        let sessionRuntime = session.npcAgentRuntime.trimmingCharacters(in: .whitespacesAndNewlines)
        if !sessionRuntime.isEmpty {
            return sanitize(sessionRuntime)
        }
        let director = session.npcDirector.trimmingCharacters(in: .whitespacesAndNewlines)
        return sanitize(director.isEmpty ? "not started" : director)
    }

    private static func providerLabel(
        session: MythSession,
        npcProvider: ProviderReadinessItem?
    ) -> String {
        let provider = npcProvider?.selectedProvider.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        if !provider.isEmpty {
            return sanitize(provider)
        }
        let director = session.npcDirector.trimmingCharacters(in: .whitespacesAndNewlines)
        return sanitize(director.isEmpty ? "unknown" : director)
    }

    private static func isOpenAIMode(
        provider: String,
        runtime: String,
        npcProvider: ProviderReadinessItem?
    ) -> Bool {
        let providerLower = provider.lowercased()
        let runtimeLower = runtime.lowercased()
        return providerLower.contains("openai")
            || runtimeLower.contains("openai")
            || npcProvider?.isRealProviderReady == true
    }

    private static func setupDetail(missingEnv: [String], error: String?) -> String {
        if !missingEnv.isEmpty {
            return "Missing \(missingEnv.joined(separator: ", ")) before AI Agent NPC mode is ready."
        }
        if let error, !error.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            return sanitize(error)
        }
        return "NPC provider setup is incomplete."
    }

    private static func makeSummary(
        status: NPCAgentModeStatus,
        title: String,
        detail: String,
        providerLabel: String,
        runtimeLabel: String,
        traceCount: Int,
        tickHistoryCount: Int,
        missingEnv: [String]
    ) -> NPCAgentModeSummary {
        NPCAgentModeSummary(
            status: status,
            title: sanitize(title),
            detail: sanitize(detail),
            providerLabel: sanitize(providerLabel),
            runtimeLabel: sanitize(runtimeLabel),
            traceCount: max(0, traceCount),
            tickHistoryCount: max(0, tickHistoryCount),
            missingEnv: missingEnv.map(sanitize).filter { !$0.isEmpty },
            privacyNotes: [
                "NPC provider keys stay backend-only.",
                "Only approved myth session context is used for NPC prompts.",
                "Raw private messages, calendars, and files are not shown.",
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
