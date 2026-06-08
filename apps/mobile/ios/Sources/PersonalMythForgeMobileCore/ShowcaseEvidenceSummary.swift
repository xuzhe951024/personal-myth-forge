import Foundation

public enum ShowcaseEvidenceStatus: String, Codable, Equatable, Sendable {
    case waiting
    case ready
    case needsAttention
}

public struct ShowcaseEvidenceItem: Codable, Equatable, Sendable {
    public var id: String
    public var label: String
    public var status: ShowcaseEvidenceStatus
    public var detail: String

    public init(id: String, label: String, status: ShowcaseEvidenceStatus, detail: String) {
        self.id = id
        self.label = label
        self.status = status
        self.detail = detail
    }
}

public struct ShowcaseEvidenceSummary: Codable, Equatable, Sendable {
    public var status: ShowcaseEvidenceStatus
    public var title: String
    public var detail: String
    public var items: [ShowcaseEvidenceItem]
    public var privacyNotes: [String]
    public var canClaimLocalShowcaseReady: Bool

    public init(
        status: ShowcaseEvidenceStatus,
        title: String,
        detail: String,
        items: [ShowcaseEvidenceItem],
        privacyNotes: [String],
        canClaimLocalShowcaseReady: Bool
    ) {
        self.status = status
        self.title = title
        self.detail = detail
        self.items = items
        self.privacyNotes = privacyNotes
        self.canClaimLocalShowcaseReady = canClaimLocalShowcaseReady
    }

    public func item(id: String) -> ShowcaseEvidenceItem? {
        items.first { $0.id == id }
    }
}

public enum ShowcaseEvidenceSummaryBuilder {
    public static func build(
        captureReceipt: CaptureGenerationReceipt,
        generationReceipt: GenerationResultReceipt,
        sceneLoadProof: ArtifactSceneLoadProof,
        npcTickSummary: NPCAgentTickSummary,
        tickHistoryCount: Int,
        printFulfillmentReceipt: PrintFulfillmentReceipt
    ) -> ShowcaseEvidenceSummary {
        let items = [
            captureItem(captureReceipt),
            generationItem(generationReceipt),
            sceneLoadItem(sceneLoadProof),
            npcAgentItem(summary: npcTickSummary, tickHistoryCount: tickHistoryCount),
            printHandoffItem(printFulfillmentReceipt),
        ]
        let status = overallStatus(items)
        let ready = status == .ready
        let title: String
        let detail: String
        switch status {
        case .ready:
            title = "Showcase evidence ready"
            detail = "This phone has local evidence for capture, 3D, SceneKit, NPC Agent, and print handoff."
        case .needsAttention:
            title = "Showcase evidence needs attention"
            detail = firstDetail(in: items, status: .needsAttention)
                ?? "One or more showcase evidence items need attention."
        case .waiting:
            title = "Showcase evidence waiting"
            detail = firstDetail(in: items, status: .waiting)
                ?? "Local showcase evidence is waiting for the demo loop."
        }

        return ShowcaseEvidenceSummary(
            status: status,
            title: sanitize(title),
            detail: sanitize(detail),
            items: items,
            privacyNotes: [
                "Raw capture media stays out of showcase evidence.",
                "Provider keys remain backend-only.",
                "Local file paths and payment links are withheld.",
            ],
            canClaimLocalShowcaseReady: ready
        )
    }

    private static func captureItem(_ receipt: CaptureGenerationReceipt) -> ShowcaseEvidenceItem {
        item(
            "capture_to_3d",
            "Capture-to-3D",
            status(receipt.status),
            "\(receipt.title): \(receipt.detail)"
        )
    }

    private static func generationItem(_ receipt: GenerationResultReceipt) -> ShowcaseEvidenceItem {
        let status: ShowcaseEvidenceStatus
        switch receipt.status {
        case .ready:
            status = receipt.canPresentResult ? .ready : .needsAttention
        case .waiting:
            status = .waiting
        case .needsAttention:
            status = .needsAttention
        }
        return item(
            "generation_result",
            "Generation Result",
            status,
            "\(receipt.title): \(receipt.detail)"
        )
    }

