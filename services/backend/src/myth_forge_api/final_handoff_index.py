from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from myth_forge_api.configured_acceptance_command import (
    CONFIGURED_FINAL_ACCEPTANCE_COMMAND,
    CONFIGURED_FINAL_ACCEPTANCE_COST_REVIEW_ACTION,
)
from myth_forge_api.config import Settings, load_settings
from myth_forge_api.final_configured_preflight import (
    build_final_configured_preflight_report,
)
from myth_forge_api.final_handoff_commands import (
    FINAL_DEMO_LAUNCH_CONFIGURED_COMMAND,
    FINAL_DEMO_LAUNCH_LOCAL_COMMAND,
)
from myth_forge_api.operator_actions import (
    BACKEND_DEVICE_DEMO_VALIDATED_ACTION,
    normalize_operator_action,
    prefer_guarded_print_quote_handoff_actions,
)

LOCAL_REPORT_SOURCES = [
    {
        "id": "three_d_evaluation",
        "path": "services/backend/.local/3d-evaluation-local.json",
        "command": "make backend-evaluate-3d",
    },
    {
        "id": "npc_agent_evaluation",
        "path": "services/backend/.local/npc-evaluation-local.json",
        "command": "make backend-evaluate-npc",
    },
    {
        "id": "visual_regression",
        "path": "services/backend/.local/visual-regression-local.json",
        "command": "make visual-regression-local",
    },
    {
        "id": "final_acceptance_local",
        "path": "services/backend/.local/final-acceptance-local.json",
        "command": "make final-acceptance-local",
    },
    {
        "id": "final_demo_launch_local",
        "path": "services/backend/.local/final-demo-launch-local.json",
        "command": FINAL_DEMO_LAUNCH_LOCAL_COMMAND,
    },
    {
        "id": "ios_deploy_runbook_local",
        "path": "services/backend/.local/ios-deploy-runbook-local.json",
        "command": "make ios-deploy-runbook-local",
    },
]
CONFIGURED_PREFLIGHT_SOURCE = {
    "id": "final_configured_preflight",
    "path": "services/backend/.local/final-configured-preflight.json",
    "command": "make final-configured-preflight",
}
FINAL_HANDOFF_SOURCE_ACTION_PREFIXES = tuple(
    f"{source['id']}: " for source in LOCAL_REPORT_SOURCES
) + (f"{CONFIGURED_PREFLIGHT_SOURCE['id']}: ",)
FINAL_HANDOFF_PROVIDER_ACTION_MARKERS = (
    "make provider-handoff",
    "live-provider-evidence",
    "provider-handoff",
)
FINAL_HANDOFF_PRINT_ACTION_MARKERS = (
    "treatstock",
    "print-quote-configured",
    "print quote",
    "print-quote",
    "print_quote",
    "/v1/print-quotes",
)
FINAL_HANDOFF_LAN_BACKEND_URL_MARKER = "iphone-reachable lan url"
FINAL_HANDOFF_BACKEND_DEVICE_DEMO_MARKER = "backend-device-demo"
FINAL_HANDOFF_SOURCE_OPERATOR_ACTION_LIMIT = 6


@dataclass(frozen=True)
class FinalHandoffIndexResult:
    exit_code: int
    report: dict[str, Any]


def build_final_handoff_index_report(
    *,
    settings: Settings | None = None,
    repo_root: Path | str | None = None,
) -> FinalHandoffIndexResult:
    selected_settings = settings or load_settings()
    selected_repo_root = Path(repo_root) if repo_root is not None else _default_repo_root()
    local_sources = [
        _source_report(source=source, repo_root=selected_repo_root)
        for source in LOCAL_REPORT_SOURCES
    ]
    configured_preflight = build_final_configured_preflight_report(
        settings=selected_settings,
        repo_root=selected_repo_root,
    ).report
    configured_source = _configured_preflight_source(
        repo_root=selected_repo_root,
        computed_report=configured_preflight,
    )
    source_reports = [*local_sources, configured_source]
    lanes = _lanes(
        local_sources=local_sources,
        configured_preflight=configured_preflight,
    )
    status = _overall_status(lanes)
    first_blocker = _first_blocker(lanes)
    device_action_bundle = _device_action_bundle(source_reports)
    report = {
        "kind": "final_handoff_index_report",
        "status": status,
        "summary": _summary(lanes),
        "first_blocker": first_blocker,
        "next_action": _next_action(first_blocker),
        "device_action_bundle": device_action_bundle,
        "lanes": lanes,
        "lanes_by_id": {lane["id"]: lane for lane in lanes},
        "source_reports": source_reports,
        "freshness_summary": _freshness_summary(source_reports),
        "operator_actions": _operator_actions(lanes),
        "operator_sequence": _operator_sequence(lanes),
        "commands": _commands(),
        "safety": _safety(),
    }
    sanitized = _sanitize_report(report, selected_repo_root)
    return FinalHandoffIndexResult(
        exit_code=0 if sanitized["status"] == "ready" else 2,
        report=sanitized,
    )


