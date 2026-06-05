from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ObjectObservation(BaseModel):
    model_config = ConfigDict(extra="allow")

    label: str = Field(min_length=1)
    materials: list[str] = Field(default_factory=list)
    source: str = Field(min_length=1)
    visual_notes: str | None = None


class ContextCapsule(BaseModel):
    model_config = ConfigDict(extra="allow")

    current_theme: str = Field(min_length=1)
    desired_tone: str = Field(min_length=1)
    recent_milestone: str | None = None


class ObjectCard(BaseModel):
    label: str
    materials: list[str]
    source: str
    affordances: list[str]
    symbolic_reading: str


class MythSeed(BaseModel):
    title: str
    personal_resonance: str
    generation_prompt: str


class NPCReaction(BaseModel):
    npc_id: str
    name: str
    emotion: str
    interpretation: str
    plan: list[str]
    world_change: str


class GeneratedAsset(BaseModel):
    kind: Literal["game_asset"]
    provider: str
    format: str
    uri: str
    prompt: str
    moderation_status: Literal["not_requested", "approved", "needs_review"]


class PrintCandidate(BaseModel):
    kind: Literal["print_asset"]
    source_asset_uri: str
    provider: str
    format: str
    uri: str
    requires_user_approval: bool
    approval_reason: str
    printability_notes: list[str]


class MythSession(BaseModel):
    session_id: str
    status: Literal["ready_for_review", "blocked", "processing"]
    object_card: ObjectCard
    myth_seed: MythSeed
    generated_asset: GeneratedAsset
    npc_reactions: list[NPCReaction]
    print_candidate: PrintCandidate


class MythSessionRequest(BaseModel):
    object_observation: ObjectObservation
    context_capsule: ContextCapsule

