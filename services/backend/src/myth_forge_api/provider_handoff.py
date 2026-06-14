from __future__ import annotations

from typing import Any

from myth_forge_api.config import Settings
from myth_forge_api.operator_actions import add_final_resource_validation_command
from myth_forge_api.providers.readiness import build_provider_readiness

CORE_PROVIDER_KINDS = ["three_d", "npc", "capture_storage"]
BACKEND_ONLY_ENV = [
    "MESHY_API_KEY",
    "OPENAI_API_KEY",
    "TREATSTOCK_API_KEY",
    "SCULPTEO_API_KEY",
]
FINAL_RESOURCES_FILE = "services/backend/.local/final-resources.env"
FINAL_RESOURCE_FILL_GUIDE_COMMAND = "make final-resource-fill-guide"
FINAL_RESOURCE_FILL_GUIDE_PREVIEW_COMMAND = (
    "make final-resource-fill-guide; rerun make final-resource-apply-preview"
)
FINAL_RESOURCE_APPLY_PREVIEW_COMMAND = "make final-resource-apply-preview"
FINAL_RESOURCE_APPLY_COMMAND = "make final-apply-resources"
PROVIDER_HANDOFF_COMMAND = "make provider-handoff"
NEXT_HANDOFF_COMMANDS = [
    FINAL_RESOURCE_APPLY_PREVIEW_COMMAND,
    FINAL_RESOURCE_APPLY_COMMAND,
    "make backend-dev",
    "curl http://127.0.0.1:8080/v1/provider-readiness",
    (
        "cd services/backend && uv run python -m myth_forge_api.cli provider-handoff "
        "--require-core-real --output .local/provider-handoff.json"
    ),
]


def build_provider_handoff_report(settings: Settings) -> dict[str, Any]:
    readiness = build_provider_readiness(settings)
    provider_items = [item.model_dump(mode="json") for item in readiness.providers]
    provider_by_kind = {item["kind"]: item for item in provider_items}
    core_items = [
        provider_by_kind[kind]
        for kind in CORE_PROVIDER_KINDS
        if kind in provider_by_kind
    ]
    core_real_count = sum(
        1 for provider in core_items if provider["is_real_provider_ready"]
    )
    core_total = len(core_items)
    core_real_ready = core_real_count == core_total
    missing_env = sorted(
        {
            env_name
            for provider in provider_items
            for env_name in provider.get("missing_env", [])
        }
    )
    first_blocker = _first_blocker(
        core_items=core_items,
        missing_env=missing_env,
        core_real_ready=core_real_ready,
    )
    return {
        "kind": "provider_handoff_report",
        "mode": "configuration",
        "status": "ready" if core_real_ready else "blocked",
        "classification": (
            "core_real_providers_ready"
            if core_real_ready
            else "core_real_providers_not_ready"
        ),
        "summary": {
            "providers": len(provider_items),
            "core_total": core_total,
            "core_real_ready": core_real_count,
            "missing_env": len(missing_env),
        },
        "overall_demo_ready": readiness.overall_demo_ready,
        "overall_real_ready": readiness.overall_real_ready,
        "core_real_ready": core_real_ready,
        "core_provider_kinds": CORE_PROVIDER_KINDS,
        "missing_env": missing_env,
        "backend_only_env": BACKEND_ONLY_ENV,
        "mobile_secret_policy": (
            "Provider secrets stay on the backend; mobile clients only see readiness metadata."
        ),
        "providers": provider_items,
        "next_commands": NEXT_HANDOFF_COMMANDS,
        "first_blocker": first_blocker,
        "next_action": _next_action(first_blocker),
        "operator_actions": _operator_actions(
            core_items=core_items,
            missing_env=missing_env,
            first_blocker=first_blocker,
        ),
        "safety": _safety(),
    }


