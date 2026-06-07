import Foundation

public enum JSONValue: Codable, Equatable, Sendable {
    case string(String)
    case int(Int)
    case double(Double)
    case bool(Bool)
    case null

    public init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        if container.decodeNil() {
            self = .null
        } else if let value = try? container.decode(Bool.self) {
            self = .bool(value)
        } else if let value = try? container.decode(Int.self) {
            self = .int(value)
        } else if let value = try? container.decode(Double.self) {
            self = .double(value)
        } else {
            self = .string(try container.decode(String.self))
        }
    }

    public func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        switch self {
        case let .string(value):
            try container.encode(value)
        case let .int(value):
            try container.encode(value)
        case let .double(value):
            try container.encode(value)
        case let .bool(value):
            try container.encode(value)
        case .null:
            try container.encodeNil()
        }
    }
}

public enum FinalLaunchMode: String, Codable, CaseIterable, Identifiable, Sendable {
    case local
    case configured

    public var id: String {
        rawValue
    }

    public var displayLabel: String {
        switch self {
        case .local:
            return "Local"
        case .configured:
            return "Configured"
        }
    }

    public static func safe(rawValue: String?) -> FinalLaunchMode {
        guard let rawValue else {
            return .local
        }
        let normalized = rawValue.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        return FinalLaunchMode(rawValue: normalized) ?? .local
    }
}

public struct ObjectObservation: Codable, Equatable, Sendable {
    public var label: String
    public var materials: [String]
    public var source: String
    public var visualNotes: String?

    public init(label: String, materials: [String] = [], source: String, visualNotes: String? = nil) {
        self.label = label
        self.materials = materials
        self.source = source
        self.visualNotes = visualNotes
    }
}

public struct ContextCapsule: Codable, Equatable, Sendable {
    public var currentTheme: String
    public var desiredTone: String
    public var recentMilestone: String?

    public init(currentTheme: String, desiredTone: String, recentMilestone: String? = nil) {
        self.currentTheme = currentTheme
        self.desiredTone = desiredTone
        self.recentMilestone = recentMilestone
    }
}

public struct ObjectCaptureMetadata: Codable, Equatable, Sendable {
    public var label: String
    public var materials: [String]
    public var source: String
    public var captureMode: String
    public var visualNotes: String?

    public init(
        label: String,
        materials: [String] = [],
        source: String,
        captureMode: String,
        visualNotes: String? = nil
    ) {
        self.label = label
        self.materials = materials
        self.source = source
        self.captureMode = captureMode
        self.visualNotes = visualNotes
    }
}

public struct CaptureMediaItem: Codable, Equatable, Sendable {
    public var mediaId: String
    public var role: String
    public var contentType: String
    public var byteSize: Int
    public var uri: String
    public var moderationStatus: String

    public init(
        mediaId: String,
        role: String,
        contentType: String,
        byteSize: Int,
        uri: String,
        moderationStatus: String
    ) {
        self.mediaId = mediaId
        self.role = role
        self.contentType = contentType
        self.byteSize = byteSize
        self.uri = uri
        self.moderationStatus = moderationStatus
    }
}

public struct ObjectCapture: Codable, Equatable, Sendable {
    public var captureId: String
    public var status: String
    public var source: String
    public var captureMode: String
    public var objectObservation: ObjectObservation
    public var mediaItems: [CaptureMediaItem]
    public var createdAt: String

    public init(
        captureId: String,
        status: String,
        source: String,
        captureMode: String,
        objectObservation: ObjectObservation,
        mediaItems: [CaptureMediaItem],
        createdAt: String
    ) {
        self.captureId = captureId
        self.status = status
        self.source = source
        self.captureMode = captureMode
        self.objectObservation = objectObservation
        self.mediaItems = mediaItems
        self.createdAt = createdAt
    }
}

public struct ObjectCard: Codable, Equatable, Sendable {
    public var label: String
    public var materials: [String]
    public var source: String
    public var affordances: [String]
    public var symbolicReading: String

    public init(
        label: String,
        materials: [String],
        source: String,
        affordances: [String],
        symbolicReading: String
    ) {
        self.label = label
        self.materials = materials
        self.source = source
        self.affordances = affordances
        self.symbolicReading = symbolicReading
    }
}

public struct MythSeed: Codable, Equatable, Sendable {
    public var title: String
    public var personalResonance: String
    public var generationPrompt: String

    public init(title: String, personalResonance: String, generationPrompt: String) {
        self.title = title
        self.personalResonance = personalResonance
        self.generationPrompt = generationPrompt
    }
}

public struct GeneratedAssetVariant: Codable, Equatable, Sendable {
    public var role: String
    public var format: String
    public var uri: String
    public var isSceneLoadable: Bool

    public init(
        role: String,
        format: String,
        uri: String,
        isSceneLoadable: Bool
    ) {
        self.role = role
        self.format = format
        self.uri = uri
        self.isSceneLoadable = isSceneLoadable
    }
}

public struct GeneratedAssetProvenance: Codable, Equatable, Sendable {
    public var inputMode: String
    public var providerRoute: String?
    public var sourceImageCount: Int
    public var selectedSourceImageCount: Int
    public var sourceAssetCount: Int
    public var maxSourceImages: Int?
    public var selectionReason: String
    public var rawSourcesIncluded: Bool

    public init(
        inputMode: String,
        providerRoute: String?,
        sourceImageCount: Int,
        selectedSourceImageCount: Int,
        sourceAssetCount: Int,
        maxSourceImages: Int?,
        selectionReason: String,
        rawSourcesIncluded: Bool
    ) {
        self.inputMode = inputMode
        self.providerRoute = providerRoute
        self.sourceImageCount = sourceImageCount
        self.selectedSourceImageCount = selectedSourceImageCount
        self.sourceAssetCount = sourceAssetCount
        self.maxSourceImages = maxSourceImages
        self.selectionReason = selectionReason
        self.rawSourcesIncluded = rawSourcesIncluded
    }
}

public struct GeneratedAsset: Codable, Equatable, Sendable {
    public var kind: String
    public var provider: String
    public var format: String
    public var uri: String
    public var prompt: String
    public var moderationStatus: String
    public var variants: [GeneratedAssetVariant]
    public var generationProvenance: GeneratedAssetProvenance?

    private enum CodingKeys: String, CodingKey {
        case kind
        case provider
        case format
        case uri
        case prompt
        case moderationStatus
        case variants
        case generationProvenance
    }

    public init(
        kind: String,
        provider: String,
        format: String,
        uri: String,
        prompt: String,
        moderationStatus: String,
        variants: [GeneratedAssetVariant] = [],
        generationProvenance: GeneratedAssetProvenance? = nil
    ) {
        self.kind = kind
        self.provider = provider
        self.format = format
        self.uri = uri
        self.prompt = prompt
        self.moderationStatus = moderationStatus
        self.variants = variants
        self.generationProvenance = generationProvenance
    }

    public init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.kind = try container.decode(String.self, forKey: .kind)
        self.provider = try container.decode(String.self, forKey: .provider)
        self.format = try container.decode(String.self, forKey: .format)
        self.uri = try container.decode(String.self, forKey: .uri)
        self.prompt = try container.decode(String.self, forKey: .prompt)
        self.moderationStatus = try container.decode(String.self, forKey: .moderationStatus)
        self.variants = try container.decodeIfPresent([GeneratedAssetVariant].self, forKey: .variants) ?? []
        self.generationProvenance = try container.decodeIfPresent(
            GeneratedAssetProvenance.self,
            forKey: .generationProvenance
        )
    }

    public func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(kind, forKey: .kind)
        try container.encode(provider, forKey: .provider)
        try container.encode(format, forKey: .format)
        try container.encode(uri, forKey: .uri)
        try container.encode(prompt, forKey: .prompt)
        try container.encode(moderationStatus, forKey: .moderationStatus)
        try container.encode(variants, forKey: .variants)
        try container.encodeIfPresent(generationProvenance, forKey: .generationProvenance)
    }
}

public struct NPCReaction: Codable, Equatable, Sendable {
    public var npcId: String
    public var name: String
    public var emotion: String
    public var interpretation: String
    public var plan: [String]
    public var worldChange: String

    public init(
        npcId: String,
        name: String,
        emotion: String,
        interpretation: String,
        plan: [String],
        worldChange: String
    ) {
        self.npcId = npcId
        self.name = name
        self.emotion = emotion
        self.interpretation = interpretation
        self.plan = plan
        self.worldChange = worldChange
    }
}

