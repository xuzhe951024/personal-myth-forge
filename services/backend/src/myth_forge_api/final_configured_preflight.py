from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from myth_forge_api.configured_acceptance_command import (
    CONFIGURED_FINAL_ACCEPTANCE_COMMAND,
    CONFIGURED_FINAL_ACCEPTANCE_COST_REVIEW_ACTION,
)
from myth_forge_api.config import Settings, load_settings
from myth_forge_api.final_demo_launch import build_final_demo_launch_report
from myth_forge_api.final_resources_preflight import (
    build_final_resources_preflight_report,
)
from myth_forge_api.operator_actions import (
    FINAL_RESOURCE_APPLY_ACTION,
    add_final_resource_validation_command,
    add_mobile_deploy_validation_command,
    normalize_operator_action,
)
from myth_forge_api.ios_deploy_runbook import build_ios_deploy_runbook_report
from myth_forge_api.provider_handoff import build_provider_handoff_report
from myth_forge_api.resource_handoff import build_resource_handoff_report


@dataclass(frozen=True)
class FinalConfiguredPreflightResult:
    exit_code: int
    report: dict[str, Any]


def build_final_configured_preflight_report(
    *,
    settings: Settings | None = None,
    repo_root: Path | str | None = None,
) -> FinalConfiguredPreflightResult:
    selected_settings = settings or load_settings()
    selected_repo_root = Path(repo_root) if repo_root is not None else _default_repo_root()
    final_resources_preflight = build_final_resources_preflight_report(
        repo_root=selected_repo_root,
    ).report
    provider_handoff = build_provider_handoff_report(selected_settings)
    resource_handoff = build_resource_handoff_report(
        settings=selected_settings,
        repo_root=selected_repo_root,
    )
    configured_final_launch = build_final_demo_launch_report(
        mode="configured",
        settings=selected_settings,
        repo_root=selected_repo_root,
        include_configured_evidence_plan=False,
        include_ios_device_launch_certificate=False,
    ).report
    configured_ios_deploy_runbook = build_ios_deploy_runbook_report(
        mode="configured",
        repo_root=selected_repo_root,
    )
    components = _components(
        final_resources_preflight=final_resources_preflight,
        provider_handoff=provider_handoff,
        resource_handoff=resource_handoff,
        configured_final_launch=configured_final_launch,
        configured_ios_deploy_runbook=configured_ios_deploy_runbook,
    )
    status = _overall_status(
        final_resources_preflight=final_resources_preflight,
        provider_handoff=provider_handoff,
        resource_handoff=resource_handoff,
        configured_final_launch=configured_final_launch,
        configured_ios_deploy_runbook=configured_ios_deploy_runbook,
    )
    first_blocker = _first_blocker(components)
    report = {
        "kind": "final_configured_preflight_report",
        "status": status,
        "summary": _summary(
            final_resources_preflight=final_resources_preflight,
            provider_handoff=provider_handoff,
            resource_handoff=resource_handoff,
            configured_final_launch=configured_final_launch,
            configured_ios_deploy_runbook=configured_ios_deploy_runbook,
        ),
        "final_resources_preflight": final_resources_preflight,
        "provider_handoff": provider_handoff,
        "resource_handoff": resource_handoff,
        "configured_final_launch": configured_final_launch,
        "configured_ios_deploy_runbook": configured_ios_deploy_runbook,
        "first_blocker": first_blocker,
        "next_action": _next_action(first_blocker),
        "operator_actions": _operator_actions(
            final_resources_preflight=final_resources_preflight,
            provider_handoff=provider_handoff,
            resource_handoff=resource_handoff,
            configured_final_launch=configured_final_launch,
            configured_ios_deploy_runbook=configured_ios_deploy_runbook,
        ),
        "commands": _commands(),
        "safety": _safety(),
    }
    sanitized = _sanitize_report(report, selected_repo_root)
    return FinalConfiguredPreflightResult(
        exit_code=0 if sanitized["status"] == "ready" else 2,
        report=sanitized,
    )


