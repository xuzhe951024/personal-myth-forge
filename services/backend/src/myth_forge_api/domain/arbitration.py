from __future__ import annotations

from typing import Protocol

from myth_forge_api.domain.models import (
    ContextCapsule,
    GeneratedAsset,
    MythSeed,
    NPCReaction,
    ObjectCard,
    ResolvedNPCAction,
    WorldResolution,
)


class WorldArbitrator(Protocol):
    arbitrator_name: str

    def resolve(
        self,
        session_id: str,
        object_card: ObjectCard,
        myth_seed: MythSeed,
        context_capsule: ContextCapsule,
        generated_asset: GeneratedAsset,
        npc_reactions: list[NPCReaction],
    ) -> WorldResolution:
        ...


class LocalWorldArbitrator:
    arbitrator_name = "local_rules"

    allowed_terms = {
        "approach",
        "kneel",
        "invite",
        "keep",
        "question",
        "guard",
        "circle",
        "sketch",
        "suggest",
        "observe",
        "name",
        "debate",
    }
    unsafe_terms = {"steal", "private", "destroy", "harm", "order_print", "purchase", "dox"}

    def resolve(
        self,
        session_id: str,
        object_card: ObjectCard,
        myth_seed: MythSeed,
        context_capsule: ContextCapsule,
        generated_asset: GeneratedAsset,
        npc_reactions: list[NPCReaction],
    ) -> WorldResolution:
        accepted: list[ResolvedNPCAction] = []
        rejected: list[ResolvedNPCAction] = []
        for reaction in npc_reactions:
            for action in reaction.plan:
                lowered = action.lower()
                if any(term in lowered for term in self.unsafe_terms):
                    rejected.append(
                        ResolvedNPCAction(
                            npc_id=reaction.npc_id,
                            action=action,
                            status="rejected",
                            reason="blocked by safety and privacy rules",
                        )
                    )
                    continue
                if any(term in lowered for term in self.allowed_terms):
                    accepted.append(
                        ResolvedNPCAction(
                            npc_id=reaction.npc_id,
                            action=action,
                            status="accepted",
                            reason="safe ritual or debate action",
                        )
                    )
                    continue
                rejected.append(
                    ResolvedNPCAction(
                        npc_id=reaction.npc_id,
                        action=action,
                        status="rejected",
                        reason="unknown action requires review",
                    )
                )

        return WorldResolution(
            arbitrator=self.arbitrator_name,
            summary=_summary(accepted, rejected),
            accepted_actions=accepted,
            rejected_actions=rejected,
            world_state_delta=_world_delta(npc_reactions, accepted),
            visible_changes=_visible_changes(npc_reactions, accepted),
        )


def _summary(
    accepted_actions: list[ResolvedNPCAction],
    rejected_actions: list[ResolvedNPCAction],
) -> str:
    if rejected_actions:
        return (
            f"The village accepts {len(accepted_actions)} actions and blocks "
            f"{len(rejected_actions)} actions for review."
        )
    return f"The village accepts {len(accepted_actions)} ritual actions around the relic."


def _world_delta(
    npc_reactions: list[NPCReaction],
    accepted_actions: list[ResolvedNPCAction],
) -> dict[str, int | str | bool]:
    emotions = {reaction.npc_id: reaction.emotion.lower() for reaction in npc_reactions}
    accepted_count = len(accepted_actions)
    return {
        "faith": _count_emotion(emotions, "awe") + _count_world_change(npc_reactions, "faith"),
        "curiosity": _count_emotion(emotions, "curiosity"),
        "suspicion": _count_emotion(emotions, "suspicion") + _count_emotion(emotions, "fear"),
        "debate_intensity": _count_world_change(npc_reactions, "debate"),
        "artifact_renown": min(5, accepted_count),
    }


def _visible_changes(
    npc_reactions: list[NPCReaction],
    accepted_actions: list[ResolvedNPCAction],
) -> list[str]:
    changes = [
        f"{_npc_name(npc_reactions, action.npc_id)} prepares to {action.action.replace('_', ' ')}."
        for action in accepted_actions[:4]
    ]
    if any("debate" in reaction.world_change for reaction in npc_reactions):
        changes.append("The village debate grows louder.")
    if any("name" in reaction.world_change for reaction in npc_reactions):
        changes.append("The artifact gains a local name.")
    return changes or ["The village holds still and studies the relic."]


def _npc_name(npc_reactions: list[NPCReaction], npc_id: str) -> str:
    for reaction in npc_reactions:
        if reaction.npc_id == npc_id:
            return reaction.name
    return npc_id


def _count_emotion(emotions: dict[str, str], emotion: str) -> int:
    return sum(1 for value in emotions.values() if emotion in value)


def _count_world_change(npc_reactions: list[NPCReaction], term: str) -> int:
    return sum(1 for reaction in npc_reactions if term in reaction.world_change.lower())
