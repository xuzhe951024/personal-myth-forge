import PersonalMythForgeMobileCore
import SwiftUI

struct WorldResolutionView: View {
    let session: MythSession?

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("World State")
                .font(.headline)

            if let session {
                let resolution = session.worldResolution

                Text(resolution.summary)

                if !resolution.visibleChanges.isEmpty {
                    Text("Visible Changes")
                        .font(.subheadline)
                        .fontWeight(.semibold)
                    ForEach(resolution.visibleChanges, id: \.self) { change in
                        Text(change)
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }

                ActionResolutionSection(
                    title: "Accepted Actions",
                    actions: resolution.acceptedActions
                )
                ActionResolutionSection(
                    title: "Rejected Actions",
                    actions: resolution.rejectedActions
                )
            } else {
                Text("World changes appear after the myth session is ready.")
                    .foregroundStyle(.secondary)
            }
        }
    }
}

private struct ActionResolutionSection: View {
    let title: String
    let actions: [ResolvedNPCAction]

    var body: some View {
        if !actions.isEmpty {
            VStack(alignment: .leading, spacing: 8) {
                Text(title)
                    .font(.subheadline)
                    .fontWeight(.semibold)

                ForEach(Array(actions.enumerated()), id: \.offset) { _, action in
                    VStack(alignment: .leading, spacing: 4) {
                        HStack {
                            Text(action.action)
                                .fontWeight(.medium)
                            Spacer()
                            Text(action.status)
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                        Text(action.reason)
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                    .padding(10)
                    .background(.secondary.opacity(0.08))
                    .clipShape(RoundedRectangle(cornerRadius: 8))
                }
            }
        }
    }
}
