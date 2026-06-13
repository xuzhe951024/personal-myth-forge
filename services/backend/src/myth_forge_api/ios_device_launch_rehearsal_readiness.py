from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from myth_forge_api.operator_actions import (
    add_final_resource_validation_command,
    add_mobile_deploy_validation_command,
    normalize_operator_action,
    prefer_project_local_ios_deploy_handoff_actions,
)
from myth_forge_api.source_freshness import (
    freshness_payload,
    git_product_source_metadata,
)

DEFAULT_IOS_DEVICE_LAUNCH_REHEARSAL_PATH = Path(
    "services/backend/.local/ios-device-launch-rehearsal.json"
)
IOS_DEVICE_LAUNCH_REHEARSAL_COMMAND = "make ios-device-launch-rehearsal"
IOS_DEVICE_LAUNCH_REHEARSAL_RERUN_ACTION = (
    "rerun make ios-device-launch-rehearsal to regenerate "
    "services/backend/.local/ios-device-launch-rehearsal.json for the current product sources"
)
IOS_DEVICE_LAUNCH_REHEARSAL_ACTION_LIMIT = 20


@dataclass(frozen=True)
class IOSDeviceLaunchRehearsalReadinessResult:
    exit_code: int
    report: dict[str, Any]


def build_ios_device_launch_rehearsal_readiness_report(
    *,
    repo_root: Path | str | None = None,
    rehearsal_file: Path | str | None = None,
) -> IOSDeviceLaunchRehearsalReadinessResult:
    selected_repo_root = Path(repo_root) if repo_root is not None else _default_repo_root()
    selected_rehearsal_file = (
        Path(rehearsal_file)
        if rehearsal_file is not None
        else selected_repo_root / DEFAULT_IOS_DEVICE_LAUNCH_REHEARSAL_PATH
    )
    source_file = {
        "path": _path_label(path=selected_rehearsal_file, repo_root=selected_repo_root),
        "exists": selected_rehearsal_file.exists(),
    }
    freshness = _freshness_report(
        repo_root=selected_repo_root,
        rehearsal_file=selected_rehearsal_file,
        source_exists=selected_rehearsal_file.exists(),
    )
    if not selected_rehearsal_file.exists():
        return IOSDeviceLaunchRehearsalReadinessResult(
            exit_code=2,
            report=_base_report(
                repo_root=selected_repo_root,
                status="missing",
                source_file=source_file,
                freshness=freshness,
                summary=_empty_summary(),
                sequence=[],
                operator_actions=[f"run {IOS_DEVICE_LAUNCH_REHEARSAL_COMMAND}"],
                commands=_commands([]),
                blockers=[],
                saved_safety={},
            ),
        )

    try:
        saved_report = json.loads(selected_rehearsal_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _blocked_result(
            repo_root=selected_repo_root,
            source_file=source_file,
            freshness=freshness,
            classification="unreadable_report",
            detail="Saved iOS device launch rehearsal report is not valid JSON.",
        )

    if not isinstance(saved_report, dict):
        return _blocked_result(
            repo_root=selected_repo_root,
            source_file=source_file,
            freshness=freshness,
            classification="invalid_report_shape",
            detail="Saved iOS device launch rehearsal report must be a JSON object.",
        )

    if saved_report.get("kind") != "ios_device_launch_rehearsal_report":
        return _blocked_result(
            repo_root=selected_repo_root,
            source_file=source_file,
            freshness=freshness,
            classification="wrong_report_kind",
            detail="Saved report is not an ios_device_launch_rehearsal_report.",
        )

    status = _normalized_status(str(saved_report.get("status", "blocked")))
    blockers: list[dict[str, Any]] = []
    if freshness["status"] == "stale":
        status = "blocked"
        blockers.append(_freshness_blocker(freshness))
    report = _base_report(
        repo_root=selected_repo_root,
        status=status,
        source_file=source_file,
        freshness=freshness,
        summary=_summary(saved_report.get("summary")),
        sequence=_sequence(saved_report.get("sequence")),
        operator_actions=_operator_actions(
            saved_report.get("operator_actions"),
            freshness=freshness,
        ),
        commands=_commands(saved_report.get("commands")),
        blockers=blockers,
        saved_safety=saved_report.get("safety"),
    )
    return IOSDeviceLaunchRehearsalReadinessResult(
        exit_code=0 if status in {"ready", "partial"} else 2,
        report=report,
    )


def _blocked_result(
    *,
    repo_root: Path,
    source_file: dict[str, Any],
    freshness: dict[str, Any],
    classification: str,
    detail: str,
) -> IOSDeviceLaunchRehearsalReadinessResult:
    return IOSDeviceLaunchRehearsalReadinessResult(
        exit_code=2,
        report=_base_report(
            repo_root=repo_root,
            status="blocked",
            source_file=source_file,
            freshness=freshness,
            summary=_empty_summary(),
            sequence=[],
            operator_actions=[f"rerun {IOS_DEVICE_LAUNCH_REHEARSAL_COMMAND}"],
            commands=_commands([]),
            blockers=[
                {
                    "id": "ios_device_launch_rehearsal_file",
                    "label": "iOS device launch rehearsal file",
                    "status": "failed",
                    "classification": classification,
                    "command": IOS_DEVICE_LAUNCH_REHEARSAL_COMMAND,
                    "detail": detail,
                }
            ],
            saved_safety={},
        ),
    )


def _base_report(
    *,
    repo_root: Path,
    status: str,
    source_file: dict[str, Any],
    freshness: dict[str, Any],
    summary: dict[str, int],
    sequence: list[dict[str, Any]],
    operator_actions: list[str],
    commands: list[str],
    blockers: list[dict[str, Any]],
    saved_safety: Any,
) -> dict[str, Any]:
    first_blocker = _first_blocker(blockers=blockers, sequence=sequence)
    next_action = _next_action(
        first_blocker=first_blocker,
        operator_actions=operator_actions,
    )
    device_action_bundle = _device_action_bundle(
        status=status,
        sequence=sequence,
        operator_actions=operator_actions,
    )
    report = {
        "kind": "ios_device_launch_rehearsal_readiness_report",
        "status": status,
        "source_file": source_file,
        "freshness": freshness,
        "summary": summary,
        "sequence": sequence,
        "blockers": blockers,
        "first_blocker": first_blocker,
        "next_action": next_action,
        "device_action_bundle": device_action_bundle,
        "operator_actions": operator_actions,
        "commands": commands,
        "safety": _safety(saved_safety),
    }
    return _sanitize_report(report, repo_root)


def _first_blocker(
    *,
    blockers: list[dict[str, Any]],
    sequence: list[dict[str, Any]],
) -> dict[str, Any] | None:
    if blockers:
        blocker = dict(blockers[0])
        blocker["source"] = "blockers"
        return blocker
    for row in sequence:
        if str(row.get("status", "")).strip().lower() == "ready":
            continue
        return {
            "id": str(row.get("id", "unknown")),
            "label": str(row.get("label", row.get("id", "Unknown"))),
            "status": str(row.get("status", "blocked")),
            "classification": str(row.get("classification", "saved_report")),
            "command": str(row.get("command", IOS_DEVICE_LAUNCH_REHEARSAL_COMMAND)),
            "detail": str(row.get("detail", "")),
            "source": "sequence",
        }
    return None


def _next_action(
    *,
    first_blocker: dict[str, Any] | None,
    operator_actions: list[str],
) -> dict[str, Any] | None:
    if first_blocker is None:
        return None
    next_action = {**first_blocker, "source": "first_blocker"}
    if operator_actions:
        next_action["command"] = _structured_next_action_command(operator_actions[0])
    return next_action


def _structured_next_action_command(action: str) -> str:
    command, _separator, _detail = action.partition(" | ")
    return command.strip()


def _device_action_bundle(
    *,
    status: str,
    sequence: list[dict[str, Any]],
    operator_actions: list[str],
) -> dict[str, Any]:
    first_operator_action = operator_actions[0] if operator_actions else None
    actions = [
        _device_action(
            row,
            command_override=first_operator_action if index == 0 else None,
        )
        for index, row in enumerate(sequence)
    ]
    if not actions:
        actions = [
            _device_action(
                {
                    "id": "run_ios_device_launch_rehearsal",
                    "label": "Run iOS device launch rehearsal",
                    "status": "missing",
                    "classification": "missing_saved_report",
                    "command": IOS_DEVICE_LAUNCH_REHEARSAL_COMMAND,
                    "detail": (
                        "Regenerate the saved iOS device launch rehearsal report."
                    ),
                },
                command_override=None,
            )
        ]
    return {
        "id": "ios_device_launch_rehearsal_readiness_actions",
        "label": "iOS Device Launch Rehearsal Readiness Actions",
        "source_report": "ios_device_launch_rehearsal_readiness",
        "status": status,
        "actions": actions,
        "first_action": _first_device_action(actions),
        "summary": _device_action_summary(actions),
        "safety": {
            "commands_run": False,
            "global_mutation": False,
            "keychain_writes": False,
            "live_provider_calls": False,
            "provider_calls": False,
            "writes_backend_env": False,
            "writes_ios_deploy_config": False,
            "xcode_or_signing": False,
        },
    }


def _device_action(
    row: dict[str, Any],
    *,
    command_override: str | None,
) -> dict[str, Any]:
    action_status = str(row.get("status", "blocked"))
    command = (
        _structured_next_action_command(command_override)
        if command_override
        else str(row.get("command", IOS_DEVICE_LAUNCH_REHEARSAL_COMMAND))
    )
    action: dict[str, Any] = {
        "id": str(row.get("id", "device_action")),
        "label": str(row.get("label", row.get("id", "Device action"))),
        "status": action_status,
        "classification": str(row.get("classification", "saved_report")),
        "command": command,
        "detail": str(row.get("detail", "")),
        "source": "ios_device_launch_rehearsal_readiness",
        "blocks": ["ios_deployable", "functional_regression"],
        "manual": action_status != "ready",
        "provider_calls": False,
        "global_action": False,
        "xcode_or_signing": _is_xcode_or_signing_action(row),
        "validation_command": IOS_DEVICE_LAUNCH_REHEARSAL_COMMAND,
    }
    if action_status != "ready":
        action["next_action"] = {
            "id": action["id"],
            "label": action["label"],
            "status": action["status"],
            "command": action["command"],
            "detail": action["detail"],
            "source": "device_action_bundle",
            "validation_command": action["validation_command"],
        }
    return action


def _first_device_action(actions: list[dict[str, Any]]) -> dict[str, Any] | None:
    return next(
        (action for action in actions if action["status"] != "ready"),
        actions[0] if actions else None,
    )


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
        "global_actions": sum(
            1 for action in actions if action["global_action"] is True
        ),
        "xcode_or_signing": sum(
            1 for action in actions if action["xcode_or_signing"] is True
        ),
    }


