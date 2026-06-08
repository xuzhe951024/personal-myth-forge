from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from myth_forge_api.config import Settings, load_settings
from myth_forge_api.final_acceptance_readiness import (
    LOCAL_FINAL_ACCEPTANCE_COMMAND,
    build_final_acceptance_readiness_report,
)
from myth_forge_api.final_external_action_ledger import (
    build_final_external_action_ledger_report,
)
from myth_forge_api.final_resource_fill_guide import (
    build_final_resource_fill_guide_report,
)
from myth_forge_api.final_showcase_readiness import (
    build_final_showcase_readiness_report,
)
from myth_forge_api.ios_device_evidence_bundle import (
    build_ios_device_evidence_bundle_report,
)
from myth_forge_api.operator_actions import normalize_operator_action

COMMANDS = [
    "make final-resource-fill-guide",
    "make final-external-action-ledger",
    "make ios-device-launch-rehearsal",
    "make live-provider-evidence",
    "make final-showcase-readiness",
    "make final-acceptance-local",
]


@dataclass(frozen=True)
class FinalLaunchClosurePacketResult:
    exit_code: int
    report: dict[str, Any]


def build_final_launch_closure_packet_report(
    *,
    settings: Settings | None = None,
    repo_root: Path | str | None = None,
) -> FinalLaunchClosurePacketResult:
    selected_settings = settings or load_settings()
    selected_repo_root = Path(repo_root) if repo_root is not None else _default_repo_root()
    fill_guide = build_final_resource_fill_guide_report(
        repo_root=selected_repo_root,
    ).report
    action_ledger = build_final_external_action_ledger_report(
        settings=selected_settings,
        repo_root=selected_repo_root,
    ).report
    device_evidence = build_ios_device_evidence_bundle_report(
        repo_root=selected_repo_root,
    ).report
    showcase_readiness = build_final_showcase_readiness_report(
        settings=selected_settings,
        repo_root=selected_repo_root,
    ).report
    final_acceptance = build_final_acceptance_readiness_report(
        repo_root=selected_repo_root,
    ).report
    sections = _sections(
        fill_guide=fill_guide,
        action_ledger=action_ledger,
        device_evidence=device_evidence,
        showcase_readiness=showcase_readiness,
        final_acceptance=final_acceptance,
    )
    status = _overall_status(sections)
    report = {
        "kind": "final_launch_closure_packet_report",
        "status": status,
        "summary": _summary(sections),
        "sections": sections,
        "sections_by_id": {section["id"]: section for section in sections},
        "operator_actions": _operator_actions(sections),
        "commands": COMMANDS,
        "source_reports": {
            "final_resource_fill_guide": _source_summary(fill_guide),
            "final_external_action_ledger": _source_summary(action_ledger),
            "ios_device_evidence_bundle": _source_summary(device_evidence),
            "final_showcase_readiness": _source_summary(showcase_readiness),
            "final_acceptance_readiness": _source_summary(final_acceptance),
        },
        "safety": _safety(),
    }
    sanitized = _sanitize_report(report, selected_repo_root)
    return FinalLaunchClosurePacketResult(
        exit_code=0 if sanitized["status"] == "ready" else 2,
        report=sanitized,
    )


def _sections(
    *,
    fill_guide: dict[str, Any],
    action_ledger: dict[str, Any],
    device_evidence: dict[str, Any],
    showcase_readiness: dict[str, Any],
    final_acceptance: dict[str, Any],
) -> list[dict[str, Any]]:
    groups = {
        str(group.get("id", "")): group
        for group in action_ledger.get("action_groups", [])
        if isinstance(group, dict)
    }
    return [
        _ledger_section(
            section_id="resource_inputs",
            label="Resource inputs",
            command="make final-resource-fill-guide",
            detail=_resource_inputs_detail(fill_guide),
            group=groups.get("resource_inputs", {}),
            required=True,
        ),
        _ledger_section(
            section_id="safe_local_writes",
            label="Safe local writes",
            command="make final-resource-apply-preview",
            detail="Preview and apply ignored backend/iOS local resource files.",
            group=groups.get("safe_local_writes", {}),
            required=True,
        ),
        _device_section(device_evidence),
        _ledger_section(
            section_id="live_provider_consent",
            label="Live provider consent",
            command="make live-provider-evidence",
            detail="Run Meshy, OpenAI, and print-provider evidence only after cost consent.",
            group=groups.get("live_provider_costs", {}),
            required=False,
        ),
        _final_acceptance_section(
            showcase_readiness=showcase_readiness,
            final_acceptance=final_acceptance,
        ),
    ]


