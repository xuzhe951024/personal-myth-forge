import PersonalMythForgeMobileCore
import SwiftUI

struct CaptureGenerationReceiptView: View {
    let receipt: CaptureGenerationReceipt

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(alignment: .firstTextBaseline) {
                VStack(alignment: .leading, spacing: 2) {
                    Text("Capture-to-3D")
                        .font(.headline)
                    Text(receipt.title)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
                Spacer()
                Text(statusBadge)
                    .font(.caption2.weight(.bold))
                    .foregroundStyle(statusColor)
            }

            Text(receipt.detail)
                .font(.caption)
                .foregroundStyle(.secondary)
                .lineLimit(2)

            if !receipt.rows.isEmpty {
                VStack(alignment: .leading, spacing: 4) {
                    ForEach(receipt.rows.prefix(7), id: \.self) { row in
                        Text(row)
                            .font(.caption2)
                            .foregroundStyle(.secondary)
                            .lineLimit(2)
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
        case .ready:
            return .green
        case .needsAttention:
            return .orange
        }
    }
}
