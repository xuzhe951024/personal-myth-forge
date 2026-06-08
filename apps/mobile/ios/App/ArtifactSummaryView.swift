import PersonalMythForgeMobileCore
import SwiftUI

struct ArtifactSummaryView: View {
    let session: MythSession?
    let latestTick: NPCAgentTick?
    let onSceneLoadProofChange: @MainActor (ArtifactSceneLoadProof) -> Void

    init(
        session: MythSession?,
        latestTick: NPCAgentTick?,
        onSceneLoadProofChange: @escaping @MainActor (ArtifactSceneLoadProof) -> Void = { _ in }
    ) {
        self.session = session
        self.latestTick = latestTick
        self.onSceneLoadProofChange = onSceneLoadProofChange
    }

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

            Artifact3DPreviewView(
                session: session,
                latestTick: latestTick,
                onSceneLoadProofChange: onSceneLoadProofChange
            )

            GenerationResultReceiptView(
                receipt: GenerationResultReceiptBuilder.build(session: session)
            )

            if let generationProvenance = session?.generatedAsset.generationProvenance {
                ProvenanceSummaryView(
                    summary: ArtifactGenerationProvenanceSummaryBuilder.build(
                        provenance: generationProvenance
                    )
                )
            }
        }
    }
}

private struct ProvenanceSummaryView: View {
    let summary: ArtifactGenerationProvenanceSummary

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text("Generation")
                .font(.subheadline)
                .fontWeight(.semibold)

            HStack(spacing: 8) {
                Text(summary.routeLabel)
                    .font(.caption)
                    .fontWeight(.semibold)
                Text(summary.sourceSummary)
                    .font(.caption)
            }

            Text(summary.providerRoute)
                .font(.caption2)
                .foregroundStyle(.secondary)
                .lineLimit(1)
                .truncationMode(.middle)

            Text(summary.selectionReason)
                .font(.caption2)
                .foregroundStyle(.secondary)
                .lineLimit(2)

            Text(summary.privacySummary)
                .font(.caption2)
                .foregroundStyle(.secondary)
        }
        .padding(10)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.secondary.opacity(0.08))
        .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))
    }
}
