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
from myth_forge_api.operator_actions import BACKEND_DEVICE_DEMO_VALIDATED_ACTION

LaunchMode = Literal["local", "configured"]

IOS_BASE_CONFIG_PATH = Path("apps/mobile/ios/Config/Deployment.xcconfig")
IOS_DEPLOY_CONFIG_PATH = Path("apps/mobile/ios/Config/Deployment.local.xcconfig")


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
    report = {
        "kind": "ios_device_launch_certificate_report",
        "status": status,
        "mode": mode,
        "summary": _summary(device_gates),
        "certificate": certificate,
        "device_gates": device_gates,
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
) -> dict[str, Any]:
    return {
        "id": gate_id,
        "label": label,
        "status": _normalized_gate_status(status),
        "command": command,
        "required": required,
        "requires_consent": requires_consent,
        "notes": notes,
    }


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
        gate_id = str(gate.get("id", "gate"))
        command = str(gate.get("command", ""))
        if gate_id == "final_handoff_index":
            actions.append("run make final-handoff-index")
        elif gate_id == "ios_deploy_config":
            actions.append("provide iOS deploy config and rerun mobile deploy preflight")
        elif gate_id == "ios_deploy_runbook":
            actions.append("run make ios-deploy-runbook-local")
        elif gate_id == "final_demo_launch":
            actions.append("run make final-demo-launch")
        elif gate_id == "backend_device_server":
            actions.append("start backend-device-demo")
        elif gate_id == "mobile_deploy_preflight":
            actions.append(BACKEND_DEVICE_DEMO_VALIDATED_ACTION)
        elif gate_id == "xcode_build_gate":
            actions.append("resolve Xcode build gate outside the app")
        elif gate_id == "configured_final_acceptance":
            actions.append(CONFIGURED_FINAL_ACCEPTANCE_COST_REVIEW_ACTION)
        elif command:
            actions.append(f"run {command}")
        else:
            actions.append(f"unblock {gate_id}")
    return _dedupe(actions)[:6]


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
