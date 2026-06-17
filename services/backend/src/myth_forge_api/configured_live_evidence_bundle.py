from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from myth_forge_api.config import Settings, load_settings
from myth_forge_api.final_configured_evidence_plan import (
    build_final_configured_evidence_plan_report,
)
from myth_forge_api.live_provider_evidence import build_live_provider_evidence_report
from myth_forge_api.operator_actions import normalize_operator_action


@dataclass(frozen=True)
class ConfiguredLiveEvidenceBundleResult:
    exit_code: int
    report: dict[str, Any]


def build_configured_live_evidence_bundle_report(
    *,
    repo_root: Path | str | None = None,
    settings: Settings | None = None,
    allow_live_provider_calls: bool = False,
) -> ConfiguredLiveEvidenceBundleResult:
    selected_repo_root = Path(repo_root) if repo_root is not None else _default_repo_root()
    selected_settings = settings or load_settings()
    configured_plan = build_final_configured_evidence_plan_report(
        repo_root=selected_repo_root,
        settings=selected_settings,
        allow_live_provider_calls=allow_live_provider_calls,
    ).report
    live_evidence = build_live_provider_evidence_report(
        repo_root=selected_repo_root,
    ).report
    evidence_files = _evidence_files(live_evidence)
    command_sequence = _command_sequence(configured_plan)
    status = _bundle_status(configured_plan=configured_plan, live_evidence=live_evidence)
    current_blocker = _current_blocker(
        status=status,
        configured_plan=configured_plan,
        live_evidence=live_evidence,
        command_sequence=command_sequence,
    )
    first_blocker = current_blocker
    report = {
        "kind": "configured_live_evidence_bundle_report",
        "status": status,
        "summary": _summary(
            configured_plan=configured_plan,
            live_evidence=live_evidence,
            command_sequence=command_sequence,
            evidence_files=evidence_files,
        ),
        "current_blocker": current_blocker,
        "first_blocker": first_blocker,
        "next_action": _next_action(first_blocker),
        "device_action_bundle": _device_action_bundle(configured_plan),
        "evidence_files": evidence_files,
        "evidence_files_by_id": {row["id"]: row for row in evidence_files},
        "command_sequence": command_sequence,
        "command_sequence_by_id": {row["id"]: row for row in command_sequence},
        "operator_actions": _operator_actions(
            status=status,
            current_blocker=current_blocker,
            configured_plan=configured_plan,
            live_evidence=live_evidence,
        ),
        "source_reports": {
            "final_configured_evidence_plan": _source_summary(configured_plan),
            "live_provider_evidence": _source_summary(live_evidence),
        },
        "commands": _commands(configured_plan=configured_plan, live_evidence=live_evidence),
        "live_call_policy": {
            "bundle_calls_live_providers": False,
            "live_calls_by_default": False,
            "allow_live_provider_calls": allow_live_provider_calls,
            "consent_flag": "--allow-live-provider-calls",
            "consent_required_for": configured_plan.get("live_call_policy", {}).get(
                "consent_required_for",
                [],
            ),
        },
        "safety": _safety(),
    }
    sanitized = _sanitize_report(report, selected_repo_root)
    return ConfiguredLiveEvidenceBundleResult(
        exit_code=0 if sanitized["status"] == "ready" else 2,
        report=sanitized,
    )


def _bundle_status(
    *,
    configured_plan: dict[str, Any],
    live_evidence: dict[str, Any],
) -> str:
    live_status = str(live_evidence.get("status", "blocked"))
    if live_status in {"blocked", "partial"}:
        return "blocked"
    plan_status = str(configured_plan.get("status", "blocked"))
    if plan_status in {"ready", "ready_to_run", "consent_required", "blocked"}:
        return plan_status
    return "blocked"


def _evidence_files(live_evidence: dict[str, Any]) -> list[dict[str, Any]]:
    rows = live_evidence.get("evidence", [])
    if not isinstance(rows, list):
        return []
    return [_evidence_row(row) for row in rows if isinstance(row, dict)]


def _evidence_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(row.get("id", "")),
        "label": str(row.get("label", "")),
        "path": str(row.get("path", "")),
        "status": str(row.get("status", "missing")),
        "classification": str(row.get("classification", "")),
        "expected_kind": str(row.get("expected_kind", "")),
        "command": str(row.get("command", "")),
        "requires_live_provider_consent": bool(
            row.get("requires_live_provider_consent", False)
        ),
        "detail": str(row.get("detail", "")),
    }


