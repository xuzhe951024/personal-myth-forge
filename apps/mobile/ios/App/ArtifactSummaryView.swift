import PersonalMythForgeMobileCore
import SwiftUI

struct ArtifactSummaryView: View {
    let session: MythSession?

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("Artifact")
                .font(.headline)

            if let session {
                Text(session.mythSeed.title)
                    .font(.title3)
                    .fontWeight(.semibold)
                Text(session.mythSeed.personalResonance)
                Text("3D: \(session.generatedAsset.provider) \(session.generatedAsset.format)")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                Text(session.generatedAsset.uri)
                    .font(.caption2)
                    .textSelection(.enabled)
            } else {
                RoundedRectangle(cornerRadius: 8)
                    .fill(.secondary.opacity(0.12))
                    .frame(height: 160)
                    .overlay(Text("Generated artifact preview"))
            }
        }
    }
}
