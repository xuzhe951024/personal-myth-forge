import Foundation

public enum LiveProviderConsentStatus: String, Codable, Equatable, Sendable {
    case waiting
    case blocked
    case ready
}

public struct LiveProviderConsentRow: Codable, Equatable, Sendable {
    public var id: String
    public var label: String
    public var status: LiveProviderConsentStatus
    public var detail: String

    public init(id: String, label: String, status: LiveProviderConsentStatus, detail: String) {
        self.id = id
        self.label = label
        self.status = status
        self.detail = detail
    }
}

public struct LiveProviderConsentSummary: Codable, Equatable, Sendable {
    public var status: LiveProviderConsentStatus
    public var title: String
    public var subtitle: String
    public var rows: [LiveProviderConsentRow]
    public var privacyNotes: [String]
    public var canRunConfiguredAcceptance: Bool
    public var consentFlag: String?

    public init(
        status: LiveProviderConsentStatus,
        title: String,
        subtitle: String,
        rows: [LiveProviderConsentRow],
        privacyNotes: [String],
        canRunConfiguredAcceptance: Bool,
        consentFlag: String?
    ) {
        self.status = status
        self.title = title
        self.subtitle = subtitle
        self.rows = rows
        self.privacyNotes = privacyNotes
        self.canRunConfiguredAcceptance = canRunConfiguredAcceptance
        self.consentFlag = consentFlag
    }
}

public enum LiveProviderConsentSummaryBuilder {
    public static func build(
        providerReadiness: ProviderReadinessResponse?,
        providerReadinessError: String?,
        finalLaunchReport: FinalDemoLaunchReport?,
        finalLaunchError: String?
    ) -> LiveProviderConsentSummary {
        var rows: [LiveProviderConsentRow] = []

        if let providerReadinessError {
            rows.append(row("providers", "Providers", .blocked, providerReadinessError))
        } else if let providerReadiness {
            rows.append(providerRow(providerReadiness))
        } else {
            rows.append(row("providers", "Providers", .waiting, "Waiting for backend provider readiness."))
        }

        if let finalLaunchError {
            rows.append(row("final_launch", "Final launch", .blocked, finalLaunchError))
        } else if let finalLaunchReport {
            rows.append(livePolicyRow(finalLaunchReport.liveCallPolicy))
            rows.append(finalResourcesRow(finalLaunchReport.finalResourcesPreflight))
            rows.append(resourceHandoffRow(finalLaunchReport.resourceReport))
            rows.append(liveEvidenceRow(finalLaunchReport.liveProviderEvidence))
        } else {
            rows.append(row("live_policy", "Live-call policy", .waiting, "Waiting for final launch report."))
            rows.append(row("final_resources", "Final resources", .waiting, "Waiting for final resources report."))
            rows.append(row("resource_handoff", "Resource handoff", .waiting, "Waiting for resource handoff report."))
            rows.append(row("live_evidence", "Live evidence", .waiting, "Live provider evidence report has not loaded."))
        }

        let sanitizedRows = rows.map { item in
            row(item.id, item.label, item.status, item.detail)
        }
        let hasMissingData = providerReadiness == nil || finalLaunchReport == nil
        let hasError = providerReadinessError != nil || finalLaunchError != nil
        let hasBlocked = sanitizedRows.contains { $0.status == .blocked }
        let liveEvidenceReady = finalLaunchReport?.liveProviderEvidence?.status
            .trimmingCharacters(in: .whitespacesAndNewlines)
            .lowercased() == "ready"
        let allReady = providerReadiness?.overallRealReady == true
            && finalLaunchReport?.finalResourcesPreflight?.status == "ready"
            && finalLaunchReport?.resourceReport?.overallStatus == "ready"
            && liveEvidenceReady
            && !hasError
            && !hasBlocked

        let status: LiveProviderConsentStatus
        if allReady {
            status = .ready
        } else if hasError || hasBlocked {
            status = .blocked
        } else if hasMissingData {
            status = .waiting
        } else {
            status = .waiting
        }

        return LiveProviderConsentSummary(
            status: status,
            title: title(for: status),
            subtitle: subtitle(for: status, hasMissingData: hasMissingData),
            rows: sanitizedRows,
            privacyNotes: privacyNotes(finalLaunchReport?.liveCallPolicy),
            canRunConfiguredAcceptance: allReady,
            consentFlag: sanitize(finalLaunchReport?.liveCallPolicy.consentFlag ?? nil)
        )
    }

