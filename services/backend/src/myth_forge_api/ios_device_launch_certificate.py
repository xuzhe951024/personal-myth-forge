from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from myth_forge_api.configured_acceptance_command import (
    CONFIGURED_FINAL_ACCEPTANCE_COMMAND,
    CONFIGURED_FINAL_ACCEPTANCE_COST_REVIEW_ACTION,
)
from myth_forge_api.config import Settings, load_settings
from myth_forge_api.final_demo_launch import build_final_demo_launch_report
from myth_forge_api.final_handoff_commands import (
    FINAL_DEMO_LAUNCH_CONFIGURED_COMMAND,
    FINAL_DEMO_LAUNCH_LOCAL_COMMAND,
)
from myth_forge_api.final_handoff_index import build_final_handoff_index_report
from myth_forge_api.ios_deploy_runbook import build_ios_deploy_runbook_report
from myth_forge_api.operator_actions import (
    BACKEND_DEVICE_DEMO_VALIDATED_ACTION,
    normalize_operator_action,
    prefer_guarded_print_quote_handoff_actions,
    prefer_project_local_ios_deploy_handoff_actions,
)

LaunchMode = Literal["local", "configured"]

IOS_BASE_CONFIG_PATH = Path("apps/mobile/ios/Config/Deployment.xcconfig")
IOS_DEPLOY_CONFIG_PATH = Path("apps/mobile/ios/Config/Deployment.local.xcconfig")
CERTIFICATE_PROVIDER_ACTION_MARKERS = (
    "make provider-handoff",
    "live-provider-evidence",
    "provider-handoff",
)
CERTIFICATE_PRINT_ACTION_MARKERS = (
    "treatstock",
    "print-quote-configured",
    "print quote",
    "print-quote",
    "print_quote",
    "print-fulfillment-readiness",
    "/v1/print-quotes",
)
CERTIFICATE_IOS_HANDOFF_ACTION_MARKERS = (
    "ios-device-launch-rehearsal",
    "mobile-write-deploy-config-auto",
    "mobile-deploy-preflight",
    "deployment.local.xcconfig",
)


@dataclass(frozen=True)
class IOSDeviceLaunchCertificateResult:
    exit_code: int
    report: dict[str, Any]


def build_ios_device_launch_certificate_report(
    *,
    settings: Settings | None = None,
    repo_root: Path | str | None = None,
    final_demo_launch_report: dict[str, Any] | None = None,
) -> IOSDeviceLaunchCertificateResult:
    selected_settings = settings or load_settings()
    selected_repo_root = Path(repo_root) if repo_root is not None else _default_repo_root()
    deploy_values = _deploy_config_values(selected_repo_root)
    mode, mode_status = _selected_mode(deploy_values.get("PMF_FINAL_LAUNCH_MODE", ""))
    certificate = _certificate(deploy_values=deploy_values, mode=mode, mode_status=mode_status)
    final_handoff_index = build_final_handoff_index_report(
        settings=selected_settings,
        repo_root=selected_repo_root,
    ).report
    ios_deploy_runbook = build_ios_deploy_runbook_report(
        mode=mode,
        repo_root=selected_repo_root,
    )
    final_demo_launch = final_demo_launch_report or build_final_demo_launch_report(
        mode=mode,
        settings=selected_settings,
        repo_root=selected_repo_root,
        include_ios_device_launch_certificate=False,
    ).report
    device_gates = _device_gates(
        final_handoff_index=final_handoff_index,
        ios_deploy_config_status=_deploy_config_status(certificate),
        ios_deploy_runbook=ios_deploy_runbook,
        final_demo_launch=final_demo_launch,
    )
    status = _overall_status(device_gates)
    first_blocker = _first_blocker(device_gates)
    report = {
        "kind": "ios_device_launch_certificate_report",
        "status": status,
        "mode": mode,
        "summary": _summary(device_gates),
        "first_blocker": first_blocker,
        "next_action": _next_action(first_blocker),
        "certificate": certificate,
        "device_gates": device_gates,
        "device_action_bundle": _device_action_bundle(device_gates),
        "operator_actions": _operator_actions(device_gates),
        "final_handoff_index": _final_handoff_index_summary(final_handoff_index),
        "ios_deploy_runbook": _ios_deploy_runbook_summary(ios_deploy_runbook),
        "final_demo_launch": _final_demo_launch_summary(final_demo_launch),
        "operator_sequence": _operator_sequence(device_gates=device_gates, mode=mode),
        "commands": _commands(mode),
        "safety": _safety(),
    }
    sanitized = _sanitize_report(report, selected_repo_root)
    return IOSDeviceLaunchCertificateResult(
        exit_code=0 if sanitized["status"] == "ready" else 2,
        report=sanitized,
    )


