import Foundation

public enum DevicePreflightStatus: String, Codable, Equatable, Sendable {
    case blocked
    case waiting
    case ready
}

public struct DevicePreflightItem: Codable, Equatable, Sendable {
    public var id: String
    public var label: String
    public var status: DevicePreflightStatus
    public var detail: String

    public init(id: String, label: String, status: DevicePreflightStatus, detail: String) {
        self.id = id
        self.label = label
        self.status = status
        self.detail = detail
    }
}

public struct DevicePreflightSummary: Codable, Equatable, Sendable {
    public var overallStatus: DevicePreflightStatus
    public var title: String
    public var backendBaseURL: String
    public var items: [DevicePreflightItem]
    public var notes: [String]

    public init(
        overallStatus: DevicePreflightStatus,
        title: String,
        backendBaseURL: String,
        items: [DevicePreflightItem],
        notes: [String]
    ) {
        self.overallStatus = overallStatus
        self.title = title
        self.backendBaseURL = backendBaseURL
        self.items = items
        self.notes = notes
    }

    public func item(id: String) -> DevicePreflightItem? {
        items.first { $0.id == id }
    }
}

public struct BackendHealthResponse: Codable, Equatable, Sendable {
    public var status: String

    public init(status: String) {
        self.status = status
    }

    public var isOK: Bool {
        status.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() == "ok"
    }
}

public enum BackendHealthProbeStatus: String, Codable, Equatable, Sendable {
    case notChecked
    case checking
    case reachable
    case unreachable
}

public struct BackendHealthProbe: Codable, Equatable, Sendable {
    public var status: BackendHealthProbeStatus
    public var detail: String

    public init(status: BackendHealthProbeStatus, detail: String) {
        self.status = status
        self.detail = detail
    }

    public init(response: BackendHealthResponse) {
        if response.isOK {
            self.init(status: .reachable, detail: "Backend /health returned ok.")
        } else {
            self.init(status: .unreachable, detail: "Backend /health returned \(response.status).")
        }
    }
}

public enum DevicePreflightSummaryBuilder {
    public static func build(
        backendBaseURL: URL,
        backendHealthProbe: BackendHealthProbe? = nil,
        providerReadiness: ProviderReadinessResponse?,
        providerReadinessError: String?,
        finalDemoLaunch: FinalDemoLaunchReport? = nil,
        finalDemoLaunchError: String? = nil,
        finalShowcaseSummary: FinalShowcaseSummary,
        savedNPCTickCount: Int
    ) -> DevicePreflightSummary {
        let items = [
            backendItem(backendBaseURL, healthProbe: backendHealthProbe),
            providerItem(readiness: providerReadiness, error: providerReadinessError),
            finalLaunchItem(report: finalDemoLaunch, error: finalDemoLaunchError),
            externalActionLedgerItem(report: finalDemoLaunch),
            finalResourcesItem(report: finalDemoLaunch),
            finalResourceRequirementsItem(report: finalDemoLaunch),
            finalResourceFillGuideItem(report: finalDemoLaunch),
            finalResourceApplyPreviewItem(report: finalDemoLaunch),
            iosDeployRunbookItem(report: finalDemoLaunch),
            iosDeviceEvidenceBundleItem(report: finalDemoLaunch),
            iosLaunchRehearsalReadinessItem(report: finalDemoLaunch),
            iosDeviceLaunchCertificateItem(report: finalDemoLaunch),
            finalClosurePacketItem(report: finalDemoLaunch),
            finalOperatorHandoffItem(report: finalDemoLaunch),
            localDemoItem(finalShowcaseSummary),
            savedHistoryItem(savedNPCTickCount),
        ]
        let status = overallStatus(items)
        return DevicePreflightSummary(
            overallStatus: status,
            title: title(for: status),
            backendBaseURL: sanitize(backendBaseURL.absoluteString),
            items: items,
            notes: [
                "Provider keys stay backend-only.",
                "Use a Mac LAN URL for iPhone demos.",
                "Final launch readiness is read-only.",
                "This preflight does not install or sign the app.",
            ]
        )
    }

    private static func backendItem(_ url: URL, healthProbe: BackendHealthProbe?) -> DevicePreflightItem {
        let host = url.host?.lowercased() ?? ""
        if isLoopback(host) {
            return item(
                "backend_url",
                "Backend URL",
                .blocked,
                "Loopback is not reachable from iPhone; use the Mac LAN URL."
            )
        }
        guard let healthProbe else {
            return item("backend_url", "Backend URL", .waiting, "Check Backend before iPhone demo.")
        }
        switch healthProbe.status {
        case .notChecked:
            return item("backend_url", "Backend URL", .waiting, "Check Backend before iPhone demo.")
        case .checking:
            return item("backend_url", "Backend URL", .waiting, healthProbe.detail)
        case .reachable:
            return item("backend_url", "Backend URL", .ready, healthProbe.detail)
        case .unreachable:
            return item("backend_url", "Backend URL", .blocked, healthProbe.detail)
        }
    }

    private static func providerItem(
        readiness: ProviderReadinessResponse?,
        error: String?
    ) -> DevicePreflightItem {
        if let error {
            return item("providers", "Providers", .blocked, error)
        }
        guard let readiness else {
            return item("providers", "Providers", .waiting, "Backend readiness has not loaded.")
        }
        if readiness.overallDemoReady {
            let detail = readiness.overallRealReady ? "Real providers ready." : "Local demo providers ready."
            return item("providers", "Providers", .ready, detail)
        }
        let missing = readiness.providers.flatMap(\.missingEnv)
        let detail = missing.isEmpty ? "Provider setup needed." : "Missing \(missing.joined(separator: ", "))"
        return item("providers", "Providers", .blocked, detail)
    }

    private static func finalLaunchItem(
        report: FinalDemoLaunchReport?,
        error: String?
    ) -> DevicePreflightItem {
        if let error {
            return item("final_launch", "Final Launch", .blocked, error)
        }
        guard let report else {
            return item("final_launch", "Final Launch", .waiting, "Final launch report has not loaded.")
        }
        switch report.overallStatus {
        case "ready":
            return item("final_launch", "Final Launch", .ready, "Final launch lane ready.")
        case "blocked":
            return item("final_launch", "Final Launch", .blocked, finalLaunchDetail(report))
        default:
            return item("final_launch", "Final Launch", .waiting, finalLaunchDetail(report))
        }
    }