def _source_report(*, source: dict[str, str], repo_root: Path) -> dict[str, Any]:
    relative_path = source["path"]
    path = repo_root / relative_path
    freshness = _freshness_report(
        repo_root=repo_root,
        source_file=path,
        source_exists=path.exists(),
    )
    base = {
        "id": source["id"],
        "path": relative_path,
        "exists": path.exists(),
        "command": source["command"],
        "freshness": freshness,
    }
    if not path.exists():
        return {
            **base,
            "status": "missing",
            "kind": None,
            "classification": "missing_report",
        }
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {
            **base,
            "status": "blocked",
            "kind": None,
            "classification": "unreadable_report",
        }
    if not isinstance(payload, dict):
        return {
            **base,
            "status": "blocked",
            "kind": None,
            "classification": "invalid_report_shape",
        }
    status = _saved_report_status(payload)
    classification = "saved_report"
    if freshness["status"] == "stale":
        status = "blocked"
        classification = "stale_report"
    report = {
        **base,
        "status": status,
        "kind": payload.get("kind"),
        "classification": classification,
    }
    detail = _saved_report_detail(payload)
    operator_actions = _saved_report_operator_actions(payload)
    if detail:
        report["detail"] = detail
    if operator_actions:
        report["operator_actions"] = operator_actions
    device_action_bundle = payload.get("device_action_bundle")
    if isinstance(device_action_bundle, dict):
        report["device_action_bundle"] = device_action_bundle
    return report


def _configured_preflight_source(
    *,
    repo_root: Path,
    computed_report: dict[str, Any],
) -> dict[str, Any]:
    source = CONFIGURED_PREFLIGHT_SOURCE
    path = repo_root / source["path"]
    report = {
        "id": source["id"],
        "path": source["path"],
        "exists": path.exists(),
        "command": source["command"],
        "status": str(computed_report.get("status", "blocked")),
        "kind": computed_report.get("kind", "final_configured_preflight_report"),
        "classification": "computed_report",
    }
    device_action_bundle = computed_report.get("device_action_bundle")
    if isinstance(device_action_bundle, dict):
        report["device_action_bundle"] = device_action_bundle
    return report


def _saved_report_status(payload: dict[str, Any]) -> str:
    kind = str(payload.get("kind", ""))
    if kind in {"three_d_evaluation_report", "npc_agent_evaluation_report"}:
        return "blocked" if _positive_int(payload.get("failed")) else "ready"
    if kind == "visual_regression_report":
        summary = payload.get("summary", {})
        failed = summary.get("failed") if isinstance(summary, dict) else None
        if str(payload.get("status")) != "passed" or _positive_int(failed):
            return "blocked"
        return "ready"
    if kind == "final_acceptance_report":
        summary = payload.get("summary", {})
        if isinstance(summary, dict) and (
            _positive_int(summary.get("blocked")) or _positive_int(summary.get("failed"))
        ):
            return "blocked"
        return _normalized_status(str(payload.get("overall_status", "ready")))
    if kind == "final_demo_launch_report":
        return _normalized_status(str(payload.get("overall_status", "ready")))
    if kind == "ios_deploy_runbook_report":
        return _normalized_status(str(payload.get("status", "ready")))
    return _normalized_status(str(payload.get("status", "ready")))


def _saved_report_detail(payload: dict[str, Any]) -> str:
    first_blocker = payload.get("first_blocker")
    if isinstance(first_blocker, dict):
        detail = str(first_blocker.get("detail", "")).strip()
        if detail:
            return detail[:240]
    return _first_operator_action(payload)


def _saved_report_operator_actions(payload: dict[str, Any]) -> list[str]:
    next_action = _saved_report_operator_action(payload)
    actions = [next_action] if next_action else []
    actions.extend(_bounded_operator_actions(payload.get("operator_actions")))
    return _dedupe(actions)[:FINAL_HANDOFF_SOURCE_OPERATOR_ACTION_LIMIT]


