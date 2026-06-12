from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from myth_forge_api.configured_acceptance_command import (
    CONFIGURED_FINAL_ACCEPTANCE_COST_REVIEW_ACTION,
)
from myth_forge_api.operator_actions import (
    BACKEND_DEVICE_DEMO_VALIDATED_ACTION,
    DEPLOYMENT_TEAM_VALIDATED_ACTION,
    FINAL_RESOURCE_APPLY_ACTION,
    IOS_DEPLOY_CONFIG_VALIDATED_ACTION,
    MOBILE_WRITE_DEPLOY_CONFIG_AUTO_VALIDATED_ACTION,
    add_final_resource_validation_command,
    add_mobile_deploy_validation_command,
    normalize_operator_action,
    prefer_project_local_ios_deploy_handoff_actions,
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
        "command": "make final-demo-launch",
    },
    {
        "id": "ios_deploy_runbook_local",
        "path": "services/backend/.local/ios-deploy-runbook-local.json",
        "command": "make ios-deploy-runbook-local",
    },
    {
        "id": "mobile_deploy_preflight_evidence",
        "path": "services/backend/.local/mobile-deploy-preflight-evidence.json",
        "command": "make mobile-deploy-preflight-evidence",
    },
]

REHEARSAL_REPORT_SOURCES = [
    {
        "id": "final_configured_preflight",
        "path": "services/backend/.local/final-configured-preflight.json",
        "command": "make final-configured-preflight",
    },
    {
        "id": "final_handoff_index",
        "path": "services/backend/.local/final-handoff-index.json",
        "command": "make final-handoff-index",
    },
    {
        "id": "ios_device_launch_certificate",
        "path": "services/backend/.local/ios-device-launch-certificate.json",
        "command": "make ios-device-launch-certificate",
    },
]
IOS_REHEARSAL_SOURCE_ACTION_PREFIXES = (
    "final_rehearsal_local: ",
    *(f"{source['id']}: " for source in LOCAL_REPORT_SOURCES),
    *(f"{source['id']}: " for source in REHEARSAL_REPORT_SOURCES),
)
IOS_REHEARSAL_PROVIDER_HANDOFF_ACTION_MARKERS = (
    "make provider-handoff",
    "live-provider-evidence",
    "provider-handoff",
)
IOS_REHEARSAL_PRINT_HANDOFF_ACTION_MARKERS = (
    "treatstock",
    "print-quote-configured",
    "print quote",
    "print-quote",
    "print_quote",
    "/v1/print-quotes",
)


@dataclass(frozen=True)
class IOSDeviceLaunchRehearsalResult:
    exit_code: int
    report: dict[str, Any]


def build_ios_device_launch_rehearsal_report(
    *,
    repo_root: Path | str | None = None,
) -> IOSDeviceLaunchRehearsalResult:
    selected_repo_root = Path(repo_root) if repo_root is not None else _default_repo_root()
    local_sources = [
        _source_report(source=source, repo_root=selected_repo_root)
        for source in LOCAL_REPORT_SOURCES
    ]
    final_rehearsal_local = _final_rehearsal_local(local_sources)
    report_sources = {
        source["id"]: _source_report(source=source, repo_root=selected_repo_root)
        for source in REHEARSAL_REPORT_SOURCES
    }
    sequence = _sequence_with_details(
        [
            final_rehearsal_local,
            report_sources["final_configured_preflight"],
            report_sources["final_handoff_index"],
            report_sources["ios_device_launch_certificate"],
        ]
    )
    status = _overall_status(sequence)
    mode = _mode_from_certificate(report_sources["ios_device_launch_certificate"])
    first_blocker = _first_blocker(sequence)
    operator_actions = _operator_actions(sequence)
    report = {
        "kind": "ios_device_launch_rehearsal_report",
        "status": status,
        "mode": mode,
        "summary": _summary(sequence),
        "first_blocker": first_blocker,
        "next_action": _next_action(
            first_blocker=first_blocker,
            operator_actions=operator_actions,
        ),
        "sequence": sequence,
        "local_rehearsal_reports": local_sources,
        "configured_preflight": report_sources["final_configured_preflight"],
        "final_handoff_index": report_sources["final_handoff_index"],
        "ios_device_launch_certificate": report_sources[
            "ios_device_launch_certificate"
        ],
        "operator_actions": operator_actions,
        "commands": _commands(),
        "safety": _safety(),
    }
    sanitized = _sanitize_report(report, selected_repo_root)
    return IOSDeviceLaunchRehearsalResult(
        exit_code=0 if sanitized["status"] in {"ready", "partial"} else 2,
        report=sanitized,
    )


