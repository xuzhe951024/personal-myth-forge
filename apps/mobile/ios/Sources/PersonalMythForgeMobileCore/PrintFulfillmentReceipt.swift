import Foundation

public enum PrintFulfillmentReceiptStatus: String, Codable, Equatable, Sendable {
    case waiting
    case needsApproval
    case ready
    case blocked
}

public struct PrintFulfillmentReceiptRow: Codable, Equatable, Sendable {
    public var id: String
    public var label: String
    public var status: PrintFulfillmentReceiptStatus
    public var detail: String

    public init(id: String, label: String, status: PrintFulfillmentReceiptStatus, detail: String) {
        self.id = id
        self.label = label
        self.status = status
        self.detail = detail
    }
}

public struct PrintFulfillmentReceipt: Codable, Equatable, Sendable {
    public var status: PrintFulfillmentReceiptStatus
    public var title: String
    public var detail: String
    public var rows: [PrintFulfillmentReceiptRow]
    public var privacyNotes: [String]
    public var canApprove: Bool
    public var canHandOffToProvider: Bool

    public init(
        status: PrintFulfillmentReceiptStatus,
        title: String,
        detail: String,
        rows: [PrintFulfillmentReceiptRow],
        privacyNotes: [String],
        canApprove: Bool,
        canHandOffToProvider: Bool
    ) {
        self.status = status
        self.title = title
        self.detail = detail
        self.rows = rows
        self.privacyNotes = privacyNotes
        self.canApprove = canApprove
        self.canHandOffToProvider = canHandOffToProvider
    }

    public func row(id: String) -> PrintFulfillmentReceiptRow? {
        rows.first { $0.id == id }
    }
}

public enum PrintFulfillmentReceiptBuilder {
    public static func build(
        session: MythSession?,
        quote: PrintQuote?,
        isLoading: Bool,
        errorMessage: String?,
        isApproved: Bool
    ) -> PrintFulfillmentReceipt {
        if let errorMessage {
            return receipt(
                status: .blocked,
                title: "Print fulfillment blocked",
                detail: "Provider quote handoff is blocked: \(errorMessage)",
                rows: baseRows(session: session, quote: quote) + [
                    row("error", "Quote error", .blocked, errorMessage),
                ],
                canApprove: false,
                canHandOffToProvider: false
            )
        }

        guard let session else {
            return receipt(
                status: .waiting,
                title: "Print fulfillment waiting",
                detail: "Forge a myth session before requesting a print quote.",
                rows: [
                    row("session", "Myth session", .waiting, "Waiting for generated game asset and print candidate."),
                    row("quote", "Quote", .waiting, "No provider quote requested."),
                    row("approval", "Approval", .waiting, "Approval unlocks only after a quote exists."),
                ],
                canApprove: false,
                canHandOffToProvider: false
            )
        }

        guard let quote else {
            return receipt(
                status: .waiting,
                title: isLoading ? "Print quote loading" : "Print fulfillment waiting",
                detail: isLoading ? "Requesting a provider quote for the print candidate." : "Request a quote before print fulfillment handoff.",
                rows: [
                    candidateRow(session.printCandidate),
                    row("quote", "Quote", isLoading ? .needsApproval : .waiting, isLoading ? "Provider quote request is running." : "No provider quote loaded."),
                    row("approval", "Approval", .waiting, "User approval is unavailable until the quote returns."),
                ],
                canApprove: false,
                canHandOffToProvider: false
            )
        }

        let canApprove = quote.requiresUserApproval
        let isReady = !quote.requiresUserApproval || isApproved
        let status: PrintFulfillmentReceiptStatus = isReady ? .ready : .needsApproval
        let title = isReady ? "Print handoff ready" : "Print approval required"
        let detail = isReady
            ? "Approved quote is ready for provider handoff; order placement remains separate."
            : "User approval required before provider handoff."
        let approvalDetail = quote.requiresUserApproval
            ? (isApproved ? "Approved locally for provider handoff." : quote.approvalReason)
            : "No extra approval required for this quote."

        return receipt(
            status: status,
            title: title,
            detail: detail,
            rows: [
                candidateRow(session.printCandidate),
                row("provider", "Provider", status, quote.provider),
                quoteRow(quote, status: status),
                row("timeline", "Timeline", status, "Production \(quote.estimatedProductionDays)d, shipping \(quote.estimatedShippingDays)d."),
                row("approval", "Approval", status, approvalDetail),
                notesRow(quote, status: status),
            ],
            canApprove: canApprove,
            canHandOffToProvider: isReady
        )
    }