public struct NPCAgentTrace: Codable, Equatable, Sendable {
    public var npcId: String
    public var name: String
    public var belief: String
    public var intention: String
    public var proposedAction: String
    public var rationale: String
    public var confidence: Double

    public init(
        npcId: String,
        name: String,
        belief: String,
        intention: String,
        proposedAction: String,
        rationale: String,
        confidence: Double
    ) {
        self.npcId = npcId
        self.name = name
        self.belief = belief
        self.intention = intention
        self.proposedAction = proposedAction
        self.rationale = rationale
        self.confidence = confidence
    }
}

public struct ResolvedNPCAction: Codable, Equatable, Sendable {
    public var npcId: String
    public var action: String
    public var status: String
    public var reason: String

    public init(npcId: String, action: String, status: String, reason: String) {
        self.npcId = npcId
        self.action = action
        self.status = status
        self.reason = reason
    }
}

public struct WorldResolution: Codable, Equatable, Sendable {
    public var arbitrator: String
    public var summary: String
    public var acceptedActions: [ResolvedNPCAction]
    public var rejectedActions: [ResolvedNPCAction]
    public var worldStateDelta: [String: JSONValue]
    public var visibleChanges: [String]

    public init(
        arbitrator: String,
        summary: String,
        acceptedActions: [ResolvedNPCAction],
        rejectedActions: [ResolvedNPCAction],
        worldStateDelta: [String: JSONValue],
        visibleChanges: [String]
    ) {
        self.arbitrator = arbitrator
        self.summary = summary
        self.acceptedActions = acceptedActions
        self.rejectedActions = rejectedActions
        self.worldStateDelta = worldStateDelta
        self.visibleChanges = visibleChanges
    }
}

public struct PrintCandidate: Codable, Equatable, Sendable {
    public var kind: String
    public var sourceAssetUri: String
    public var provider: String
    public var format: String
    public var uri: String
    public var requiresUserApproval: Bool
    public var approvalReason: String
    public var printabilityNotes: [String]

    public init(
        kind: String,
        sourceAssetUri: String,
        provider: String,
        format: String,
        uri: String,
        requiresUserApproval: Bool,
        approvalReason: String,
        printabilityNotes: [String]
    ) {
        self.kind = kind
        self.sourceAssetUri = sourceAssetUri
        self.provider = provider
        self.format = format
        self.uri = uri
        self.requiresUserApproval = requiresUserApproval
        self.approvalReason = approvalReason
        self.printabilityNotes = printabilityNotes
    }
}

public struct PrintQuoteRequest: Codable, Equatable, Sendable {
    public var printCandidate: PrintCandidate
    public var quantity: Int
    public var material: String
    public var finish: String
    public var shipToCountry: String

    public init(
        printCandidate: PrintCandidate,
        quantity: Int = 1,
        material: String = "standard_resin",
        finish: String = "matte",
        shipToCountry: String = "US"
    ) {
        self.printCandidate = printCandidate
        self.quantity = quantity
        self.material = material
        self.finish = finish
        self.shipToCountry = shipToCountry
    }
}

public struct PrintQuote: Codable, Equatable, Sendable {
    public var kind: String
    public var provider: String
    public var status: String
    public var sourceAssetUri: String
    public var printCandidateUri: String
    public var currency: String
    public var estimatedPriceCents: Int
    public var estimatedProductionDays: Int
    public var estimatedShippingDays: Int
    public var checkoutUrl: String?
    public var requiresUserApproval: Bool
    public var approvalReason: String
    public var quoteNotes: [String]

    public init(
        kind: String,
        provider: String,
        status: String,
        sourceAssetUri: String,
        printCandidateUri: String,
        currency: String,
        estimatedPriceCents: Int,
        estimatedProductionDays: Int,
        estimatedShippingDays: Int,
        checkoutUrl: String? = nil,
        requiresUserApproval: Bool,
        approvalReason: String,
        quoteNotes: [String]
    ) {
        self.kind = kind
        self.provider = provider
        self.status = status
        self.sourceAssetUri = sourceAssetUri
        self.printCandidateUri = printCandidateUri
        self.currency = currency
        self.estimatedPriceCents = estimatedPriceCents
        self.estimatedProductionDays = estimatedProductionDays
        self.estimatedShippingDays = estimatedShippingDays
        self.checkoutUrl = checkoutUrl
        self.requiresUserApproval = requiresUserApproval
        self.approvalReason = approvalReason
        self.quoteNotes = quoteNotes
    }
}

public struct ProviderReadinessItem: Codable, Equatable, Sendable {
    public var kind: String
    public var selectedProvider: String
    public var status: String
    public var isDemoReady: Bool
    public var isRealProviderReady: Bool
    public var missingEnv: [String]
    public var capabilities: [String]
    public var notes: [String]

    public init(
        kind: String,
        selectedProvider: String,
        status: String,
        isDemoReady: Bool,
        isRealProviderReady: Bool,
        missingEnv: [String] = [],
        capabilities: [String] = [],
        notes: [String] = []
    ) {
        self.kind = kind
        self.selectedProvider = selectedProvider
        self.status = status
        self.isDemoReady = isDemoReady
        self.isRealProviderReady = isRealProviderReady
        self.missingEnv = missingEnv
        self.capabilities = capabilities
        self.notes = notes
    }
}

public struct ProviderReadinessResponse: Codable, Equatable, Sendable {
    public var overallDemoReady: Bool
    public var overallRealReady: Bool
    public var providers: [ProviderReadinessItem]

    public init(
        overallDemoReady: Bool,
        overallRealReady: Bool,
        providers: [ProviderReadinessItem]
    ) {
        self.overallDemoReady = overallDemoReady
        self.overallRealReady = overallRealReady
        self.providers = providers
    }
}

public struct FinalDemoLaunchSummary: Codable, Equatable, Sendable {
    public var ready: Int
    public var missing: Int
    public var blocked: Int
    public var manual: Int
    public var optional: Int
    public var partial: Int

    public init(
        ready: Int,
        missing: Int,
        blocked: Int,
        manual: Int,
        optional: Int,
        partial: Int = 0
    ) {
        self.ready = ready
        self.missing = missing
        self.blocked = blocked
        self.manual = manual
        self.optional = optional
        self.partial = partial
    }
}

public struct FinalDemoLaunchPhase: Codable, Equatable, Sendable {
    public var id: String
    public var label: String
    public var status: String
    public var requiredFor: String
    public var command: String
    public var notes: [String]

    public init(
        id: String,
        label: String,
        status: String,
        requiredFor: String,
        command: String,
        notes: [String] = []
    ) {
        self.id = id
        self.label = label
        self.status = status
        self.requiredFor = requiredFor
        self.command = command
        self.notes = notes
    }
}

public struct FinalDemoLaunchLiveCallPolicy: Codable, Equatable, Sendable {
    public var liveCallsByDefault: Bool
    public var configuredAcceptanceRequiresConsent: Bool
    public var consentFlag: String

    public init(
        liveCallsByDefault: Bool,
        configuredAcceptanceRequiresConsent: Bool,
        consentFlag: String
    ) {
        self.liveCallsByDefault = liveCallsByDefault
        self.configuredAcceptanceRequiresConsent = configuredAcceptanceRequiresConsent
        self.consentFlag = consentFlag
    }
}

public struct FinalDemoLaunchSafety: Codable, Equatable, Sendable {
    public var providerSecretsInReport: Bool
    public var localPathsInReport: Bool
    public var paymentLinksInReport: Bool
    public var globalMutation: Bool
    public var liveProviderCallsByDefault: Bool

    public init(
        providerSecretsInReport: Bool,
        localPathsInReport: Bool,
        paymentLinksInReport: Bool,
        globalMutation: Bool,
        liveProviderCallsByDefault: Bool
    ) {
        self.providerSecretsInReport = providerSecretsInReport
        self.localPathsInReport = localPathsInReport
        self.paymentLinksInReport = paymentLinksInReport
        self.globalMutation = globalMutation
        self.liveProviderCallsByDefault = liveProviderCallsByDefault
    }
}

public struct FinalResourcesFileStatus: Codable, Equatable, Sendable {
    public var path: String
    public var exists: Bool