def _ledger_section(
    *,
    section_id: str,
    label: str,
    command: str,
    detail: str,
    group: dict[str, Any],
    required: bool,
) -> dict[str, Any]:
    raw_actions = group.get("actions", [])
    actions = [
        _compact_ledger_action(action)
        for action in raw_actions
        if isinstance(action, dict)
    ]
    if not actions:
        actions = [
            _closure_action(
                action_id=f"{section_id}_missing",
                label=label,
                status="missing",
                command=command,
                detail=f"{label} source action group is missing.",
                required=required,
            )
        ]
    return _section(
        section_id=section_id,
        label=label,
        status=str(group.get("status", "missing")),
        command=command,
        detail=detail,
        required=required,
        actions=actions,
        blocked_by=_blocked_by(actions),
    )


def _compact_ledger_action(action: dict[str, Any]) -> dict[str, Any]:
    return _closure_action(
        action_id=str(action.get("id", "unknown_action")),
        label=str(action.get("label", action.get("id", "Unknown action"))),
        status=str(action.get("status", "blocked")),
        command=str(action.get("command", "")),
        detail=str(action.get("detail", "")),
        required=bool(action.get("required", True)),
        secret=bool(action.get("secret")),
        requires_user_input=bool(action.get("requires_user_input")),
        requires_user_confirmation=bool(action.get("requires_user_confirmation")),
        requires_cost_consent=bool(action.get("requires_cost_consent")),
        global_action=bool(action.get("global")),
        xcode_or_signing=bool(action.get("xcode_or_signing")),
        live_provider_call=bool(action.get("live_provider_call")),
        safe_local_write=bool(action.get("safe_local_write")),
        writes_repo_local_files=bool(action.get("writes_repo_local_files")),
        classification=_optional_string(action.get("classification")),
    )


def _device_section(device_evidence: dict[str, Any]) -> dict[str, Any]:
    raw_slots = device_evidence.get("evidence_slots", [])
    actions = [
        _device_action(slot)
        for slot in raw_slots
        if isinstance(slot, dict)
    ]
    if not actions:
        actions = [
            _closure_action(
                action_id="device_evidence_missing",
                label="Device evidence",
                status="missing",
                command="make ios-device-launch-rehearsal",
                detail="iOS device evidence source report is missing.",
                required=True,
            )
        ]
    summary = device_evidence.get("summary", {})
    detail = (
        "Collect backend LAN, mobile deploy preflight, Xcode build, "
        "and iOS device launch rehearsal evidence."
    )
    if isinstance(summary, dict):
        detail = (
            f"{detail} ready {summary.get('ready', 0)}, "
            f"blocked {summary.get('blocked', 0)}, missing {summary.get('missing', 0)}."
        )
    return _section(
        section_id="device_evidence",
        label="Device evidence",
        status=str(device_evidence.get("status", "missing")),
        command="make ios-device-launch-rehearsal",
        detail=detail,
        required=True,
        actions=actions,
        blocked_by=_blocked_by(actions),
    )


