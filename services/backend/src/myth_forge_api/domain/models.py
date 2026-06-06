from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

CAPTURE_ID_PATTERN = r"^cap_[0-9a-f]{16}$"


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


class ObjectCaptureMetadata(BaseModel):
    label: str = Field(min_length=1)
    materials: list[str] = Field(default_factory=list)
    source: str = Field(min_length=1)
    capture_mode: Literal["single_photo", "photo_set", "manual_upload", "arkit_scan"]
    visual_notes: str | None = None

    def to_object_observation(self) -> ObjectObservation:
        return ObjectObservation(
            label=self.label,
            materials=self.materials,
            source=self.source,
            visual_notes=self.visual_notes,
        )


class CaptureMediaItem(BaseModel):
    media_id: str
    role: Literal["reference_image", "scan_asset"]
    content_type: str
    byte_size: int = Field(ge=0)
    uri: str
    moderation_status: Literal["not_requested", "approved", "needs_review"]


class ObjectCapture(BaseModel):
    capture_id: str = Field(pattern=CAPTURE_ID_PATTERN)
    status: Literal["ready", "blocked", "processing"]
    source: str
    capture_mode: Literal["single_photo", "photo_set", "manual_upload", "arkit_scan"]
    object_observation: ObjectObservation
    media_items: list[CaptureMediaItem]
    created_at: str


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


class NPCDirectorResult(BaseModel):
    provider: str
    reactions: list[NPCReaction]


class ResolvedNPCAction(BaseModel):
    npc_id: str
    action: str
    status: Literal["accepted", "rejected"]
    reason: str


class WorldResolution(BaseModel):
    arbitrator: str
    summary: str
    accepted_actions: list[ResolvedNPCAction]
    rejected_actions: list[ResolvedNPCAction]
    world_state_delta: dict[str, int | str | bool]
    visible_changes: list[str]


class GeneratedAssetVariant(BaseModel):
    role: Literal["game_asset", "ios_scene_asset", "print_source"]
    format: str
    uri: str
    is_scene_loadable: bool = False


class GeneratedAsset(BaseModel):
    kind: Literal["game_asset"]
    provider: str
    format: str
    uri: str
    prompt: str
    moderation_status: Literal["not_requested", "approved", "needs_review"]
    variants: list[GeneratedAssetVariant] = Field(default_factory=list)


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
    npc_director: str
    npc_reactions: list[NPCReaction]
    world_resolution: WorldResolution
    print_candidate: PrintCandidate


class MythSessionRequest(BaseModel):
    object_observation: ObjectObservation
    context_capsule: ContextCapsule


class MythSessionFromCaptureRequest(BaseModel):
    capture_id: str = Field(min_length=1, pattern=CAPTURE_ID_PATTERN)
    context_capsule: ContextCapsule
