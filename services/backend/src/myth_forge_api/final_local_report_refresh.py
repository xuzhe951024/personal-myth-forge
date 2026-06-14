from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from myth_forge_api.config import Settings, load_settings
from myth_forge_api.configured_live_evidence_bundle import (
    build_configured_live_evidence_bundle_report,
)
from myth_forge_api.evaluation.npc import (
    DEFAULT_NPC_AGENT_EVALUATION_SUITE,
    run_npc_agent_evaluation,
)
from myth_forge_api.evaluation.three_d import (
    DEFAULT_THREE_D_EVALUATION_SUITE,
    run_three_d_evaluation,
)
from myth_forge_api.final_acceptance import (
    CommandExecutionResult,
    run_final_acceptance,
)
from myth_forge_api.final_configured_preflight import (
    build_final_configured_preflight_report,
)
from myth_forge_api.final_configured_evidence_plan import (
    build_final_configured_evidence_plan_report,
)
from myth_forge_api.final_demo_launch import build_final_demo_launch_report
from myth_forge_api.final_external_action_ledger import (
    build_final_external_action_ledger_report,
)
from myth_forge_api.final_handoff_index import build_final_handoff_index_report
from myth_forge_api.final_launch_closure_packet import (
    build_final_launch_closure_packet_report,
)
from myth_forge_api.final_resource_apply_preview import (
    build_final_resource_apply_preview_report,
)
from myth_forge_api.final_resource_fill_guide import (
    build_final_resource_fill_guide_report,
)
from myth_forge_api.final_resource_repair import build_final_resource_repair_report
from myth_forge_api.final_resource_requirements import (
    build_final_resource_requirements_report,
)
from myth_forge_api.final_showcase_readiness import (
    build_final_showcase_readiness_report,
)
from myth_forge_api.ios_deploy_runbook import build_ios_deploy_runbook_report
from myth_forge_api.ios_device_launch_certificate import (
    build_ios_device_launch_certificate_report,
)
from myth_forge_api.ios_device_evidence_bundle import (
    build_ios_device_evidence_bundle_report,
)
from myth_forge_api.ios_device_launch_rehearsal import (
    build_ios_device_launch_rehearsal_report,
)
from myth_forge_api.live_provider_evidence import build_live_provider_evidence_report
from myth_forge_api.mobile_deploy_preflight_evidence import (
    run_mobile_deploy_preflight_evidence,
)
from myth_forge_api.operator_actions import (
    PROVIDER_LIVE_HANDOFF_ACTION,
    normalize_operator_action,
    prefer_guarded_print_quote_handoff_actions,
    prefer_iphone_reachable_backend_url_handoff_actions,
    prefer_project_local_ios_deploy_handoff_actions,
    prefer_provider_fill_guide_handoff_actions,
)
from myth_forge_api.print_fulfillment_readiness import (
    build_print_fulfillment_readiness_report,
)
from myth_forge_api.providers.factory import (
    build_npc_director,
    build_npc_tick_runtime,
    build_three_d_provider,
)
from myth_forge_api.provider_handoff import build_provider_handoff_report
from myth_forge_api.resource_handoff import build_resource_handoff_report
from myth_forge_api.visual_regression import check_visual_artifacts

LOCAL_REPORT_DIR = Path("services/backend/.local")
FINAL_RESOURCE_APPLY_ACTION = "make final-apply-resources"
FINAL_RESOURCE_APPLY_PREVIEW_ACTION = "make final-resource-apply-preview"
FINAL_RESOURCE_APPLY_PREVIEW_BEFORE_APPLY_ACTION = (
    "rerun make final-resource-apply-preview before applying resources"
)
FINAL_LOCAL_REPORT_REHEARSAL_COMMAND = "make final-rehearsal-local"
FINAL_LOCAL_REPORT_PROVIDER_HANDOFF_ACTION_MARKERS = (
    "make provider-handoff",
    "live-provider-evidence",
    "provider-handoff",
)
FINAL_LOCAL_REPORT_PROVIDER_CHAIN_ACTION = PROVIDER_LIVE_HANDOFF_ACTION
FINAL_LOCAL_REPORT_WEAK_PROVIDER_ACTION_ROOTS = {
    (
        "make final-resource-apply-preview; rerun make provider-handoff; "
        "rerun make live-provider-evidence"
    ),
    "make final-resource-apply-preview; rerun make live-provider-evidence",
    "make provider-handoff",
    "make provider-handoff; rerun make live-provider-evidence",
}
FINAL_LOCAL_REPORT_PRINT_HANDOFF_ACTION_MARKERS = (
    "treatstock",
    "print-quote-configured",
    "print quote",
    "print-quote",
    "print_quote",
    "/v1/print-quotes",
)
FINAL_LOCAL_REPORT_LAN_BACKEND_URL_MARKER = "iphone-reachable lan url"
FINAL_LOCAL_REPORT_BACKEND_DEVICE_DEMO_MARKER = "backend-device-demo"
BACKEND_DEVICE_DEMO_BARE_ACTION = "make backend-device-demo"
BACKEND_DEVICE_DEMO_VALIDATION = "make mobile-deploy-preflight"
LOCAL_SETTINGS = Settings(
    three_d_provider="local",
    npc_provider="local",
    print_provider="local",
)
ReportStep = Callable[[Path], dict[str, Any]]


@dataclass(frozen=True)
class FinalLocalReportRefreshResult:
    exit_code: int
    report: dict[str, Any]


@dataclass(frozen=True)
class RefreshStepDefinition:
    id: str
    label: str
    output_path: Path | None
    runner: ReportStep


def run_final_local_report_refresh(
    *,
    repo_root: Path | str | None = None,
    extra_steps: dict[str, ReportStep] | None = None,
) -> FinalLocalReportRefreshResult:
    selected_repo_root = Path(repo_root) if repo_root is not None else _default_repo_root()
    steps = _merge_step_definitions(
        defaults=_default_steps(),
        extras=_extra_step_definitions(extra_steps or {}),
    )
    step_results = [_run_step(step, selected_repo_root) for step in steps]
    summary = _summary(step_results)
    status = _overall_status(summary)
    showcase_next_action = _showcase_next_action(step_results)
    first_blocker = _first_blocker(
        step_results,
        showcase_next_action=showcase_next_action,
    )
    next_action = _next_action(first_blocker)
    device_action_bundle = _device_action_bundle(step_results)
    report = {
        "kind": "final_local_report_refresh_report",
        "status": status,
        "first_blocker": first_blocker,
        "next_action": next_action,
        "showcase_next_action": showcase_next_action,
        "device_action_bundle": device_action_bundle,
        "summary": summary,
        "steps": step_results,
        "steps_by_id": {step["id"]: step for step in step_results},
        "operator_actions": _operator_actions(
            step_results,
            next_action=next_action,
            showcase_next_action=showcase_next_action,
        ),
        "safety": _safety(),
    }
    sanitized = _sanitize_report(report, selected_repo_root)
    return FinalLocalReportRefreshResult(
        exit_code=_exit_code_for_status(status),
        report=sanitized,
    )