def _saved_report_operator_action(payload: dict[str, Any]) -> str:
    next_action = payload.get("next_action")
    if isinstance(next_action, dict):
        command = str(next_action.get("command", "")).strip()
        validation_command = str(next_action.get("validation_command", "")).strip()
        if command and validation_command:
            return f"{command}; rerun {validation_command}"[:240]
        if command:
            return command[:240]
    return _first_operator_action(payload)


def _device_action_bundle(source_reports: list[dict[str, Any]]) -> dict[str, Any]:
    source_report, source_bundle = _preferred_device_action_source(source_reports)
    if not isinstance(source_bundle, dict):
        return _missing_device_action_bundle()

    actions = [
        _device_action(action)
        for action in source_bundle.get("actions", [])
        if isinstance(action, dict)
    ]
    return {
        "id": "final_handoff_index_device_actions",
        "label": "Final Handoff Index Device Actions",
        "source_report": source_report,
        "status": _device_action_status(str(source_bundle.get("status", "blocked"))),
        "actions": actions,
        "first_action": _device_first_action(source_bundle.get("first_action"), actions),
        "summary": _device_action_summary(actions),
        "safety": _device_action_safety(),
    }


def _preferred_device_action_source(
    source_reports: list[dict[str, Any]],
) -> tuple[str, dict[str, Any] | None]:
    sources_by_id = {str(source.get("id", "")): source for source in source_reports}
    for source_id in (
        "final_demo_launch_local",
        "ios_deploy_runbook_local",
    ):
        source = sources_by_id.get(source_id)
        if not isinstance(source, dict):
            continue
        bundle = source.get("device_action_bundle")
        if isinstance(bundle, dict):
            return source_id, bundle
    return "missing", None


def _missing_device_action_bundle() -> dict[str, Any]:
    return {
        "id": "final_handoff_index_device_actions",
        "label": "Final Handoff Index Device Actions",
        "source_report": "missing",
        "status": "blocked",
        "actions": [],
        "first_action": None,
        "summary": {
            "actions": 0,
            "ready": 0,
            "missing": 1,
            "blocked": 0,
            "manual": 0,
            "partial": 0,
            "live": 0,
            "provider_calls": 0,
            "global_actions": 0,
            "xcode_or_signing": 0,
        },
        "safety": _device_action_safety(),
    }


def _device_action(action: dict[str, Any]) -> dict[str, Any]:
    copied = {
        "id": str(action.get("id", "device_action")),
        "label": str(action.get("label", action.get("id", "Device action"))),
        "status": _device_action_status(str(action.get("status", "blocked"))),
        "classification": str(action.get("classification", "")),
        "command": str(action.get("command", "")),
        "detail": str(action.get("detail", "")),
        "manual": bool(action.get("manual")),
        "provider_calls": bool(action.get("provider_calls")),
        "global_action": bool(action.get("global_action")),
        "xcode_or_signing": bool(action.get("xcode_or_signing")),
    }
    for optional_field in (
        "blocks",
        "evidence_status",
        "evidence_source",
        "evidence_detail",
        "validation_command",
        "operator_actions",
        "required",
        "requires_consent",
    ):
        if optional_field in action:
            copied[optional_field] = action[optional_field]
    next_action = action.get("next_action")
    if isinstance(next_action, dict):
        copied["next_action"] = _device_next_action(next_action)
    return copied


def _device_next_action(next_action: dict[str, Any]) -> dict[str, Any]:
    copied = {
        "id": str(next_action.get("id", "")),
        "label": str(next_action.get("label", "")),
        "status": str(next_action.get("status", "")),
        "command": str(next_action.get("command", "")),
        "detail": str(next_action.get("detail", "")),
        "source": str(next_action.get("source", "")),
    }
    for optional_field in (
        "classification",
        "validation_command",
        "output",
        "step_id",
        "source_id",
    ):
        if optional_field in next_action:
            copied[optional_field] = str(next_action.get(optional_field, ""))
    return copied


def _device_first_action(
    source_first_action: Any,
    actions: list[dict[str, Any]],
) -> dict[str, Any] | None:
    if isinstance(source_first_action, dict):
        return _device_action(source_first_action)
    for action in actions:
        if action.get("status") != "ready":
            return action
    return actions[0] if actions else None


