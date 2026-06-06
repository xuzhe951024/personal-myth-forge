import Foundation

public struct ArtifactGenerationProvenanceSummary: Codable, Equatable, Sendable {
    public let title: String
    public let routeLabel: String
    public let sourceSummary: String
    public let providerRoute: String
    public let selectionReason: String
    public let privacySummary: String
    public let isAvailable: Bool

    public init(
        title: String,
        routeLabel: String,
        sourceSummary: String,
        providerRoute: String,
        selectionReason: String,
        privacySummary: String,
        isAvailable: Bool
    ) {
        self.title = title
        self.routeLabel = routeLabel
        self.sourceSummary = sourceSummary
        self.providerRoute = providerRoute
        self.selectionReason = selectionReason
        self.privacySummary = privacySummary
        self.isAvailable = isAvailable
    }
}

public enum ArtifactGenerationProvenanceSummaryBuilder {
    public static func build(provenance: GeneratedAssetProvenance?) -> ArtifactGenerationProvenanceSummary {
        guard let provenance else {
            return ArtifactGenerationProvenanceSummary(
                title: "3D generation route",
                routeLabel: "Waiting",
                sourceSummary: "3D generation provenance has not loaded.",
                providerRoute: "provider route waiting",
                selectionReason: "Source routing will appear after forging.",
                privacySummary: "Raw source media withheld",
                isAvailable: false
            )
        }

        return ArtifactGenerationProvenanceSummary(
            title: "3D generation route",
            routeLabel: routeLabel(provenance.inputMode),
            sourceSummary: sourceSummary(provenance),
            providerRoute: sanitize(provenance.providerRoute ?? "provider route unavailable"),
            selectionReason: sanitize(provenance.selectionReason),
            privacySummary: provenance.rawSourcesIncluded
                ? "Raw source media retained"
                : "Raw source media withheld",
            isAvailable: true
        )
    }

    private static func routeLabel(_ inputMode: String) -> String {
        let label = inputMode
            .trimmingCharacters(in: .whitespacesAndNewlines)
            .replacingOccurrences(of: "_", with: " ")
            .capitalized
        return label.isEmpty ? "Unknown" : label
    }

    private static func sourceSummary(_ provenance: GeneratedAssetProvenance) -> String {
        var parts: [String]
        if provenance.sourceImageCount > 0 {
            let imageText = "\(provenance.selectedSourceImageCount)/\(provenance.sourceImageCount) images selected"
            if let maxSourceImages = provenance.maxSourceImages {
                parts = [imageText, "max \(maxSourceImages)"]
            } else {
                parts = [imageText]
            }
        } else {
            parts = ["Text prompt"]
        }

        if provenance.sourceAssetCount > 0 {
            let assetLabel = provenance.sourceAssetCount == 1 ? "scan asset" : "scan assets"
            parts.append("\(provenance.sourceAssetCount) \(assetLabel)")
        }

        return parts.joined(separator: ", ")
    }

    private static func sanitize(_ text: String) -> String {
        var sanitized = text
        let patterns = [
            #"sk-[A-Za-z0-9._-]+"#,
            #"Bearer\s+[A-Za-z0-9._~+/\-=:-]+"#,
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
