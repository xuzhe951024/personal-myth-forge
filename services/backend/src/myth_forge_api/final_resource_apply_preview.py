from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from myth_forge_api.final_resource_requirements import (
    build_final_resource_requirements_report,
)
from myth_forge_api.final_resource_repair import build_final_resource_repair_report
from myth_forge_api.final_resources_preflight import (
    DEFAULT_RESOURCES_PATH,
    SECRET_KEYS,
    build_final_resources_preflight_report,
)

BACKEND_ENV_DESTINATION = "services/backend/.env"
IOS_DEPLOY_DESTINATION = "apps/mobile/ios/Config/Deployment.local.xcconfig"
BACKEND_WRITER = "services/backend/scripts/write_backend_env.sh"
IOS_WRITER = "apps/mobile/ios/scripts/write_deploy_local_config.sh"

BASE_COMMANDS = [
    "make final-resource-apply-preview",
    "make final-resources-preflight",
    "make final-apply-resources",
]
REPAIR_COMMANDS = [
    "make final-resource-repair-preview",
    "make final-resource-repair",
]

BACKEND_SLOTS = {
    "MESHY_API_KEY": ("MESHY_API_KEY",),
    "OPENAI_API_KEY": ("OPENAI_API_KEY",),
    "OPENAI_API_BASE_URL": ("OPENAI_API_BASE_URL",),
    "PRINT_PROVIDER": ("PRINT_PROVIDER",),
    "TREATSTOCK_API_KEY": ("TREATSTOCK_API_KEY",),
    "TREATSTOCK_API_BASE_URL": ("TREATSTOCK_API_BASE_URL",),
    "SCULPTEO_API_KEY": ("SCULPTEO_API_KEY",),
    "CAPTURE_STORAGE_DIR": ("CAPTURE_STORAGE_DIR",),
    "MYTH_SESSION_STORAGE_DIR": ("MYTH_SESSION_STORAGE_DIR",),
}
IOS_SLOTS = {
    "DEVELOPMENT_TEAM": ("DEVELOPMENT_TEAM",),
    "PRODUCT_BUNDLE_IDENTIFIER": ("PRODUCT_BUNDLE_IDENTIFIER",),
    "PMF_BACKEND_BASE_URL": ("PMF_BACKEND_BASE_URL",),
    "PMF_FINAL_LAUNCH_MODE": ("PMF_FINAL_LAUNCH_MODE",),
}
REQUIRED_IF_MISSING_FILE = {
    "MESHY_API_KEY",
    "OPENAI_API_KEY",
    "DEVELOPMENT_TEAM",
    "PRODUCT_BUNDLE_IDENTIFIER",
    "PMF_BACKEND_BASE_URL",
}


@dataclass(frozen=True)
class FinalResourceApplyPreviewResult:
    exit_code: int
    report: dict[str, Any]


