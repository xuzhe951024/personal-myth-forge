import Foundation
import PersonalMythForgeMobileCore
import PhotosUI
import SwiftUI
import UniformTypeIdentifiers

struct ForgeRootView: View {
    private let apiClient: PersonalMythForgeAPIClient
    private let forgeService: ForgeFlowService
    private let demoSnapshotStore: DemoRunSnapshotFileStore

    @State private var state = ForgeFlowState()
    @State private var providerReadiness: ProviderReadinessResponse?
    @State private var providerReadinessError: String?
    @State private var restoredSnapshot: DemoRunSnapshot?
    @State private var npcTickHistory: [NPCAgentTick] = []
    @State private var snapshotStatusText: String?
    @State private var backendHistoryStatusText: String?
    @State private var isSyncingBackendHistory = false
    @State private var npcTickError: String?
    @State private var isAdvancingNPCTick = false
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
    @State private var isGuidedScanPresented = false
    @State private var captureInputError: String?

    init(
        apiClient: PersonalMythForgeAPIClient = PersonalMythForgeAPIClient(
            baseURL: AppConfiguration.backendBaseURL
        ),
        demoSnapshotStore: DemoRunSnapshotFileStore = .live()
    ) {
        self.apiClient = apiClient
        self.forgeService = ForgeFlowService(api: apiClient)
        self.demoSnapshotStore = demoSnapshotStore
    }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    DemoSnapshotStatusView(
                        restoredTitle: restoredSnapshot?.session.mythSeed.title,
                        savedAt: restoredSnapshot?.savedAt,
                        tickCount: npcTickHistory.count,
                        statusText: snapshotStatusText,
                        backendHistoryStatusText: backendHistoryStatusText,
                        isSyncingBackendHistory: isSyncingBackendHistory,
                        clearSnapshot: clearDemoRunSnapshot
                    )
                    ProviderReadinessView(readiness: providerReadiness, errorMessage: providerReadinessError)
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
                        startGuidedScan: startGuidedScan,
                        forgeMyth: forgeMyth
                    )
                    ArtifactSummaryView(session: readySession)
                    WorldResolutionView(session: readySession)
                    NPCReactionsView(session: readySession)
                    NPCTickView(
                        session: readySession,
                        tick: latestNPCTick,
                        tickHistoryCount: npcTickHistory.count,
                        isLoading: isAdvancingNPCTick,
                        errorMessage: npcTickError,
                        advanceVillage: advanceNPCTick
                    )
                }
                .padding()
            }
            .navigationTitle("Personal Myth Forge")
            .task {
                let restoredSessionId = restoreDemoRunSnapshot()
                if let restoredSessionId {
                    await syncBackendHistory(for: restoredSessionId)
                }
                await loadProviderReadiness()
            }
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
            .sheet(isPresented: $isGuidedScanPresented) {
                GuidedScanCaptureView(
                    onComplete: { directory in
                        isGuidedScanPresented = false
                        Task {
                            await loadGuidedScanDirectory(directory)
                        }
                    },
                    onCancel: {
                        isGuidedScanPresented = false
                    }
                )
            }
        }
    }

    private func loadProviderReadiness() async {
        do {
            let readiness = try await apiClient.getProviderReadiness()
            await MainActor.run {
                providerReadiness = readiness
                providerReadinessError = nil
            }
        } catch {
            await MainActor.run {
                providerReadinessError = "Backend preflight is not reachable yet."
            }
        }
    }

    @discardableResult
    private func restoreDemoRunSnapshot() -> String? {
        do {
            guard let snapshot = try demoSnapshotStore.load() else {
                return nil
            }
            state = ForgeFlowReducer.reduce(state: state, event: .sessionCreated(snapshot.session))
            npcTickHistory = snapshot.npcTicks
            restoredSnapshot = snapshot
            snapshotStatusText = "Loaded local demo state. No raw capture media was restored."
            return snapshot.session.sessionId
        } catch {
            snapshotStatusText = "Could not load local demo state."
            return nil
        }
    }

    private func saveDemoRunSnapshot(session: MythSession, ticks: [NPCAgentTick]) {
        let snapshot = DemoRunSnapshot(
            savedAt: currentSnapshotTimestamp(),
            session: session,
            npcTicks: ticks
        )
        do {
            try demoSnapshotStore.save(snapshot)
            restoredSnapshot = snapshot
            snapshotStatusText = "Saved local demo state."
        } catch {
            snapshotStatusText = "Could not save local demo state."
        }
    }

    private func clearDemoRunSnapshot() {
        do {
            try demoSnapshotStore.clear()
            restoredSnapshot = nil
            npcTickHistory = []
            snapshotStatusText = "Cleared local demo state."
            backendHistoryStatusText = nil
            isSyncingBackendHistory = false
            if readySession != nil {
                state = ForgeFlowReducer.reduce(state: state, event: .reset)
            }
        } catch {
            snapshotStatusText = "Could not clear local demo state."
        }
    }

    private func chooseCapture() {
        isFileImporterPresented = true
    }

    private func startGuidedScan() {
        selectedCaptureMode = .guidedScan
        captureInputError = nil
        isGuidedScanPresented = true
    }

    private func forgeMyth() {
        npcTickHistory = []
        restoredSnapshot = nil
        snapshotStatusText = nil
        backendHistoryStatusText = nil
        isSyncingBackendHistory = false
        npcTickError = nil
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
            if case let .ready(session) = finalState.phase {
                saveDemoRunSnapshot(session: session, ticks: [])
            }
        }
    }

    private func advanceNPCTick() {
        guard let session = readySession else {
            return
        }
        isAdvancingNPCTick = true
        npcTickError = nil

        Task {
            if MythSessionID.isValid(session.sessionId) {
                await advanceBackendNPCTick(session: session)
            } else {
                await advanceStatelessNPCTick(session: session)
            }
        }
    }

    private func advanceBackendNPCTick(session: MythSession) async {
        do {
            let history = try await apiClient.advanceMythSessionHistory(sessionId: session.sessionId)
            await MainActor.run {
                _ = applyBackendHistory(history)
                isAdvancingNPCTick = false
                npcTickError = nil
            }
        } catch {
            await MainActor.run {
                isAdvancingNPCTick = false
                npcTickError = "Server history advance is not reachable yet."
            }
        }
    }

    private func advanceStatelessNPCTick(session: MythSession) async {
        let nextTickIndex = (latestNPCTick?.tickIndex ?? 0) + 1
        let recentEvents = latestNPCTick?.worldResolution.visibleChanges
            ?? session.worldResolution.visibleChanges

        do {
            let tick = try await apiClient.createNPCAgentTick(
                session: session,
                tickIndex: nextTickIndex,
                recentEvents: recentEvents
            )
            await MainActor.run {
                let updatedTicks = DemoRunSnapshot(
                    savedAt: currentSnapshotTimestamp(),
                    session: session,
                    npcTicks: npcTickHistory + [tick]
                ).npcTicks
                npcTickHistory = updatedTicks
                saveDemoRunSnapshot(session: session, ticks: updatedTicks)
                isAdvancingNPCTick = false
                npcTickError = nil
            }
        } catch {
            await MainActor.run {
                isAdvancingNPCTick = false
                npcTickError = "NPC tick is not reachable yet."
            }
        }
    }

    private var readySession: MythSession? {
        if case let .ready(session) = state.phase {
            return session
        }
        return nil
    }

    private var latestNPCTick: NPCAgentTick? {
        npcTickHistory.last
    }

    private func syncBackendHistory(for sessionId: String) async {
        guard MythSessionID.isValid(sessionId) else {
            await MainActor.run {
                backendHistoryStatusText = "Backend history is unavailable for this legacy demo session."
            }
            return
        }

        await MainActor.run {
            isSyncingBackendHistory = true
            backendHistoryStatusText = nil
        }

        do {
            let history = try await apiClient.getMythSessionHistory(sessionId: sessionId)
            await MainActor.run {
                let restoredTickCount = applyBackendHistory(history)
                isSyncingBackendHistory = false
                backendHistoryStatusText = "Backend history synced. \(restoredTickCount) NPC ticks restored."
            }
        } catch {
            await MainActor.run {
                isSyncingBackendHistory = false
                backendHistoryStatusText = "Backend history not reachable; using local demo state."
            }
        }
    }

    @discardableResult
    private func applyBackendHistory(_ history: MythSessionHistory) -> Int {
        let snapshot = DemoRunSnapshot(history: history, savedAt: currentSnapshotTimestamp())
        state = ForgeFlowReducer.reduce(state: state, event: .sessionCreated(snapshot.session))
        npcTickHistory = snapshot.npcTicks
        restoredSnapshot = snapshot
        do {
            try demoSnapshotStore.save(snapshot)
            snapshotStatusText = "Updated local demo state from backend history."
        } catch {
            snapshotStatusText = "Could not save backend history locally."
        }
        return snapshot.npcTicks.count
    }

    private func currentSnapshotTimestamp() -> String {
        ISO8601DateFormatter().string(from: Date())
    }

    private var allowedImportContentTypes: [UTType] {
        let glb = UTType(filenameExtension: "glb") ?? .data
        let usdz = UTType(filenameExtension: "usdz") ?? .data
        let heic = UTType("public.heic") ?? .image
        let heif = UTType("public.heif") ?? .image
        switch selectedCaptureMode {
        case .singlePhoto, .photoSet, .guidedScan:
            return [.jpeg, .png, heic, heif]
        case .manualUpload:
            return [.jpeg, .png, heic, heif, glb, usdz, .data]
        case .arkitScan:
            return [glb, usdz, .data]
        }
    }

    private func loadGuidedScanDirectory(_ directory: URL) async {
        do {
            let images = try guidedScanImageFiles(in: directory)
            let media = try GuidedScanPhotoSetBuilder.mediaDrafts(from: images)
            await MainActor.run {
                selectedCaptureMode = .guidedScan
                mediaSelection = CaptureMediaSelection(mode: .guidedScan, media: media)
                selectedSinglePhotoItem = nil
                selectedPhotoItems = []
                captureInputError = nil
                isGuidedScanPresented = false
            }
        } catch {
            await MainActor.run {
                captureInputError = "Could not import guided scan photos."
                isGuidedScanPresented = false
            }
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

    private func guidedScanImageFiles(in directory: URL) throws -> [GuidedScanImageFile] {
        let urls = try FileManager.default.contentsOfDirectory(
            at: directory,
            includingPropertiesForKeys: [.isRegularFileKey],
            options: [.skipsHiddenFiles]
        )
        return try urls.compactMap { url in
            let values = try url.resourceValues(forKeys: [.isRegularFileKey])
            guard values.isRegularFile == true else {
                return nil
            }
            let contentType = contentType(
                for: UTType(filenameExtension: url.pathExtension),
                filename: url.lastPathComponent
            )
            guard guidedScanContentTypes.contains(contentType) else {
                return nil
            }
            return GuidedScanImageFile(
                filename: url.lastPathComponent,
                contentType: contentType,
                data: try Data(contentsOf: url)
            )
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

    private var guidedScanContentTypes: Set<String> {
        [
            "image/heic",
            "image/heif",
            "image/jpeg",
            "image/png",
        ]
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
