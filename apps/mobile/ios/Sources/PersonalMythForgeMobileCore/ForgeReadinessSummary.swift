import Foundation

public enum ForgeReadinessSummaryStatus: String, Codable, Equatable, Sendable {
    case waiting
    case ready
    case needsAttention
}

public struct ForgeReadinessSummary: Codable, Equatable, Sendable {
    public let status: ForgeReadinessSummaryStatus
    public let title: String
    public let detail: String
    public let routeLabel: String
    public let rows: [String]
    public let privacyNotes: [String]
    public let canForge: Bool

    public init(
        status: ForgeReadinessSummaryStatus,
        title: String,
        detail: String,
        routeLabel: String,
        rows: [String],
        privacyNotes: [String],
        canForge: Bool
    ) {
        self.status = status
        self.title = title
        self.detail = detail
        self.routeLabel = routeLabel
        self.rows = rows
        self.privacyNotes = privacyNotes
        self.canForge = canForge
    }
}

public struct ForgeActionGate: Codable, Equatable, Sendable {
    public let isEnabled: Bool
    public let title: String
    public let detail: String
    public let disabledReason: String?
}

public enum ForgeActionGateBuilder {
    public static func build(
        isMediaReadyForUpload: Bool,
        contextCapsuleReview: ContextCapsuleReview,
        forgeReadinessSummary: ForgeReadinessSummary
    ) -> ForgeActionGate {
        if !isMediaReadyForUpload {
            return gate(
                isEnabled: false,
                detail: "Capture an object before forging.",
                disabledReason: "capture_required"
            )
        }

        if contextCapsuleReview.status != .ready {
            return gate(
                isEnabled: false,
                detail: contextCapsuleReview.detail,
                disabledReason: "context_approval_required"
            )
        }

        if !forgeReadinessSummary.canForge {
            return gate(
                isEnabled: false,
                detail: forgeReadinessSummary.detail,
                disabledReason: "forge_readiness_required"
            )
        }

        return gate(
            isEnabled: true,
            detail: "Forge route \(forgeReadinessSummary.routeLabel) is ready.",
            disabledReason: nil
        )
    }

