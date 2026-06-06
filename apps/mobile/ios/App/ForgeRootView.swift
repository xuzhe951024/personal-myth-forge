import Foundation
import PersonalMythForgeMobileCore
import PhotosUI
import SwiftUI
import UniformTypeIdentifiers

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
    @State private var mediaSelection = CaptureMediaSelection(mode: .singlePhoto)
    @State private var selectedSinglePhotoItem: PhotosPickerItem?
    @State private var selectedPhotoItems: [PhotosPickerItem] = []
    @State private var isFileImporterPresented = false
    @State private var captureInputError: String?

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
                        selectedSinglePhotoItem: $selectedSinglePhotoItem,
                        selectedPhotoItems: $selectedPhotoItems,
                        phase: state.phase,
                        mediaSummaryTitle: mediaSelection.summary.title,
                        mediaSummaryDetail: mediaSelection.summary.detail,
                        captureInputError: captureInputError,
                        isMediaReadyForUpload: mediaSelection.isReadyForUpload,
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
            .onChange(of: selectedCaptureMode) { mode in
                mediaSelection = mediaSelection.changingMode(to: mode)
                selectedSinglePhotoItem = nil
                selectedPhotoItems = []
                captureInputError = nil
            }
            .onChange(of: selectedSinglePhotoItem?.itemIdentifier) { _ in
                guard let selectedSinglePhotoItem else {
                    return
                }
                Task {
                    await loadPhotoItems([selectedSinglePhotoItem], mode: .singlePhoto)
                }
            }
            .onChange(of: selectedPhotoItems.map(\.itemIdentifier)) { _ in
                let items = selectedPhotoItems
                guard !items.isEmpty else {
                    return
                }
                Task {
                    await loadPhotoItems(items, mode: selectedCaptureMode)
                }
            }
            .fileImporter(
                isPresented: $isFileImporterPresented,
                allowedContentTypes: allowedImportContentTypes,
                allowsMultipleSelection: selectedCaptureMode != .singlePhoto
            ) { result in
                Task {
                    await loadImportedFiles(result)
                }
            }
        }
    }

    private func chooseCapture() {
        isFileImporterPresented = true
    }

    private func forgeMyth() {
        let draft = mediaSelection.captureDraft(
            label: objectLabel,
            materialsText: materials,
            visualNotes: visualNotes,
            source: "phone_capture",
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
                Task { @MainActor in
                    state = nextState
                }
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

    private var allowedImportContentTypes: [UTType] {
        let glb = UTType(filenameExtension: "glb") ?? .data
        let usdz = UTType(filenameExtension: "usdz") ?? .data
        let heic = UTType("public.heic") ?? .image
        let heif = UTType("public.heif") ?? .image
        switch selectedCaptureMode {
        case .singlePhoto, .photoSet:
            return [.jpeg, .png, heic, heif]
        case .manualUpload:
            return [.jpeg, .png, heic, heif, glb, usdz, .data]
        case .arkitScan:
            return [glb, usdz, .data]
        }
    }

    private func loadPhotoItems(_ items: [PhotosPickerItem], mode: CaptureMode) async {
        do {
            var media: [CaptureMediaDraft] = []
            for (index, item) in items.enumerated() {
                guard let data = try await item.loadTransferable(type: Data.self) else {
                    throw CaptureInputLoadError.unreadablePhoto
                }
                let contentType = imageContentType(for: item.supportedContentTypes)
                media.append(
                    CaptureMediaDraft(
                        originalFilename: photoFilename(index: index, contentType: contentType),
                        contentType: contentType,
                        data: data,
                        kind: .image
                    )
                )
            }
            await MainActor.run {
                guard selectedCaptureMode == mode else {
                    return
                }
                guard !media.isEmpty else {
                    captureInputError = "Could not read selected photo data."
                    return
                }
                applyPhotoMedia(media, mode: mode)
                captureInputError = nil
            }
        } catch {
            await MainActor.run {
                guard selectedCaptureMode == mode else {
                    return
                }
                captureInputError = "Could not read selected photos."
            }
        }
    }

    private func loadImportedFiles(_ result: Result<[URL], Error>) async {
        do {
            let urls = try result.get()
            var imported: [CaptureMediaDraft] = []
            for url in urls {
                imported.append(try importedMedia(from: url))
            }
            await MainActor.run {
                guard !imported.isEmpty else {
                    captureInputError = "No files were imported."
                    return
                }
                applyImportedMedia(imported)
                captureInputError = nil
            }
        } catch {
            await MainActor.run {
                captureInputError = "Could not import selected files."
            }
        }
    }

    private func importedMedia(from url: URL) throws -> CaptureMediaDraft {
        let accessed = url.startAccessingSecurityScopedResource()
        defer {
            if accessed {
                url.stopAccessingSecurityScopedResource()
            }
        }
        let data = try Data(contentsOf: url)
        let contentType = contentType(for: UTType(filenameExtension: url.pathExtension), filename: url.lastPathComponent)
        return CaptureMediaDraft(
            originalFilename: url.lastPathComponent,
            contentType: contentType,
            data: data,
            kind: mediaKind(for: contentType)
        )
    }

    @MainActor
    private func applyPhotoMedia(_ media: [CaptureMediaDraft], mode: CaptureMode) {
        guard selectedCaptureMode == mode else {
            return
        }
        if mode == .arkitScan {
            let scanAssets = mediaSelection.media.filter { $0.kind == .scanAsset }
            mediaSelection = CaptureMediaSelection(mode: mode, media: scanAssets + media)
        } else {
            mediaSelection = CaptureMediaSelection(mode: mode, media: media)
        }
    }

    @MainActor
    private func applyImportedMedia(_ media: [CaptureMediaDraft]) {
        if selectedCaptureMode == .arkitScan {
            let referenceImages = mediaSelection.media.filter { $0.kind == .image }
            let scanAssets = media.filter { $0.kind == .scanAsset }
            mediaSelection = CaptureMediaSelection(
                mode: selectedCaptureMode,
                media: scanAssets + referenceImages
            )
        } else {
            mediaSelection = CaptureMediaSelection(mode: selectedCaptureMode, media: media)
        }
    }

    private func imageContentType(for types: [UTType]) -> String {
        if types.contains(where: { $0.conforms(to: .jpeg) }) {
            return "image/jpeg"
        }
        if types.contains(where: { $0.conforms(to: .png) }) {
            return "image/png"
        }
        if types.contains(where: { $0.identifier == "public.heic" }) {
            return "image/heic"
        }
        if types.contains(where: { $0.identifier == "public.heif" }) {
            return "image/heif"
        }
        return "image/jpeg"
    }

    private func contentType(for type: UTType?, filename: String) -> String {
        let lowercasedName = filename.lowercased()
        if type?.conforms(to: .jpeg) == true || lowercasedName.hasSuffix(".jpg") || lowercasedName.hasSuffix(".jpeg") {
            return "image/jpeg"
        }
        if type?.conforms(to: .png) == true || lowercasedName.hasSuffix(".png") {
            return "image/png"
        }
        if lowercasedName.hasSuffix(".heic") {
            return "image/heic"
        }
        if lowercasedName.hasSuffix(".heif") {
            return "image/heif"
        }
        if lowercasedName.hasSuffix(".glb") {
            return "model/gltf-binary"
        }
        if lowercasedName.hasSuffix(".usdz") {
            return "model/vnd.usdz+zip"
        }
        return "application/octet-stream"
    }

    private func mediaKind(for contentType: String) -> CaptureMediaKind {
        if contentType.hasPrefix("image/") {
            return .image
        }
        return .scanAsset
    }

    private func photoFilename(index: Int, contentType: String) -> String {
        switch contentType {
        case "image/png":
            return "photo_\(index).png"
        case "image/heic":
            return "photo_\(index).heic"
        case "image/heif":
            return "photo_\(index).heif"
        default:
            return "photo_\(index).jpg"
        }
    }
}

private enum CaptureInputLoadError: Error {
    case unreadablePhoto
}