    private static func finalLaunchDetail(_ report: FinalDemoLaunchReport) -> String {
        if let blocker = report.firstBlocker {
            return finalLaunchFirstBlockerDetail(blocker, overallStatus: report.overallStatus)
        }
        if let firstAction = report.operatorChecklist.first {
            return "\(report.overallStatus): \(firstAction)"
        }
        if let firstBlockedPhase = report.launchPhases.first(where: { phase in
            phase.status == "blocked" || phase.status == "missing"
        }) {
            return "\(report.overallStatus): \(firstBlockedPhase.label)"
        }
        return "Final launch report \(report.overallStatus)."
    }

    private static func finalLaunchFirstBlockerDetail(
        _ blocker: FinalDemoLaunchFirstBlocker,
        overallStatus: String
    ) -> String {
        var headingParts = [
            overallStatus,
            blocker.id,
            blocker.status,
        ]
        if let classification = blocker.classification, !classification.isEmpty {
            headingParts.append(classification)
        }

        var parts = [headingParts.joined(separator: ": ")]
        if !blocker.command.isEmpty {
            parts.append(blocker.command)
        }
        if !blocker.detail.isEmpty {
            parts.append(blocker.detail)
        }
        return parts.joined(separator: " | ")
    }

    private static func externalActionLedgerItem(report: FinalDemoLaunchReport?) -> DevicePreflightItem {
        guard let ledger = report?.finalExternalActionLedger else {
            return item(
                "external_actions",
                "External Actions",
                .waiting,
                "External action ledger has not loaded."
            )
        }

        switch normalizedStatus(ledger.status) {
        case "ready":
            return item(
                "external_actions",
                "External Actions",
                .ready,
                externalActionLedgerDetail(ledger)
            )
        case "blocked", "missing", "manual", "live":
            return item(
                "external_actions",
                "External Actions",
                .blocked,
                externalActionLedgerDetail(ledger)
            )
        default:
            return item(
                "external_actions",
                "External Actions",
                .waiting,
                externalActionLedgerDetail(ledger)
            )
        }
    }

    private static func externalActionLedgerDetail(_ ledger: FinalExternalActionLedgerReport) -> String {
        var parts = [
            "External actions \(ledger.status): groups \(ledger.summary.groups), blocked \(ledger.summary.blocked), missing \(ledger.summary.missing), live \(ledger.summary.live), manual \(ledger.summary.manual)."
        ]
        if let nextAction = ledger.nextAction {
            parts.append(externalActionLedgerBlockerDetail(prefix: "Next action", nextAction))
        }
        if let firstBlocker = ledger.firstBlocker,
           !externalActionLedgerBlocker(firstBlocker, matches: ledger.nextAction) {
            parts.append(externalActionLedgerBlockerDetail(prefix: "First blocker", firstBlocker))
        }

        let attentionGroups = ledger.actionGroups.filter { group in
            normalizedStatus(group.status) != "ready"
        }
        let selectedGroups = attentionGroups.isEmpty ? ledger.actionGroups : attentionGroups
        parts.append(contentsOf: selectedGroups.prefix(3).map(externalActionLedgerGroupDetail))
        parts.append(contentsOf: externalActionLedgerOperatorActionRows(ledger.operatorActions))
        parts.append(
            "Consent: global confirmation \(boolText(ledger.safety.requiresUserConfirmationForGlobalActions)), live cost consent \(boolText(ledger.safety.requiresCostConsentForLiveActions))."
        )
        parts.append(
            "Safety: commands_run=\(boolText(ledger.safety.commandsRun)) global_mutation=\(boolText(ledger.safety.globalMutation)) live_calls=\(boolText(ledger.safety.liveProviderCalls))"
        )
        return parts.joined(separator: " ")
    }

    private static func externalActionLedgerBlocker(
        _ blocker: FinalExternalActionLedgerBlocker,
        matches nextAction: FinalExternalActionLedgerBlocker?
    ) -> Bool {
        guard let nextAction else {
            return false
        }
        return blocker.id == nextAction.id && blocker.command == nextAction.command
    }

    private static func externalActionLedgerBlockerDetail(
        prefix: String,
        _ blocker: FinalExternalActionLedgerBlocker
    ) -> String {
        var parts = [
            "\(prefix):",
            blocker.id,
            blocker.status,
            blocker.command,
            blocker.detail,
        ]
        if let validationCommand = blocker.validationCommand, !validationCommand.isEmpty {
            parts.append("validate \(validationCommand)")
        }
        return parts.filter { !normalizedStatus($0).isEmpty }.joined(separator: " ")
    }

    private static func externalActionLedgerGroupDetail(
        _ group: FinalExternalActionLedgerActionGroup
    ) -> String {
        "\(group.id): \(group.status) actions \(group.summary.actions), missing \(group.summary.missing), blocked \(group.summary.blocked), live \(group.summary.live), manual \(group.summary.manual)."
    }

    private static func externalActionLedgerOperatorActionRows(
        _ operatorActions: [String]
    ) -> [String] {
        var rows: [String] = []
        if let first = operatorActions.first(where: { !normalizedStatus($0).isEmpty }) {
            rows.append(first)
        }
        if let backend = operatorActions.first(where: { action in
            let trimmed = action.trimmingCharacters(in: .whitespacesAndNewlines)
            return !trimmed.isEmpty
                && trimmed.localizedCaseInsensitiveContains("backend-device-demo")
        }) {
            rows.append(backend)
        }

        var seen = Set<String>()
        return rows.filter { row in
            seen.insert(row).inserted
        }
    }

    private static func finalResourcesItem(report: FinalDemoLaunchReport?) -> DevicePreflightItem {
        guard let report else {
            return item(
                "final_resources",
                "Final Resources",
                .waiting,
                "Final resources preflight has not loaded."
            )
        }
        guard let preflight = report.finalResourcesPreflight else {
            return item(
                "final_resources",
                "Final Resources",
                .waiting,
                "Final resources preflight has not loaded."
            )
        }
        switch preflight.status {
        case "ready":
            return item(
                "final_resources",
                "Final Resources",
                .ready,
                "Final resources file ready to apply."
            )
        case "blocked":
            return item("final_resources", "Final Resources", .blocked, finalResourcesDetail(preflight))
        case "missing":
            return item(
                "final_resources",
                "Final Resources",
                .waiting,
                "Final resources file missing."
            )
        default:
            return item(
                "final_resources",
                "Final Resources",
                .waiting,
                "Final resources preflight \(preflight.status)."
            )
        }
    }

    private static func finalResourcesDetail(_ report: FinalResourcesPreflightReport) -> String {
        if let firstAction = report.operatorActions.first {
            return "\(report.status): \(firstAction)"
        }
        return "Final resources preflight \(report.status)."
    }

