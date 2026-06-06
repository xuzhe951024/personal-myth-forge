import Foundation

public enum CaptureMode: String, Codable, Equatable, Hashable, CaseIterable, Sendable {
    case singlePhoto = "single_photo"
    case photoSet = "photo_set"
    case manualUpload = "manual_upload"
    case arkitScan = "arkit_scan"
}

public enum CaptureMediaKind: String, Codable, Equatable, Sendable {
    case image
    case scanAsset
}

public struct CaptureMediaDraft: Equatable, Sendable {
    public let originalFilename: String
    public let contentType: String
    public let data: Data
    public let kind: CaptureMediaKind

    public init(originalFilename: String, contentType: String, data: Data, kind: CaptureMediaKind) {
        self.originalFilename = originalFilename
        self.contentType = contentType
        self.data = data
        self.kind = kind
    }
}

public struct CaptureUploadPayload: Equatable, Sendable {
    public let metadata: ObjectCaptureMetadata
    public let uploads: [CaptureUpload]

    public init(metadata: ObjectCaptureMetadata, uploads: [CaptureUpload]) {
        self.metadata = metadata
        self.uploads = uploads
    }
}

public enum CaptureDraftValidationError: Error, Equatable, Sendable {
    case missingLabel
    case unsupportedContentType(String)
    case invalidMediaCount(CaptureMode, Int)
    case mediaTooLarge(Int, Int)
    case missingScanAsset
}

public struct CaptureDraft: Equatable, Sendable {
    public static let maxFileBytes = 10 * 1024 * 1024

    private static let imageContentTypes: Set<String> = [
        "image/heic",
        "image/heif",
        "image/jpeg",
        "image/png",
    ]
    private static let scanContentTypes: Set<String> = [
        "application/octet-stream",
        "model/gltf-binary",
        "model/vnd.usdz+zip",
    ]

    public let label: String
    public let materialsText: String
    public let visualNotes: String
    public let source: String
    public let mode: CaptureMode
    public let media: [CaptureMediaDraft]

    public init(
        label: String,
        materialsText: String,
        visualNotes: String,
        source: String,
        mode: CaptureMode,
        media: [CaptureMediaDraft]
    ) {
        self.label = label
        self.materialsText = materialsText
        self.visualNotes = visualNotes
        self.source = source
        self.mode = mode
        self.media = media
    }

    public func validatedUploadPayload() throws -> CaptureUploadPayload {
        let trimmedLabel = label.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmedLabel.isEmpty else {
            throw CaptureDraftValidationError.missingLabel
        }

        let normalizedMedia = try media.map(normalizedMedia)
        try validateMediaRules(normalizedMedia)

        let metadata = ObjectCaptureMetadata(
            label: trimmedLabel,
            materials: normalizedMaterials,
            source: source.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ? "phone_capture" : source,
            captureMode: mode.rawValue,
            visualNotes: normalizedVisualNotes
        )
        let uploads = normalizedMedia.map { item in
            CaptureUpload(
                filename: item.originalFilename,
                contentType: item.contentType,
                data: item.data
            )
        }
        return CaptureUploadPayload(metadata: metadata, uploads: uploads)
    }

    private var normalizedMaterials: [String] {
        materialsText
            .split(separator: ",")
            .map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }
            .filter { !$0.isEmpty }
    }

    private var normalizedVisualNotes: String? {
        let value = visualNotes.trimmingCharacters(in: .whitespacesAndNewlines)
        return value.isEmpty ? nil : value
    }

    private func normalizedMedia(_ media: CaptureMediaDraft) throws -> CaptureMediaDraft {
        let contentType = media.contentType
            .trimmingCharacters(in: .whitespacesAndNewlines)
            .lowercased()
        switch media.kind {
        case .image:
            guard Self.imageContentTypes.contains(contentType) else {
                throw CaptureDraftValidationError.unsupportedContentType(contentType)
            }
        case .scanAsset:
            guard Self.scanContentTypes.contains(contentType) else {
                throw CaptureDraftValidationError.unsupportedContentType(contentType)
            }
        }
        guard media.data.count <= Self.maxFileBytes else {
            throw CaptureDraftValidationError.mediaTooLarge(media.data.count, Self.maxFileBytes)
        }
        return CaptureMediaDraft(
            originalFilename: media.originalFilename,
            contentType: contentType,
            data: media.data,
            kind: media.kind
        )
    }

    private func validateMediaRules(_ media: [CaptureMediaDraft]) throws {
        switch mode {
        case .singlePhoto:
            guard media.count == 1, media.allSatisfy({ $0.kind == .image }) else {
                throw CaptureDraftValidationError.invalidMediaCount(mode, media.count)
            }
        case .photoSet:
            guard (2...12).contains(media.count), media.allSatisfy({ $0.kind == .image }) else {
                throw CaptureDraftValidationError.invalidMediaCount(mode, media.count)
            }
        case .manualUpload:
            guard (1...12).contains(media.count) else {
                throw CaptureDraftValidationError.invalidMediaCount(mode, media.count)
            }
        case .arkitScan:
            guard (1...12).contains(media.count) else {
                throw CaptureDraftValidationError.invalidMediaCount(mode, media.count)
            }
            guard media.contains(where: { $0.kind == .scanAsset }) else {
                throw CaptureDraftValidationError.missingScanAsset
            }
        }
    }
}
