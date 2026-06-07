import PersonalMythForgeMobileCore
import SwiftUI

struct LiveProviderConsentView: View {
    let summary: LiveProviderConsentSummary

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(alignment: .firstTextBaseline) {
                VStack(alignment: .leading, spacing: 2) {
                    Text("Live Provider Consent")
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

            VStack(alignment: .leading, spacing: 6) {
                ForEach(summary.rows, id: \.id) { row in
                    consentRow(row)
                }
            }

            if let consentFlag = summary.consentFlag, !consentFlag.isEmpty {
                Text(consentFlag)
                    .font(.caption2.monospaced())
                    .foregroundStyle(.secondary)
                    .lineLimit(1)
                    .textSelection(.enabled)
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
        case .blocked:
            return "BLOCKED"
        case .ready:
            return "READY"
        }
    }

    private var statusColor: Color {
        color(for: summary.status)
    }

    private func consentRow(_ row: LiveProviderConsentRow) -> some View {
        HStack(alignment: .firstTextBaseline, spacing: 8) {
            Circle()
                .fill(color(for: row.status))
                .frame(width: 8, height: 8)
            Text(row.label)
                .font(.caption.weight(.semibold))
                .frame(width: 104, alignment: .leading)
                .lineLimit(2)
            Text(row.detail)
                .font(.caption2)
                .foregroundStyle(.secondary)
                .lineLimit(2)
                .textSelection(.enabled)
            Spacer(minLength: 0)
        }
    }

    private func color(for status: LiveProviderConsentStatus) -> Color {
        switch status {
        case .waiting:
            return .secondary
        case .blocked:
            return .red
        case .ready:
            return .green
        }
    }
}
