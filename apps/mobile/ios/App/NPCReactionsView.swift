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
}
