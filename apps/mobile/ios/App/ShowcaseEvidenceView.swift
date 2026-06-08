import PersonalMythForgeMobileCore
import SwiftUI

struct ShowcaseEvidenceView: View {
    let summary: ShowcaseEvidenceSummary

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(alignment: .firstTextBaseline) {
                VStack(alignment: .leading, spacing: 2) {
                    Text("Showcase Evidence")
                        .font(.headline)
                    Text(summary.detail)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                        .lineLimit(2)
                }
                Spacer()
                Text(statusBadge)
                    .font(.caption2.weight(.bold))
                    .foregroundStyle(statusColor)
            }

            Text(summary.title)
                .font(.subheadline.weight(.semibold))
                .lineLimit(2)

            VStack(alignment: .leading, spacing: 6) {
                ForEach(summary.items, id: \.id) { item in
                    HStack(alignment: .firstTextBaseline, spacing: 8) {
                        Circle()
                            .fill(color(for: item.status))
                            .frame(width: 8, height: 8)
                        Text(item.label)
                            .font(.caption.weight(.semibold))
                            .frame(width: 104, alignment: .leading)
                        Text(item.detail)
                            .font(.caption2)
                            .foregroundStyle(.secondary)
                            .lineLimit(2)
                        Spacer(minLength: 0)
                    }
                }
            }

            if !summary.privacyNotes.isEmpty {
                Text(summary.privacyNotes.joined(separator: " "))
                    .font(.caption2)
                    .foregroundStyle(.secondary)
                    .lineLimit(3)
            }
        }
        .padding(10)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(.thinMaterial)
        .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))
    }

    private var statusBadge: String {
        switch summary.status {
        case .waiting:
            return "WAITING"
        case .ready:
            return "READY"
        case .needsAttention:
            return "CHECK"
        }
    }

    private var statusColor: Color {
        switch summary.status {
        case .waiting:
            return .secondary
        case .ready:
            return .green
        case .needsAttention:
            return .orange
        }
    }

    private func color(for status: ShowcaseEvidenceStatus) -> Color {
        switch status {
        case .waiting:
            return .secondary
        case .ready:
            return .green
        case .needsAttention:
            return .orange
        }
    }
}
