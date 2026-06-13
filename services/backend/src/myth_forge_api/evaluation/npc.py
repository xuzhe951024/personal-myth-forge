from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from typing import Protocol

from myth_forge_api.domain.models import (
    ContextCapsule,
    GeneratedAsset,
    GeneratedAssetProvenance,
    GeneratedAssetVariant,
    MythSeed,
    MythSession,
    NPCAgentTick,
    NPCAgentTickRequest,
    NPCReaction,
    ObjectObservation,
    PrintCandidate,
    WorldResolution,
)
from myth_forge_api.domain.pipeline import (
    _create_myth_seed as create_myth_seed,
)
from myth_forge_api.domain.pipeline import (
    _create_object_card as create_object_card,
)
from myth_forge_api.providers.npc import EXPECTED_NPC_ID_LIST

REVIEW_RUBRIC = [
    "NPC beliefs are distinct and grounded in the artifact",
    "Intentions produce visible village behavior",
    "Proposed actions appear in each NPC plan",
    "World arbitration accepts or rejects concrete actions",
    "Privacy boundary stays limited to approved context capsules",
]

MANUAL_REVIEW_EMPTY = {
    "agent_believability": None,
    "autonomy_signal": None,
    "world_impact": None,
    "privacy_boundary": None,
    "notes": None,
}


class NPCDirectorForEvaluation(Protocol):
    provider_name: str

    def generate_reactions(self, **kwargs):
        ...


class NPCTickRuntimeForEvaluation(Protocol):
    runtime_name: str

    def generate_tick(self, request: NPCAgentTickRequest) -> NPCAgentTick:
        ...


@dataclass(frozen=True)
class NPCAgentEvaluationCase:
    case_id: str
    category: str
    object_observation: ObjectObservation
    context_capsule: ContextCapsule
    review_focus: str
    recent_events: tuple[str, ...] = ()


DEFAULT_NPC_AGENT_EVALUATION_SUITE = (
    NPCAgentEvaluationCase(
        case_id="npc_01_brass_key_dispute",
        category="artifact_conflict",
        object_observation=ObjectObservation(
            label="worn brass key",
            materials=["brass", "scratched metal"],
            source="evaluation_object",
            visual_notes="small key with chipped teeth",
        ),
        context_capsule=ContextCapsule(
            current_theme="deciding who may open a difficult door",
            desired_tone="tender, cautious, autonomous",
            recent_milestone="finished a demanding transition",
        ),
        review_focus="distinct NPC beliefs and visible disagreement",
        recent_events=("Mara approached the relic first.", "Ior asked for rules."),
    ),
    NPCAgentEvaluationCase(
        case_id="npc_02_cup_memory",
        category="personal_resonance",
        object_observation=ObjectObservation(
            label="cracked ceramic cup",
            materials=["ceramic", "tea stain"],
            source="evaluation_object",
            visual_notes="hairline crack along the rim",
        ),
        context_capsule=ContextCapsule(
            current_theme="protecting a fragile routine",
            desired_tone="quiet, strange, hopeful",
            recent_milestone="rebuilt a morning habit",
        ),
        review_focus="personal context is summarized without raw private data",
    ),
    NPCAgentEvaluationCase(
        case_id="npc_03_receipt_rules",
        category="privacy_boundary",
        object_observation=ObjectObservation(
            label="folded receipt",
            materials=["paper", "ink"],
            source="evaluation_object",
            visual_notes="creased paper with unreadable numbers",
        ),
        context_capsule=ContextCapsule(
            current_theme="raw_email: never include this marker",
            desired_tone="private_message: never include this marker",
            recent_milestone="raw_calendar: never include this marker",
        ),
        review_focus="unsafe raw markers are redacted from reports",
    ),
    NPCAgentEvaluationCase(
        case_id="npc_04_threaded_charm",
        category="ritual_creation",
        object_observation=ObjectObservation(
            label="red threaded charm",
            materials=["thread", "wax", "brass bell"],
            source="evaluation_object",
            visual_notes="small charm with wax seal",
        ),
        context_capsule=ContextCapsule(
            current_theme="naming a promise before sharing it",
            desired_tone="ceremonial but practical",
            recent_milestone="made a promise public",
        ),
        review_focus="ritual naming with concrete village action",
        recent_events=("Senn proposed a first ritual name.",),
    ),
    NPCAgentEvaluationCase(
        case_id="npc_05_rusted_mirror",
        category="material_stress",
        object_observation=ObjectObservation(
            label="rusted mirror shard",
            materials=["rusted iron", "mirror glass"],
            source="evaluation_object",
            visual_notes="sharp reflective shard bound with rusted wire",
        ),
        context_capsule=ContextCapsule(
            current_theme="choosing what to reflect and what to hide",
            desired_tone="uneasy, observant, safe",
            recent_milestone="set a boundary",
        ),
        review_focus="cautious behavior around hazardous-looking material",
    ),
    NPCAgentEvaluationCase(
        case_id="npc_06_pocket_stone",
        category="continuity_tick",
        object_observation=ObjectObservation(
            label="smooth pocket stone",
            materials=["stone", "pale mineral vein"],
            source="evaluation_object",
            visual_notes="small stone with map-like line",
        ),
        context_capsule=ContextCapsule(
            current_theme="moving without losing orientation",
            desired_tone="grounded, curious, forward-looking",
            recent_milestone="arrived in a new place",
        ),
        review_focus="later ticks respond to recent events",
        recent_events=("The village placed the stone at the path entrance.",),
    ),
)


