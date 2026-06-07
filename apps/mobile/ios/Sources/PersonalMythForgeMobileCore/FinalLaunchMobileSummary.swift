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
    public var launchReceiptRows: [String]
    public var modePolicyRows: [String]
    public var resourceChecklistRows: [String]
    public var resourceActions: [String]
    public var acceptanceRows: [String]
    public var npcEvaluationRows: [String]
    public var handoffRows: [String]
    public var commandRows: [String]
    public var notes: [String]

    public init(
        overallStatus: FinalLaunchMobileStatus,
        title: String,
        subtitle: String,
        phaseRows: [FinalLaunchMobilePhaseRow],
        launchReceiptRows: [String] = [],
        modePolicyRows: [String] = [],
        resourceChecklistRows: [String] = [],
        resourceActions: [String],
        acceptanceRows: [String] = [],
        npcEvaluationRows: [String] = [],
        handoffRows: [String] = [],
        commandRows: [String],
        notes: [String]
    ) {
        self.overallStatus = overallStatus
        self.title = title
        self.subtitle = subtitle
        self.phaseRows = phaseRows
        self.launchReceiptRows = launchReceiptRows
        self.modePolicyRows = modePolicyRows
        self.resourceChecklistRows = resourceChecklistRows
        self.resourceActions = resourceActions
        self.acceptanceRows = acceptanceRows
        self.npcEvaluationRows = npcEvaluationRows
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
                launchReceiptRows: ["Receipt: final launch report blocked by API error."],
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
                launchReceiptRows: ["Receipt: waiting for final launch report."],
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
            launchReceiptRows: launchReceiptRows(from: report),
            modePolicyRows: modePolicyRows(from: report),
            resourceChecklistRows: resourceChecklistRows(from: report.finalResourcesPreflight),
            resourceActions: resourceActions(from: report.finalResourcesPreflight),
            acceptanceRows: acceptanceRows(from: report.finalAcceptanceReadiness),
            npcEvaluationRows: npcEvaluationRows(from: report.npcAgentEvaluationReadiness),
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

    private static func launchReceiptRows(from report: FinalDemoLaunchReport) -> [String] {
        [
            receiptStatusRow(report),
            acceptanceReceiptRow(report.finalAcceptanceReadiness),
            firstBlockerReceiptRow(report),
            liveProviderReceiptRow(report),
        ].map(sanitize)
    }

    private static func receiptStatusRow(_ report: FinalDemoLaunchReport) -> String {
        "Receipt: \(displayMode(report.mode).lowercased()) launch \(report.overallStatus)."
    }

    private static func acceptanceReceiptRow(_ readiness: FinalAcceptanceReadinessReport?) -> String {
        guard let readiness else {
            return "Acceptance: readiness report not loaded."
        }
        if let freshness = readiness.freshness, freshness.status == "stale" {
            return "Acceptance: \(freshness.classification); rerun final acceptance for current revision."
        }
        return "Acceptance: \(readiness.summary.passed) passed, \(readiness.summary.blocked) blocked, \(readiness.summary.failed) failed."
    }

    private static func firstBlockerReceiptRow(_ report: FinalDemoLaunchReport) -> String {
        if let blocker = report.finalAcceptanceReadiness?.blockers.first {
            return "First blocker: \(blocker.id) \(blocker.status) \(blocker.classification) | \(blocker.detail)"
        }
        if let item = report.finalResourcesPreflight?.items.first(where: {
            ($0.status == "missing" && $0.required) || $0.status == "blocked"
        }) {
            let detail = item.classification ?? item.normalizedValue ?? ""
            return "First blocker: \(item.id) \(item.status) \(detail)"
        }
        if let action = report.finalOperatorHandoff?.nextActions.first {
            return "First blocker: \(action)"
        }
        return "First blocker: none; final handoff ready."
    }

    private static func liveProviderReceiptRow(_ report: FinalDemoLaunchReport) -> String {
        if report.liveCallPolicy.configuredAcceptanceRequiresConsent {
            return "Live providers: consent required for configured acceptance."
        }
        if report.liveCallPolicy.liveCallsByDefault {
            return "Live providers: live calls enabled by default."
        }
        return "Live providers: no live calls by default."
    }

    private static func resourceChecklistRows(from preflight: FinalResourcesPreflightReport?) -> [String] {
        guard let preflight else {
            return ["Final resources checklist has not loaded."]
        }
        let attention = preflight.items.filter { item in
            (item.status == "missing" && item.required) || item.status == "blocked"
        }
        if !attention.isEmpty {
            return attention.prefix(5).map(resourceChecklistRow)
        }
        if preflight.status == "ready" {
            return ["Required final resources ready."]
        }
        if preflight.items.isEmpty {
            return ["Final resources checklist is empty."]
        }
        return preflight.items.prefix(3).map(resourceChecklistRow)
    }

    private static func resourceChecklistRow(_ item: FinalResourcesPreflightItem) -> String {
        var parts = ["\(item.id): \(item.status)"]
        parts.append(item.required ? "required" : "optional")
        if let classification = item.classification, !classification.isEmpty {
            parts.append(classification)
        } else if let normalizedValue = item.normalizedValue, !normalizedValue.isEmpty {
            parts.append(normalizedValue)
        }
        return sanitize(parts.joined(separator: " "))
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
        if let freshness = readiness.freshness, freshness.status == "stale" {
            return [
                "Final acceptance freshness \(sanitize(freshness.classification)); rerun local final acceptance.",
            ]
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

    private static func npcEvaluationRows(from readiness: NPCAgentEvaluationReadinessReport?) -> [String] {
        guard let readiness else {
            return ["NPC Agent evaluation readiness has not loaded."]
        }
        switch readiness.status.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() {
        case "ready":
            return [
                "NPC Agent evaluation ready: \(readiness.summary.succeeded) cases, \(readiness.coverage.tickStepsCompleted) ticks.",
                "Coverage: \(readiness.coverage.traceSets) trace sets, \(readiness.coverage.worldResolutionSteps) world resolutions.",
            ].map(sanitize)
        case "missing":
            return ["Run local NPC Agent evaluation to create the readiness report."]
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
            return ["NPC Agent evaluation blocked."]
        default:
            return ["NPC Agent evaluation \(sanitize(readiness.status))."]
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
            #"(private_message|raw_context|message_body)\s*:\s*[^\n]+"#,
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