def _is_xcode_or_signing_action(row: dict[str, Any]) -> bool:
    text = " ".join(
        [
            str(row.get("id", "")),
            str(row.get("classification", "")),
            str(row.get("command", "")),
            str(row.get("detail", "")),
        ]
    ).lower()
    return "xcode" in text or "signing" in text


def _summary(raw_summary: Any) -> dict[str, int]:
    if not isinstance(raw_summary, dict):
        return _empty_summary()
    return {
        "ready": _non_negative_int(raw_summary.get("ready")),
        "missing": _non_negative_int(raw_summary.get("missing")),
        "blocked": _non_negative_int(raw_summary.get("blocked")),
        "partial": _non_negative_int(raw_summary.get("partial")),
        "manual": _non_negative_int(raw_summary.get("manual")),
        "live": _non_negative_int(raw_summary.get("live")),
    }


def _empty_summary() -> dict[str, int]:
    return {
        "ready": 0,
        "missing": 0,
        "blocked": 0,
        "partial": 0,
        "manual": 0,
        "live": 0,
    }


def _sequence(raw_sequence: Any) -> list[dict[str, Any]]:
    if not isinstance(raw_sequence, list):
        return []
    rows: list[dict[str, Any]] = []
    for raw_step in raw_sequence:
        if not isinstance(raw_step, dict):
            continue
        row = {
            "id": str(raw_step.get("id", "unknown")),
            "label": str(raw_step.get("label", raw_step.get("id", "Unknown"))),
            "status": _normalized_status(str(raw_step.get("status", "blocked"))),
            "command": str(raw_step.get("command", IOS_DEVICE_LAUNCH_REHEARSAL_COMMAND)),
            "classification": str(raw_step.get("classification", "saved_report")),
        }
        if isinstance(raw_step.get("detail"), str) and raw_step["detail"]:
            row["detail"] = str(raw_step["detail"])
        freshness_summary = _bounded_freshness_summary(
            raw_step.get("freshness_summary")
        )
        if freshness_summary is not None:
            row["freshness_summary"] = freshness_summary
        if isinstance(raw_step.get("freshness_status"), str):
            row["freshness_status"] = str(raw_step["freshness_status"])
        if isinstance(raw_step.get("freshness_classification"), str):
            row["freshness_classification"] = str(
                raw_step["freshness_classification"]
            )
        rows.append(row)
    return rows[:8]