    private static func gate(
        isEnabled: Bool,
        detail: String,
        disabledReason: String?
    ) -> ForgeActionGate {
        ForgeActionGate(
            isEnabled: isEnabled,
            title: "Forge Myth",
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

public enum ForgeReadinessSummaryBuilder {
    public static func build(
        captureGenerationReadiness: CaptureGenerationReadiness,
        contextCapsuleReview: ContextCapsuleReview,
        providerReadiness: ProviderReadinessResponse?,
        providerReadinessError: String?,
        npcAgentModeSummary: NPCAgentModeSummary
    ) -> ForgeReadinessSummary {
        let rows = summaryRows(
            captureGenerationReadiness: captureGenerationReadiness,
            contextCapsuleReview: contextCapsuleReview,
            providerReadiness: providerReadiness,
            npcAgentModeSummary: npcAgentModeSummary
        )

        if let providerReadinessError,
           !providerReadinessError.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
        {
            return summary(
                status: .needsAttention,
                title: "Forge needs attention",
                detail: sanitize(providerReadinessError),
                routeLabel: "needs_attention",
                rows: rows,
                canForge: false
            )
        }

        if captureGenerationReadiness.status == .waiting {
            return summary(
                status: .waiting,
                title: "Forge waiting for capture",
                detail: captureGenerationReadiness.detail,
                routeLabel: "waiting",
                rows: rows,
                canForge: false
            )
        }

        if contextCapsuleReview.status != .ready {
            return summary(
                status: .waiting,
                title: "Forge waiting for context",
                detail: contextCapsuleReview.detail,
                routeLabel: "waiting",
                rows: rows,
                canForge: false
            )
        }

        let missingEnv = providerReadiness?.providers.flatMap(\.missingEnv).map(sanitize).filter { !$0.isEmpty } ?? []
        if captureGenerationReadiness.status == .needsAttention
            || npcAgentModeSummary.status == .needsSetup
            || !missingEnv.isEmpty
            || providerReadiness?.overallDemoReady == false
        {
            return summary(
                status: .needsAttention,
                title: "Forge needs attention",
                detail: needsAttentionDetail(
                    captureGenerationReadiness: captureGenerationReadiness,
                    npcAgentModeSummary: npcAgentModeSummary,
                    missingEnv: missingEnv
                ),
                routeLabel: "needs_attention",
                rows: rows,
                canForge: false
            )
        }

        guard let providerReadiness else {
            return summary(
                status: .waiting,
                title: "Forge waiting for backend readiness",
                detail: "Backend provider readiness has not loaded.",
                routeLabel: "waiting",
                rows: rows,
                canForge: false
            )
        }

        return summary(
            status: .ready,
            title: "Forge ready",
            detail: "Capture, context, 3D generation, and NPC Agent routing are ready.",
            routeLabel: providerReadiness.overallRealReady ? "configured" : "local_demo",
            rows: rows,
            canForge: true
        )
    }

    private static func summaryRows(
        captureGenerationReadiness: CaptureGenerationReadiness,
        contextCapsuleReview: ContextCapsuleReview,
        providerReadiness: ProviderReadinessResponse?,
        npcAgentModeSummary: NPCAgentModeSummary
    ) -> [String] {
        let threeDProvider = providerReadiness?.providers.first {
            $0.kind.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() == "three_d"
        }
        let npcProvider = providerReadiness?.providers.first {
            $0.kind.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() == "npc"
        }
        return [
            "Capture: \(captureGenerationReadiness.title)",
            "Context: \(contextCapsuleReview.title)",
            "3D Provider: \(providerLabel(threeDProvider, fallback: captureGenerationReadiness.route.displayLabel))",
            "NPC Agent: \(providerLabel(npcProvider, fallback: npcAgentModeSummary.providerLabel))",
        ]
    }

    private static func providerLabel(_ provider: ProviderReadinessItem?, fallback: String) -> String {
        guard let provider else {
            return sanitize(fallback)
        }
        let selected = provider.selectedProvider.trimmingCharacters(in: .whitespacesAndNewlines)
        let status = provider.status.trimmingCharacters(in: .whitespacesAndNewlines)
        let missing = provider.missingEnv.map(sanitize).filter { !$0.isEmpty }
        if !missing.isEmpty {
            return sanitize("\(selected.isEmpty ? fallback : selected) missing \(missing.joined(separator: ", "))")
        }
        if !selected.isEmpty && !status.isEmpty {
            return sanitize("\(selected) \(status)")
        }
        if !selected.isEmpty {
            return sanitize(selected)
        }
        return sanitize(fallback)
    }

    private static func needsAttentionDetail(
        captureGenerationReadiness: CaptureGenerationReadiness,
        npcAgentModeSummary: NPCAgentModeSummary,
        missingEnv: [String]
    ) -> String {
        if !missingEnv.isEmpty {
            return "Missing \(missingEnv.joined(separator: ", ")) before Forge is provider-ready."
        }
        if captureGenerationReadiness.status == .needsAttention {
            return captureGenerationReadiness.detail
        }
        if npcAgentModeSummary.status == .needsSetup {
            return npcAgentModeSummary.detail
        }
        return "Provider setup is incomplete before Forge."
    }

    private static func summary(
        status: ForgeReadinessSummaryStatus,
        title: String,
        detail: String,
        routeLabel: String,
        rows: [String],
        canForge: Bool
    ) -> ForgeReadinessSummary {
        ForgeReadinessSummary(
            status: status,
            title: sanitize(title),
            detail: sanitize(detail),
            routeLabel: sanitize(routeLabel),
            rows: rows.map(sanitize).filter { !$0.isEmpty },
            privacyNotes: [
                "Provider keys stay backend-only.",
                "Raw capture media and private source text are not shown in Forge readiness.",
                "Only the approved context capsule is sent when Forge runs.",
            ],
            canForge: canForge
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
