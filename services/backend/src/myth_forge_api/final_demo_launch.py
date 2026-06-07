from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from myth_forge_api.config import Settings, load_settings
from myth_forge_api.final_acceptance_readiness import (
    LOCAL_FINAL_ACCEPTANCE_COMMAND,
    build_final_acceptance_readiness_report,
)
from myth_forge_api.final_external_action_ledger import (
    build_final_external_action_ledger_report,
)
from myth_forge_api.final_resource_apply_preview import (
    build_final_resource_apply_preview_report,
)
from myth_forge_api.final_resources_preflight import (
    build_final_resources_preflight_report,
)
from myth_forge_api.final_resource_requirements import (
    build_final_resource_requirements_report,
)
from myth_forge_api.final_showcase_readiness import (
    build_final_showcase_readiness_report,
)
from myth_forge_api.final_operator_handoff import build_final_operator_handoff_report
from myth_forge_api.ios_deploy_runbook import build_ios_deploy_runbook_report
from myth_forge_api.ios_device_launch_rehearsal_readiness import (
    build_ios_device_launch_rehearsal_readiness_report,
)
from myth_forge_api.live_provider_evidence import build_live_provider_evidence_report
from myth_forge_api.npc_agent_evaluation_readiness import (
    build_npc_agent_evaluation_readiness_report,
)
from myth_forge_api.print_fulfillment_readiness import (
    build_print_fulfillment_readiness_report,
)
from myth_forge_api.resource_handoff import build_resource_handoff_report
from myth_forge_api.three_d_evaluation_readiness import (
    build_three_d_evaluation_readiness_report,
)
from myth_forge_api.visual_regression_readiness import (
    build_visual_regression_readiness_report,
)

LaunchMode = Literal["local", "configured"]


@dataclass(frozen=True)
class FinalDemoLaunchResult:
    exit_code: int
    report: dict[str, Any]


