import Foundation

public struct GuidedScanImageFile: Equatable, Sendable {
    public let filename: String
    public let contentType: String
    public let data: Data

    public init(filename: String, contentType: String, data: Data) {
        self.filename = filename
        self.contentType = contentType
        self.data = data
    }
}

public enum GuidedScanPhotoSetBuilderError: Error, Equatable, Sendable {
    case tooFewImages(Int)
    case unsupportedContentType(String)
    case mediaTooLarge(Int, Int)
}

public enum GuidedScanPhotoSetBuilder {
    public static let maximumImportedImages = 12

    private static let supportedContentTypes: Set<String> = [
        "image/heic",
        "image/heif",
        "image/jpeg",
        "image/png",
    ]

    public static func mediaDrafts(from images: [GuidedScanImageFile]) throws -> [CaptureMediaDraft] {
        guard images.count >= 2 else {
            throw GuidedScanPhotoSetBuilderError.tooFewImages(images.count)
        }

        return try images
            .sorted { lhs, rhs in
                lhs.filename.localizedStandardCompare(rhs.filename) == .orderedAscending
            }
            .prefix(maximumImportedImages)
            .map(mediaDraft)
    }

    private static func mediaDraft(from image: GuidedScanImageFile) throws -> CaptureMediaDraft {
        let contentType = image.contentType
            .trimmingCharacters(in: .whitespacesAndNewlines)
            .lowercased()
        guard supportedContentTypes.contains(contentType) else {
            throw GuidedScanPhotoSetBuilderError.unsupportedContentType(contentType)
        }
        guard image.data.count <= CaptureDraft.maxFileBytes else {
            throw GuidedScanPhotoSetBuilderError.mediaTooLarge(
                image.data.count,
                CaptureDraft.maxFileBytes
            )
        }
        return CaptureMediaDraft(
            originalFilename: image.filename,
            contentType: contentType,
            data: image.data,
            kind: .image
        )
    }
}