    private static func providerRow(_ readiness: ProviderReadinessResponse) -> LiveProviderConsentRow {
        if readiness.overallRealReady {
            let details = readiness.providers.map { provider in
                "\(displayProvider(provider.selectedProvider)) \(displayKind(provider.kind)) \(sanitize(provider.status))"
            }
            return row("providers", "Providers", .ready, details.joined(separator: "; "))
        }

        let missing = readiness.providers.flatMap(\.missingEnv)
        if !missing.isEmpty {
            return row("providers", "Providers", .blocked, "Missing \(missing.joined(separator: ", ")).")
        }

        let details = readiness.providers.map { provider in
            "\(displayProvider(provider.selectedProvider)) \(displayKind(provider.kind)) \(sanitize(provider.status))"
        }
        return row(
            "providers",
            "Providers",
            readiness.overallDemoReady ? .waiting : .blocked,
            details.isEmpty ? "Provider readiness needs configured real providers." : details.joined(separator: "; ")
        )
    }

    private static func livePolicyRow(_ policy: FinalDemoLaunchLiveCallPolicy) -> LiveProviderConsentRow {
        let defaultDetail = policy.liveCallsByDefault ? "live calls enabled by default" : "no live calls by default"
        if policy.configuredAcceptanceRequiresConsent {
            return row(
                "live_policy",
                "Live-call policy",
                .waiting,
                "configured acceptance consent required via \(policy.consentFlag); \(defaultDetail)."
            )
        }
        return row("live_policy", "Live-call policy", .ready, defaultDetail)
    }

    private static func finalResourcesRow(
        _ report: FinalResourcesPreflightReport?
    ) -> LiveProviderConsentRow {
        guard let report else {
            return row("final_resources", "Final resources", .waiting, "Final resources report has not loaded.")
        }
        if report.status == "ready" {
            return row("final_resources", "Final resources", .ready, "Final resources ready.")
        }

        let attention = report.items.filter { item in
            (item.status == "missing" && item.required) || item.status == "blocked"
        }
        let detail: String
        if attention.isEmpty {
            detail = "Final resources \(report.status). \(report.operatorActions.first ?? "")"
        } else {
            detail = "Final resources \(report.status): \(attention.prefix(4).map(resourceItemDetail).joined(separator: "; "))."
        }
        return row("final_resources", "Final resources", status(from: report.status), detail)
    }

    private static func resourceHandoffRow(_ report: ResourceHandoffReport?) -> LiveProviderConsentRow {
        guard let report else {
            return row("resource_handoff", "Resource handoff", .waiting, "Resource handoff report has not loaded.")
        }
        if report.overallStatus == "ready" {
            return row("resource_handoff", "Resource handoff", .ready, "Resource handoff ready.")
        }
        return row(
            "resource_handoff",
            "Resource handoff",
            status(from: report.overallStatus),
            "Resource handoff \(report.overallStatus): ready \(report.summary.ready), missing \(report.summary.missing), blocked \(report.summary.blocked). \(report.operatorActions.first ?? "")"
        )
    }

    private static func liveEvidenceRow(
        _ evidence: LiveProviderEvidenceReport?
    ) -> LiveProviderConsentRow {
        guard let evidence else {
            return row("live_evidence", "Live evidence", .waiting, "Live provider evidence report has not loaded.")
        }

        let detailPrefix = (
            "Live evidence \(sanitize(evidence.status)): ready \(evidence.summary.ready), "
                + "missing \(evidence.summary.missing), blocked \(evidence.summary.blocked), "
                + "partial \(evidence.summary.partial)."
        )
        if evidence.status.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() == "ready" {
            return row("live_evidence", "Live evidence", .ready, detailPrefix)
        }

        let blockerDetail: String
        if let blocker = evidence.firstBlocker {
            blockerDetail = " " + liveEvidenceBlockerDetail(blocker)
        } else if let slot = evidence.evidence.first(where: { status(from: $0.status) != .ready }) {
            blockerDetail = " " + liveEvidenceBlockerDetail(slot)
        } else {
            blockerDetail = ""
        }
        return row("live_evidence", "Live evidence", status(from: evidence.status), detailPrefix + blockerDetail)
    }

