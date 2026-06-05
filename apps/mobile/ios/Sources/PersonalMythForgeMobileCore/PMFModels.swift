import Foundation

public enum JSONValue: Codable, Equatable {
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

public struct ObjectObservation: Codable, Equatable {
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

public struct ContextCapsule: Codable, Equatable {
    public var currentTheme: String
    public var desiredTone: String
    public var recentMilestone: String?

    public init(currentTheme: String, desiredTone: String, recentMilestone: String? = nil) {
        self.currentTheme = currentTheme
        self.desiredTone = desiredTone
        self.recentMilestone = recentMilestone
    }
}

public struct ObjectCaptureMetadata: Codable, Equatable {
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

public struct CaptureMediaItem: Codable, Equatable {
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

public struct ObjectCapture: Codable, Equatable {
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

public struct ObjectCard: Codable, Equatable {
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

public struct MythSeed: Codable, Equatable {
    public var title: String
    public var personalResonance: String
    public var generationPrompt: String

    public init(title: String, personalResonance: String, generationPrompt: String) {
        self.title = title
        self.personalResonance = personalResonance
        self.generationPrompt = generationPrompt
    }
}

public struct GeneratedAsset: Codable, Equatable {
    public var kind: String
    public var provider: String
    public var format: String
    public var uri: String
    public var prompt: String
    public var moderationStatus: String

    public init(
        kind: String,
        provider: String,
        format: String,
        uri: String,
        prompt: String,
        moderationStatus: String
    ) {
        self.kind = kind
        self.provider = provider
        self.format = format
        self.uri = uri
        self.prompt = prompt
        self.moderationStatus = moderationStatus
    }
}

public struct NPCReaction: Codable, Equatable {
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

public struct ResolvedNPCAction: Codable, Equatable {
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

public struct WorldResolution: Codable, Equatable {
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

public struct PrintCandidate: Codable, Equatable {
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

public struct MythSession: Codable, Equatable {
    public var sessionId: String
    public var status: String
    public var objectCard: ObjectCard
    public var mythSeed: MythSeed
    public var generatedAsset: GeneratedAsset
    public var npcDirector: String
    public var npcReactions: [NPCReaction]
    public var worldResolution: WorldResolution
    public var printCandidate: PrintCandidate

    public init(
        sessionId: String,
        status: String,
        objectCard: ObjectCard,
        mythSeed: MythSeed,
        generatedAsset: GeneratedAsset,
        npcDirector: String,
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
        self.npcReactions = npcReactions
        self.worldResolution = worldResolution
        self.printCandidate = printCandidate
    }
}