def _certificate(
    *,
    deploy_values: dict[str, str],
    mode: LaunchMode,
    mode_status: str,
) -> dict[str, Any]:
    return {
        "development_team": _configured_fact(
            "DEVELOPMENT_TEAM",
            deploy_values.get("DEVELOPMENT_TEAM", ""),
        ),
        "product_bundle_identifier": _configured_fact(
            "PRODUCT_BUNDLE_IDENTIFIER",
            deploy_values.get("PRODUCT_BUNDLE_IDENTIFIER", ""),
        ),
        "backend_base_url": _backend_url_fact(
            deploy_values.get("PMF_BACKEND_BASE_URL", "")
        ),
        "final_launch_mode": {
            "key": "PMF_FINAL_LAUNCH_MODE",
            "status": mode_status,
            "configured": bool(deploy_values.get("PMF_FINAL_LAUNCH_MODE", "")),
            "mode": mode,
            "source": IOS_DEPLOY_CONFIG_PATH.as_posix(),
            "redacted": False,
        },
    }


def _configured_fact(key: str, value: str) -> dict[str, Any]:
    configured = bool(value)
    return {
        "key": key,
        "status": "ready" if configured else "missing",
        "configured": configured,
        "source": IOS_DEPLOY_CONFIG_PATH.as_posix(),
        "redacted": configured,
    }


def _backend_url_fact(value: str) -> dict[str, Any]:
    configured = bool(value)
    if not configured:
        status = "missing"
        classification = "missing_required_value"
    elif _is_loopback_url(value):
        status = "blocked"
        classification = "loopback_url"
    else:
        status = "ready"
        classification = None
    fact = {
        "key": "PMF_BACKEND_BASE_URL",
        "status": status,
        "configured": configured and status == "ready",
        "source": IOS_DEPLOY_CONFIG_PATH.as_posix(),
        "redacted": configured,
    }
    if classification:
        fact["classification"] = classification
    return fact


def _deploy_config_status(certificate: dict[str, Any]) -> str:
    statuses = [
        str(certificate["development_team"]["status"]),
        str(certificate["product_bundle_identifier"]["status"]),
        str(certificate["backend_base_url"]["status"]),
        str(certificate["final_launch_mode"]["status"]),
    ]
    return _combined_status(statuses)