def run_npc_agent_evaluation(
    *,
    director: NPCDirectorForEvaluation,
    tick_runtime: NPCTickRuntimeForEvaluation,
    selected_provider: str,
    suite_name: str,
    tick_steps: int,
    cases: tuple[NPCAgentEvaluationCase, ...],
) -> dict[str, object]:
    case_reports = [_run_case(director, tick_runtime, case, tick_steps) for case in cases]
    succeeded = sum(1 for case in case_reports if case["status"] == "succeeded")
    failed = sum(1 for case in case_reports if case["status"] == "failed")
    return _sanitize_report(
        {
            "kind": "npc_agent_evaluation_report",
            "status": "failed" if failed else "succeeded",
            "suite": suite_name,
            "provider": selected_provider,
            "tick_steps": tick_steps,
            "total_cases": len(cases),
            "succeeded": succeeded,
            "failed": failed,
            "coverage": _coverage(case_reports),
            "review_rubric": REVIEW_RUBRIC,
            "safety": {
                "raw_private_context_in_report": False,
                "provider_secrets_in_report": False,
                "local_paths_in_report": False,
                "media_payloads_in_report": False,
            },
            "cases": case_reports,
        }
    )


def _run_case(
    director: NPCDirectorForEvaluation,
    tick_runtime: NPCTickRuntimeForEvaluation,
    evaluation_case: NPCAgentEvaluationCase,
    tick_steps: int,
) -> dict[str, object]:
    started_at = time.perf_counter()
    object_card = create_object_card(evaluation_case.object_observation)
    myth_seed = create_myth_seed(object_card, evaluation_case.context_capsule)
    generated_asset = _evaluation_asset(evaluation_case.case_id, myth_seed)
    session_id = _session_id_for_case(evaluation_case.case_id)
    base_report = {
        "case_id": evaluation_case.case_id,
        "category": evaluation_case.category,
        "object_label": evaluation_case.object_observation.label,
        "review_focus": evaluation_case.review_focus,
        "expected_npc_ids": EXPECTED_NPC_ID_LIST,
        "manual_review": dict(MANUAL_REVIEW_EMPTY),
    }
    try:
        director_result = director.generate_reactions(
            session_id=session_id,
            object_card=object_card,
            myth_seed=myth_seed,
            context_capsule=evaluation_case.context_capsule,
            generated_asset=generated_asset,
        )
        session = MythSession(
            session_id=session_id,
            status="ready_for_review",
            object_card=object_card,
            myth_seed=myth_seed,
            generated_asset=generated_asset,
            npc_director=director_result.provider,
            npc_agent_runtime=director_result.agent_runtime,
            npc_agent_traces=director_result.agent_traces,
            npc_reactions=director_result.reactions,
            world_resolution=_empty_world_resolution(),
            print_candidate=_evaluation_print_candidate(generated_asset),
        )
        ticks = []
        recent_events = list(evaluation_case.recent_events)
        for tick_index in range(1, tick_steps + 1):
            tick = tick_runtime.generate_tick(
                NPCAgentTickRequest(
                    session=session,
                    tick_index=tick_index,
                    recent_events=recent_events,
                )
            )
            ticks.append(_tick_summary(tick))
            recent_events.extend(tick.world_resolution.visible_changes)
        return {
            **base_report,
            "status": "succeeded",
            "provider": director_result.provider,
            "agent_runtime": director_result.agent_runtime,
            "tick_runtime": tick_runtime.runtime_name,
            "npc_ids": _canonical_npc_ids(director_result.reactions),
            "trace_count": len(director_result.agent_traces),
            "proposed_actions_in_plan": _proposed_actions_in_plan(
                director_result.agent_traces,
                director_result.reactions,
            ),
            "reaction_summaries": [
                {
                    "npc_id": reaction.npc_id,
                    "emotion": reaction.emotion,
                    "plan_count": len(reaction.plan),
                    "world_change": reaction.world_change,
                }
                for reaction in director_result.reactions
            ],
            "trace_summaries": [
                {
                    "npc_id": trace.npc_id,
                    "intention": trace.intention,
                    "proposed_action": trace.proposed_action,
                    "confidence": trace.confidence,
                }
                for trace in director_result.agent_traces
            ],
            "ticks": ticks,
            "elapsed_seconds": round(time.perf_counter() - started_at, 4),
            "error": None,
        }
    except Exception as exc:
        return {
            **base_report,
            "status": "failed",
            "provider": getattr(director, "provider_name", "unknown"),
            "agent_runtime": None,
            "tick_runtime": getattr(tick_runtime, "runtime_name", "unknown"),
            "npc_ids": [],
            "trace_count": 0,
            "proposed_actions_in_plan": False,
            "reaction_summaries": [],
            "trace_summaries": [],
            "ticks": [],
            "elapsed_seconds": round(time.perf_counter() - started_at, 4),
            "error": _safe_text(str(exc)),
        }