def _device_action_summary(actions: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "actions": len(actions),
        "ready": sum(1 for action in actions if action["status"] == "ready"),
        "missing": sum(1 for action in actions if action["status"] == "missing"),
        "blocked": sum(1 for action in actions if action["status"] == "blocked"),
        "manual": sum(1 for action in actions if action.get("manual") is True),
        "partial": sum(1 for action in actions if action["status"] == "partial"),
        "live": sum(1 for action in actions if action["status"] == "live"),
        "provider_calls": sum(
            1 for action in actions if action["provider_calls"] is True
        ),
        "global_actions": sum(1 for action in actions if action["global_action"] is True),
        "xcode_or_signing": sum(
            1 for action in actions if action["xcode_or_signing"] is True
        ),
    }


def _device_action_safety() -> dict[str, bool]:
    return {
        "commands_run": False,
        "global_mutation": False,
        "keychain_writes": False,
        "live_provider_calls": False,
        "provider_calls": False,
        "writes_backend_env": False,
        "writes_ios_deploy_config": False,
        "xcode_or_signing": False,
    }


def _device_action_status(status: str) -> str:
    if status in {
        "ready",
        "missing",
        "blocked",
        "manual",
        "partial",
        "live",
    }:
        return status
    if status in {"passed", "succeeded"}:
        return "ready"
    return "blocked"


def _bounded_operator_actions(raw_actions: Any) -> list[str]:
    if not isinstance(raw_actions, list):
        return []
    actions: list[str] = []
    for action in raw_actions:
        if isinstance(action, str) and action.strip():
            actions.append(action.strip()[:240])
    actions = prefer_guarded_print_quote_handoff_actions(actions)
    return _prioritize_final_handoff_operator_actions(
        _dedupe(actions)
    )[:FINAL_HANDOFF_SOURCE_OPERATOR_ACTION_LIMIT]


def _first_operator_action(report: dict[str, Any]) -> str:
    actions = report.get("operator_actions")
    if isinstance(actions, list) and actions:
        action = actions[0]
        if isinstance(action, str):
            return action.strip()[:240]
    return ""


def _lanes(
    *,
    local_sources: list[dict[str, Any]],
    configured_preflight: dict[str, Any],
) -> list[dict[str, Any]]:
    local_status = _combined_lane_status([str(source["status"]) for source in local_sources])
    local_detail = _local_lane_detail(local_sources)
    configured_status = str(configured_preflight.get("status", "blocked"))
    configured_launch_status = str(
        configured_preflight.get("configured_final_launch", {}).get(
            "overall_status",
            "blocked",
        )
    )
    device_deploy_status = str(
        configured_preflight.get("configured_ios_deploy_runbook", {}).get(
            "status",
            "blocked",
        )
    )
    return [
        _lane(
            lane_id="local_rehearsal",
            label="Local rehearsal",
            status=local_status,
            command="make final-rehearsal-local",
            required=True,
            notes=["Writes local/no-key saved reports for final launch review."],
            detail=local_detail,
            operator_action=_local_lane_operator_action(local_sources),
            operator_actions=_local_lane_handoff_actions(local_sources),
        ),
        _lane(
            lane_id="configured_preflight",
            label="Configured preflight",
            status=configured_status,
            command="make final-configured-preflight",
            required=True,
            notes=["Reviews API/key and iOS handoff without live provider calls."],
        ),
        _lane(
            lane_id="configured_launch",
            label="Configured launch report",
            status=configured_launch_status,
            command=FINAL_DEMO_LAUNCH_CONFIGURED_COMMAND,
            required=False,
            notes=["Read-only launch profile for the configured lane."],
        ),
        _lane(
            lane_id="device_deploy",
            label="Device deploy path",
            status=device_deploy_status,
            command="make mobile-deploy-preflight",
            required=False,
            notes=["Backend LAN server, deploy preflight, and Xcode remain operator-run."],
        ),
        _lane(
            lane_id="live_acceptance",
            label="Configured live acceptance",
            status="live",
            command=_configured_acceptance_command(),
            required=False,
            requires_consent=True,
            notes=["May call live providers and spend provider credits."],
        ),
    ]


