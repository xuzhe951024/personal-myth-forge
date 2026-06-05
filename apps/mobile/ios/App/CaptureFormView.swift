import PersonalMythForgeMobileCore
import SwiftUI

struct CaptureFormView: View {
    @Binding var objectLabel: String
    @Binding var materials: String
    @Binding var visualNotes: String
    @Binding var currentTheme: String
    @Binding var desiredTone: String
    let phase: ForgeFlowPhase

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Object Capture")
                .font(.headline)
            TextField("Object label", text: $objectLabel)
                .textInputAutocapitalization(.never)
            TextField("Materials", text: $materials)
                .textInputAutocapitalization(.never)
            TextField("Visual notes", text: $visualNotes, axis: .vertical)
                .lineLimit(3, reservesSpace: true)

            Text("Context Capsule")
                .font(.headline)
                .padding(.top, 8)
            TextField("Current theme", text: $currentTheme)
            TextField("Desired tone", text: $desiredTone)

            Button("Choose Image") {
                // Future Xcode target wires PhotosPicker or camera capture here.
            }
            .buttonStyle(.bordered)

            Button("Forge Myth") {
                // Future Xcode target triggers upload and from-capture session calls.
            }
            .buttonStyle(.borderedProminent)

            Text(statusText)
                .font(.caption)
                .foregroundStyle(.secondary)
        }
    }

    private var statusText: String {
        switch phase {
        case .idle:
            return "Awaiting object"
        case .editingObject:
            return "Ready to upload"
        case .uploadingCapture:
            return "Uploading capture"
        case .creatingSession:
            return "Creating myth session"
        case .ready:
            return "Ready for review"
        case .failed:
            return "Needs attention"
        }
    }
}