def _operator_actions(
    raw_actions: Any,
    *,
    freshness: dict[str, Any] | None = None,
) -> list[str]:
    if freshness is not None and freshness["status"] == "stale":
        existing_actions = (
            [
                _validation_aware_operator_action(str(action))
                for action in raw_actions
                if isinstance(action, str) and action
            ]
            if isinstance(raw_actions, list)
            else []
        )
        actions = _dedupe([IOS_DEVICE_LAUNCH_REHEARSAL_RERUN_ACTION, *existing_actions])
        return prefer_project_local_ios_deploy_handoff_actions(actions)[
            :IOS_DEVICE_LAUNCH_REHEARSAL_ACTION_LIMIT
        ]
    if not isinstance(raw_actions, list):
        return [f"run {IOS_DEVICE_LAUNCH_REHEARSAL_COMMAND}"]
    actions = [
        _validation_aware_operator_action(str(action))
        for action in raw_actions
        if isinstance(action, str) and action
    ]
    deduped = prefer_project_local_ios_deploy_handoff_actions(_dedupe(actions))
    return (
        deduped[:IOS_DEVICE_LAUNCH_REHEARSAL_ACTION_LIMIT]
        or [f"run {IOS_DEVICE_LAUNCH_REHEARSAL_COMMAND}"]
    )


