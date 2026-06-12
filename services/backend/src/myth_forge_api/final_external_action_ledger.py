from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from myth_forge_api.configured_acceptance_command import CONFIGURED_FINAL_ACCEPTANCE_COMMAND
from myth_forge_api.config import Settings, load_settings
from myth_forge_api.final_resource_apply_preview import (
    build_final_resource_apply_preview_report,
)
from myth_forge_api.final_resource_requirements import (
    build_final_resource_requirements_report,
)
from myth_forge_api.ios_deploy_runbook import build_ios_deploy_runbook_report
from myth_forge_api.live_provider_evidence import build_live_provider_evidence_report
from myth_forge_api.operator_actions import normalize_operator_action
from myth_forge_api.print_fulfillment_readiness import (
    build_print_fulfillment_readiness_report,
)

OPERATOR_SEQUENCE = [
    "make final-resource-requirements",
    "make final-resources-preflight",
    "make final-resource-repair-preview",
    "make final-resource-repair",
    "make final-resource-apply-preview",
    "make final-apply-resources",
    "make backend-device-demo",
    "make mobile-deploy-preflight",
    "make ios-device-launch-rehearsal",
    "make live-provider-evidence",
    "make print-fulfillment-readiness",
    "make final-showcase-readiness",
]
IOS_DEPLOY_DESTINATION = "apps/mobile/ios/Config/Deployment.local.xcconfig"
IOS_DEPLOY_VALIDATION_COMMAND = "make mobile-deploy-preflight"


@dataclass(frozen=True)
class FinalExternalActionLedgerResult:
    exit_code: int
    report: dict[str, Any]


def build_final_external_action_ledger_report(
    *,
    settings: Settings | None = None,
    repo_root: Path | str | None = None,
) -> FinalExternalActionLedgerResult:
    selected_settings = settings or load_settings()
    selected_repo_root = Path(repo_root) if repo_root is not None else _default_repo_root()
    requirements = build_final_resource_requirements_report(
        repo_root=selected_repo_root,
    ).report
    apply_preview = build_final_resource_apply_preview_report(
        repo_root=selected_repo_root,
    ).report
    live_provider_evidence = build_live_provider_evidence_report(
        repo_root=selected_repo_root,
    ).report
    print_fulfillment = build_print_fulfillment_readiness_report(
        settings=selected_settings,
        repo_root=selected_repo_root,
    ).report
    ios_deploy_runbook = build_ios_deploy_runbook_report(
        mode="local",
        repo_root=selected_repo_root,
    )
    action_groups = _action_groups(
        requirements=requirements,
        apply_preview=apply_preview,
        live_provider_evidence=live_provider_evidence,
        print_fulfillment=print_fulfillment,
        ios_deploy_runbook=ios_deploy_runbook,
    )
    actions = [action for group in action_groups for action in group["actions"]]
    summary = _summary(action_groups=action_groups, actions=actions)
    status = _overall_status(action_groups)
    report = {
        "kind": "final_external_action_ledger_report",
        "status": status,
        "summary": summary,
        "action_groups": action_groups,
        "actions_by_id": {action["id"]: action for action in actions},
        "operator_sequence": OPERATOR_SEQUENCE,
        "source_reports": {
            "final_resource_requirements": _source_summary(requirements),
            "final_resource_apply_preview": _source_summary(apply_preview),
            "final_resource_repair": _repair_source_summary(apply_preview),
            "live_provider_evidence": _source_summary(live_provider_evidence),
            "print_fulfillment_readiness": _source_summary(print_fulfillment),
            "ios_deploy_runbook": _source_summary(ios_deploy_runbook),
        },
        "operator_actions": _operator_actions(action_groups),
        "safety": _safety(),
    }
    sanitized = _sanitize_report(report, selected_repo_root)
    return FinalExternalActionLedgerResult(
        exit_code=0 if sanitized["status"] == "ready" else 2,
        report=sanitized,
    )


