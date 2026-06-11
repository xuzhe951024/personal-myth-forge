from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from myth_forge_api.configured_acceptance_command import (
    CONFIGURED_FINAL_ACCEPTANCE_COMMAND,
)
from myth_forge_api.config import Settings, load_settings
from myth_forge_api.final_acceptance_readiness import (
    LOCAL_FINAL_ACCEPTANCE_COMMAND,
    build_final_acceptance_readiness_report,
)
from myth_forge_api.final_external_action_ledger import (
    build_final_external_action_ledger_report,
)
from myth_forge_api.final_handoff_commands import (
    FINAL_DEMO_LAUNCH_CONFIGURED_COMMAND,
    FINAL_DEMO_LAUNCH_LOCAL_COMMAND,
    PROVIDER_HANDOFF_COMMAND,
)
from myth_forge_api.final_launch_closure_packet import (
    build_final_launch_closure_packet_report,
)
from myth_forge_api.final_resource_apply_preview import (
    build_final_resource_apply_preview_report,
)
from myth_forge_api.final_resource_fill_guide import (
    build_final_resource_fill_guide_report,
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
from myth_forge_api.ios_device_evidence_bundle import (
    build_ios_device_evidence_bundle_report,
)
from myth_forge_api.ios_device_launch_rehearsal_readiness import (
    build_ios_device_launch_rehearsal_readiness_report,
)
from myth_forge_api.live_provider_evidence import build_live_provider_evidence_report
from myth_forge_api.local_showcase_smoke import build_local_showcase_smoke_report
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
    include_ios_device_launch_certificate: bool = True,
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
    final_resource_fill_guide = build_final_resource_fill_guide_report(
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
    local_showcase_smoke = build_local_showcase_smoke_report().report
    live_provider_evidence = build_live_provider_evidence_report(
        repo_root=selected_repo_root,
    ).report
    configured_live_evidence_bundle: dict[str, Any] | None = None
    if include_configured_evidence_plan:
        from myth_forge_api.configured_live_evidence_bundle import (
            build_configured_live_evidence_bundle_report,
        )

        configured_live_evidence_bundle = build_configured_live_evidence_bundle_report(
            settings=selected_settings,
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
    ios_device_evidence_bundle = build_ios_device_evidence_bundle_report(
        repo_root=selected_repo_root,
    ).report
    final_launch_closure_packet = build_final_launch_closure_packet_report(
        settings=selected_settings,
        repo_root=selected_repo_root,
    ).report
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
    first_blocker = _first_blocker(
        mode=mode,
        phases=phases,
        nested_reports=[
            ("final_resource_requirements", final_resource_requirements),
            ("final_resource_apply_preview", final_resource_apply_preview),
            ("final_resource_fill_guide", final_resource_fill_guide),
            ("final_acceptance_readiness", final_acceptance_readiness),
            ("final_showcase_readiness", final_showcase_readiness),
            ("final_launch_closure_packet", final_launch_closure_packet),
            ("live_provider_evidence", live_provider_evidence),
            ("print_fulfillment_readiness", print_fulfillment_readiness),
            ("configured_live_evidence_bundle", configured_live_evidence_bundle),
            ("final_operator_handoff", final_operator_handoff),
        ],
        final_showcase_readiness=final_showcase_readiness,
    )
    next_action = _next_action(
        first_blocker,
        final_showcase_readiness=final_showcase_readiness,
    )
    operator_checklist = _operator_checklist(
        mode=mode,
        resource_report=resource_report,
        final_resources_preflight=final_resources_preflight,
        live_provider_evidence=live_provider_evidence,
        phases=phases,
    )
    report = {
        "kind": "final_demo_launch_report",
        "mode": mode,
        "overall_status": overall_status,
        "status": overall_status,
        "first_blocker": first_blocker,
        "next_action": next_action,
        "operator_actions": _operator_actions(
            next_action=next_action,
            operator_checklist=operator_checklist,
        ),
        "summary": resource_summary,
        "phase_summary": phase_summary,
        "final_resources_preflight": final_resources_preflight,
        "final_resource_requirements": final_resource_requirements,
        "final_resource_apply_preview": final_resource_apply_preview,
        "final_resource_fill_guide": final_resource_fill_guide,
        "final_external_action_ledger": final_external_action_ledger,
        "final_launch_closure_packet": final_launch_closure_packet,
        "final_acceptance_readiness": final_acceptance_readiness,
        "three_d_evaluation_readiness": three_d_evaluation_readiness,
        "npc_agent_evaluation_readiness": npc_agent_evaluation_readiness,
        "visual_regression_readiness": visual_regression_readiness,
        "local_showcase_smoke": local_showcase_smoke,
        "live_provider_evidence": live_provider_evidence,
        "print_fulfillment_readiness": print_fulfillment_readiness,
        "final_showcase_readiness": final_showcase_readiness,
        "ios_device_launch_rehearsal_readiness": (
            ios_device_launch_rehearsal_readiness
        ),
        "ios_deploy_runbook": ios_deploy_runbook,
        "ios_device_evidence_bundle": ios_device_evidence_bundle,
        "final_operator_handoff": final_operator_handoff,
        "resource_report": resource_report,
        "launch_phases": phases,
        "operator_checklist": operator_checklist,
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
    if configured_live_evidence_bundle is not None:
        report["configured_live_evidence_bundle"] = configured_live_evidence_bundle
    if include_ios_device_launch_certificate:
        from myth_forge_api.ios_device_launch_certificate import (
            build_ios_device_launch_certificate_report,
        )

        report["ios_device_launch_certificate"] = (
            build_ios_device_launch_certificate_report(
                settings=selected_settings,
                repo_root=selected_repo_root,
                final_demo_launch_report=report,
            ).report
        )
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
            PROVIDER_HANDOFF_COMMAND,
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
            CONFIGURED_FINAL_ACCEPTANCE_COMMAND,
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


def _operator_actions(
    *,
    next_action: dict[str, Any] | None,
    operator_checklist: list[str],
) -> list[str]:
    actions: list[str] = []
    concrete = _next_action_operator_action(next_action)
    if concrete:
        actions.append(concrete)
    actions.extend(operator_checklist)
    return _dedupe(actions)[:8]


def _next_action_operator_action(next_action: dict[str, Any] | None) -> str:
    if not isinstance(next_action, dict):
        return ""
    command = str(next_action.get("command", "")).strip()
    validation_command = str(next_action.get("validation_command", "")).strip()
    if command and validation_command:
        return f"{command}; rerun {validation_command}"
    return command


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
            FINAL_DEMO_LAUNCH_LOCAL_COMMAND,
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
        PROVIDER_HANDOFF_COMMAND,
        FINAL_DEMO_LAUNCH_CONFIGURED_COMMAND,
        LOCAL_FINAL_ACCEPTANCE_COMMAND,
        CONFIGURED_FINAL_ACCEPTANCE_COMMAND,
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


def _first_blocker(
    *,
    mode: LaunchMode,
    phases: list[dict[str, Any]],
    nested_reports: list[tuple[str, dict[str, Any] | None]],
    final_showcase_readiness: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    nested_blocker = _first_nested_blocker(nested_reports)
    candidate_phases = _first_blocker_phases(mode=mode, phases=phases)
    phase_blocker = _first_phase_blocker(
        phases=candidate_phases,
        statuses={"failed", "blocked", "missing"},
    )
    if phase_blocker is not None:
        if mode == "local":
            return _local_phase_blocker_with_device_evidence(
                phase_blocker,
                final_showcase_readiness=final_showcase_readiness,
            )
        return _phase_blocker_with_nested_hint(phase_blocker, nested_blocker)
    if nested_blocker is not None:
        return nested_blocker
    return _first_phase_blocker(
        phases=candidate_phases,
        statuses={"manual", "partial"},
    )


def _first_blocker_phases(
    *,
    mode: LaunchMode,
    phases: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if mode != "local":
        return phases
    return [
        phase
        for phase in phases
        if not (
            phase.get("id") == "apply_final_resources"
            and phase.get("status") in {"missing", "blocked", "partial"}
        )
    ]


def _next_action(
    first_blocker: dict[str, Any] | None,
    *,
    final_showcase_readiness: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    if first_blocker is None:
        return None
    action = dict(first_blocker)
    _apply_concrete_mobile_preflight_next_action(
        action,
        final_showcase_readiness=final_showcase_readiness,
    )
    action["source"] = "first_blocker"
    action["source_id"] = str(action.get("source_id") or action.get("id", ""))
    return action


def _apply_concrete_mobile_preflight_next_action(
    action: dict[str, Any],
    *,
    final_showcase_readiness: dict[str, Any] | None,
) -> None:
    if action.get("id") != "mobile_deploy_preflight":
        return
    concrete_action = _final_showcase_next_action(final_showcase_readiness)
    if not concrete_action:
        return
    validation_command = str(concrete_action.get("validation_command", "")).strip()
    if not validation_command:
        return
    command = str(concrete_action.get("command", "")).strip()
    if command:
        action["command"] = command
    action["validation_command"] = validation_command


def _final_showcase_next_action(
    final_showcase_readiness: dict[str, Any] | None,
) -> dict[str, Any]:
    if not isinstance(final_showcase_readiness, dict):
        return {}
    next_action = final_showcase_readiness.get("next_action")
    return next_action if isinstance(next_action, dict) else {}


def _first_phase_blocker(
    *,
    phases: list[dict[str, Any]],
    statuses: set[str],
) -> dict[str, Any] | None:
    for phase in phases:
        if phase.get("status") in statuses:
            return _phase_blocker(phase)
    return None


def _phase_blocker(phase: dict[str, Any]) -> dict[str, Any]:
    notes = phase.get("notes", [])
    note = notes[0] if notes else ""
    detail_parts = [
        str(phase.get("required_for", "")),
        str(note),
    ]
    return {
        "id": str(phase.get("id", "unknown_phase")),
        "label": str(phase.get("label", "Unknown phase")),
        "status": str(phase.get("status", "blocked")),
        "classification": "final_demo_launch_phase",
        "command": str(phase.get("command", "")),
        "detail": " | ".join(part for part in detail_parts if part),
        "source": "final_demo_launch_phase",
        "source_id": str(phase.get("id", "unknown_phase")),
    }


def _local_phase_blocker_with_device_evidence(
    phase_blocker: dict[str, Any],
    *,
    final_showcase_readiness: dict[str, Any] | None,
) -> dict[str, Any]:
    if phase_blocker.get("id") != "mobile_deploy_preflight":
        return phase_blocker
    evidence_detail = _mobile_preflight_action_evidence_detail(
        final_showcase_readiness,
    )
    if not evidence_detail:
        return phase_blocker
    result = dict(phase_blocker)
    detail = str(result.get("detail", ""))
    result["detail"] = " | ".join(
        part for part in [detail, evidence_detail] if part
    )
    return result


def _mobile_preflight_action_evidence_detail(
    final_showcase_readiness: dict[str, Any] | None,
) -> str:
    if not isinstance(final_showcase_readiness, dict):
        return ""
    bundle = final_showcase_readiness.get("device_action_bundle")
    if not isinstance(bundle, dict):
        return ""
    actions = bundle.get("actions")
    if not isinstance(actions, list):
        return ""
    for action in actions:
        if not isinstance(action, dict):
            continue
        if action.get("id") != "run_mobile_deploy_preflight":
            continue
        return str(action.get("evidence_detail", ""))
    return ""


def _phase_blocker_with_nested_hint(
    phase_blocker: dict[str, Any],
    nested_blocker: dict[str, Any] | None,
) -> dict[str, Any]:
    if nested_blocker is None:
        return phase_blocker
    hint = _nested_blocker_hint(nested_blocker)
    if not hint:
        return phase_blocker
    result = dict(phase_blocker)
    detail = str(result.get("detail", ""))
    result["detail"] = " | ".join(part for part in [detail, hint] if part)
    return result


def _nested_blocker_hint(blocker: dict[str, Any]) -> str:
    source = str(blocker.get("source", "nested_report"))
    blocker_id = str(blocker.get("source_id", blocker.get("id", source)))
    parts = [f"Blocked by {source}:{blocker_id}"]
    command = str(blocker.get("command", ""))
    detail = str(blocker.get("detail", ""))
    if command:
        parts.append(command)
    if detail:
        parts.append(detail)
    return " | ".join(parts)


def _first_nested_blocker(
    nested_reports: list[tuple[str, dict[str, Any] | None]],
) -> dict[str, Any] | None:
    for source, report in nested_reports:
        if not isinstance(report, dict):
            continue
        blocker = _nested_report_blocker(source=source, report=report)
        if blocker is not None:
            return blocker
    return None


def _nested_report_blocker(
    *,
    source: str,
    report: dict[str, Any],
) -> dict[str, Any] | None:
    raw_blocker = report.get("first_blocker")
    if not isinstance(raw_blocker, dict):
        raw_blockers = report.get("blockers")
        if isinstance(raw_blockers, list) and raw_blockers:
            candidate = raw_blockers[0]
            raw_blocker = candidate if isinstance(candidate, dict) else None
    if not isinstance(raw_blocker, dict):
        current_blocker = report.get("current_blocker")
        raw_blocker = current_blocker if isinstance(current_blocker, dict) else None
    if isinstance(raw_blocker, dict):
        return _compact_nested_blocker(source=source, blocker=raw_blocker)
    next_actions = report.get("next_actions")
    if isinstance(next_actions, list) and next_actions:
        first_action = str(next_actions[0])
        if first_action:
            return {
                "id": source,
                "label": _source_label(source),
                "status": str(report.get("status", "blocked")),
                "classification": "operator_action",
                "command": first_action,
                "detail": first_action,
                "source": source,
                "source_id": source,
            }
    return None


def _compact_nested_blocker(*, source: str, blocker: dict[str, Any]) -> dict[str, Any]:
    blocker_id = str(blocker.get("id", source))
    result = {
        "id": blocker_id,
        "label": str(blocker.get("label", blocker_id)),
        "status": str(blocker.get("status", "blocked")),
        "command": _command_text(blocker.get("command")),
        "detail": str(blocker.get("detail", "")),
        "source": source,
        "source_id": blocker_id,
    }
    classification = blocker.get("classification")
    if classification is not None:
        result["classification"] = str(classification)
    return result


def _command_text(value: Any) -> str:
    if isinstance(value, list):
        return " ".join(str(part) for part in value)
    if value is None:
        return ""
    return str(value)


def _source_label(source: str) -> str:
    return source.replace("_", " ").capitalize()


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