def _default_steps() -> list[RefreshStepDefinition]:
    return [
        _step(
            "final_resource_requirements",
            "Final resource requirements",
            "final-resource-requirements.json",
            lambda repo_root: build_final_resource_requirements_report(
                repo_root=repo_root,
            ).report,
        ),
        _step(
            "final_resource_repair_preview",
            "Final resource repair preview",
            "final-resource-repair-preview.json",
            lambda repo_root: build_final_resource_repair_report(
                repo_root=repo_root,
                apply=False,
            ).report,
        ),
        _step(
            "final_resource_apply_preview",
            "Final resource apply preview",
            "final-resource-apply-preview.json",
            lambda repo_root: build_final_resource_apply_preview_report(
                repo_root=repo_root,
            ).report,
        ),
        _step(
            "final_resource_fill_guide",
            "Final resource fill guide",
            "final-resource-fill-guide.json",
            _final_resource_fill_guide_report,
        ),
        _step(
            "three_d_evaluation_local",
            "Local 3D evaluation",
            "3d-evaluation-local.json",
            _three_d_evaluation_report,
        ),
        _step(
            "npc_evaluation_local",
            "Local NPC Agent evaluation",
            "npc-evaluation-local.json",
            _npc_evaluation_report,
        ),
        _step(
            "provider_handoff",
            "Provider handoff",
            "provider-handoff.json",
            lambda repo_root: build_provider_handoff_report(load_settings()),
        ),
        _step(
            "resource_handoff",
            "Resource handoff",
            "resource-handoff.json",
            lambda repo_root: build_resource_handoff_report(
                settings=load_settings(),
                repo_root=repo_root,
            ),
        ),
        _step(
            "visual_regression_local",
            "Visual regression",
            "visual-regression-local.json",
            lambda repo_root: check_visual_artifacts(repo_root).report,
        ),
        _step(
            "ios_deploy_runbook_local",
            "iOS deploy runbook",
            "ios-deploy-runbook-local.json",
            lambda repo_root: build_ios_deploy_runbook_report(
                mode="local",
                repo_root=repo_root,
            ),
        ),
        _step(
            "mobile_deploy_preflight_evidence",
            "Mobile deploy preflight evidence",
            "mobile-deploy-preflight-evidence.json",
            _mobile_deploy_preflight_evidence_snapshot,
        ),
        _step(
            "final_acceptance_local",
            "Safe final acceptance",
            "final-acceptance-local.json",
            _safe_final_acceptance_report,
        ),
        _step(
            "mobile_xcode_build_evidence",
            "Mobile Xcode build evidence",
            "mobile-xcode-build-evidence.json",
            _mobile_xcode_build_evidence_snapshot,
        ),
        _step(
            "final_configured_preflight",
            "Final configured preflight",
            "final-configured-preflight.json",
            lambda repo_root: build_final_configured_preflight_report(
                repo_root=repo_root,
            ).report,
        ),
        _step(
            "final_configured_evidence_plan",
            "Final configured evidence plan",
            "final-configured-evidence-plan.json",
            lambda repo_root: build_final_configured_evidence_plan_report(
                repo_root=repo_root,
            ).report,
        ),
        _step(
            "final_handoff_index",
            "Final handoff index",
            "final-handoff-index.json",
            lambda repo_root: build_final_handoff_index_report(
                repo_root=repo_root,
            ).report,
        ),
        _step(
            "ios_device_launch_certificate",
            "iOS device launch certificate",
            "ios-device-launch-certificate.json",
            lambda repo_root: build_ios_device_launch_certificate_report(
                repo_root=repo_root,
            ).report,
        ),
        _step(
            "ios_device_launch_rehearsal",
            "iOS device launch rehearsal",
            "ios-device-launch-rehearsal.json",
            lambda repo_root: build_ios_device_launch_rehearsal_report(
                repo_root=repo_root,
            ).report,
        ),
        _step(
            "ios_device_evidence_bundle",
            "iOS device evidence bundle",
            "ios-device-evidence-bundle.json",
            lambda repo_root: build_ios_device_evidence_bundle_report(
                repo_root=repo_root,
            ).report,
        ),
        _step(
            "live_provider_evidence",
            "Live provider evidence readiness",
            "live-provider-evidence.json",
            lambda repo_root: build_live_provider_evidence_report(
                repo_root=repo_root,
            ).report,
        ),
        _step(
            "configured_live_evidence_bundle",
            "Configured live evidence bundle",
            "configured-live-evidence-bundle.json",
            lambda repo_root: build_configured_live_evidence_bundle_report(
                settings=LOCAL_SETTINGS,
                repo_root=repo_root,
            ).report,
        ),
        _step(
            "print_fulfillment_readiness",
            "Print fulfillment readiness",
            "print-fulfillment-readiness.json",
            lambda repo_root: build_print_fulfillment_readiness_report(
                settings=LOCAL_SETTINGS,
                repo_root=repo_root,
            ).report,
        ),
        _step(
            "final_external_action_ledger",
            "Final external action ledger",
            "final-external-action-ledger.json",
            lambda repo_root: build_final_external_action_ledger_report(
                settings=LOCAL_SETTINGS,
                repo_root=repo_root,
            ).report,
        ),
        _step(
            "final_showcase_readiness",
            "Final showcase readiness",
            "final-showcase-readiness.json",
            lambda repo_root: build_final_showcase_readiness_report(
                settings=LOCAL_SETTINGS,
                repo_root=repo_root,
            ).report,
        ),
        _step(
            "final_launch_closure_packet",
            "Final launch closure packet",
            "final-launch-closure-packet.json",
            lambda repo_root: build_final_launch_closure_packet_report(
                repo_root=repo_root,
            ).report,
        ),
        _step(
            "final_demo_launch_local",
            "Local final demo launch",
            "final-demo-launch-local.json",
            lambda repo_root: build_final_demo_launch_report(
                mode="local",
                repo_root=repo_root,
            ).report,
        ),
        _step(
            "final_demo_launch_configured",
            "Configured final demo launch",
            "final-demo-launch-configured.json",
            lambda repo_root: build_final_demo_launch_report(
                mode="configured",
                repo_root=repo_root,
            ).report,
        ),
    ]


def _step(
    step_id: str,
    label: str,
    output_name: str,
    runner: ReportStep,
) -> RefreshStepDefinition:
    return RefreshStepDefinition(
        id=step_id,
        label=label,
        output_path=LOCAL_REPORT_DIR / output_name,
        runner=runner,
    )


def _extra_step_definitions(
    extra_steps: dict[str, ReportStep],
) -> list[RefreshStepDefinition]:
    return [
        RefreshStepDefinition(
            id=step_id,
            label=step_id.replace("_", " ").title(),
            output_path=None,
            runner=runner,
        )
        for step_id, runner in extra_steps.items()
    ]