def _final_rehearsal_local(local_sources: list[dict[str, Any]]) -> dict[str, Any]:
    status = _combined_status([str(source["status"]) for source in local_sources])
    step = {
        "id": "final_rehearsal_local",
        "label": "Local final rehearsal",
        "status": status,
        "path": "services/backend/.local/",
        "exists": all(source["exists"] for source in local_sources),
        "command": "make final-rehearsal-local",
        "kind": "local_rehearsal_report_set",
        "classification": "saved_report_set",
        "reports": [
            _compact_source(source)
            for source in local_sources
        ],
    }
    actions = _local_rehearsal_operator_actions(local_sources)
    if actions:
        step["operator_actions"] = actions
    return step


def _local_rehearsal_operator_actions(
    local_sources: list[dict[str, Any]],
) -> list[str]:
    actions: list[str] = []
    mobile_preflight_detail = _blocked_mobile_preflight_detail(local_sources)
    for source in local_sources:
        status = str(source["status"])
        if status == "missing":
            actions.append(f"refresh {source['id']}: {source['command']}")
            continue
        if status != "blocked":
            continue
        detail = source.get("detail")
        if isinstance(detail, str) and detail.strip():
            actions.append(
                _validation_aware_operator_action(f"{source['id']}: {detail.strip()}")
            )
            if len(actions) >= 6:
                break
            continue
        nested_actions = source.get("operator_actions")
        if isinstance(nested_actions, list) and nested_actions:
            for action in nested_actions:
                actions.append(
                    _local_rehearsal_action(
                        source_id=str(source["id"]),
                        action=str(action),
                        mobile_preflight_detail=mobile_preflight_detail,
                    )
                )
        else:
            actions.append(f"review {source['id']}: {source['command']}")
        if len(actions) >= 6:
            break
    return _dedupe(actions)[:6]


def _blocked_mobile_preflight_detail(local_sources: list[dict[str, Any]]) -> str:
    for source in local_sources:
        if source.get("id") != "mobile_deploy_preflight_evidence":
            continue
        if source.get("status") != "blocked":
            continue
        detail = source.get("detail")
        if isinstance(detail, str) and detail.strip():
            return detail.strip()
    return ""


def _local_rehearsal_action(
    *,
    source_id: str,
    action: str,
    mobile_preflight_detail: str,
) -> str:
    if (
        mobile_preflight_detail
        and source_id != "mobile_deploy_preflight_evidence"
        and _is_mobile_preflight_action(action)
    ):
        return normalize_operator_action(
            f"mobile_deploy_preflight_evidence: {mobile_preflight_detail}"
        )
    return _validation_aware_operator_action(f"{source_id}: {action}")


def _is_mobile_preflight_action(action: str) -> bool:
    normalized = action.lower().replace("-", " ")
    return "mobile deploy preflight" in normalized