def _lane(
    *,
    lane_id: str,
    label: str,
    status: str,
    command: str,
    required: bool,
    notes: list[str],
    requires_consent: bool = False,
    detail: str = "",
    operator_action: str = "",
    operator_actions: list[str] | None = None,
) -> dict[str, Any]:
    lane = {
        "id": lane_id,
        "label": label,
        "status": _normalized_status(status),
        "command": command,
        "required": required,
        "requires_consent": requires_consent,
        "notes": notes,
    }
    if detail:
        lane["detail"] = detail
    if operator_action:
        lane["operator_action"] = operator_action
    if operator_actions:
        lane["operator_actions"] = operator_actions
    return lane


def _local_lane_detail(local_sources: list[dict[str, Any]]) -> str:
    preferred = _source_detail_by_id(local_sources, "final_demo_launch_local")
    if preferred:
        return preferred
    for source in local_sources:
        if source.get("status") not in {"blocked", "missing"}:
            continue
        detail = _source_detail(source)
        if detail:
            return detail
    return ""


def _source_detail_by_id(local_sources: list[dict[str, Any]], source_id: str) -> str:
    for source in local_sources:
        if source.get("id") != source_id:
            continue
        return _source_detail(source)
    return ""


def _local_lane_operator_action(local_sources: list[dict[str, Any]]) -> str:
    preferred = _source_operator_action_by_id(local_sources, "final_demo_launch_local")
    if preferred:
        return preferred
    for source in local_sources:
        if source.get("status") not in {"blocked", "missing"}:
            continue
        action = _source_operator_action(source)
        if action:
            return action
    return ""


def _source_operator_action_by_id(
    local_sources: list[dict[str, Any]],
    source_id: str,
) -> str:
    source = _source_by_id(local_sources, source_id)
    return _source_operator_action(source) if source is not None else ""


def _local_lane_handoff_actions(local_sources: list[dict[str, Any]]) -> list[str]:
    source = _source_by_id(local_sources, "final_demo_launch_local")
    if source is None:
        return []
    actions = source.get("operator_actions")
    if not isinstance(actions, list):
        return []
    selected: list[str] = []
    for action in actions:
        if not isinstance(action, str):
            continue
        stripped = action.strip()
        if not (
            _is_provider_handoff_action(stripped)
            or _is_print_handoff_action(stripped)
            or _is_device_handoff_action(stripped)
        ):
            continue
        selected.append(f"final_demo_launch_local: {stripped}")
    return selected


def _source_by_id(
    local_sources: list[dict[str, Any]],
    source_id: str,
) -> dict[str, Any] | None:
    for source in local_sources:
        if source.get("id") == source_id:
            return source
    return None


def _is_provider_handoff_action(action: str) -> bool:
    lowered = action.lower()
    return any(marker in lowered for marker in FINAL_HANDOFF_PROVIDER_ACTION_MARKERS)


def _is_print_handoff_action(action: str) -> bool:
    lowered = action.lower()
    return any(marker in lowered for marker in FINAL_HANDOFF_PRINT_ACTION_MARKERS)


def _is_device_handoff_action(action: str) -> bool:
    return _is_lan_backend_url_action(action) or _is_backend_device_demo_action(action)


def _is_lan_backend_url_action(action: str) -> bool:
    return FINAL_HANDOFF_LAN_BACKEND_URL_MARKER in action.lower()


def _is_backend_device_demo_action(action: str) -> bool:
    return FINAL_HANDOFF_BACKEND_DEVICE_DEMO_MARKER in action.lower()


def _source_detail(source: dict[str, Any]) -> str:
    detail = str(source.get("detail", "")).strip()
    if detail:
        return f"{source['id']}: {detail}"
    actions = source.get("operator_actions")
    if isinstance(actions, list) and actions:
        return f"{source['id']}: {actions[0]}"
    return ""


def _source_operator_action(source: dict[str, Any]) -> str:
    actions = source.get("operator_actions")
    if not isinstance(actions, list):
        return ""
    for action in actions:
        if isinstance(action, str) and action.strip():
            return f"{source['id']}: {action.strip()}"
    return ""