def _device_gates(
    *,
    final_handoff_index: dict[str, Any],
    ios_deploy_config_status: str,
    ios_deploy_runbook: dict[str, Any],
    final_demo_launch: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        _gate(
            "final_handoff_index",
            "Final handoff index",
            str(final_handoff_index.get("status", "blocked")),
            "make final-handoff-index",
            required=True,
            notes=["Refreshes the unified local/configured handoff index."],
            operator_actions=_final_handoff_priority_actions(
                final_handoff_index,
                final_demo_launch,
            ),
        ),
        _gate(
            "ios_deploy_config",
            "iOS deploy config",
            ios_deploy_config_status,
            "make mobile-deploy-preflight",
            required=True,
            notes=["Requires Team ID, bundle id, final launch mode, and LAN backend URL."],
        ),
        _gate(
            "ios_deploy_runbook",
            "iOS deploy runbook",
            str(ios_deploy_runbook.get("status", "blocked")),
            "make ios-deploy-runbook-local",
            required=True,
            notes=["Partial is acceptable because Xcode/signing remain manual gates."],
        ),
        _gate(
            "final_demo_launch",
            "Final demo launch",
            str(final_demo_launch.get("overall_status", "blocked")),
            "make final-demo-launch",
            required=True,
            notes=["Partial is acceptable when only manual/live steps remain."],
        ),
        _gate(
            "backend_device_server",
            "Backend device server",
            "manual",
            "make backend-device-demo",
            required=False,
            notes=["Starts FastAPI on 0.0.0.0:8080 for iPhone LAN access."],
        ),
        _gate(
            "mobile_deploy_preflight",
            "Mobile deploy preflight",
            "manual" if ios_deploy_config_status == "ready" else ios_deploy_config_status,
            "make mobile-deploy-preflight",
            required=False,
            notes=["Operator-run backend health and deployment config check."],
        ),
        _gate(
            "xcode_build_gate",
            "Xcode build gate",
            "manual",
            "make mobile-xcode-build",
            required=False,
            notes=["Apple SDK license and signing state remain outside this report."],
        ),
        _gate(
            "configured_final_acceptance",
            "Configured final acceptance",
            "live",
            _configured_acceptance_command(),
            required=False,
            requires_consent=True,
            notes=["May call live providers and spend provider credits."],
        ),
    ]


def _gate(
    gate_id: str,
    label: str,
    status: str,
    command: str,
    *,
    required: bool,
    notes: list[str],
    requires_consent: bool = False,
    operator_actions: list[str] | None = None,
) -> dict[str, Any]:
    gate = {
        "id": gate_id,
        "label": label,
        "status": _normalized_gate_status(status),
        "command": command,
        "required": required,
        "requires_consent": requires_consent,
        "notes": notes,
    }
    if operator_actions:
        gate["operator_actions"] = operator_actions
    return gate


def _final_handoff_priority_actions(*reports: dict[str, Any]) -> list[str]:
    selected: list[str] = []
    for report in reports:
        actions = report.get("operator_actions")
        if not isinstance(actions, list):
            continue
        for action in actions:
            if not isinstance(action, str):
                continue
            stripped = normalize_operator_action(action.strip())
            if (
                _is_ios_handoff_action(stripped)
                or _is_provider_handoff_action(stripped)
                or _is_print_handoff_action(stripped)
                or _is_backend_device_demo_handoff_action(stripped)
            ):
                selected.append(stripped)
    preferred = prefer_project_local_ios_deploy_handoff_actions(_dedupe(selected))
    return _prioritize_final_handoff_child_actions(preferred)


def _prioritize_final_handoff_child_actions(actions: list[str]) -> list[str]:
    ios_actions = [action for action in actions if _is_ios_handoff_action(action)]
    backend_url_actions = [
        action for action in ios_actions if _is_backend_url_handoff_action(action)
    ]
    deploy_config_actions = [
        action for action in ios_actions if action not in backend_url_actions
    ]
    provider_actions = [
        action
        for action in actions
        if action not in ios_actions and _is_provider_handoff_action(action)
    ]
    print_actions = [
        action
        for action in actions
        if action not in ios_actions
        and action not in provider_actions
        and _is_print_handoff_action(action)
    ]
    priority_actions = set(
        deploy_config_actions + backend_url_actions + provider_actions + print_actions
    )
    remaining = [action for action in actions if action not in priority_actions]
    return (
        deploy_config_actions
        + backend_url_actions
        + provider_actions
        + print_actions
        + remaining
    )


def _is_ios_handoff_action(action: str) -> bool:
    lowered = action.lower()
    if "backend-device-demo" in lowered:
        return False
    if lowered in {"make mobile-deploy-preflight", "run make mobile-deploy-preflight"}:
        return False
    return any(marker in lowered for marker in CERTIFICATE_IOS_HANDOFF_ACTION_MARKERS)