    private static func finalResourceRequirementsItem(report: FinalDemoLaunchReport?) -> DevicePreflightItem {
        guard let report else {
            return item(
                "final_resource_requirements",
                "Resource Requirements",
                .waiting,
                "Final resource requirements have not loaded."
            )
        }
        guard let requirements = report.finalResourceRequirements else {
            return item(
                "final_resource_requirements",
                "Resource Requirements",
                .waiting,
                "Final resource requirements have not loaded."
            )
        }
        if requirements.status == "ready" {
            return item(
                "final_resource_requirements",
                "Resource Requirements",
                .ready,
                finalResourceRequirementsReadyDetail(requirements)
            )
        }
        if let blocker = requirements.firstBlocker {
            return item(
                "final_resource_requirements",
                "Resource Requirements",
                .blocked,
                finalResourceRequirementsDetail(requirements, blocker: blocker)
            )
        }
        if requirements.status == "blocked" {
            return item(
                "final_resource_requirements",
                "Resource Requirements",
                .blocked,
                finalResourceRequirementsSummaryDetail(requirements)
            )
        }
        return item(
            "final_resource_requirements",
            "Resource Requirements",
            .waiting,
            finalResourceRequirementsSummaryDetail(requirements)
        )
    }

    private static func finalResourceRequirementsReadyDetail(
        _ requirements: FinalResourceRequirementsReport
    ) -> String {
        finalResourceRequirementsSummaryDetail(requirements)
    }

    private static func finalResourceRequirementsDetail(
        _ requirements: FinalResourceRequirementsReport,
        blocker: FinalResourceRequirementsFirstBlocker
    ) -> String {
        var parts = [finalResourceRequirementsSummaryDetail(requirements)]
        var blockerParts = ["First blocker:", blocker.id, blocker.status]
        if let classification = blocker.classification, !classification.isEmpty {
            blockerParts.append(classification)
        }
        if !blocker.command.isEmpty {
            blockerParts.append("| \(blocker.command)")
        }
        if !blocker.detail.isEmpty {
            blockerParts.append("| \(blocker.detail)")
        }
        if !blocker.domain.isEmpty {
            blockerParts.append("| \(blocker.domain)")
        }
        if !blocker.destination.isEmpty {
            blockerParts.append("| \(blocker.destination)")
        }
        if !blocker.validationCommand.isEmpty {
            blockerParts.append("| \(blocker.validationCommand)")
        }
        parts.append(blockerParts.joined(separator: " "))
        if let action = requirements.operatorActions.first, !action.isEmpty {
            parts.append("Action: \(action)")
        }
        return parts.joined(separator: " ")
    }

    private static func finalResourceRequirementsSummaryDetail(
        _ requirements: FinalResourceRequirementsReport
    ) -> String {
        "\(requirements.status): total \(requirements.summary.total), ready \(requirements.summary.ready), missing \(requirements.summary.missing), required \(requirements.summary.required), secret \(requirements.summary.secret)."
    }

    private static func finalResourceFillGuideItem(report: FinalDemoLaunchReport?) -> DevicePreflightItem {
        guard let report else {
            return item(
                "final_resource_fill_guide",
                "Fill Guide",
                .waiting,
                "Final resource fill guide has not loaded."
            )
        }
        guard let guide = report.finalResourceFillGuide else {
            return item(
                "final_resource_fill_guide",
                "Fill Guide",
                .waiting,
                "Final resource fill guide has not loaded."
            )
        }
        let requiredBlocker = guide.requiredInputs.first { input in
            input.required && (input.status == "missing" || input.status == "blocked")
        }
        if guide.status == "ready" {
            return item(
                "final_resource_fill_guide",
                "Fill Guide",
                .ready,
                finalResourceFillGuideReadyDetail(guide)
            )
        }
        if let blocker = guide.firstBlocker {
            return item(
                "final_resource_fill_guide",
                "Fill Guide",
                .blocked,
                finalResourceFillGuideDetail(guide, blocker: blocker)
            )
        }
        if let requiredBlocker {
            return item(
                "final_resource_fill_guide",
                "Fill Guide",
                .blocked,
                finalResourceFillGuideDetail(guide, input: requiredBlocker)
            )
        }
        if guide.status == "blocked" {
            return item(
                "final_resource_fill_guide",
                "Fill Guide",
                .blocked,
                finalResourceFillGuideDetail(guide, input: guide.requiredInputs.first)
            )
        }
        return item(
            "final_resource_fill_guide",
            "Fill Guide",
            .waiting,
            finalResourceFillGuideSummaryDetail(guide)
        )
    }

    private static func finalResourceFillGuideReadyDetail(
        _ guide: FinalResourceFillGuideReport
    ) -> String {
        "\(guide.status): required \(guide.summary.requiredInputs), optional \(guide.summary.optionalInputs), configured \(guide.summary.configuredInputs), secret \(guide.summary.secretInputs)."
    }

    private static func finalResourceFillGuideDetail(
        _ guide: FinalResourceFillGuideReport,
        input: FinalResourceFillGuideItem?
    ) -> String {
        var parts = [finalResourceFillGuideSummaryDetail(guide)]
        if let input {
            parts.append("\(input.id) \(input.status): \(input.fillAction)")
        }
        if let command = guide.commands.first, !command.isEmpty {
            parts.append("Command: \(command)")
        }
        return parts.joined(separator: " ")
    }

    private static func finalResourceFillGuideDetail(
        _ guide: FinalResourceFillGuideReport,
        blocker: FinalResourceFillGuideFirstBlocker
    ) -> String {
        var parts = [finalResourceFillGuideSummaryDetail(guide)]
        var blockerParts = ["First blocker:", blocker.id, blocker.status]
        if let classification = blocker.classification, !classification.isEmpty {
            blockerParts.append(classification)
        }
        if !blocker.command.isEmpty {
            blockerParts.append("| \(blocker.command)")
        }
        if !blocker.detail.isEmpty {
            blockerParts.append("| \(blocker.detail)")
        }
        if !blocker.validationCommand.isEmpty {
            blockerParts.append("| \(blocker.validationCommand)")
        }
        parts.append(blockerParts.joined(separator: " "))
        if let command = guide.commands.first, !command.isEmpty {
            parts.append("Command: \(command)")
        }
        return parts.joined(separator: " ")
    }

    private static func finalResourceFillGuideSummaryDetail(
        _ guide: FinalResourceFillGuideReport
    ) -> String {
        "\(guide.status): required \(guide.summary.requiredInputs), optional \(guide.summary.optionalInputs), configured \(guide.summary.configuredInputs), secret \(guide.summary.secretInputs)."
    }