def _operator_sequence(lanes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {lane["id"]: lane for lane in lanes}
    sequence = [
        _sequence_step(
            "local_rehearsal",
            "Run local rehearsal",
            by_id["local_rehearsal"]["status"],
            "make final-rehearsal-local",
            "no-key local report generation",
        ),
        _sequence_step(
            "configured_preflight",
            "Run configured preflight",
            by_id["configured_preflight"]["status"],
            "make final-configured-preflight",
            "read-only API/key and iOS deploy review",
        ),
        _sequence_step(
            "final_handoff_index",
            "Refresh final handoff index",
            "ready",
            "make final-handoff-index",
            "writes this ignored JSON index",
        ),
        _sequence_step(
            "backend_device_server",
            "Start backend on LAN",
            "manual",
            "make backend-device-demo",
            "operator-run backend server for the iPhone",
        ),
        _sequence_step(
            "mobile_deploy_preflight",
            "Run mobile deploy preflight",
            by_id["device_deploy"]["status"],
            "make mobile-deploy-preflight",
            "validates iPhone-reachable backend URL and local deploy config",
        ),
        _sequence_step(
            "configured_final_acceptance",
            "Run configured final acceptance",
            "live",
            _configured_acceptance_command(),
            "requires explicit live provider cost consent",
            requires_consent=True,
        ),
    ]
    return sequence


def _sequence_step(
    step_id: str,
    label: str,
    status: str,
    command: str,
    purpose: str,
    *,
    requires_consent: bool = False,
) -> dict[str, Any]:
    return {
        "id": step_id,
        "label": label,
        "status": _normalized_status(status),
        "command": command,
        "purpose": purpose,
        "requires_consent": requires_consent,
    }


def _commands() -> list[str]:
    return [
        "make final-rehearsal-local",
        "make final-configured-preflight",
        "make final-handoff-index",
        "make backend-device-demo",
        "make mobile-deploy-preflight",
        FINAL_DEMO_LAUNCH_CONFIGURED_COMMAND,
        _configured_acceptance_command(),
    ]


def _configured_acceptance_command() -> str:
    return CONFIGURED_FINAL_ACCEPTANCE_COMMAND


def _overall_status(lanes: list[dict[str, Any]]) -> str:
    required_statuses = [str(lane["status"]) for lane in lanes if lane["required"]]
    if any(status in {"missing", "blocked"} for status in required_statuses):
        return "blocked"
    return "ready"


def _summary(lanes: list[dict[str, Any]]) -> dict[str, int]:
    statuses = ["ready", "missing", "blocked", "manual", "optional", "partial", "live"]
    return {
        status: sum(1 for lane in lanes if lane["status"] == status)
        for status in statuses
    }


def _operator_actions(lanes: list[dict[str, Any]]) -> list[str]:
    actions: list[str] = []
    for lane in lanes:
        status = str(lane.get("status", ""))
        if status not in {"missing", "blocked", "manual", "live"}:
            continue
        lane_id = str(lane.get("id", "lane"))
        command = str(lane.get("command", ""))
        if lane_id == "local_rehearsal":
            actions.append(
                _lane_operator_action_or_default(
                    lane,
                    _lane_detail_or_default(lane, "run make final-rehearsal-local"),
                )
            )
            nested_actions = lane.get("operator_actions")
            if isinstance(nested_actions, list):
                actions.extend(str(action) for action in nested_actions)
        elif lane_id == "configured_preflight":
            actions.append("run make final-configured-preflight")
        elif lane_id == "device_deploy":
            actions.append(BACKEND_DEVICE_DEMO_VALIDATED_ACTION)
        elif lane_id == "live_acceptance":
            actions.append(CONFIGURED_FINAL_ACCEPTANCE_COST_REVIEW_ACTION)
        elif command:
            actions.append(f"run {command}")
        else:
            actions.append(f"unblock {lane_id}")
    deduped = _dedupe(_final_handoff_operator_action(action) for action in actions)
    deduped = prefer_guarded_print_quote_handoff_actions(deduped)
    return _prioritize_final_handoff_operator_actions(deduped)[:6]


def _prioritize_final_handoff_operator_actions(actions: list[str]) -> list[str]:
    if not actions:
        return []
    first_actions = actions[:1]
    rest = actions[1:]
    lan_backend_url_actions = [
        action for action in rest if _is_lan_backend_url_action(action)
    ]
    backend_device_demo_actions = [
        action for action in rest if _is_backend_device_demo_action(action)
    ]
    if _is_mobile_deploy_handoff_action(first_actions[0]):
        device_actions = [
            *backend_device_demo_actions,
            *lan_backend_url_actions,
        ]
    else:
        device_actions = [
            *lan_backend_url_actions,
            *(backend_device_demo_actions if lan_backend_url_actions else []),
        ]
    provider_actions = [
        action for action in rest if _is_provider_handoff_action(action)
    ]
    print_actions = [action for action in rest if _is_print_handoff_action(action)]
    priority_actions = set(device_actions + provider_actions + print_actions)
    remaining = [action for action in rest if action not in priority_actions]
    return first_actions + device_actions + provider_actions + print_actions + remaining


def _is_mobile_deploy_handoff_action(action: str) -> bool:
    root, _detail_suffix = _split_detail_suffix(action)
    return (
        "rerun make mobile-deploy-preflight" in root
        and not _is_backend_device_demo_action(root)
        and "mobile-xcode-build" not in root
    )


def _final_handoff_operator_action(action: str) -> str:
    normalized = normalize_operator_action(action)
    if normalized == CONFIGURED_FINAL_ACCEPTANCE_COST_REVIEW_ACTION:
        return normalized
    command_part, detail_suffix = _split_detail_suffix(normalized)
    bare_root = _strip_final_handoff_source_prefixes(command_part)
    if bare_root.startswith("run make "):
        return f"{bare_root.removeprefix('run ')}{detail_suffix}"
    if bare_root != command_part:
        return f"{bare_root}{detail_suffix}"
    return f"{command_part}{detail_suffix}"


def _split_detail_suffix(action: str) -> tuple[str, str]:
    command, separator, detail = action.partition(" | ")
    if not separator:
        return action.strip(), ""
    return command.strip(), f"{separator}{detail}"


def _strip_final_handoff_source_prefixes(command: str) -> str:
    stripped = command.strip()
    changed = True
    while changed:
        changed = False
        for prefix in FINAL_HANDOFF_SOURCE_ACTION_PREFIXES:
            if stripped.startswith(prefix):
                stripped = stripped.removeprefix(prefix).strip()
                changed = True
    return stripped


def _first_blocker(lanes: list[dict[str, Any]]) -> dict[str, Any] | None:
    for lane in lanes:
        status = str(lane.get("status", ""))
        if status not in {"missing", "blocked"}:
            continue
        lane_id = str(lane.get("id", "lane"))
        command = str(lane.get("command", ""))
        return {
            "id": lane_id,
            "label": str(lane.get("label", lane_id)),
            "status": status,
            "classification": f"lane_{status}",
            "command": command,
            "detail": _lane_blocker_detail(lane),
        }
    return None


def _next_action(first_blocker: dict[str, Any] | None) -> dict[str, Any] | None:
    if first_blocker is None:
        return None
    next_action = {**first_blocker, "source": "first_blocker"}
    validation_command = _validation_command_for_blocker(first_blocker)
    if validation_command:
        next_action["validation_command"] = validation_command
    return next_action


def _validation_command_for_blocker(blocker: dict[str, Any]) -> str | None:
    command = str(blocker.get("command", "")).strip()
    if command.startswith("make "):
        return command
    return None


def _lane_blocker_detail(lane: dict[str, Any]) -> str:
    lane_id = str(lane.get("id", "lane"))
    command = str(lane.get("command", ""))
    if lane_id == "local_rehearsal":
        return _lane_detail_or_default(lane, "run make final-rehearsal-local")
    if lane_id == "configured_preflight":
        return "run make final-configured-preflight"
    if lane_id == "device_deploy":
        return BACKEND_DEVICE_DEMO_VALIDATED_ACTION
    return f"run {command}" if command else f"unblock {lane_id}"


def _lane_detail_or_default(lane: dict[str, Any], default: str) -> str:
    detail = str(lane.get("detail", "")).strip()
    return detail or default


def _lane_operator_action_or_default(lane: dict[str, Any], default: str) -> str:
    action = str(lane.get("operator_action", "")).strip()
    return action or default


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        deduped.append(value)
    return deduped


def _combined_lane_status(statuses: list[str]) -> str:
    normalized = [_normalized_status(status) for status in statuses]
    if "missing" in normalized:
        return "missing"
    if "blocked" in normalized:
        return "blocked"
    return "ready"


def _normalized_status(status: str) -> str:
    if status in {"ready", "missing", "blocked", "manual", "optional", "partial", "live"}:
        return status
    if status in {"passed", "succeeded"}:
        return "ready"
    if status in {"failed", "error"}:
        return "blocked"
    return "blocked"


def _positive_int(value: Any) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, int) and value > 0:
        return value
    return 0