def _merge_step_definitions(
    *,
    defaults: list[RefreshStepDefinition],
    extras: list[RefreshStepDefinition],
) -> list[RefreshStepDefinition]:
    extras_by_id = {step.id: step for step in extras}
    used_extra_ids: set[str] = set()
    merged: list[RefreshStepDefinition] = []
    for step in defaults:
        replacement = extras_by_id.get(step.id)
        if replacement is None:
            merged.append(step)
            continue
        merged.append(replacement)
        used_extra_ids.add(replacement.id)
    merged.extend(step for step in extras if step.id not in used_extra_ids)
    return merged


def _run_step(step: RefreshStepDefinition, repo_root: Path) -> dict[str, Any]:
    started_at = time.perf_counter()
    try:
        report = step.runner(repo_root)
        if step.output_path is not None:
            _write_json(repo_root=repo_root, relative_path=step.output_path, report=report)
        raw_status = _raw_status(report)
        status = _normalized_status(raw_status)
        next_command = _next_command(report)
        blocker_hint = _blocker_hint(report)
        blocker_fields = _promoted_blocker_fields(blocker_hint)
        if step.id == "final_resource_apply_preview" and status == "blocked":
            blocker_fields["command"] = FINAL_RESOURCE_APPLY_PREVIEW_ACTION
            blocker_fields.pop("validation_command", None)
        if next_command and not blocker_fields["command"]:
            blocker_fields["command"] = next_command
        step_result = {
            "id": step.id,
            "label": step.label,
            "status": status,
            "raw_status": raw_status,
            "exit_code": _step_exit_code(status),
            "kind": report.get("kind", "unknown"),
            "summary": report.get("summary", {}),
            "report_operator_actions": _report_operator_actions(report),
            "next_command": next_command,
            "blocker_hint": blocker_hint,
            **blocker_fields,
            "output": step.output_path.as_posix() if step.output_path else None,
            "accepted_blocked": status == "blocked",
            "writes_repo_local_report": step.output_path is not None,
            "elapsed_seconds": round(time.perf_counter() - started_at, 4),
        }
        device_action_bundle = report.get("device_action_bundle")
        if isinstance(device_action_bundle, dict):
            step_result["device_action_bundle"] = device_action_bundle
        source_reports = report.get("source_reports")
        if isinstance(source_reports, dict):
            step_result["source_reports"] = source_reports
        return _step_with_next_action(step_result)
    except Exception as exc:
        return {
            "id": step.id,
            "label": step.label,
            "status": "failed",
            "raw_status": "failed",
            "exit_code": 1,
            "kind": "unknown",
            "summary": {},
            "blocker_hint": {},
            "classification": "step_failed",
            "command": f"fix final-local-report-refresh step {step.id}",
            "detail": str(exc),
            "output": step.output_path.as_posix() if step.output_path else None,
            "accepted_blocked": False,
            "writes_repo_local_report": False,
            "elapsed_seconds": round(time.perf_counter() - started_at, 4),
            "error": str(exc),
        }


def _promoted_blocker_fields(hint: dict[str, Any]) -> dict[str, str]:
    fields = {
        "classification": str(hint.get("classification") or ""),
        "command": str(hint.get("command") or ""),
        "detail": str(hint.get("detail") or ""),
    }
    validation_command = str(hint.get("validation_command") or "").strip()
    if validation_command:
        fields["validation_command"] = validation_command
    return fields


def _step_with_next_action(step: dict[str, Any]) -> dict[str, Any]:
    if step.get("status") == "ready":
        step.pop("next_action", None)
        return step
    command = _structured_next_action_command(step.get("command"))
    detail = str(step.get("detail") or "").strip()
    if not command and not detail:
        step.pop("next_action", None)
        return step
    action = {
        "id": str(step.get("id", "")),
        "label": str(step.get("label", "")),
        "status": str(step.get("status", "")),
        "classification": str(step.get("classification", "")),
        "command": command,
        "detail": detail,
        "source": "step",
        "output": step.get("output"),
        "step_id": str(step.get("id", "")),
    }
    validation_command = str(step.get("validation_command") or "").strip()
    if validation_command:
        action["validation_command"] = validation_command
    step["next_action"] = action
    return step


def _structured_next_action_command(value: Any) -> str:
    command, _separator, _detail = str(value or "").partition(" | ")
    return command.strip()


def _three_d_evaluation_report(repo_root: Path) -> dict[str, Any]:
    _ = repo_root
    provider = build_three_d_provider(LOCAL_SETTINGS)
    return dict(
        run_three_d_evaluation(
            provider=provider,
            selected_provider="local",
            suite_name="default-v0",
            cases=DEFAULT_THREE_D_EVALUATION_SUITE,
        )
    )


def _final_resource_fill_guide_report(repo_root: Path) -> dict[str, Any]:
    report = build_final_resource_fill_guide_report(repo_root=repo_root).report
    markdown_path = LOCAL_REPORT_DIR / "final-resource-fill-guide.md"
    _write_text(
        repo_root=repo_root,
        relative_path=markdown_path,
        payload=str(report.get("markdown", "")),
    )
    return report


def _npc_evaluation_report(repo_root: Path) -> dict[str, Any]:
    _ = repo_root
    director = build_npc_director(LOCAL_SETTINGS)
    tick_runtime = build_npc_tick_runtime(LOCAL_SETTINGS)
    return dict(
        run_npc_agent_evaluation(
            director=director,
            tick_runtime=tick_runtime,
            selected_provider="local",
            suite_name="default-v0",
            tick_steps=2,
            cases=DEFAULT_NPC_AGENT_EVALUATION_SUITE,
        )
    )


def _safe_final_acceptance_report(repo_root: Path) -> dict[str, Any]:
    report = run_final_acceptance(
        profile="quick",
        provider_mode="local",
        require_real_core=False,
        allow_live_provider_calls=False,
        npc_steps=3,
        repo_root=repo_root,
        command_runner=lambda command, cwd: _final_acceptance_refresh_command_runner(
            command,
            cwd,
            repo_root=repo_root,
        ),
    ).report
    report["refresh_safety"] = {
        "mobile_gate_commands_executed": False,
        "xcode_or_signing_executed": False,
        "live_provider_calls": False,
        "detail": (
            "final-local-report-refresh records blocked device/Xcode gates without "
            "executing those commands"
        ),
    }
    return report


def _mobile_deploy_preflight_evidence_snapshot(repo_root: Path) -> dict[str, Any]:
    existing = _load_local_report(
        repo_root,
        "mobile-deploy-preflight-evidence.json",
    )
    if isinstance(existing, dict):
        return existing
    return run_mobile_deploy_preflight_evidence(repo_root=repo_root).report


