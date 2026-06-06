import Foundation

public enum ContextCapsuleReviewStatus: String, Codable, Equatable, Sendable {
    case waiting
    case ready
}

public struct ContextCapsuleReview: Codable, Equatable, Sendable {
    public var status: ContextCapsuleReviewStatus
    public var title: String
    public var detail: String
    public var summaryLines: [String]
    public var privacyNotes: [String]
    public var canApprove: Bool
    public var canForge: Bool

    public init(
        status: ContextCapsuleReviewStatus,
        title: String,
        detail: String,
        summaryLines: [String],
        privacyNotes: [String],
        canApprove: Bool,
        canForge: Bool
    ) {
        self.status = status
        self.title = title
        self.detail = detail
        self.summaryLines = summaryLines
        self.privacyNotes = privacyNotes
        self.canApprove = canApprove
        self.canForge = canForge
    }
}

public enum ContextCapsuleReviewBuilder {
    public static func build(
        currentTheme: String,
        desiredTone: String,
        isApproved: Bool
    ) -> ContextCapsuleReview {
        let theme = currentTheme.trimmingCharacters(in: .whitespacesAndNewlines)
        let tone = desiredTone.trimmingCharacters(in: .whitespacesAndNewlines)
        let summary = summaryLines(theme: theme, tone: tone)

        if theme.isEmpty || tone.isEmpty {
            return ContextCapsuleReview(
                status: .waiting,
                title: "Context capsule incomplete",
                detail: missingDetail(theme: theme, tone: tone),
                summaryLines: summary,
                privacyNotes: privacyNotes(),
                canApprove: false,
                canForge: false
            )
        }

        if !isApproved {
            return ContextCapsuleReview(
                status: .waiting,
                title: "Review context capsule",
                detail: "Approve this summary capsule before forging.",
                summaryLines: summary,
                privacyNotes: privacyNotes(),
                canApprove: true,
                canForge: false
            )
        }

        return ContextCapsuleReview(
            status: .ready,
            title: "Context capsule approved",
            detail: "Only this summary capsule will be sent to the backend.",
            summaryLines: summary,
            privacyNotes: privacyNotes(),
            canApprove: true,
            canForge: true
        )
    }

    private static func summaryLines(theme: String, tone: String) -> [String] {
        [
            "Theme: \(sanitize(theme.isEmpty ? "missing" : theme))",
            "Tone: \(sanitize(tone.isEmpty ? "missing" : tone))",
        ]
    }

    private static func missingDetail(theme: String, tone: String) -> String {
        if theme.isEmpty && tone.isEmpty {
            return "Add a current theme and desired tone."
        }
        if theme.isEmpty {
            return "Add a current theme."
        }
        return "Add a desired tone."
    }

    private static func privacyNotes() -> [String] {
        [
            "No raw email, chat, calendar, document, or file bodies are included.",
            "Provider keys stay backend-only.",
            "Changing the capsule requires approval again.",
        ]
    }

    private static func sanitize(_ text: String) -> String {
        var sanitized = text
        let patterns = [
            #"sk-[A-Za-z0-9._-]+"#,
            #"Bearer\s+[A-Za-z0-9._~+/\-=:-]+"#,
            #"api[_-]?key\s*[=:]\s*[^\s,;"']+"#,
            #"local-capture://[^\s,;"']+"#,
            #"file://[^\s,;"']+"#,
            #"/Users/[^\s,;"']+"#,
            #"/tmp/[^\s,;"']+"#,
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
