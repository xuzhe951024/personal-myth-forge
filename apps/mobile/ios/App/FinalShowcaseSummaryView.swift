import PersonalMythForgeMobileCore
import SwiftUI

struct FinalShowcaseSummaryView: View {
    let summary: FinalShowcaseSummary

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(alignment: .firstTextBaseline) {
                VStack(alignment: .leading, spacing: 2) {
                    Text("Final Showcase")
                        .font(.headline)
                    Text(statusTitle)
                        .font(.caption)
                        .foregroundStyle(.secondary)
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
                ForEach(summary.stages, id: \.id) { stage in
                    HStack(alignment: .firstTextBaseline, spacing: 8) {
                        Circle()
                            .fill(color(for: stage.status))
                            .frame(width: 8, height: 8)
                        Text(stage.label)
                            .font(.caption.weight(.semibold))
                            .frame(width: 70, alignment: .leading)
                        Text(stage.detail)
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

    private var statusTitle: String {
        switch summary.overallStatus {
        case .waiting:
            return "Waiting for first complete run"
        case .readyForLocalDemo:
            return "Ready for local demo"
        case .needsAttention:
            return "Needs attention before demo"
        }
    }

    private var statusBadge: String {
        switch summary.overallStatus {
        case .waiting:
            return "WAITING"
        case .readyForLocalDemo:
            return "READY"
        case .needsAttention:
            return "CHECK"
        }
    }

    private var statusColor: Color {
        switch summary.overallStatus {
        case .waiting:
            return .secondary
        case .readyForLocalDemo:
            return .green
        case .needsAttention:
            return .orange
        }
    }

    private func color(for status: FinalShowcaseStageStatus) -> Color {
        switch status {
        case .waiting:
            return .secondary
        case .ready:
            return .green
        case .needsAttention:
            return .orange
        case .optional:
            return .cyan
        }
    }
}