def _command_sequence(configured_plan: dict[str, Any]) -> list[dict[str, Any]]:
    rows = configured_plan.get("steps", [])
    if not isinstance(rows, list):
        return []
    return [_command_row(row) for row in rows if isinstance(row, dict)]


def _command_row(row: dict[str, Any]) -> dict[str, Any]:
    result = {
        "id": str(row.get("id", "")),
        "label": str(row.get("label", "")),
        "status": str(row.get("status", "blocked")),
        "command": str(row.get("command", "")),
        "requires_live_provider_consent": bool(
            row.get("requires_live_provider_consent", False)
        ),
        "may_call_live_provider": bool(row.get("may_call_live_provider", False)),
        "cost_risk": bool(row.get("cost_risk", False)),
        "repo_local_write": bool(row.get("repo_local_write", False)),
        "would_write_backend_env": bool(row.get("would_write_backend_env", False)),
        "would_write_ios_deploy_config": bool(
            row.get("would_write_ios_deploy_config", False)
        ),
        "blocked_by": _string_list(row.get("blocked_by")),
    }
    for key in ("evidence_status", "evidence_path", "evidence_detail"):
        if key in row:
            result[key] = str(row[key])
    return result


def _current_blocker(
    *,
    status: str,
    configured_plan: dict[str, Any],
    live_evidence: dict[str, Any],
    command_sequence: list[dict[str, Any]],
) -> dict[str, Any] | None:
    if status in {"ready", "ready_to_run"}:
        return None

    live_status = str(live_evidence.get("status", "blocked"))
    if live_status in {"blocked", "partial"}:
        first_blocker = live_evidence.get("first_blocker")
        if isinstance(first_blocker, dict):
            return _live_blocker(first_blocker, live_evidence.get("next_action"))

    for step_status in ("blocked", "consent_required"):
        for row in command_sequence:
            if row["status"] == step_status:
                return {
                    "id": row["id"],
                    "label": row["label"],
                    "status": row["status"],
                    "command": row["command"],
                    "blocked_by": row["blocked_by"],
                    "detail": _step_detail(row, configured_plan),
                }

    return None


def _live_blocker(
    first_blocker: dict[str, Any],
    next_action: Any = None,
) -> dict[str, Any]:
    blocker = {
        "id": str(first_blocker.get("id", "")),
        "label": str(first_blocker.get("label", "")),
        "status": str(first_blocker.get("status", "blocked")),
        "classification": str(first_blocker.get("classification", "")),
        "command": str(first_blocker.get("command", "")),
        "detail": str(first_blocker.get("detail", "")),
    }
    if isinstance(next_action, dict):
        command = str(next_action.get("command", "")).strip()
        if command:
            blocker["command"] = command
        validation_command = str(next_action.get("validation_command", "")).strip()
        if validation_command:
            blocker["validation_command"] = validation_command
    return blocker


def _next_action(first_blocker: dict[str, Any] | None) -> dict[str, Any] | None:
    if first_blocker is None:
        return None
    return {**first_blocker, "source": "first_blocker"}


def _step_detail(row: dict[str, Any], configured_plan: dict[str, Any]) -> str:
    if row["status"] == "consent_required":
        return "Live provider cost consent is required before this command."
    if row["blocked_by"]:
        return "Blocked by " + ", ".join(row["blocked_by"])
    actions = configured_plan.get("operator_actions")
    if isinstance(actions, list) and actions:
        return str(actions[0])
    return "Step is not ready."


def _summary(
    *,
    configured_plan: dict[str, Any],
    live_evidence: dict[str, Any],
    command_sequence: list[dict[str, Any]],
    evidence_files: list[dict[str, Any]],
) -> dict[str, int]:
    evidence_statuses = [row["status"] for row in evidence_files]
    command_statuses = [row["status"] for row in command_sequence]
    plan_summary = configured_plan.get("summary", {})
    return {
        "evidence_files": len(evidence_files),
        "evidence_ready": evidence_statuses.count("ready"),
        "evidence_missing": evidence_statuses.count("missing"),
        "evidence_blocked": evidence_statuses.count("blocked"),
        "evidence_partial": evidence_statuses.count("partial"),
        "commands": len(command_sequence),
        "commands_ready": command_statuses.count("ready"),
        "commands_ready_to_run": command_statuses.count("ready_to_run"),
        "blocked_steps": command_statuses.count("blocked"),
        "consent_required_steps": command_statuses.count("consent_required"),
        "live_provider_steps": _non_negative_int(plan_summary.get("live_provider_steps")),
        "cost_steps": _non_negative_int(plan_summary.get("cost_steps")),
        "repo_local_write_steps": _non_negative_int(
            plan_summary.get("repo_local_write_steps")
        ),
        "commands_run": 0,
        "source_live_evidence_ready": 1
        if str(live_evidence.get("status")) == "ready"
        else 0,
    }


