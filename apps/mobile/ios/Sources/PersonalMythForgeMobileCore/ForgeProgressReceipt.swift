import Foundation

public enum ForgeProgressReceiptStatus: String, Codable, Equatable, Sendable {
    case waiting
    case running
    case ready
    case needsAttention
}

public struct ForgeProgressReceiptRow: Codable, Equatable, Sendable {
    public let label: String
    public let status: String
    public let detail: String

    public init(label: String, status: String, detail: String) {
        self.label = label
        self.status = status
        self.detail = detail
    }
}

public struct ForgeProgressReceipt: Codable, Equatable, Sendable {
    public let status: ForgeProgressReceiptStatus
    public let title: String
    public let detail: String
    public let rows: [ForgeProgressReceiptRow]
    public let privacyNotes: [String]

    public init(
        status: ForgeProgressReceiptStatus,
        title: String,
        detail: String,
        rows: [ForgeProgressReceiptRow],
        privacyNotes: [String]
    ) {
        self.status = status
        self.title = title
        self.detail = detail
        self.rows = rows
        self.privacyNotes = privacyNotes
    }
}

public enum ForgeProgressReceiptBuilder {
    public static func build(
        state: ForgeFlowState,
        captureGenerationReadiness: CaptureGenerationReadiness
    ) -> ForgeProgressReceipt {
        switch state.phase {
        case .idle, .editingObject:
            return receipt(
                status: .waiting,
                title: "Forge waiting",
                detail: "Capture and context must be ready before forging.",
                rows: waitingRows(captureGenerationReadiness: captureGenerationReadiness)
            )
        case .uploadingCapture:
            return receipt(
                status: .running,
                title: "Forge running",
                detail: "Uploading capture before myth generation.",
                rows: [
                    row("Capture upload", "running", "Uploading capture media."),
                    row("Myth session", "waiting", "Waiting for uploaded capture."),
                    row("3D generation", "waiting", "Route \(captureGenerationReadiness.route.displayLabel) queued."),
                    row("NPC Agent", "waiting", "NPC interpretation starts after session creation."),
                ]
            )
        case .creatingSession:
            return receipt(
                status: .running,
                title: "Forge running",
                detail: "Creating myth session, 3D artifact, and NPC interpretation.",
                rows: creatingRows(
                    capture: state.capture,
                    captureGenerationReadiness: captureGenerationReadiness
                )
            )
        case let .ready(session):
            return receipt(
                status: .ready,
                title: "Forge ready",
                detail: "Myth session, generated 3D asset, and NPC interpretation are ready.",
                rows: readyRows(session: session)
            )
        case let .failed(error):
            return receipt(
                status: .needsAttention,
                title: "Forge needs attention",
                detail: "Forge failed: \(String(describing: error))",
                rows: [
                    row("Capture upload", "blocked", "Forge request did not complete."),
                    row("Myth session", "blocked", String(describing: error)),
                    row("3D generation", "blocked", "Generated asset unavailable."),
                    row("NPC Agent", "blocked", "NPC interpretation unavailable."),
                ]
            )
        }
    }

    private static func waitingRows(
        captureGenerationReadiness: CaptureGenerationReadiness
    ) -> [ForgeProgressReceiptRow] {
        [
            row("Capture upload", "waiting", "Route \(captureGenerationReadiness.route.displayLabel) is not running."),
            row("Myth session", "waiting", "Waiting for Forge Myth."),
            row("3D generation", "waiting", captureGenerationReadiness.detail),
            row("NPC Agent", "waiting", "NPC Agent starts after the artifact exists."),
        ]
    }

    private static func creatingRows(
        capture: ObjectCapture?,
        captureGenerationReadiness: CaptureGenerationReadiness
    ) -> [ForgeProgressReceiptRow] {
        let captureDetail = capture.map { "Uploaded capture \($0.captureId)." } ?? "Capture uploaded."
        return [
            row("Capture upload", "uploaded", captureDetail),
            row("Myth session", "running", "Creating myth session."),
            row("3D generation", "running", "Generating via \(captureGenerationReadiness.route.displayLabel)."),
            row("NPC Agent", "running", "NPC interpretation starts with session creation."),
        ]
    }

    private static func readyRows(session: MythSession) -> [ForgeProgressReceiptRow] {
        let asset = session.generatedAsset
        let provenance = asset.generationProvenance
        let route = provenance?.providerRoute ?? "unknown"
        let input = provenance?.inputMode ?? "prompt"
        return [
            row("Capture upload", "uploaded", "Capture accepted for myth session."),
            row("Myth session", "ready", session.sessionId),
            row("3D generation", "ready", "\(asset.provider) \(input) \(route)"),
            row("NPC Agent", "ready", "\(session.npcAgentRuntime), \(session.npcReactions.count) reactions."),
        ]
    }

    private static func receipt(
        status: ForgeProgressReceiptStatus,
        title: String,
        detail: String,
        rows: [ForgeProgressReceiptRow]
    ) -> ForgeProgressReceipt {
        ForgeProgressReceipt(
            status: status,
            title: sanitize(title),
            detail: sanitize(detail),
            rows: rows,
            privacyNotes: [
                "Raw capture media stays off this receipt.",
                "Provider keys and local paths are redacted.",
                "NPC Agent context uses approved capsule summaries only.",
            ]
        )
    }

    private static func row(_ label: String, _ status: String, _ detail: String) -> ForgeProgressReceiptRow {
        ForgeProgressReceiptRow(
            label: sanitize(label),
            status: sanitize(status),
            detail: sanitize(detail)
        )
    }

    private static func sanitize(_ value: String) -> String {
        var sanitized = value
        let patterns = [
            #"sk-[A-Za-z0-9._-]+"#,
            #"Bearer\s+[A-Za-z0-9._~+/\-=:-]+"#,
            #"api[_-]?key\s*[=:]\s*[^\s,;"']+"#,
            #"(private_message|raw_context|message_body)\s*:\s*[^\n]+"#,
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