    private static func finalResourceApplyPreviewItem(report: FinalDemoLaunchReport?) -> DevicePreflightItem {
        guard let report else {
            return item(
                "final_resource_apply_preview",
                "Apply Preview",
                .waiting,
                "Final resource apply preview has not loaded."
            )
        }
        guard let preview = report.finalResourceApplyPreview else {
            return item(
                "final_resource_apply_preview",
                "Apply Preview",
                .waiting,
                "Final resource apply preview has not loaded."
            )
        }
        if preview.status == "ready" {
            return item(
                "final_resource_apply_preview",
                "Apply Preview",
                .ready,
                finalResourceApplyPreviewReadyDetail(preview)
            )
        }
        if let blocker = preview.firstBlocker {
            return item(
                "final_resource_apply_preview",
                "Apply Preview",
                .blocked,
                finalResourceApplyPreviewDetail(preview, blocker: blocker)
            )
        }
        if preview.status == "blocked" {
            return item(
                "final_resource_apply_preview",
                "Apply Preview",
                .blocked,
                finalResourceApplyPreviewSummaryDetail(preview)
            )
        }
        return item(
            "final_resource_apply_preview",
            "Apply Preview",
            .waiting,
            finalResourceApplyPreviewSummaryDetail(preview)
        )
    }

    private static func finalResourceApplyPreviewReadyDetail(
        _ preview: FinalResourceApplyPreviewReport
    ) -> String {
        finalResourceApplyPreviewSummaryDetail(preview)
    }

    private static func finalResourceApplyPreviewDetail(
        _ preview: FinalResourceApplyPreviewReport,
        blocker: FinalResourceApplyPreviewFirstBlocker
    ) -> String {
        var parts = [finalResourceApplyPreviewSummaryDetail(preview)]
        var blockerParts = ["First blocker:", blocker.id, blocker.status]
        if let classification = blocker.classification, !classification.isEmpty {
            blockerParts.append(classification)
        }
        if !blocker.command.isEmpty {
            blockerParts.append("| \(blocker.command)")
        }
        if !blocker.detail.isEmpty {
            blockerParts.append("| \(blocker.detail)")
        }
        if !blocker.destination.isEmpty {
            blockerParts.append("| \(blocker.destination)")
        }
        if !blocker.writer.isEmpty {
            blockerParts.append("| \(blocker.writer)")
        }
        if !blocker.blockedBy.isEmpty {
            blockerParts.append("| blocked_by \(blocker.blockedBy.joined(separator: ", "))")
        }
        if !blocker.validationCommand.isEmpty {
            blockerParts.append("| \(blocker.validationCommand)")
        }
        parts.append(blockerParts.joined(separator: " "))
        if let command = preview.commands.first, !command.isEmpty {
            parts.append("Command: \(command)")
        }
        return parts.joined(separator: " ")
    }

    private static func finalResourceApplyPreviewSummaryDetail(
        _ preview: FinalResourceApplyPreviewReport
    ) -> String {
        "\(preview.status): ready \(preview.summary.ready), missing \(preview.summary.missing), blocked \(preview.summary.blocked), targets \(preview.summary.writeTargets), secret \(preview.summary.secret)."
    }

    private static func iosDeployRunbookItem(report: FinalDemoLaunchReport?) -> DevicePreflightItem {
        guard let report else {
            return item(
                "ios_deploy_runbook",
                "Deploy Runbook",
                .waiting,
                "iOS deploy runbook has not loaded."
            )
        }
        guard let runbook = report.iosDeployRunbook else {
            return item(
                "ios_deploy_runbook",
                "Deploy Runbook",
                .waiting,
                "iOS deploy runbook has not loaded."
            )
        }
        if runbook.status == "ready" {
            return item(
                "ios_deploy_runbook",
                "Deploy Runbook",
                .ready,
                iosDeployRunbookReadyDetail(runbook)
            )
        }
        if runbook.status == "blocked" || runbook.status == "partial" {
            return item(
                "ios_deploy_runbook",
                "Deploy Runbook",
                .blocked,
                iosDeployRunbookBlockedDetail(runbook)
            )
        }
        return item(
            "ios_deploy_runbook",
            "Deploy Runbook",
            .waiting,
            iosDeployRunbookSummaryDetail(runbook)
        )
    }

    private static func iosDeployRunbookReadyDetail(
        _ runbook: IOSDeployRunbookReport
    ) -> String {
        var parts = [iosDeployRunbookSummaryDetail(runbook)]
        parts.append(iosDeployRunbookSafetyDetail(runbook.safety))
        return parts.joined(separator: " ")
    }

    private static func iosDeployRunbookBlockedDetail(
        _ runbook: IOSDeployRunbookReport
    ) -> String {
        var parts = [iosDeployRunbookSummaryDetail(runbook)]
        if let step = firstDeployRunbookAttentionStep(runbook) {
            parts.append(iosDeployRunbookStepDetail(step))
        }
        if let action = runbook.operatorActions.first, !action.isEmpty {
            parts.append("Action: \(action)")
        }
        parts.append(iosDeployRunbookSafetyDetail(runbook.safety))
        return parts.joined(separator: " ")
    }

    private static func firstDeployRunbookAttentionStep(
        _ runbook: IOSDeployRunbookReport
    ) -> IOSDeployRunbookCommandStep? {
        runbook.commandSequence.first { step in
            step.status != "ready" && step.status != "manual"
        }
    }

    private static func iosDeployRunbookStepDetail(
        _ step: IOSDeployRunbookCommandStep
    ) -> String {
        var parts = [
            "Step:",
            step.id,
            step.status,
            step.label,
            "| \(step.command)",
        ]
        if let note = step.notes.first, !note.isEmpty {
            parts.append("| \(note)")
        }
        if step.requiresConsent {
            parts.append("| consent required")
        }
        return parts.joined(separator: " ")
    }

    private static func iosDeployRunbookSummaryDetail(
        _ runbook: IOSDeployRunbookReport
    ) -> String {
        let requiredSlots = runbook.inputSlots.filter(\.required).count
        return "\(runbook.status): mode \(runbook.mode), required slots \(requiredSlots), commands \(runbook.commandSequence.count)."
    }

    private static func iosDeployRunbookSafetyDetail(
        _ safety: IOSDeployRunbookSafety
    ) -> String {
        "Safety: commands_run=\(safety.commandsRun) provider_calls=\(safety.providerCalls) global_mutation=\(safety.globalMutation)."
    }

