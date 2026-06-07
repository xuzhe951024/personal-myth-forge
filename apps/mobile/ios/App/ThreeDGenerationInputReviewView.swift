import PersonalMythForgeMobileCore
import SwiftUI

struct ThreeDGenerationInputReviewView: View {
    let review: ThreeDGenerationInputReview

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(alignment: .firstTextBaseline) {
                VStack(alignment: .leading, spacing: 2) {
                    Text("3D Generation Input")
                        .font(.subheadline.weight(.semibold))
                    Text(review.title)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
                Spacer(minLength: 8)
                VStack(alignment: .trailing, spacing: 2) {
                    Text(statusBadge)
                        .font(.caption2.weight(.bold))
                        .foregroundStyle(statusColor)
                    Text(review.routeLabel)
                        .font(.caption.monospaced().weight(.semibold))
                        .foregroundStyle(.secondary)
                        .lineLimit(1)
                }
            }

            Text(review.detail)
                .font(.caption)
                .foregroundStyle(.secondary)
                .lineLimit(3)

            VStack(alignment: .leading, spacing: 5) {
                ForEach(review.rows, id: \.id) { row in
                    inputRow(row)
                }
            }

            if !review.privacyNotes.isEmpty {
                Text(review.privacyNotes.joined(separator: " "))
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
        switch review.status {
        case .waiting:
            return "WAIT"
        case .ready:
            return "READY"
        case .needsAttention:
            return "CHECK"
        }
    }

    private var statusColor: Color {
        color(for: review.status)
    }

    private func inputRow(_ row: ThreeDGenerationInputReviewRow) -> some View {
        HStack(alignment: .top, spacing: 7) {
            Circle()
                .fill(color(for: row.status))
                .frame(width: 7, height: 7)
                .padding(.top, 4)
            Text(row.label)
                .font(.caption2.weight(.semibold))
                .foregroundStyle(.secondary)
                .frame(width: 86, alignment: .leading)
                .lineLimit(2)
            Text(row.detail)
                .font(.caption2)
                .foregroundStyle(.secondary)
                .lineLimit(2)
                .textSelection(.enabled)
        }
    }

    private func color(for status: ThreeDGenerationInputReviewStatus) -> Color {
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
