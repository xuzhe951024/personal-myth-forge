import Foundation

public enum CaptureGenerationReadinessStatus: String, Codable, Equatable, Sendable {
    case waiting
    case ready
    case needsAttention
}

public enum CaptureGenerationRoute: String, Codable, Equatable, Sendable {
    case waiting
    case textPrompt
    case singleImage
    case multiImage
    case scanAsset

    public var displayLabel: String {
        switch self {
        case .waiting:
            return "waiting"
        case .textPrompt:
            return "text_prompt"
        case .singleImage:
            return "single_image"
        case .multiImage:
            return "multi_image"
        case .scanAsset:
            return "scan_asset"
        }
    }
}

public struct CaptureGenerationReadiness: Codable, Equatable, Sendable {
    public let title: String
    public let detail: String
    public let status: CaptureGenerationReadinessStatus
    public let route: CaptureGenerationRoute
    public let sourceCount: Int
    public let selectedProviderSourceCount: Int

    public init(
        title: String,
        detail: String,
        status: CaptureGenerationReadinessStatus,
        route: CaptureGenerationRoute,
        sourceCount: Int,
        selectedProviderSourceCount: Int
    ) {
        self.title = title
        self.detail = detail
        self.status = status
        self.route = route
        self.sourceCount = sourceCount
        self.selectedProviderSourceCount = selectedProviderSourceCount
    }
}

public enum CaptureGenerationReadinessBuilder {
    public static let maximumProviderSourceImages = 4

    public static func build(
        selection: CaptureMediaSelection?,
        providerReadiness: ProviderReadinessResponse?,
        providerReadinessError: String?
    ) -> CaptureGenerationReadiness {
        guard let selection else {
            return waiting("Capture media needed", "Choose a photo, guided scan, upload, or scan asset.")
        }

        let base = baseReadiness(for: selection)
        guard base.status == .ready else {
            return base
        }

        return withProviderDetail(base, readiness: providerReadiness, error: providerReadinessError)
    }

    private static func baseReadiness(for selection: CaptureMediaSelection) -> CaptureGenerationReadiness {
        guard selection.isReadyForUpload else {
            switch selection.mode {
            case .guidedScan:
                return waiting("Guided scan needs photos", "Capture at least 2 photos for multi-image 3D.")
            case .arkitScan:
                return waiting("Scan model needed", "Import a GLB, USDZ, or binary scan plus optional references.")
            default:
                return waiting("Capture media needed", selection.summary.detail)
            }
        }

        switch selection.mode {
        case .singlePhoto:
            return ready("Single image ready for 3D", "1 photo can drive image-to-3D.", .singleImage, 1, 1)
        case .photoSet:
            return multiImageReady(title: "Photo set ready for 3D", imageCount: selection.imageCount)
        case .guidedScan:
            return multiImageReady(title: "Guided scan ready for 3D", imageCount: selection.imageCount)
        case .arkitScan:
            let referenceText = selection.imageCount == 1 ? "1 reference" : "\(selection.imageCount) references"
            return ready(
                "Scan package ready for 3D",
                "\(selection.scanAssetCount) scan asset + \(referenceText).",
                .scanAsset,
                selection.media.count,
                max(1, selection.scanAssetCount)
            )
        case .manualUpload:
            if selection.scanAssetCount > 0 {
                return ready(
                    "Uploaded scan ready for 3D",
                    "\(selection.scanAssetCount) scan asset selected.",
                    .scanAsset,
                    selection.media.count,
                    selection.scanAssetCount
                )
            }
            if selection.imageCount >= 2 {
                return multiImageReady(title: "Uploaded images ready for 3D", imageCount: selection.imageCount)
            }
            return ready(
                "Uploaded image ready for 3D",
                "1 image can drive image-to-3D.",
                .singleImage,
                selection.imageCount,
                selection.imageCount
            )
        }
    }

    private static func multiImageReady(title: String, imageCount: Int) -> CaptureGenerationReadiness {
        ready(
            title,
            "\(imageCount) photos; provider uses up to \(maximumProviderSourceImages) prepared images.",
            .multiImage,
            imageCount,
            min(imageCount, maximumProviderSourceImages)
        )
    }

    private static func withProviderDetail(
        _ base: CaptureGenerationReadiness,
        readiness: ProviderReadinessResponse?,
        error: String?
    ) -> CaptureGenerationReadiness {
        if let error {
            return replacing(base, status: .needsAttention, detail: sanitize(error))
        }
        guard let threeDProvider = readiness?.providers.first(where: { $0.kind == "three_d" }) else {
            return replacing(base, detail: base.detail + " Backend 3D readiness has not loaded.")
        }
        if threeDProvider.isRealProviderReady {
            return replacing(base, detail: base.detail + " Real 3D provider ready.")
        }
        if threeDProvider.isDemoReady {
            return replacing(base, detail: base.detail + " Local demo route ready; Meshy key needed for live 3D.")
        }
        let missing = threeDProvider.missingEnv.joined(separator: ", ")
        return replacing(
            base,
            status: .needsAttention,
            detail: missing.isEmpty ? "3D provider setup needed." : "Missing \(missing)."
        )
    }

    private static func ready(
        _ title: String,
        _ detail: String,
        _ route: CaptureGenerationRoute,
        _ sourceCount: Int,
        _ selectedProviderSourceCount: Int
    ) -> CaptureGenerationReadiness {
        CaptureGenerationReadiness(
            title: title,
            detail: sanitize(detail),
            status: .ready,
            route: route,
            sourceCount: sourceCount,
            selectedProviderSourceCount: selectedProviderSourceCount
        )
    }

    private static func waiting(_ title: String, _ detail: String) -> CaptureGenerationReadiness {
        CaptureGenerationReadiness(
            title: title,
            detail: sanitize(detail),
            status: .waiting,
            route: .waiting,
            sourceCount: 0,
            selectedProviderSourceCount: 0
        )
    }

    private static func replacing(
        _ readiness: CaptureGenerationReadiness,
        status: CaptureGenerationReadinessStatus? = nil,
        detail: String
    ) -> CaptureGenerationReadiness {
        CaptureGenerationReadiness(
            title: readiness.title,
            detail: sanitize(detail),
            status: status ?? readiness.status,
            route: readiness.route,
            sourceCount: readiness.sourceCount,
            selectedProviderSourceCount: readiness.selectedProviderSourceCount
        )
    }

    private static func sanitize(_ value: String) -> String {
        if value.contains("sk-")
            || value.contains("/Users/")
            || value.contains("file://")
            || value.contains("local-capture://")
            || value.contains("Authorization")
        {
            return "[withheld]"
        }
        return value
    }
}