def _is_provider_handoff_action(action: str) -> bool:
    lowered = action.lower()
    return any(marker in lowered for marker in CERTIFICATE_PROVIDER_ACTION_MARKERS)


def _is_print_handoff_action(action: str) -> bool:
    lowered = action.lower()
    return any(marker in lowered for marker in CERTIFICATE_PRINT_ACTION_MARKERS)


def _is_backend_device_demo_handoff_action(action: str) -> bool:
    return "backend-device-demo" in action.lower()


def _preferred_backend_device_demo_handoff_actions(actions: list[str]) -> list[str]:
    backend_actions = [
        action for action in actions if _is_backend_device_demo_handoff_action(action)
    ]
    validated_actions = [
        action for action in backend_actions if "mobile-deploy-preflight" in action.lower()
    ]
    return validated_actions or backend_actions


def _final_handoff_index_summary(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": report.get("kind", "final_handoff_index_report"),
        "status": report.get("status", "blocked"),
        "summary": report.get("summary", {}),
        "lanes_by_id": _status_rows(report.get("lanes_by_id", {})),
    }


def _ios_deploy_runbook_summary(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": report.get("kind", "ios_deploy_runbook_report"),
        "mode": report.get("mode", "local"),
        "status": report.get("status", "blocked"),
        "input_slots": [
            _compact_row(slot, fields=["id", "label", "status", "required", "source"])
            for slot in _dict_list(report.get("input_slots"))
        ],
        "command_sequence": [
            _compact_row(step, fields=["id", "label", "status", "command"])
            for step in _dict_list(report.get("command_sequence"))
        ],
    }


def _final_demo_launch_summary(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": report.get("kind", "final_demo_launch_report"),
        "mode": report.get("mode", "local"),
        "overall_status": report.get("overall_status", "blocked"),
        "summary": report.get("summary", {}),
        "phase_summary": report.get("phase_summary", {}),
        "first_blocker": _first_blocker_summary(report),
        "launch_phases": [
            _compact_row(phase, fields=["id", "label", "status", "command"])
            for phase in _dict_list(report.get("launch_phases"))
        ],
    }


def _first_blocker_summary(report: dict[str, Any]) -> dict[str, Any] | None:
    blocker = report.get("first_blocker")
    if not isinstance(blocker, dict):
        return None
    compact = _compact_row(
        blocker,
        fields=[
            "id",
            "label",
            "status",
            "classification",
            "command",
            "detail",
            "source",
            "source_id",
        ],
    )
    return compact or None


def _operator_sequence(
    *,
    device_gates: list[dict[str, Any]],
    mode: LaunchMode,
) -> list[dict[str, Any]]:
    by_id = {gate["id"]: gate for gate in device_gates}
    sequence = [
        _sequence_step(
            "ios_device_launch_certificate",
            "Refresh device launch certificate",
            "ready",
            "make ios-device-launch-certificate",
            "writes this ignored JSON certificate",
        ),
        _sequence_step(
            "final_handoff_index",
            "Refresh final handoff index",
            str(by_id["final_handoff_index"]["status"]),
            "make final-handoff-index",
            "confirms local rehearsal and configured preflight lanes",
        ),
        _sequence_step(
            "backend_device_server",
            "Start backend on LAN",
            "manual",
            "make backend-device-demo",
            "keeps uvicorn running for iPhone requests",
        ),
        _sequence_step(
            "mobile_deploy_preflight",
            "Run mobile deploy preflight",
            str(by_id["mobile_deploy_preflight"]["status"]),
            "make mobile-deploy-preflight",
            "checks iPhone-reachable backend health",
        ),
        _sequence_step(
            "xcode_build_gate",
            "Run Xcode build gate",
            "manual",
            "make mobile-xcode-build",
            "validates local Apple SDK and signing state",
        ),
    ]
    if mode == "configured":
        sequence.append(
            _sequence_step(
                "configured_final_acceptance",
                "Run configured final acceptance",
                "live",
                _configured_acceptance_command(),
                "requires explicit live provider cost consent",
                requires_consent=True,
            )
        )
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
        "status": _normalized_gate_status(status),
        "command": command,
        "purpose": purpose,
        "requires_consent": requires_consent,
    }