    public init(path: String, exists: Bool) {
        self.path = path
        self.exists = exists
    }
}

public struct FinalResourcesPreflightSummary: Codable, Equatable, Sendable {
    public var ready: Int
    public var missing: Int
    public var blocked: Int
    public var optional: Int

    public init(ready: Int, missing: Int, blocked: Int, optional: Int) {
        self.ready = ready
        self.missing = missing
        self.blocked = blocked
        self.optional = optional
    }
}

public struct FinalResourcesPreflightItem: Codable, Equatable, Sendable {
    public var id: String
    public var status: String
    public var required: Bool
    public var configured: Bool
    public var redacted: Bool
    public var classification: String?
    public var normalizedValue: String?

    public init(
        id: String,
        status: String,
        required: Bool,
        configured: Bool,
        redacted: Bool,
        classification: String? = nil,
        normalizedValue: String? = nil
    ) {
        self.id = id
        self.status = status
        self.required = required
        self.configured = configured
        self.redacted = redacted
        self.classification = classification
        self.normalizedValue = normalizedValue
    }
}

public struct FinalResourcesPreflightReport: Codable, Equatable, Sendable {
    public var kind: String
    public var status: String
    public var resourcesFile: FinalResourcesFileStatus
    public var summary: FinalResourcesPreflightSummary
    public var items: [FinalResourcesPreflightItem]
    public var operatorActions: [String]

    public init(
        kind: String,
        status: String,
        resourcesFile: FinalResourcesFileStatus,
        summary: FinalResourcesPreflightSummary,
        items: [FinalResourcesPreflightItem] = [],
        operatorActions: [String] = []
    ) {
        self.kind = kind
        self.status = status
        self.resourcesFile = resourcesFile
        self.summary = summary
        self.items = items
        self.operatorActions = operatorActions
    }
}

public struct FinalAcceptanceSourceFile: Codable, Equatable, Sendable {
    public var path: String
    public var exists: Bool

    public init(path: String, exists: Bool) {
        self.path = path
        self.exists = exists
    }
}

public struct FinalAcceptanceReadinessSummary: Codable, Equatable, Sendable {
    public var passed: Int
    public var blocked: Int
    public var failed: Int
    public var skipped: Int

    public init(passed: Int, blocked: Int, failed: Int, skipped: Int) {
        self.passed = passed
        self.blocked = blocked
        self.failed = failed
        self.skipped = skipped
    }
}

public struct FinalAcceptanceBlocker: Codable, Equatable, Sendable {
    public var id: String
    public var label: String
    public var status: String
    public var classification: String
    public var command: String
    public var detail: String

    public init(
        id: String,
        label: String,
        status: String,
        classification: String,
        command: String,
        detail: String
    ) {
        self.id = id
        self.label = label
        self.status = status
        self.classification = classification
        self.command = command
        self.detail = detail
    }
}

public struct FinalAcceptanceReadinessSafety: Codable, Equatable, Sendable {
    public var commandsRun: Bool
    public var providerCalls: Bool
    public var globalMutation: Bool
    public var providerSecretsInReport: Bool
    public var rawMediaInReport: Bool
    public var paymentLinksInReport: Bool
    public var localPathsInReport: Bool

    public init(
        commandsRun: Bool,
        providerCalls: Bool,
        globalMutation: Bool,
        providerSecretsInReport: Bool,
        rawMediaInReport: Bool,
        paymentLinksInReport: Bool,
        localPathsInReport: Bool
    ) {
        self.commandsRun = commandsRun
        self.providerCalls = providerCalls
        self.globalMutation = globalMutation
        self.providerSecretsInReport = providerSecretsInReport
        self.rawMediaInReport = rawMediaInReport
        self.paymentLinksInReport = paymentLinksInReport
        self.localPathsInReport = localPathsInReport
    }
}

public struct FinalAcceptanceFreshness: Codable, Equatable, Sendable {
    public var status: String
    public var classification: String
    public var checkedAgainst: String
    public var sourceModifiedAt: String?
    public var currentRevision: String?
    public var currentRevisionCommittedAt: String?

    public init(
        status: String,
        classification: String,
        checkedAgainst: String,
        sourceModifiedAt: String? = nil,
        currentRevision: String? = nil,
        currentRevisionCommittedAt: String? = nil
    ) {
        self.status = status
        self.classification = classification
        self.checkedAgainst = checkedAgainst
        self.sourceModifiedAt = sourceModifiedAt
        self.currentRevision = currentRevision
        self.currentRevisionCommittedAt = currentRevisionCommittedAt
    }
}

public struct FinalAcceptanceReadinessReport: Codable, Equatable, Sendable {
    public var kind: String
    public var status: String
    public var sourceFile: FinalAcceptanceSourceFile
    public var freshness: FinalAcceptanceFreshness?
    public var summary: FinalAcceptanceReadinessSummary
    public var blockers: [FinalAcceptanceBlocker]
    public var operatorActions: [String]
    public var safety: FinalAcceptanceReadinessSafety

    public init(
        kind: String,
        status: String,
        sourceFile: FinalAcceptanceSourceFile,
        freshness: FinalAcceptanceFreshness? = nil,
        summary: FinalAcceptanceReadinessSummary,
        blockers: [FinalAcceptanceBlocker],
        operatorActions: [String],
        safety: FinalAcceptanceReadinessSafety
    ) {
        self.kind = kind
        self.status = status
        self.sourceFile = sourceFile
        self.freshness = freshness
        self.summary = summary
        self.blockers = blockers
        self.operatorActions = operatorActions
        self.safety = safety
    }
}

public struct NPCAgentEvaluationReadinessSummary: Codable, Equatable, Sendable {
    public var totalCases: Int
    public var succeeded: Int
    public var failed: Int
    public var tickSteps: Int

    public init(totalCases: Int, succeeded: Int, failed: Int, tickSteps: Int) {
        self.totalCases = totalCases
        self.succeeded = succeeded
        self.failed = failed
        self.tickSteps = tickSteps
    }
}

public struct ThreeDEvaluationReadinessSummary: Codable, Equatable, Sendable {
    public var totalCases: Int
    public var succeeded: Int
    public var failed: Int

    public init(totalCases: Int, succeeded: Int, failed: Int) {
        self.totalCases = totalCases
        self.succeeded = succeeded
        self.failed = failed
    }
}

public struct ThreeDEvaluationReadinessInputModes: Codable, Equatable, Sendable {
    public var textPrompt: Int
    public var singleImage: Int
    public var multiImage: Int
    public var unknown: Int

    public init(textPrompt: Int, singleImage: Int, multiImage: Int, unknown: Int) {
        self.textPrompt = textPrompt
        self.singleImage = singleImage
        self.multiImage = multiImage
        self.unknown = unknown
    }
}

public struct ThreeDEvaluationReadinessCoverage: Codable, Equatable, Sendable {
    public var inputModes: ThreeDEvaluationReadinessInputModes
    public var variantRoles: [String: Int]
    public var sceneLoadableCases: Int

    public init(
        inputModes: ThreeDEvaluationReadinessInputModes,
        variantRoles: [String: Int],
        sceneLoadableCases: Int
    ) {
        self.inputModes = inputModes
        self.variantRoles = variantRoles
        self.sceneLoadableCases = sceneLoadableCases
    }
}

public struct ThreeDEvaluationReadinessBlocker: Codable, Equatable, Sendable {
    public var id: String
    public var label: String
    public var status: String
    public var classification: String
    public var command: String
    public var detail: String

    public init(
        id: String,
        label: String,
        status: String,
        classification: String,
        command: String,
        detail: String
    ) {
        self.id = id
        self.label = label
        self.status = status
        self.classification = classification
        self.command = command
        self.detail = detail
    }
}

public struct ThreeDEvaluationReadinessSafety: Codable, Equatable, Sendable {
    public var commandsRun: Bool
    public var providerCalls: Bool
    public var globalMutation: Bool
    public var providerSecretsInReport: Bool
    public var rawPrivateContextInReport: Bool
    public var rawMediaInReport: Bool
    public var localPathsInReport: Bool
    public var paymentLinksInReport: Bool

