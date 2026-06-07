import Foundation

public enum ThreeDGenerationInputReviewStatus: String, Codable, Equatable, Sendable {
    case waiting
    case ready
    case needsAttention
}

public struct ThreeDGenerationInputReviewRow: Codable, Equatable, Sendable {
    public var id: String
    public var label: String
    public var status: ThreeDGenerationInputReviewStatus
    public var detail: String

    public init(id: String, label: String, status: ThreeDGenerationInputReviewStatus, detail: String) {
        self.id = id
        self.label = label
        self.status = status
        self.detail = detail
    }
}

public struct ThreeDGenerationInputReview: Codable, Equatable, Sendable {
    public var status: ThreeDGenerationInputReviewStatus
    public var title: String
    public var detail: String
    public var routeLabel: String
    public var rows: [ThreeDGenerationInputReviewRow]
    public var privacyNotes: [String]
    public var selectedProviderSourceCount: Int
    public var canForge3D: Bool

    public init(
        status: ThreeDGenerationInputReviewStatus,
        title: String,
        detail: String,
        routeLabel: String,
        rows: [ThreeDGenerationInputReviewRow],
        privacyNotes: [String],
        selectedProviderSourceCount: Int,
        canForge3D: Bool
    ) {
        self.status = status
        self.title = title
        self.detail = detail
        self.routeLabel = routeLabel
        self.rows = rows
        self.privacyNotes = privacyNotes
        self.selectedProviderSourceCount = selectedProviderSourceCount
        self.canForge3D = canForge3D
    }

    public func row(id: String) -> ThreeDGenerationInputReviewRow? {
        rows.first { $0.id == id }
    }
}

public enum ThreeDGenerationInputReviewBuilder {
    public static func build(
        selection: CaptureMediaSelection?,
        generationReadiness: CaptureGenerationReadiness,
        providerReadiness: ProviderReadinessResponse?,
        providerReadinessError: String?
    ) -> ThreeDGenerationInputReview {
        let status = status(for: generationReadiness, providerReadinessError: providerReadinessError)
        let provider = providerReadiness?.providers.first { $0.kind == "three_d" }
        let selectedCount = max(0, generationReadiness.selectedProviderSourceCount)
        let canForge = status == .ready

        return review(
            status: status,
            title: title(for: status),
            detail: detail(
                for: status,
                generationReadiness: generationReadiness,
                providerReadinessError: providerReadinessError
            ),
            routeLabel: generationReadiness.route.displayLabel,
            rows: [
                row(
                    "capture_mode",
                    "Capture mode",
                    status,
                    captureModeDetail(selection)
                ),
                row(
                    "source_media",
                    "Source media",
                    status,
                    sourceMediaDetail(selection)
                ),
                row(
                    "provider_route",
                    "Provider route",
                    status,
                    providerRouteDetail(
                        selection: selection,
                        readiness: generationReadiness
                    )
                ),
                row(
                    "provider",
                    "Provider",
                    status,
                    providerDetail(
                        provider,
                        providerReadinessError: providerReadinessError,
                        generationReadiness: generationReadiness
                    )
                ),
            ],
            selectedProviderSourceCount: selectedCount,
            canForge3D: canForge
        )
    }

    private static func review(
        status: ThreeDGenerationInputReviewStatus,
        title: String,
        detail: String,
        routeLabel: String,
        rows: [ThreeDGenerationInputReviewRow],
        selectedProviderSourceCount: Int,
        canForge3D: Bool
    ) -> ThreeDGenerationInputReview {
        ThreeDGenerationInputReview(
            status: status,
            title: sanitize(title),
            detail: sanitize(detail),
            routeLabel: sanitize(routeLabel),
            rows: rows.map { row($0.id, $0.label, $0.status, $0.detail) },
            privacyNotes: [
                "Raw capture files withheld.",
                "Only counts, content types, and provider route labels are shown.",
                "Provider keys stay backend-only.",
            ],
            selectedProviderSourceCount: selectedProviderSourceCount,
            canForge3D: canForge3D
        )
    }

    private static func status(
        for readiness: CaptureGenerationReadiness,
        providerReadinessError: String?
    ) -> ThreeDGenerationInputReviewStatus {
        if providerReadinessError != nil || readiness.status == .needsAttention {
            return .needsAttention
        }
        if readiness.status == .ready {
            return .ready
        }
        return .waiting
    }

    private static func title(for status: ThreeDGenerationInputReviewStatus) -> String {
        switch status {
        case .waiting:
            return "3D input waiting"
        case .ready:
            return "3D input ready"
        case .needsAttention:
            return "3D input needs attention"
        }
    }