    private static func iosDeviceEvidenceBundleItem(report: FinalDemoLaunchReport?) -> DevicePreflightItem {
        guard let report else {
            return item(
                "ios_device_evidence_bundle",
                "Device Evidence",
                .waiting,
                "iOS device evidence bundle has not loaded."
            )
        }
        guard let bundle = report.iosDeviceEvidenceBundle else {
            return item(
                "ios_device_evidence_bundle",
                "Device Evidence",
                .waiting,
                "iOS device evidence bundle has not loaded."
            )
        }
        if bundle.status == "ready" {
            return item(
                "ios_device_evidence_bundle",
                "Device Evidence",
                .ready,
                iosDeviceEvidenceReadyDetail(bundle)
            )
        }
        if bundle.status == "blocked" {
            return item(
                "ios_device_evidence_bundle",
                "Device Evidence",
                .blocked,
                iosDeviceEvidenceBlockedDetail(bundle)
            )
        }
        return item(
            "ios_device_evidence_bundle",
            "Device Evidence",
            .waiting,
            iosDeviceEvidenceSummaryDetail(bundle)
        )
    }

    private static func iosDeviceEvidenceReadyDetail(
        _ bundle: IOSDeviceEvidenceBundleReport
    ) -> String {
        var parts = [iosDeviceEvidenceSummaryDetail(bundle)]
        parts.append(iosDeviceEvidenceSafetyDetail(bundle.safety))
        return parts.joined(separator: " ")
    }

    private static func iosDeviceEvidenceBlockedDetail(
        _ bundle: IOSDeviceEvidenceBundleReport
    ) -> String {
        var parts = [iosDeviceEvidenceSummaryDetail(bundle)]
        if let slot = firstIOSDeviceEvidenceAttentionSlot(bundle) {
            parts.append(iosDeviceEvidenceSlotDetail(slot))
        }
        if let action = bundle.operatorActions.first, !action.isEmpty {
            parts.append("Action: \(action)")
        }
        parts.append(iosDeviceEvidenceSafetyDetail(bundle.safety))
        return parts.joined(separator: " ")
    }

    private static func firstIOSDeviceEvidenceAttentionSlot(
        _ bundle: IOSDeviceEvidenceBundleReport
    ) -> IOSDeviceEvidenceSlot? {
        bundle.evidenceSlots.first { slot in
            slot.status != "ready"
        }
    }

    private static func iosDeviceEvidenceSlotDetail(
        _ slot: IOSDeviceEvidenceSlot
    ) -> String {
        var parts = [
            "Slot:",
            slot.id,
            slot.status,
            slot.label,
            "| \(slot.command)",
        ]
        if let classification = slot.classification, !classification.isEmpty {
            parts.append("| \(classification)")
        }
        if !slot.detail.isEmpty {
            parts.append("| \(slot.detail)")
        }
        if slot.globalAction {
            parts.append("| global action")
        }
        if slot.xcodeOrSigning {
            parts.append("| Xcode/signing")
        }
        return parts.joined(separator: " ")
    }

    private static func iosDeviceEvidenceSummaryDetail(
        _ bundle: IOSDeviceEvidenceBundleReport
    ) -> String {
        "\(bundle.status): ready \(bundle.summary.ready), missing \(bundle.summary.missing), blocked \(bundle.summary.blocked), required \(bundle.summary.required), global \(bundle.summary.globalActions)."
    }

    private static func iosDeviceEvidenceSafetyDetail(
        _ safety: IOSDeviceEvidenceBundleSafety
    ) -> String {
        "Safety: commands_run=\(safety.commandsRun) xcode=\(safety.xcodeOrSigning) global_mutation=\(safety.globalMutation)."
    }

    private static func iosLaunchRehearsalReadinessItem(
        report: FinalDemoLaunchReport?
    ) -> DevicePreflightItem {
        guard let report else {
            return item(
                "ios_device_launch_rehearsal_readiness",
                "Launch Rehearsal",
                .waiting,
                "iOS launch rehearsal readiness has not loaded."
            )
        }
        guard let readiness = report.iosDeviceLaunchRehearsalReadiness else {
            return item(
                "ios_device_launch_rehearsal_readiness",
                "Launch Rehearsal",
                .waiting,
                "iOS launch rehearsal readiness has not loaded."
            )
        }

        switch readiness.status.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() {
        case "ready":
            return item(
                "ios_device_launch_rehearsal_readiness",
                "Launch Rehearsal",
                .ready,
                iosLaunchRehearsalReadyDetail(readiness)
            )
        case "blocked", "partial":
            return item(
                "ios_device_launch_rehearsal_readiness",
                "Launch Rehearsal",
                .blocked,
                iosLaunchRehearsalAttentionDetail(readiness)
            )
        case "missing":
            return item(
                "ios_device_launch_rehearsal_readiness",
                "Launch Rehearsal",
                .waiting,
                iosLaunchRehearsalAttentionDetail(readiness)
            )
        default:
            return item(
                "ios_device_launch_rehearsal_readiness",
                "Launch Rehearsal",
                .waiting,
                iosLaunchRehearsalReadyDetail(readiness)
            )
        }
    }

    private static func iosLaunchRehearsalReadyDetail(
        _ readiness: IOSDeviceLaunchRehearsalReadinessReport
    ) -> String {
        var parts = [
            iosLaunchRehearsalSummaryDetail(readiness),
            iosLaunchRehearsalFreshnessDetail(readiness),
            "Source: \(readiness.sourceFile.path).",
            iosLaunchRehearsalSafetyDetail(readiness.safety),
        ]
        if let row = readiness.sequence.first,
           let sourceFreshness = iosLaunchRehearsalSourceFreshnessDetail(row) {
            parts.insert(sourceFreshness, at: 2)
        }
        return parts.joined(separator: " ")
    }

    private static func iosLaunchRehearsalAttentionDetail(
        _ readiness: IOSDeviceLaunchRehearsalReadinessReport
    ) -> String {
        var parts = [
            iosLaunchRehearsalSummaryDetail(readiness),
            iosLaunchRehearsalFreshnessDetail(readiness),
        ]
        if let row = firstIOSLaunchRehearsalAttentionRow(readiness) {
            if let sourceFreshness = iosLaunchRehearsalSourceFreshnessDetail(row) {
                parts.append(sourceFreshness)
            }
            parts.append(iosLaunchRehearsalSequenceDetail(row))
        }
        if let blocker = readiness.blockers.first {
            parts.append(iosLaunchRehearsalBlockerDetail(blocker))
        } else if let action = readiness.operatorActions.first, !action.isEmpty {
            parts.append("Action: \(action)")
        }
        if let savedNextAction = iosLaunchRehearsalSavedNextActionDetail(readiness) {
            parts.append(savedNextAction)
        }
        parts.append(iosLaunchRehearsalSafetyDetail(readiness.safety))
        return parts.joined(separator: " ")
    }