    public init(
        commandsRun: Bool,
        providerCalls: Bool,
        globalMutation: Bool,
        providerSecretsInReport: Bool,
        rawPrivateContextInReport: Bool,
        rawMediaInReport: Bool,
        localPathsInReport: Bool,
        paymentLinksInReport: Bool
    ) {
        self.commandsRun = commandsRun
        self.providerCalls = providerCalls
        self.globalMutation = globalMutation
        self.providerSecretsInReport = providerSecretsInReport
        self.rawPrivateContextInReport = rawPrivateContextInReport
        self.rawMediaInReport = rawMediaInReport
        self.localPathsInReport = localPathsInReport
        self.paymentLinksInReport = paymentLinksInReport
    }
}

public struct ThreeDEvaluationReadinessReport: Codable, Equatable, Sendable {
    public var kind: String
    public var status: String
    public var sourceFile: FinalAcceptanceSourceFile
    public var summary: ThreeDEvaluationReadinessSummary
    public var coverage: ThreeDEvaluationReadinessCoverage
    public var blockers: [ThreeDEvaluationReadinessBlocker]
    public var operatorActions: [String]
    public var safety: ThreeDEvaluationReadinessSafety

    public init(
        kind: String,
        status: String,
        sourceFile: FinalAcceptanceSourceFile,
        summary: ThreeDEvaluationReadinessSummary,
        coverage: ThreeDEvaluationReadinessCoverage,
        blockers: [ThreeDEvaluationReadinessBlocker],
        operatorActions: [String],
        safety: ThreeDEvaluationReadinessSafety
    ) {
        self.kind = kind
        self.status = status
        self.sourceFile = sourceFile
        self.summary = summary
        self.coverage = coverage
        self.blockers = blockers
        self.operatorActions = operatorActions
        self.safety = safety
    }
}

public struct VisualRegressionReadinessSummary: Codable, Equatable, Sendable {
    public var passed: Int
    public var failed: Int

    public init(passed: Int, failed: Int) {
        self.passed = passed
        self.failed = failed
    }
}

public struct VisualRegressionReadinessArtifact: Codable, Equatable, Sendable {
    public var id: String
    public var status: String
    public var htmlPath: String?
    public var pngPath: String?
    public var notesPath: String?

    public init(
        id: String,
        status: String,
        htmlPath: String? = nil,
        pngPath: String? = nil,
        notesPath: String? = nil
    ) {
        self.id = id
        self.status = status
        self.htmlPath = htmlPath
        self.pngPath = pngPath
        self.notesPath = notesPath
    }
}

public struct VisualRegressionReadinessSafety: Codable, Equatable, Sendable {
    public var commandsRun: Bool
    public var providerCalls: Bool
    public var liveProviderCalls: Bool
    public var globalMutation: Bool
    public var xcodeOrSigning: Bool
    public var keychainWrites: Bool
    public var providerSecretsInReport: Bool
    public var rawPrivateContextInReport: Bool
    public var rawMediaInReport: Bool
    public var paymentLinksInReport: Bool
    public var localPathsInReport: Bool

    public init(
        commandsRun: Bool,
        providerCalls: Bool,
        liveProviderCalls: Bool,
        globalMutation: Bool,
        xcodeOrSigning: Bool,
        keychainWrites: Bool,
        providerSecretsInReport: Bool,
        rawPrivateContextInReport: Bool,
        rawMediaInReport: Bool,
        paymentLinksInReport: Bool,
        localPathsInReport: Bool
    ) {
        self.commandsRun = commandsRun
        self.providerCalls = providerCalls
        self.liveProviderCalls = liveProviderCalls
        self.globalMutation = globalMutation
        self.xcodeOrSigning = xcodeOrSigning
        self.keychainWrites = keychainWrites
        self.providerSecretsInReport = providerSecretsInReport
        self.rawPrivateContextInReport = rawPrivateContextInReport
        self.rawMediaInReport = rawMediaInReport
        self.paymentLinksInReport = paymentLinksInReport
        self.localPathsInReport = localPathsInReport
    }
}

public struct VisualRegressionReadinessReport: Codable, Equatable, Sendable {
    public var kind: String
    public var status: String
    public var sourceFile: FinalAcceptanceSourceFile
    public var freshness: FinalAcceptanceFreshness?
    public var summary: VisualRegressionReadinessSummary
    public var artifacts: [VisualRegressionReadinessArtifact]
    public var blockers: [ThreeDEvaluationReadinessBlocker]
    public var operatorActions: [String]
    public var commands: [String]
    public var safety: VisualRegressionReadinessSafety

    public init(
        kind: String,
        status: String,
        sourceFile: FinalAcceptanceSourceFile,
        freshness: FinalAcceptanceFreshness? = nil,
        summary: VisualRegressionReadinessSummary,
        artifacts: [VisualRegressionReadinessArtifact],
        blockers: [ThreeDEvaluationReadinessBlocker] = [],
        operatorActions: [String],
        commands: [String],
        safety: VisualRegressionReadinessSafety
    ) {
        self.kind = kind
        self.status = status
        self.sourceFile = sourceFile
        self.freshness = freshness
        self.summary = summary
        self.artifacts = artifacts
        self.blockers = blockers
        self.operatorActions = operatorActions
        self.commands = commands
        self.safety = safety
    }
}

public struct NPCAgentEvaluationReadinessCoverage: Codable, Equatable, Sendable {
    public var expectedNpcSets: Int
    public var traceSets: Int
    public var proposedActionPlanMatches: Int
    public var tickStepsCompleted: Int
    public var worldResolutionSteps: Int

    public init(
        expectedNpcSets: Int,
        traceSets: Int,
        proposedActionPlanMatches: Int,
        tickStepsCompleted: Int,
        worldResolutionSteps: Int
    ) {
        self.expectedNpcSets = expectedNpcSets
        self.traceSets = traceSets
        self.proposedActionPlanMatches = proposedActionPlanMatches
        self.tickStepsCompleted = tickStepsCompleted
        self.worldResolutionSteps = worldResolutionSteps
    }
}

public struct NPCAgentEvaluationReadinessBlocker: Codable, Equatable, Sendable {
    public var id: String
    public var label: String
    public var status: String
    public var classification: String
    public var command: String
    public var detail: String

    public init(
        id: String,
        label: String,
        status: String,
        classification: String,
        command: String,
        detail: String
    ) {
        self.id = id
        self.label = label
        self.status = status
        self.classification = classification
        self.command = command
        self.detail = detail
    }
}

public struct NPCAgentEvaluationReadinessSafety: Codable, Equatable, Sendable {
    public var commandsRun: Bool
    public var providerCalls: Bool
    public var globalMutation: Bool
    public var providerSecretsInReport: Bool
    public var rawPrivateContextInReport: Bool
    public var rawMediaInReport: Bool
    public var localPathsInReport: Bool
    public var paymentLinksInReport: Bool

    public init(
        commandsRun: Bool,
        providerCalls: Bool,
        globalMutation: Bool,
        providerSecretsInReport: Bool,
        rawPrivateContextInReport: Bool,
        rawMediaInReport: Bool,
        localPathsInReport: Bool,
        paymentLinksInReport: Bool
    ) {
        self.commandsRun = commandsRun
        self.providerCalls = providerCalls
        self.globalMutation = globalMutation
        self.providerSecretsInReport = providerSecretsInReport
        self.rawPrivateContextInReport = rawPrivateContextInReport
        self.rawMediaInReport = rawMediaInReport
        self.localPathsInReport = localPathsInReport
        self.paymentLinksInReport = paymentLinksInReport
    }
}

public struct NPCAgentEvaluationReadinessReport: Codable, Equatable, Sendable {
    public var kind: String
    public var status: String
    public var sourceFile: FinalAcceptanceSourceFile
    public var summary: NPCAgentEvaluationReadinessSummary
    public var coverage: NPCAgentEvaluationReadinessCoverage
    public var blockers: [NPCAgentEvaluationReadinessBlocker]
    public var operatorActions: [String]
    public var safety: NPCAgentEvaluationReadinessSafety

    public init(
        kind: String,
        status: String,
        sourceFile: FinalAcceptanceSourceFile,
        summary: NPCAgentEvaluationReadinessSummary,
        coverage: NPCAgentEvaluationReadinessCoverage,
        blockers: [NPCAgentEvaluationReadinessBlocker],
        operatorActions: [String],
        safety: NPCAgentEvaluationReadinessSafety
    ) {
        self.kind = kind
        self.status = status
        self.sourceFile = sourceFile
        self.summary = summary
        self.coverage = coverage
        self.blockers = blockers
        self.operatorActions = operatorActions
        self.safety = safety
    }
}

