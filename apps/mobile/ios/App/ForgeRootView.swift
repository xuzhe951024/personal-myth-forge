import PersonalMythForgeMobileCore
import SwiftUI

struct ForgeRootView: View {
    @State private var state = ForgeFlowState()
    @State private var objectLabel = "old brass key"
    @State private var materials = "metal, brass"
    @State private var visualNotes = "worn teeth, circular bow, warm reflections"
    @State private var currentTheme = "deadline pressure"
    @State private var desiredTone = "tender, strange"

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
                        phase: state.phase
                    )
                    ArtifactSummaryView(session: readySession)
                    NPCReactionsView(session: readySession)
                }
                .padding()
            }
            .navigationTitle("Personal Myth Forge")
        }
    }

    private var readySession: MythSession? {
        if case let .ready(session) = state.phase {
            return session
        }
        return nil
    }
}