def _components(
    *,
    final_resources_preflight: dict[str, Any],
    provider_handoff: dict[str, Any],
    resource_handoff: dict[str, Any],
    configured_final_launch: dict[str, Any],
    configured_ios_deploy_runbook: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        _component(
            component_id="final_resources_preflight",
            label="Final resources preflight",
            report=final_resources_preflight,
            status=str(final_resources_preflight.get("status", "blocked")),
            command="make final-resources-preflight",
        ),
        _component(
            component_id="provider_handoff",
            label="Provider handoff",
            report=provider_handoff,
            status="ready" if provider_handoff.get("core_real_ready", False) else "blocked",
            command="make provider-handoff",
        ),
        _component(
            component_id="resource_handoff",
            label="Resource handoff",
            report=resource_handoff,
            status=str(resource_handoff.get("overall_status", "blocked")),
            command="make resource-handoff",
        ),
        _component(
            component_id="configured_final_launch",
            label="Configured final launch",
            report=configured_final_launch,
            status=str(configured_final_launch.get("overall_status", "blocked")),
            command="make final-demo-launch-configured",
        ),
        _component(
            component_id="configured_ios_deploy_runbook",
            label="Configured iOS deploy runbook",
            report=configured_ios_deploy_runbook,
            status=str(configured_ios_deploy_runbook.get("status", "blocked")),
            command="make ios-deploy-runbook-configured",
        ),
    ]


def _component(
    *,
    component_id: str,
    label: str,
    report: dict[str, Any],
    status: str,
    command: str,
) -> dict[str, Any]:
    return {
        "id": component_id,
        "label": label,
        "report": report,
        "status": status,
        "command": command,
    }


def _first_blocker(components: list[dict[str, Any]]) -> dict[str, Any] | None:
    for component in components:
        status = str(component["status"])
        if status not in {"blocked", "missing"}:
            continue
        child_action = _child_action(component["report"])
        return {
            "id": component["id"],
            "label": component["label"],
            "status": status,
            "classification": _classification(component, child_action),
            "command": _command(component, child_action),
            "detail": _detail(component, child_action),
            "source_kind": str(component["report"].get("kind", "")),
            "source_id": _source_id(component, child_action),
            "validation_command": _validation_command(component, child_action),
        }
    return None


def _next_action(first_blocker: dict[str, Any] | None) -> dict[str, Any] | None:
    if first_blocker is None:
        return None
    return {**first_blocker, "source": "first_blocker"}


def _child_action(report: dict[str, Any]) -> dict[str, Any] | None:
    for key in ("next_action", "first_blocker"):
        value = report.get(key)
        if isinstance(value, dict):
            return value
    return None


def _classification(
    component: dict[str, Any],
    child_action: dict[str, Any] | None,
) -> str:
    if child_action is not None and child_action.get("classification"):
        return str(child_action["classification"])
    report = component["report"]
    if report.get("classification"):
        return str(report["classification"])
    return f"{component['id']}_{component['status']}"


def _command(
    component: dict[str, Any],
    child_action: dict[str, Any] | None,
) -> str:
    if child_action is not None and child_action.get("command"):
        return str(child_action["command"])
    actions = _string_list(component["report"].get("operator_actions"))
    if actions:
        return actions[0]
    return str(component["command"])


def _detail(
    component: dict[str, Any],
    child_action: dict[str, Any] | None,
) -> str:
    if child_action is not None and child_action.get("detail"):
        return str(child_action["detail"])
    return f"{component['label']} is {component['status']}."


def _source_id(
    component: dict[str, Any],
    child_action: dict[str, Any] | None,
) -> str:
    if child_action is not None and child_action.get("id"):
        return str(child_action["id"])
    return str(component["id"])


def _validation_command(
    component: dict[str, Any],
    child_action: dict[str, Any] | None,
) -> str:
    if child_action is not None and child_action.get("validation_command"):
        return str(child_action["validation_command"])
    return str(component["command"])