public struct FinalOperatorHandoffSummary: Codable, Equatable, Sendable {
    public var ready: Int
    public var missing: Int
    public var blocked: Int
    public var manual: Int
    public var optional: Int
    public var partial: Int
    public var live: Int

    public init(
        ready: Int,
        missing: Int,
        blocked: Int,
        manual: Int,
        optional: Int,
        partial: Int = 0,
        live: Int = 0
    ) {
        self.ready = ready
        self.missing = missing
        self.blocked = blocked
        self.manual = manual
        self.optional = optional
        self.partial = partial
        self.live = live
    }
}

public struct FinalOperatorHandoffStep: Codable, Equatable, Sendable {
    public var id: String
    public var label: String
    public var status: String
    public var command: String
    public var requiredFor: String
    public var source: String
    public var notes: [String]
    public var requiresConsent: Bool

    public init(
        id: String,
        label: String,
        status: String,
        command: String,
        requiredFor: String,
        source: String,
        notes: [String] = [],
        requiresConsent: Bool = false
    ) {
        self.id = id
        self.label = label
        self.status = status
        self.command = command
        self.requiredFor = requiredFor
        self.source = source
        self.notes = notes
        self.requiresConsent = requiresConsent
    }
}

public struct FinalOperatorHandoffSafety: Codable, Equatable, Sendable {
    public var commandsRun: Bool
    public var providerCalls: Bool
    public var globalMutation: Bool
    public var providerSecretsInReport: Bool
    public var rawMediaInReport: Bool
    public var paymentLinksInReport: Bool
    public var localPathsInReport: Bool
    public var commandExecutionFromApp: Bool

    public init(
        commandsRun: Bool,
        providerCalls: Bool,
        globalMutation: Bool,
        providerSecretsInReport: Bool,
        rawMediaInReport: Bool,
        paymentLinksInReport: Bool,
        localPathsInReport: Bool,
        commandExecutionFromApp: Bool
    ) {
        self.commandsRun = commandsRun
        self.providerCalls = providerCalls
        self.globalMutation = globalMutation
        self.providerSecretsInReport = providerSecretsInReport
        self.rawMediaInReport = rawMediaInReport
        self.paymentLinksInReport = paymentLinksInReport
        self.localPathsInReport = localPathsInReport
        self.commandExecutionFromApp = commandExecutionFromApp
    }
}

public struct FinalOperatorHandoffReport: Codable, Equatable, Sendable {
    public var kind: String
    public var mode: String
    public var status: String
    public var summary: FinalOperatorHandoffSummary
    public var steps: [FinalOperatorHandoffStep]
    public var nextActions: [String]
    public var safety: FinalOperatorHandoffSafety

    public init(
        kind: String,
        mode: String,
        status: String,
        summary: FinalOperatorHandoffSummary,
        steps: [FinalOperatorHandoffStep],
        nextActions: [String],
        safety: FinalOperatorHandoffSafety
    ) {
        self.kind = kind
        self.mode = mode
        self.status = status
        self.summary = summary
        self.steps = steps
        self.nextActions = nextActions
        self.safety = safety
    }
}

public struct IOSDeployRunbookInputSlot: Codable, Equatable, Sendable {
    public var id: String
    public var label: String
    public var status: String
    public var required: Bool
    public var source: String
    public var operatorAction: String
    public var configured: Bool
    public var redacted: Bool
    public var classification: String?
    public var key: String?
    public var expectedMode: String?

    public init(
        id: String,
        label: String,
        status: String,
        required: Bool,
        source: String,
        operatorAction: String,
        configured: Bool,
        redacted: Bool,
        classification: String? = nil,
        key: String? = nil,
        expectedMode: String? = nil
    ) {
        self.id = id
        self.label = label
        self.status = status
        self.required = required
        self.source = source
        self.operatorAction = operatorAction
        self.configured = configured
        self.redacted = redacted
        self.classification = classification
        self.key = key
        self.expectedMode = expectedMode
    }
}

public struct IOSDeployRunbookCommandStep: Codable, Equatable, Sendable {
    public var id: String
    public var label: String
    public var status: String
    public var command: String
    public var notes: [String]
    public var requiresConsent: Bool

    public init(
        id: String,
        label: String,
        status: String,
        command: String,
        notes: [String] = [],
        requiresConsent: Bool = false
    ) {
        self.id = id
        self.label = label
        self.status = status
        self.command = command
        self.notes = notes
        self.requiresConsent = requiresConsent
    }
}

public struct IOSDeployRunbookSafety: Codable, Equatable, Sendable {
    public var commandsRun: Bool
    public var providerCalls: Bool
    public var globalMutation: Bool
    public var providerSecretsInReport: Bool
    public var rawMediaInReport: Bool
    public var paymentLinksInReport: Bool
    public var localPathsInReport: Bool

    public init(
        commandsRun: Bool,
        providerCalls: Bool,
        globalMutation: Bool,
        providerSecretsInReport: Bool,
        rawMediaInReport: Bool,
        paymentLinksInReport: Bool,
        localPathsInReport: Bool
    ) {
        self.commandsRun = commandsRun
        self.providerCalls = providerCalls
        self.globalMutation = globalMutation
        self.providerSecretsInReport = providerSecretsInReport
        self.rawMediaInReport = rawMediaInReport
        self.paymentLinksInReport = paymentLinksInReport
        self.localPathsInReport = localPathsInReport
    }
}

public struct IOSDeployRunbookReport: Codable, Equatable, Sendable {
    public var kind: String
    public var mode: String
    public var status: String
    public var inputSlots: [IOSDeployRunbookInputSlot]
    public var commandSequence: [IOSDeployRunbookCommandStep]
    public var operatorActions: [String]
    public var safety: IOSDeployRunbookSafety

    public init(
        kind: String,
        mode: String,
        status: String,
        inputSlots: [IOSDeployRunbookInputSlot],
        commandSequence: [IOSDeployRunbookCommandStep],
        operatorActions: [String],
        safety: IOSDeployRunbookSafety
    ) {
        self.kind = kind
        self.mode = mode
        self.status = status
        self.inputSlots = inputSlots
        self.commandSequence = commandSequence
        self.operatorActions = operatorActions
        self.safety = safety
    }
}

public struct IOSDeviceLaunchRehearsalReadinessSummary: Codable, Equatable, Sendable {
    public var ready: Int
    public var missing: Int
    public var blocked: Int
    public var partial: Int
    public var manual: Int
    public var live: Int

    public init(
        ready: Int,
        missing: Int,
        blocked: Int,
        partial: Int,
        manual: Int,
        live: Int
    ) {
        self.ready = ready
        self.missing = missing
        self.blocked = blocked
        self.partial = partial
        self.manual = manual
        self.live = live
    }
}

public struct IOSDeviceLaunchRehearsalSequenceRow: Codable, Equatable, Sendable {
    public var id: String
    public var label: String
    public var status: String
    public var command: String
    public var classification: String?
    public var freshnessStatus: String?
    public var freshnessClassification: String?
    public var freshnessSummary: [String: Int]?

    public init(
        id: String,
        label: String,
        status: String,
        command: String,
        classification: String? = nil,
        freshnessStatus: String? = nil,
        freshnessClassification: String? = nil,
        freshnessSummary: [String: Int]? = nil
    ) {
        self.id = id
        self.label = label
        self.status = status
        self.command = command
        self.classification = classification
        self.freshnessStatus = freshnessStatus
        self.freshnessClassification = freshnessClassification
        self.freshnessSummary = freshnessSummary
    }
}

public struct IOSDeviceLaunchRehearsalSafety: Codable, Equatable, Sendable {
    public var commandsRun: Bool
    public var providerCalls: Bool
    public var liveProviderCalls: Bool
    public var writesBackendEnv: Bool
    public var writesIosDeployConfig: Bool
    public var globalMutation: Bool
    public var xcodeOrSigning: Bool
    public var keychainWrites: Bool
    public var providerSecretsInReport: Bool
    public var rawMediaInReport: Bool
    public var paymentLinksInReport: Bool
    public var localPathsInReport: Bool

