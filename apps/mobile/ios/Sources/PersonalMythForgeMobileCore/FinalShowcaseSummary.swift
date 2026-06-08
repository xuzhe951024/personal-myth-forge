import Foundation

public enum FinalShowcaseSummaryStatus: String, Codable, Equatable, Sendable {
    case waiting
    case readyForLocalDemo
    case needsAttention
}

public enum FinalShowcaseStageStatus: String, Codable, Equatable, Sendable {
    case waiting
    case ready
    case needsAttention
    case optional
}

public struct FinalShowcaseSummaryStage: Codable, Equatable, Sendable {
    public var id: String
    public var label: String
    public var status: FinalShowcaseStageStatus
    public var detail: String

    public init(id: String, label: String, status: FinalShowcaseStageStatus, detail: String) {
        self.id = id
        self.label = label
        self.status = status
        self.detail = detail
    }
}

public struct FinalShowcaseSummary: Codable, Equatable, Sendable {
    public var overallStatus: FinalShowcaseSummaryStatus
    public var title: String
    public var stages: [FinalShowcaseSummaryStage]
    public var privacyNotes: [String]

    public init(
        overallStatus: FinalShowcaseSummaryStatus,
        title: String,
        stages: [FinalShowcaseSummaryStage],
        privacyNotes: [String]
    ) {
        self.overallStatus = overallStatus
        self.title = title
        self.stages = stages
        self.privacyNotes = privacyNotes
    }

    public func stage(id: String) -> FinalShowcaseSummaryStage? {
        stages.first { $0.id == id }
    }
}

public enum FinalShowcaseSummaryBuilder {
    public static func build(
        captureSelection: CaptureMediaSelection?,
        session: MythSession?,
        npcTickHistoryCount: Int,
        printQuote: PrintQuote?,
        providerReadiness: ProviderReadinessResponse?,
        providerReadinessError: String?,
        finalLaunchSummary: FinalLaunchMobileSummary? = nil
    ) -> FinalShowcaseSummary {
        var stages = [
            captureStage(captureSelection),
            threeDStage(session),
            npcStage(session: session, npcTickHistoryCount: npcTickHistoryCount),
            printStage(session: session, printQuote: printQuote),
            resourcesStage(readiness: providerReadiness, error: providerReadinessError),
        ]
        if let finalLaunchSummary {
            stages.append(providerHandoffStage(finalLaunchSummary))
            stages.append(localSmokeStage(finalLaunchSummary))
            stages.append(iosDeployStage(finalLaunchSummary))
            stages.append(threeDEvaluationStage(finalLaunchSummary))
            stages.append(npcEvaluationStage(finalLaunchSummary))
            stages.append(operatorHandoffStage(finalLaunchSummary))
            stages.append(finalLaunchStage(finalLaunchSummary))
        }
        return FinalShowcaseSummary(
            overallStatus: overallStatus(session: session, stages: stages),
            title: sanitize(session?.mythSeed.title ?? "Waiting for first myth session"),
            stages: stages,
            privacyNotes: [
                "Raw capture media stays out of the summary.",
                "Provider keys remain backend-only.",
                "Checkout links are not surfaced in the demo summary.",
                "Local file paths are withheld.",
            ]
        )
    }

    private static func providerHandoffStage(_ summary: FinalLaunchMobileSummary) -> FinalShowcaseSummaryStage {
        let statusRows = providerHandoffStatusRows(summary)
        let combinedRows = providerHandoffCombinedRows(summary)
        return stage(
            "provider_handoff",
            "Provider Handoff",
            providerHandoffStatus(statusRows),
            providerHandoffDetail(statusRows: statusRows, combinedRows: combinedRows)
        )
    }

    private static func providerHandoffStatusRows(_ summary: FinalLaunchMobileSummary) -> [String] {
        let liveRows = summary.liveProviderEvidenceRows
        if !liveRows.isEmpty, providerHandoffStatus(liveRows) != .ready {
            return liveRows
        }
        let applyRows = summary.applyPreviewRows
        if !applyRows.isEmpty {
            if providerHandoffStatus(applyRows) == .ready {
                return liveRows.isEmpty ? applyRows : liveRows
            }
            return applyRows
        }
        let candidates = [
            summary.resourceFillGuideRows,
            summary.resourceHandoffRows,
        ].filter { !$0.isEmpty }
        if let firstNotReady = candidates.first(where: { providerHandoffStatus($0) != .ready }) {
            return firstNotReady
        }
        return liveRows.isEmpty ? candidates.first ?? [] : liveRows
    }

    private static func providerHandoffCombinedRows(_ summary: FinalLaunchMobileSummary) -> [String] {
        providerHandoffCandidateRows(summary).flatMap { $0 }
    }

