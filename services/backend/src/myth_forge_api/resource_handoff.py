from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from myth_forge_api.configured_acceptance_command import CONFIGURED_FINAL_ACCEPTANCE_COMMAND
from myth_forge_api.config import Settings, load_settings
from myth_forge_api.operator_actions import (
    add_final_resource_validation_command,
    add_mobile_deploy_validation_command,
)
from myth_forge_api.saved_mobile_xcode_evidence import (
    has_ready_mobile_xcode_build_evidence,
)

Status = str

BACKEND_ENV_DESTINATION = "services/backend/.env"
IOS_DEPLOY_DESTINATION = "apps/mobile/ios/Config/Deployment.local.xcconfig"
FINAL_RESOURCE_APPLY_PREVIEW_ACTION = "make final-resource-apply-preview"


def build_resource_handoff_report(
    *,
    settings: Settings | None = None,
    repo_root: Path | str | None = None,
) -> dict[str, Any]:
    selected_settings = settings or load_settings()
    selected_repo_root = Path(repo_root) if repo_root is not None else _default_repo_root()
    backend_items = _backend_items(selected_settings)
    ios_items = _ios_items(selected_repo_root)
    all_items = backend_items + ios_items
    summary = _summary(all_items)
    overall_status = _overall_status(summary)
    report = {
        "kind": "resource_handoff_report",
        "overall_status": overall_status,
        "status": overall_status,
        "summary": summary,
        "backend": {
            "destination": BACKEND_ENV_DESTINATION,
            "items": backend_items,
        },
        "ios": {
            "destination": IOS_DEPLOY_DESTINATION,
            "items": ios_items,
        },
        "first_blocker": _first_blocker(all_items),
        "next_action": _next_action(all_items),
        "operator_actions": _operator_actions(backend_items, ios_items),
        "commands": _commands(),
        "safety": {
            "provider_secrets_in_report": False,
            "local_paths_in_report": False,
            "payment_links_in_report": False,
        },
    }
    return _sanitize_report(report)


def _backend_items(settings: Settings) -> list[dict[str, Any]]:
    print_status = _print_provider_status(settings)
    treatstock_status = _treatstock_key_status(settings)
    return [
        _item(
            "THREE_D_PROVIDER",
            "3D provider selection",
            BACKEND_ENV_DESTINATION,
            "real 3D generation",
            "ready" if settings.three_d_provider == "meshy" else "manual",
            configured=settings.three_d_provider == "meshy",
            missing=settings.three_d_provider != "meshy",
            notes=["Set THREE_D_PROVIDER=meshy for final real-provider acceptance."],
        ),
        _item(
            "MESHY_API_KEY",
            "Meshy API key",
            BACKEND_ENV_DESTINATION,
            "real text/image/multi-image 3D generation",
            "ready" if bool(settings.meshy_api_key) else "missing",
            configured=bool(settings.meshy_api_key),
            missing=not bool(settings.meshy_api_key),
            notes=["Backend-only key; never put it in the iOS app."],
        ),
        _item(
            "NPC_PROVIDER",
            "NPC provider selection",
            BACKEND_ENV_DESTINATION,
            "AI Agent NPC traces and ticks",
            "ready" if settings.npc_provider == "openai" else "manual",
            configured=settings.npc_provider == "openai",
            missing=settings.npc_provider != "openai",
            notes=["Set NPC_PROVIDER=openai for AI-driven NPC acceptance."],
        ),
        _item(
            "OPENAI_API_KEY",
            "OpenAI API key",
            BACKEND_ENV_DESTINATION,
            "AI Agent NPC traces and ticks",
            "ready" if bool(settings.openai_api_key) else "missing",
            configured=bool(settings.openai_api_key),
            missing=not bool(settings.openai_api_key),
            notes=["Backend-only key; mobile sees only generated NPC state."],
        ),
        _item(
            "PRINT_PROVIDER",
            "Print provider selection",
            BACKEND_ENV_DESTINATION,
            "print quote review",
            print_status,
            configured=bool(settings.print_provider),
            missing=print_status == "missing",
            notes=[
                "PRINT_PROVIDER=local is deterministic for no-key demos.",
                (
                    "PRINT_PROVIDER=treatstock enables live quote handoff when "
                    "TREATSTOCK_API_KEY is configured; order placement remains manual."
                ),
            ],
        ),
        _item(
            "TREATSTOCK_API_KEY",
            "Treatstock API key slot",
            BACKEND_ENV_DESTINATION,
            "live Treatstock print quote handoff",
            treatstock_status,
            configured=bool(settings.treatstock_api_key),
            missing=treatstock_status == "missing",
            notes=[
                "Treatstock live quote handoff is implemented.",
                "Automatic order placement remains out of scope and requires user approval.",
            ],
        ),
        _item(
            "SCULPTEO_API_KEY",
            "Sculpteo API key slot",
            BACKEND_ENV_DESTINATION,
            "future live print quote/order handoff",
            "optional",
            configured=bool(settings.sculpteo_api_key),
            missing=False,
            notes=["Slot exists; current live adapter is intentionally not implemented."],
        ),
        _item(
            "CAPTURE_STORAGE_DIR",
            "Capture storage directory",
            BACKEND_ENV_DESTINATION,
            "local capture media manifests",
            "ready",
            configured=True,
            missing=False,
            notes=["Default local capture storage is acceptable for development."],
        ),
        _item(
            "MYTH_SESSION_STORAGE_DIR",
            "Myth session storage directory",
            BACKEND_ENV_DESTINATION,
            "local myth session persistence",
            "ready",
            configured=True,
            missing=False,
            notes=["Default local myth session storage is acceptable for development."],
        ),
    ]