    public init(
        commandsRun: Bool,
        providerCalls: Bool,
        liveProviderCalls: Bool,
        writesBackendEnv: Bool,
        writesIosDeployConfig: Bool,
        globalMutation: Bool,
        xcodeOrSigning: Bool,
        keychainWrites: Bool,
        providerSecretsInReport: Bool,
        rawMediaInReport: Bool,
        paymentLinksInReport: Bool,
        localPathsInReport: Bool
    ) {
        self.commandsRun = commandsRun
        self.providerCalls = providerCalls
        self.liveProviderCalls = liveProviderCalls
        self.writesBackendEnv = writesBackendEnv
        self.writesIosDeployConfig = writesIosDeployConfig
        self.globalMutation = globalMutation
        self.xcodeOrSigning = xcodeOrSigning
        self.keychainWrites = keychainWrites
        self.providerSecretsInReport = providerSecretsInReport
        self.rawMediaInReport = rawMediaInReport
        self.paymentLinksInReport = paymentLinksInReport
        self.localPathsInReport = localPathsInReport
    }
}

public struct IOSDeviceLaunchRehearsalReadinessReport: Codable, Equatable, Sendable {
    public var kind: String
    public var status: String
    public var sourceFile: FinalAcceptanceSourceFile
    public var freshness: FinalAcceptanceFreshness?
    public var summary: IOSDeviceLaunchRehearsalReadinessSummary
    public var sequence: [IOSDeviceLaunchRehearsalSequenceRow]
    public var blockers: [ThreeDEvaluationReadinessBlocker]
    public var operatorActions: [String]
    public var commands: [String]
    public var safety: IOSDeviceLaunchRehearsalSafety

    public init(
        kind: String,
        status: String,
        sourceFile: FinalAcceptanceSourceFile,
        freshness: FinalAcceptanceFreshness? = nil,
        summary: IOSDeviceLaunchRehearsalReadinessSummary,
        sequence: [IOSDeviceLaunchRehearsalSequenceRow],
        blockers: [ThreeDEvaluationReadinessBlocker] = [],
        operatorActions: [String],
        commands: [String],
        safety: IOSDeviceLaunchRehearsalSafety
    ) {
        self.kind = kind
        self.status = status
        self.sourceFile = sourceFile
        self.freshness = freshness
        self.summary = summary
        self.sequence = sequence
        self.blockers = blockers
        self.operatorActions = operatorActions
        self.commands = commands
        self.safety = safety
    }
}

public struct ResourceHandoffSummary: Codable, Equatable, Sendable {
    public var ready: Int
    public var missing: Int
    public var blocked: Int
    public var manual: Int
    public var optional: Int

    public init(ready: Int, missing: Int, blocked: Int, manual: Int, optional: Int) {
        self.ready = ready
        self.missing = missing
        self.blocked = blocked
        self.manual = manual
        self.optional = optional
    }
}

public struct ResourceHandoffItem: Codable, Equatable, Sendable {
    public var id: String
    public var label: String
    public var destination: String
    public var requiredFor: String
    public var status: String
    public var configured: Bool
    public var missing: Bool
    public var notes: [String]

    public init(
        id: String,
        label: String,
        destination: String,
        requiredFor: String,
        status: String,
        configured: Bool,
        missing: Bool,
        notes: [String] = []
    ) {
        self.id = id
        self.label = label
        self.destination = destination
        self.requiredFor = requiredFor
        self.status = status
        self.configured = configured
        self.missing = missing
        self.notes = notes
    }
}

public struct ResourceHandoffSection: Codable, Equatable, Sendable {
    public var destination: String
    public var items: [ResourceHandoffItem]

    public init(destination: String, items: [ResourceHandoffItem]) {
        self.destination = destination
        self.items = items
    }
}

public struct ResourceHandoffSafety: Codable, Equatable, Sendable {
    public var providerSecretsInReport: Bool
    public var localPathsInReport: Bool
    public var paymentLinksInReport: Bool

    public init(
        providerSecretsInReport: Bool,
        localPathsInReport: Bool,
        paymentLinksInReport: Bool
    ) {
        self.providerSecretsInReport = providerSecretsInReport
        self.localPathsInReport = localPathsInReport
        self.paymentLinksInReport = paymentLinksInReport
    }
}

public struct ResourceHandoffReport: Codable, Equatable, Sendable {
    public var kind: String
    public var overallStatus: String
    public var summary: ResourceHandoffSummary
    public var backend: ResourceHandoffSection
    public var ios: ResourceHandoffSection
    public var operatorActions: [String]
    public var commands: [String]
    public var safety: ResourceHandoffSafety

    public init(
        kind: String,
        overallStatus: String,
        summary: ResourceHandoffSummary,
        backend: ResourceHandoffSection,
        ios: ResourceHandoffSection,
        operatorActions: [String],
        commands: [String],
        safety: ResourceHandoffSafety
    ) {
        self.kind = kind
        self.overallStatus = overallStatus
        self.summary = summary
        self.backend = backend
        self.ios = ios
        self.operatorActions = operatorActions
        self.commands = commands
        self.safety = safety
    }
}

public struct LiveProviderEvidenceSummary: Codable, Equatable, Sendable {
    public var ready: Int
    public var missing: Int
    public var blocked: Int
    public var partial: Int
    public var requiresLiveProviderConsent: Int

    public init(
        ready: Int,
        missing: Int,
        blocked: Int,
        partial: Int,
        requiresLiveProviderConsent: Int
    ) {
        self.ready = ready
        self.missing = missing
        self.blocked = blocked
        self.partial = partial
        self.requiresLiveProviderConsent = requiresLiveProviderConsent
    }
}

public struct LiveProviderEvidenceSlot: Codable, Equatable, Sendable {
    public var id: String
    public var label: String
    public var status: String
    public var classification: String?
    public var command: String
    public var detail: String?
    public var requiresLiveProviderConsent: Bool

    public init(
        id: String,
        label: String,
        status: String,
        classification: String? = nil,
        command: String,
        detail: String? = nil,
        requiresLiveProviderConsent: Bool
    ) {
        self.id = id
        self.label = label
        self.status = status
        self.classification = classification
        self.command = command
        self.detail = detail
        self.requiresLiveProviderConsent = requiresLiveProviderConsent
    }
}

public struct LiveProviderEvidenceSafety: Codable, Equatable, Sendable {
    public var commandsRun: Bool
    public var providerCalls: Bool
    public var providerSecretsInReport: Bool
    public var rawMediaInReport: Bool
    public var localPathsInReport: Bool
    public var paymentLinksInReport: Bool

    public init(
        commandsRun: Bool,
        providerCalls: Bool,
        providerSecretsInReport: Bool,
        rawMediaInReport: Bool,
        localPathsInReport: Bool,
        paymentLinksInReport: Bool
    ) {
        self.commandsRun = commandsRun
        self.providerCalls = providerCalls
        self.providerSecretsInReport = providerSecretsInReport
        self.rawMediaInReport = rawMediaInReport
        self.localPathsInReport = localPathsInReport
        self.paymentLinksInReport = paymentLinksInReport
    }
}

public struct LiveProviderEvidenceReport: Codable, Equatable, Sendable {
    public var kind: String
    public var status: String
    public var summary: LiveProviderEvidenceSummary
    public var firstBlocker: LiveProviderEvidenceSlot?
    public var evidence: [LiveProviderEvidenceSlot]
    public var operatorActions: [String]
    public var safety: LiveProviderEvidenceSafety

    public init(
        kind: String,
        status: String,
        summary: LiveProviderEvidenceSummary,
        firstBlocker: LiveProviderEvidenceSlot? = nil,
        evidence: [LiveProviderEvidenceSlot],
        operatorActions: [String],
        safety: LiveProviderEvidenceSafety
    ) {
        self.kind = kind
        self.status = status
        self.summary = summary
        self.firstBlocker = firstBlocker
        self.evidence = evidence
        self.operatorActions = operatorActions
        self.safety = safety
    }
}

public struct PrintFulfillmentReadinessSummary: Codable, Equatable, Sendable {
    public var ready: Int
    public var partial: Int
    public var blocked: Int

    public init(ready: Int, partial: Int, blocked: Int) {
        self.ready = ready
        self.partial = partial
        self.blocked = blocked
    }
}

public struct PrintFulfillmentReadinessCheck: Codable, Equatable, Sendable {
    public var id: String
    public var label: String
    public var status: String
    public var classification: String?
    public var command: String
    public var detail: String
    public var evidence: [String]