    private static func receipt(
        status: PrintFulfillmentReceiptStatus,
        title: String,
        detail: String,
        rows: [PrintFulfillmentReceiptRow],
        canApprove: Bool,
        canHandOffToProvider: Bool
    ) -> PrintFulfillmentReceipt {
        PrintFulfillmentReceipt(
            status: status,
            title: sanitize(title),
            detail: sanitize(detail),
            rows: rows.map { row($0.id, $0.label, $0.status, $0.detail) },
            privacyNotes: [
                "Checkout/payment links stay withheld until a separate order flow.",
                "Approval is local app state and does not place an order.",
                "Provider keys, raw captures, and personal context stay backend-only.",
            ].map(sanitize),
            canApprove: canApprove,
            canHandOffToProvider: canHandOffToProvider
        )
    }

    private static func baseRows(session: MythSession?, quote: PrintQuote?) -> [PrintFulfillmentReceiptRow] {
        var rows: [PrintFulfillmentReceiptRow] = []
        if let session {
            rows.append(candidateRow(session.printCandidate))
        } else {
            rows.append(row("candidate", "Print asset", .waiting, "Waiting for myth session print candidate."))
        }
        if let quote {
            rows.append(row("provider", "Provider", .blocked, quote.provider))
            rows.append(quoteRow(quote, status: .blocked))
            rows.append(notesRow(quote, status: .blocked))
        } else {
            rows.append(row("quote", "Quote", .blocked, "No quote available after provider error."))
        }
        return rows
    }

    private static func candidateRow(_ candidate: PrintCandidate) -> PrintFulfillmentReceiptRow {
        row(
            "candidate",
            "Print asset",
            .ready,
            "\(candidate.format) candidate from \(candidate.provider); \(candidate.approvalReason)"
        )
    }

    private static func quoteRow(_ quote: PrintQuote, status: PrintFulfillmentReceiptStatus) -> PrintFulfillmentReceiptRow {
        row(
            "quote",
            "Quote",
            status,
            "\(quote.currency) \(priceString(cents: quote.estimatedPriceCents)) \(quote.status)"
        )
    }

    private static func notesRow(_ quote: PrintQuote, status: PrintFulfillmentReceiptStatus) -> PrintFulfillmentReceiptRow {
        let notes = quote.quoteNotes.isEmpty ? "No provider notes." : quote.quoteNotes.joined(separator: "; ")
        return row("notes", "Provider notes", status, notes)
    }

    private static func row(
        _ id: String,
        _ label: String,
        _ status: PrintFulfillmentReceiptStatus,
        _ detail: String
    ) -> PrintFulfillmentReceiptRow {
        PrintFulfillmentReceiptRow(
            id: sanitize(id),
            label: sanitize(label),
            status: status,
            detail: sanitize(detail)
        )
    }

    private static func priceString(cents: Int) -> String {
        let safeCents = max(0, cents)
        return "\(safeCents / 100).\(String(format: "%02d", safeCents % 100))"
    }

    private static func sanitize(_ value: String) -> String {
        var sanitized = value
        let patterns = [
            #"sk-[A-Za-z0-9._-]+"#,
            #"Bearer\s+[A-Za-z0-9._~+/\-=:-]+"#,
            #"Authorization\s*=\s*Bearer\s+[A-Za-z0-9._~+/\-=:-]+"#,
            #"api[_-]?key\s*[=:]\s*[^\s,;"']+"#,
            #"(private_message|raw_context|message_body)\s*:\s*[^\n]+"#,
            #"local-capture://[^\s,;"']+"#,
            #"file://[^\s,;"']+"#,
            #"/Users/[^\s,;"']+"#,
            #"/tmp/[^\s,;"']+"#,
            #"checkout_url\s*=\s*[^\s,;"']+"#,
            #"checkout_url"#,
            #"https?://checkout\.[^\s,;"']+"#,
            #"https?://pay\.[^\s,;"']+"#,
        ]
        for pattern in patterns {
            sanitized = sanitized.replacingOccurrences(
                of: pattern,
                with: "[withheld]",
                options: .regularExpression
            )
        }
        return sanitized
    }
}