def _source_report(*, source: dict[str, str], repo_root: Path) -> dict[str, Any]:
    relative_path = source["path"]
    path = repo_root / relative_path
    base = {
        "id": source["id"],
        "label": _label(source["id"]),
        "path": relative_path,
        "exists": path.exists(),
        "command": source["command"],
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
    report = {
        **base,
        "status": _saved_report_status(payload),
        "kind": payload.get("kind"),
        "classification": "saved_report",
        "mode": payload.get("mode"),
        "summary": payload.get("summary", {}),
    }
    nested_actions = _bounded_operator_actions(
        payload.get("operator_actions"),
        repo_root=repo_root,
    )
    if nested_actions:
        report["operator_actions"] = nested_actions
    evidence_detail = _mobile_preflight_evidence_detail(payload)
    if evidence_detail:
        report["detail"] = evidence_detail
    freshness_summary = _bounded_freshness_summary(payload.get("freshness_summary"))
    if freshness_summary is not None:
        report["freshness_summary"] = freshness_summary
        report["freshness_status"] = _freshness_status(freshness_summary)
        report["freshness_classification"] = _freshness_classification(
            str(report["freshness_status"])
        )
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
    if kind == "mobile_deploy_preflight_evidence_report":
        return _normalized_status(str(payload.get("status", "blocked")))
    if kind in {
        "ios_deploy_runbook_report",
        "final_configured_preflight_report",
        "final_handoff_index_report",
        "ios_device_launch_certificate_report",
    }:
        return _normalized_status(str(payload.get("status", "ready")))
    return _normalized_status(str(payload.get("status", "ready")))


def _sequence_with_details(sequence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    preferred_sequence = _prefer_sequence_ios_deploy_handoff_actions(sequence)
    rows: list[dict[str, Any]] = []
    for step in preferred_sequence:
        row = dict(step)
        if row.get("status") in {"missing", "blocked"}:
            row["detail"] = _step_blocker_detail(row)
        rows.append(row)
    return rows


def _prefer_sequence_ios_deploy_handoff_actions(
    sequence: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not _sequence_has_ios_deploy_writer(sequence):
        return sequence
    rows: list[dict[str, Any]] = []
    for step in sequence:
        nested_actions = step.get("operator_actions")
        if not isinstance(nested_actions, list):
            rows.append(step)
            continue
        preferred_actions = _prefer_nested_ios_deploy_handoff_actions(nested_actions)
        row = dict(step)
        if preferred_actions:
            row["operator_actions"] = preferred_actions
        else:
            row.pop("operator_actions", None)
        rows.append(row)
    return rows


def _sequence_has_ios_deploy_writer(sequence: list[dict[str, Any]]) -> bool:
    return any(
        _top_level_action_root(str(action))
        == MOBILE_WRITE_DEPLOY_CONFIG_AUTO_VALIDATED_ACTION
        for step in sequence
        for action in step.get("operator_actions", [])
        if isinstance(action, str)
    )


def _prefer_nested_ios_deploy_handoff_actions(actions: list[Any]) -> list[str]:
    preferred: list[str] = []
    writer_index: int | None = None
    old_roots = {
        DEPLOYMENT_TEAM_VALIDATED_ACTION,
        IOS_DEPLOY_CONFIG_VALIDATED_ACTION,
    }
    for action in actions:
        if not isinstance(action, str) or not action.strip():
            continue
        root = _top_level_action_root(action)
        if root in old_roots:
            continue
        if root != MOBILE_WRITE_DEPLOY_CONFIG_AUTO_VALIDATED_ACTION:
            if action not in preferred:
                preferred.append(action)
            continue
        if writer_index is None:
            writer_index = len(preferred)
            preferred.append(action)
            continue
        if " | " in action and " | " not in preferred[writer_index]:
            preferred[writer_index] = action
    return preferred


def _top_level_action_root(action: str) -> str:
    command, _detail_suffix = _split_detail_suffix(_top_level_operator_action(action))
    return command


def _overall_status(sequence: list[dict[str, Any]]) -> str:
    statuses = [str(step["status"]) for step in sequence]
    if "missing" in statuses or "blocked" in statuses:
        return "blocked"
    if any(status in {"partial", "manual", "live"} for status in statuses):
        return "partial"
    certificate = next(
        (step for step in sequence if step["id"] == "ios_device_launch_certificate"),
        {},
    )
    summary = certificate.get("summary", {})
    if isinstance(summary, dict) and any(
        _positive_int(summary.get(status)) for status in ["manual", "live", "partial"]
    ):
        return "partial"
    return "ready"


def _summary(sequence: list[dict[str, Any]]) -> dict[str, int]:
    statuses = ["ready", "missing", "blocked", "partial", "manual", "live"]
    return {
        status: sum(1 for step in sequence if step["status"] == status)
        for status in statuses
    }


def _operator_actions(sequence: list[dict[str, Any]]) -> list[str]:
    if any(step["status"] == "missing" for step in sequence):
        actions = ["run make ios-device-launch-rehearsal"]
        for step in sequence:
            if step["status"] == "missing":
                actions.append(f"refresh {step['id']}: {step['command']}")
        return _dedupe(actions)

    actions: list[str] = []
    for step in sequence:
        if step["status"] != "blocked":
            continue
        nested_actions = step.get("operator_actions")
        if isinstance(nested_actions, list) and nested_actions:
            actions.extend(
                _validation_aware_operator_action(f"{step['id']}: {action}")
                for action in nested_actions
            )
        else:
            actions.append(f"review {step['id']}: {step['command']}")
    if actions:
        return _prioritize_rehearsal_handoff_actions(
            prefer_project_local_ios_deploy_handoff_actions(
                _dedupe(_top_level_operator_action(action) for action in actions)
            )
        )

    if all(step["status"] not in {"missing", "blocked"} for step in sequence):
        actions.append("continue with make backend-device-demo")
        actions.append(BACKEND_DEVICE_DEMO_VALIDATED_ACTION)
    return _prioritize_rehearsal_handoff_actions(
        prefer_project_local_ios_deploy_handoff_actions(
            _dedupe(_top_level_operator_action(action) for action in actions)
        )
    )


def _prioritize_rehearsal_handoff_actions(actions: list[str]) -> list[str]:
    if not actions:
        return []
    first_actions = actions[:1]
    rest = actions[1:]
    provider_actions = [
        action for action in rest if _is_provider_handoff_action(action)
    ]
    print_actions = [action for action in rest if _is_print_handoff_action(action)]
    priority_actions = set(provider_actions + print_actions)
    remaining = [action for action in rest if action not in priority_actions]
    return first_actions + provider_actions + print_actions + remaining


def _is_provider_handoff_action(action: str) -> bool:
    lowered = action.lower()
    return any(
        marker in lowered
        for marker in IOS_REHEARSAL_PROVIDER_HANDOFF_ACTION_MARKERS
    )


def _is_print_handoff_action(action: str) -> bool:
    lowered = action.lower()
    return any(
        marker in lowered
        for marker in IOS_REHEARSAL_PRINT_HANDOFF_ACTION_MARKERS
    )


def _top_level_operator_action(action: str) -> str:
    normalized = _validation_aware_operator_action(action)
    command_part, detail_suffix = _split_detail_suffix(normalized)
    bare_root = _strip_rehearsal_source_prefixes(command_part)
    if bare_root == CONFIGURED_FINAL_ACCEPTANCE_COST_REVIEW_ACTION:
        return f"{bare_root}{detail_suffix}"
    if bare_root == FINAL_RESOURCE_APPLY_ACTION:
        return f"make final-apply-resources{detail_suffix}"
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


def _strip_rehearsal_source_prefixes(command: str) -> str:
    stripped = command.strip()
    changed = True
    while changed:
        changed = False
        for prefix in IOS_REHEARSAL_SOURCE_ACTION_PREFIXES:
            if stripped.startswith(prefix):
                stripped = stripped.removeprefix(prefix).strip()
                changed = True
    return stripped


def _first_blocker(sequence: list[dict[str, Any]]) -> dict[str, Any] | None:
    for step in sequence:
        status = str(step.get("status", ""))
        if status not in {"missing", "blocked"}:
            continue
        step_id = str(step.get("id", "step"))
        command = str(step.get("command", ""))
        return {
            "id": step_id,
            "label": str(step.get("label", step_id)),
            "status": status,
            "classification": f"step_{status}",
            "command": command,
            "detail": _step_blocker_detail(step),
        }
    return None


def _next_action(
    *,
    first_blocker: dict[str, Any] | None,
    operator_actions: list[str],
) -> dict[str, Any] | None:
    if first_blocker is None:
        return None
    for action in operator_actions:
        if action == "run make ios-device-launch-rehearsal":
            continue
        if action.startswith("refresh "):
            continue
        return {
            **first_blocker,
            "command": action,
            "source": "operator_actions",
            "validation_command": "make ios-device-launch-rehearsal",
        }
    return {
        **first_blocker,
        "source": "first_blocker",
        "validation_command": "make ios-device-launch-rehearsal",
    }


def _step_blocker_detail(step: dict[str, Any]) -> str:
    if step.get("status") == "missing":
        return "run make ios-device-launch-rehearsal"
    nested_actions = step.get("operator_actions")
    if isinstance(nested_actions, list) and nested_actions:
        return _validation_aware_operator_action(f"{step['id']}: {nested_actions[0]}")
    command = str(step.get("command", ""))
    return f"review {step['id']}: {command}" if command else f"review {step['id']}"


def _commands() -> list[str]:
    return [
        "make ios-device-launch-rehearsal",
        "make final-rehearsal-local",
        "make final-configured-preflight",
        "make final-handoff-index",
        "make ios-device-launch-certificate",
        (
            "cd services/backend && uv run python -m myth_forge_api.cli "
            "ios-device-launch-rehearsal --repo-root ../.. "
            "--output .local/ios-device-launch-rehearsal.json"
        ),
    ]


def _mode_from_certificate(certificate: dict[str, Any]) -> str:
    mode = certificate.get("mode")
    return str(mode) if mode in {"local", "configured"} else "local"


def _compact_source(source: dict[str, Any]) -> dict[str, Any]:
    return {
        key: source[key]
        for key in [
            "id",
            "status",
            "path",
            "exists",
            "kind",
            "command",
            "freshness",
            "freshness_summary",
            "freshness_status",
            "freshness_classification",
            "detail",
            "operator_actions",
        ]
        if key in source
    }


def _combined_status(statuses: list[str]) -> str:
    normalized = [_normalized_status(status) for status in statuses]
    if "missing" in normalized:
        return "missing"
    if "blocked" in normalized:
        return "blocked"
    if "partial" in normalized:
        return "partial"
    return "ready"


def _normalized_status(status: str) -> str:
    if status in {"ready", "missing", "blocked", "partial", "manual", "live"}:
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


def _non_negative_int(value: Any) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, int) and value >= 0:
        return value
    return 0


def _bounded_freshness_summary(raw_summary: Any) -> dict[str, int] | None:
    if not isinstance(raw_summary, dict):
        return None
    return {
        "fresh": _non_negative_int(raw_summary.get("fresh")),
        "stale": _non_negative_int(raw_summary.get("stale")),
        "unknown": _non_negative_int(raw_summary.get("unknown")),
    }


def _bounded_operator_actions(raw_actions: Any, *, repo_root: Path) -> list[str]:
    if not isinstance(raw_actions, list):
        return []
    actions: list[str] = []
    for action in raw_actions:
        if isinstance(action, str):
            actions.append(
                _validation_aware_operator_action(
                    _clean_action(action, repo_root=repo_root)
                )
            )
        if len(actions) == 4:
            break
    return [action for action in actions if action]


def _mobile_preflight_evidence_detail(payload: dict[str, Any]) -> str:
    if payload.get("kind") != "mobile_deploy_preflight_evidence_report":
        return ""
    checks = payload.get("checks")
    if not isinstance(checks, list):
        return ""
    details: list[str] = []
    for check in checks:
        if not isinstance(check, dict):
            continue
        if str(check.get("status", "")) not in {"blocked", "missing"}:
            continue
        detail = str(check.get("detail", "")).strip()
        if detail:
            details.append(detail[:120])
    return "; ".join(_dedupe(details))[:240]


def _clean_action(action: str, *, repo_root: Path) -> str:
    return _safe_text(action.strip(), repo_root)[:180]


def _validation_aware_operator_action(action: str) -> str:
    return add_final_resource_validation_command(
        add_mobile_deploy_validation_command(normalize_operator_action(action))
    )


def _freshness_status(summary: dict[str, int]) -> str:
    if summary["stale"]:
        return "stale"
    if summary["unknown"] and not summary["fresh"]:
        return "unknown"
    return "fresh"


def _freshness_classification(status: str) -> str:
    if status == "stale":
        return "stale_report"
    if status == "unknown":
        return "unknown_report_freshness"
    return "fresh_report"


def _label(source_id: str) -> str:
    return source_id.replace("_", " ").capitalize()


def _safety() -> dict[str, bool]:
    return {
        "report_builder_commands_run": False,
        "make_wrapper_runs_commands": True,
        "writes_ignored_reports": True,
        "provider_calls": False,
        "live_provider_calls": False,
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
        r"data:[A-Za-z0-9.+-]+/[A-Za-z0-9.+-]+;base64,[A-Za-z0-9+/=_-]+",
        r"local-capture://[^\s,;\"']+",
        r"file://[^\s,;\"']+",
        r"https?://pay\.[^\s,;\"']+",
        r"https?://checkout\.[^\s,;\"']+",
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


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parents[4]
