public struct ForgeFlowState: Equatable {
    public var phase: ForgeFlowPhase
    public var metadata: ObjectCaptureMetadata?
    public var context: ContextCapsule?
    public var capture: ObjectCapture?

    public init(
        phase: ForgeFlowPhase = .idle,
        metadata: ObjectCaptureMetadata? = nil,
        context: ContextCapsule? = nil,
        capture: ObjectCapture? = nil
    ) {
        self.phase = phase
        self.metadata = metadata
        self.context = context
        self.capture = capture
    }
}

public enum ForgeFlowPhase: Equatable {
    case idle
    case editingObject
    case uploadingCapture
    case creatingSession
    case ready(MythSession)
    case failed(ForgeFlowError)
}

public enum ForgeFlowEvent: Equatable {
    case setObjectMetadata(ObjectCaptureMetadata)
    case setContextCapsule(ContextCapsule)
    case beginUpload
    case captureUploaded(ObjectCapture)
    case sessionCreated(MythSession)
    case requestFailed(ForgeFlowError)
    case reset
}

public enum ForgeFlowReducer {
    public static func reduce(state: ForgeFlowState, event: ForgeFlowEvent) -> ForgeFlowState {
        var next = state
        switch event {
        case let .setObjectMetadata(metadata):
            next.metadata = metadata
            next.phase = .editingObject
        case let .setContextCapsule(context):
            next.context = context
            next.phase = .editingObject
        case .beginUpload:
            next.phase = .uploadingCapture
        case let .captureUploaded(capture):
            next.capture = capture
            next.phase = .creatingSession
        case let .sessionCreated(session):
            next.phase = .ready(session)
        case let .requestFailed(error):
            next.phase = .failed(error)
        case .reset:
            next = ForgeFlowState()
        }
        return next
    }
}