def _overall_status(
    *,
    final_resources_preflight: dict[str, Any],
    provider_handoff: dict[str, Any],
    resource_handoff: dict[str, Any],
    configured_final_launch: dict[str, Any],
    configured_ios_deploy_runbook: dict[str, Any],
) -> str:
    resource_summary = resource_handoff.get("summary", {})
    if final_resources_preflight.get("status") != "ready":
        return "blocked"
    if not provider_handoff.get("core_real_ready", False):
        return "blocked"
    if int(resource_summary.get("missing", 0)) or int(resource_summary.get("blocked", 0)):
        return "blocked"
    if configured_final_launch.get("overall_status") == "blocked":
        return "blocked"
    if configured_ios_deploy_runbook.get("status") == "blocked":
        return "blocked"
    return "ready"


def _summary(
    *,
    final_resources_preflight: dict[str, Any],
    provider_handoff: dict[str, Any],
    resource_handoff: dict[str, Any],
    configured_final_launch: dict[str, Any],
    configured_ios_deploy_runbook: dict[str, Any],
) -> dict[str, int]:
    component_statuses = [
        str(final_resources_preflight.get("status", "blocked")),
        "ready" if provider_handoff.get("core_real_ready", False) else "blocked",
        str(resource_handoff.get("overall_status", "blocked")),
        str(configured_final_launch.get("overall_status", "blocked")),
        str(configured_ios_deploy_runbook.get("status", "blocked")),
    ]
    statuses = ["ready", "missing", "blocked", "manual", "optional", "partial", "live"]
    return {
        status: sum(1 for component_status in component_statuses if component_status == status)
        for status in statuses
    }


def _operator_actions(
    *,
    final_resources_preflight: dict[str, Any],
    provider_handoff: dict[str, Any],
    resource_handoff: dict[str, Any],
    configured_final_launch: dict[str, Any],
    configured_ios_deploy_runbook: dict[str, Any],
) -> list[str]:
    actions: list[str] = []
    actions.extend(_string_list(final_resources_preflight.get("operator_actions")))
    actions.extend(_string_list(provider_handoff.get("next_commands")))
    actions.extend(_missing_provider_actions(provider_handoff))
    actions.extend(_string_list(resource_handoff.get("operator_actions")))
    actions.extend(_string_list(configured_final_launch.get("operator_checklist")))
    actions.extend(_string_list(configured_ios_deploy_runbook.get("operator_actions")))
    if (
        final_resources_preflight.get("status") == "ready"
        and not provider_handoff.get("core_real_ready", False)
    ):
        actions.append(FINAL_RESOURCE_APPLY_ACTION)
    actions.append(CONFIGURED_FINAL_ACCEPTANCE_COST_REVIEW_ACTION)
    return _dedupe(
        [
            add_final_resource_validation_command(
                add_mobile_deploy_validation_command(normalize_operator_action(action))
            )
            for action in actions
        ]
    )


def _missing_provider_actions(provider_handoff: dict[str, Any]) -> list[str]:
    return [
        f"provide {env_name}"
        for env_name in _string_list(provider_handoff.get("missing_env"))
    ]


def _commands() -> list[str]:
    return [
        "make final-resources-preflight",
        "make final-apply-resources",
        "make final-configured-preflight",
        "make backend-device-demo",
        "make mobile-deploy-preflight",
        (
            "cd services/backend && uv run python -m myth_forge_api.cli "
            "final-demo-launch --mode configured --repo-root ../.. "
            "--output .local/final-demo-launch-configured.json"
        ),
        (
            "cd services/backend && uv run python -m myth_forge_api.cli "
            "ios-deploy-runbook --mode configured --repo-root ../.. "
            "--output .local/ios-deploy-runbook-configured.json"
        ),
        CONFIGURED_FINAL_ACCEPTANCE_COMMAND,
    ]


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
        r"data:[A-Za-z0-9.+-]+/[A-Za-z0-9+/=_-]+",
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
