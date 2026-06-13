from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Literal

from myth_forge_api.configured_acceptance_command import (
    CONFIGURED_FINAL_ACCEPTANCE_COMMAND,
    CONFIGURED_FINAL_ACCEPTANCE_COST_REVIEW_ACTION,
)
from myth_forge_api.final_acceptance_readiness import (
    LOCAL_FINAL_ACCEPTANCE_COMMAND,
    build_final_acceptance_readiness_report,
)
from myth_forge_api.final_resource_apply_preview import (
    build_final_resource_apply_preview_report,
)
from myth_forge_api.final_resources_preflight import (
    DEFAULT_RESOURCES_PATH,
    build_final_resources_preflight_report,
)
from myth_forge_api.npc_agent_evaluation_readiness import (
    LOCAL_NPC_EVALUATION_COMMAND,
    build_npc_agent_evaluation_readiness_report,
)
from myth_forge_api.operator_actions import (
    add_final_resource_validation_command,
    add_mobile_deploy_validation_command,
)
from myth_forge_api.three_d_evaluation_readiness import (
    LOCAL_THREE_D_EVALUATION_COMMAND,
    build_three_d_evaluation_readiness_report,
)

LaunchMode = Literal["local", "configured"]

IOS_BASE_CONFIG_PATH = Path("apps/mobile/ios/Config/Deployment.xcconfig")
IOS_DEPLOY_CONFIG_PATH = Path("apps/mobile/ios/Config/Deployment.local.xcconfig")
IOS_DEPLOY_RUNBOOK_COMMAND = "make ios-deploy-runbook-local"


def build_ios_deploy_runbook_report(
    *,
    mode: LaunchMode,
    repo_root: Path | str | None = None,
) -> dict[str, Any]:
    if mode not in ("local", "configured"):
        raise ValueError(f"Unsupported iOS deploy runbook mode: {mode}")
    selected_repo_root = Path(repo_root) if repo_root is not None else _default_repo_root()
    final_resources = build_final_resources_preflight_report(
        repo_root=selected_repo_root,
    ).report
    final_resource_apply_preview = build_final_resource_apply_preview_report(
        repo_root=selected_repo_root,
    ).report
    final_acceptance = build_final_acceptance_readiness_report(
        repo_root=selected_repo_root,
    ).report
    three_d_evaluation = build_three_d_evaluation_readiness_report(
        repo_root=selected_repo_root,
    ).report
    npc_evaluation = build_npc_agent_evaluation_readiness_report(
        repo_root=selected_repo_root,
    ).report
    input_slots = _input_slots(
        mode=mode,
        deploy_values=_deploy_config_values(selected_repo_root),
        final_resources=final_resources,
        final_resource_apply_preview=final_resource_apply_preview,
        final_acceptance=final_acceptance,
        three_d_evaluation=three_d_evaluation,
        npc_evaluation=npc_evaluation,
    )
    command_sequence = _command_sequence(mode=mode, input_slots=input_slots)
    first_blocker = _first_blocker(
        input_slots=input_slots,
        command_sequence=command_sequence,
    )
    report = {
        "kind": "ios_deploy_runbook_report",
        "mode": mode,
        "status": _overall_status(input_slots=input_slots, command_sequence=command_sequence),
        "input_slots": input_slots,
        "command_sequence": command_sequence,
        "first_blocker": first_blocker,
        "next_action": _next_action(first_blocker),
        "device_action_bundle": _device_action_bundle(
            input_slots=input_slots,
            command_sequence=command_sequence,
        ),
        "operator_actions": _operator_actions(
            mode=mode,
            input_slots=input_slots,
            final_resources=final_resources,
            final_resource_apply_preview=final_resource_apply_preview,
            final_acceptance=final_acceptance,
            three_d_evaluation=three_d_evaluation,
            npc_evaluation=npc_evaluation,
            command_sequence=command_sequence,
        ),
        "safety": {
            "commands_run": False,
            "provider_calls": False,
            "global_mutation": False,
            "provider_secrets_in_report": False,
            "raw_media_in_report": False,
            "payment_links_in_report": False,
            "local_paths_in_report": False,
        },
    }
    return _sanitize_report(report, selected_repo_root)


