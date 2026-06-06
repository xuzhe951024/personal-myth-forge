from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, replace
from typing import Any, Literal

from myth_forge_api.config import Settings, load_settings
from myth_forge_api.domain.models import (
    ContextCapsule,
    MythSessionHistory,
    NPCAgentTick,
    NPCAgentTickRequest,
    ObjectObservation,
)
from myth_forge_api.domain.pipeline import create_demo_myth_session
from myth_forge_api.providers.factory import (
    build_myth_session_store,
    build_npc_director,
    build_npc_tick_runtime,
    build_three_d_provider,
)
from myth_forge_api.providers.readiness import build_provider_readiness

CORE_PROVIDER_KINDS = ["three_d", "npc", "capture_storage"]
ProviderMode = Literal["local", "configured"]


@dataclass(frozen=True)
class DemoAcceptanceResult:
    exit_code: int
    report: dict[str, Any]


def run_demo_acceptance(
    *,
    settings: Settings | None = None,
    provider_mode: ProviderMode = "local",
    npc_steps: int = 3,
    require_real_core: bool = False,
) -> DemoAcceptanceResult:
    if npc_steps < 0 or npc_steps > 3:
        raise ValueError("npc_steps must be between 0 and 3.")
    started_at = time.perf_counter()
    selected_settings = _settings_for_provider_mode(settings or load_settings(), provider_mode)
    readiness = build_provider_readiness(selected_settings)
    readiness_payload = readiness.model_dump(mode="json")
    provider_by_kind = {item["kind"]: item for item in readiness_payload["providers"]}
    core_real_ready = _core_real_ready(provider_by_kind)
    base_report = _base_report(
        provider_mode=provider_mode,
        require_real_core=require_real_core,
        readiness_payload=readiness_payload,
        provider_by_kind=provider_by_kind,
        core_real_ready=core_real_ready,
        started_at=started_at,
    )

    if require_real_core and not core_real_ready:
        report = {
            **base_report,
            "status": "not_ready",
            "missing_env": _missing_env(readiness_payload),
            "error": "Core providers are not real-provider-ready.",
        }
        return DemoAcceptanceResult(exit_code=2, report=_sanitize_report(report))

    try:
        session = create_demo_myth_session(
            object_observation=_acceptance_observation(),
            context_capsule=_acceptance_context(),
            three_d_provider=build_three_d_provider(selected_settings),
            npc_director=build_npc_director(selected_settings),
        )
        store = build_myth_session_store(selected_settings)
        history = store.save_session(session)
        ticks: list[NPCAgentTick] = []
        runtime = build_npc_tick_runtime(selected_settings)
        current_history = history
        for _ in range(npc_steps):
            request = NPCAgentTickRequest(
                session=current_history.session,
                tick_index=_next_tick_index(current_history),
                recent_events=_recent_events(current_history),
            )
            tick = runtime.generate_tick(request)
            current_history = store.append_tick(current_history.session, tick)
            ticks.append(tick)
        report = {
            **base_report,
            "status": "succeeded",
            "missing_env": _missing_env(readiness_payload),
            "session": _session_summary(session),
            "npc": _npc_summary(session, ticks, npc_steps),
            "timings": _timings(started_at),
            "safety": _safety_summary(),
            "error": None,
        }
        return DemoAcceptanceResult(exit_code=0, report=_sanitize_report(report))
    except Exception as exc:
        report = {
            **base_report,
            "status": "failed",
            "missing_env": _missing_env(readiness_payload),
            "session": None,
            "npc": {
                "requested_steps": npc_steps,
                "completed_steps": 0,
                "latest_tick_index": None,
                "tick_runtime": None,
            },
            "timings": _timings(started_at),
            "safety": _safety_summary(),
            "error": _safe_text(str(exc)),
        }
        return DemoAcceptanceResult(exit_code=1, report=_sanitize_report(report))


def _settings_for_provider_mode(settings: Settings, provider_mode: ProviderMode) -> Settings:
    if provider_mode == "local":
        return replace(settings, three_d_provider="local", npc_provider="local")
    if provider_mode == "configured":
        return settings
    raise ValueError(f"Unsupported provider_mode: {provider_mode}")