def _source_summary(report: dict[str, Any]) -> dict[str, Any]:
    summary = {
        "kind": report.get("kind", "unknown"),
        "status": report.get("status", report.get("overall_status", "unknown")),
        "summary": report.get("summary", {}),
        "first_blocker": report.get("first_blocker"),
    }
    device_action_bundle = report.get("device_action_bundle")
    if isinstance(device_action_bundle, dict):
        summary["device_action_bundle"] = device_action_bundle
    return summary


def _operator_actions(
    *,
    status: str,
    current_blocker: dict[str, Any] | None,
    configured_plan: dict[str, Any],
    live_evidence: dict[str, Any],
) -> list[str]:
    if status == "ready":
        return []
    actions: list[str] = []
    if current_blocker is not None:
        blocker_status = str(current_blocker.get("status", "blocked"))
        blocker_id = str(current_blocker.get("id", "unknown"))
        blocker_command = str(current_blocker.get("command", "")).strip()
        if blocker_command.startswith("PMF_ALLOW_LIVE_PROVIDER_CALLS=1 "):
            actions.append(blocker_command)
        elif blocker_status == "consent_required":
            actions.append(f"review live provider cost consent before {blocker_id}")
        else:
            actions.append(f"unblock {blocker_id} before configured evidence bundle")
    elif status == "ready_to_run":
        actions.append("run configured evidence commands in order")
    actions.extend(
        _without_shadowed_live_blocker_actions(
            _string_list(configured_plan.get("operator_actions")),
            live_evidence=live_evidence,
        )
    )
    actions.extend(_string_list(live_evidence.get("operator_actions")))
    return _prefer_live_provider_consent_action(_dedupe_operator_actions(actions))[:12]


def _without_shadowed_live_blocker_actions(
    actions: list[str],
    *,
    live_evidence: dict[str, Any],
) -> list[str]:
    if str(live_evidence.get("status", "blocked")) not in {"blocked", "partial"}:
        return actions

    first_blocker = live_evidence.get("first_blocker")
    next_action = live_evidence.get("next_action")
    if not isinstance(first_blocker, dict) or not isinstance(next_action, dict):
        return actions

    source_command = str(first_blocker.get("command", "")).strip()
    replacement_command = str(next_action.get("command", "")).strip()
    if (
        not source_command
        or not replacement_command
        or source_command == replacement_command
    ):
        return actions

    shadowed_command = normalize_operator_action(source_command)
    return [
        action
        for action in actions
        if normalize_operator_action(action) != shadowed_command
    ]


def _commands(
    *,
    configured_plan: dict[str, Any],
    live_evidence: dict[str, Any],
) -> list[str]:
    commands: list[str] = []
    commands.extend(_string_list(configured_plan.get("commands")))
    commands.extend(_string_list(live_evidence.get("commands")))
    commands.append("make configured-live-evidence-bundle")
    return _dedupe(commands)


def _safety() -> dict[str, bool]:
    return {
        "commands_run": False,
        "provider_calls": False,
        "live_provider_calls": False,
        "writes_backend_env": False,
        "writes_ios_deploy_config": False,
        "global_mutation": False,
        "xcode_or_signing": False,
        "keychain_writes": False,
        "provider_secrets_in_report": False,
        "raw_private_context_in_report": False,
        "raw_media_in_report": False,
        "payment_links_in_report": False,
        "local_paths_in_report": False,
    }