def _session_id_for_case(case_id: str) -> str:
    safe_case_id = re.sub(r"[^A-Za-z0-9_-]+", "_", case_id).strip("_").lower()
    return f"myth_eval_{safe_case_id[:48]}"


def _evaluation_asset(case_id: str, myth_seed: MythSeed) -> GeneratedAsset:
    safe_case_id = re.sub(r"[^A-Za-z0-9_-]+", "_", case_id).strip("_").lower()
    uri = f"local-generated://npc-evaluation/{safe_case_id}.glb"
    return GeneratedAsset(
        kind="game_asset",
        provider="npc_evaluation_local_asset",
        format="glb",
        uri=uri,
        prompt=myth_seed.generation_prompt,
        moderation_status="not_requested",
        variants=[
            GeneratedAssetVariant(
                role="game_asset",
                format="glb",
                uri=uri,
                is_scene_loadable=True,
            ),
            GeneratedAssetVariant(
                role="ios_scene_asset",
                format="usdz",
                uri=f"local-generated://npc-evaluation/{safe_case_id}.usdz",
                is_scene_loadable=True,
            ),
        ],
        generation_provenance=GeneratedAssetProvenance(
            input_mode="text_prompt",
            provider_route="npc_evaluation_local",
            source_image_count=0,
            selected_source_image_count=0,
            source_asset_count=0,
            selection_reason="NPC evaluation uses deterministic text prompt assets.",
            raw_sources_included=False,
        ),
    )


def _evaluation_print_candidate(generated_asset: GeneratedAsset) -> PrintCandidate:
    return PrintCandidate(
        kind="print_asset",
        source_asset_uri=generated_asset.uri,
        provider="npc_evaluation_local_print",
        format="3mf",
        uri=f"{generated_asset.uri}.3mf",
        requires_user_approval=True,
        approval_reason="Evaluation print candidate is illustrative only.",
        printability_notes=["NPC evaluation does not perform print repair."],
    )