def _mobile_xcode_build_evidence_snapshot(repo_root: Path) -> dict[str, Any]:
    existing = _load_local_report(repo_root, "mobile-xcode-build-evidence.json")
    if isinstance(existing, dict):
        return _normalize_existing_mobile_xcode_build_evidence(existing)

    first_blocker = {
        "id": "xcode_build_gate",
        "label": "Xcode build gate",
        "status": "blocked",
        "classification": "xcode_build_gate_not_run_by_final_local_report_refresh",
        "command": "run make mobile-xcode-build-evidence outside final-local-report-refresh",
        "detail": (
            "Xcode build gate was not run by final-local-report-refresh "
            "to avoid global Apple SDK/signing state."
        ),
        "validation_command": "make mobile-xcode-build-evidence",
    }
    return {
        "kind": "mobile_xcode_build_evidence_report",
        "status": "blocked",
        "classification": "xcode_build_gate_not_run_by_final_local_report_refresh",
        "command": "make mobile-xcode-build",
        "script": "apps/mobile/ios/scripts/xcode_build_gate.sh",
        "exit_code": 2,
        "checks": [
            {
                "id": "xcode_build_gate",
                "label": "Xcode build gate",
                "status": "blocked",
                "detail": (
                    "Xcode build gate was not run by final-local-report-refresh "
                    "to avoid global Apple SDK/signing state."
                ),
            }
        ],
        "stdout_lines": [],
        "stderr_lines": [
            "Xcode build gate not run by final-local-report-refresh."
        ],
        "operator_actions": [
            "run make mobile-xcode-build-evidence outside final-local-report-refresh"
        ],
        "first_blocker": first_blocker,
        "next_action": {**first_blocker, "source": "first_blocker"},
        "device_action_bundle": _safe_xcode_device_action_bundle(first_blocker),
        "safety": {
            "commands_run": False,
            "provider_calls": False,
            "live_provider_calls": False,
            "writes_backend_env": False,
            "writes_ios_deploy_config": False,
            "global_mutation": False,
            "xcode_or_signing": False,
            "code_signing_allowed": False,
            "keychain_writes": False,
            "provider_secrets_in_report": False,
            "local_paths_in_report": False,
            "writes_derived_data": False,
        },
    }


def _safe_xcode_device_action_bundle(first_blocker: dict[str, Any]) -> dict[str, Any]:
    action = {
        "id": str(first_blocker["id"]),
        "label": str(first_blocker["label"]),
        "status": str(first_blocker["status"]),
        "classification": str(first_blocker["classification"]),
        "command": str(first_blocker["command"]),
        "detail": str(first_blocker["detail"]),
        "manual": True,
        "provider_calls": False,
        "global_action": False,
        "xcode_or_signing": False,
        "validation_command": "make mobile-xcode-build-evidence",
        "next_action": {**first_blocker, "source": "device_action_bundle"},
    }
    return {
        "id": "mobile_xcode_build_evidence_actions",
        "label": "Mobile Xcode Build Evidence Actions",
        "source_report": "mobile_xcode_build_evidence",
        "status": "blocked",
        "actions": [action],
        "first_action": action,
        "summary": {
            "actions": 1,
            "ready": 0,
            "missing": 0,
            "blocked": 1,
            "manual": 1,
            "provider_calls": 0,
            "global_actions": 0,
            "xcode_or_signing": 0,
        },
        "safety": {
            "commands_run": False,
            "provider_calls": False,
            "live_provider_calls": False,
            "writes_backend_env": False,
            "writes_ios_deploy_config": False,
            "global_mutation": False,
            "xcode_or_signing": False,
            "code_signing_allowed": False,
            "keychain_writes": False,
            "provider_secrets_in_report": False,
            "local_paths_in_report": False,
            "writes_derived_data": False,
        },
    }


def _normalize_existing_mobile_xcode_build_evidence(
    report: dict[str, Any],
) -> dict[str, Any]:
    normalized = dict(report)
    if normalized.get("status") == "ready":
        normalized["first_blocker"] = None
        normalized["next_action"] = None
        return normalized

    first_blocker = normalized.get("first_blocker")
    if not isinstance(first_blocker, dict):
        first_blocker = _existing_mobile_xcode_first_blocker(normalized)
        normalized["first_blocker"] = first_blocker
    if not isinstance(normalized.get("next_action"), dict):
        normalized["next_action"] = {**first_blocker, "source": "first_blocker"}
    return normalized


def _existing_mobile_xcode_first_blocker(report: dict[str, Any]) -> dict[str, Any]:
    checks = report.get("checks")
    check = checks[0] if isinstance(checks, list) and checks else {}
    if not isinstance(check, dict):
        check = {}
    operator_actions = report.get("operator_actions")
    command = (
        operator_actions[0]
        if isinstance(operator_actions, list)
        and operator_actions
        and isinstance(operator_actions[0], str)
        else "review make mobile-xcode-build output, then rerun make mobile-xcode-build-evidence"
    )
    return {
        "id": check.get("id", "xcode_build_gate"),
        "label": check.get("label", "Xcode build gate"),
        "status": check.get("status", "blocked"),
        "classification": report.get("classification", "xcode_build_gate_failed"),
        "command": command,
        "detail": check.get("detail", "Review make mobile-xcode-build output."),
        "validation_command": "make mobile-xcode-build-evidence",
    }


def _blocked_final_acceptance_command_runner(
    command: list[str],
    cwd: Path,
) -> CommandExecutionResult:
    _ = cwd
    joined = " ".join(command)
    if "mobile-deploy-preflight" in joined:
        return CommandExecutionResult(
            exit_code=2,
            stdout=(
                "backend health check skipped by final-local-report-refresh; "
                "run make mobile-deploy-preflight manually during device validation"
            ),
            stderr="",
            elapsed_seconds=0.0,
        )
    if "mobile-xcode-build" in joined:
        return CommandExecutionResult(
            exit_code=69,
            stdout="",
            stderr=(
                "Xcode build gate skipped by final-local-report-refresh to avoid "
                "global Apple SDK/signing state"
            ),
            elapsed_seconds=0.0,
        )
    return CommandExecutionResult(
        exit_code=2,
        stdout="command skipped by final-local-report-refresh",
        stderr="",
        elapsed_seconds=0.0,
    )


def _final_acceptance_refresh_command_runner(
    command: list[str],
    cwd: Path,
    *,
    repo_root: Path,
) -> CommandExecutionResult:
    joined = " ".join(command)
    if "mobile-deploy-preflight" in joined:
        evidence = _load_local_report(repo_root, "mobile-deploy-preflight-evidence.json")
        if _is_ready_mobile_deploy_preflight_evidence(evidence):
            return _ready_command_result_from_evidence(
                evidence,
                fallback_stdout="iOS deploy preflight passed.",
            )
    if "mobile-xcode-build" in joined:
        evidence = _load_local_report(repo_root, "mobile-xcode-build-evidence.json")
        if _is_ready_mobile_xcode_build_evidence(evidence):
            return _ready_command_result_from_evidence(
                evidence,
                fallback_stdout="Xcode build gate passed with code signing disabled.",
            )
    return _blocked_final_acceptance_command_runner(command, cwd)