    private enum CodingKeys: String, CodingKey {
        case id
        case label
        case status
        case classification
        case command
        case detail
        case evidence
    }

    public init(
        id: String,
        label: String,
        status: String,
        classification: String? = nil,
        command: String,
        detail: String,
        evidence: [String]
    ) {
        self.id = id
        self.label = label
        self.status = status
        self.classification = classification
        self.command = command
        self.detail = detail
        self.evidence = evidence
    }

    public init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.id = try container.decode(String.self, forKey: .id)
        self.label = try container.decode(String.self, forKey: .label)
        self.status = try container.decode(String.self, forKey: .status)
        self.classification = try container.decodeIfPresent(String.self, forKey: .classification)
        self.command = try container.decode(String.self, forKey: .command)
        self.detail = try container.decodeIfPresent(String.self, forKey: .detail) ?? ""
        self.evidence = try container.decodeIfPresent([String].self, forKey: .evidence) ?? []
    }
}

public struct PrintFulfillmentReadinessSafety: Codable, Equatable, Sendable {
    public var commandsRun: Bool
    public var providerCalls: Bool
    public var liveProviderCalls: Bool
    public var writesBackendEnv: Bool
    public var writesIosDeployConfig: Bool
    public var globalMutation: Bool
    public var xcodeOrSigning: Bool
    public var keychainWrites: Bool
    public var providerSecretsInReport: Bool
    public var rawPrivateContextInReport: Bool
    public var rawMediaInReport: Bool
    public var paymentLinksInReport: Bool
    public var localPathsInReport: Bool

    public init(
        commandsRun: Bool,
        providerCalls: Bool,
        liveProviderCalls: Bool,
        writesBackendEnv: Bool,
        writesIosDeployConfig: Bool,
        globalMutation: Bool,
        xcodeOrSigning: Bool,
        keychainWrites: Bool,
        providerSecretsInReport: Bool,
        rawPrivateContextInReport: Bool,
        rawMediaInReport: Bool,
        paymentLinksInReport: Bool,
        localPathsInReport: Bool
    ) {
        self.commandsRun = commandsRun
        self.providerCalls = providerCalls
        self.liveProviderCalls = liveProviderCalls
        self.writesBackendEnv = writesBackendEnv
        self.writesIosDeployConfig = writesIosDeployConfig
        self.globalMutation = globalMutation
        self.xcodeOrSigning = xcodeOrSigning
        self.keychainWrites = keychainWrites
        self.providerSecretsInReport = providerSecretsInReport
        self.rawPrivateContextInReport = rawPrivateContextInReport
        self.rawMediaInReport = rawMediaInReport
        self.paymentLinksInReport = paymentLinksInReport
        self.localPathsInReport = localPathsInReport
    }
}

public struct PrintFulfillmentReadinessReport: Codable, Equatable, Sendable {
    public var kind: String
    public var status: String
    public var summary: PrintFulfillmentReadinessSummary
    public var checks: [PrintFulfillmentReadinessCheck]
    public var firstBlocker: PrintFulfillmentReadinessCheck?
    public var operatorActions: [String]
    public var commands: [String]
    public var safety: PrintFulfillmentReadinessSafety

    public init(
        kind: String,
        status: String,
        summary: PrintFulfillmentReadinessSummary,
        checks: [PrintFulfillmentReadinessCheck],
        firstBlocker: PrintFulfillmentReadinessCheck? = nil,
        operatorActions: [String],
        commands: [String],
        safety: PrintFulfillmentReadinessSafety
    ) {
        self.kind = kind
        self.status = status
        self.summary = summary
        self.checks = checks
        self.firstBlocker = firstBlocker
        self.operatorActions = operatorActions
        self.commands = commands
        self.safety = safety
    }
}

public struct FinalShowcaseReadinessSummary: Codable, Equatable, Sendable {
    public var ready: Int
    public var partial: Int
    public var blocked: Int

    public init(ready: Int, partial: Int, blocked: Int) {
        self.ready = ready
        self.partial = partial
        self.blocked = blocked
    }
}

public struct FinalShowcaseReadinessCapability: Codable, Equatable, Sendable {
    public var id: String
    public var label: String
    public var status: String
    public var classification: String?
    public var required: Bool
    public var evidence: [String]
    public var command: String
    public var detail: String

    public init(
        id: String,
        label: String,
        status: String,
        classification: String? = nil,
        required: Bool,
        evidence: [String],
        command: String,
        detail: String
    ) {
        self.id = id
        self.label = label
        self.status = status
        self.classification = classification
        self.required = required
        self.evidence = evidence
        self.command = command
        self.detail = detail
    }
}

public struct FinalShowcaseReadinessSafety: Codable, Equatable, Sendable {
    public var commandsRun: Bool
    public var providerCalls: Bool
    public var liveProviderCalls: Bool
    public var writesBackendEnv: Bool
    public var writesIosDeployConfig: Bool
    public var globalMutation: Bool
    public var xcodeOrSigning: Bool
    public var keychainWrites: Bool
    public var providerSecretsInReport: Bool
    public var rawPrivateContextInReport: Bool
    public var rawMediaInReport: Bool
    public var paymentLinksInReport: Bool
    public var localPathsInReport: Bool

    public init(
        commandsRun: Bool,
        providerCalls: Bool,
        liveProviderCalls: Bool,
        writesBackendEnv: Bool,
        writesIosDeployConfig: Bool,
        globalMutation: Bool,
        xcodeOrSigning: Bool,
        keychainWrites: Bool,
        providerSecretsInReport: Bool,
        rawPrivateContextInReport: Bool,
        rawMediaInReport: Bool,
        paymentLinksInReport: Bool,
        localPathsInReport: Bool
    ) {
        self.commandsRun = commandsRun
        self.providerCalls = providerCalls
        self.liveProviderCalls = liveProviderCalls
        self.writesBackendEnv = writesBackendEnv
        self.writesIosDeployConfig = writesIosDeployConfig
        self.globalMutation = globalMutation
        self.xcodeOrSigning = xcodeOrSigning
        self.keychainWrites = keychainWrites
        self.providerSecretsInReport = providerSecretsInReport
        self.rawPrivateContextInReport = rawPrivateContextInReport
        self.rawMediaInReport = rawMediaInReport
        self.paymentLinksInReport = paymentLinksInReport
        self.localPathsInReport = localPathsInReport
    }
}

public struct FinalShowcaseReadinessReport: Codable, Equatable, Sendable {
    public var kind: String
    public var status: String
    public var summary: FinalShowcaseReadinessSummary
    public var capabilities: [FinalShowcaseReadinessCapability]
    public var firstBlocker: FinalShowcaseReadinessCapability?
    public var operatorActions: [String]
    public var commands: [String]
    public var safety: FinalShowcaseReadinessSafety

    public init(
        kind: String,
        status: String,
        summary: FinalShowcaseReadinessSummary,
        capabilities: [FinalShowcaseReadinessCapability],
        firstBlocker: FinalShowcaseReadinessCapability? = nil,
        operatorActions: [String],
        commands: [String],
        safety: FinalShowcaseReadinessSafety
    ) {
        self.kind = kind
        self.status = status
        self.summary = summary
        self.capabilities = capabilities
        self.firstBlocker = firstBlocker
        self.operatorActions = operatorActions
        self.commands = commands
        self.safety = safety
    }
}

public struct FinalDemoLaunchReport: Codable, Equatable, Sendable {
    public var kind: String
    public var mode: String
    public var overallStatus: String
    public var summary: FinalDemoLaunchSummary
    public var phaseSummary: FinalDemoLaunchSummary?
    public var finalResourcesPreflight: FinalResourcesPreflightReport?
    public var finalAcceptanceReadiness: FinalAcceptanceReadinessReport?
    public var threeDEvaluationReadiness: ThreeDEvaluationReadinessReport?
    public var npcAgentEvaluationReadiness: NPCAgentEvaluationReadinessReport?
    public var visualRegressionReadiness: VisualRegressionReadinessReport?
    public var liveProviderEvidence: LiveProviderEvidenceReport?
    public var printFulfillmentReadiness: PrintFulfillmentReadinessReport?
    public var finalShowcaseReadiness: FinalShowcaseReadinessReport?
    public var finalOperatorHandoff: FinalOperatorHandoffReport?
    public var iosDeployRunbook: IOSDeployRunbookReport?
    public var iosDeviceLaunchRehearsalReadiness: IOSDeviceLaunchRehearsalReadinessReport?
    public var resourceReport: ResourceHandoffReport?
    public var launchPhases: [FinalDemoLaunchPhase]
    public var operatorChecklist: [String]
    public var commands: [String]
    public var liveCallPolicy: FinalDemoLaunchLiveCallPolicy
    public var safety: FinalDemoLaunchSafety