def _input_slots(
    *,
    mode: LaunchMode,
    deploy_values: dict[str, str],
    final_resources: dict[str, Any],
    final_resource_apply_preview: dict[str, Any],
    final_acceptance: dict[str, Any],
    three_d_evaluation: dict[str, Any],
    npc_evaluation: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        _final_resources_slot(mode=mode, final_resources=final_resources),
        _slot(
            slot_id="final_resource_apply_preview",
            label="Final resource apply preview",
            status=str(final_resource_apply_preview.get("status", "missing")),
            required=mode == "configured",
            source="services/backend/.local/final-resource-apply-preview.json",
            action="make final-resource-apply-preview",
        ),
        _slot(
            slot_id="backend_provider_env",
            label="Backend provider env",
            status=str(final_resources.get("status", "missing")),
            required=mode == "configured",
            source="services/backend/.local/final-resources.env",
            action="provide Meshy/OpenAI provider values in final-resources.env",
        ),
        _deploy_value_slot(
            slot_id="development_team",
            label="Apple Team ID",
            key="DEVELOPMENT_TEAM",
            value=deploy_values.get("DEVELOPMENT_TEAM", ""),
            action="provide DEVELOPMENT_TEAM in Deployment.local.xcconfig",
        ),
        _deploy_value_slot(
            slot_id="product_bundle_identifier",
            label="Bundle identifier",
            key="PRODUCT_BUNDLE_IDENTIFIER",
            value=deploy_values.get("PRODUCT_BUNDLE_IDENTIFIER", ""),
            action="provide PRODUCT_BUNDLE_IDENTIFIER in Deployment.local.xcconfig",
        ),
        _backend_url_slot(deploy_values.get("PMF_BACKEND_BASE_URL", "")),
        _final_launch_mode_slot(mode, deploy_values.get("PMF_FINAL_LAUNCH_MODE", "")),
        _slot(
            slot_id="local_final_acceptance",
            label="Local final acceptance",
            status=str(final_acceptance.get("status", "missing")),
            required=True,
            source="services/backend/.local/final-acceptance-local.json",
            action=(
                f"run {LOCAL_FINAL_ACCEPTANCE_COMMAND} to write "
                "services/backend/.local/final-acceptance-local.json"
            ),
        ),
        _slot(
            slot_id="three_d_evaluation",
            label="3D evaluation",
            status=str(three_d_evaluation.get("status", "missing")),
            required=True,
            source="services/backend/.local/3d-evaluation-local.json",
            action=(
                f"run {LOCAL_THREE_D_EVALUATION_COMMAND} to write "
                "services/backend/.local/3d-evaluation-local.json"
            ),
        ),
        _slot(
            slot_id="npc_agent_evaluation",
            label="NPC Agent evaluation",
            status=str(npc_evaluation.get("status", "missing")),
            required=True,
            source="services/backend/.local/npc-evaluation-local.json",
            action=(
                f"run {LOCAL_NPC_EVALUATION_COMMAND} to write "
                "services/backend/.local/npc-evaluation-local.json"
            ),
        ),
    ]


def _final_resources_slot(
    *,
    mode: LaunchMode,
    final_resources: dict[str, Any],
) -> dict[str, Any]:
    resources_file = final_resources.get("resources_file", {})
    resources_path = str(
        resources_file.get(
            "path",
            DEFAULT_RESOURCES_PATH.as_posix(),
        )
    )
    child_blocker = _final_resources_child_blocker(final_resources)
    action = "run make final-resource-init"
    classification = None
    if child_blocker is not None:
        action = str(child_blocker.get("command") or action)
        classification = str(child_blocker.get("classification") or "") or None
    slot = _slot(
        slot_id="final_resources_env",
        label="Final resources env",
        status=str(final_resources.get("status", "missing")),
        required=mode == "configured",
        source=resources_path,
        action=action,
        classification=classification,
    )
    if child_blocker is None:
        return slot
    child_id = str(child_blocker.get("id", ""))
    child_label = str(child_blocker.get("label", child_id))
    detail = str(child_blocker.get("detail", "")).strip()
    validation_command = str(child_blocker.get("validation_command", "")).strip()
    slot["source_blocker_id"] = child_id
    slot["source_blocker_label"] = child_label
    if detail:
        slot["blocker_detail"] = detail
    if validation_command:
        slot["validation_command"] = validation_command
    return slot