def _empty_world_resolution() -> WorldResolution:
    return WorldResolution(
        arbitrator="npc_evaluation_initial_state",
        summary="NPC evaluation initial state before tick arbitration.",
        accepted_actions=[],
        rejected_actions=[],
        world_state_delta={"evaluation": True},
        visible_changes=[],
    )


def _tick_summary(tick: NPCAgentTick) -> dict[str, object]:
    return {
        "tick_index": tick.tick_index,
        "agent_runtime": tick.agent_runtime,
        "trace_count": len(tick.npc_agent_traces),
        "reaction_count": len(tick.npc_reactions),
        "accepted_action_count": len(tick.world_resolution.accepted_actions),
        "rejected_action_count": len(tick.world_resolution.rejected_actions),
        "visible_change_count": len(tick.world_resolution.visible_changes),
        "world_delta_keys": sorted(tick.world_resolution.world_state_delta.keys()),
    }


def _proposed_actions_in_plan(traces, reactions: list[NPCReaction]) -> bool:
    reaction_by_id = {reaction.npc_id: reaction for reaction in reactions}
    for trace in traces:
        reaction = reaction_by_id.get(trace.npc_id)
        if reaction is None:
            return False
        planned_actions = {_normalized_action(action) for action in reaction.plan}
        if _normalized_action(trace.proposed_action) not in planned_actions:
            return False
    return True


def _canonical_npc_ids(reactions: list[NPCReaction]) -> list[str]:
    present_ids = {reaction.npc_id for reaction in reactions}
    canonical_ids = [npc_id for npc_id in EXPECTED_NPC_ID_LIST if npc_id in present_ids]
    extra_ids = sorted(present_ids - set(EXPECTED_NPC_ID_LIST))
    return canonical_ids + extra_ids


def _coverage(case_reports: list[dict[str, object]]) -> dict[str, int]:
    coverage = {
        "expected_npc_sets": 0,
        "trace_sets": 0,
        "proposed_action_plan_matches": 0,
        "tick_steps_completed": 0,
        "world_resolution_steps": 0,
    }
    expected_ids = EXPECTED_NPC_ID_LIST
    for case_report in case_reports:
        if case_report.get("status") != "succeeded":
            continue
        if case_report.get("npc_ids") == expected_ids:
            coverage["expected_npc_sets"] += 1
        if case_report.get("trace_count") == 3:
            coverage["trace_sets"] += 1
        if case_report.get("proposed_actions_in_plan") is True:
            coverage["proposed_action_plan_matches"] += 1
        ticks = case_report.get("ticks")
        if not isinstance(ticks, list):
            continue
        coverage["tick_steps_completed"] += len(ticks)
        coverage["world_resolution_steps"] += sum(
            1
            for tick in ticks
            if isinstance(tick, dict)
            and (
                tick.get("accepted_action_count", 0) > 0
                or tick.get("rejected_action_count", 0) > 0
            )
        )
    return coverage


def _normalized_action(action: str) -> str:
    return action.strip().lower()


def _sanitize_report(report: dict[str, object]) -> dict[str, object]:
    return json.loads(json.dumps(_sanitize_value(report)))


def _sanitize_value(value):
    if isinstance(value, str):
        return _safe_text(value)
    if isinstance(value, list):
        return [_sanitize_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _sanitize_value(item) for key, item in value.items()}
    return value


def _safe_text(message: str) -> str:
    replacements = [
        r"Authorization\s*[=:]\s*Bearer\s+[A-Za-z0-9._~+/\-=:-]+",
        r"Bearer\s+[A-Za-z0-9._~+/\-=:-]+",
        r"raw=[^\s,;\"']+",
        r"api[_-]?key\s*[=:]\s*[^\s,;\"']+",
        r"file://[^\s,;\"']+",
        r"data:image/[^\s,;\"']+",
        r"/Users/[^\s,;\"']+",
        r"/tmp/[^\s,;\"']+",
        r"raw_email:[^\n\r]+",
        r"raw_calendar:[^\n\r]+",
        r"private_message:[^\n\r]+",
    ]
    sanitized = message
    for pattern in replacements:
        sanitized = re.sub(pattern, "[withheld]", sanitized, flags=re.IGNORECASE)
    return sanitized