def _commands(raw_commands: Any) -> list[str]:
    commands = [IOS_DEVICE_LAUNCH_REHEARSAL_COMMAND]
    if isinstance(raw_commands, list):
        commands.extend(command for command in raw_commands if isinstance(command, str))
    commands.append(
        (
            "cd services/backend && uv run python -m myth_forge_api.cli "
            "ios-device-launch-rehearsal --repo-root ../.. "
            "--output .local/ios-device-launch-rehearsal.json"
        )
    )
    return _dedupe(commands)


def _validation_aware_operator_action(action: str) -> str:
    return add_final_resource_validation_command(
        add_mobile_deploy_validation_command(normalize_operator_action(action))
    )


def _safety(raw_safety: Any) -> dict[str, bool]:
    saved = raw_safety if isinstance(raw_safety, dict) else {}
    return {
        "commands_run": False,
        "provider_calls": _bool(saved.get("provider_calls")),
        "live_provider_calls": _bool(saved.get("live_provider_calls")),
        "writes_backend_env": _bool(saved.get("writes_backend_env")),
        "writes_ios_deploy_config": _bool(saved.get("writes_ios_deploy_config")),
        "global_mutation": _bool(saved.get("global_mutation")),
        "xcode_or_signing": _bool(saved.get("xcode_or_signing")),
        "keychain_writes": _bool(saved.get("keychain_writes")),
        "provider_secrets_in_report": _bool(saved.get("provider_secrets_in_report")),
        "raw_media_in_report": _bool(saved.get("raw_media_in_report")),
        "payment_links_in_report": _bool(saved.get("payment_links_in_report")),
        "local_paths_in_report": _bool(saved.get("local_paths_in_report")),
    }


def _normalized_status(status: str) -> str:
    normalized = status.strip().lower()
    if normalized in {"ready", "missing", "blocked", "partial"}:
        return normalized
    if normalized in {"manual", "live"}:
        return "partial"
    if normalized in {"passed", "succeeded"}:
        return "ready"
    return "blocked"


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


def _bool(value: Any) -> bool:
    return value is True


def _freshness_report(
    *,
    repo_root: Path,
    rehearsal_file: Path,
    source_exists: bool,
) -> dict[str, Any]:
    if not source_exists:
        return _freshness_payload(
            status="unknown",
            classification="source_missing",
            source_modified_at=None,
            git_metadata=None,
            checked_against="git_head",
        )
    source_modified_at = rehearsal_file.stat().st_mtime
    git_metadata = git_product_source_metadata(repo_root)
    if git_metadata is None:
        return _freshness_payload(
            status="unknown",
            classification="git_unavailable",
            source_modified_at=source_modified_at,
            git_metadata=None,
            checked_against="git_product_sources",
        )
    freshness_status = (
        "stale"
        if source_modified_at < git_metadata.committed_at_epoch
        else "fresh"
    )
    return _freshness_payload(
        status=freshness_status,
        classification="stale_report" if freshness_status == "stale" else "fresh_report",
        source_modified_at=source_modified_at,
        git_metadata=git_metadata,
        checked_against="git_product_sources",
    )


def _freshness_payload(
    *,
    status: str,
    classification: str,
    source_modified_at: float | None,
    git_metadata: Any,
    checked_against: str,
) -> dict[str, Any]:
    return freshness_payload(
        status=status,
        classification=classification,
        source_modified_at=source_modified_at,
        git_metadata=git_metadata,
        checked_against=checked_against,
    )


def _freshness_blocker(freshness: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": "ios_device_launch_rehearsal_freshness",
        "label": "iOS device launch rehearsal freshness",
        "status": "blocked",
        "classification": str(freshness["classification"]),
        "command": IOS_DEVICE_LAUNCH_REHEARSAL_COMMAND,
        "detail": (
            "Saved iOS device launch rehearsal report is older than the current "
            "product sources."
        ),
    }


def _path_label(*, path: Path, repo_root: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return _safe_text(str(path), repo_root)


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
