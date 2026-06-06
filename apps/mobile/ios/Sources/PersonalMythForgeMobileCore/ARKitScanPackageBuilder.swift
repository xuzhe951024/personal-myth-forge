import Foundation

public struct ARKitScanExportFile: Equatable, Sendable {
    public let filename: String
    public let contentType: String
    public let data: Data

    public init(filename: String, contentType: String, data: Data) {
        self.filename = filename
        self.contentType = contentType
        self.data = data
    }
}

public struct ARKitScanReferenceImageFile: Equatable, Sendable {
    public let filename: String
    public let contentType: String
    public let data: Data

    public init(filename: String, contentType: String, data: Data) {
        self.filename = filename
        self.contentType = contentType
        self.data = data
    }
}

public enum ARKitScanPackageBuilderError: Error, Equatable, Sendable {
    case unsupportedScanContentType(String)
    case unsupportedReferenceContentType(String)
    case scanTooLarge(Int, Int)
    case referenceTooLarge(String, Int, Int)
}

public enum ARKitScanPackageBuilder {
    public static let maximumReferenceImages = 11

    private static let supportedScanContentTypes: Set<String> = [
        "application/octet-stream",
        "model/gltf-binary",
        "model/vnd.usdz+zip",
    ]

    private static let supportedReferenceContentTypes: Set<String> = [
        "image/heic",
        "image/heif",
        "image/jpeg",
        "image/png",
    ]

    public static func selection(
        scanExport: ARKitScanExportFile,
        referenceImages: [ARKitScanReferenceImageFile] = []
    ) throws -> CaptureMediaSelection {
        let media = try [mediaDraft(from: scanExport)] + referenceImages
            .sorted { lhs, rhs in
                lhs.filename.localizedStandardCompare(rhs.filename) == .orderedAscending
            }
            .prefix(maximumReferenceImages)
            .map(mediaDraft)

        return CaptureMediaSelection(mode: .arkitScan, media: media)
    }

    private static func mediaDraft(from scanExport: ARKitScanExportFile) throws -> CaptureMediaDraft {
        let contentType = normalizedContentType(scanExport.contentType)
        guard supportedScanContentTypes.contains(contentType) else {
            throw ARKitScanPackageBuilderError.unsupportedScanContentType(contentType)
        }
        guard scanExport.data.count <= CaptureDraft.maxFileBytes else {
            throw ARKitScanPackageBuilderError.scanTooLarge(
                scanExport.data.count,
                CaptureDraft.maxFileBytes
            )
        }

        return CaptureMediaDraft(
            originalFilename: scanExport.filename,
            contentType: contentType,
            data: scanExport.data,
            kind: .scanAsset
        )
    }

    private static func mediaDraft(from referenceImage: ARKitScanReferenceImageFile) throws -> CaptureMediaDraft {
        let contentType = normalizedContentType(referenceImage.contentType)
        guard supportedReferenceContentTypes.contains(contentType) else {
            throw ARKitScanPackageBuilderError.unsupportedReferenceContentType(contentType)
        }
        guard referenceImage.data.count <= CaptureDraft.maxFileBytes else {
            throw ARKitScanPackageBuilderError.referenceTooLarge(
                referenceImage.filename,
                referenceImage.data.count,
                CaptureDraft.maxFileBytes
            )
        }

        return CaptureMediaDraft(
            originalFilename: referenceImage.filename,
            contentType: contentType,
            data: referenceImage.data,
            kind: .image
        )
    }

    private static func normalizedContentType(_ contentType: String) -> String {
        contentType
            .trimmingCharacters(in: .whitespacesAndNewlines)
            .lowercased()
    }
}