def build_final_demo_launch_report(
    *,
    mode: LaunchMode,
    settings: Settings | None = None,
    repo_root: Path | str | None = None,
    include_configured_evidence_plan: bool = True,
) -> FinalDemoLaunchResult:
    if mode not in ("local", "configured"):
        raise ValueError(f"Unsupported final demo launch mode: {mode}")
    selected_settings = settings or load_settings()
    selected_repo_root = Path(repo_root) if repo_root is not None else _default_repo_root()
    resource_report = build_resource_handoff_report(
        settings=selected_settings,
        repo_root=selected_repo_root,
    )
    final_resources_preflight = build_final_resources_preflight_report(
        repo_root=selected_repo_root,
    ).report
    final_resource_requirements = build_final_resource_requirements_report(
        repo_root=selected_repo_root,
    ).report
    final_resource_apply_preview = build_final_resource_apply_preview_report(
        repo_root=selected_repo_root,
    ).report
    final_external_action_ledger = build_final_external_action_ledger_report(
        settings=selected_settings,
        repo_root=selected_repo_root,
    ).report
    final_acceptance_readiness = build_final_acceptance_readiness_report(
        repo_root=selected_repo_root,
    ).report
    three_d_evaluation_readiness = build_three_d_evaluation_readiness_report(
        repo_root=selected_repo_root,
    ).report
    npc_agent_evaluation_readiness = build_npc_agent_evaluation_readiness_report(
        repo_root=selected_repo_root,
    ).report
    visual_regression_readiness = build_visual_regression_readiness_report(
        repo_root=selected_repo_root,
    ).report
    live_provider_evidence = build_live_provider_evidence_report(
        repo_root=selected_repo_root,
    ).report
    final_configured_evidence_plan: dict[str, Any] | None = None
    if include_configured_evidence_plan:
        from myth_forge_api.final_configured_evidence_plan import (
            build_final_configured_evidence_plan_report,
        )

        final_configured_evidence_plan = build_final_configured_evidence_plan_report(
            settings=selected_settings,
            repo_root=selected_repo_root,
        ).report
    print_fulfillment_readiness = build_print_fulfillment_readiness_report(
        settings=selected_settings,
        repo_root=selected_repo_root,
    ).report
    final_showcase_readiness = build_final_showcase_readiness_report(
        settings=selected_settings,
        repo_root=selected_repo_root,
    ).report
    ios_device_launch_rehearsal_readiness = (
        build_ios_device_launch_rehearsal_readiness_report(
            repo_root=selected_repo_root,
        ).report
    )
    ios_deploy_runbook = build_ios_deploy_runbook_report(
        mode=mode,
        repo_root=selected_repo_root,
    )
    phases = _launch_phases(
        mode=mode,
        resource_report=resource_report,
        final_resources_preflight=final_resources_preflight,
    )
    final_operator_handoff = build_final_operator_handoff_report(
        mode=mode,
        final_resources_preflight=final_resources_preflight,
        final_acceptance_readiness=final_acceptance_readiness,
        three_d_evaluation_readiness=three_d_evaluation_readiness,
        npc_agent_evaluation_readiness=npc_agent_evaluation_readiness,
        ios_deploy_runbook=ios_deploy_runbook,
        launch_phases=phases,
        repo_root=selected_repo_root,
    )
    resource_summary = dict(resource_report["summary"])
    phase_summary = _summary(phases)
    overall_status = _overall_status(mode=mode, summary=phase_summary)
    report = {
        "kind": "final_demo_launch_report",
        "mode": mode,
        "overall_status": overall_status,
        "summary": resource_summary,
        "phase_summary": phase_summary,
        "final_resources_preflight": final_resources_preflight,
        "final_resource_requirements": final_resource_requirements,
        "final_resource_apply_preview": final_resource_apply_preview,
        "final_external_action_ledger": final_external_action_ledger,
        "final_acceptance_readiness": final_acceptance_readiness,
        "three_d_evaluation_readiness": three_d_evaluation_readiness,
        "npc_agent_evaluation_readiness": npc_agent_evaluation_readiness,
        "visual_regression_readiness": visual_regression_readiness,
        "live_provider_evidence": live_provider_evidence,
        "print_fulfillment_readiness": print_fulfillment_readiness,
        "final_showcase_readiness": final_showcase_readiness,
        "ios_device_launch_rehearsal_readiness": (
            ios_device_launch_rehearsal_readiness
        ),
        "ios_deploy_runbook": ios_deploy_runbook,
        "final_operator_handoff": final_operator_handoff,
        "resource_report": resource_report,
        "launch_phases": phases,
        "operator_checklist": _operator_checklist(
            mode=mode,
            resource_report=resource_report,
            final_resources_preflight=final_resources_preflight,
            live_provider_evidence=live_provider_evidence,
            phases=phases,
        ),
        "commands": _commands(mode),
        "live_call_policy": {
            "live_calls_by_default": False,
            "configured_acceptance_requires_consent": True,
            "consent_flag": "--allow-live-provider-calls",
        },
        "safety": {
            "provider_secrets_in_report": False,
            "local_paths_in_report": False,
            "payment_links_in_report": False,
            "global_mutation": False,
            "live_provider_calls_by_default": False,
        },
    }
    if final_configured_evidence_plan is not None:
        report["final_configured_evidence_plan"] = final_configured_evidence_plan
    sanitized = _sanitize_report(report, selected_repo_root)
    return FinalDemoLaunchResult(
        exit_code=_exit_code(mode=mode, summary=phase_summary),
        report=sanitized,
    )