def _first_blocker(
    *,
    core_items: list[dict[str, Any]],
    missing_env: list[str],
    core_real_ready: bool,
) -> dict[str, Any] | None:
    if core_real_ready:
        return None
    if missing_env:
        env_name = missing_env[0]
        return {
            "id": env_name,
            "label": env_name,
            "status": "blocked",
            "classification": "missing_required_env",
            "command": _resource_env_command(env_name),
            "detail": (
                "Backend-only provider value is missing from ignored final resources."
            ),
            "resources_file": FINAL_RESOURCES_FILE,
            "apply_preview_command": FINAL_RESOURCE_APPLY_PREVIEW_COMMAND,
            "apply_command": FINAL_RESOURCE_APPLY_COMMAND,
            "handoff_command": PROVIDER_HANDOFF_COMMAND,
            "blocked_by": [env_name],
            "validation_command": "make final-resources-preflight",
        }
    for provider in core_items:
        if provider.get("is_real_provider_ready") is False:
            return _provider_blocker(provider)
    return None


def _provider_blocker(provider: dict[str, Any]) -> dict[str, Any]:
    kind = str(provider.get("kind", "provider"))
    status = str(provider.get("status", "blocked"))
    return {
        "id": f"{kind}_provider",
        "label": kind.replace("_", " ").title(),
        "status": "blocked",
        "classification": status,
        "command": _provider_command(kind),
        "detail": (
            "Core provider is demo-ready but not configured as a real provider. "
            "Fill ignored final resources, preview the apply step, then apply "
            "resources to write backend-only provider settings."
        ),
        "resources_file": FINAL_RESOURCES_FILE,
        "apply_preview_command": FINAL_RESOURCE_APPLY_PREVIEW_COMMAND,
        "apply_command": FINAL_RESOURCE_APPLY_COMMAND,
        "handoff_command": PROVIDER_HANDOFF_COMMAND,
        "blocked_by": _provider_required_env(kind),
        "validation_command": PROVIDER_HANDOFF_COMMAND,
    }


def _provider_command(kind: str) -> str:
    if kind in {"three_d", "npc"}:
        return FINAL_RESOURCE_APPLY_PREVIEW_COMMAND
    return PROVIDER_HANDOFF_COMMAND


def _provider_required_env(kind: str) -> list[str]:
    if kind == "three_d":
        return ["MESHY_API_KEY"]
    if kind == "npc":
        return ["OPENAI_API_KEY"]
    return []


def _next_action(first_blocker: dict[str, Any] | None) -> dict[str, Any] | None:
    if first_blocker is None:
        return None
    return {**first_blocker, "source": "first_blocker"}


def _operator_actions(
    *,
    core_items: list[dict[str, Any]],
    missing_env: list[str],
    first_blocker: dict[str, Any] | None,
) -> list[str]:
    if first_blocker is None:
        return []
    actions = [FINAL_RESOURCE_FILL_GUIDE_PREVIEW_COMMAND]
    resource_env = _resource_env_actions(
        core_items=core_items,
        missing_env=missing_env,
    )
    actions.extend(
        add_final_resource_validation_command(_resource_env_command(env_name))
        for env_name in resource_env
    )
    actions.append(PROVIDER_HANDOFF_COMMAND)
    return _dedupe(actions)


def _resource_env_actions(
    *,
    core_items: list[dict[str, Any]],
    missing_env: list[str],
) -> list[str]:
    env_names: list[str] = list(missing_env)
    for provider in core_items:
        if provider.get("is_real_provider_ready") is not False:
            continue
        for env_name in _provider_required_env(str(provider.get("kind", ""))):
            env_names.append(env_name)
    order = {name: index for index, name in enumerate(BACKEND_ONLY_ENV)}
    return sorted(set(env_names), key=lambda name: order.get(name, len(order)))


def _resource_env_command(env_name: str) -> str:
    return f"provide {env_name} in final-resources.env"


def _dedupe(actions: list[str]) -> list[str]:
    deduped: list[str] = []
    seen: set[str] = set()
    for action in actions:
        if action in seen:
            continue
        deduped.append(action)
        seen.add(action)
    return deduped


def _safety() -> dict[str, bool]:
    return {
        "commands_run": False,
        "provider_calls": False,
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
    }
