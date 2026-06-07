import Foundation

public enum CaptureGenerationReceiptStatus: String, Codable, Equatable, Sendable {
    case waiting
    case ready
    case needsAttention
}

public struct CaptureGenerationReceipt: Codable, Equatable, Sendable {
    public var status: CaptureGenerationReceiptStatus
    public var title: String
    public var detail: String
    public var rows: [String]
    public var privacyNotes: [String]

    public init(
        status: CaptureGenerationReceiptStatus,
        title: String,
        detail: String,
        rows: [String],
        privacyNotes: [String]
    ) {
        self.status = status
        self.title = title
        self.detail = detail
        self.rows = rows
        self.privacyNotes = privacyNotes
    }
}

public enum CaptureGenerationReceiptBuilder {
    public static func build(
        capture: ObjectCapture?,
        session: MythSession?,
        captureGenerationReadiness: CaptureGenerationReadiness
    ) -> CaptureGenerationReceipt {
        guard let capture else {
            return CaptureGenerationReceipt(
                status: .waiting,
                title: "Capture waiting",
                detail: sanitize(captureGenerationReadiness.title),
                rows: [
                    "readiness \(captureGenerationReadiness.route.displayLabel)",
                    captureGenerationReadiness.detail,
                ].map(sanitize),
                privacyNotes: basePrivacyNotes()
            )
        }

        let captureRows = rows(for: capture)
        guard let session else {
            return CaptureGenerationReceipt(
                status: .waiting,
                title: "Capture uploaded",
                detail: "Capture uploaded; waiting for myth session.",
                rows: captureRows,
                privacyNotes: basePrivacyNotes()
            )
        }

        guard let provenance = session.generatedAsset.generationProvenance else {
            return CaptureGenerationReceipt(
                status: .needsAttention,
                title: "Capture-to-3D proof missing",
                detail: "Generation provenance has not loaded for this myth session.",
                rows: captureRows + [
                    "provider \(session.generatedAsset.provider)",
                    "asset \(session.generatedAsset.format)",
                ].map(sanitize),
                privacyNotes: basePrivacyNotes()
            )
        }

        return CaptureGenerationReceipt(
            status: .ready,
            title: "Capture-to-3D ready",
            detail: "Uploaded capture is linked to generated 3D provenance.",
            rows: captureRows + rows(for: provenance, asset: session.generatedAsset),
            privacyNotes: basePrivacyNotes()
        )
    }

    private static func rows(for capture: ObjectCapture) -> [String] {
        let roleCounts = Dictionary(grouping: capture.mediaItems, by: \.role)
            .mapValues(\.count)
        let referenceCount = roleCounts["reference_image"] ?? 0
        let scanAssetCount = roleCounts["scan_asset"] ?? 0
        let totalBytes = capture.mediaItems.reduce(0) { $0 + max(0, $1.byteSize) }
        return [
            "capture \(capture.captureId)",
            "mode \(capture.captureMode)",
            "media reference_image \(referenceCount), scan_asset \(scanAssetCount)",
            "bytes \(totalBytes)",
            "status \(capture.status)",
        ].map(sanitize)
    }

    private static func rows(for provenance: GeneratedAssetProvenance, asset: GeneratedAsset) -> [String] {
        [
            "provider \(asset.provider)",
            "input \(provenance.inputMode)",
            "route \(provenance.providerRoute ?? "unknown")",
            "source images \(provenance.sourceImageCount)",
            "source assets \(provenance.sourceAssetCount)",
            "selected \(provenance.selectedSourceImageCount)/\(provenance.sourceImageCount)",
            "raw sources \(provenance.rawSourcesIncluded ? "retained" : "withheld")",
        ].map(sanitize)
    }

    private static func basePrivacyNotes() -> [String] {
        [
            "Raw capture media withheld.",
            "Capture media URIs stay off this receipt.",
            "Provider keys and local paths are redacted.",
        ]
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