def _is_ready_mobile_deploy_preflight_evidence(evidence: Any) -> bool:
    return (
        isinstance(evidence, dict)
        and evidence.get("kind") == "mobile_deploy_preflight_evidence_report"
        and evidence.get("status") == "ready"
        and evidence.get("exit_code") == 0
        and bool(evidence.get("safety", {}).get("commands_run"))
        and not bool(evidence.get("safety", {}).get("global_mutation"))
        and not bool(evidence.get("safety", {}).get("live_provider_calls"))
        and not bool(evidence.get("safety", {}).get("xcode_or_signing"))
    )


def _is_ready_mobile_xcode_build_evidence(evidence: Any) -> bool:
    return (
        isinstance(evidence, dict)
        and evidence.get("kind") == "mobile_xcode_build_evidence_report"
        and evidence.get("status") == "ready"
        and evidence.get("classification") == "ready"
        and evidence.get("exit_code") == 0
        and bool(evidence.get("safety", {}).get("commands_run"))
        and not bool(evidence.get("safety", {}).get("global_mutation"))
        and not bool(evidence.get("safety", {}).get("live_provider_calls"))
    )


def _ready_command_result_from_evidence(
    evidence: dict[str, Any],
    *,
    fallback_stdout: str,
) -> CommandExecutionResult:
    stdout_lines = evidence.get("stdout_lines")
    stderr_lines = evidence.get("stderr_lines")
    stdout = (
        "\n".join(str(line) for line in stdout_lines)
        if isinstance(stdout_lines, list)
        else fallback_stdout
    )
    stderr = (
        "\n".join(str(line) for line in stderr_lines)
        if isinstance(stderr_lines, list)
        else ""
    )
    return CommandExecutionResult(
        exit_code=0,
        stdout=stdout,
        stderr=stderr,
        elapsed_seconds=0.0,
    )


def _load_local_report(repo_root: Path, output_name: str) -> dict[str, Any] | None:
    existing_path = repo_root / LOCAL_REPORT_DIR / output_name
    if not existing_path.exists():
        return None
    try:
        loaded = json.loads(existing_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return loaded if isinstance(loaded, dict) else None


def _write_json(
    *,
    repo_root: Path,
    relative_path: Path,
    report: dict[str, Any],
) -> None:
    destination = repo_root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2), encoding="utf-8")


def _write_text(
    *,
    repo_root: Path,
    relative_path: Path,
    payload: str,
) -> None:
    destination = repo_root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(payload, encoding="utf-8")


def _raw_status(report: dict[str, Any]) -> str:
    return str(
        report.get("status")
        or report.get("overall_status")
        or ("failed" if int(report.get("failed", 0) or 0) else "passed")
    )


def _normalized_status(status: str) -> str:
    if status in {"passed", "ready", "repaired", "succeeded"}:
        return "ready"
    if status in {"failed", "error"}:
        return "failed"
    return "blocked"


def _step_exit_code(status: str) -> int:
    if status == "ready":
        return 0
    if status == "blocked":
        return 2
    return 1


def _summary(steps: list[dict[str, Any]]) -> dict[str, int]:
    statuses = [str(step["status"]) for step in steps]
    return {
        "steps": len(steps),
        "ready": statuses.count("ready"),
        "blocked": statuses.count("blocked"),
        "failed": statuses.count("failed"),
        "written": sum(1 for step in steps if step["writes_repo_local_report"]),
        "accepted_blocked": sum(1 for step in steps if step["accepted_blocked"]),
    }


def _overall_status(summary: dict[str, int]) -> str:
    if summary["failed"]:
        return "failed"
    if summary["blocked"]:
        return "blocked"
    return "ready"


def _exit_code_for_status(status: str) -> int:
    if status == "ready":
        return 0
    if status == "blocked":
        return 2
    return 1


def _operator_actions(
    steps: list[dict[str, Any]],
    *,
    next_action: dict[str, Any] | None = None,
    showcase_next_action: dict[str, Any] | None = None,
) -> list[str]:
    actions: list[str] = []
    for action in (next_action, showcase_next_action):
        command = _action_command(action)
        if command:
            actions.append(command)
    priority_step_actions: list[str] = []
    fallback_step_actions: list[str] = []
    for step in steps:
        step_actions = priority_step_actions if step.get("next_command") else fallback_step_actions
        step_actions.extend(_selected_step_report_actions(step))
        if step["status"] == "failed":
            step_actions.append(f"fix final-local-report-refresh step {step['id']}")
        elif step["status"] == "blocked":
            command = _action_command(step)
            if command:
                step_actions.append(command)
            else:
                step_actions.append(f"review refreshed {step['id']} report")
    actions.extend(priority_step_actions)
    actions.extend(fallback_step_actions)
    deduped_actions = _dedupe_operator_actions(actions)
    pruned_actions = _drop_bare_rehearsal_when_specific_actions_exist(
        deduped_actions
    )
    return _prioritize_final_local_report_operator_actions(pruned_actions)[:12]


def _action_command(action: dict[str, Any] | None) -> str:
    if not isinstance(action, dict):
        return ""
    command = str(action.get("command") or "").strip()
    validation_command = str(action.get("validation_command") or "").strip()
    if command and validation_command:
        if f"rerun {validation_command}" in command:
            return command
        command_root = _action_command_root(command)
        validation_root = _action_command_root(validation_command)
        if command_root == validation_root:
            return command_root
        return f"{command}; rerun {validation_command}"
    return command


def _selected_step_report_actions(step: dict[str, Any]) -> list[str]:
    if step.get("id") != "final_demo_launch_local":
        return []
    raw_actions = step.get("report_operator_actions")
    if not isinstance(raw_actions, list):
        return []
    return [
        str(action)
        for action in raw_actions
        if isinstance(action, str)
        and (
            _is_provider_handoff_action(action)
            or _is_print_handoff_action(action)
            or _is_device_handoff_action(action)
        )
    ]


def _action_command_root(value: str) -> str:
    normalized = normalize_operator_action(value)
    return normalized.split("; rerun ", 1)[0].strip()


def _next_command(report: dict[str, Any]) -> str:
    commands = report.get("next_commands")
    if not isinstance(commands, list):
        return ""
    for command in commands:
        if not isinstance(command, str):
            continue
        normalized = normalize_operator_action(command)
        if normalized:
            return normalized
    return ""


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        normalized = value.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(normalized)
    return deduped