def _acceptance_observation() -> ObjectObservation:
    return ObjectObservation(
        label="old brass key",
        materials=["metal", "brass"],
        source="acceptance_harness",
        visual_notes="worn teeth, circular bow, warm reflections",
    )


def _acceptance_context() -> ContextCapsule:
    return ContextCapsule(
        current_theme="deadline pressure",
        desired_tone="tender, strange",
    )


def _base_report(
    *,
    provider_mode: str,
    require_real_core: bool,
    readiness_payload: dict[str, Any],
    provider_by_kind: dict[str, dict[str, Any]],
    core_real_ready: bool,
    started_at: float,
) -> dict[str, Any]:
    return {
        "kind": "demo_acceptance_report",
        "mode": provider_mode,
        "require_real_core": require_real_core,
        "core_provider_kinds": CORE_PROVIDER_KINDS,
        "core_real_ready": core_real_ready,
        "provider_readiness": readiness_payload,
        "selected_providers": {
            kind: provider_by_kind.get(kind, {}).get("selected_provider")
            for kind in CORE_PROVIDER_KINDS
        },
        "timings": _timings(started_at),
        "safety": _safety_summary(),
    }


def _core_real_ready(provider_by_kind: dict[str, dict[str, Any]]) -> bool:
    return all(
        provider_by_kind.get(kind, {}).get("is_real_provider_ready") is True
        for kind in CORE_PROVIDER_KINDS
    )


def _missing_env(readiness_payload: dict[str, Any]) -> list[str]:
    return sorted(
        {
            env_name
            for provider in readiness_payload["providers"]
            for env_name in provider.get("missing_env", [])
        }
    )


def _next_tick_index(history: MythSessionHistory) -> int:
    if not history.npc_ticks:
        return 1
    return max(tick.tick_index for tick in history.npc_ticks) + 1


def _recent_events(history: MythSessionHistory) -> list[str]:
    if history.npc_ticks:
        return history.npc_ticks[-1].world_resolution.visible_changes
    return history.session.world_resolution.visible_changes


def _session_summary(session) -> dict[str, Any]:
    scene_variant = next(
        (
            variant
            for variant in session.generated_asset.variants
            if variant.role == "ios_scene_asset" and variant.is_scene_loadable
        ),
        None,
    )
    return {
        "session_id": session.session_id,
        "title": session.myth_seed.title,
        "generated_asset_provider": session.generated_asset.provider,
        "generated_asset_format": session.generated_asset.format,
        "generated_asset_uri": session.generated_asset.uri,
        "generation_provenance": _generation_provenance_summary(
            session.generated_asset.generation_provenance
        ),
        "scene_variant_uri": scene_variant.uri if scene_variant is not None else None,
        "print_candidate_format": session.print_candidate.format,
    }


def _generation_provenance_summary(provenance) -> dict[str, Any] | None:
    if provenance is None:
        return None
    return provenance.model_dump(mode="json")


def _npc_summary(
    session,
    ticks: list[NPCAgentTick],
    requested_steps: int,
) -> dict[str, Any]:
    latest_tick = ticks[-1] if ticks else None
    return {
        "initial_runtime": session.npc_agent_runtime,
        "reaction_count": len(session.npc_reactions),
        "requested_steps": requested_steps,
        "completed_steps": len(ticks),
        "latest_tick_index": latest_tick.tick_index if latest_tick is not None else None,
        "tick_runtime": latest_tick.agent_runtime if latest_tick is not None else None,
    }


def _timings(started_at: float) -> dict[str, float]:
    return {"total_elapsed_seconds": round(time.perf_counter() - started_at, 4)}


def _safety_summary() -> dict[str, Any]:
    return {
        "mobile_secret_policy": "Provider secrets stay on the backend.",
        "raw_media_in_report": False,
        "raw_personal_source_in_report": False,
    }


def _sanitize_report(report: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(_sanitize_value(report)))


def _sanitize_value(value: Any) -> Any:
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
        r"data:[A-Za-z0-9.+-]+/[A-Za-z0-9.+-]+;base64,[A-Za-z0-9+/=_-]+",
        r"file://[^\s,;\"']+",
    ]
    sanitized = message
    for pattern in replacements:
        sanitized = re.sub(pattern, "[redacted]", sanitized, flags=re.IGNORECASE)
    return sanitized