    private static func providerHandoffCandidateRows(_ summary: FinalLaunchMobileSummary) -> [[String]] {
        [
            summary.liveProviderEvidenceRows,
            summary.applyPreviewRows,
            summary.resourceFillGuideRows,
            summary.resourceHandoffRows,
        ].filter { !$0.isEmpty }
    }

    private static func providerHandoffStatus(_ rows: [String]) -> FinalShowcaseStageStatus {
        guard let first = rows.first else {
            return .waiting
        }
        if first.hasPrefix("Live evidence ready")
            || first.hasPrefix("Apply preview ready")
            || first.hasPrefix("Fill guide ready")
            || first.hasPrefix("Resource handoff ready")
        {
            return .ready
        }
        let text = rows.joined(separator: " ").lowercased()
        if text.contains("has not loaded") || text.contains("waiting") {
            return .waiting
        }
        if text.contains("blocked")
            || text.contains("failed")
            || text.contains("missing")
            || text.contains("partial")
            || text.contains("consent")
            || text.contains("required")
        {
            return .needsAttention
        }
        return .needsAttention
    }

    private static func providerHandoffDetail(statusRows: [String], combinedRows: [String]) -> String {
        guard let first = statusRows.first else {
            return "Provider handoff evidence has not loaded."
        }
        if statusRows.count == 1 || providerHandoffStatus(statusRows) == .ready {
            return sanitize(first)
        }
        let candidates = combinedRows.filter { $0 != first }
        if let inputAction = candidates.first(where: providerHandoffInputActionRow) {
            return sanitize([first, providerHandoffActionDetail(inputAction)].joined(separator: " "))
        }
        if let actionable = candidates.first(where: providerHandoffActionableRow) {
            return sanitize([first, actionable].joined(separator: " "))
        }
        return sanitize(statusRows.prefix(2).joined(separator: " "))
    }

    private static func providerHandoffInputActionRow(_ row: String) -> Bool {
        let text = row.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        if text.hasPrefix("freshness:") || text.hasPrefix("source freshness:") {
            return false
        }
        return text.contains("provide ")
            || text.contains("fill ")
            || text.contains("meshy_api_key")
            || text.contains("openai_api_key")
            || text.contains("final-resources.env")
    }

    private static func providerHandoffActionableRow(_ row: String) -> Bool {
        let text = row.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        if text.hasPrefix("freshness:") || text.hasPrefix("source freshness:") {
            return false
        }
        return text.contains("provide ")
            || text.contains("fill ")
            || text.contains("make ")
            || text.contains("run ")
            || text.contains("consent")
            || text.contains("missing")
            || text.contains("blocked")
            || text.contains("required")
    }

    private static func providerHandoffActionDetail(_ row: String) -> String {
        let trimmed = row.trimmingCharacters(in: .whitespacesAndNewlines)
        let lowered = trimmed.lowercased()
        if lowered.contains("provide ") || lowered.contains("fill ") {
            return trimmed
        }
        if lowered.contains("meshy_api_key") {
            return "provide MESHY_API_KEY in final-resources.env"
        }
        if lowered.contains("openai_api_key") {
            return "provide OPENAI_API_KEY in final-resources.env"
        }
        return trimmed
    }

    private static func localSmokeStage(_ summary: FinalLaunchMobileSummary) -> FinalShowcaseSummaryStage {
        stage(
            "local_smoke",
            "Local Smoke",
            launchRowStatus(
                summary.localShowcaseSmokeRows,
                readyPrefix: "Local showcase smoke ready:",
                waitingNeedle: "local showcase smoke has not loaded"
            ),
            localSmokeDetail(summary.localShowcaseSmokeRows)
        )
    }

    private static func localSmokeDetail(_ rows: [String]) -> String {
        guard let first = rows.first else {
            return "Local showcase smoke has not loaded."
        }
        if first.hasPrefix("Local showcase smoke ready:") || rows.count == 1 {
            return sanitize(first)
        }
        return sanitize(rows.prefix(2).joined(separator: " "))
    }

    private static func iosDeployStage(_ summary: FinalLaunchMobileSummary) -> FinalShowcaseSummaryStage {
        let rows = iosDeployRows(summary)
        return stage(
            "ios_deploy",
            "iOS Deploy",
            iosDeployStatus(rows),
            iosDeployDetail(rows)
        )
    }

    private static func iosDeployRows(_ summary: FinalLaunchMobileSummary) -> [String] {
        if !summary.launchRehearsalRows.isEmpty {
            return summary.launchRehearsalRows
        }
        return summary.deployRunbookRows
    }