def _dedupe_operator_actions(values: list[str]) -> list[str]:
    deduped = _dedupe(
        [
            _normalize_apply_preview_action(normalize_operator_action(value))
            for value in values
        ]
    )
    validation_by_root: dict[str, str] = {}
    for value in deduped:
        if "; rerun " not in value:
            continue
        root = value.split("; rerun ", 1)[0].strip()
        existing = validation_by_root.get(root)
        validation_by_root[root] = _preferred_validation_action(
            existing,
            value,
        )
    validation_deduped: list[str] = []
    emitted_roots: set[str] = set()
    for value in deduped:
        root = value.split("; rerun ", 1)[0].strip()
        replacement = validation_by_root.get(root, value)
        if root in emitted_roots:
            continue
        emitted_roots.add(root)
        validation_deduped.append(replacement)
    validation_deduped = _prefer_complete_provider_handoff_chain(validation_deduped)
    validation_deduped = _prefer_validated_backend_device_demo_action(
        validation_deduped
    )
    validation_deduped = prefer_guarded_print_quote_handoff_actions(validation_deduped)
    validation_deduped = prefer_provider_fill_guide_handoff_actions(validation_deduped)
    validation_deduped = prefer_project_local_ios_deploy_handoff_actions(
        validation_deduped
    )
    validation_deduped = prefer_iphone_reachable_backend_url_handoff_actions(
        validation_deduped
    )
    return _prefer_apply_preview_before_apply(
        _dedupe_operator_action_roots(validation_deduped)
    )


def _drop_bare_rehearsal_when_specific_actions_exist(actions: list[str]) -> list[str]:
    has_specific_action = any(
        _action_command_root(action) != FINAL_LOCAL_REPORT_REHEARSAL_COMMAND
        for action in actions
    )
    if not has_specific_action:
        return actions
    return [
        action
        for action in actions
        if _action_command_root(action) != FINAL_LOCAL_REPORT_REHEARSAL_COMMAND
    ]


def _normalize_apply_preview_action(action: str) -> str:
    root = _operator_action_root(action)
    if root == FINAL_RESOURCE_APPLY_PREVIEW_BEFORE_APPLY_ACTION:
        return FINAL_RESOURCE_APPLY_PREVIEW_ACTION
    return action


def _preferred_validation_action(existing: str | None, candidate: str) -> str:
    if existing is None:
        return candidate
    if (
        "make provider-handoff" in candidate
        and "make live-provider-evidence" in candidate
        and (
            "make provider-handoff" not in existing
            or "make live-provider-evidence" not in existing
        )
    ):
        return candidate
    if (
        "make live-provider-evidence" in candidate
        and "make live-provider-evidence" not in existing
    ):
        return candidate
    return existing


def _prefer_complete_provider_handoff_chain(actions: list[str]) -> list[str]:
    if FINAL_LOCAL_REPORT_PROVIDER_CHAIN_ACTION not in actions:
        return actions
    return [
        action
        for action in actions
        if action == FINAL_LOCAL_REPORT_PROVIDER_CHAIN_ACTION
        or action not in FINAL_LOCAL_REPORT_WEAK_PROVIDER_ACTION_ROOTS
    ]


def _prefer_validated_backend_device_demo_action(actions: list[str]) -> list[str]:
    has_validated_backend_demo = any(
        BACKEND_DEVICE_DEMO_BARE_ACTION in action
        and f"rerun {BACKEND_DEVICE_DEMO_VALIDATION}" in action
        for action in actions
    )
    if not has_validated_backend_demo:
        return actions
    return [action for action in actions if action != BACKEND_DEVICE_DEMO_BARE_ACTION]


def _prioritize_final_local_report_operator_actions(actions: list[str]) -> list[str]:
    if not actions:
        return []
    first_actions = actions[:2]
    rest = actions[2:]
    backend_device_actions = [
        action for action in rest if _is_backend_device_demo_action(action)
    ]
    if backend_device_actions:
        first_actions = actions[:1]
        rest = actions[1:]
        backend_device_actions = [
            action for action in rest if _is_backend_device_demo_action(action)
        ]
    backend_url_actions = [
        action
        for action in rest
        if action not in backend_device_actions and _is_lan_backend_url_action(action)
    ]
    provider_actions = [
        action for action in rest if _is_provider_handoff_action(action)
    ]
    print_actions = [action for action in rest if _is_print_handoff_action(action)]
    priority_actions = set(
        backend_device_actions + backend_url_actions + provider_actions + print_actions
    )
    remaining = [action for action in rest if action not in priority_actions]
    return (
        first_actions
        + backend_device_actions
        + backend_url_actions
        + provider_actions
        + print_actions
        + remaining
    )


def _is_provider_handoff_action(action: str) -> bool:
    lowered = action.lower()
    return any(
        marker in lowered
        for marker in FINAL_LOCAL_REPORT_PROVIDER_HANDOFF_ACTION_MARKERS
    )


def _is_print_handoff_action(action: str) -> bool:
    lowered = action.lower()
    return any(
        marker in lowered
        for marker in FINAL_LOCAL_REPORT_PRINT_HANDOFF_ACTION_MARKERS
    )


def _is_device_handoff_action(action: str) -> bool:
    return _is_lan_backend_url_action(action) or _is_backend_device_demo_action(action)


def _is_lan_backend_url_action(action: str) -> bool:
    return FINAL_LOCAL_REPORT_LAN_BACKEND_URL_MARKER in action.lower()


def _is_backend_device_demo_action(action: str) -> bool:
    return FINAL_LOCAL_REPORT_BACKEND_DEVICE_DEMO_MARKER in action.lower()


def _prefer_apply_preview_before_apply(actions: list[str]) -> list[str]:
    action_roots = {_operator_action_root(action) for action in actions}
    if FINAL_RESOURCE_APPLY_PREVIEW_ACTION not in action_roots:
        return actions
    return [
        action
        for action in actions
        if _operator_action_root(action) != FINAL_RESOURCE_APPLY_ACTION
    ]


def _dedupe_operator_action_roots(actions: list[str]) -> list[str]:
    normalized = [action.strip() for action in actions if action.strip()]
    bare_roots = {
        _operator_action_root(action)
        for action in normalized
        if _operator_action_root(action) == action
    }
    deduped: list[str] = []
    seen_exact: set[str] = set()
    for action in normalized:
        if action in seen_exact:
            continue
        root = _operator_action_root(action)
        if root in bare_roots and action != root:
            continue
        seen_exact.add(action)
        deduped.append(action)
    return deduped


def _operator_action_root(action: str) -> str:
    return action.split(" | ", 1)[0].strip()


def _report_operator_actions(report: dict[str, Any]) -> list[str]:
    actions = report.get("operator_actions")
    if not isinstance(actions, list):
        return []
    return [str(action) for action in actions if isinstance(action, str) and action]