def build_final_resource_apply_preview_report(
    *,
    repo_root: Path | str | None = None,
    resources_file: Path | str | None = None,
) -> FinalResourceApplyPreviewResult:
    selected_repo_root = Path(repo_root) if repo_root is not None else _default_repo_root()
    selected_resources_file = Path(resources_file) if resources_file is not None else None
    preflight_result = build_final_resources_preflight_report(
        repo_root=selected_repo_root,
        resources_file=selected_resources_file,
    )
    requirements_result = build_final_resource_requirements_report(
        repo_root=selected_repo_root,
        resources_file=selected_resources_file,
    )
    repair_result = build_final_resource_repair_report(
        repo_root=selected_repo_root,
        resources_file=selected_resources_file,
        apply=False,
    )
    preflight_report = preflight_result.report
    repair_report = repair_result.report
    preflight_items = {
        item["id"]: item for item in preflight_report.get("items", [])
    }
    missing_file = preflight_report.get("status") == "missing"
    backend_target = _target(
        target_id="backend_env",
        label="Backend env",
        destination=BACKEND_ENV_DESTINATION,
        writer=BACKEND_WRITER,
        command="make final-apply-resources",
        slot_writes=BACKEND_SLOTS,
        preflight_items=preflight_items,
        missing_file=missing_file,
        notes=[
            "Would configure Meshy, OpenAI NPC Agent, print provider, and storage env slots.",
            "Preview does not write services/backend/.env.",
        ],
    )
    ios_target = _target(
        target_id="ios_deploy_config",
        label="iOS deploy config",
        destination=IOS_DEPLOY_DESTINATION,
        writer=IOS_WRITER,
        command="make final-apply-resources",
        slot_writes=IOS_SLOTS,
        preflight_items=preflight_items,
        missing_file=missing_file,
        notes=[
            "Would configure Apple team, bundle id, iPhone backend URL, and launch mode.",
            "Preview does not write Deployment.local.xcconfig.",
        ],
    )
    targets = [backend_target, ios_target]
    all_slots = [slot for target in targets for slot in target["slots"]]
    status = _status(preflight_status=str(preflight_report.get("status")), targets=targets)
    first_blocker = _first_blocker(targets)
    report = {
        "kind": "final_resource_apply_preview_report",
        "status": status,
        "summary": _summary(all_slots=all_slots, targets=targets),
        "resources_file": preflight_report.get(
            "resources_file",
            {
                "path": DEFAULT_RESOURCES_PATH.as_posix(),
                "exists": False,
            },
        ),
        "write_targets": targets,
        "write_targets_by_id": {target["id"]: target for target in targets},
        "first_blocker": first_blocker,
        "operator_actions": _operator_actions(
            status=status,
            preflight_report=preflight_report,
            repair_report=repair_report,
            targets=targets,
        ),
        "commands": _commands(repair_report),
        "source_reports": {
            "final_resources_preflight": _source_summary(preflight_report),
            "final_resource_requirements": _source_summary(requirements_result.report),
            "final_resource_repair": _source_summary(repair_report),
        },
        "safety": _safety(),
    }
    return FinalResourceApplyPreviewResult(
        exit_code=0 if status == "ready" else 2,
        report=report,
    )


def _target(
    *,
    target_id: str,
    label: str,
    destination: str,
    writer: str,
    command: str,
    slot_writes: dict[str, tuple[str, ...]],
    preflight_items: dict[str, dict[str, Any]],
    missing_file: bool,
    notes: list[str],
) -> dict[str, Any]:
    slots = [
        _slot(
            slot_id=slot_id,
            writes=list(writes),
            preflight_item=preflight_items.get(slot_id),
            missing_file=missing_file,
        )
        for slot_id, writes in slot_writes.items()
    ]
    blocked_by = [
        slot["id"]
        for slot in slots
        if slot["status"] == "blocked"
        or (slot["required"] and slot["status"] == "missing")
    ]
    status = "ready"
    if missing_file:
        status = "missing"
    elif blocked_by:
        status = "blocked"
    return {
        "id": target_id,
        "label": label,
        "destination": destination,
        "writer": writer,
        "status": status,
        "command": command,
        "slots": slots,
        "blocked_by": blocked_by,
        "notes": notes,
    }


def _slot(
    *,
    slot_id: str,
    writes: list[str],
    preflight_item: dict[str, Any] | None,
    missing_file: bool,
) -> dict[str, Any]:
    if preflight_item is None:
        required = slot_id in REQUIRED_IF_MISSING_FILE
        status = "missing" if required else "optional"
        configured = False
        classification = "missing_required_value" if required else "optional_value_not_required"
    else:
        required = bool(preflight_item.get("required"))
        status = str(preflight_item.get("status"))
        configured = bool(preflight_item.get("configured"))
        classification = str(
            preflight_item.get("classification")
            or ("configured" if status == "ready" else status)
        )
    if missing_file and slot_id not in REQUIRED_IF_MISSING_FILE:
        status = "optional"
        classification = "optional_value_not_required"
    secret = slot_id in SECRET_KEYS
    slot = {
        "id": slot_id,
        "status": status,
        "required": required,
        "secret": secret,
        "configured": configured,
        "classification": classification,
        "redacted": secret,
        "writes": writes,
    }
    for metadata_key in ("resolution_mode", "apply_note"):
        metadata_value = (
            preflight_item.get(metadata_key) if preflight_item is not None else None
        )
        if metadata_value is not None:
            slot[metadata_key] = metadata_value
    return slot


