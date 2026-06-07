import PersonalMythForgeMobileCore
import SwiftUI

struct ForgeProgressReceiptView: View {
    let receipt: ForgeProgressReceipt

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(alignment: .firstTextBaseline) {
                VStack(alignment: .leading, spacing: 2) {
                    Text("Forge Progress")
                        .font(.subheadline.weight(.semibold))
                    Text(receipt.title)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
                Spacer(minLength: 8)
                Text(statusBadge)
                    .font(.caption2.weight(.bold))
                    .foregroundStyle(statusColor)
            }

            Text(receipt.detail)
                .font(.caption)
                .foregroundStyle(.secondary)
                .lineLimit(3)

            VStack(alignment: .leading, spacing: 5) {
                ForEach(receipt.rows, id: \.label) { row in
                    HStack(alignment: .top, spacing: 6) {
                        Circle()
                            .fill(rowColor(row.status))
                            .frame(width: 7, height: 7)
                            .padding(.top, 4)
                        VStack(alignment: .leading, spacing: 1) {
                            Text("\(row.label) \(row.status)")
                                .font(.caption2.weight(.semibold))
                                .foregroundStyle(.secondary)
                            Text(row.detail)
                                .font(.caption2)
                                .foregroundStyle(.secondary)
                                .lineLimit(2)
                        }
                    }
                }
            }

            if !receipt.privacyNotes.isEmpty {
                Text(receipt.privacyNotes.joined(separator: " "))
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
        switch receipt.status {
        case .waiting:
            return "WAIT"
        case .running:
            return "RUN"
        case .ready:
            return "READY"
        case .needsAttention:
            return "CHECK"
        }
    }

    private var statusColor: Color {
        switch receipt.status {
        case .waiting:
            return .secondary
        case .running:
            return .blue
        case .ready:
            return .green
        case .needsAttention:
            return .orange
        }
    }

    private func rowColor(_ status: String) -> Color {
        switch status {
        case "running":
            return .blue
        case "ready", "uploaded":
            return .green
        case "blocked":
            return .orange
        default:
            return .secondary
        }
    }
}
