import Foundation

public enum GenerationResultReceiptStatus: String, Codable, Equatable, Sendable {
    case waiting
    case ready
    case needsAttention
}

public struct GenerationResultReceiptRow: Codable, Equatable, Sendable {
    public var id: String
    public var label: String
    public var status: GenerationResultReceiptStatus
    public var detail: String

    public init(id: String, label: String, status: GenerationResultReceiptStatus, detail: String) {
        self.id = id
        self.label = label
        self.status = status
        self.detail = detail
    }
}

public struct GenerationResultReceipt: Codable, Equatable, Sendable {
    public var status: GenerationResultReceiptStatus
    public var title: String
    public var detail: String
    public var routeLabel: String
    public var rows: [GenerationResultReceiptRow]
    public var privacyNotes: [String]
    public var canPresentResult: Bool

    public init(
        status: GenerationResultReceiptStatus,
        title: String,
        detail: String,
        routeLabel: String,
        rows: [GenerationResultReceiptRow],
        privacyNotes: [String],
        canPresentResult: Bool
    ) {
        self.status = status
        self.title = title
        self.detail = detail
        self.routeLabel = routeLabel
        self.rows = rows
        self.privacyNotes = privacyNotes
        self.canPresentResult = canPresentResult
    }

    public func row(id: String) -> GenerationResultReceiptRow? {
        rows.first { $0.id == id }
    }
}

public enum GenerationResultReceiptBuilder {
    public static func build(session: MythSession?) -> GenerationResultReceipt {
        guard let session else {
            return receipt(
                status: .waiting,
                title: "Generation result waiting",
                detail: "Forge a myth session to produce 3D, NPC, and print outputs.",
                routeLabel: "waiting",
                rows: [
                    row("game_asset", "Game asset", .waiting, "No game asset has been generated."),
                    row("ios_scene", "iOS scene", .waiting, "No scene-loadable iOS asset is available."),
                    row("print_candidate", "Print asset", .waiting, "No printable derivative is available."),
                    row("npc_agent", "NPC Agent", .waiting, "No NPC Agent traces have been generated."),
                ],
                canPresentResult: false
            )
        }

        let gameReady = hasText(session.generatedAsset.uri) && hasText(session.generatedAsset.format)
        let sceneVariant = sceneLoadableVariant(in: session.generatedAsset.variants)
        let sceneReady = sceneVariant != nil
        let printReady = hasText(session.printCandidate.uri) && hasText(session.printCandidate.format)
        let npcReady = hasText(session.npcAgentRuntime) && !session.npcAgentTraces.isEmpty
        let ready = gameReady && sceneReady && printReady && npcReady
        let status: GenerationResultReceiptStatus = ready ? .ready : .needsAttention

        return receipt(
            status: status,
            title: ready ? "Generation result ready" : "Generation result needs attention",
            detail: ready
                ? "Session \(session.sessionId) produced all required demo outputs."
                : "Session \(session.sessionId) is missing one or more demo outputs.",
            routeLabel: routeLabel(for: session.generatedAsset.generationProvenance),
            rows: [
                row(
                    "game_asset",
                    "Game asset",
                    gameReady ? .ready : .needsAttention,
                    gameAssetDetail(session.generatedAsset)
                ),
                row(
                    "ios_scene",
                    "iOS scene",
                    sceneReady ? .ready : .needsAttention,
                    sceneDetail(sceneVariant)
                ),
                row(
                    "print_candidate",
                    "Print asset",
                    printReady ? .ready : .needsAttention,
                    printCandidateDetail(session.printCandidate)
                ),
                row(
                    "npc_agent",
                    "NPC Agent",
                    npcReady ? .ready : .needsAttention,
                    npcAgentDetail(runtime: session.npcAgentRuntime, traceCount: session.npcAgentTraces.count)
                ),
            ],
            canPresentResult: ready
        )
    }

    private static func receipt(
        status: GenerationResultReceiptStatus,
        title: String,
        detail: String,
        routeLabel: String,
        rows: [GenerationResultReceiptRow],
        canPresentResult: Bool
    ) -> GenerationResultReceipt {
        GenerationResultReceipt(
            status: status,
            title: sanitize(title),
            detail: sanitize(detail),
            routeLabel: sanitize(routeLabel),
            rows: rows.map { row($0.id, $0.label, $0.status, $0.detail) },
            privacyNotes: [
                "Raw provider URIs and prompts withheld.",
                "Provider keys stay backend-only.",
                "Print ordering remains a separate approval step.",
            ],
            canPresentResult: canPresentResult
        )
    }

    private static func row(
        _ id: String,
        _ label: String,
        _ status: GenerationResultReceiptStatus,
        _ detail: String
    ) -> GenerationResultReceiptRow {
        GenerationResultReceiptRow(
            id: id,
            label: sanitize(label),
            status: status,
            detail: sanitize(detail)
        )
    }

    private static func gameAssetDetail(_ asset: GeneratedAsset) -> String {
        guard hasText(asset.uri), hasText(asset.format) else {
            return "No game asset returned."
        }
        let inputMode = asset.generationProvenance?.inputMode ?? "prompt"
        return "\(asset.provider) \(asset.format) from \(inputMode)"
    }

    private static func sceneDetail(_ variant: GeneratedAssetVariant?) -> String {
        guard let variant else {
            return "missing scene-loadable iOS asset"
        }
        return "\(variant.format) scene-loadable iOS asset"
    }

    private static func printCandidateDetail(_ candidate: PrintCandidate) -> String {
        guard hasText(candidate.uri), hasText(candidate.format) else {
            return "missing printable derivative"
        }
        let approval = candidate.requiresUserApproval ? "approval required" : "approval not required"
        return "\(candidate.format) \(approval)"
    }

    private static func npcAgentDetail(runtime: String, traceCount: Int) -> String {
        guard traceCount > 0 else {
            return "missing NPC Agent traces"
        }
        let traceLabel = traceCount == 1 ? "1 trace" : "\(traceCount) traces"
        let runtimeLabel = hasText(runtime) ? runtime : "runtime missing"
        return "\(runtimeLabel), \(traceLabel)"
    }

    private static func routeLabel(for provenance: GeneratedAssetProvenance?) -> String {
        guard let provenance else {
            return "route missing"
        }
        return provenance.inputMode.isEmpty ? "route missing" : provenance.inputMode
    }

    private static func sceneLoadableVariant(in variants: [GeneratedAssetVariant]) -> GeneratedAssetVariant? {
        variants.first { variant in
            variant.role == "ios_scene_asset"
                && variant.isSceneLoadable
                && hasText(variant.format)
                && hasText(variant.uri)
        }
    }

    private static func hasText(_ value: String) -> Bool {
        !value.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
    }

    private static func sanitize(_ text: String) -> String {
        var sanitized = text
        let patterns = [
            #"sk-[A-Za-z0-9._-]+"#,
            #"Bearer\s+[A-Za-z0-9._~+/\-=:-]+"#,
            #"api[_-]?key\s*[=:]\s*[^\s,;"']+"#,
            #"local-capture://[^\s,;"']+"#,
            #"file://[^\s,;"']+"#,
            #"data:image/[^\s,;"']+"#,
            #"/Users/[^\s,;"']+"#,
            #"/tmp/[^\s,;"']+"#,
            #"checkout_url"#,
            #"payment_link"#,
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
