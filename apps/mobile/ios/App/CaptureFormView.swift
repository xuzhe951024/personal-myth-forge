import PersonalMythForgeMobileCore
import PhotosUI
import SwiftUI

struct CaptureFormView: View {
    @Binding var objectLabel: String
    @Binding var materials: String
    @Binding var visualNotes: String
    @Binding var currentTheme: String
    @Binding var desiredTone: String
    @Binding var selectedCaptureMode: CaptureMode
    @Binding var selectedSinglePhotoItem: PhotosPickerItem?
    @Binding var selectedPhotoItems: [PhotosPickerItem]
    let phase: ForgeFlowPhase
    let mediaSummaryTitle: String
    let mediaSummaryDetail: String
    let captureInputError: String?
    let isMediaReadyForUpload: Bool
    let chooseCapture: () -> Void
    let takePhoto: () -> Void
    let startGuidedScan: () -> Void
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
                .mobileTextInputAutocapitalizationDisabled()
            TextField("Materials", text: $materials)
                .mobileTextInputAutocapitalizationDisabled()
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

            VStack(alignment: .leading, spacing: 8) {
                HStack(alignment: .firstTextBaseline) {
                    VStack(alignment: .leading, spacing: 2) {
                        Text(mediaSummaryTitle)
                            .font(.subheadline.weight(.semibold))
                        Text(mediaSummaryDetail)
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                    Spacer()
                }

                captureInputControls

                if let captureInputError {
                    Text(captureInputError)
                        .font(.caption)
                        .foregroundStyle(.red)
                }
            }
            .padding(10)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(.regularMaterial)
            .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))

            if selectedCaptureMode == .arkitScan || selectedCaptureMode == .guidedScan {
                HStack(alignment: .firstTextBaseline) {
                    Text(scanReadinessTitle)
                        .font(.subheadline.weight(.semibold))
                    Spacer()
                    Text(scanReadinessDetail)
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

            Button("Forge Myth", action: forgeMyth)
                .buttonStyle(.borderedProminent)
                .disabled(!isMediaReadyForUpload)

            Text(statusText)
                .font(.caption)
                .foregroundStyle(.secondary)
        }
    }

    @ViewBuilder
    private var captureInputControls: some View {
        switch selectedCaptureMode {
        case .singlePhoto:
            HStack {
                Button(action: takePhoto) {
                    Label("Take Photo", systemImage: "camera")
                }
                .buttonStyle(.borderedProminent)

                PhotosPicker(selection: $selectedSinglePhotoItem, matching: .images) {
                    Label("Choose Photo", systemImage: "photo")
                }
                .buttonStyle(.bordered)
            }
        case .photoSet:
            PhotosPicker(selection: $selectedPhotoItems, maxSelectionCount: 12, matching: .images) {
                Label("Choose Photos", systemImage: "photo.on.rectangle")
            }
            .buttonStyle(.bordered)
        case .guidedScan:
            VStack(alignment: .leading, spacing: 8) {
                Button(action: startGuidedScan) {
                    Label("Start Guided Scan", systemImage: "camera.viewfinder")
                }
                .buttonStyle(.borderedProminent)

                PhotosPicker(selection: $selectedPhotoItems, maxSelectionCount: 12, matching: .images) {
                    Label("Choose Photos", systemImage: "photo.stack")
                }
                .buttonStyle(.bordered)
            }
        case .manualUpload:
            Button(action: chooseCapture) {
                Label("Choose File", systemImage: "doc")
            }
            .buttonStyle(.bordered)
        case .arkitScan:
            HStack {
                Button(action: chooseCapture) {
                    Label("Choose Scan", systemImage: "cube")
                }
                .buttonStyle(.bordered)

                PhotosPicker(selection: $selectedPhotoItems, maxSelectionCount: 11, matching: .images) {
                    Label("Add References", systemImage: "photo.stack")
                }
                .buttonStyle(.bordered)
            }
        }
    }

    private var captureModeTitle: String {
        switch selectedCaptureMode {
        case .singlePhoto:
            return "Single photo"
        case .photoSet:
            return "Photo set"
        case .guidedScan:
            return "Guided scan"
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
        case .guidedScan:
            return "Object Capture guided photos become one object observation."
        case .manualUpload:
            return "Imported media becomes the object observation."
        case .arkitScan:
            return "A scan asset and references become the object observation."
        }
    }

    private func captureModeLabel(for mode: CaptureMode) -> String {
        switch mode {
        case .singlePhoto:
            return "Photo"
        case .photoSet:
            return "Set"
        case .guidedScan:
            return "Scan"
        case .manualUpload:
            return "File"
        case .arkitScan:
            return "Mesh"
        }
    }

    private var scanReadinessTitle: String {
        switch selectedCaptureMode {
        case .guidedScan:
            return "Guided scan readiness"
        default:
            return "Scan readiness"
        }
    }

    private var scanReadinessDetail: String {
        switch selectedCaptureMode {
        case .guidedScan:
            return "2+ photos"
        default:
            return "mesh + reference"
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

private extension View {
    @ViewBuilder
    func mobileTextInputAutocapitalizationDisabled() -> some View {
        #if os(iOS)
        self.textInputAutocapitalization(.never)
        #else
        self
        #endif
    }
}
