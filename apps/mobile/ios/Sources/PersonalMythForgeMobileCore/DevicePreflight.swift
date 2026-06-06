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

public enum DevicePreflightSummaryBuilder {
    public static func build(
        backendBaseURL: URL,
        providerReadiness: ProviderReadinessResponse?,
        providerReadinessError: String?,
        finalShowcaseSummary: FinalShowcaseSummary,
        savedNPCTickCount: Int
    ) -> DevicePreflightSummary {
        let items = [
            backendItem(backendBaseURL),
            providerItem(readiness: providerReadiness, error: providerReadinessError),
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
                "This preflight does not install or sign the app.",
            ]
        )
    }

    private static func backendItem(_ url: URL) -> DevicePreflightItem {
        let host = url.host?.lowercased() ?? ""
        if isLoopback(host) {
            return item(
                "backend_url",
                "Backend URL",
                .blocked,
                "Loopback is not reachable from iPhone; use the Mac LAN URL."
            )
        }
        if isPrivateLAN(host) {
            return item("backend_url", "Backend URL", .ready, "LAN backend URL is ready for iPhone.")
        }
        return item("backend_url", "Backend URL", .waiting, "Confirm this backend URL is reachable from iPhone.")
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
        let required = Set(["backend_url", "providers", "local_demo"])
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

    private static func isPrivateLAN(_ host: String) -> Bool {
        if host.hasPrefix("10.") || host.hasPrefix("192.168.") {
            return true
        }
        let parts = host.split(separator: ".").compactMap { Int($0) }
        guard parts.count == 4 else {
            return false
        }
        return parts[0] == 172 && (16...31).contains(parts[1])
    }

    private static func sanitize(_ value: String) -> String {
        let lowered = value.lowercased()
        let apiKeyMarker = "api" + "_key"
        let bearerMarker = "Bearer" + " "
        if value.contains("sk-")
            || value.contains("/Users/")
            || value.contains("file://")
            || value.contains("local-capture://")
            || value.contains("Authorization")
            || value.contains(bearerMarker)
            || lowered.contains(apiKeyMarker)
            || lowered.contains("checkout")
        {
            return "[withheld]"
        }
        return value
    }
}
