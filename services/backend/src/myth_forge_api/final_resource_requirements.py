from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from myth_forge_api.final_resources_preflight import (
    DEFAULT_RESOURCES_PATH,
    SECRET_KEYS,
    build_final_resources_preflight_report,
)

BACKEND_RESOURCE_DESTINATION = "services/backend/.local/final-resources.env"
IOS_DEPLOY_DESTINATION = "apps/mobile/ios/Config/Deployment.local.xcconfig"
BACKEND_TEMPLATE = "services/backend/final-resources.env.example"
IOS_TEMPLATE = "apps/mobile/ios/Config/Deployment.local.xcconfig.example"

VALIDATION_COMMANDS = [
    "make final-resource-requirements",
    "make final-resources-preflight",
    "make final-configured-preflight",
    "make final-showcase-readiness",
]


@dataclass(frozen=True)
class RequirementMetadata:
    id: str
    label: str
    domain: str
    destination: str
    source_template: str
    default_required: bool
    unblocks: tuple[str, ...]
    validation_command: str
    notes: str
    audiences: tuple[str, ...]


@dataclass(frozen=True)
class FinalResourceRequirementsResult:
    exit_code: int
    report: dict[str, Any]


REQUIREMENTS = [
    RequirementMetadata(
        id="MESHY_API_KEY",
        label="Meshy API key",
        domain="backend_provider",
        destination=BACKEND_RESOURCE_DESTINATION,
        source_template=BACKEND_TEMPLATE,
        default_required=True,
        unblocks=("game_asset_3d_generation", "provider_key_handoff"),
        validation_command="make final-resources-preflight",
        notes="Backend-only secret for live Meshy 3D generation.",
        audiences=("backend",),
    ),
    RequirementMetadata(
        id="OPENAI_API_KEY",
        label="OpenAI API key",
        domain="backend_provider",
        destination=BACKEND_RESOURCE_DESTINATION,
        source_template=BACKEND_TEMPLATE,
        default_required=True,
        unblocks=("ai_agent_npc", "provider_key_handoff"),
        validation_command="make final-resources-preflight",
        notes="Backend-only secret for live AI NPC Agent behavior.",
        audiences=("backend",),
    ),
    RequirementMetadata(
        id="OPENAI_API_BASE_URL",
        label="OpenAI base URL override",
        domain="backend_provider",
        destination=BACKEND_RESOURCE_DESTINATION,
        source_template=BACKEND_TEMPLATE,
        default_required=False,
        unblocks=("ai_agent_npc",),
        validation_command="make final-resources-preflight",
        notes="Optional OpenAI-compatible endpoint override.",
        audiences=("backend",),
    ),
    RequirementMetadata(
        id="PRINT_PROVIDER",
        label="Print provider",
        domain="print_provider",
        destination=BACKEND_RESOURCE_DESTINATION,
        source_template=BACKEND_TEMPLATE,
        default_required=False,
        unblocks=("print_fulfillment",),
        validation_command="make print-fulfillment-readiness",
        notes="Use local for demo quote stubs or treatstock for configured quote checks.",
        audiences=("backend", "print"),
    ),
    RequirementMetadata(
        id="TREATSTOCK_API_KEY",
        label="Treatstock API key",
        domain="print_provider",
        destination=BACKEND_RESOURCE_DESTINATION,
        source_template=BACKEND_TEMPLATE,
        default_required=False,
        unblocks=("print_fulfillment", "provider_key_handoff"),
        validation_command="make print-fulfillment-readiness",
        notes="Backend-only secret required when PRINT_PROVIDER=treatstock.",
        audiences=("backend", "print"),
    ),
    RequirementMetadata(
        id="TREATSTOCK_API_BASE_URL",
        label="Treatstock base URL override",
        domain="print_provider",
        destination=BACKEND_RESOURCE_DESTINATION,
        source_template=BACKEND_TEMPLATE,
        default_required=False,
        unblocks=("print_fulfillment",),
        validation_command="make print-fulfillment-readiness",
        notes="Optional Treatstock endpoint override for integration testing.",
        audiences=("backend", "print"),
    ),
    RequirementMetadata(
        id="SCULPTEO_API_KEY",
        label="Sculpteo API key",
        domain="print_provider",
        destination=BACKEND_RESOURCE_DESTINATION,
        source_template=BACKEND_TEMPLATE,
        default_required=False,
        unblocks=("print_fulfillment",),
        validation_command="make print-fulfillment-readiness",
        notes="Optional backend-only backup print provider secret.",
        audiences=("backend", "print"),
    ),
    RequirementMetadata(
        id="DEVELOPMENT_TEAM",
        label="Apple development team",
        domain="ios_deploy",
        destination=IOS_DEPLOY_DESTINATION,
        source_template=IOS_TEMPLATE,
        default_required=True,
        unblocks=("ios_deployable", "functional_regression"),
        validation_command="make ios-device-launch-rehearsal",
        notes="Apple Team ID used by Xcode signing for device install.",
        audiences=("ios",),
    ),
    RequirementMetadata(
        id="PRODUCT_BUNDLE_IDENTIFIER",
        label="iOS bundle identifier",
        domain="ios_deploy",
        destination=IOS_DEPLOY_DESTINATION,
        source_template=IOS_TEMPLATE,
        default_required=True,
        unblocks=("ios_deployable", "functional_regression"),
        validation_command="make ios-device-launch-rehearsal",
        notes="Unique bundle id used for the iPhone build.",
        audiences=("ios",),
    ),
    RequirementMetadata(
        id="PMF_BACKEND_BASE_URL",
        label="iPhone backend URL",
        domain="ios_deploy",
        destination=IOS_DEPLOY_DESTINATION,
        source_template=IOS_TEMPLATE,
        default_required=True,
        unblocks=("ios_deployable", "capture_scanning", "functional_regression"),
        validation_command="make final-resources-preflight",
        notes="Must be an iPhone-reachable LAN URL, not localhost or 127.0.0.1.",
        audiences=("backend", "ios"),
    ),
    RequirementMetadata(
        id="PMF_FINAL_LAUNCH_MODE",
        label="Final launch mode",
        domain="final_launch",
        destination=IOS_DEPLOY_DESTINATION,
        source_template=IOS_TEMPLATE,
        default_required=False,
        unblocks=("provider_key_handoff", "privacy_safety"),
        validation_command="make final-configured-preflight",
        notes="Optional local/configured switch for the iPhone launch panel.",
        audiences=("ios",),
    ),
    RequirementMetadata(
        id="CAPTURE_STORAGE_DIR",
        label="Capture storage directory",
        domain="storage",
        destination=BACKEND_RESOURCE_DESTINATION,
        source_template=BACKEND_TEMPLATE,
        default_required=False,
        unblocks=("capture_scanning",),
        validation_command="make final-resources-preflight",
        notes="Optional backend storage override for uploaded capture assets.",
        audiences=("backend",),
    ),
    RequirementMetadata(
        id="MYTH_SESSION_STORAGE_DIR",
        label="Myth session storage directory",
        domain="storage",
        destination=BACKEND_RESOURCE_DESTINATION,
        source_template=BACKEND_TEMPLATE,
        default_required=False,
        unblocks=("capture_scanning", "ai_agent_npc"),
        validation_command="make final-resources-preflight",
        notes="Optional backend storage override for persisted myth sessions.",
        audiences=("backend",),
    ),
]