    private static func firstIOSLaunchRehearsalAttentionRow(
        _ readiness: IOSDeviceLaunchRehearsalReadinessReport
    ) -> IOSDeviceLaunchRehearsalSequenceRow? {
        readiness.sequence.first { row in
            row.status.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() != "ready"
        }
    }

    private static func iosLaunchRehearsalSequenceDetail(
        _ row: IOSDeviceLaunchRehearsalSequenceRow
    ) -> String {
        var parts = [
            "Step:",
            row.id,
            row.status,
            row.label,
            "| \(row.command)",
        ]
        if let classification = row.classification, !classification.isEmpty {
            parts.append("| \(classification)")
        }
        return parts.joined(separator: " ")
    }

    private static func iosLaunchRehearsalBlockerDetail(
        _ blocker: ThreeDEvaluationReadinessBlocker
    ) -> String {
        [
            "Blocker:",
            blocker.id,
            blocker.status,
            blocker.classification,
            "| \(blocker.command)",
            "| \(blocker.detail)",
        ].joined(separator: " ")
    }

    private static func iosLaunchRehearsalSavedNextActionDetail(
        _ readiness: IOSDeviceLaunchRehearsalReadinessReport
    ) -> String? {
        guard let savedNextAction = readiness.deviceActionBundle?.firstAction.savedNextAction,
              !savedNextAction.command.isEmpty
        else {
            return nil
        }

        var detail = "Saved next: \(savedNextAction.command)"
        if !savedNextAction.detail.isEmpty {
            detail += " | \(savedNextAction.detail)"
        }
        return detail
    }

    private static func iosLaunchRehearsalSummaryDetail(
        _ readiness: IOSDeviceLaunchRehearsalReadinessReport
    ) -> String {
        "\(readiness.status): ready \(readiness.summary.ready), missing \(readiness.summary.missing), blocked \(readiness.summary.blocked), partial \(readiness.summary.partial)."
    }

    private static func iosLaunchRehearsalFreshnessDetail(
        _ readiness: IOSDeviceLaunchRehearsalReadinessReport
    ) -> String {
        guard let freshness = readiness.freshness else {
            return "Freshness: not reported."
        }
        return "Freshness: \(freshness.classification)"
    }

    private static func iosLaunchRehearsalSourceFreshnessDetail(
        _ row: IOSDeviceLaunchRehearsalSequenceRow
    ) -> String? {
        var parts: [String] = []
        if let summary = row.freshnessSummary {
            parts.append(
                "Source freshness: \(summary["fresh", default: 0]) fresh, \(summary["stale", default: 0]) stale, \(summary["unknown", default: 0]) unknown."
            )
        }
        if let status = row.freshnessStatus,
           status.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() == "stale",
           let classification = row.freshnessClassification,
           !classification.isEmpty {
            parts.append("\(row.id): \(status) | \(classification)")
        }
        return parts.isEmpty ? nil : parts.joined(separator: " ")
    }

    private static func iosLaunchRehearsalSafetyDetail(
        _ safety: IOSDeviceLaunchRehearsalSafety
    ) -> String {
        "Safety: commands_run=\(safety.commandsRun) xcode=\(safety.xcodeOrSigning) global_mutation=\(safety.globalMutation)."
    }

    private static func iosDeviceLaunchCertificateItem(report: FinalDemoLaunchReport?) -> DevicePreflightItem {
        guard let report else {
            return item(
                "ios_device_launch_certificate",
                "Launch Certificate",
                .waiting,
                "iOS device launch certificate has not loaded."
            )
        }
        guard let certificate = report.iosDeviceLaunchCertificate else {
            return item(
                "ios_device_launch_certificate",
                "Launch Certificate",
                .waiting,
                "iOS device launch certificate has not loaded."
            )
        }

        switch certificate.status.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() {
        case "ready":
            return item(
                "ios_device_launch_certificate",
                "Launch Certificate",
                .ready,
                iosDeviceLaunchCertificateReadyDetail(certificate)
            )
        case "missing":
            return item(
                "ios_device_launch_certificate",
                "Launch Certificate",
                .waiting,
                iosDeviceLaunchCertificateAttentionDetail(certificate)
            )
        case "blocked", "partial", "manual", "live":
            return item(
                "ios_device_launch_certificate",
                "Launch Certificate",
                .blocked,
                iosDeviceLaunchCertificateAttentionDetail(certificate)
            )
        default:
            return item(
                "ios_device_launch_certificate",
                "Launch Certificate",
                .waiting,
                iosDeviceLaunchCertificateReadyDetail(certificate)
            )
        }
    }

    private static func iosDeviceLaunchCertificateReadyDetail(
        _ certificate: IOSDeviceLaunchCertificateReport
    ) -> String {
        var parts = [
            iosDeviceLaunchCertificateSummaryDetail(certificate),
            iosDeviceLaunchCertificateSafetyDetail(certificate.safety),
        ]
        if let gate = certificate.deviceGates.first {
            parts.insert(iosDeviceLaunchCertificateGateDetail(gate), at: 1)
        }
        return parts.joined(separator: " ")
    }

    private static func iosDeviceLaunchCertificateAttentionDetail(
        _ certificate: IOSDeviceLaunchCertificateReport
    ) -> String {
        var parts = [iosDeviceLaunchCertificateSummaryDetail(certificate)]
        if let action = certificate.operatorActions.first, !action.isEmpty {
            parts.append("Action: \(action)")
        }
        if let gate = firstIOSDeviceLaunchCertificateAttentionGate(certificate) {
            parts.append(iosDeviceLaunchCertificateGateDetail(gate))
        }
        if let consentGate = firstIOSDeviceLaunchCertificateConsentGate(certificate),
           consentGate.id != firstIOSDeviceLaunchCertificateAttentionGate(certificate)?.id {
            parts.append(iosDeviceLaunchCertificateGateDetail(consentGate))
        }
        parts.append(iosDeviceLaunchCertificateSafetyDetail(certificate.safety))
        return parts.joined(separator: " ")
    }

    private static func firstIOSDeviceLaunchCertificateAttentionGate(
        _ certificate: IOSDeviceLaunchCertificateReport
    ) -> IOSDeviceLaunchCertificateGate? {
        let nonReadyRequired = certificate.deviceGates.filter { gate in
            gate.required
                && gate.status.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() != "ready"
        }
        if let gate = nonReadyRequired.first {
            return gate
        }
        return certificate.deviceGates.first { gate in
            gate.status.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() != "ready"
        }
    }

