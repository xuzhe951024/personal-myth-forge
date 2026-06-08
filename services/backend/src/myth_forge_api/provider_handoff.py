from __future__ import annotations

from typing import Any

from myth_forge_api.config import Settings
from myth_forge_api.providers.readiness import build_provider_readiness

CORE_PROVIDER_KINDS = ["three_d", "npc", "capture_storage"]
BACKEND_ONLY_ENV = [
    "MESHY_API_KEY",
    "OPENAI_API_KEY",
    "TREATSTOCK_API_KEY",
    "SCULPTEO_API_KEY",
]
NEXT_HANDOFF_COMMANDS = [
    "make final-apply-resources",
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
    }