def build_final_resource_requirements_report(
    *,
    repo_root: Path | str | None = None,
    resources_file: Path | str | None = None,
) -> FinalResourceRequirementsResult:
    selected_repo_root = Path(repo_root) if repo_root is not None else _default_repo_root()
    selected_resources_file = Path(resources_file) if resources_file is not None else None
    preflight = build_final_resources_preflight_report(
        repo_root=selected_repo_root,
        resources_file=selected_resources_file,
    )
    preflight_report = preflight.report
    preflight_items = {
        item["id"]: item for item in preflight_report.get("items", [])
    }
    requirements = [
        _requirement_row(metadata=metadata, preflight_item=preflight_items.get(metadata.id))
        for metadata in REQUIREMENTS
    ]
    summary = _summary(requirements)
    status = _status(requirements)
    report = {
        "kind": "final_resource_requirements_report",
        "status": status,
        "summary": summary,
        "requirements": requirements,
        "requirements_by_id": {item["id"]: item for item in requirements},
        "operator_actions": _operator_actions(
            requirements=requirements,
            preflight_report=preflight_report,
        ),
        "validation_commands": VALIDATION_COMMANDS,
        "source_reports": {
            "final_resources_preflight": _source_summary(preflight_report),
        },
        "resources_file": preflight_report.get(
            "resources_file",
            {
                "path": DEFAULT_RESOURCES_PATH.as_posix(),
                "exists": False,
            },
        ),
        "safety": _safety(),
    }
    return FinalResourceRequirementsResult(
        exit_code=0 if status == "ready" else 2,
        report=report,
    )


