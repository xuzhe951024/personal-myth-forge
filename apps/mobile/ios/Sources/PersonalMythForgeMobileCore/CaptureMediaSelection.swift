import Foundation

public struct CaptureMediaSelectionSummary: Equatable, Sendable {
    public let title: String
    public let detail: String
    public let isComplete: Bool

    public init(title: String, detail: String, isComplete: Bool) {
        self.title = title
        self.detail = detail
        self.isComplete = isComplete
    }
}

public struct CaptureMediaSelection: Equatable, Sendable {
    public let mode: CaptureMode
    public let media: [CaptureMediaDraft]

    public init(mode: CaptureMode, media: [CaptureMediaDraft] = []) {
        self.mode = mode
        self.media = media
    }

    public var imageCount: Int {
        media.filter { $0.kind == .image }.count
    }

    public var scanAssetCount: Int {
        media.filter { $0.kind == .scanAsset }.count
    }

    public var isReadyForUpload: Bool {
        switch mode {
        case .singlePhoto:
            return media.count == 1 && imageCount == 1
        case .photoSet:
            return (2...12).contains(media.count) && imageCount == media.count
        case .guidedScan:
            return (2...12).contains(media.count) && imageCount == media.count
        case .manualUpload:
            return (1...12).contains(media.count)
        case .arkitScan:
            return (1...12).contains(media.count) && scanAssetCount > 0
        }
    }

    public var summary: CaptureMediaSelectionSummary {
        let names = media.map(\.originalFilename).prefix(3).joined(separator: ", ")
        let overflow = media.count > 3 ? " +\(media.count - 3) more" : ""
        let detail = media.isEmpty ? emptyDetail : names + overflow
        return CaptureMediaSelectionSummary(
            title: title,
            detail: detail,
            isComplete: isReadyForUpload
        )
    }

    public func replacingMedia(_ media: [CaptureMediaDraft]) -> CaptureMediaSelection {
        CaptureMediaSelection(mode: mode, media: media)
    }

    public func changingMode(to mode: CaptureMode) -> CaptureMediaSelection {
        CaptureMediaSelection(mode: mode, media: [])
    }

    public func captureDraft(
        label: String,
        materialsText: String,
        visualNotes: String,
        source: String
    ) -> CaptureDraft {
        CaptureDraft(
            label: label,
            materialsText: materialsText,
            visualNotes: visualNotes,
            source: source,
            mode: mode,
            media: media
        )
    }

    private var title: String {
        switch mode {
        case .singlePhoto:
            return imageCount == 1 ? "1 photo selected" : "Choose 1 photo"
        case .photoSet:
            return imageCount == 1 ? "1 photo selected" : "\(imageCount) photos selected"
        case .guidedScan:
            if imageCount == 0 {
                return "Choose guided scan photos"
            }
            return imageCount == 1
                ? "1 guided scan photo selected"
                : "\(imageCount) guided scan photos selected"
        case .manualUpload:
            return media.count == 1 ? "1 file selected" : "\(media.count) files selected"
        case .arkitScan:
            if scanAssetCount == 0 {
                return "Choose scan file"
            }
            let referenceText = imageCount == 1 ? "1 reference" : "\(imageCount) references"
            return "\(scanAssetCount) scan, \(referenceText)"
        }
    }

    private var emptyDetail: String {
        switch mode {
        case .singlePhoto:
            return "No photo selected"
        case .photoSet:
            return "Choose at least 2 photos"
        case .guidedScan:
            return "Choose at least 2 guided scan photos"
        case .manualUpload:
            return "No file selected"
        case .arkitScan:
            return "Choose a GLB, USDZ, or binary scan"
        }
    }
}