    private static func liveEvidenceBlockerDetail(_ slot: LiveProviderEvidenceSlot) -> String {
        var parts = ["\(slot.id) \(slot.status)"]
        if let classification = slot.classification, !classification.isEmpty {
            parts.append(classification)
        }
        if let detail = slot.detail, !detail.isEmpty {
            parts.append(detail)
        }
        return sanitize(parts.joined(separator: ": "))
    }

    private static func resourceItemDetail(_ item: FinalResourcesPreflightItem) -> String {
        var parts = ["\(item.id) \(item.status)"]
        if item.required {
            parts.append("required")
        }
        if let classification = item.classification, !classification.isEmpty {
            parts.append(classification)
        }
        return parts.joined(separator: " ")
    }

    private static func status(from raw: String) -> LiveProviderConsentStatus {
        switch raw.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() {
        case "ready", "passed":
            return .ready
        case "blocked", "failed", "missing":
            return .blocked
        default:
            return .waiting
        }
    }

    private static func title(for status: LiveProviderConsentStatus) -> String {
        switch status {
        case .waiting:
            return "Live provider consent waiting"
        case .blocked:
            return "Live provider consent blocked"
        case .ready:
            return "Live provider consent ready"
        }
    }

    private static func subtitle(for status: LiveProviderConsentStatus, hasMissingData: Bool) -> String {
        switch status {
        case .waiting:
            if hasMissingData {
                return "Waiting for provider readiness and final launch reports."
            }
            return "Configured providers still need operator confirmation."
        case .blocked:
            return "Configured provider handoff is not ready for live acceptance."
        case .ready:
            return "Configured providers are ready; pass the consent flag on the Mac before live acceptance."
        }
    }

    private static func privacyNotes(_ policy: FinalDemoLaunchLiveCallPolicy?) -> [String] {
        var notes = [
            "Provider keys remain backend-only.",
            "The iPhone does not call live providers by default.",
        ]
        if let policy, policy.configuredAcceptanceRequiresConsent {
            notes.append("Use \(policy.consentFlag) on the Mac for configured acceptance.")
        }
        return notes.map(sanitize)
    }

    private static func displayProvider(_ raw: String) -> String {
        switch raw.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() {
        case "meshy":
            return "Meshy"
        case "openai":
            return "OpenAI"
        case "treatstock":
            return "Treatstock"
        case "sculpteo":
            return "Sculpteo"
        case "local", "local_stub":
            return "Local"
        default:
            return sanitize(raw)
        }
    }

    private static func displayKind(_ raw: String) -> String {
        switch raw.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() {
        case "three_d":
            return "3D"
        case "npc":
            return "NPC"
        case "print", "printing":
            return "print"
        default:
            return sanitize(raw)
        }
    }

    private static func row(
        _ id: String,
        _ label: String,
        _ status: LiveProviderConsentStatus,
        _ detail: String
    ) -> LiveProviderConsentRow {
        LiveProviderConsentRow(
            id: sanitize(id),
            label: sanitize(label),
            status: status,
            detail: sanitize(detail)
        )
    }

    private static func sanitize(_ text: String?) -> String? {
        guard let text else {
            return nil
        }
        return sanitize(text)
    }

    private static func sanitize(_ text: String) -> String {
        var sanitized = text
        let patterns = [
            #"sk-[A-Za-z0-9._-]+"#,
            #"Bearer\s+[^\s,;"']+"#,
            #"Authorization[^\s,;"']*"#,
            #"api[_-]?key\s*[=:]\s*[^\s,;"']+"#,
            #"(private_message|raw_context|message_body)\s*:\s*[^\n]+"#,
            #"local-capture://[^\s,;"']+"#,
            #"file://[^\s,;"']+"#,
            #"/Users/[^\s,;"']+"#,
            #"/tmp/[^\s,;"']+"#,
            #"https?://checkout\.[^\s,;"']+"#,
            #"https?://pay\.[^\s,;"']+"#,
            #"checkout_url"#,
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