def _action_groups(
    *,
    requirements: dict[str, Any],
    apply_preview: dict[str, Any],
    live_provider_evidence: dict[str, Any],
    print_fulfillment: dict[str, Any],
    ios_deploy_runbook: dict[str, Any],
) -> list[dict[str, Any]]:
    groups = [
        _group(
            group_id="resource_inputs",
            label="Resource inputs",
            actions=[
                _resource_action(requirement)
                for requirement in requirements.get("requirements", [])
                if isinstance(requirement, dict)
            ],
        ),
        _group(
            group_id="safe_local_writes",
            label="Safe local writes",
            actions=_safe_local_write_actions(apply_preview),
        ),
        _group(
            group_id="live_provider_costs",
            label="Live provider costs",
            actions=_live_provider_cost_actions(
                live_provider_evidence=live_provider_evidence,
                print_fulfillment=print_fulfillment,
            ),
        ),
        _group(
            group_id="global_machine_actions",
            label="Global machine actions",
            actions=_global_machine_actions(),
        ),
        _group(
            group_id="device_runtime_actions",
            label="Device runtime actions",
            actions=_device_runtime_actions(ios_deploy_runbook),
        ),
    ]
    return groups


def _resource_action(requirement: dict[str, Any]) -> dict[str, Any]:
    slot_id = str(requirement["id"])
    required = bool(requirement.get("required"))
    status = str(requirement.get("status", "missing"))
    if status == "optional":
        detail = "Optional final resource input is not required for the first demo."
    elif status == "ready":
        detail = "Final resource input is configured."
    elif status == "blocked":
        detail = str(requirement.get("notes") or "Final resource input is blocked.")
    else:
        detail = str(requirement.get("notes") or "Final resource input is missing.")
    return _action(
        action_id=f"provide_{slot_id}",
        group_id="resource_inputs",
        label=str(requirement.get("label") or slot_id),
        status=status,
        command=_resource_validation_command(requirement),
        detail=detail,
        required=required,
        secret=bool(requirement.get("secret")),
        requires_user_input=required or status in {"missing", "blocked"},
        destination=str(requirement.get("destination", "")),
        classification=str(requirement.get("classification", status)),
    )


def _resource_validation_command(requirement: dict[str, Any]) -> str:
    if str(requirement.get("destination", "")) == IOS_DEPLOY_DESTINATION:
        return IOS_DEPLOY_VALIDATION_COMMAND
    return str(
        requirement.get("validation_command") or "make final-resource-requirements"
    )


def _safe_local_write_actions(apply_preview: dict[str, Any]) -> list[dict[str, Any]]:
    preview_status = _normalized_status(str(apply_preview.get("status", "missing")))
    apply_status = "ready" if preview_status == "ready" else "blocked"
    repair_action = _final_resource_repair_action(
        _repair_source_summary(apply_preview),
    )
    return [
        repair_action,
        _action(
            action_id="preview_final_resource_apply",
            group_id="safe_local_writes",
            label="Preview final resource apply",
            status=preview_status,
            command="make final-resource-apply-preview",
            detail=(
                "Review backend .env and iOS deploy config writes without running "
                "writer scripts."
            ),
            safe_local_write=True,
        ),
        _action(
            action_id="apply_final_resources",
            group_id="safe_local_writes",
            label="Apply final resources",
            status=apply_status,
            command="make final-apply-resources",
            detail=(
                "Write ignored backend and iOS local config files after preview is ready."
            ),
            safe_local_write=True,
            writes_repo_local_files=True,
        ),
    ]


