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

public struct GeneratedAsset: Codable, Equatable, Sendable {
    public var kind: String
    public var provider: String
    public var format: String
    public var uri: String
    public var prompt: String
    public var moderationStatus: String
    public var variants: [GeneratedAssetVariant]

    private enum CodingKeys: String, CodingKey {
        case kind
        case provider
        case format
        case uri
        case prompt
        case moderationStatus
        case variants
    }

    public init(
        kind: String,
        provider: String,
        format: String,
        uri: String,
        prompt: String,
        moderationStatus: String,
        variants: [GeneratedAssetVariant] = []
    ) {
        self.kind = kind
        self.provider = provider
        self.format = format
        self.uri = uri
        self.prompt = prompt
        self.moderationStatus = moderationStatus
        self.variants = variants
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
