import Foundation

public enum FinalLaunchMobileStatus: String, Codable, Equatable, Sendable {
    case blocked
    case waiting
    case ready
}

public struct FinalLaunchMobilePhaseRow: Codable, Equatable, Sendable {
    public var id: String
    public var label: String
    public var status: FinalLaunchMobileStatus
    public var detail: String

    public init(id: String, label: String, status: FinalLaunchMobileStatus, detail: String) {
        self.id = id
        self.label = label
        self.status = status
        self.detail = detail
    }
}

public struct FinalLaunchMobileSummary: Codable, Equatable, Sendable {
    public var overallStatus: FinalLaunchMobileStatus
    public var title: String
    public var subtitle: String
    public var phaseRows: [FinalLaunchMobilePhaseRow]
    public var modePolicyRows: [String]
    public var resourceActions: [String]
    public var acceptanceRows: [String]
    public var handoffRows: [String]
    public var commandRows: [String]
    public var notes: [String]

    public init(
        overallStatus: FinalLaunchMobileStatus,
        title: String,
        subtitle: String,
        phaseRows: [FinalLaunchMobilePhaseRow],
        modePolicyRows: [String] = [],
        resourceActions: [String],
        acceptanceRows: [String] = [],
        handoffRows: [String] = [],
        commandRows: [String],
        notes: [String]
    ) {
        self.overallStatus = overallStatus
        self.title = title
        self.subtitle = subtitle
        self.phaseRows = phaseRows
        self.modePolicyRows = modePolicyRows
        self.resourceActions = resourceActions
        self.acceptanceRows = acceptanceRows
        self.handoffRows = handoffRows
        self.commandRows = commandRows
        self.notes = notes
    }
}

public enum FinalLaunchMobileSummaryBuilder {
    public static func build(
        report: FinalDemoLaunchReport?,
        error: String? = nil
    ) -> FinalLaunchMobileSummary {
        if let error {
            return FinalLaunchMobileSummary(
                overallStatus: .blocked,
                title: "Final launch report blocked",
                subtitle: sanitize(error),
                phaseRows: [],
                resourceActions: [],
                acceptanceRows: [],
                handoffRows: [],
                commandRows: [],
                notes: baseNotes()
            )
        }
        guard let report else {
            return FinalLaunchMobileSummary(
                overallStatus: .waiting,
                title: "Final launch report waiting",
                subtitle: "Final launch report has not loaded.",
                phaseRows: [],
                resourceActions: [],
                acceptanceRows: [],
                handoffRows: [],
                commandRows: [],
                notes: baseNotes()
            )
        }

        let phaseRows = report.launchPhases.map { phase in
            FinalLaunchMobilePhaseRow(
                id: sanitize(phase.id),
                label: sanitize(phase.label),
                status: status(from: phase.status),
                detail: phaseDetail(phase)
            )
        }

        return FinalLaunchMobileSummary(
            overallStatus: status(from: report.overallStatus),
            title: "Final launch \(sanitize(report.overallStatus))",
            subtitle: summaryText(report.summary, mode: report.mode),
            phaseRows: Array(phaseRows.prefix(4)),
            modePolicyRows: modePolicyRows(from: report),
            resourceActions: resourceActions(from: report.finalResourcesPreflight),
            acceptanceRows: acceptanceRows(from: report.finalAcceptanceReadiness),
            handoffRows: handoffRows(from: report.finalOperatorHandoff),
            commandRows: report.commands.prefix(4).map(sanitize),
            notes: baseNotes()
        )
    }

    private static func modePolicyRows(from report: FinalDemoLaunchReport) -> [String] {
        var rows = [
            "Mode: \(displayMode(report.mode))",
            "Live calls by default: \(yesNo(report.liveCallPolicy.liveCallsByDefault))",
        ]
        if report.liveCallPolicy.configuredAcceptanceRequiresConsent {
            rows.append("Consent flag: \(sanitize(report.liveCallPolicy.consentFlag))")
        }
        return rows.map(sanitize)
    }

    private static func displayMode(_ mode: String) -> String {
        switch mode.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() {
        case "configured":
            return "Configured"
        case "local":
            return "Local"
        default:
            return sanitize(mode)
        }
    }

    private static func yesNo(_ value: Bool) -> String {
        value ? "yes" : "no"
    }

    private static func status(from raw: String) -> FinalLaunchMobileStatus {
        switch raw.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() {
        case "ready", "passed":
            return .ready
        case "blocked", "failed":
            return .blocked
        default:
            return .waiting
        }
    }

    private static func summaryText(_ summary: FinalDemoLaunchSummary, mode: String) -> String {
        sanitize(
            "mode \(mode); ready \(summary.ready), missing \(summary.missing), blocked \(summary.blocked), manual \(summary.manual)"
        )
    }

    private static func phaseDetail(_ phase: FinalDemoLaunchPhase) -> String {
        var parts = [phase.command]
        if let note = phase.notes.first {
            parts.append(note)
        }
        return sanitize(parts.joined(separator: " | "))
    }

    private static func resourceActions(from preflight: FinalResourcesPreflightReport?) -> [String] {
        guard let preflight else {
            return ["Final resources preflight has not loaded."]
        }
        if preflight.status == "ready" {
            return ["Final resources file ready to apply."]
        }
        if !preflight.operatorActions.isEmpty {
            return preflight.operatorActions.prefix(3).map(sanitize)
        }
        return ["Final resources preflight \(sanitize(preflight.status))."]
    }

    private static func acceptanceRows(from readiness: FinalAcceptanceReadinessReport?) -> [String] {
        guard let readiness else {
            return ["Final acceptance readiness has not loaded."]
        }
        switch readiness.status.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() {
        case "ready":
            return ["Final acceptance ready."]
        case "missing":
            return ["Run local final acceptance to create the latest readiness report."]
        case "blocked", "failed":
            if !readiness.blockers.isEmpty {
                return readiness.blockers.prefix(3).map { blocker in
                    sanitize(
                        "\(blocker.id): \(blocker.status) \(blocker.classification) | \(blocker.command) | \(blocker.detail)"
                    )
                }
            }
            if !readiness.operatorActions.isEmpty {
                return readiness.operatorActions.prefix(3).map(sanitize)
            }
            return ["Final acceptance blocked."]
        default:
            return ["Final acceptance \(sanitize(readiness.status))."]
        }
    }

    private static func handoffRows(from handoff: FinalOperatorHandoffReport?) -> [String] {
        guard let handoff else {
            return ["Final operator handoff has not loaded."]
        }
        switch handoff.status.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() {
        case "ready":
            return ["Final operator handoff ready."]
        case "blocked", "partial", "live":
            if !handoff.nextActions.isEmpty {
                return handoff.nextActions.prefix(3).map(sanitize)
            }
            if let step = handoff.steps.first(where: { status(from: $0.status) != .ready }) {
                let note = step.notes.first ?? step.requiredFor
                return [sanitize("\(step.id): \(step.status) | \(step.command) | \(note)")]
            }
            return ["Final operator handoff \(sanitize(handoff.status))."]
        case "missing":
            if !handoff.nextActions.isEmpty {
                return handoff.nextActions.prefix(3).map(sanitize)
            }
            return ["Final operator handoff waiting for local operator data."]
        default:
            return ["Final operator handoff \(sanitize(handoff.status))."]
        }
    }

    private static func baseNotes() -> [String] {
        [
            "read-only iPhone launch status.",
            "Provider keys and resource files stay backend-only.",
            "Commands are for the Mac operator; the app does not run them.",
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