def _final_resource_repair_action(repair_source: dict[str, Any]) -> dict[str, Any]:
    repair_status = str(repair_source.get("status", "missing"))
    if repair_status == "repairable":
        return _action(
            action_id="repair_final_resources",
            group_id="safe_local_writes",
            label="Repair final resources",
            status="blocked",
            command="make final-resource-repair",
            detail="Clear stale final resource placeholders before preview/apply.",
            safe_local_write=True,
            writes_repo_local_files=True,
            classification="placeholder_value",
        )
    if repair_status == "missing":
        return _action(
            action_id="repair_final_resources",
            group_id="safe_local_writes",
            label="Repair final resources",
            status="missing",
            command="make final-resource-init",
            detail="Create the ignored final resources file before repair can run.",
            safe_local_write=True,
            writes_repo_local_files=True,
            classification="missing_final_resources",
        )
    if repair_status == "blocked":
        return _action(
            action_id="repair_final_resources",
            group_id="safe_local_writes",
            label="Repair final resources",
            status="blocked",
            command="make final-resource-repair-preview",
            detail="Review the blocked repair report before changing final resources.",
            safe_local_write=True,
            classification="repair_blocked",
        )
    if repair_status in {"ready", "repaired"}:
        return _action(
            action_id="repair_final_resources",
            group_id="safe_local_writes",
            label="Repair final resources",
            status="ready",
            command="make final-resource-repair-preview",
            detail="No stale final resource placeholders need repair.",
            safe_local_write=True,
            classification="no_repair_needed",
        )
    return _action(
        action_id="repair_final_resources",
        group_id="safe_local_writes",
        label="Repair final resources",
        status="blocked",
        command="make final-resource-repair-preview",
        detail="Refresh the repair preview because repair status is unavailable.",
        safe_local_write=True,
        classification="repair_status_unknown",
    )


def _live_provider_cost_actions(
    *,
    live_provider_evidence: dict[str, Any],
    print_fulfillment: dict[str, Any],
) -> list[dict[str, Any]]:
    live_status = "ready" if live_provider_evidence.get("status") == "ready" else "live"
    print_status = "ready" if print_fulfillment.get("status") == "ready" else "live"
    return [
        _live_action(
            action_id="run_live_provider_evidence",
            label="Refresh live provider evidence",
            status=live_status,
            command="make live-provider-evidence",
            detail="Refresh configured Meshy/OpenAI evidence after cost consent.",
        ),
        _live_action(
            action_id="run_configured_3d_evaluation",
            label="Run configured 3D evaluation",
            status=live_status,
            command="make backend-evaluate-3d-configured",
            detail="Calls Meshy and may spend Meshy credits.",
        ),
        _live_action(
            action_id="run_configured_npc_evaluation",
            label="Run configured NPC evaluation",
            status=live_status,
            command="make backend-evaluate-npc-configured",
            detail="Calls OpenAI and may spend API credits.",
        ),
        _live_action(
            action_id="run_configured_final_acceptance",
            label="Run configured final acceptance",
            status=live_status,
            command=CONFIGURED_FINAL_ACCEPTANCE_COMMAND,
            detail="Calls live providers only with explicit consent flag.",
        ),
        _live_action(
            action_id="refresh_configured_treatstock_quote",
            label="Refresh configured Treatstock quote",
            status=print_status,
            command="make print-fulfillment-readiness",
            detail="Configured print quote evidence may call a print provider.",
        ),
    ]


def _live_action(
    *,
    action_id: str,
    label: str,
    status: str,
    command: str,
    detail: str,
) -> dict[str, Any]:
    return _action(
        action_id=action_id,
        group_id="live_provider_costs",
        label=label,
        status=status,
        command=command,
        detail=detail,
        live_provider_call=True,
        requires_cost_consent=True,
    )


def _global_machine_actions() -> list[dict[str, Any]]:
    return [
        _global_action(
            action_id="accept_apple_sdk_license",
            label="Accept Apple SDK license",
            command="accept Apple SDK license manually on this Mac",
            detail="Requires explicit user confirmation because it changes machine state.",
        ),
        _global_action(
            action_id="configure_apple_signing",
            label="Configure Apple signing",
            command="configure Apple Team ID, bundle id, certificates, and device trust manually",
            detail="Signing, certificates, device trust, and keychain state are outside repo control.",
        ),
        _global_action(
            action_id="run_xcode_build_gate",
            label="Run Xcode build gate",
            command="make mobile-xcode-build",
            detail="May invoke Xcode signing and Apple SDK global state.",
        ),
    ]