def _launch_phases(
    *,
    mode: LaunchMode,
    resource_report: dict[str, Any],
    final_resources_preflight: dict[str, Any],
) -> list[dict[str, Any]]:
    backend = _items_by_id(resource_report["backend"]["items"])
    ios = _items_by_id(resource_report["ios"]["items"])
    core_backend_status = _combined_status(
        [
            backend["THREE_D_PROVIDER"]["status"],
            backend["MESHY_API_KEY"]["status"],
            backend["NPC_PROVIDER"]["status"],
            backend["OPENAI_API_KEY"]["status"],
        ]
    )
    ios_status = _combined_status(
        [
            ios["DEVELOPMENT_TEAM"]["status"],
            ios["PRODUCT_BUNDLE_IDENTIFIER"]["status"],
            ios["PMF_BACKEND_BASE_URL"]["status"],
        ]
    )
    local_backend_status = "ready"
    local_acceptance_status = "ready"
    final_resource_apply_status = _final_resource_apply_status(
        mode=mode,
        core_backend_status=core_backend_status,
        ios_status=ios_status,
        final_resources_preflight_status=final_resources_preflight["status"],
    )
    configured_acceptance_status = _combined_status([core_backend_status, ios_status])
    if mode == "local":
        configured_acceptance_status = "optional"
    return [
        _phase(
            "apply_final_resources",
            "Apply final resources",
            final_resource_apply_status,
            "one-file backend and iOS final demo handoff",
            "make final-apply-resources",
            [
                "Reads only ignored services/backend/.local/final-resources.env.",
                "Writes only ignored services/backend/.env and Deployment.local.xcconfig.",
                "Use a LAN backend URL for PMF_BACKEND_BASE_URL, not localhost or 127.0.0.1.",
                "Local no-key acceptance can continue when this phase is missing, blocked, or partial.",
            ],
        ),
        _phase(
            "backend_device_server",
            "Start backend on LAN",
            local_backend_status,
            "iPhone-to-Mac API calls",
            "make backend-device-demo",
            ["Starts uvicorn on 0.0.0.0:8080; does not change firewall or signing."],
        ),
        _phase(
            "provider_readiness",
            "Check provider readiness",
            core_backend_status if mode == "configured" else "ready",
            "real Meshy/OpenAI readiness",
            (
                "cd services/backend && uv run python -m myth_forge_api.cli "
                "provider-handoff --require-core-real"
            ),
            ["Configuration-only report; does not call live providers."],
        ),
        _phase(
            "local_final_acceptance",
            "Run local final acceptance",
            local_acceptance_status,
            "no-key deterministic smoke acceptance",
            LOCAL_FINAL_ACCEPTANCE_COMMAND,
            ["Expected to surface local iOS/Xcode environment blockers on this machine."],
        ),
        _phase(
            "configured_final_acceptance",
            "Run configured final acceptance",
            configured_acceptance_status,
            "real 3D and AI NPC provider acceptance",
            (
                "cd services/backend && uv run python -m myth_forge_api.cli "
                "final-acceptance --profile quick --provider-mode configured "
                "--require-real-core --allow-live-provider-calls --repo-root ../.."
            ),
            ["May call live providers and may spend provider credits."],
        ),
        _phase(
            "mobile_deploy_preflight",
            "Run iOS deploy preflight",
            ios_status,
            "physical iPhone backend health gate",
            "make mobile-deploy-preflight",
            ["Checks local config and backend /health; does not build or sign."],
        ),
        _phase(
            "xcode_build_gate",
            "Run Xcode build gate",
            "manual",
            "final local iOS build",
            "make mobile-xcode-build",
            ["Apple SDK license/signing state remains external to this repo."],
        ),
    ]


def _items_by_id(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in items}


def _combined_status(statuses: list[str]) -> str:
    if "blocked" in statuses:
        return "blocked"
    if "missing" in statuses or "manual" in statuses:
        return "blocked"
    if "optional" in statuses:
        return "partial"
    return "ready"


def _final_resource_apply_status(
    *,
    mode: LaunchMode,
    core_backend_status: str,
    ios_status: str,
    final_resources_preflight_status: str,
) -> str:
    if final_resources_preflight_status in {"missing", "blocked"}:
        return final_resources_preflight_status
    if final_resources_preflight_status == "ready":
        return "ready"
    if mode == "configured":
        return _combined_status([core_backend_status, ios_status])
    if ios_status != "ready":
        return ios_status
    if core_backend_status != "ready":
        return "partial"
    return "ready"


def _phase(
    phase_id: str,
    label: str,
    status: str,
    required_for: str,
    command: str,
    notes: list[str],
) -> dict[str, Any]:
    return {
        "id": phase_id,
        "label": label,
        "status": status,
        "required_for": required_for,
        "command": command,
        "notes": notes,
    }


