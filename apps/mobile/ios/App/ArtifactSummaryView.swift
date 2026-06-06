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
            }

            Artifact3DPreviewView(session: session)
        }
    }
}
