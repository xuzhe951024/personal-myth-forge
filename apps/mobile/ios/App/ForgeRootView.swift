import Foundation
import PersonalMythForgeMobileCore
import SwiftUI

struct ForgeRootView: View {
    private let forgeService = ForgeFlowService(
        api: PersonalMythForgeAPIClient(baseURL: AppConfiguration.backendBaseURL)
    )

    @State private var state = ForgeFlowState()
    @State private var objectLabel = "old brass key"
    @State private var materials = "metal, brass"
    @State private var visualNotes = "worn teeth, circular bow, warm reflections"
    @State private var currentTheme = "deadline pressure"
    @State private var desiredTone = "tender, strange"
    @State private var selectedCaptureMode = CaptureMode.singlePhoto
    @State private var selectedMedia = [
        CaptureMediaDraft(
            originalFilename: "sample.jpg",
            contentType: "image/jpeg",
            data: Data("sample-image".utf8),
            kind: .image
        )
    ]

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    CaptureFormView(
                        objectLabel: $objectLabel,
                        materials: $materials,
                        visualNotes: $visualNotes,
                        currentTheme: $currentTheme,
                        desiredTone: $desiredTone,
                        selectedCaptureMode: $selectedCaptureMode,
                        phase: state.phase,
                        chooseCapture: chooseCapture,
                        forgeMyth: forgeMyth
                    )
                    ArtifactSummaryView(session: readySession)
                    WorldResolutionView(session: readySession)
                    NPCReactionsView(session: readySession)
                }
                .padding()
            }
            .navigationTitle("Personal Myth Forge")
        }
    }

    private func chooseCapture() {
        selectedMedia = sampleMedia(for: selectedCaptureMode)
    }

    private func forgeMyth() {
        let draft = CaptureDraft(
            label: objectLabel,
            materialsText: materials,
            visualNotes: visualNotes,
            source: "phone_capture",
            mode: selectedCaptureMode,
            media: selectedMedia
        )
        let context = ContextCapsule(
            currentTheme: currentTheme,
            desiredTone: desiredTone
        )

        Task {
            let finalState = await forgeService.forge(
                draft: draft,
                context: context
            ) { nextState in
                state = nextState
            }
            state = finalState
        }
    }

    private var readySession: MythSession? {
        if case let .ready(session) = state.phase {
            return session
        }
        return nil
    }

    private func sampleMedia(for mode: CaptureMode) -> [CaptureMediaDraft] {
        switch mode {
        case .singlePhoto:
            return [
                CaptureMediaDraft(
                    originalFilename: "sample.jpg",
                    contentType: "image/jpeg",
                    data: Data("sample-image".utf8),
                    kind: .image
                )
            ]
        case .photoSet:
            return [
                CaptureMediaDraft(
                    originalFilename: "front.jpg",
                    contentType: "image/jpeg",
                    data: Data("front-image".utf8),
                    kind: .image
                ),
                CaptureMediaDraft(
                    originalFilename: "side.png",
                    contentType: "image/png",
                    data: Data("side-image".utf8),
                    kind: .image
                ),
            ]
        case .manualUpload:
            return [
                CaptureMediaDraft(
                    originalFilename: "manual.glb",
                    contentType: "model/gltf-binary",
                    data: Data("manual-glb".utf8),
                    kind: .scanAsset
                )
            ]
        case .arkitScan:
            return [
                CaptureMediaDraft(
                    originalFilename: "scan.glb",
                    contentType: "model/gltf-binary",
                    data: Data("scan-glb".utf8),
                    kind: .scanAsset
                ),
                CaptureMediaDraft(
                    originalFilename: "reference.jpg",
                    contentType: "image/jpeg",
                    data: Data("reference-image".utf8),
                    kind: .image
                ),
            ]
        }
    }
}