def _operator_checklist(
    *,
    mode: LaunchMode,
    resource_report: dict[str, Any],
    final_resources_preflight: dict[str, Any],
    live_provider_evidence: dict[str, Any],
    phases: list[dict[str, Any]],
) -> list[str]:
    actions: list[str] = []
    actions.extend(final_resources_preflight.get("operator_actions", []))
    if mode == "configured":
        actions.extend(resource_report["operator_actions"])
    else:
        actions.extend(
            action
            for action in resource_report["operator_actions"]
            if action.startswith("provide DEVELOPMENT_TEAM")
            or action.startswith("set PMF_BACKEND_BASE_URL")
            or action.startswith("accept the Apple SDK license")
        )
    for phase in phases:
        if phase["status"] in {"blocked", "missing"}:
            actions.append(f"unblock {phase['id']}: {phase['command']}")
    if mode == "configured" and live_provider_evidence.get("status") != "ready":
        actions.append(
            "run make live-provider-evidence after configured provider evidence files are refreshed"
        )
    return _dedupe(actions)


def _commands(mode: LaunchMode) -> list[str]:
    if mode == "local":
        return [
            "make final-resource-requirements",
            "make final-resources-preflight",
            "make final-resource-apply-preview",
            "make final-apply-resources",
            "make visual-regression-local",
            "make live-provider-evidence",
            "make ios-deploy-runbook",
            "make ios-device-launch-rehearsal",
            "make backend-device-demo",
            "make mobile-deploy-preflight",
            (
                "cd services/backend && uv run python -m myth_forge_api.cli "
                "final-demo-launch --mode local --repo-root ../.. "
                "--output .local/final-demo-launch-local.json"
            ),
            LOCAL_FINAL_ACCEPTANCE_COMMAND,
        ]
    return [
        "make final-resource-requirements",
        "make final-resources-preflight",
        "make final-resource-apply-preview",
        "make final-apply-resources",
        "make visual-regression-local",
        "make live-provider-evidence",
        "make ios-deploy-runbook",
        "make ios-device-launch-rehearsal",
        "make backend-device-demo",
        (
            "cd services/backend && uv run python -m myth_forge_api.cli "
            "provider-handoff --require-core-real "
            "--output .local/provider-handoff.json"
        ),
        (
            "cd services/backend && uv run python -m myth_forge_api.cli "
            "final-demo-launch --mode configured --repo-root ../.. "
            "--output .local/final-demo-launch-configured.json"
        ),
        LOCAL_FINAL_ACCEPTANCE_COMMAND,
        (
            "cd services/backend && uv run python -m myth_forge_api.cli "
            "final-acceptance --profile quick --provider-mode configured "
            "--require-real-core --allow-live-provider-calls --repo-root ../.. "
            "--output .local/final-acceptance-configured.json"
        ),
        "make mobile-deploy-preflight",
        "make mobile-xcode-build",
    ]


def _summary(phases: list[dict[str, Any]]) -> dict[str, int]:
    statuses = ["ready", "missing", "blocked", "manual", "optional", "partial"]
    return {status: sum(1 for phase in phases if phase["status"] == status) for status in statuses}


def _overall_status(*, mode: LaunchMode, summary: dict[str, int]) -> str:
    if mode == "configured" and (summary["missing"] or summary["blocked"]):
        return "blocked"
    if summary["manual"] or summary["optional"] or summary["partial"] or summary["blocked"]:
        return "partial"
    return "ready"


def _exit_code(*, mode: LaunchMode, summary: dict[str, int]) -> int:
    if mode == "configured" and (summary["missing"] or summary["blocked"]):
        return 2
    return 0


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
        r"sk-[A-Za-z0-9_-]+",
        r"Bearer\s+[A-Za-z0-9._~+/\-=:-]+",
        r"api[_-]?key\s*[=:]\s*[^\s,;\"']+",
        r"data:[A-Za-z0-9.+-]+/[A-Za-z0-9.+-]+;base64,[A-Za-z0-9+/=_-]+",
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