    private static func iosDeployStatus(_ rows: [String]) -> FinalShowcaseStageStatus {
        guard let first = rows.first else {
            return .waiting
        }
        if first.hasPrefix("iOS launch rehearsal ready:")
            || first.hasPrefix("iOS deploy runbook ready.")
        {
            return .ready
        }
        let text = rows.joined(separator: " ").lowercased()
        if text.contains("has not loaded")
            || text.contains("run ios device launch rehearsal")
            || text.contains("waiting")
        {
            return .waiting
        }
        if text.contains("blocked")
            || text.contains("failed")
            || text.contains("missing")
            || text.contains("stale")
            || text.contains("partial")
        {
            return .needsAttention
        }
        return .needsAttention
    }

    private static func iosDeployDetail(_ rows: [String]) -> String {
        guard let first = rows.first else {
            return "iOS deploy evidence has not loaded."
        }
        if rows.count == 1 || iosDeployStatus(rows) == .ready {
            return sanitize(first)
        }
        if let actionable = rows.dropFirst().first(where: iosDeployActionableRow) {
            return sanitize([first, actionable].joined(separator: " "))
        }
        return sanitize(rows.prefix(2).joined(separator: " "))
    }

    private static func iosDeployActionableRow(_ row: String) -> Bool {
        let text = row.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        if text.hasPrefix("freshness:") || text.hasPrefix("source freshness:") {
            return false
        }
        return text.contains("blocked")
            || text.contains("failed")
            || text.contains("missing")
            || text.contains("make ")
            || text.contains("run ")
    }

    private static func threeDEvaluationStage(_ summary: FinalLaunchMobileSummary) -> FinalShowcaseSummaryStage {
        stage(
            "three_d_evaluation",
            "3D Evaluation",
            launchRowStatus(
                summary.threeDEvaluationRows,
                readyPrefix: "3D evaluation ready:",
                waitingNeedle: "3d evaluation readiness has not loaded"
            ),
            launchDetail(summary.threeDEvaluationRows, fallback: "3D evaluation readiness has not loaded.")
        )
    }

    private static func npcEvaluationStage(_ summary: FinalLaunchMobileSummary) -> FinalShowcaseSummaryStage {
        stage(
            "npc_evaluation",
            "NPC Eval",
            launchRowStatus(
                summary.npcEvaluationRows,
                readyPrefix: "NPC Agent evaluation ready:",
                waitingNeedle: "evaluation readiness has not loaded"
            ),
            launchDetail(summary.npcEvaluationRows, fallback: "NPC Agent evaluation readiness has not loaded.")
        )
    }

    private static func operatorHandoffStage(_ summary: FinalLaunchMobileSummary) -> FinalShowcaseSummaryStage {
        stage(
            "operator_handoff",
            "Handoff",
            launchRowStatus(
                summary.handoffRows,
                readyPrefix: "Final operator handoff ready.",
                waitingNeedle: "handoff has not loaded"
            ),
            launchDetail(summary.handoffRows, fallback: "Final operator handoff has not loaded.")
        )
    }

    private static func finalLaunchStage(_ summary: FinalLaunchMobileSummary) -> FinalShowcaseSummaryStage {
        let status: FinalShowcaseStageStatus
        switch summary.overallStatus {
        case .ready:
            status = .ready
        case .blocked:
            status = .needsAttention
        case .waiting:
            status = .waiting
        }
        let detail = summary.phaseRows.first { $0.status != .ready }?.detail
            ?? summary.acceptanceRows.first
            ?? summary.handoffRows.first
            ?? summary.subtitle
        return stage("final_launch", "Launch", status, "\(summary.title): \(detail)")
    }

    private static func launchRowStatus(
        _ rows: [String],
        readyPrefix: String,
        waitingNeedle: String
    ) -> FinalShowcaseStageStatus {
        guard !rows.isEmpty else {
            return .waiting
        }
        if rows.first?.hasPrefix(readyPrefix) == true {
            return .ready
        }
        let text = rows.joined(separator: " ").lowercased()
        if text.contains(waitingNeedle)
            || text.contains("has not loaded")
            || text.contains("run local")
        {
            return .waiting
        }
        if text.contains("blocked")
            || text.contains("failed")
            || text.contains("missing")
            || text.contains("stale")
            || text.contains("npc_agent_evaluation_failed")
        {
            return .needsAttention
        }
        return .needsAttention
    }

    private static func launchDetail(_ rows: [String], fallback: String) -> String {
        rows.first.map(sanitize) ?? fallback
    }

    private static func captureStage(_ selection: CaptureMediaSelection?) -> FinalShowcaseSummaryStage {
        guard let selection else {
            return stage("capture", "Capture", .waiting, "Choose a photo, guided scan, upload, or scan asset.")
        }
        if selection.isReadyForUpload {
            return stage("capture", "Capture", .ready, selection.summary.title)
        }
        return stage("capture", "Capture", .waiting, selection.summary.detail)
    }

