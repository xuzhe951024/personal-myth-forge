import Foundation

public enum NPCRitualStance: String, Codable, Equatable, Sendable {
    case watching
    case acting
    case debating
}

public struct NPCRitualActor: Codable, Equatable, Sendable {
    public var npcId: String
    public var name: String
    public var emotion: String
    public var stance: NPCRitualStance
    public var action: String
    public var positionX: Double
    public var positionZ: Double

    public init(
        npcId: String,
        name: String,
        emotion: String,
        stance: NPCRitualStance,
        action: String,
        positionX: Double,
        positionZ: Double
    ) {
        self.npcId = npcId
        self.name = name
        self.emotion = emotion
        self.stance = stance
        self.action = action
        self.positionX = positionX
        self.positionZ = positionZ
    }
}

public struct NPCRitualScene: Codable, Equatable, Sendable {
    public var title: String
    public var runtime: String
    public var actors: [NPCRitualActor]
    public var visibleChanges: [String]

    public init(
        title: String,
        runtime: String,
        actors: [NPCRitualActor],
        visibleChanges: [String]
    ) {
        self.title = title
        self.runtime = runtime
        self.actors = actors
        self.visibleChanges = visibleChanges
    }
}

public enum NPCRitualSceneBuilder {
    private static let positions: [(x: Double, z: Double)] = [
        (-1.1, 0.7),
        (1.1, 0.7),
        (0.0, -1.05),
    ]

    public static func build(session: MythSession, latestTick: NPCAgentTick?) -> NPCRitualScene {
        let source = ritualSource(session: session, latestTick: latestTick)
        let actors = actorSources(session: session, latestTick: latestTick)
            .enumerated()
            .prefix(3)
            .map { index, source in
            actor(
                source: source,
                position: positions[index]
            )
        }

        return NPCRitualScene(
            title: sanitize(session.mythSeed.title),
            runtime: sanitize(source.runtime),
            actors: actors,
            visibleChanges: source.resolution.visibleChanges.map(sanitize)
        )
    }

    private struct ActorSource {
        var trace: NPCAgentTrace
        var reaction: NPCReaction?
        var acceptedAction: ResolvedNPCAction?
        var rejectedAction: ResolvedNPCAction?
    }

    private static func ritualSource(
        session: MythSession,
        latestTick: NPCAgentTick?
    ) -> (
        runtime: String,
        traces: [NPCAgentTrace],
        reactions: [NPCReaction],
        resolution: WorldResolution
    ) {
        if let latestTick {
            return (
                latestTick.agentRuntime,
                latestTick.npcAgentTraces,
                latestTick.npcReactions,
                latestTick.worldResolution
            )
        }
        return (
            session.npcAgentRuntime,
            session.npcAgentTraces,
            session.npcReactions,
            session.worldResolution
        )
    }

    private static func actorSources(session: MythSession, latestTick: NPCAgentTick?) -> [ActorSource] {
        var sources: [ActorSource] = []
        if let latestTick {
            sources.append(
                contentsOf: actorSources(
                    traces: latestTick.npcAgentTraces,
                    reactions: latestTick.npcReactions,
                    resolution: latestTick.worldResolution
                )
            )
        } else {
            sources.append(
                contentsOf: actorSources(
                    traces: session.npcAgentTraces,
                    reactions: session.npcReactions,
                    resolution: session.worldResolution
                )
            )
        }

        if latestTick != nil, sources.count < positions.count {
            var seenNPCIds = Set(sources.map(\.trace.npcId))
            for fallback in actorSources(
                traces: session.npcAgentTraces,
                reactions: session.npcReactions,
                resolution: session.worldResolution
            ) {
                guard !seenNPCIds.contains(fallback.trace.npcId) else {
                    continue
                }
                sources.append(fallback)
                seenNPCIds.insert(fallback.trace.npcId)
                if sources.count == positions.count {
                    break
                }
            }
        }

        return sources
    }

    private static func actorSources(
        traces: [NPCAgentTrace],
        reactions: [NPCReaction],
        resolution: WorldResolution
    ) -> [ActorSource] {
        traces.map { trace in
            ActorSource(
                trace: trace,
                reaction: reactions.first { $0.npcId == trace.npcId },
                acceptedAction: resolution.acceptedActions.first { $0.npcId == trace.npcId },
                rejectedAction: resolution.rejectedActions.first { $0.npcId == trace.npcId }
            )
        }
    }

    private static func actor(
        source: ActorSource,
        position: (x: Double, z: Double)
    ) -> NPCRitualActor {
        NPCRitualActor(
            npcId: sanitize(source.trace.npcId),
            name: sanitize(source.trace.name),
            emotion: sanitize(source.reaction?.emotion ?? "watching"),
            stance: stance(acceptedAction: source.acceptedAction, rejectedAction: source.rejectedAction),
            action: sanitize(source.acceptedAction?.action ?? source.rejectedAction?.action ?? source.trace.proposedAction),
            positionX: position.x,
            positionZ: position.z
        )
    }

    private static func stance(
        acceptedAction: ResolvedNPCAction?,
        rejectedAction: ResolvedNPCAction?
    ) -> NPCRitualStance {
        if acceptedAction != nil {
            return .acting
        }
        if rejectedAction != nil {
            return .debating
        }
        return .watching
    }

    private static func sanitize(_ value: String) -> String {
        let lowered = value.lowercased()
        let bearerMarker = "Bearer" + " "
        let apiKeyMarker = "api" + "_key"
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