def _final_resources_child_blocker(
    final_resources: dict[str, Any],
) -> dict[str, Any] | None:
    if final_resources.get("status") == "ready":
        return None
    resources_file = final_resources.get("resources_file", {})
    if not bool(resources_file.get("exists")):
        return None
    for key in ("next_action", "first_blocker"):
        candidate = final_resources.get(key)
        if isinstance(candidate, dict) and candidate.get("command"):
            return candidate
    return None


def _deploy_value_slot(
    *,
    slot_id: str,
    label: str,
    key: str,
    value: str,
    action: str,
) -> dict[str, Any]:
    configured = bool(value)
    status = "ready" if configured else "missing"
    slot = _slot(
        slot_id=slot_id,
        label=label,
        status=status,
        required=True,
        source=IOS_DEPLOY_CONFIG_PATH.as_posix(),
        action=action,
        configured=configured,
        redacted=configured,
        classification=None if configured else "missing_required_value",
    )
    slot["key"] = key
    return slot


def _backend_url_slot(value: str) -> dict[str, Any]:
    configured = bool(value)
    if not configured:
        status = "missing"
        classification = "missing_required_value"
        action = "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL"
    elif _is_loopback_url(value):
        status = "blocked"
        classification = "loopback_url"
        action = "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL"
    else:
        status = "ready"
        classification = None
        action = "PMF_BACKEND_BASE_URL is ready"
    slot = _slot(
        slot_id="backend_base_url",
        label="iPhone backend URL",
        status=status,
        required=True,
        source=IOS_DEPLOY_CONFIG_PATH.as_posix(),
        action=action,
        configured=configured and status == "ready",
        redacted=configured,
        classification=classification,
    )
    slot["key"] = "PMF_BACKEND_BASE_URL"
    return slot


def _final_launch_mode_slot(mode: LaunchMode, value: str) -> dict[str, Any]:
    normalized = (value or "local").lower()
    if normalized in {"local", "configured"}:
        status = "ready"
        classification = None
        action = "PMF_FINAL_LAUNCH_MODE is ready"
    else:
        status = "blocked"
        classification = "unsupported_value"
        action = "set PMF_FINAL_LAUNCH_MODE to local or configured"
    slot = _slot(
        slot_id="final_launch_mode",
        label="Final launch mode",
        status=status,
        required=False,
        source=IOS_DEPLOY_CONFIG_PATH.as_posix(),
        action=action,
        configured=bool(value),
        redacted=False,
        classification=classification,
    )
    slot["key"] = "PMF_FINAL_LAUNCH_MODE"
    slot["expected_mode"] = mode
    return slot


def _slot(
    *,
    slot_id: str,
    label: str,
    status: str,
    required: bool,
    source: str,
    action: str,
    configured: bool | None = None,
    redacted: bool = False,
    classification: str | None = None,
) -> dict[str, Any]:
    normalized_status = _normalized_slot_status(status)
    slot = {
        "id": slot_id,
        "label": label,
        "status": normalized_status,
        "required": required,
        "source": source,
        "operator_action": action,
        "configured": normalized_status == "ready" if configured is None else configured,
        "redacted": redacted,
    }
    if classification:
        slot["classification"] = classification
    return slot