    public init(
        kind: String,
        mode: String,
        overallStatus: String,
        summary: FinalDemoLaunchSummary,
        phaseSummary: FinalDemoLaunchSummary? = nil,
        finalResourcesPreflight: FinalResourcesPreflightReport? = nil,
        finalAcceptanceReadiness: FinalAcceptanceReadinessReport? = nil,
        threeDEvaluationReadiness: ThreeDEvaluationReadinessReport? = nil,
        npcAgentEvaluationReadiness: NPCAgentEvaluationReadinessReport? = nil,
        visualRegressionReadiness: VisualRegressionReadinessReport? = nil,
        liveProviderEvidence: LiveProviderEvidenceReport? = nil,
        printFulfillmentReadiness: PrintFulfillmentReadinessReport? = nil,
        finalShowcaseReadiness: FinalShowcaseReadinessReport? = nil,
        finalOperatorHandoff: FinalOperatorHandoffReport? = nil,
        iosDeployRunbook: IOSDeployRunbookReport? = nil,
        iosDeviceLaunchRehearsalReadiness: IOSDeviceLaunchRehearsalReadinessReport? = nil,
        resourceReport: ResourceHandoffReport? = nil,
        launchPhases: [FinalDemoLaunchPhase],
        operatorChecklist: [String],
        commands: [String],
        liveCallPolicy: FinalDemoLaunchLiveCallPolicy,
        safety: FinalDemoLaunchSafety
    ) {
        self.kind = kind
        self.mode = mode
        self.overallStatus = overallStatus
        self.summary = summary
        self.phaseSummary = phaseSummary
        self.finalResourcesPreflight = finalResourcesPreflight
        self.finalAcceptanceReadiness = finalAcceptanceReadiness
        self.threeDEvaluationReadiness = threeDEvaluationReadiness
        self.npcAgentEvaluationReadiness = npcAgentEvaluationReadiness
        self.visualRegressionReadiness = visualRegressionReadiness
        self.liveProviderEvidence = liveProviderEvidence
        self.printFulfillmentReadiness = printFulfillmentReadiness
        self.finalShowcaseReadiness = finalShowcaseReadiness
        self.finalOperatorHandoff = finalOperatorHandoff
        self.iosDeployRunbook = iosDeployRunbook
        self.iosDeviceLaunchRehearsalReadiness = iosDeviceLaunchRehearsalReadiness
        self.resourceReport = resourceReport
        self.launchPhases = launchPhases
        self.operatorChecklist = operatorChecklist
        self.commands = commands
        self.liveCallPolicy = liveCallPolicy
        self.safety = safety
    }
}

public struct NPCAgentTick: Codable, Equatable, Sendable {
    public var sessionId: String
    public var tickIndex: Int
    public var agentRuntime: String
    public var npcAgentTraces: [NPCAgentTrace]
    public var npcReactions: [NPCReaction]
    public var worldResolution: WorldResolution

    public init(
        sessionId: String,
        tickIndex: Int,
        agentRuntime: String,
        npcAgentTraces: [NPCAgentTrace],
        npcReactions: [NPCReaction],
        worldResolution: WorldResolution
    ) {
        self.sessionId = sessionId
        self.tickIndex = tickIndex
        self.agentRuntime = agentRuntime
        self.npcAgentTraces = npcAgentTraces
        self.npcReactions = npcReactions
        self.worldResolution = worldResolution
    }
}

public struct MythSession: Codable, Equatable, Sendable {
    public var sessionId: String
    public var status: String
    public var objectCard: ObjectCard
    public var mythSeed: MythSeed
    public var generatedAsset: GeneratedAsset
    public var npcDirector: String
    public var npcAgentRuntime: String
    public var npcAgentTraces: [NPCAgentTrace]
    public var npcReactions: [NPCReaction]
    public var worldResolution: WorldResolution
    public var printCandidate: PrintCandidate

    private enum CodingKeys: String, CodingKey {
        case sessionId
        case status
        case objectCard
        case mythSeed
        case generatedAsset
        case npcDirector
        case npcAgentRuntime
        case npcAgentTraces
        case npcReactions
        case worldResolution
        case printCandidate
    }

    public init(
        sessionId: String,
        status: String,
        objectCard: ObjectCard,
        mythSeed: MythSeed,
        generatedAsset: GeneratedAsset,
        npcDirector: String,
        npcAgentRuntime: String = "",
        npcAgentTraces: [NPCAgentTrace] = [],
        npcReactions: [NPCReaction],
        worldResolution: WorldResolution,
        printCandidate: PrintCandidate
    ) {
        self.sessionId = sessionId
        self.status = status
        self.objectCard = objectCard
        self.mythSeed = mythSeed
        self.generatedAsset = generatedAsset
        self.npcDirector = npcDirector
        self.npcAgentRuntime = npcAgentRuntime
        self.npcAgentTraces = npcAgentTraces
        self.npcReactions = npcReactions
        self.worldResolution = worldResolution
        self.printCandidate = printCandidate
    }

    public init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.sessionId = try container.decode(String.self, forKey: .sessionId)
        self.status = try container.decode(String.self, forKey: .status)
        self.objectCard = try container.decode(ObjectCard.self, forKey: .objectCard)
        self.mythSeed = try container.decode(MythSeed.self, forKey: .mythSeed)
        self.generatedAsset = try container.decode(GeneratedAsset.self, forKey: .generatedAsset)
        self.npcDirector = try container.decode(String.self, forKey: .npcDirector)
        self.npcAgentRuntime = try container.decodeIfPresent(String.self, forKey: .npcAgentRuntime) ?? ""
        self.npcAgentTraces = try container.decodeIfPresent([NPCAgentTrace].self, forKey: .npcAgentTraces) ?? []
        self.npcReactions = try container.decode([NPCReaction].self, forKey: .npcReactions)
        self.worldResolution = try container.decode(WorldResolution.self, forKey: .worldResolution)
        self.printCandidate = try container.decode(PrintCandidate.self, forKey: .printCandidate)
    }

    public func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(sessionId, forKey: .sessionId)
        try container.encode(status, forKey: .status)
        try container.encode(objectCard, forKey: .objectCard)
        try container.encode(mythSeed, forKey: .mythSeed)
        try container.encode(generatedAsset, forKey: .generatedAsset)
        try container.encode(npcDirector, forKey: .npcDirector)
        try container.encode(npcAgentRuntime, forKey: .npcAgentRuntime)
        try container.encode(npcAgentTraces, forKey: .npcAgentTraces)
        try container.encode(npcReactions, forKey: .npcReactions)
        try container.encode(worldResolution, forKey: .worldResolution)
        try container.encode(printCandidate, forKey: .printCandidate)
    }
}

public struct MythSessionHistory: Codable, Equatable, Sendable {
    public var sessionId: String
    public var session: MythSession
    public var npcTicks: [NPCAgentTick]
    public var updatedAt: String

    public init(
        sessionId: String,
        session: MythSession,
        npcTicks: [NPCAgentTick],
        updatedAt: String
    ) {
        self.sessionId = sessionId
        self.session = session
        self.npcTicks = npcTicks
        self.updatedAt = updatedAt
    }
}

public struct NPCAutonomyRun: Codable, Equatable, Sendable {
    public var sessionId: String
    public var requestedSteps: Int
    public var completedSteps: Int
    public var startedTickIndex: Int
    public var completedTickIndex: Int
    public var agentRuntime: String
    public var history: MythSessionHistory

    public init(
        sessionId: String,
        requestedSteps: Int,
        completedSteps: Int,
        startedTickIndex: Int,
        completedTickIndex: Int,
        agentRuntime: String,
        history: MythSessionHistory
    ) {
        self.sessionId = sessionId
        self.requestedSteps = requestedSteps
        self.completedSteps = completedSteps
        self.startedTickIndex = startedTickIndex
        self.completedTickIndex = completedTickIndex
        self.agentRuntime = agentRuntime
        self.history = history
    }
}