    private static func firstIOSDeviceLaunchCertificateConsentGate(
        _ certificate: IOSDeviceLaunchCertificateReport
    ) -> IOSDeviceLaunchCertificateGate? {
        certificate.deviceGates.first { gate in
            gate.requiresConsent
                && gate.status.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() != "ready"
        }
    }

    private static func iosDeviceLaunchCertificateSummaryDetail(
        _ certificate: IOSDeviceLaunchCertificateReport
    ) -> String {
        "\(certificate.status): mode \(certificate.mode), ready \(certificate.summary.ready), missing \(certificate.summary.missing), blocked \(certificate.summary.blocked), manual \(certificate.summary.manual), partial \(certificate.summary.partial), live \(certificate.summary.live)."
    }

    private static func iosDeviceLaunchCertificateGateDetail(
        _ gate: IOSDeviceLaunchCertificateGate
    ) -> String {
        var parts = [
            "Gate:",
            gate.id,
            gate.status,
            gate.label,
            "| \(gate.command)",
        ]
        if let note = gate.notes.first, !note.isEmpty {
            parts.append("| \(note)")
        }
        if gate.requiresConsent {
            parts.append("| requires consent")
        }
        return parts.joined(separator: " ")
    }

    private static func iosDeviceLaunchCertificateSafetyDetail(
        _ safety: IOSDeviceLaunchCertificateSafety
    ) -> String {
        "Safety: commands_run=\(safety.commandsRun) provider_calls=\(safety.providerCalls) writes_env=\(safety.writesBackendEnv) writes_ios_config=\(safety.writesIosDeployConfig) global=\(safety.globalMutation) xcode=\(safety.xcodeOrSigning) keychain=\(safety.keychainWrites)."
    }

    private static func finalClosurePacketItem(report: FinalDemoLaunchReport?) -> DevicePreflightItem {
        guard let report else {
            return item(
                "final_launch_closure_packet",
                "Final Closure",
                .waiting,
                "Final launch closure packet has not loaded."
            )
        }
        guard let packet = report.finalLaunchClosurePacket else {
            return item(
                "final_launch_closure_packet",
                "Final Closure",
                .waiting,
                "Final launch closure packet has not loaded."
            )
        }

        switch packet.status.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() {
        case "ready":
            return item(
                "final_launch_closure_packet",
                "Final Closure",
                .ready,
                finalClosurePacketReadyDetail(packet)
            )
        case "blocked", "partial":
            return item(
                "final_launch_closure_packet",
                "Final Closure",
                .blocked,
                finalClosurePacketAttentionDetail(packet)
            )
        default:
            return item(
                "final_launch_closure_packet",
                "Final Closure",
                .waiting,
                finalClosurePacketReadyDetail(packet)
            )
        }
    }

    private static func finalClosurePacketReadyDetail(
        _ packet: FinalLaunchClosurePacketReport
    ) -> String {
        [
            finalClosurePacketSummaryDetail(packet),
            finalClosurePacketConsentDetail(packet),
            finalClosurePacketSafetyDetail(packet.safety),
        ].joined(separator: " ")
    }

    private static func finalClosurePacketAttentionDetail(
        _ packet: FinalLaunchClosurePacketReport
    ) -> String {
        var parts = [finalClosurePacketSummaryDetail(packet)]
        if let blocker = packet.firstBlocker {
            parts.append(finalClosurePacketFirstBlockerDetail(blocker))
        }
        if let section = firstFinalClosureAttentionSection(packet) {
            parts.append(finalClosurePacketSectionDetail(section))
        }
        if let configuredBundle = packet.sectionsById["configured_evidence_bundle"],
           configuredBundle.id != firstFinalClosureAttentionSection(packet)?.id {
            parts.append(finalClosurePacketSectionDetail(configuredBundle))
        }
        if let action = packet.operatorActions.first, !action.isEmpty {
            parts.append("Action: \(action)")
        }
        parts.append(finalClosurePacketConsentDetail(packet))
        parts.append(finalClosurePacketSafetyDetail(packet.safety))
        return parts.joined(separator: " ")
    }

    private static func firstFinalClosureAttentionSection(
        _ packet: FinalLaunchClosurePacketReport
    ) -> FinalLaunchClosurePacketSection? {
        packet.sections.first { section in
            section.status.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() != "ready"
        }
    }

    private static func finalClosurePacketSummaryDetail(
        _ packet: FinalLaunchClosurePacketReport
    ) -> String {
        "\(packet.status): sections \(packet.summary.sections), actions \(packet.summary.actions), blocked \(packet.summary.blocked), live \(packet.summary.live), cost consent \(packet.summary.requiresCostConsent)."
    }

    private static func finalClosurePacketFirstBlockerDetail(
        _ blocker: FinalLaunchClosurePacketBlocker
    ) -> String {
        var parts = [
            "First blocker:",
            blocker.id,
            blocker.status,
        ]
        if let classification = blocker.classification, !classification.isEmpty {
            parts.append(classification)
        }
        if !blocker.actionId.isEmpty {
            parts.append("| \(blocker.actionId)")
        }
        if !blocker.command.isEmpty {
            parts.append("| \(blocker.command)")
        }
        if !blocker.detail.isEmpty {
            parts.append("| \(blocker.detail)")
        }
        return parts.joined(separator: " ")
    }

    private static func finalClosurePacketSectionDetail(
        _ section: FinalLaunchClosurePacketSection
    ) -> String {
        let action = section.firstAction
        var parts = [
            "Section:",
            section.id,
            section.status,
            "| \(action.id)",
            action.status,
            "| \(action.command)",
        ]
        if !action.detail.isEmpty {
            parts.append("| \(action.detail)")
        }
        return parts.joined(separator: " ")
    }

    private static func finalClosurePacketConsentDetail(
        _ packet: FinalLaunchClosurePacketReport
    ) -> String {
        "Consent: user input \(packet.summary.requiresUserInput), confirmation \(packet.summary.requiresUserConfirmation), cost consent \(packet.summary.requiresCostConsent), global \(packet.summary.globalActions), xcode \(packet.summary.xcodeOrSigningActions)."
    }

    private static func finalClosurePacketSafetyDetail(
        _ safety: FinalLaunchClosurePacketSafety
    ) -> String {
        "Safety: commands_run=\(safety.commandsRun) global=\(safety.globalMutation) live_calls=\(safety.liveProviderCalls)."
    }