def _freshness_report(
    *,
    repo_root: Path,
    source_file: Path,
    source_exists: bool,
) -> dict[str, Any]:
    if not source_exists:
        return _freshness_payload(
            status="unknown",
            classification="source_missing",
            source_modified_at=None,
            git_metadata=None,
        )
    source_modified_at = source_file.stat().st_mtime
    git_metadata = _git_head_metadata(repo_root)
    if git_metadata is None:
        return _freshness_payload(
            status="unknown",
            classification="git_unavailable",
            source_modified_at=source_modified_at,
            git_metadata=None,
        )
    freshness_status = (
        "stale"
        if source_modified_at < git_metadata["committed_at_epoch"]
        else "fresh"
    )
    return _freshness_payload(
        status=freshness_status,
        classification="stale_report" if freshness_status == "stale" else "fresh_report",
        source_modified_at=source_modified_at,
        git_metadata=git_metadata,
    )


def _git_head_metadata(repo_root: Path) -> dict[str, Any] | None:
    try:
        revision = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "--short", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            timeout=2,
        ).stdout.strip()
        committed_at = subprocess.run(
            ["git", "-C", str(repo_root), "log", "-1", "--format=%ct", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            timeout=2,
        ).stdout.strip()
    except (subprocess.SubprocessError, OSError):
        return None
    try:
        committed_at_epoch = float(committed_at)
    except ValueError:
        return None
    return {
        "revision": revision or None,
        "committed_at_epoch": committed_at_epoch,
    }


def _freshness_payload(
    *,
    status: str,
    classification: str,
    source_modified_at: float | None,
    git_metadata: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "status": status,
        "classification": classification,
        "checked_against": "git_head",
        "source_modified_at": _iso_timestamp(source_modified_at),
        "current_revision": None if git_metadata is None else git_metadata["revision"],
        "current_revision_committed_at": None
        if git_metadata is None
        else _iso_timestamp(git_metadata["committed_at_epoch"]),
    }


def _iso_timestamp(epoch: float | None) -> str | None:
    if epoch is None:
        return None
    return (
        datetime.fromtimestamp(epoch, tz=timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _freshness_summary(source_reports: list[dict[str, Any]]) -> dict[str, int]:
    statuses = ["fresh", "stale", "unknown"]
    return {
        status: sum(
            1
            for source in source_reports
            if source.get("freshness", {}).get("status") == status
        )
        for status in statuses
    }


def _safety() -> dict[str, bool]:
    return {
        "commands_run": False,
        "provider_calls": False,
        "writes_local_config": False,
        "writes_backend_env": False,
        "writes_ios_deploy_config": False,
        "global_mutation": False,
        "xcode_or_signing": False,
        "keychain_writes": False,
        "provider_secrets_in_report": False,
        "raw_media_in_report": False,
        "payment_links_in_report": False,
        "local_paths_in_report": False,
    }


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _sanitize_report(report: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    return json.loads(json.dumps(_sanitize_value(report, repo_root)))


def _sanitize_value(value: Any, repo_root: Path) -> Any:
    if isinstance(value, str):
        return _safe_text(value, repo_root)
    if isinstance(value, list):
        return [_sanitize_value(item, repo_root) for item in value]
    if isinstance(value, dict):
        return {key: _sanitize_value(item, repo_root) for key, item in value.items()}
    return value


def _safe_text(message: str, repo_root: Path) -> str:
    sanitized = message
    patterns = [
        r"sk-[A-Za-z0-9._-]+",
        r"Bearer\s+[A-Za-z0-9._~+/\-=:-]+",
        r"api[_-]?key\s*[=:]\s*[^\s,;\"']+",
        r"data:[A-Za-z0-9.+-]+/[A-Za-z0-9+/=_-]+",
        r"local-capture://[^\s,;\"']+",
        r"file://[^\s,;\"']+",
        r"https?://pay\.[^\s,;\"']+",
        r"https?://checkout\.[^\s,;\"']+",
        r"checkout_url",
        r"raw_email:[^\n\r]+",
        r"raw_calendar:[^\n\r]+",
        r"private_message:[^\n\r]+",
        r"raw_context:[^\n\r]+",
        r"message_body:[^\n\r]+",
    ]
    for pattern in patterns:
        sanitized = re.sub(pattern, "[redacted]", sanitized, flags=re.IGNORECASE)
    root_text = str(repo_root)
    if root_text:
        sanitized = sanitized.replace(root_text, "[repo-root]")
    home_text = str(Path.home())
    if home_text:
        sanitized = sanitized.replace(home_text, "[home]")
    return sanitized
