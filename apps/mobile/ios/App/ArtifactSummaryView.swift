import PersonalMythForgeMobileCore
import SwiftUI

struct ArtifactSummaryView: View {
    let session: MythSession?
    let latestTick: NPCAgentTick?

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

            Artifact3DPreviewView(session: session, latestTick: latestTick)

            if let generationProvenance = session?.generatedAsset.generationProvenance {
                ProvenanceSummaryView(provenance: generationProvenance)
            }
        }
    }
}

private struct ProvenanceSummaryView: View {
    let provenance: GeneratedAssetProvenance

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text("Generation")
                .font(.subheadline)
                .fontWeight(.semibold)

            HStack(spacing: 8) {
                Text(inputModeLabel)
                    .font(.caption)
                    .fontWeight(.semibold)
                Text(sourceImageSummary)
                    .font(.caption)
            }

            if let providerRoute = provenance.providerRoute, !providerRoute.isEmpty {
                Text(providerRoute)
                    .font(.caption2)
                    .foregroundStyle(.secondary)
                    .lineLimit(1)
                    .truncationMode(.middle)
            }

            Text(provenance.rawSourcesIncluded ? "Raw sources retained" : "Raw sources withheld")
                .font(.caption2)
                .foregroundStyle(.secondary)
        }
        .padding(10)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.secondary.opacity(0.08))
        .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))
    }

    private var inputModeLabel: String {
        provenance.inputMode
            .replacingOccurrences(of: "_", with: " ")
            .capitalized
    }

    private var sourceImageSummary: String {
        let selectedSourceImageCount = provenance.selectedSourceImageCount
        if provenance.sourceImageCount == 0 {
            return "Text prompt"
        }
        if let maxSourceImages = provenance.maxSourceImages {
            return "\(selectedSourceImageCount)/\(provenance.sourceImageCount) images, max \(maxSourceImages)"
        }
        return "\(selectedSourceImageCount)/\(provenance.sourceImageCount) images"
    }
}
