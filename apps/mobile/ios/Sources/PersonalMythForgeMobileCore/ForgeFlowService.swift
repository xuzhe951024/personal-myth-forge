public protocol ForgeFlowAPI: Sendable {
    func uploadObjectCapture(metadata: ObjectCaptureMetadata, media: [CaptureUpload]) async throws -> ObjectCapture
    func createMythSessionFromCapture(captureId: String, context: ContextCapsule) async throws -> MythSession
}

public struct ForgeFlowService: Sendable {
    private let api: any ForgeFlowAPI

    public init(api: any ForgeFlowAPI) {
        self.api = api
    }

    public func forge(
        draft: CaptureDraft,
        context: ContextCapsule,
        stateChanged: @Sendable (ForgeFlowState) -> Void = { _ in }
    ) async -> ForgeFlowState {
        var state = ForgeFlowState()
        let payload: CaptureUploadPayload
        do {
            payload = try draft.validatedUploadPayload()
        } catch {
            state = ForgeFlowReducer.reduce(
                state: state,
                event: .requestFailed(.invalidCaptureDraft(String(describing: error)))
            )
            stateChanged(state)
            return state
        }

        state = ForgeFlowReducer.reduce(state: state, event: .setObjectMetadata(payload.metadata))
        stateChanged(state)
        state = ForgeFlowReducer.reduce(state: state, event: .setContextCapsule(context))
        stateChanged(state)
        state = ForgeFlowReducer.reduce(state: state, event: .beginUpload)
        stateChanged(state)

        do {
            let capture = try await api.uploadObjectCapture(
                metadata: payload.metadata,
                media: payload.uploads
            )
            state = ForgeFlowReducer.reduce(state: state, event: .captureUploaded(capture))
            stateChanged(state)
            let session = try await api.createMythSessionFromCapture(
                captureId: capture.captureId,
                context: context
            )
            state = ForgeFlowReducer.reduce(state: state, event: .sessionCreated(session))
            stateChanged(state)
            return state
        } catch let error as ForgeFlowError {
            state = ForgeFlowReducer.reduce(state: state, event: .requestFailed(error))
            stateChanged(state)
            return state
        } catch {
            state = ForgeFlowReducer.reduce(
                state: state,
                event: .requestFailed(.transport(String(describing: error)))
            )
            stateChanged(state)
            return state
        }
    }
}
