import PersonalMythForgeMobileCore
import SwiftUI

struct NPCReactionsView: View {
    let session: MythSession?

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Village Response")
                .font(.headline)

            if let session {
                ForEach(session.npcReactions, id: \.npcId) { reaction in
                    VStack(alignment: .leading, spacing: 6) {
                        HStack {
                            Text(reaction.name)
                                .fontWeight(.semibold)
                            Spacer()
                            Text(reaction.emotion)
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                        Text(reaction.interpretation)
                        Text(reaction.worldChange)
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                    .padding()
                    .background(.secondary.opacity(0.08))
                    .clipShape(RoundedRectangle(cornerRadius: 8))
                }

                if !session.npcAgentTraces.isEmpty {
                    VStack(alignment: .leading, spacing: 8) {
                        HStack(alignment: .firstTextBaseline) {
                            Text("NPC agent runtime")
                                .font(.headline)
                            Spacer()
                            Text(session.npcAgentRuntime)
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }

                        ForEach(session.npcAgentTraces, id: \.npcId) { trace in
                            VStack(alignment: .leading, spacing: 4) {
                                HStack {
                                    Text(trace.name)
                                        .font(.subheadline.weight(.semibold))
                                    Spacer()
                                    Text(confidenceLabel(trace.confidence))
                                        .font(.caption2.weight(.semibold))
                                        .foregroundStyle(.secondary)
                                }
                                Text(trace.belief)
                                    .font(.caption)
                                Text(trace.intention)
                                    .font(.caption)
                                    .foregroundStyle(.secondary)
                                Text(trace.proposedAction)
                                    .font(.caption.weight(.semibold))
                                Text(trace.rationale)
                                    .font(.caption2)
                                    .foregroundStyle(.secondary)
                            }
                            .padding(10)
                            .background(.tertiary.opacity(0.12))
                            .clipShape(RoundedRectangle(cornerRadius: 8))
                        }
                    }
                }

                Text("Print Review")
                    .font(.headline)
                Text(session.printCandidate.approvalReason)
                Text(session.printCandidate.printabilityNotes.joined(separator: " | "))
                    .font(.caption)
                    .foregroundStyle(.secondary)
            } else {
                Text("NPC interpretations appear after the myth session is ready.")
                    .foregroundStyle(.secondary)
            }
        }
    }

    private func confidenceLabel(_ confidence: Double) -> String {
        "\(Int((confidence * 100).rounded()))%"
    }
}