    private static func threeDStage(_ session: MythSession?) -> FinalShowcaseSummaryStage {
        guard let session else {
            return stage("three_d", "3D Asset", .waiting, "Forge a myth session to create the game asset.")
        }
        let asset = session.generatedAsset
        guard !asset.uri.isEmpty, !asset.format.isEmpty else {
            return stage("three_d", "3D Asset", .needsAttention, "Generated asset metadata is incomplete.")
        }
        let inputMode = asset.generationProvenance?.inputMode ?? "prompt"
        return stage("three_d", "3D Asset", .ready, "\(asset.provider) \(asset.format) via \(inputMode)")
    }

    private static func npcStage(
        session: MythSession?,
        npcTickHistoryCount: Int
    ) -> FinalShowcaseSummaryStage {
        guard let session else {
            return stage("npc_agent", "NPC Agent", .waiting, "NPC agents start after the artifact exists.")
        }
        let hasNPCOutput = !session.npcAgentTraces.isEmpty || session.npcReactions.count >= 3
        guard hasNPCOutput else {
            return stage("npc_agent", "NPC Agent", .needsAttention, "No NPC agent output returned.")
        }
        let tickText = npcTickHistoryCount == 1 ? "1 saved tick" : "\(npcTickHistoryCount) saved ticks"
        let runtime = session.npcAgentRuntime.isEmpty ? session.npcDirector : session.npcAgentRuntime
        return stage("npc_agent", "NPC Agent", .ready, "\(runtime), \(tickText)")
    }

    private static func printStage(session: MythSession?, printQuote: PrintQuote?) -> FinalShowcaseSummaryStage {
        guard session != nil else {
            return stage("print", "Print", .waiting, "Print candidate appears after the myth session.")
        }
        if let printQuote {
            let dollars = Double(printQuote.estimatedPriceCents) / 100.0
            return stage(
                "print",
                "Print",
                .ready,
                "\(printQuote.currency) \(String(format: "%.2f", dollars)) \(printQuote.status)"
            )
        }
        return stage("print", "Print", .optional, "Print candidate ready; quote not requested yet.")
    }

    private static func resourcesStage(
        readiness: ProviderReadinessResponse?,
        error: String?
    ) -> FinalShowcaseSummaryStage {
        if let error {
            return stage("resources", "Resources", .needsAttention, sanitize(error))
        }
        guard let readiness else {
            return stage("resources", "Resources", .waiting, "Backend readiness has not loaded.")
        }
        if readiness.overallDemoReady {
            let mode = readiness.overallRealReady ? "real providers ready" : "local demo providers ready"
            return stage("resources", "Resources", .ready, mode)
        }
        let missing = readiness.providers.flatMap(\.missingEnv).joined(separator: ", ")
        return stage(
            "resources",
            "Resources",
            .needsAttention,
            missing.isEmpty ? "Provider setup needed." : "Missing \(missing)"
        )
    }

    private static func overallStatus(
        session: MythSession?,
        stages: [FinalShowcaseSummaryStage]
    ) -> FinalShowcaseSummaryStatus {
        guard session != nil else {
            return .waiting
        }
        if stages.contains(where: { $0.status == .needsAttention }) {
            return .needsAttention
        }
        let requiredReady = ["capture", "three_d", "npc_agent", "resources"].allSatisfy { id in
            stages.first(where: { $0.id == id })?.status == .ready
        }
        let launchStageIDs = Set([
            "provider_handoff", "local_smoke", "ios_deploy", "three_d_evaluation",
            "npc_evaluation", "operator_handoff", "final_launch",
        ])
        let launchStages = stages.filter { launchStageIDs.contains($0.id) }
        let launchReady = launchStages.allSatisfy { $0.status == .ready }
        return requiredReady && launchReady ? .readyForLocalDemo : .waiting
    }

    private static func stage(
        _ id: String,
        _ label: String,
        _ status: FinalShowcaseStageStatus,
        _ detail: String
    ) -> FinalShowcaseSummaryStage {
        FinalShowcaseSummaryStage(id: id, label: label, status: status, detail: sanitize(detail))
    }

    private static func sanitize(_ value: String) -> String {
        var sanitized = value
        let patterns = [
            #"sk-[A-Za-z0-9._-]+"#,
            #"Bearer\s+[A-Za-z0-9._~+/\-=:-]+"#,
            #"Authorization"#,
            #"Bearer"#,
            #"api[_-]?key\s*[=:]\s*[^\s,;"']+"#,
            #"(private_message|raw_context|message_body)\s*:\s*[^\n]+"#,
            #"data:[A-Za-z0-9.+-]+/[A-Za-z0-9.+-]+;base64,[A-Za-z0-9+/=_-]+"#,
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