def _commands(mode: LaunchMode) -> list[str]:
    final_demo_launch_command = (
        FINAL_DEMO_LAUNCH_CONFIGURED_COMMAND
        if mode == "configured"
        else FINAL_DEMO_LAUNCH_LOCAL_COMMAND
    )
    commands = [
        "make ios-device-launch-certificate",
        "make final-handoff-index",
        "make backend-device-demo",
        "make mobile-deploy-preflight",
        "make mobile-xcode-build",
        final_demo_launch_command,
    ]
    if mode == "configured":
        commands.append(_configured_acceptance_command())
    return commands


def _configured_acceptance_command() -> str:
    return CONFIGURED_FINAL_ACCEPTANCE_COMMAND


def _overall_status(device_gates: list[dict[str, Any]]) -> str:
    required_statuses = [str(gate["status"]) for gate in device_gates if gate["required"]]
    if any(status in {"missing", "blocked"} for status in required_statuses):
        return "blocked"
    return "ready"


def _summary(device_gates: list[dict[str, Any]]) -> dict[str, int]:
    statuses = ["ready", "missing", "blocked", "manual", "partial", "live"]
    return {
        status: sum(1 for gate in device_gates if gate["status"] == status)
        for status in statuses
    }


def _operator_actions(device_gates: list[dict[str, Any]]) -> list[str]:
    actions: list[str] = []
    for gate in device_gates:
        status = str(gate.get("status", ""))
        if status not in {"missing", "blocked", "manual", "live"}:
            continue
        actions.append(_operator_action_for_gate(gate))
        nested_actions = gate.get("operator_actions")
        if isinstance(nested_actions, list):
            actions.extend(str(action) for action in nested_actions)
    deduped = prefer_guarded_print_quote_handoff_actions(_dedupe(actions))
    return _prioritize_certificate_operator_actions(deduped)[:6]