def _status(*, preflight_status: str, targets: list[dict[str, Any]]) -> str:
    if preflight_status == "missing":
        return "missing"
    if any(target["status"] == "blocked" for target in targets):
        return "blocked"
    if any(target["status"] == "missing" for target in targets):
        return "missing"
    return "ready"


def _first_blocker(targets: list[dict[str, Any]]) -> dict[str, Any] | None:
    for target in targets:
        if target["status"] == "ready":
            continue
        blocked_by = list(target["blocked_by"])
        detail = (
            f"blocked by {', '.join(blocked_by)}"
            if blocked_by
            else "target is not ready"
        )
        return {
            "id": target["id"],
            "label": target["label"],
            "status": target["status"],
            "classification": _target_classification(target, blocked_by),
            "command": target["command"],
            "detail": detail,
            "destination": target["destination"],
            "writer": target["writer"],
            "blocked_by": blocked_by,
            "validation_command": "make final-resources-preflight",
        }
    return None


def _target_classification(target: dict[str, Any], blocked_by: list[str]) -> str:
    first_blocked_id = blocked_by[0] if blocked_by else ""
    for slot in target["slots"]:
        if slot["id"] == first_blocked_id:
            return str(slot["classification"])
    return str(target["status"])


def _summary(
    *,
    all_slots: list[dict[str, Any]],
    targets: list[dict[str, Any]],
) -> dict[str, int]:
    statuses = [slot["status"] for slot in all_slots]
    return {
        "ready": statuses.count("ready"),
        "missing": statuses.count("missing"),
        "blocked": statuses.count("blocked"),
        "optional": statuses.count("optional"),
        "secret": sum(1 for slot in all_slots if slot["secret"]),
        "backend": len(BACKEND_SLOTS),
        "ios": len(IOS_SLOTS),
        "print": sum(1 for slot in all_slots if slot["id"] in {"PRINT_PROVIDER", "TREATSTOCK_API_KEY", "TREATSTOCK_API_BASE_URL", "SCULPTEO_API_KEY"}),
        "write_targets": len(targets),
    }


def _operator_actions(
    *,
    status: str,
    preflight_report: dict[str, Any],
    repair_report: dict[str, Any],
    targets: list[dict[str, Any]],
) -> list[str]:
    actions: list[str] = []
    if repair_report.get("status") == "repairable":
        actions.append("run make final-resource-repair")
    if status == "ready":
        actions.append("review preview, then run make final-apply-resources")
    elif preflight_report.get("status") == "missing":
        actions.append("run make final-resource-init")
    for target in targets:
        for slot_id in target["blocked_by"]:
            if slot_id == "PMF_BACKEND_BASE_URL":
                actions.append("set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL")
            else:
                actions.append(f"provide {slot_id} in final-resources.env")
    actions.extend(str(action) for action in preflight_report.get("operator_actions", []))
    actions.append("rerun make final-resource-apply-preview before applying resources")
    return _dedupe(actions)


def _commands(repair_report: dict[str, Any]) -> list[str]:
    if repair_report.get("status") == "repairable":
        return [*REPAIR_COMMANDS, *BASE_COMMANDS]
    return BASE_COMMANDS


def _source_summary(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": report.get("kind", "unknown"),
        "status": report.get("status", "unknown"),
        "summary": report.get("summary", {}),
    }


def _safety() -> dict[str, bool]:
    return {
        "provider_secrets_in_report": False,
        "local_paths_in_report": False,
        "writes_backend_env": False,
        "writes_ios_deploy_config": False,
        "runs_shell_writers": False,
        "live_provider_calls": False,
        "global_mutation": False,
        "xcode_or_signing": False,
    }


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