    private static func detail(
        for status: ThreeDGenerationInputReviewStatus,
        generationReadiness: CaptureGenerationReadiness,
        providerReadinessError: String?
    ) -> String {
        if let providerReadinessError {
            return "Provider readiness blocked: \(providerReadinessError)"
        }
        switch status {
        case .waiting:
            return generationReadiness.detail
        case .ready:
            return generationReadiness.detail
        case .needsAttention:
            return generationReadiness.detail
        }
    }

    private static func captureModeDetail(_ selection: CaptureMediaSelection?) -> String {
        guard let selection else {
            return "waiting for capture media"
        }
        return selection.mode.rawValue
    }

    private static func sourceMediaDetail(_ selection: CaptureMediaSelection?) -> String {
        guard let selection else {
            return "No capture media selected."
        }
        switch selection.mode {
        case .singlePhoto:
            return selection.imageCount == 1 ? "1 single photo" : "\(selection.imageCount) single-photo inputs"
        case .photoSet:
            return "\(selection.imageCount) photo set images"
        case .guidedScan:
            return "\(selection.imageCount) guided scan photos"
        case .manualUpload:
            if selection.scanAssetCount > 0 {
                return "\(selection.scanAssetCount) uploaded scan assets + \(selection.imageCount) references"
            }
            return "\(selection.imageCount) uploaded images"
        case .arkitScan:
            let referenceText = selection.imageCount == 1 ? "1 reference" : "\(selection.imageCount) references"
            return "\(selection.scanAssetCount) scan asset + \(referenceText)"
        }
    }

    private static func providerRouteDetail(
        selection: CaptureMediaSelection?,
        readiness: CaptureGenerationReadiness
    ) -> String {
        switch readiness.route {
        case .waiting:
            return "waiting for provider-ready capture media"
        case .textPrompt:
            return "text-to-3D prompt route"
        case .singleImage:
            return "image-to-3D single source image"
        case .multiImage:
            let total = max(selection?.imageCount ?? readiness.sourceCount, readiness.sourceCount)
            return "multi-image 3D; selected \(readiness.selectedProviderSourceCount)/\(total) provider images"
        case .scanAsset:
            return "scan asset handoff; selected \(readiness.selectedProviderSourceCount) provider source"
        }
    }

    private static func providerDetail(
        _ provider: ProviderReadinessItem?,
        providerReadinessError: String?,
        generationReadiness: CaptureGenerationReadiness
    ) -> String {
        if let providerReadinessError {
            return providerReadinessError
        }
        guard let provider else {
            return "Backend 3D readiness has not loaded."
        }
        let name = displayProvider(provider.selectedProvider)
        if provider.isRealProviderReady {
            return "\(name) real provider ready."
        }
        if provider.isDemoReady {
            return "Local demo route ready; \(name) live route needs backend key setup."
        }
        if !provider.missingEnv.isEmpty {
            return "Missing \(provider.missingEnv.joined(separator: ", "))."
        }
        return generationReadiness.detail
    }

    private static func displayProvider(_ raw: String) -> String {
        switch raw.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() {
        case "meshy":
            return "Meshy"
        case "local", "local_stub":
            return "Meshy"
        default:
            return sanitize(raw)
        }
    }

    private static func row(
        _ id: String,
        _ label: String,
        _ status: ThreeDGenerationInputReviewStatus,
        _ detail: String
    ) -> ThreeDGenerationInputReviewRow {
        ThreeDGenerationInputReviewRow(
            id: sanitize(id),
            label: sanitize(label),
            status: status,
            detail: sanitize(detail)
        )
    }

    private static func sanitize(_ value: String) -> String {
        var sanitized = value
        let patterns = [
            #"sk-[A-Za-z0-9._-]+"#,
            #"Bearer\s+[A-Za-z0-9._~+/\-=:-]+"#,
            #"Authorization\s*=\s*Bearer\s+[A-Za-z0-9._~+/\-=:-]+"#,
            #"api[_-]?key\s*[=:]\s*[^\s,;"']+"#,
            #"(private_message|raw_context|message_body)\s*:\s*[^\n]+"#,
            #"local-capture://[^\s,;"']+"#,
            #"file://[^\s,;"']+"#,
            #"/Users/[^\s,;"']+"#,
            #"/tmp/[^\s,;"']+"#,
            #"data:image/[^\s,;"']+"#,
            #"checkout_url\s*=\s*[^\s,;"']+"#,
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