def _print_provider_status(settings: Settings) -> str:
    if settings.print_provider == "local":
        return "ready"
    if settings.print_provider == "treatstock":
        return "ready" if settings.treatstock_api_key else "missing"
    return "optional"


def _treatstock_key_status(settings: Settings) -> str:
    if settings.print_provider == "treatstock":
        return "ready" if settings.treatstock_api_key else "missing"
    return "optional"


def _ios_items(repo_root: Path) -> list[dict[str, Any]]:
    values = _read_xcconfig_values(repo_root)
    team = values.get("DEVELOPMENT_TEAM", "")
    bundle_id = values.get("PRODUCT_BUNDLE_IDENTIFIER", "")
    backend_url = values.get("PMF_BACKEND_BASE_URL", "")
    xcode_evidence_ready = has_ready_mobile_xcode_build_evidence(repo_root)
    backend_status = "ready"
    if not backend_url:
        backend_status = "missing"
    elif _is_loopback_url(backend_url):
        backend_status = "blocked"
    return [
        _item(
            "DEVELOPMENT_TEAM",
            "Apple development team",
            IOS_DEPLOY_DESTINATION,
            "iPhone signing",
            "ready" if team and team != "YOUR_TEAM_ID" else "missing",
            configured=bool(team and team != "YOUR_TEAM_ID"),
            missing=not bool(team and team != "YOUR_TEAM_ID"),
            notes=["Copy Deployment.local.xcconfig.example and fill your Apple Team ID."],
        ),
        _item(
            "PRODUCT_BUNDLE_IDENTIFIER",
            "Bundle identifier",
            IOS_DEPLOY_DESTINATION,
            "iPhone signing",
            "ready" if bool(bundle_id) else "missing",
            configured=bool(bundle_id),
            missing=not bool(bundle_id),
            notes=["Use a bundle id available to your Apple developer account."],
        ),
        _item(
            "PMF_BACKEND_BASE_URL",
            "iPhone-reachable backend URL",
            IOS_DEPLOY_DESTINATION,
            "device-to-Mac backend calls",
            backend_status,
            configured=bool(backend_url and not _is_loopback_url(backend_url)),
            missing=not bool(backend_url),
            notes=["Use a LAN URL such as http://192.168.1.10:8080, not loopback."],
        ),
        _item(
            "APPLE_SDK_LICENSE",
            "Apple SDK license/build gate",
            "local machine",
            "make mobile-xcode-build",
            "ready" if xcode_evidence_ready else "manual",
            configured=xcode_evidence_ready,
            missing=False,
            notes=[
                "Saved mobile Xcode build evidence is ready."
                if xcode_evidence_ready
                else "Accept the Xcode/Apple SDK license outside this repo before final build."
            ],
        ),
    ]


def _read_xcconfig_values(repo_root: Path) -> dict[str, str]:
    config_dir = repo_root / "apps/mobile/ios/Config"
    values: dict[str, str] = {}
    for name in ("Deployment.xcconfig", "Deployment.local.xcconfig"):
        path = config_dir / name
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("//") or stripped.startswith("#"):
                continue
            if "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            values[key.strip()] = value.strip()
    return values


def _is_loopback_url(value: str) -> bool:
    lowered = value.lower()
    return "://127.0.0.1" in lowered or "://localhost" in lowered


def _item(
    item_id: str,
    label: str,
    destination: str,
    required_for: str,
    status: Status,
    *,
    configured: bool,
    missing: bool,
    notes: list[str],
) -> dict[str, Any]:
    return {
        "id": item_id,
        "label": label,
        "destination": destination,
        "required_for": required_for,
        "status": status,
        "configured": configured,
        "missing": missing,
        "notes": notes,
    }


def _summary(items: list[dict[str, Any]]) -> dict[str, int]:
    statuses = ["ready", "missing", "blocked", "manual", "optional"]
    return {status: sum(1 for item in items if item["status"] == status) for status in statuses}


def _overall_status(summary: dict[str, int]) -> str:
    if summary["missing"] or summary["blocked"]:
        return "blocked"
    if summary["manual"] or summary["optional"]:
        return "partial"
    return "ready"


def _first_blocker(items: list[dict[str, Any]]) -> dict[str, Any] | None:
    for item in items:
        if item["status"] not in {"missing", "blocked"}:
            continue
        return {
            "id": item["id"],
            "label": item["label"],
            "status": item["status"],
            "classification": _blocker_classification(item),
            "command": _blocker_command(item),
            "detail": _blocker_detail(item),
            "destination": item["destination"],
            "required_for": item["required_for"],
            "validation_command": _validation_command(item),
        }
    return None


