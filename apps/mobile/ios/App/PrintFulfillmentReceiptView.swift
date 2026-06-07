import PersonalMythForgeMobileCore
import SwiftUI

struct PrintFulfillmentReceiptView: View {
    let receipt: PrintFulfillmentReceipt

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(alignment: .firstTextBaseline) {
                VStack(alignment: .leading, spacing: 2) {
                    Text("Print Fulfillment")
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
                ForEach(receipt.rows, id: \.id) { row in
                    fulfillmentRow(row)
                }
            }

            if !receipt.privacyNotes.isEmpty {
                Text(receipt.privacyNotes.joined(separator: " "))
                    .font(.caption2)
                    .foregroundStyle(.secondary)
                    .lineLimit(4)
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
        case .needsApproval:
            return "APPROVE"
        case .ready:
            return "READY"
        case .blocked:
            return "BLOCKED"
        }
    }

    private var statusColor: Color {
        color(for: receipt.status)
    }

    private func fulfillmentRow(_ row: PrintFulfillmentReceiptRow) -> some View {
        HStack(alignment: .top, spacing: 7) {
            Circle()
                .fill(color(for: row.status))
                .frame(width: 7, height: 7)
                .padding(.top, 4)
            VStack(alignment: .leading, spacing: 1) {
                Text(row.label)
                    .font(.caption2.weight(.semibold))
                    .foregroundStyle(.secondary)
                Text(row.detail)
                    .font(.caption2)
                    .foregroundStyle(.secondary)
                    .lineLimit(2)
                    .textSelection(.enabled)
            }
        }
    }

    private func color(for status: PrintFulfillmentReceiptStatus) -> Color {
        switch status {
        case .waiting:
            return .secondary
        case .needsApproval:
            return .orange
        case .ready:
            return .green
        case .blocked:
            return .red
        }
    }
}
