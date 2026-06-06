import PersonalMythForgeMobileCore
import SwiftUI

struct FinalLaunchStatusView: View {
    let summary: FinalLaunchMobileSummary

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(alignment: .center) {
                VStack(alignment: .leading, spacing: 2) {
                    Text("Final Launch Status")
                        .font(.headline)
                    Text(summary.subtitle)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                        .lineLimit(2)
                }
                Spacer(minLength: 8)
                Text(statusBadge)
                    .font(.caption2.weight(.bold))
                    .foregroundStyle(statusColor)
            }

            if !summary.phaseRows.isEmpty {
                VStack(alignment: .leading, spacing: 6) {
                    ForEach(summary.phaseRows, id: \.id) { row in
                        phaseRow(row)
                    }
                }
            }

            if !summary.resourceActions.isEmpty {
                groupedLines(title: "Resources", lines: summary.resourceActions)
            }

            if !summary.commandRows.isEmpty {
                groupedLines(title: "Commands", lines: summary.commandRows)
            }

            if !summary.notes.isEmpty {
                Text(summary.notes.joined(separator: " "))
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
        switch summary.overallStatus {
        case .blocked:
            return "BLOCKED"
        case .waiting:
            return "WAITING"
        case .ready:
            return "READY"
        }
    }

    private var statusColor: Color {
        color(for: summary.overallStatus)
    }

    private func phaseRow(_ row: FinalLaunchMobilePhaseRow) -> some View {
        HStack(alignment: .firstTextBaseline, spacing: 8) {
            Circle()
                .fill(color(for: row.status))
                .frame(width: 8, height: 8)
            Text(row.label)
                .font(.caption.weight(.semibold))
                .frame(width: 112, alignment: .leading)
                .lineLimit(2)
            Text(row.detail)
                .font(.caption2)
                .foregroundStyle(.secondary)
                .lineLimit(2)
            Spacer(minLength: 0)
        }
    }

    private func groupedLines(title: String, lines: [String]) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title)
                .font(.caption.weight(.semibold))
            ForEach(Array(lines.enumerated()), id: \.offset) { _, line in
                Text(line)
                    .font(.caption2.monospaced())
                    .foregroundStyle(.secondary)
                    .lineLimit(2)
                    .textSelection(.enabled)
            }
        }
    }

    private func color(for status: FinalLaunchMobileStatus) -> Color {
        switch status {
        case .blocked:
            return .red
        case .waiting:
            return .secondary
        case .ready:
            return .green
        }
    }
}