def _global_action(
    *,
    action_id: str,
    label: str,
    command: str,
    detail: str,
) -> dict[str, Any]:
    return _action(
        action_id=action_id,
        group_id="global_machine_actions",
        label=label,
        status="manual",
        command=command,
        detail=detail,
        requires_user_confirmation=True,
        global_action=True,
        xcode_or_signing=True,
    )


def _device_runtime_actions(ios_deploy_runbook: dict[str, Any]) -> list[dict[str, Any]]:
    runbook_status = _normalized_status(str(ios_deploy_runbook.get("status", "blocked")))
    deploy_preflight_status = "ready" if runbook_status == "ready" else "blocked"
    return [
        _action(
            action_id="start_backend_device_demo",
            group_id="device_runtime_actions",
            label="Start backend device server",
            status="manual",
            command="make backend-device-demo",
            detail="Starts uvicorn on the LAN for iPhone testing.",
        ),
        _action(
            action_id="run_mobile_deploy_preflight",
            group_id="device_runtime_actions",
            label="Run mobile deploy preflight",
            status=deploy_preflight_status,
            command="make mobile-deploy-preflight",
            detail="Checks iPhone-reachable backend health and local deploy config.",
        ),
        _action(
            action_id="run_ios_device_launch_rehearsal",
            group_id="device_runtime_actions",
            label="Run iOS device launch rehearsal",
            status=runbook_status,
            command="make ios-device-launch-rehearsal",
            detail="Refreshes local launch and deploy rehearsal reports without installing to a device.",
        ),
        _action(
            action_id="connect_iphone_on_lan",
            group_id="device_runtime_actions",
            label="Connect iPhone on LAN",
            status="manual",
            command="connect iPhone to the same LAN and open the development build",
            detail="Physical device availability remains a manual runtime action.",
        ),
    ]