def _device_action(slot: dict[str, Any]) -> dict[str, Any]:
    return _closure_action(
        action_id=str(slot.get("id", "unknown_device_slot")),
        label=str(slot.get("label", slot.get("id", "Unknown device slot"))),
        status=str(slot.get("status", "blocked")),
        command=str(slot.get("command", "make ios-device-launch-rehearsal")),
        detail=str(slot.get("detail", "")),
        required=bool(slot.get("required", True)),
        global_action=bool(slot.get("global_action")),
        xcode_or_signing=bool(slot.get("xcode_or_signing")),
        classification=_optional_string(slot.get("classification")),
    )


def _final_acceptance_section(
    *,
    showcase_readiness: dict[str, Any],
    final_acceptance: dict[str, Any],
) -> dict[str, Any]:
    actions = [
        _final_acceptance_action(final_acceptance),
        _showcase_readiness_action(showcase_readiness),
    ]
    status = _combined_final_status(
        final_acceptance_status=str(final_acceptance.get("status", "missing")),
        showcase_status=str(showcase_readiness.get("status", "missing")),
    )
    return _section(
        section_id="final_acceptance",
        label="Final acceptance",
        status=status,
        command="make final-showcase-readiness",
        detail="Rerun final acceptance and showcase readiness after resources and device evidence are ready.",
        required=True,
        actions=actions,
        blocked_by=_blocked_by(actions),
    )


def _final_acceptance_action(final_acceptance: dict[str, Any]) -> dict[str, Any]:
    blockers = final_acceptance.get("blockers", [])
    blocker = blockers[0] if isinstance(blockers, list) and blockers else {}
    return _closure_action(
        action_id="final_acceptance_readiness",
        label="Final acceptance readiness",
        status=str(final_acceptance.get("status", "missing")),
        command=str(blocker.get("command") or LOCAL_FINAL_ACCEPTANCE_COMMAND),
        detail=_first_detail(
            report=final_acceptance,
            fallback="Run local final acceptance to refresh the latest report.",
        ),
        required=True,
        classification=_optional_string(blocker.get("classification")),
    )


def _showcase_readiness_action(showcase_readiness: dict[str, Any]) -> dict[str, Any]:
    first_blocker = showcase_readiness.get("first_blocker")
    blocker = first_blocker if isinstance(first_blocker, dict) else {}
    return _closure_action(
        action_id="final_showcase_readiness",
        label="Final showcase readiness",
        status=str(showcase_readiness.get("status", "missing")),
        command=str(blocker.get("command") or "make final-showcase-readiness"),
        detail=_first_detail(
            report=showcase_readiness,
            fallback="Run final showcase readiness after all evidence is refreshed.",
        ),
        required=True,
        classification=_optional_string(blocker.get("classification")),
    )


def _first_detail(*, report: dict[str, Any], fallback: str) -> str:
    first_blocker = report.get("first_blocker")
    if isinstance(first_blocker, dict) and first_blocker.get("detail"):
        return str(first_blocker["detail"])
    blockers = report.get("blockers")
    if isinstance(blockers, list) and blockers:
        blocker = blockers[0]
        if isinstance(blocker, dict) and blocker.get("detail"):
            return str(blocker["detail"])
    actions = report.get("operator_actions")
    if isinstance(actions, list) and actions:
        return str(actions[0])
    return fallback


def _combined_final_status(
    *,
    final_acceptance_status: str,
    showcase_status: str,
) -> str:
    statuses = [
        _normalized_status(final_acceptance_status),
        _normalized_status(showcase_status),
    ]
    if "blocked" in statuses:
        return "blocked"
    if "missing" in statuses:
        return "blocked"
    if "partial" in statuses:
        return "partial"
    if "live" in statuses:
        return "partial"
    if "manual" in statuses:
        return "partial"
    return "ready"


