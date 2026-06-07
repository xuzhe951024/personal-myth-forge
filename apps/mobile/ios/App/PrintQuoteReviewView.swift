import Foundation
import PersonalMythForgeMobileCore
import SwiftUI

struct PrintQuoteReviewView: View {
    let session: MythSession?
    let quote: PrintQuote?
    let isLoading: Bool
    let errorMessage: String?
    let fulfillmentReceipt: PrintFulfillmentReceipt
    @Binding var isPrintQuoteApproved: Bool
    let requestQuote: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("Print Quote")
                .font(.headline)

            if let session {
                candidateSummary(session.printCandidate)
                Button(action: requestQuote) {
                    Text(isLoading ? "Quoting..." : "Get Quote")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
                .disabled(isLoading)

                if let errorMessage {
                    Text(errorMessage)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }

                if let quote {
                    quoteSummary(quote)
                }

                PrintFulfillmentReceiptView(receipt: fulfillmentReceipt)

                if quote != nil && fulfillmentReceipt.canApprove {
                    Toggle("Approve Print Handoff", isOn: $isPrintQuoteApproved)
                        .font(.caption.weight(.semibold))
                        .toggleStyle(.switch)
                    Text("Approval only unlocks provider handoff readiness in this demo.")
                        .font(.caption2)
                        .foregroundStyle(.secondary)
                }
            } else {
                Text("Print quote review appears after the myth session is ready.")
                    .foregroundStyle(.secondary)
                PrintFulfillmentReceiptView(receipt: fulfillmentReceipt)
            }
        }
    }

    private func candidateSummary(_ candidate: PrintCandidate) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack {
                Text(candidate.format.uppercased())
                    .font(.caption.weight(.semibold))
                Spacer()
                Text(candidate.provider)
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            Text(candidate.approvalReason)
                .font(.caption)
            Text(candidate.printabilityNotes.joined(separator: " | "))
                .font(.caption2)
                .foregroundStyle(.secondary)
        }
        .padding(10)
        .background(Color.secondary.opacity(0.08))
        .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))
    }

    private func quoteSummary(_ quote: PrintQuote) -> some View {
        VStack(alignment: .leading, spacing: 7) {
            HStack {
                Text(quote.status.replacingOccurrences(of: "_", with: " ").capitalized)
                    .font(.subheadline.weight(.semibold))
                Spacer()
                Text(priceLabel(quote))
                    .font(.subheadline.weight(.semibold))
            }
            Text("\(quote.estimatedProductionDays)d production + \(quote.estimatedShippingDays)d shipping")
                .font(.caption)
            Text(quote.requiresUserApproval ? "User approval required" : "Ready for provider handoff")
                .font(.caption)
                .foregroundStyle(.secondary)
            if quote.checkoutUrl == nil {
                Text("Checkout is withheld in this demo.")
                    .font(.caption2)
                    .foregroundStyle(.secondary)
            }
            if !quote.quoteNotes.isEmpty {
                Text(quote.quoteNotes.joined(separator: " | "))
                    .font(.caption2)
                    .foregroundStyle(.secondary)
            }
        }
        .padding(10)
        .background(Color.secondary.opacity(0.08))
        .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))
    }

    private func priceLabel(_ quote: PrintQuote) -> String {
        let dollars = Double(quote.estimatedPriceCents) / 100.0
        return "\(quote.currency) \(String(format: "%.2f", dollars))"
    }
}