def _command_sequence(
    *,
    mode: LaunchMode,
    input_slots: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    slots = {slot["id"]: slot for slot in input_slots}
    deploy_config_status = _combined_status(
        [
            str(slots["development_team"]["status"]),
            str(slots["product_bundle_identifier"]["status"]),
            str(slots["backend_base_url"]["status"]),
            str(slots["final_launch_mode"]["status"]),
        ]
    )
    sequence = [
        _command_step(
            "final_resources_preflight",
            "Check final resources",
            _resource_command_status(
                mode=mode,
                status=str(slots["final_resources_env"]["status"]),
            ),
            "make final-resources-preflight",
            "Validate ignored final resources file without applying it.",
        ),
        _command_step(
            "preview_final_resource_apply",
            "Preview final resource apply",
            _resource_command_status(
                mode=mode,
                status=str(slots["final_resource_apply_preview"]["status"]),
            ),
            "make final-resource-apply-preview",
            "Preview backend .env and iOS deploy config writes without running writer scripts.",
        ),
        _command_step(
            "apply_final_resources",
            "Apply final resources",
            _resource_command_status(
                mode=mode,
                status=_combined_status(
                    [
                        str(slots["final_resources_env"]["status"]),
                        str(slots["final_resource_apply_preview"]["status"]),
                    ]
                ),
            ),
            "make final-apply-resources",
            "Write only ignored backend and iOS local config files.",
        ),
        _command_step(
            "backend_device_server",
            "Start backend on LAN",
            "ready",
            "make backend-device-demo",
            "Start uvicorn on 0.0.0.0:8080.",
        ),
        _command_step(
            "mobile_deploy_preflight",
            "Run iOS deploy preflight",
            deploy_config_status,
            "make mobile-deploy-preflight",
            "Validate iPhone-reachable backend health before opening Xcode.",
        ),
    ]
    if mode == "configured":
        sequence.append(
            _command_step(
                "configured_final_acceptance",
                "Run configured final acceptance",
                "live",
                CONFIGURED_FINAL_ACCEPTANCE_COMMAND,
                "May call live providers and spend credits.",
                requires_consent=True,
            )
        )
    sequence.append(
        _command_step(
            "xcode_build_gate",
            "Run Xcode build gate",
            "manual",
            "make mobile-xcode-build",
            "Apple license/signing state remains external to this repo.",
        )
    )
    return sequence


def _resource_command_status(*, mode: LaunchMode, status: str) -> str:
    if mode == "configured":
        return status
    return "ready" if status == "ready" else "partial"


def _command_step(
    step_id: str,
    label: str,
    status: str,
    command: str,
    note: str,
    *,
    requires_consent: bool = False,
) -> dict[str, Any]:
    return {
        "id": step_id,
        "label": label,
        "status": _normalized_command_status(status),
        "command": command,
        "notes": [note],
        "requires_consent": requires_consent,
    }


def _operator_actions(
    *,
    mode: LaunchMode,
    input_slots: list[dict[str, Any]],
    final_resources: dict[str, Any],
    final_resource_apply_preview: dict[str, Any],
    final_acceptance: dict[str, Any],
    three_d_evaluation: dict[str, Any],
    npc_evaluation: dict[str, Any],
    command_sequence: list[dict[str, Any]],
) -> list[str]:
    actions: list[str] = []
    actions.extend(_string_list(final_resources.get("operator_actions")))
    actions.extend(_selected_apply_preview_actions(final_resource_apply_preview))
    actions.extend(
        action
        for action in _string_list(final_acceptance.get("operator_actions"))
        if action != "final acceptance is ready"
    )
    actions.extend(
        action
        for action in _string_list(three_d_evaluation.get("operator_actions"))
        if action != "3D evaluation is ready"
    )
    actions.extend(
        action
        for action in _string_list(npc_evaluation.get("operator_actions"))
        if action != "NPC Agent evaluation is ready"
    )
    for slot in input_slots:
        if slot["status"] in {"missing", "blocked"}:
            actions.append(str(slot["operator_action"]))
    if mode == "configured":
        actions.append(CONFIGURED_FINAL_ACCEPTANCE_COST_REVIEW_ACTION)
    for step in command_sequence:
        if step["status"] == "manual" and step["id"] == "xcode_build_gate":
            actions.append("run Xcode build gate manually on the Mac: make mobile-xcode-build")
    return _dedupe(
        [
            add_final_resource_validation_command(
                add_mobile_deploy_validation_command(action)
            )
            for action in actions
        ]
    )


def _selected_apply_preview_actions(report: dict[str, Any]) -> list[str]:
    if report.get("status") == "ready":
        return []
    return _string_list(report.get("operator_actions"))


def _overall_status(
    *,
    input_slots: list[dict[str, Any]],
    command_sequence: list[dict[str, Any]],
) -> str:
    statuses = [str(slot["status"]) for slot in input_slots if slot["required"]]
    statuses.extend(str(step["status"]) for step in command_sequence)
    if "blocked" in statuses or "missing" in statuses:
        return "blocked"
    if any(status in {"manual", "partial", "live"} for status in statuses):
        return "partial"
    return "ready"


def _first_blocker(
    *,
    input_slots: list[dict[str, Any]],
    command_sequence: list[dict[str, Any]],
) -> dict[str, Any] | None:
    for slot in input_slots:
        if slot["required"] and slot["status"] != "ready":
            return _slot_blocker(slot)
    for step in command_sequence:
        if step["status"] != "ready":
            return _command_step_blocker(step)
    return None


def _slot_blocker(slot: dict[str, Any]) -> dict[str, Any]:
    if slot.get("validation_command"):
        command = str(slot["operator_action"])
    else:
        command = add_final_resource_validation_command(
            add_mobile_deploy_validation_command(str(slot["operator_action"]))
        )
    blocker = {
        "id": str(slot["id"]),
        "label": str(slot["label"]),
        "status": str(slot["status"]),
        "classification": str(slot.get("classification", "")),
        "command": command,
        "detail": str(
            slot.get("blocker_detail") or f"{slot['label']} is {slot['status']}."
        ),
        "input_source": str(slot["source"]),
        "required": bool(slot["required"]),
    }
    for key in ("source_blocker_id", "source_blocker_label", "validation_command"):
        if slot.get(key):
            blocker[key] = slot[key]
    return blocker


def _command_step_blocker(step: dict[str, Any]) -> dict[str, Any]:
    notes = "; ".join(str(note) for note in step.get("notes", []) if str(note))
    return {
        "id": str(step["id"]),
        "label": str(step["label"]),
        "status": str(step["status"]),
        "classification": "command_step_not_ready",
        "command": str(step["command"]),
        "detail": notes,
    }


def _next_action(first_blocker: dict[str, Any] | None) -> dict[str, Any] | None:
    if first_blocker is None:
        return None
    return {**first_blocker, "source": "first_blocker"}


def _device_action_bundle(
    *,
    input_slots: list[dict[str, Any]],
    command_sequence: list[dict[str, Any]],
) -> dict[str, Any]:
    slots = {slot["id"]: slot for slot in input_slots}
    steps = {step["id"]: step for step in command_sequence}
    actions = [
        _device_slot_action(
            "write_development_team",
            "Write Apple Team ID",
            slots["development_team"],
            "DEVELOPMENT_TEAM=YOUR_TEAM_ID make mobile-write-deploy-config-auto",
            "Provide the Apple Team ID in ignored Deployment.local.xcconfig.",
        ),
        _device_slot_action(
            "write_product_bundle_identifier",
            "Write bundle identifier",
            slots["product_bundle_identifier"],
            "provide PRODUCT_BUNDLE_IDENTIFIER in Deployment.local.xcconfig",
            "Provide the bundle identifier in ignored Deployment.local.xcconfig.",
        ),
        _device_slot_action(
            "write_backend_base_url",
            "Write iPhone backend URL",
            slots["backend_base_url"],
            "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL",
            "Use a LAN URL the iPhone can reach; localhost is not valid.",
        ),
        _device_step_action(
            "start_backend_device_demo",
            "Start backend device demo",
            "ready",
            "make backend-device-demo",
            "Start the LAN backend before running mobile preflight.",
        ),
        _device_step_action(
            "run_mobile_deploy_preflight",
            "Run mobile deploy preflight",
            str(steps["mobile_deploy_preflight"]["status"]),
            "make mobile-deploy-preflight",
            "Verify device config and backend health before Xcode.",
        ),
        _device_step_action(
            "resolve_xcode_build_gate",
            "Resolve Xcode build gate",
            str(steps["xcode_build_gate"]["status"]),
            "make mobile-xcode-build",
            "Run or resolve the Xcode build/signing gate on the Mac.",
            xcode_or_signing=True,
        ),
        _device_step_action(
            "run_ios_device_launch_rehearsal",
            "Run iOS device launch rehearsal",
            str(steps["xcode_build_gate"]["status"]),
            "make ios-device-launch-rehearsal",
            "Refresh final device launch rehearsal evidence after preflight and build gates.",
        ),
    ]
    return {
        "id": "ios_deploy_runbook_device_actions",
        "label": "iOS Deploy Runbook Device Actions",
        "status": _device_bundle_status(actions),
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


def _device_slot_action(
    action_id: str,
    label: str,
    slot: dict[str, Any],
    command: str,
    detail: str,
) -> dict[str, Any]:
    status = str(slot["status"])
    action = _device_step_action(action_id, label, status, command, detail)
    action["input_source"] = str(slot["source"])
    action["next_action"] = {
        "id": str(slot["id"]),
        "label": str(slot["label"]),
        "status": str(action["status"]),
        "command": command,
        "detail": str(slot.get("blocker_detail") or detail),
        "source": "device_action_bundle",
        "validation_command": "make mobile-deploy-preflight",
    }
    return action


def _device_step_action(
    action_id: str,
    label: str,
    status: str,
    command: str,
    detail: str,
    *,
    xcode_or_signing: bool = False,
) -> dict[str, Any]:
    normalized = _normalized_device_action_status(status)
    return {
        "id": action_id,
        "label": label,
        "status": normalized,
        "classification": _device_action_classification(normalized, xcode_or_signing),
        "command": command,
        "detail": detail,
        "manual": normalized != "ready",
        "provider_calls": False,
        "global_action": False,
        "xcode_or_signing": xcode_or_signing,
        "validation_command": "make mobile-deploy-preflight",
    }


def _normalized_device_action_status(status: str) -> str:
    if status == "ready":
        return "ready"
    if status == "manual":
        return "manual"
    return "blocked"


def _device_action_classification(status: str, xcode_or_signing: bool) -> str:
    if status == "ready":
        return "ready"
    if xcode_or_signing:
        return "manual_xcode_or_signing_required"
    if status == "manual":
        return "manual_device_step_required"
    return "manual_device_config_required"


def _device_bundle_status(actions: list[dict[str, Any]]) -> str:
    statuses = [str(action["status"]) for action in actions]
    if "blocked" in statuses:
        return "blocked"
    if "manual" in statuses:
        return "partial"
    return "ready"


def _first_device_action(actions: list[dict[str, Any]]) -> dict[str, Any] | None:
    return next((action for action in actions if action["status"] != "ready"), None)


def _device_action_summary(actions: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "actions": len(actions),
        "ready": sum(1 for action in actions if action["status"] == "ready"),
        "blocked": sum(1 for action in actions if action["status"] == "blocked"),
        "manual": sum(1 for action in actions if action.get("manual") is True),
        "provider_calls": sum(1 for action in actions if action["provider_calls"] is True),
        "global_actions": sum(1 for action in actions if action["global_action"] is True),
        "xcode_or_signing": sum(
            1 for action in actions if action["xcode_or_signing"] is True
        ),
    }


def _deploy_config_values(repo_root: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for relative_path in (IOS_BASE_CONFIG_PATH, IOS_DEPLOY_CONFIG_PATH):
        path = repo_root / relative_path
        if path.exists():
            values.update(_parse_xcconfig(path))
    return values


def _parse_xcconfig(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("//") or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def _combined_status(statuses: list[str]) -> str:
    if "blocked" in statuses:
        return "blocked"
    if "missing" in statuses:
        return "missing"
    if "partial" in statuses:
        return "partial"
    return "ready"


def _normalized_slot_status(status: str) -> str:
    if status in {"ready", "missing", "blocked", "partial"}:
        return status
    if status == "failed":
        return "blocked"
    return "blocked"


def _normalized_command_status(status: str) -> str:
    if status in {"ready", "missing", "blocked", "partial", "manual", "live"}:
        return status
    if status == "failed":
        return "blocked"
    return "blocked"


def _is_loopback_url(value: str) -> bool:
    lowered = value.lower()
    return (
        "://127.0.0.1" in lowered
        or "://localhost" in lowered
        or "://0.0.0.0" in lowered
    )


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


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item)]


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
