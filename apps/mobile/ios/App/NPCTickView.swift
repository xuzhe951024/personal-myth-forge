import PersonalMythForgeMobileCore
import SwiftUI

struct NPCTickView: View {
    let session: MythSession?
    let tick: NPCAgentTick?
    let tickHistoryCount: Int
    let isLoading: Bool
    let errorMessage: String?
    let advanceVillage: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(alignment: .firstTextBaseline) {
                Text("Next Village Tick")
                    .font(.headline)
                Spacer()
                if let tick {
                    Text(tick.agentRuntime)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }

            if tickHistoryCount > 0 {
                Text("\(tickHistoryCount) local ticks saved")
                    .font(.caption2.weight(.semibold))
                    .foregroundStyle(.secondary)
            }

            Button(action: advanceVillage) {
                if isLoading {
                    ProgressView()
                } else {
                    Text("Advance Village")
                }
            }
            .buttonStyle(.borderedProminent)
            .disabled(session == nil || isLoading)

            if let errorMessage {
                Text(errorMessage)
                    .font(.caption)
                    .foregroundStyle(.red)
            }

            if let tick {
                Text("Tick \(tick.tickIndex)")
                    .font(.subheadline.weight(.semibold))

                ForEach(tick.npcAgentTraces, id: \.npcId) { trace in
                    VStack(alignment: .leading, spacing: 4) {
                        HStack {
                            Text(trace.name)
                                .font(.subheadline.weight(.semibold))
                            Spacer()
                            Text(confidenceLabel(trace.confidence))
                                .font(.caption2.weight(.semibold))
                                .foregroundStyle(.secondary)
                        }
                        Text(trace.intention)
                            .font(.caption)
                        Text(trace.proposedAction)
                            .font(.caption.weight(.semibold))
                        Text(trace.rationale)
                            .font(.caption2)
                            .foregroundStyle(.secondary)
                    }
                    .padding(10)
                    .background(.secondary.opacity(0.08))
                    .clipShape(RoundedRectangle(cornerRadius: 8))
                }

                actionGroup(title: "Accepted", actions: tick.worldResolution.acceptedActions)
                actionGroup(title: "Rejected", actions: tick.worldResolution.rejectedActions)

                if !tick.worldResolution.visibleChanges.isEmpty {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Visible Changes")
                            .font(.subheadline.weight(.semibold))
                        ForEach(tick.worldResolution.visibleChanges, id: \.self) { change in
                            Text(change)
                                .font(.caption)
                        }
                    }
                }
            } else if session != nil {
                Text("Advance once the first village response is ready.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
        }
    }

    private func actionGroup(title: String, actions: [ResolvedNPCAction]) -> some View {
        Group {
            if !actions.isEmpty {
                VStack(alignment: .leading, spacing: 4) {
                    Text(title)
                        .font(.subheadline.weight(.semibold))
                    ForEach(actions, id: \.action) { action in
                        Text("\(action.action) - \(action.reason)")
                            .font(.caption)
                            .foregroundStyle(action.status == "accepted" ? .primary : .secondary)
                    }
                }
            }
        }
    }

    private func confidenceLabel(_ confidence: Double) -> String {
        "\(Int((confidence * 100).rounded()))%"
    }
}
