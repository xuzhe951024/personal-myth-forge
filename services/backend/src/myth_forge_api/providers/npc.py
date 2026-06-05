from __future__ import annotations

from typing import Protocol

from myth_forge_api.domain.models import (
    ContextCapsule,
    GeneratedAsset,
    MythSeed,
    NPCDirectorResult,
    NPCReaction,
    ObjectCard,
)


class NPCDirector(Protocol):
    provider_name: str

    def generate_reactions(
        self,
        session_id: str,
        object_card: ObjectCard,
        myth_seed: MythSeed,
        context_capsule: ContextCapsule,
        generated_asset: GeneratedAsset,
    ) -> NPCDirectorResult:
        ...


class LocalNPCDirector:
    provider_name = "local_stub"

    def generate_reactions(
        self,
        session_id: str,
        object_card: ObjectCard,
        myth_seed: MythSeed,
        context_capsule: ContextCapsule,
        generated_asset: GeneratedAsset,
    ) -> NPCDirectorResult:
        return NPCDirectorResult(
            provider=self.provider_name,
            reactions=[
                NPCReaction(
                    npc_id="mara",
                    name="Mara",
                    emotion="awe",
                    interpretation=f"{object_card.label} is a sign that the village has been heard.",
                    plan=[
                        "approach_artifact",
                        "kneel_near_artifact",
                        "invite_neighbors_to_witness",
                    ],
                    world_change="faith_in_player_increases",
                ),
                NPCReaction(
                    npc_id="ior",
                    name="Ior",
                    emotion="suspicion",
                    interpretation=f"{myth_seed.title} may be a test rather than a gift.",
                    plan=[
                        "keep_distance",
                        "question_mara",
                        "propose_guarding_the_artifact_overnight",
                    ],
                    world_change="village_debate_starts",
                ),
                NPCReaction(
                    npc_id="senn",
                    name="Senn",
                    emotion="curiosity",
                    interpretation="The artifact should be named before anyone tries to use it.",
                    plan=[
                        "circle_artifact",
                        "sketch_symbol_in_dirt",
                        "suggest_ritual_name",
                    ],
                    world_change="artifact_gets_a_local_name",
                ),
            ],
        )