def _next_action(first_blocker: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(first_blocker, dict):
        return None
    action = {
        "id": str(first_blocker.get("id", "")),
        "label": str(first_blocker.get("label", "")),
        "status": str(first_blocker.get("status", "")),
        "classification": str(first_blocker.get("classification", "")),
        "command": str(first_blocker.get("command", "")),
        "detail": str(first_blocker.get("detail", "")),
        "source": "first_blocker",
        "output": first_blocker.get("output"),
        "step_id": str(first_blocker.get("step_id", "")),
    }
    validation_command = str(first_blocker.get("validation_command") or "").strip()
    if validation_command:
        action["validation_command"] = validation_command
    return action


def _showcase_next_action(steps: list[dict[str, Any]]) -> dict[str, Any] | None:
    step = next(
        (
            candidate
            for candidate in steps
            if candidate.get("id") == "final_showcase_readiness"
        ),
        None,
    )
    if not isinstance(step, dict) or step.get("status") != "blocked":
        return None

    command = str(step.get("command") or "").strip()
    if not command:
        return None

    action = {
        "id": "final_showcase_readiness",
        "label": str(step.get("label", "Final showcase readiness")),
        "status": str(step.get("status", "")),
        "classification": str(step.get("classification", "")),
        "command": command,
        "detail": str(step.get("detail", "")),
        "source": "final_showcase_readiness",
        "output": step.get("output"),
        "step_id": "final_showcase_readiness",
    }
    validation_command = _showcase_validation_command(step)
    if validation_command:
        action["validation_command"] = validation_command
    return action


def _showcase_validation_command(step: dict[str, Any]) -> str:
    hint = step.get("blocker_hint")
    if isinstance(hint, dict):
        validation_command = str(hint.get("validation_command") or "").strip()
        if validation_command:
            return validation_command
    return ""


def _device_action_bundle(steps: list[dict[str, Any]]) -> dict[str, Any]:
    source_report, source_bundle = _preferred_device_action_source(steps)
    if not isinstance(source_bundle, dict):
        return _missing_device_action_bundle()

    actions = [
        _device_action(action)
        for action in source_bundle.get("actions", [])
        if isinstance(action, dict)
    ]
    return {
        "id": "final_local_report_refresh_device_actions",
        "label": "Final Local Report Refresh Device Actions",
        "source_report": source_report,
        "status": _device_action_status(str(source_bundle.get("status", "blocked"))),
        "actions": actions,
        "first_action": _device_first_action(source_bundle.get("first_action"), actions),
        "summary": _device_action_summary(actions),
        "safety": _device_action_safety(),
    }


def _preferred_device_action_source(
    steps: list[dict[str, Any]],
) -> tuple[str, dict[str, Any] | None]:
    steps_by_id = {str(step.get("id", "")): step for step in steps}
    for step_id in (
        "final_demo_launch_local",
        "final_showcase_readiness",
        "ios_device_evidence_bundle",
    ):
        step = steps_by_id.get(step_id)
        if not isinstance(step, dict):
            continue
        bundle = step.get("device_action_bundle")
        if isinstance(bundle, dict):
            return step_id, bundle
    return "missing", None


def _missing_device_action_bundle() -> dict[str, Any]:
    return {
        "id": "final_local_report_refresh_device_actions",
        "label": "Final Local Report Refresh Device Actions",
        "source_report": "missing",
        "status": "blocked",
        "actions": [],
        "first_action": None,
        "summary": {
            "actions": 0,
            "ready": 0,
            "missing": 1,
            "blocked": 0,
            "manual": 0,
            "partial": 0,
            "provider_calls": 0,
            "global_actions": 0,
            "xcode_or_signing": 0,
        },
        "safety": _device_action_safety(),
    }


def _device_action(action: dict[str, Any]) -> dict[str, Any]:
    copied = {
        "id": str(action.get("id", "device_action")),
        "label": str(action.get("label", action.get("id", "Device action"))),
        "status": _device_action_status(str(action.get("status", "blocked"))),
        "classification": str(action.get("classification", "")),
        "command": str(action.get("command", "")),
        "detail": str(action.get("detail", "")),
        "manual": bool(action.get("manual")),
        "provider_calls": bool(action.get("provider_calls")),
        "global_action": bool(action.get("global_action")),
        "xcode_or_signing": bool(action.get("xcode_or_signing")),
    }
    for optional_field in (
        "blocks",
        "evidence_status",
        "evidence_source",
        "evidence_detail",
        "validation_command",
        "operator_actions",
        "required",
        "requires_consent",
    ):
        if optional_field in action:
            copied[optional_field] = action[optional_field]
    next_action = action.get("next_action")
    if isinstance(next_action, dict):
        copied["next_action"] = _device_next_action(next_action)
    saved_next_action = action.get("saved_next_action")
    if isinstance(saved_next_action, dict):
        copied["saved_next_action"] = _device_next_action(saved_next_action)
        _promote_saved_next_action_command(copied)
    return copied


def _promote_saved_next_action_command(action: dict[str, Any]) -> None:
    saved_next_action = action.get("saved_next_action")
    if not isinstance(saved_next_action, dict):
        return
    command = str(saved_next_action.get("command", "")).strip()
    if command:
        action["command"] = command
    validation_command = str(saved_next_action.get("validation_command", "")).strip()
    if validation_command:
        action["validation_command"] = validation_command


def _device_next_action(next_action: dict[str, Any]) -> dict[str, Any]:
    copied = {
        "id": str(next_action.get("id", "")),
        "label": str(next_action.get("label", "")),
        "status": str(next_action.get("status", "")),
        "command": str(next_action.get("command", "")),
        "detail": str(next_action.get("detail", "")),
        "source": str(next_action.get("source", "")),
    }
    for optional_field in (
        "classification",
        "validation_command",
        "output",
        "step_id",
        "source_id",
    ):
        if optional_field in next_action:
            copied[optional_field] = str(next_action.get(optional_field, ""))
    return copied


def _device_first_action(
    source_first_action: Any,
    actions: list[dict[str, Any]],
) -> dict[str, Any] | None:
    if isinstance(source_first_action, dict):
        return _device_action(source_first_action)
    for action in actions:
        if action.get("status") != "ready":
            return action
    return actions[0] if actions else None


def _device_action_summary(actions: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "actions": len(actions),
        "ready": sum(1 for action in actions if action["status"] == "ready"),
        "missing": sum(1 for action in actions if action["status"] == "missing"),
        "blocked": sum(1 for action in actions if action["status"] == "blocked"),
        "manual": sum(1 for action in actions if action.get("manual") is True),
        "partial": sum(1 for action in actions if action["status"] == "partial"),
        "provider_calls": sum(
            1 for action in actions if action["provider_calls"] is True
        ),
        "global_actions": sum(1 for action in actions if action["global_action"] is True),
        "xcode_or_signing": sum(
            1 for action in actions if action["xcode_or_signing"] is True
        ),
    }


def _device_action_safety() -> dict[str, bool]:
    return {
        "commands_run": False,
        "global_mutation": False,
        "keychain_writes": False,
        "live_provider_calls": False,
        "provider_calls": False,
        "writes_backend_env": False,
        "writes_ios_deploy_config": False,
        "xcode_or_signing": False,
    }


def _device_action_status(status: str) -> str:
    if status in {"ready", "missing", "blocked", "manual", "partial", "live"}:
        return status
    if status in {"passed", "succeeded"}:
        return "ready"
    return "blocked"


def _first_blocker(
    steps: list[dict[str, Any]],
    *,
    showcase_next_action: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    failed = next((step for step in steps if step.get("status") == "failed"), None)
    if failed is not None:
        return _step_blocker(failed)
    promoted = _promoted_showcase_device_blocker(showcase_next_action)
    if promoted is not None:
        return promoted
    step = next((step for step in steps if step.get("status") == "blocked"), None)
    if step is None:
        return None
    return _step_blocker(step)


def _promoted_showcase_device_blocker(
    showcase_next_action: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if not isinstance(showcase_next_action, dict):
        return None
    if showcase_next_action.get("status") != "blocked":
        return None
    command = str(showcase_next_action.get("command") or "")
    if (
        "mobile-write-deploy-config-auto" not in command
        and "mobile-deploy-preflight" not in command
    ):
        return None
    blocker = {
        "id": str(showcase_next_action.get("id", "final_showcase_readiness")),
        "label": str(
            showcase_next_action.get("label", "Final showcase readiness")
        ),
        "status": str(showcase_next_action.get("status", "blocked")),
        "classification": str(showcase_next_action.get("classification", "")),
        "command": command,
        "detail": str(showcase_next_action.get("detail", "")),
        "output": showcase_next_action.get("output"),
        "step_id": str(
            showcase_next_action.get("step_id", "final_showcase_readiness")
        ),
    }
    validation_command = str(
        showcase_next_action.get("validation_command") or ""
    ).strip()
    if validation_command:
        blocker["validation_command"] = validation_command
    return blocker


def _step_blocker(step: dict[str, Any]) -> dict[str, Any]:
    step_id = str(step.get("id", "step"))
    status = str(step.get("status", "blocked"))
    hint = step.get("blocker_hint") if isinstance(step.get("blocker_hint"), dict) else {}
    blocker = {
        "id": step_id,
        "label": str(step.get("label", step_id.replace("_", " ").title())),
        "status": status,
        "classification": str(
            hint.get("classification")
            or ("step_failed" if status == "failed" else "step_blocked")
        ),
        "command": _blocker_command(step, hint),
        "detail": _blocker_detail(step, hint),
        "output": step.get("output"),
        "step_id": step_id,
    }
    validation_command = str(hint.get("validation_command") or "").strip()
    if validation_command:
        blocker["validation_command"] = validation_command
    return blocker


def _blocker_command(step: dict[str, Any], hint: dict[str, Any]) -> str:
    hinted = str(hint.get("command", "")).strip()
    if hinted:
        return hinted
    next_command = str(step.get("next_command") or "").strip()
    if next_command:
        return next_command
    step_id = str(step.get("id", "step"))
    if step.get("status") == "failed":
        return f"fix final-local-report-refresh step {step_id}"
    return f"review refreshed {step_id} report"


def _blocker_detail(step: dict[str, Any], hint: dict[str, Any]) -> str:
    hinted = str(hint.get("detail", "")).strip()
    if hinted:
        return hinted
    if step.get("status") == "failed" and step.get("error"):
        return str(step["error"])
    return f"Review refreshed {step.get('id', 'step')} report."


def _blocked_check_detail_summary(checks: list[Any]) -> str:
    details: list[str] = []
    seen: set[str] = set()
    for check in checks:
        if not isinstance(check, dict):
            continue
        if str(check.get("status", "")).lower() in {"passed", "ready"}:
            continue
        detail = str(check.get("detail") or check.get("classification") or "").strip()
        if not detail or detail in seen:
            continue
        seen.add(detail)
        details.append(detail)
    return "; ".join(details)


def _blocker_hint(report: dict[str, Any]) -> dict[str, str]:
    next_action = report.get("next_action")
    if isinstance(next_action, dict):
        return _hint_from_report_action(report, next_action)

    first_blocker = report.get("first_blocker")
    if isinstance(first_blocker, dict):
        return _hint_from_report_action(report, first_blocker)

    requirements = report.get("requirements")
    if isinstance(requirements, list):
        for requirement in requirements:
            if not isinstance(requirement, dict):
                continue
            if requirement.get("status") not in {"missing", "blocked"}:
                continue
            if not bool(requirement.get("required", True)):
                continue
            hint = _hint_from_mapping(requirement)
            hint["command"] = _first_operator_action(report) or str(
                requirement.get("validation_command")
                or requirement.get("apply_command")
                or requirement.get("fill_action")
                or ""
            )
            hint["detail"] = str(
                requirement.get("notes")
                or requirement.get("detail")
                or requirement.get("classification")
                or ""
            )
            return hint

    checks = report.get("checks")
    if isinstance(checks, list):
        for check in checks:
            if not isinstance(check, dict):
                continue
            if str(check.get("status", "")).lower() in {"passed", "ready"}:
                continue
            hint = _hint_from_mapping(check)
            detail = _blocked_check_detail_summary(checks)
            if detail:
                hint["detail"] = detail
            hint["command"] = _first_operator_action(report) or hint.get("command", "")
            return hint

    action = _first_operator_action(report)
    return {"command": action} if action else {}


def _hint_from_report_action(
    report: dict[str, Any],
    action: dict[str, Any],
) -> dict[str, str]:
    hint = _hint_from_mapping(action)
    if report.get("kind") == "final_acceptance_report":
        checks = report.get("checks")
        if isinstance(checks, list):
            detail = _blocked_check_detail_summary(checks)
            if detail:
                hint["detail"] = detail
    return hint


def _hint_from_mapping(source: dict[str, Any]) -> dict[str, str]:
    hint = {
        "classification": str(source.get("classification") or ""),
        "command": str(source.get("command") or ""),
        "detail": str(
            source.get("detail")
            or source.get("notes")
            or source.get("classification")
            or ""
        ),
    }
    validation_command = str(source.get("validation_command") or "").strip()
    if validation_command:
        hint["validation_command"] = validation_command
    return hint


def _first_operator_action(report: dict[str, Any]) -> str:
    actions = report.get("operator_actions")
    if isinstance(actions, list):
        for action in actions:
            action_text = str(action).strip()
            if action_text:
                return action_text
    return ""


def _safety() -> dict[str, bool]:
    return {
        "live_provider_calls": False,
        "global_mutation": False,
        "xcode_or_signing": False,
        "keychain_writes": False,
        "writes_backend_env": False,
        "writes_ios_deploy_config": False,
        "writes_repo_local_reports": True,
        "provider_secrets_in_report": False,
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
        r"meshy-secret-[A-Za-z0-9._-]+",
        r"Bearer\s+[A-Za-z0-9._~+/\-=:-]+",
        r"Authorization",
        r"api[_-]?key\s*[=:]\s*[^\s,;\"']+",
        r"file://[^\s,;\"']+",
        r"/private/[^\s,;\"']+",
        r"/tmp/[^\s,;\"']+",
        r"/Users/[^\s,;\"']+",
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
