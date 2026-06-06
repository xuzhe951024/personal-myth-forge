import SwiftUI

#if os(iOS) && canImport(UIKit)
import UIKit
#endif

struct CameraCaptureView: View {
    let onCapture: (Data) -> Void
    let onFailure: () -> Void
    let onCancel: () -> Void

    var body: some View {
        #if os(iOS) && canImport(UIKit)
        if UIImagePickerController.isSourceTypeAvailable(.camera) {
            CameraImagePicker(
                onCapture: onCapture,
                onFailure: onFailure,
                onCancel: onCancel
            )
        } else {
            CameraUnavailableView(onCancel: onCancel)
        }
        #else
        CameraUnavailableView(onCancel: onCancel)
        #endif
    }
}

private struct CameraUnavailableView: View {
    let onCancel: () -> Void

    var body: some View {
        NavigationStack {
            VStack(alignment: .leading, spacing: 16) {
                Text("Camera unavailable")
                    .font(.headline)
                Text("Use Choose Photo to import an object image on this device.")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                Button(action: onCancel) {
                    Label("Close", systemImage: "xmark")
                }
                .buttonStyle(.bordered)
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .center)
            .padding()
            .navigationTitle("Take Photo")
        }
    }
}

#if os(iOS) && canImport(UIKit)
private struct CameraImagePicker: UIViewControllerRepresentable {
    let onCapture: (Data) -> Void
    let onFailure: () -> Void
    let onCancel: () -> Void

    func makeUIViewController(context: Context) -> UIImagePickerController {
        let picker = UIImagePickerController()
        picker.sourceType = .camera
        picker.cameraCaptureMode = .photo
        picker.delegate = context.coordinator
        return picker
    }

    func updateUIViewController(_ uiViewController: UIImagePickerController, context: Context) {}

    func makeCoordinator() -> Coordinator {
        Coordinator(
            onCapture: onCapture,
            onFailure: onFailure,
            onCancel: onCancel
        )
    }

    final class Coordinator: NSObject, UINavigationControllerDelegate, UIImagePickerControllerDelegate {
        private let onCapture: (Data) -> Void
        private let onFailure: () -> Void
        private let onCancel: () -> Void

        init(
            onCapture: @escaping (Data) -> Void,
            onFailure: @escaping () -> Void,
            onCancel: @escaping () -> Void
        ) {
            self.onCapture = onCapture
            self.onFailure = onFailure
            self.onCancel = onCancel
        }

        func imagePickerController(
            _ picker: UIImagePickerController,
            didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey: Any]
        ) {
            guard
                let image = info[.originalImage] as? UIImage,
                let data = image.jpegData(compressionQuality: 0.88)
            else {
                picker.dismiss(animated: true) {
                    self.onFailure()
                }
                return
            }

            picker.dismiss(animated: true) {
                self.onCapture(data)
            }
        }

        func imagePickerControllerDidCancel(_ picker: UIImagePickerController) {
            picker.dismiss(animated: true) {
                self.onCancel()
            }
        }
    }
}
#endif
