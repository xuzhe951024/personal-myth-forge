import PersonalMythForgeMobileCore
import SwiftUI

struct ContextCapsuleReviewView: View {
    let review: ContextCapsuleReview
    @Binding var isApproved: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(alignment: .firstTextBaseline) {
                VStack(alignment: .leading, spacing: 2) {
                    Text("Context Capsule Review")
                        .font(.subheadline.weight(.semibold))
                    Text(review.detail)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                        .lineLimit(2)
                }
                Spacer(minLength: 8)
                Text(statusBadge)
                    .font(.caption2.weight(.bold))
                    .foregroundStyle(statusColor)
            }

            ForEach(Array(review.summaryLines.enumerated()), id: \.offset) { _, line in
                Text(line)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .lineLimit(2)
            }

            Toggle("Approve Capsule", isOn: $isApproved)
                .font(.caption.weight(.semibold))
                .disabled(!review.canApprove)

            if !review.privacyNotes.isEmpty {
                Text(review.privacyNotes.joined(separator: " "))
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
        switch review.status {
        case .waiting:
            return "REVIEW"
        case .ready:
            return "APPROVED"
        }
    }

    private var statusColor: Color {
        switch review.status {
        case .waiting:
            return .secondary
        case .ready:
            return .green
        }
    }
}