def _action(
    *,
    action_id: str,
    group_id: str,
    label: str,
    status: str,
    command: str,
    detail: str,
    required: bool = True,
    secret: bool = False,
    requires_user_input: bool = False,
    requires_user_confirmation: bool = False,
    requires_cost_consent: bool = False,
    global_action: bool = False,
    xcode_or_signing: bool = False,
    live_provider_call: bool = False,
    safe_local_write: bool = False,
    writes_repo_local_files: bool = False,
    destination: str | None = None,
    classification: str | None = None,
) -> dict[str, Any]:
    action = {
        "id": action_id,
        "group_id": group_id,
        "label": label,
        "status": status,
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
    if destination:
        action["destination"] = destination
    if classification:
        action["classification"] = classification
    return action


def _group(
    *,
    group_id: str,
    label: str,
    actions: list[dict[str, Any]],
) -> dict[str, Any]:
    summary = _action_summary(actions)
    return {
        "id": group_id,
        "label": label,
        "status": _group_status(group_id=group_id, summary=summary),
        "summary": summary,
        "actions": actions,
    }


def _action_summary(actions: list[dict[str, Any]]) -> dict[str, int]:
    statuses = [str(action["status"]) for action in actions]
    return {
        "actions": len(actions),
        "ready": statuses.count("ready"),
        "missing": statuses.count("missing"),
        "blocked": statuses.count("blocked"),
        "manual": statuses.count("manual"),
        "live": statuses.count("live"),
        "partial": statuses.count("partial"),
        "optional": statuses.count("optional"),
        "secret": sum(1 for action in actions if action["secret"]),
        "requires_user_confirmation": sum(
            1 for action in actions if action["requires_user_confirmation"]
        ),
        "requires_cost_consent": sum(
            1 for action in actions if action["requires_cost_consent"]
        ),
    }


def _group_status(*, group_id: str, summary: dict[str, int]) -> str:
    if group_id == "global_machine_actions" and summary["manual"]:
        return "manual"
    if group_id == "live_provider_costs" and summary["live"]:
        return "live"
    if summary["blocked"]:
        return "blocked"
    if summary["missing"]:
        return "blocked" if group_id == "resource_inputs" else "missing"
    if summary["manual"]:
        return "manual"
    if summary["live"]:
        return "live"
    if summary["partial"]:
        return "partial"
    return "ready"


def _summary(
    *,
    action_groups: list[dict[str, Any]],
    actions: list[dict[str, Any]],
) -> dict[str, int]:
    action_summary = _action_summary(actions)
    return {
        "groups": len(action_groups),
        **action_summary,
        "global": sum(1 for action in actions if action["global"]),
        "safe_local_write": sum(1 for action in actions if action["safe_local_write"]),
        "live_provider_call": sum(
            1 for action in actions if action["live_provider_call"]
        ),
    }


def _overall_status(action_groups: list[dict[str, Any]]) -> str:
    groups = {group["id"]: group for group in action_groups}
    resource_status = groups["resource_inputs"]["status"]
    global_status = groups["global_machine_actions"]["status"]
    if resource_status == "blocked" or global_status in {"manual", "blocked"}:
        return "blocked"
    if any(group["status"] in {"blocked", "missing"} for group in action_groups):
        return "blocked"
    if any(group["status"] in {"manual", "live", "partial"} for group in action_groups):
        return "partial"
    return "ready"


def _operator_actions(action_groups: list[dict[str, Any]]) -> list[str]:
    actions: list[str] = []
    for group in action_groups:
        for action in group["actions"]:
            if action["status"] == "missing" and action["requires_user_input"]:
                actions.append(_missing_user_input_action_text(action))
            elif action["status"] == "blocked":
                actions.append(normalize_operator_action(str(action["command"])))
            elif action["requires_cost_consent"] and action["status"] == "live":
                actions.append(f"approve live provider cost before {action['command']}")
            elif action["requires_user_confirmation"] and action["status"] == "manual":
                actions.append(f"confirm global/manual action before {action['command']}")
    return _dedupe(actions)


def _missing_user_input_action_text(action: dict[str, Any]) -> str:
    slot = str(action["id"]).removeprefix("provide_")
    destination = Path(str(action.get("destination", ""))).name
    command = str(action.get("command", "")).strip()
    parts = [f"provide {slot}"]
    if destination:
        parts[0] = f"{parts[0]} in {destination}"
    if command:
        parts.append(f"rerun {command}")
    return "; ".join(parts)


def _source_summary(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": report.get("kind", "unknown"),
        "status": report.get("status") or report.get("overall_status") or "unknown",
        "summary": report.get("summary", {}),
    }


def _repair_source_summary(apply_preview: dict[str, Any]) -> dict[str, Any]:
    source_reports = apply_preview.get("source_reports", {})
    if isinstance(source_reports, dict):
        repair_source = source_reports.get("final_resource_repair", {})
        if isinstance(repair_source, dict):
            return {
                "kind": repair_source.get("kind", "final_resource_repair_report"),
                "status": repair_source.get("status", "unknown"),
                "summary": repair_source.get("summary", {}),
            }
    return {
        "kind": "final_resource_repair_report",
        "status": "unknown",
        "summary": {},
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
        "local_paths_in_report": False,
        "requires_user_confirmation_for_global_actions": True,
        "requires_cost_consent_for_live_actions": True,
    }


def _normalized_status(status: str) -> str:
    if status in {"ready", "missing", "blocked", "partial", "manual", "live", "optional"}:
        return status
    if status in {"passed", "succeeded"}:
        return "ready"
    return "blocked"


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
        r"sk-[A-Za-z0-9_-]+",
        r"meshy-secret-[A-Za-z0-9_-]+",
        r"treatstock-secret-[A-Za-z0-9_-]+",
        r"Bearer\s+[A-Za-z0-9._~+/\-=:-]+",
        r"api[_-]?key\s*[=:]\s*[^\s,;\"']+",
        r"https?://pay\.[^\s,;\"']+",
        r"https?://checkout\.[^\s,;\"']+",
        r"file://[^\s,;\"']+",
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
