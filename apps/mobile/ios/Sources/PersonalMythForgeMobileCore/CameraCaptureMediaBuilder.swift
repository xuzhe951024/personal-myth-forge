import Foundation

public enum CameraCaptureMediaBuilder {
    public static let filename = "camera-capture.jpg"
    public static let contentType = "image/jpeg"

    public static func singlePhotoSelection(jpegData: Data) -> CaptureMediaSelection {
        CaptureMediaSelection(
            mode: .singlePhoto,
            media: [
                CaptureMediaDraft(
                    originalFilename: filename,
                    contentType: contentType,
                    data: jpegData,
                    kind: .image
                )
            ]
        )
    }
}