def _device_action_bundle(device_gates: list[dict[str, Any]]) -> dict[str, Any]:
    actions = [_device_action(gate) for gate in device_gates]
    return {
        "id": "ios_device_launch_certificate_actions",
        "label": "iOS Device Launch Certificate Actions",
        "status": _overall_status(device_gates),
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


def _device_action(gate: dict[str, Any]) -> dict[str, Any]:
    status = str(gate.get("status", "blocked"))
    command = _operator_action_for_gate(gate)
    validation_command = str(gate.get("command", "make ios-device-launch-certificate"))
    action: dict[str, Any] = {
        "id": str(gate.get("id", "device_gate")),
        "label": str(gate.get("label", "Device gate")),
        "status": status,
        "classification": _device_action_classification(status, gate),
        "command": command,
        "detail": _gate_detail(gate),
        "required": bool(gate.get("required")),
        "requires_consent": bool(gate.get("requires_consent")),
        "manual": status != "ready",
        "provider_calls": False,
        "global_action": False,
        "xcode_or_signing": _is_xcode_or_signing_gate(gate),
        "validation_command": validation_command,
    }
    if status in {"missing", "blocked", "manual", "live"}:
        action["next_action"] = {
            "id": action["id"],
            "label": action["label"],
            "status": action["status"],
            "command": command,
            "detail": action["detail"],
            "source": "device_action_bundle",
            "validation_command": validation_command,
        }
    return action


def _device_action_classification(status: str, gate: dict[str, Any]) -> str:
    if status == "ready":
        return "ready"
    if status in {"missing", "blocked"}:
        return f"device_gate_{status}"
    if _is_xcode_or_signing_gate(gate):
        return "manual_xcode_or_signing_required"
    if gate.get("requires_consent"):
        return "live_provider_consent_required"
    if status == "manual":
        return "manual_device_step_required"
    if status == "partial":
        return "partial_device_gate"
    return f"device_gate_{status}"


def _first_device_action(actions: list[dict[str, Any]]) -> dict[str, Any] | None:
    for action in actions:
        if not action.get("required"):
            continue
        if action.get("status") in {"missing", "blocked"}:
            return action
    return None


def _device_action_summary(actions: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "actions": len(actions),
        "ready": sum(1 for action in actions if action["status"] == "ready"),
        "missing": sum(1 for action in actions if action["status"] == "missing"),
        "blocked": sum(1 for action in actions if action["status"] == "blocked"),
        "manual": sum(1 for action in actions if action.get("manual") is True),
        "partial": sum(1 for action in actions if action["status"] == "partial"),
        "live": sum(1 for action in actions if action["status"] == "live"),
        "provider_calls": sum(1 for action in actions if action["provider_calls"] is True),
        "global_actions": sum(1 for action in actions if action["global_action"] is True),
        "xcode_or_signing": sum(
            1 for action in actions if action["xcode_or_signing"] is True
        ),
    }


def _is_xcode_or_signing_gate(gate: dict[str, Any]) -> bool:
    return str(gate.get("id", "")) == "xcode_build_gate"


def _prioritize_certificate_operator_actions(actions: list[str]) -> list[str]:
    if not actions:
        return []
    first_actions = actions[:1]
    rest = actions[1:]
    provider_actions = [
        action for action in rest if _is_provider_handoff_action(action)
    ]
    print_actions = [action for action in rest if _is_print_handoff_action(action)]
    raw_backend_actions = [
        action for action in rest if _is_backend_device_demo_handoff_action(action)
    ]
    backend_actions = _preferred_backend_device_demo_handoff_actions(rest)
    backend_url_actions = [
        action
        for action in rest
        if action not in raw_backend_actions and _is_backend_url_handoff_action(action)
    ]
    priority_actions = set(
        provider_actions + print_actions + raw_backend_actions + backend_url_actions
    )
    remaining = [action for action in rest if action not in priority_actions]
    if _is_mobile_deploy_handoff_action(first_actions[0]):
        return (
            first_actions
            + backend_actions
            + backend_url_actions
            + provider_actions
            + print_actions
            + remaining
        )
    return first_actions + provider_actions + print_actions + backend_actions + remaining


def _is_backend_url_handoff_action(action: str) -> bool:
    lowered = action.lower()
    return "pmf_backend_base_url" in lowered or "iphone-reachable lan url" in lowered


def _is_mobile_deploy_handoff_action(action: str) -> bool:
    lowered = action.lower()
    return (
        "mobile-deploy-preflight" in lowered
        and "mobile-write-deploy-config-auto" in lowered
        and not _is_backend_device_demo_handoff_action(action)
    )


def _first_blocker(device_gates: list[dict[str, Any]]) -> dict[str, Any] | None:
    for gate in device_gates:
        if not gate.get("required"):
            continue
        status = str(gate.get("status", ""))
        if status not in {"missing", "blocked"}:
            continue
        return {
            "id": str(gate.get("id", "device_gate")),
            "label": str(gate.get("label", "Device gate")),
            "status": status,
            "classification": f"device_gate_{status}",
            "command": _operator_action_for_gate(gate),
            "detail": _gate_detail(gate),
            "validation_command": str(
                gate.get("command", "make ios-device-launch-certificate")
            ),
        }
    return None


def _next_action(first_blocker: dict[str, Any] | None) -> dict[str, Any] | None:
    if first_blocker is None:
        return None
    return {**first_blocker, "source": "first_blocker"}


def _operator_action_for_gate(gate: dict[str, Any]) -> str:
    gate_id = str(gate.get("id", "gate"))
    command = str(gate.get("command", ""))
    nested_actions = gate.get("operator_actions")
    if gate_id == "final_handoff_index" and isinstance(nested_actions, list):
        preferred_action = _preferred_device_operator_action(nested_actions)
        if preferred_action:
            return preferred_action
    if gate_id == "final_handoff_index":
        return "run make final-handoff-index"
    if gate_id == "ios_deploy_config":
        return "provide iOS deploy config and rerun mobile deploy preflight"
    if gate_id == "ios_deploy_runbook":
        return "run make ios-deploy-runbook-local"
    if gate_id == "final_demo_launch":
        return "run make final-demo-launch"
    if gate_id == "backend_device_server":
        return "start backend-device-demo"
    if gate_id == "mobile_deploy_preflight":
        return BACKEND_DEVICE_DEMO_VALIDATED_ACTION
    if gate_id == "xcode_build_gate":
        return "resolve Xcode build gate outside the app"
    if gate_id == "configured_final_acceptance":
        return CONFIGURED_FINAL_ACCEPTANCE_COST_REVIEW_ACTION
    if command:
        return f"run {command}"
    return f"unblock {gate_id}"


def _preferred_device_operator_action(actions: list[Any]) -> str:
    normalized_actions = [
        str(action).strip()
        for action in actions
        if isinstance(action, str) and action.strip()
    ]
    for action in normalized_actions:
        if _is_device_operator_action(action):
            return action
    return normalized_actions[0] if normalized_actions else ""


def _is_device_operator_action(action: str) -> bool:
    lowered = action.lower()
    if _is_backend_device_demo_handoff_action(action):
        return True
    if _is_ios_handoff_action(action):
        return True
    if "mobile-deploy-preflight" in lowered:
        return True
    if "mobile-xcode-build" in lowered or "xcode build" in lowered:
        return True
    return False


def _gate_detail(gate: dict[str, Any]) -> str:
    notes = gate.get("notes")
    if isinstance(notes, list) and notes:
        return str(notes[0])
    return str(gate.get("label", gate.get("id", "Device gate")))


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        deduped.append(value)
    return deduped


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


def _selected_mode(value: str) -> tuple[LaunchMode, str]:
    normalized = (value or "local").lower()
    if normalized == "configured":
        return "configured", "ready"
    if normalized == "local":
        return "local", "ready"
    return "local", "blocked"


def _combined_status(statuses: list[str]) -> str:
    normalized = [_normalized_gate_status(status) for status in statuses]
    if "blocked" in normalized:
        return "blocked"
    if "missing" in normalized:
        return "blocked"
    if "partial" in normalized:
        return "partial"
    return "ready"


def _normalized_gate_status(status: str) -> str:
    if status in {"ready", "missing", "blocked", "manual", "partial", "live"}:
        return status
    if status in {"passed", "succeeded"}:
        return "ready"
    if status in {"failed", "error"}:
        return "blocked"
    return "blocked"


def _is_loopback_url(value: str) -> bool:
    lowered = value.lower()
    return (
        "://127.0.0.1" in lowered
        or "://localhost" in lowered
        or "://0.0.0.0" in lowered
    )


def _status_rows(value: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(value, dict):
        return {}
    rows: dict[str, dict[str, Any]] = {}
    for row_id, row in value.items():
        if not isinstance(row, dict):
            continue
        rows[str(row_id)] = _compact_row(
            row,
            fields=["id", "label", "status", "required", "requires_consent", "command"],
        )
    return rows


def _compact_row(row: dict[str, Any], *, fields: list[str]) -> dict[str, Any]:
    return {field: row[field] for field in fields if field in row}


def _dict_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


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
        r"https?://(?:pay|checkout)\.[^\s,;\"']+",
        r"https?://(?:10|127|172|192)\.[0-9.]+(?::[0-9]+)?[^\s,;\"']*",
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


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parents[4]