def _section(
    *,
    section_id: str,
    label: str,
    status: str,
    command: str,
    detail: str,
    required: bool,
    actions: list[dict[str, Any]],
    blocked_by: list[str],
) -> dict[str, Any]:
    section_status = _section_status(status=status, required=required, actions=actions)
    first_action = _first_action(actions)
    return {
        "id": section_id,
        "label": label,
        "status": section_status,
        "command": command,
        "detail": detail,
        "required": required,
        "actions": actions,
        "first_action": first_action,
        "blocked_by": blocked_by,
        "requires_user_input": any(action["requires_user_input"] for action in actions),
        "requires_user_confirmation": any(
            action["requires_user_confirmation"] for action in actions
        ),
        "requires_cost_consent": any(action["requires_cost_consent"] for action in actions),
        "global_action": any(action["global"] for action in actions),
        "xcode_or_signing": any(action["xcode_or_signing"] for action in actions),
        "live_provider_call": any(action["live_provider_call"] for action in actions),
        "safe_local_write": any(action["safe_local_write"] for action in actions),
    }


def _section_status(
    *,
    status: str,
    required: bool,
    actions: list[dict[str, Any]],
) -> str:
    normalized = _normalized_status(status)
    if any(action["status"] in {"blocked", "missing"} and action["required"] for action in actions):
        return "blocked" if required else normalized
    return normalized


def _closure_action(
    *,
    action_id: str,
    label: str,
    status: str,
    command: str,
    detail: str,
    required: bool,
    secret: bool = False,
    requires_user_input: bool = False,
    requires_user_confirmation: bool = False,
    requires_cost_consent: bool = False,
    global_action: bool = False,
    xcode_or_signing: bool = False,
    live_provider_call: bool = False,
    safe_local_write: bool = False,
    writes_repo_local_files: bool = False,
    classification: str | None = None,
) -> dict[str, Any]:
    row = {
        "id": action_id,
        "label": label,
        "status": _normalized_status(status),
        "command": command,
        "detail": detail,
        "required": required,
        "secret": secret,
        "requires_user_input": requires_user_input,
        "requires_user_confirmation": requires_user_confirmation,
        "requires_cost_consent": requires_cost_consent,
        "global": global_action,
        "xcode_or_signing": xcode_or_signing,
        "live_provider_call": live_provider_call,
        "safe_local_write": safe_local_write,
        "writes_repo_local_files": writes_repo_local_files,
    }
    if classification:
        row["classification"] = classification
    return row


def _first_action(actions: list[dict[str, Any]]) -> dict[str, Any]:
    for action in actions:
        if action["required"] and action["status"] != "ready":
            return action
    for action in actions:
        if action["status"] not in {"ready", "optional"}:
            return action
    for action in actions:
        if action["required"]:
            return action
    return actions[0]


def _blocked_by(actions: list[dict[str, Any]]) -> list[str]:
    return [
        action["id"]
        for action in actions
        if action["required"] and action["status"] in {"missing", "blocked"}
    ]


def _resource_inputs_detail(fill_guide: dict[str, Any]) -> str:
    summary = fill_guide.get("summary", {})
    if not isinstance(summary, dict):
        return "Fill required final resource inputs."
    return (
        f"Fill required final resource inputs: required {summary.get('required_inputs', 0)}, "
        f"optional {summary.get('optional_inputs', 0)}, configured {summary.get('configured_inputs', 0)}."
    )


def _operator_actions(sections: list[dict[str, Any]]) -> list[str]:
    actions: list[str] = []
    for section in sections:
        for action in section["actions"]:
            if action["status"] == "ready":
                continue
            if action["requires_user_input"] and action["id"].startswith("provide_"):
                actions.append(f"provide {action['id'].removeprefix('provide_')}")
            elif action["requires_cost_consent"]:
                actions.append(f"approve live provider cost before {action['command']}")
            elif action["requires_user_confirmation"]:
                actions.append(f"confirm global/manual action before {action['command']}")
            else:
                actions.append(f"run {action['command']}")
    if not actions:
        return ["Final launch closure packet is ready"]
    return _dedupe(actions)