def _requirement_row(
    *,
    metadata: RequirementMetadata,
    preflight_item: dict[str, Any] | None,
) -> dict[str, Any]:
    required = (
        bool(preflight_item.get("required"))
        if preflight_item is not None
        else metadata.default_required
    )
    status = (
        str(preflight_item.get("status"))
        if preflight_item is not None
        else ("missing" if required else "optional")
    )
    configured = (
        bool(preflight_item.get("configured"))
        if preflight_item is not None
        else False
    )
    classification = _classification(
        status=status,
        required=required,
        preflight_item=preflight_item,
    )
    row = {
        "id": metadata.id,
        "label": metadata.label,
        "domain": metadata.domain,
        "destination": metadata.destination,
        "source_template": metadata.source_template,
        "required": required,
        "secret": metadata.id in SECRET_KEYS,
        "configured": configured,
        "status": status,
        "classification": classification,
        "unblocks": list(metadata.unblocks),
        "validation_command": metadata.validation_command,
        "notes": metadata.notes,
    }
    normalized_value = (
        preflight_item.get("normalized_value") if preflight_item is not None else None
    )
    if normalized_value is not None and metadata.id in {
        "PRINT_PROVIDER",
        "PMF_FINAL_LAUNCH_MODE",
    }:
        row["normalized_value"] = normalized_value
    return row


def _classification(
    *,
    status: str,
    required: bool,
    preflight_item: dict[str, Any] | None,
) -> str:
    if preflight_item is not None and preflight_item.get("classification"):
        return str(preflight_item["classification"])
    if status == "missing" and required:
        return "missing_required_value"
    if status == "optional":
        return "optional_value_not_required"
    if status == "ready":
        return "configured"
    return status


def _summary(requirements: list[dict[str, Any]]) -> dict[str, int]:
    statuses = [str(requirement["status"]) for requirement in requirements]
    return {
        "total": len(requirements),
        "ready": statuses.count("ready"),
        "missing": statuses.count("missing"),
        "blocked": statuses.count("blocked"),
        "optional": statuses.count("optional"),
        "required": sum(1 for requirement in requirements if requirement["required"]),
        "secret": sum(1 for requirement in requirements if requirement["secret"]),
        "backend": _audience_count("backend"),
        "ios": _audience_count("ios"),
        "print": _audience_count("print"),
        "validation_commands": len(VALIDATION_COMMANDS),
    }


def _audience_count(audience: str) -> int:
    return sum(1 for metadata in REQUIREMENTS if audience in metadata.audiences)


def _status(requirements: list[dict[str, Any]]) -> str:
    for requirement in requirements:
        if requirement["status"] == "blocked":
            return "blocked"
        if requirement["required"] and requirement["status"] == "missing":
            return "blocked"
    return "ready"


def _operator_actions(
    *,
    requirements: list[dict[str, Any]],
    preflight_report: dict[str, Any],
) -> list[str]:
    actions: list[str] = []
    if preflight_report.get("status") == "missing":
        actions.append("run make final-resource-init")
    for requirement in requirements:
        if requirement["status"] == "blocked" and requirement["id"] == "PMF_BACKEND_BASE_URL":
            actions.append("set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL")
        elif requirement["status"] == "blocked":
            actions.append(f"fix {requirement['id']} in final-resources.env")
        elif requirement["required"] and requirement["status"] == "missing":
            actions.append(f"provide {requirement['id']} in final-resources.env")
    actions.extend(str(action) for action in preflight_report.get("operator_actions", []))
    actions.append("run make final-resource-requirements after filling resources")
    return _dedupe(actions)


def _source_summary(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": report.get("kind", "final_resources_preflight_report"),
        "status": report.get("status", "unknown"),
        "summary": report.get("summary", {}),
        "resources_file": report.get("resources_file", {}),
    }


def _safety() -> dict[str, bool]:
    return {
        "provider_secrets_in_report": False,
        "local_paths_in_report": False,
        "writes_backend_env": False,
        "writes_ios_deploy_config": False,
        "live_provider_calls": False,
        "global_mutation": False,
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