    private static func finalOperatorHandoffItem(report: FinalDemoLaunchReport?) -> DevicePreflightItem {
        guard let report else {
            return item(
                "final_operator_handoff",
                "Operator Handoff",
                .waiting,
                "Final operator handoff has not loaded."
            )
        }
        guard let handoff = report.finalOperatorHandoff else {
            return item(
                "final_operator_handoff",
                "Operator Handoff",
                .waiting,
                "Final operator handoff has not loaded."
            )
        }

        switch handoff.status.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() {
        case "ready":
            return item(
                "final_operator_handoff",
                "Operator Handoff",
                .ready,
                finalOperatorHandoffReadyDetail(handoff)
            )
        case "missing":
            return item(
                "final_operator_handoff",
                "Operator Handoff",
                .waiting,
                finalOperatorHandoffAttentionDetail(handoff)
            )
        case "blocked", "partial", "live":
            return item(
                "final_operator_handoff",
                "Operator Handoff",
                .blocked,
                finalOperatorHandoffAttentionDetail(handoff)
            )
        default:
            return item(
                "final_operator_handoff",
                "Operator Handoff",
                .waiting,
                finalOperatorHandoffReadyDetail(handoff)
            )
        }
    }

    private static func finalOperatorHandoffReadyDetail(
        _ handoff: FinalOperatorHandoffReport
    ) -> String {
        [
            finalOperatorHandoffSummaryDetail(handoff),
            finalOperatorHandoffSafetyDetail(handoff.safety),
        ].joined(separator: " ")
    }

    private static func finalOperatorHandoffAttentionDetail(
        _ handoff: FinalOperatorHandoffReport
    ) -> String {
        var parts = [finalOperatorHandoffSummaryDetail(handoff)]
        if let action = handoff.nextActions.first, !action.isEmpty {
            parts.append("Action: \(action)")
        }
        if let step = firstFinalOperatorHandoffAttentionStep(handoff) {
            parts.append(finalOperatorHandoffStepDetail(step))
        }
        parts.append(finalOperatorHandoffSafetyDetail(handoff.safety))
        return parts.joined(separator: " ")
    }

    private static func firstFinalOperatorHandoffAttentionStep(
        _ handoff: FinalOperatorHandoffReport
    ) -> FinalOperatorHandoffStep? {
        let attentionSteps = handoff.steps.filter { step in
            step.status.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() != "ready"
        }
        return attentionSteps.first(where: \.requiresConsent) ?? attentionSteps.first
    }

    private static func finalOperatorHandoffSummaryDetail(
        _ handoff: FinalOperatorHandoffReport
    ) -> String {
        "\(handoff.status): ready \(handoff.summary.ready), missing \(handoff.summary.missing), blocked \(handoff.summary.blocked), manual \(handoff.summary.manual), optional \(handoff.summary.optional), partial \(handoff.summary.partial), live \(handoff.summary.live)."
    }

    private static func finalOperatorHandoffStepDetail(
        _ step: FinalOperatorHandoffStep
    ) -> String {
        var parts = [
            "Step:",
            step.id,
            step.status,
            step.label,
            "| \(step.command)",
            "| \(step.source)",
        ]
        if let note = step.notes.first, !note.isEmpty {
            parts.append("| \(note)")
        } else if !step.requiredFor.isEmpty {
            parts.append("| \(step.requiredFor)")
        }
        if step.requiresConsent {
            parts.append("| requires consent")
        }
        return parts.joined(separator: " ")
    }

    private static func finalOperatorHandoffSafetyDetail(
        _ safety: FinalOperatorHandoffSafety
    ) -> String {
        "Safety: commands_run=\(safety.commandsRun) provider_calls=\(safety.providerCalls) global=\(safety.globalMutation) app_exec=\(safety.commandExecutionFromApp)."
    }

    private static func localDemoItem(_ summary: FinalShowcaseSummary) -> DevicePreflightItem {
        switch summary.overallStatus {
        case .readyForLocalDemo:
            return item("local_demo", "Local Demo", .ready, "Final showcase state is ready.")
        case .needsAttention:
            return item("local_demo", "Local Demo", .blocked, summary.title)
        case .waiting:
            return item("local_demo", "Local Demo", .waiting, summary.title)
        }
    }

    private static func savedHistoryItem(_ tickCount: Int) -> DevicePreflightItem {
        if tickCount > 0 {
            let label = tickCount == 1 ? "1 saved NPC tick." : "\(tickCount) saved NPC ticks."
            return item("saved_history", "Saved NPCs", .ready, label)
        }
        return item("saved_history", "Saved NPCs", .waiting, "No saved NPC ticks yet.")
    }

    private static func item(
        _ id: String,
        _ label: String,
        _ status: DevicePreflightStatus,
        _ detail: String
    ) -> DevicePreflightItem {
        DevicePreflightItem(id: id, label: label, status: status, detail: sanitize(detail))
    }

    private static func overallStatus(_ items: [DevicePreflightItem]) -> DevicePreflightStatus {
        if items.contains(where: { $0.status == .blocked }) {
            return .blocked
        }
        let required = Set([
            "backend_url",
            "providers",
            "final_launch",
            "external_actions",
            "final_resources",
            "final_resource_requirements",
            "final_resource_fill_guide",
            "final_resource_apply_preview",
            "ios_deploy_runbook",
            "ios_device_evidence_bundle",
            "ios_device_launch_rehearsal_readiness",
            "ios_device_launch_certificate",
            "final_launch_closure_packet",
            "final_operator_handoff",
            "local_demo",
        ])
        let requiredReady = required.allSatisfy { id in
            items.first(where: { $0.id == id })?.status == .ready
        }
        return requiredReady ? .ready : .waiting
    }

    private static func title(for status: DevicePreflightStatus) -> String {
        switch status {
        case .blocked:
            return "Fix device blockers before demo"
        case .waiting:
            return "Device demo preflight pending"
        case .ready:
            return "Device demo preflight ready"
        }
    }

    private static func isLoopback(_ host: String) -> Bool {
        host == "127.0.0.1" || host == "localhost" || host == "::1"
    }

    private static func boolText(_ value: Bool) -> String {
        value ? "true" : "false"
    }

    private static func normalizedStatus(_ value: String) -> String {
        value.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
    }

    private static func sanitize(_ value: String) -> String {
        let lowered = value.lowercased()
        let apiKeyAssignmentMarker = "api" + "_key="
        let bearerMarker = "Bearer" + " "
        if value.contains("sk-")
            || value.contains("/Users/")
            || value.contains("file://")
            || value.contains("local-capture://")
            || value.contains("Authorization")
            || value.contains(bearerMarker)
            || lowered.contains(apiKeyAssignmentMarker)
            || lowered.contains("checkout")
        {
            return "[withheld]"
        }
        return value
    }
}