def _summary(sections: list[dict[str, Any]]) -> dict[str, int]:
    actions = [action for section in sections for action in section["actions"]]
    section_statuses = [section["status"] for section in sections]
    return {
        "sections": len(sections),
        "actions": len(actions),
        "ready": section_statuses.count("ready"),
        "missing": section_statuses.count("missing"),
        "blocked": section_statuses.count("blocked"),
        "manual": section_statuses.count("manual"),
        "live": section_statuses.count("live"),
        "partial": section_statuses.count("partial"),
        "optional": section_statuses.count("optional"),
        "required_sections": sum(1 for section in sections if section["required"]),
        "required_actions": sum(1 for action in actions if action["required"]),
        "secret_actions": sum(1 for action in actions if action["secret"]),
        "requires_user_input": sum(
            1 for action in actions if action["requires_user_input"]
        ),
        "requires_user_confirmation": sum(
            1 for action in actions if action["requires_user_confirmation"]
        ),
        "requires_cost_consent": sum(
            1 for action in actions if action["requires_cost_consent"]
        ),
        "global_actions": sum(1 for action in actions if action["global"]),
        "xcode_or_signing_actions": sum(
            1 for action in actions if action["xcode_or_signing"]
        ),
        "safe_local_writes": sum(1 for action in actions if action["safe_local_write"]),
        "live_provider_calls": sum(
            1 for action in actions if action["live_provider_call"]
        ),
    }


def _overall_status(sections: list[dict[str, Any]]) -> str:
    required_sections = [section for section in sections if section["required"]]
    if any(section["status"] in {"blocked", "missing"} for section in required_sections):
        return "blocked"
    if any(
        section["status"] in {"manual", "live", "partial", "optional"}
        for section in sections
    ):
        return "partial"
    return "ready"


def _source_summary(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": report.get("kind", "unknown"),
        "status": report.get("status") or report.get("overall_status") or "unknown",
        "summary": report.get("summary", {}),
    }


def _safety() -> dict[str, bool]:
    return {
        "commands_run": False,
        "writes_backend_env": False,
        "writes_ios_deploy_config": False,
        "runs_shell_writers": False,
        "provider_calls": False,
        "live_provider_calls": False,
        "global_mutation": False,
        "xcode_or_signing": False,
        "keychain_writes": False,
        "provider_secrets_in_report": False,
        "raw_private_context_in_report": False,
        "raw_media_in_report": False,
        "payment_links_in_report": False,
        "local_paths_in_report": False,
        "describes_global_actions": True,
        "requires_cost_consent_for_live_actions": True,
    }


def _normalized_status(status: str) -> str:
    normalized = status.strip().lower()
    if normalized in {
        "ready",
        "missing",
        "blocked",
        "manual",
        "live",
        "partial",
        "optional",
    }:
        return normalized
    if normalized in {"passed", "succeeded"}:
        return "ready"
    if normalized in {"failed", "error"}:
        return "blocked"
    return "blocked"


def _optional_string(value: Any) -> str | None:
    if isinstance(value, str) and value:
        return value
    return None


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        normalized = normalize_operator_action(value)
        if normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result


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
        r"meshy-secret[A-Za-z0-9._-]*",
        r"Bearer\s+[A-Za-z0-9._~+/\-=:-]+",
        r"Bearer\s+\[redacted\]",
        r"Bearer",
        r"Authorization\s*[=:]?\s*",
        r"api[_-]?key\s*[=:]\s*[^\s,;\"']+",
        r"data:[A-Za-z0-9.+-]+/[A-Za-z0-9.+-]+;base64,[A-Za-z0-9+/=_-]+",
        r"https?://pay\.[^\s,;\"']+",
        r"https?://checkout\.[^\s,;\"']+",
        r"checkout_url(?:\s*=\s*)?",
        r"file://[^\s,;\"']+",
        r"/private/[^\s,;\"']+",
        r"/tmp/[^\s,;\"']+",
        r"/Users/[^\s,;\"']+",
        r"https?://10\.[^\s,;\"'`]+",
        r"https?://127\.0\.0\.1[^\s,;\"'`]*",
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
