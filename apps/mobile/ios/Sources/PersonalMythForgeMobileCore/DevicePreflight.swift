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
            finalResourcesItem(report: finalDemoLaunch),
            finalResourceFillGuideItem(report: finalDemoLaunch),
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

    private static func finalResourceFillGuideSummaryDetail(
        _ guide: FinalResourceFillGuideReport
    ) -> String {
        "\(guide.status): required \(guide.summary.requiredInputs), optional \(guide.summary.optionalInputs), configured \(guide.summary.configuredInputs), secret \(guide.summary.secretInputs)."
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
            "final_resources",
            "final_resource_fill_guide",
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