def _next_action(items: list[dict[str, Any]]) -> dict[str, Any] | None:
    blocker = _first_blocker(items)
    if blocker is None:
        return None
    return {
        **blocker,
        "source": "first_blocker",
    }


def _blocker_classification(item: dict[str, Any]) -> str:
    if item["status"] == "blocked":
        return "blocked_required_value"
    return "missing_required_value"


def _blocker_command(item: dict[str, Any]) -> str:
    item_id = str(item["id"])
    if item_id == "PRINT_PROVIDER":
        return "provide TREATSTOCK_API_KEY or set PRINT_PROVIDER=local"
    if item_id == "DEVELOPMENT_TEAM":
        return "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig"
    if item_id == "PMF_BACKEND_BASE_URL":
        return "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL"
    if item["destination"] == BACKEND_ENV_DESTINATION:
        return f"provide {item_id} in final-resources.env"
    return f"provide {item_id}"


def _blocker_detail(item: dict[str, Any]) -> str:
    notes = item.get("notes", [])
    if notes:
        return str(notes[0])
    return str(item["required_for"])


def _validation_command(item: dict[str, Any]) -> str:
    if item["destination"] == IOS_DEPLOY_DESTINATION:
        return "make mobile-deploy-preflight"
    return "make final-resources-preflight"


def _operator_actions(
    backend_items: list[dict[str, Any]],
    ios_items: list[dict[str, Any]],
) -> list[str]:
    actions: list[str] = []
    backend_by_id = {item["id"]: item for item in backend_items}
    ios_by_id = {item["id"]: item for item in ios_items}
    provider_selection_missing = (
        backend_by_id["THREE_D_PROVIDER"]["status"] != "ready"
        or backend_by_id["NPC_PROVIDER"]["status"] != "ready"
    )
    if provider_selection_missing:
        actions.append(FINAL_RESOURCE_APPLY_PREVIEW_ACTION)
    if backend_by_id["MESHY_API_KEY"]["status"] != "ready":
        actions.append("provide MESHY_API_KEY in final-resources.env")
    if backend_by_id["OPENAI_API_KEY"]["status"] != "ready":
        actions.append("provide OPENAI_API_KEY in final-resources.env")
    if backend_by_id["PRINT_PROVIDER"]["status"] == "missing":
        actions.append("provide TREATSTOCK_API_KEY or set PRINT_PROVIDER=local")
    if backend_by_id["TREATSTOCK_API_KEY"]["status"] == "missing":
        actions.append("provide TREATSTOCK_API_KEY in final-resources.env")
    if ios_by_id["DEVELOPMENT_TEAM"]["status"] != "ready":
        actions.append("provide DEVELOPMENT_TEAM in Deployment.local.xcconfig")
    if ios_by_id["PMF_BACKEND_BASE_URL"]["status"] != "ready":
        actions.append("set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL")
    if ios_by_id["APPLE_SDK_LICENSE"]["status"] != "ready":
        actions.append("accept the Apple SDK license outside this repository before Xcode build")
    return [
        add_final_resource_validation_command(
            add_mobile_deploy_validation_command(action)
        )
        for action in actions
    ]


def _commands() -> list[str]:
    return [
        "make final-apply-resources",
        "make backend-write-provider-env",
        "make backend-dev",
        "make backend-device-demo",
        "curl http://127.0.0.1:8080/v1/provider-readiness",
        (
            "cd services/backend && uv run python -m myth_forge_api.cli resource-handoff "
            "--output .local/resource-handoff.json"
        ),
        (
            "cd services/backend && uv run python -m myth_forge_api.cli "
            "resource-template-acceptance "
            "--output .local/resource-template-acceptance.json"
        ),
        (
            "cd services/backend && uv run python -m myth_forge_api.cli "
            "final-demo-launch --mode local --repo-root ../.. "
            "--output .local/final-demo-launch-local.json"
        ),
        (
            "cd services/backend && uv run python -m myth_forge_api.cli "
            "final-demo-launch --mode configured --repo-root ../.. "
            "--output .local/final-demo-launch-configured.json"
        ),
        CONFIGURED_FINAL_ACCEPTANCE_COMMAND,
        "make mobile-deploy-preflight",
        "make mobile-xcode-build",
    ]


def _default_repo_root() -> Path:
    cwd = Path.cwd()
    if cwd.name == "backend" and cwd.parent.name == "services":
        return cwd.parent.parent
    return cwd


def _sanitize_report(report: dict[str, Any]) -> dict[str, Any]:
    sanitized = json.loads(json.dumps(report))
    text = json.dumps(sanitized)
    sanitized["safety"] = {
        "provider_secrets_in_report": bool(
            re.search(r"sk-[A-Za-z0-9_-]+|api[_-]?key\s*[=:]\s*[^\s,;]+|Bearer\s+", text)
        ),
        "local_paths_in_report": str(Path.home()) in text or "file://" in text,
        "payment_links_in_report": bool(re.search(r"https?://(?:pay|checkout)\.", text)),
    }
    return sanitized
