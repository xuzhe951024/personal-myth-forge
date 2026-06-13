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
from myth_forge_api.final_resource_requirements import (
    build_final_resource_requirements_report,
)
from myth_forge_api.final_showcase_readiness import (
    build_final_showcase_readiness_report,
)
from myth_forge_api.ios_device_evidence_bundle import (
    build_ios_device_evidence_bundle_report,
)
from myth_forge_api.operator_actions import normalize_operator_action

COMMANDS = [
    "make final-resource-requirements",
    "make final-resource-fill-guide",
    "make final-external-action-ledger",
    "make ios-device-launch-rehearsal",
    "make live-provider-evidence",
    "make configured-live-evidence-bundle",
    "make final-showcase-readiness",
    "make final-acceptance-local",
]
FINAL_RESOURCE_APPLY_PREVIEW_ACTION = "make final-resource-apply-preview"
FINAL_RESOURCE_APPLY_ACTION = "make final-apply-resources"
CONFIGURED_LIVE_EVIDENCE_BUNDLE_PATH = Path(
    "services/backend/.local/configured-live-evidence-bundle.json"
)


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
    resource_requirements = build_final_resource_requirements_report(
        repo_root=selected_repo_root,
    ).report
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
    configured_live_evidence_bundle = _load_configured_live_evidence_bundle_report(
        selected_repo_root,
    )
    final_acceptance = build_final_acceptance_readiness_report(
        repo_root=selected_repo_root,
    ).report
    sections = _sections(
        fill_guide=fill_guide,
        action_ledger=action_ledger,
        device_evidence=device_evidence,
        showcase_readiness=showcase_readiness,
        configured_live_evidence_bundle=configured_live_evidence_bundle,
        final_acceptance=final_acceptance,
    )
    status = _overall_status(sections)
    first_blocker = _first_blocker(sections)
    report = {
        "kind": "final_launch_closure_packet_report",
        "status": status,
        "summary": _summary(sections),
        "first_blocker": first_blocker,
        "next_action": _next_action(first_blocker),
        "sections": sections,
        "sections_by_id": {section["id"]: section for section in sections},
        "device_action_bundle": _device_action_bundle(device_evidence),
        "operator_actions": _operator_actions(sections),
        "commands": COMMANDS,
        "source_reports": {
            "final_resource_requirements": _source_summary(resource_requirements),
            "final_resource_fill_guide": _source_summary(fill_guide),
            "final_external_action_ledger": _source_summary(action_ledger),
            "ios_device_evidence_bundle": _source_summary(device_evidence),
            "final_showcase_readiness": _source_summary(showcase_readiness),
            "configured_live_evidence_bundle": _source_summary(
                configured_live_evidence_bundle
            ),
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
    configured_live_evidence_bundle: dict[str, Any],
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
        _configured_evidence_bundle_section(configured_live_evidence_bundle),
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
        destination=_optional_string(action.get("destination")),
        operator_action=_optional_string(action.get("operator_action")),
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


def _device_action_bundle(device_evidence: dict[str, Any]) -> dict[str, Any]:
    source_bundle = device_evidence.get("device_action_bundle")
    if isinstance(source_bundle, dict):
        actions = [
            _closure_device_action(action)
            for action in source_bundle.get("actions", [])
            if isinstance(action, dict)
        ]
        first_action = _closure_device_first_action(
            source_bundle.get("first_action"),
            actions,
        )
        status = str(
            source_bundle.get("status", device_evidence.get("status", "missing"))
        )
    else:
        actions = [
            _closure_device_action_from_slot(slot)
            for slot in device_evidence.get("evidence_slots", [])
            if isinstance(slot, dict)
        ]
        first_action = _first_closure_device_action(actions)
        status = str(device_evidence.get("status", "missing"))
    return {
        "id": "final_launch_closure_device_actions",
        "label": "Final Launch Closure Device Actions",
        "source_report": "ios_device_evidence_bundle",
        "status": _normalized_status(status),
        "actions": actions,
        "first_action": first_action,
        "summary": _device_action_bundle_summary(actions),
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


def _closure_device_action(action: dict[str, Any]) -> dict[str, Any]:
    copied = {
        "id": str(action.get("id", "device_action")),
        "label": str(action.get("label", action.get("id", "Device action"))),
        "status": _normalized_status(str(action.get("status", "blocked"))),
        "classification": str(action.get("classification", "")),
        "command": str(action.get("command", "")),
        "detail": str(action.get("detail", "")),
        "evidence_source": str(action.get("evidence_source", "")),
        "manual": bool(action.get("manual")),
        "provider_calls": bool(action.get("provider_calls")),
        "global_action": bool(action.get("global_action")),
        "xcode_or_signing": bool(action.get("xcode_or_signing")),
    }
    next_action = action.get("next_action")
    if isinstance(next_action, dict):
        copied["next_action"] = _closure_device_next_action(next_action)
    return copied


def _closure_device_next_action(next_action: dict[str, Any]) -> dict[str, str]:
    copied = {
        "id": str(next_action.get("id", "")),
        "label": str(next_action.get("label", "")),
        "status": str(next_action.get("status", "")),
        "command": str(next_action.get("command", "")),
        "detail": str(next_action.get("detail", "")),
        "source": str(next_action.get("source", "")),
    }
    validation_command = str(next_action.get("validation_command", "")).strip()
    if validation_command:
        copied["validation_command"] = validation_command
    return copied


def _closure_device_action_from_slot(slot: dict[str, Any]) -> dict[str, Any]:
    status = _normalized_status(str(slot.get("status", "blocked")))
    action = {
        "id": str(slot.get("id", "device_slot")),
        "label": str(slot.get("label", slot.get("id", "Device slot"))),
        "status": status,
        "classification": str(slot.get("classification", "")),
        "command": str(slot.get("command", "")),
        "detail": str(slot.get("detail", "")),
        "evidence_source": str(slot.get("evidence_source", "")),
        "manual": status != "ready",
        "provider_calls": False,
        "global_action": bool(slot.get("global_action")),
        "xcode_or_signing": bool(slot.get("xcode_or_signing")),
    }
    if status != "ready":
        action["next_action"] = {
            "id": action["id"],
            "label": action["label"],
            "status": action["status"],
            "command": action["command"],
            "detail": action["detail"],
            "source": "final_launch_closure_device_actions",
        }
    return action


def _closure_device_first_action(
    source_first_action: Any,
    actions: list[dict[str, Any]],
) -> dict[str, Any] | None:
    if isinstance(source_first_action, dict):
        return _closure_device_action(source_first_action)
    return _first_closure_device_action(actions)


def _first_closure_device_action(
    actions: list[dict[str, Any]],
) -> dict[str, Any] | None:
    for action in actions:
        if action["status"] != "ready":
            return action
    return None


def _device_action_bundle_summary(actions: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "actions": len(actions),
        "ready": sum(1 for action in actions if action["status"] == "ready"),
        "missing": sum(1 for action in actions if action["status"] == "missing"),
        "blocked": sum(1 for action in actions if action["status"] == "blocked"),
        "manual": sum(1 for action in actions if action.get("manual") is True),
        "provider_calls": sum(
            1 for action in actions if action["provider_calls"] is True
        ),
        "global_actions": sum(1 for action in actions if action["global_action"] is True),
        "xcode_or_signing": sum(
            1 for action in actions if action["xcode_or_signing"] is True
        ),
    }


def _configured_evidence_bundle_section(
    configured_live_evidence_bundle: dict[str, Any],
) -> dict[str, Any]:
    action = _configured_evidence_bundle_action(configured_live_evidence_bundle)
    summary = configured_live_evidence_bundle.get("summary", {})
    detail = "Refresh configured evidence bundle before final acceptance."
    if isinstance(summary, dict):
        detail = (
            "Configured evidence bundle: "
            f"ready {summary.get('evidence_ready', 0)}, "
            f"missing {summary.get('evidence_missing', 0)}, "
            f"blocked {summary.get('evidence_blocked', 0)}."
        )
    return _section(
        section_id="configured_evidence_bundle",
        label="Configured evidence bundle",
        status=str(configured_live_evidence_bundle.get("status", "missing")),
        command="make configured-live-evidence-bundle",
        detail=detail,
        required=True,
        actions=[action],
        blocked_by=_blocked_by([action]),
    )


def _configured_evidence_bundle_action(
    configured_live_evidence_bundle: dict[str, Any],
) -> dict[str, Any]:
    blocker = configured_live_evidence_bundle.get("current_blocker")
    blocker_dict = blocker if isinstance(blocker, dict) else {}
    status = str(
        blocker_dict.get("status")
        or configured_live_evidence_bundle.get("status", "missing")
    )
    command = str(
        blocker_dict.get("command") or "make configured-live-evidence-bundle"
    )
    detail = str(
        blocker_dict.get("detail")
        or _first_operator_action(configured_live_evidence_bundle)
        or "Run configured evidence bundle after live provider evidence is refreshed."
    )
    return _closure_action(
        action_id="configured_live_evidence_bundle",
        label="Configured live evidence bundle",
        status=status,
        command=command,
        detail=detail,
        required=True,
        classification=_optional_string(blocker_dict.get("classification")),
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


def _first_operator_action(report: dict[str, Any]) -> str | None:
    actions = report.get("operator_actions")
    if isinstance(actions, list) and actions:
        first = actions[0]
        if isinstance(first, str) and first:
            return first
    return None


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
    destination: str | None = None,
    operator_action: str | None = None,
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
    if destination:
        row["destination"] = destination
    if operator_action:
        row["operator_action"] = operator_action
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
                actions.append(_provide_action_text(action))
            elif action["requires_cost_consent"]:
                concrete_action = str(action.get("operator_action", "")).strip()
                if concrete_action:
                    actions.append(concrete_action)
                else:
                    actions.append(
                        f"approve live provider cost before {action['command']}"
                    )
            elif action["requires_user_confirmation"]:
                concrete_action = str(action.get("operator_action", "")).strip()
                if concrete_action:
                    actions.append(concrete_action)
                else:
                    actions.append(
                        f"confirm global/manual action before {action['command']}"
                    )
            else:
                actions.append(_run_action_text(str(action["command"])))
    if not actions:
        return ["Final launch closure packet is ready"]
    return _prefer_apply_preview_before_apply(_dedupe(actions))


def _run_action_text(command: str) -> str:
    normalized = command.strip()
    if normalized.startswith("make "):
        return normalized
    return f"run {normalized}"


def _provide_action_text(action: dict[str, Any]) -> str:
    slot = str(action["id"]).removeprefix("provide_")
    destination = Path(str(action.get("destination", ""))).name
    command = str(action.get("command", "")).strip()
    parts = [f"provide {slot}"]
    if destination:
        parts[0] = f"{parts[0]} in {destination}"
    if command:
        parts.append(f"rerun {command}")
    return "; ".join(parts)


def _blocker_command_for_action(
    action: dict[str, Any],
    section: dict[str, Any],
) -> str:
    if _is_resource_user_input_action(action):
        return _provide_action_text(action).split(";", 1)[0].strip()
    return str(action.get("command", section.get("command", "")))


def _validation_command_for_action(action: dict[str, Any]) -> str | None:
    command = str(action.get("command", "")).strip()
    if command.startswith("make "):
        return command
    return None


def _is_resource_user_input_action(action: dict[str, Any]) -> bool:
    return (
        str(action.get("id", "")).startswith("provide_")
        and action.get("status") in {"missing", "blocked"}
        and bool(action.get("requires_user_input"))
    )


def _next_action(first_blocker: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(first_blocker, dict):
        return None
    next_action = {
        "id": str(first_blocker.get("id", "")),
        "label": str(first_blocker.get("label", "")),
        "status": str(first_blocker.get("status", "")),
        "classification": str(first_blocker.get("classification", "")),
        "command": str(first_blocker.get("command", "")),
        "detail": str(first_blocker.get("detail", "")),
        "source": "first_blocker",
        "section_id": str(first_blocker.get("section_id", "")),
        "action_id": str(first_blocker.get("action_id", "")),
    }
    validation_command = first_blocker.get("validation_command")
    if validation_command:
        next_action["validation_command"] = str(validation_command)
    return next_action


def _first_blocker(sections: list[dict[str, Any]]) -> dict[str, Any] | None:
    for section in sections:
        if not section.get("required"):
            continue
        if section.get("status") not in {"blocked", "missing"}:
            continue
        action = section.get("first_action")
        if not isinstance(action, dict):
            continue
        blocker = {
            "id": str(section.get("id", "section")),
            "label": str(section.get("label", section.get("id", "section"))),
            "status": str(section.get("status", "blocked")),
            "classification": _optional_string(action.get("classification")),
            "command": _blocker_command_for_action(action, section),
            "detail": str(action.get("detail", section.get("detail", ""))),
            "section_id": str(section.get("id", "section")),
            "action_id": str(action.get("id", "action")),
        }
        validation_command = _validation_command_for_action(action)
        if validation_command:
            blocker["validation_command"] = validation_command
        if blocker["classification"] is None:
            blocker.pop("classification")
        return blocker
    return None


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
    summary = {
        "kind": report.get("kind", "unknown"),
        "status": report.get("status") or report.get("overall_status") or "unknown",
        "summary": report.get("summary", {}),
    }
    device_action_bundle = report.get("device_action_bundle")
    if isinstance(device_action_bundle, dict):
        summary["device_action_bundle"] = device_action_bundle
    source_reports = report.get("source_reports")
    if isinstance(source_reports, dict):
        summary["source_reports"] = source_reports
    return summary


def _load_configured_live_evidence_bundle_report(repo_root: Path) -> dict[str, Any]:
    relative_path = CONFIGURED_LIVE_EVIDENCE_BUNDLE_PATH.as_posix()
    path = repo_root / CONFIGURED_LIVE_EVIDENCE_BUNDLE_PATH
    if not path.exists():
        return _configured_live_evidence_bundle_stub(
            status="missing",
            classification="missing_report",
            detail=f"Missing {relative_path}.",
        )
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _configured_live_evidence_bundle_stub(
            status="blocked",
            classification="unreadable_report",
            detail=f"{relative_path} is not valid JSON.",
        )
    if not isinstance(payload, dict):
        return _configured_live_evidence_bundle_stub(
            status="blocked",
            classification="invalid_report_shape",
            detail=f"{relative_path} must contain a JSON object.",
        )
    if payload.get("kind") != "configured_live_evidence_bundle_report":
        return _configured_live_evidence_bundle_stub(
            status="blocked",
            classification="wrong_report_kind",
            detail="Expected configured_live_evidence_bundle_report.",
        )
    return payload


def _configured_live_evidence_bundle_stub(
    *,
    status: str,
    classification: str,
    detail: str,
) -> dict[str, Any]:
    return {
        "kind": "configured_live_evidence_bundle_report",
        "status": status,
        "summary": {
            "evidence_files": 0,
            "evidence_ready": 0,
            "evidence_missing": 1 if status == "missing" else 0,
            "evidence_blocked": 1 if status != "missing" else 0,
            "commands_run": 0,
        },
        "current_blocker": {
            "id": "configured_live_evidence_bundle",
            "label": "Configured live evidence bundle",
            "status": status,
            "classification": classification,
            "command": "make configured-live-evidence-bundle",
            "detail": detail,
        },
        "operator_actions": [
            "run make configured-live-evidence-bundle to refresh configured evidence bundle"
        ],
        "commands": ["make configured-live-evidence-bundle"],
        "safety": {
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
        },
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


def _prefer_apply_preview_before_apply(actions: list[str]) -> list[str]:
    action_roots = {_operator_action_root(action) for action in actions}
    if FINAL_RESOURCE_APPLY_PREVIEW_ACTION not in action_roots:
        return actions
    return [
        action
        for action in actions
        if _operator_action_root(action) != FINAL_RESOURCE_APPLY_ACTION
    ]


def _operator_action_root(action: str) -> str:
    return action.split(" | ", 1)[0].strip()


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
