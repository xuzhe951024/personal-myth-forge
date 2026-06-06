import PersonalMythForgeMobileCore
import SwiftUI

struct NPCAgentModeView: View {
    let summary: NPCAgentModeSummary

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(alignment: .firstTextBaseline) {
                VStack(alignment: .leading, spacing: 2) {
                    Text("NPC Agent Mode")
                        .font(.headline)
                    Text(summary.detail)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                        .lineLimit(2)
                }
                Spacer(minLength: 8)
                Text(statusBadge)
                    .font(.caption2.weight(.bold))
                    .foregroundStyle(statusColor)
            }

            HStack(spacing: 8) {
                metric("Provider", summary.providerLabel)
                metric("Runtime", summary.runtimeLabel)
            }

            HStack(spacing: 8) {
                metric("Traces", "\(summary.traceCount)")
                metric("Ticks", "\(summary.tickHistoryCount)")
            }

            if !summary.missingEnv.isEmpty {
                Text("Missing \(summary.missingEnv.joined(separator: ", "))")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(.orange)
                    .lineLimit(2)
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

    private func metric(_ label: String, _ value: String) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(label)
                .font(.caption2.weight(.semibold))
                .foregroundStyle(.secondary)
            Text(value)
                .font(.caption.weight(.semibold))
                .lineLimit(1)
                .truncationMode(.middle)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(8)
        .background(Color.secondary.opacity(0.08))
        .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))
    }

    private var statusBadge: String {
        switch summary.status {
        case .waiting:
            return "WAIT"
        case .localDemo:
            return "LOCAL"
        case .aiReady:
            return "AI"
        case .needsSetup:
            return "SETUP"
        }
    }

    private var statusColor: Color {
        switch summary.status {
        case .waiting:
            return .secondary
        case .localDemo:
            return .cyan
        case .aiReady:
            return .green
        case .needsSetup:
            return .orange
        }
    }
}