    private static func sceneLoadItem(_ proof: ArtifactSceneLoadProof) -> ShowcaseEvidenceItem {
        let status: ShowcaseEvidenceStatus
        switch proof.status {
        case .loaded:
            status = proof.canOpenScene ? .ready : .needsAttention
        case .waiting:
            status = .waiting
        case .conversionRequired, .failed, .unavailable:
            status = .needsAttention
        }
        return item(
            "scene_load",
            "SceneKit Load",
            status,
            "\(proof.title): \(proof.detail)"
        )
    }

    private static func npcAgentItem(
        summary: NPCAgentTickSummary,
        tickHistoryCount: Int
    ) -> ShowcaseEvidenceItem {
        let status: ShowcaseEvidenceStatus
        switch summary.status {
        case .ready:
            status = tickHistoryCount >= 3 ? .ready : .waiting
        case .running, .waiting:
            status = .waiting
        case .needsAttention:
            status = .needsAttention
        }
        let tickText = tickHistoryCount == 1 ? "1 saved tick" : "\(max(0, tickHistoryCount)) saved ticks"
        return item(
            "npc_agent",
            "NPC Agent",
            status,
            "\(summary.title): \(summary.detail) \(tickText)."
        )
    }

    private static func printHandoffItem(_ receipt: PrintFulfillmentReceipt) -> ShowcaseEvidenceItem {
        let status: ShowcaseEvidenceStatus
        switch receipt.status {
        case .ready:
            status = receipt.canHandOffToProvider ? .ready : .needsAttention
        case .waiting:
            status = .waiting
        case .needsApproval, .blocked:
            status = .needsAttention
        }
        return item(
            "print_handoff",
            "Print Handoff",
            status,
            "\(receipt.title): \(receipt.detail)"
        )
    }

    private static func status(_ receiptStatus: CaptureGenerationReceiptStatus) -> ShowcaseEvidenceStatus {
        switch receiptStatus {
        case .waiting:
            return .waiting
        case .ready:
            return .ready
        case .needsAttention:
            return .needsAttention
        }
    }

    private static func item(
        _ id: String,
        _ label: String,
        _ status: ShowcaseEvidenceStatus,
        _ detail: String
    ) -> ShowcaseEvidenceItem {
        ShowcaseEvidenceItem(
            id: sanitize(id),
            label: sanitize(label),
            status: status,
            detail: sanitize(detail)
        )
    }

    private static func overallStatus(_ items: [ShowcaseEvidenceItem]) -> ShowcaseEvidenceStatus {
        if items.contains(where: { $0.status == .needsAttention }) {
            return .needsAttention
        }
        if items.allSatisfy({ $0.status == .ready }) {
            return .ready
        }
        return .waiting
    }

    private static func firstDetail(
        in items: [ShowcaseEvidenceItem],
        status: ShowcaseEvidenceStatus
    ) -> String? {
        items.first { $0.status == status }?.detail
    }

    private static func sanitize(_ text: String) -> String {
        var sanitized = text
        let patterns = [
            #"sk-[A-Za-z0-9._-]+"#,
            #"Bearer\s+[A-Za-z0-9._~+/\-=:-]+"#,
            #"Authorization\s*=\s*Bearer\s+[A-Za-z0-9._~+/\-=:-]+"#,
            #"Authorization"#,
            #"Bearer"#,
            #"api[_-]?key\s*[=:]\s*[^\s,;"']+"#,
            #"(private_message|raw_context|message_body)\s*:\s*[^\n]+"#,
            #"local-capture://[^\s,;"']+"#,
            #"file://[^\s,;"']+"#,
            #"/Users/[^\s,;"']+"#,
            #"/tmp/[^\s,;"']+"#,
            #"checkout_url\s*=\s*[^\s,;"']+"#,
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
