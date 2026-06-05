import PersonalMythForgeMobileCore
import SwiftUI

struct CaptureFormView: View {
    @Binding var objectLabel: String
    @Binding var materials: String
    @Binding var visualNotes: String
    @Binding var currentTheme: String
    @Binding var desiredTone: String
    @Binding var selectedCaptureMode: CaptureMode
    let phase: ForgeFlowPhase
    let chooseCapture: () -> Void
    let forgeMyth: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Object Capture")
                .font(.headline)

            Picker("Capture mode", selection: $selectedCaptureMode) {
                ForEach(CaptureMode.allCases, id: \.self) { mode in
                    Text(captureModeLabel(for: mode)).tag(mode)
                }
            }
            .pickerStyle(.segmented)

            TextField("Object label", text: $objectLabel)
                .textInputAutocapitalization(.never)
            TextField("Materials", text: $materials)
                .textInputAutocapitalization(.never)
            TextField("Visual notes", text: $visualNotes, axis: .vertical)
                .lineLimit(3, reservesSpace: true)

            VStack(alignment: .leading, spacing: 6) {
                Text(captureModeTitle)
                    .font(.subheadline.weight(.semibold))
                Text(captureModeDetail)
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            .padding(10)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(.thinMaterial)
            .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))

            if selectedCaptureMode == .arkitScan {
                HStack(alignment: .firstTextBaseline) {
                    Text("Scan readiness")
                        .font(.subheadline.weight(.semibold))
                    Spacer()
                    Text("mesh + reference")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
                .padding(.vertical, 4)
            }

            Text("Context Capsule")
                .font(.headline)
                .padding(.top, 8)
            TextField("Current theme", text: $currentTheme)
            TextField("Desired tone", text: $desiredTone)

            Button(captureActionTitle, action: chooseCapture)
            .buttonStyle(.bordered)

            Button("Forge Myth", action: forgeMyth)
            .buttonStyle(.borderedProminent)

            Text(statusText)
                .font(.caption)
                .foregroundStyle(.secondary)
        }
    }

    private var captureModeTitle: String {
        switch selectedCaptureMode {
        case .singlePhoto:
            return "Single photo"
        case .photoSet:
            return "Photo set"
        case .manualUpload:
            return "Manual upload"
        case .arkitScan:
            return "ARKit scan"
        }
    }

    private var captureModeDetail: String {
        switch selectedCaptureMode {
        case .singlePhoto:
            return "One image becomes the object observation."
        case .photoSet:
            return "Multiple angles become one object observation."
        case .manualUpload:
            return "Imported media becomes the object observation."
        case .arkitScan:
            return "A scan asset and references become the object observation."
        }
    }

    private var captureActionTitle: String {
        switch selectedCaptureMode {
        case .singlePhoto:
            return "Choose Photo"
        case .photoSet:
            return "Choose Photos"
        case .manualUpload:
            return "Choose File"
        case .arkitScan:
            return "Choose Scan"
        }
    }

    private func captureModeLabel(for mode: CaptureMode) -> String {
        switch mode {
        case .singlePhoto:
            return "Photo"
        case .photoSet:
            return "Set"
        case .manualUpload:
            return "File"
        case .arkitScan:
            return "Scan"
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