def _device_action_bundle(configured_plan: dict[str, Any]) -> dict[str, Any]:
    source_bundle = configured_plan.get("device_action_bundle")
    if not isinstance(source_bundle, dict):
        return _missing_device_action_bundle()

    actions = [
        _device_action(action)
        for action in source_bundle.get("actions", [])
        if isinstance(action, dict)
    ]
    return {
        "id": "configured_live_evidence_bundle_device_actions",
        "label": "Configured Live Evidence Bundle Device Actions",
        "source_report": "final_configured_evidence_plan",
        "status": _device_action_status(str(source_bundle.get("status", "blocked"))),
        "actions": actions,
        "first_action": _device_first_action(source_bundle.get("first_action"), actions),
        "summary": _device_action_summary(actions),
        "safety": _device_action_safety(),
    }


def _missing_device_action_bundle() -> dict[str, Any]:
    return {
        "id": "configured_live_evidence_bundle_device_actions",
        "label": "Configured Live Evidence Bundle Device Actions",
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
    return "blocked"


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _non_negative_int(value: Any) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return 0
    return max(parsed, 0)


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def _dedupe_operator_actions(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        normalized = normalize_operator_action(value)
        if normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result


LIVE_PROVIDER_CONSENT_ACTION_MARKER = (
    "PMF_ALLOW_LIVE_PROVIDER_CALLS=1 make final-acceptance-configured; "
    "rerun make live-provider-evidence"
)
CONFIGURED_PLAN_CONSENT_ACTION_MARKERS = (
    (
        "PMF_ALLOW_LIVE_PROVIDER_CALLS=1 make backend-evaluate-3d-configured; "
        "rerun make final-configured-evidence-plan"
    ),
    (
        "PMF_ALLOW_LIVE_PROVIDER_CALLS=1 make backend-evaluate-npc-configured; "
        "rerun make final-configured-evidence-plan"
    ),
    (
        "PMF_ALLOW_LIVE_PROVIDER_CALLS=1 make final-acceptance-configured; "
        "rerun make final-configured-evidence-plan"
    ),
)
LIVE_PROVIDER_FALLBACK_ACTION_ROOTS = {
    "make backend-evaluate-3d-configured",
    "make backend-evaluate-npc-configured",
    "make final-acceptance-configured",
    "make final-demo-launch-configured",
    "make live-provider-evidence",
    "make provider-handoff",
    "unblock final_configured_preflight after provider_handoff",
}


def _prefer_live_provider_consent_action(actions: list[str]) -> list[str]:
    if any(_is_configured_plan_consent_action(action) for action in actions):
        return [
            action
            for action in actions
            if _is_configured_plan_consent_action(action)
            or not (
                _is_live_provider_consent_action(action)
                or _is_live_provider_fallback_action(action)
            )
        ]
    if not any(_is_live_provider_consent_action(action) for action in actions):
        return actions
    return [
        action
        for action in actions
        if _is_live_provider_consent_action(action)
        or not _is_live_provider_fallback_action(action)
    ]


def _is_live_provider_consent_action(action: str) -> bool:
    return normalize_operator_action(action) == LIVE_PROVIDER_CONSENT_ACTION_MARKER


def _is_configured_plan_consent_action(action: str) -> bool:
    return normalize_operator_action(action) in CONFIGURED_PLAN_CONSENT_ACTION_MARKERS


def _is_live_provider_fallback_action(action: str) -> bool:
    normalized = normalize_operator_action(action)
    if normalized in LIVE_PROVIDER_FALLBACK_ACTION_ROOTS:
        return True
    return normalized.startswith("review live provider cost consent before ")


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
        r"meshy-secret-[A-Za-z0-9._-]+",
        r"Bearer\s+[A-Za-z0-9._~+/\-=:-]+",
        r"Authorization\s+Bearer\s+[A-Za-z0-9._~+/\-=:-]+",
        r"api[_-]?key\s*[=:]\s*[^\s,;\"']+",
        r"data:[A-Za-z0-9.+-]+/[A-Za-z0-9.+-]+;base64,[A-Za-z0-9+/=_-]+",
        r"https?://pay\.[^\s,;\"']+",
        r"https?://checkout\.[^\s,;\"']+",
        r"checkout_url",
        r"file://[^\s,;\"']+",
        r"/private/[^\s,;\"']+",
        r"/tmp/[^\s,;\"']+",
        r"/Users/[^\s,;\"']+",
        r"https?://10\.[^\s,;\"'`]+",
        r"https?://192\.168\.[^\s,;\"'`]+",
        r"https?://172\.(?:1[6-9]|2[0-9]|3[01])\.[^\s,;\"'`]+",
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


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parents[4]
