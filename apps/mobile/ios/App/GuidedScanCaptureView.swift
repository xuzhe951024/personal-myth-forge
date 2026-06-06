import Foundation
import SwiftUI

#if os(iOS) && canImport(RealityKit)
import RealityKit
#if canImport(_RealityKit_SwiftUI)
import _RealityKit_SwiftUI
#endif
#endif

struct GuidedScanCaptureView: View {
    let onComplete: (URL) -> Void
    let onCancel: () -> Void

    var body: some View {
        #if os(iOS) && canImport(RealityKit) && canImport(_RealityKit_SwiftUI)
        if #available(iOS 17.0, *), ObjectCaptureSession.isSupported {
            GuidedObjectCaptureSessionView(
                onComplete: onComplete,
                onCancel: onCancel
            )
        } else {
            GuidedScanUnsupportedView(onCancel: onCancel)
        }
        #else
        GuidedScanUnsupportedView(onCancel: onCancel)
        #endif
    }
}

private struct GuidedScanUnsupportedView: View {
    let onCancel: () -> Void

    var body: some View {
        NavigationStack {
            VStack(alignment: .leading, spacing: 16) {
                Text("Object Capture is only available on supported iOS devices.")
                    .font(.headline)
                Button(action: onCancel) {
                    Label("Close", systemImage: "xmark")
                }
                .buttonStyle(.bordered)
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .center)
            .padding()
            .navigationTitle("Guided Scan")
        }
    }
}

#if os(iOS) && canImport(RealityKit) && canImport(_RealityKit_SwiftUI)
@available(iOS 17.0, *)
private struct GuidedObjectCaptureSessionView: View {
    let onComplete: (URL) -> Void
    let onCancel: () -> Void

    @State private var session = ObjectCaptureSession()
    @State private var imagesDirectory: URL?
    @State private var didStartSession = false
    @State private var didComplete = false
    @State private var canRequestImageCapture = false
    @State private var shotsTaken = 0
    @State private var statusText = "Preparing scan"

    var body: some View {
        ZStack(alignment: .bottom) {
            ObjectCaptureView(session: session)
                .ignoresSafeArea()

            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    VStack(alignment: .leading, spacing: 2) {
                        Text(statusText)
                            .font(.subheadline.weight(.semibold))
                        Text("\(shotsTaken) photos captured")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                    Spacer()
                }

                HStack(spacing: 10) {
                    Button {
                        session.requestImageCapture()
                    } label: {
                        Label("Capture", systemImage: "camera")
                    }
                    .buttonStyle(.borderedProminent)
                    .disabled(!canRequestImageCapture)

                    Button {
                        finishScan()
                    } label: {
                        Label("Finish", systemImage: "checkmark")
                    }
                    .buttonStyle(.bordered)
                    .disabled(shotsTaken < 2)

                    Button {
                        session.cancel()
                        onCancel()
                    } label: {
                        Label("Cancel", systemImage: "xmark")
                    }
                    .buttonStyle(.bordered)
                }
            }
            .padding(12)
            .background(.regularMaterial)
            .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))
            .padding()
        }
        .task {
            startSessionIfNeeded()
        }
        .task {
            await observeCaptureReadiness()
        }
        .task {
            await observeShotCount()
        }
        .task {
            await observeSessionState()
        }
    }

    private func startSessionIfNeeded() {
        guard !didStartSession else {
            return
        }
        didStartSession = true

        do {
            let scanID = UUID().uuidString
            let baseDirectory = FileManager.default.temporaryDirectory
                .appendingPathComponent("PersonalMythForgeGuidedScans", isDirectory: true)
            let imageDirectory = baseDirectory
                .appendingPathComponent("\(scanID)-images", isDirectory: true)
            let checkpointDirectory = baseDirectory
                .appendingPathComponent("\(scanID)-checkpoints", isDirectory: true)

            try FileManager.default.createDirectory(
                at: imageDirectory,
                withIntermediateDirectories: true
            )
            try FileManager.default.createDirectory(
                at: checkpointDirectory,
                withIntermediateDirectories: true
            )

            var configuration = ObjectCaptureSession.Configuration()
            configuration.checkpointDirectory = checkpointDirectory
            configuration.isOverCaptureEnabled = true
            imagesDirectory = imageDirectory

            session.start(imagesDirectory: imageDirectory, configuration: configuration)
            _ = session.startDetecting()
            statusText = "Find the object"
        } catch {
            statusText = "Could not start scan"
        }
    }

    private func observeCaptureReadiness() async {
        for await canRequest in session.canRequestImageCaptureUpdates {
            canRequestImageCapture = canRequest
        }
    }

    private func observeShotCount() async {
        for await count in session.numberOfShotsTakenUpdates {
            shotsTaken = count
        }
    }

    private func observeSessionState() async {
        for await state in session.stateUpdates {
            statusText = stateLabel(for: state)
            if case .completed = state {
                completeScanIfReady()
            }
        }
    }

    private func finishScan() {
        session.finish()
        completeScanIfReady()
    }

    private func completeScanIfReady() {
        guard !didComplete, let imagesDirectory else {
            return
        }
        didComplete = true
        onComplete(imagesDirectory)
    }

    private func stateLabel(for state: ObjectCaptureSession.CaptureState) -> String {
        switch state {
        case .initializing:
            return "Preparing scan"
        case .ready:
            return "Ready to capture"
        case .detecting:
            return "Finding object"
        case .capturing:
            return "Capturing object"
        case .finishing:
            return "Finishing scan"
        case .completed:
            return "Scan complete"
        case let .failed(error):
            return error.localizedDescription
        @unknown default:
            return "Scanning"
        }
    }
}
#endif
