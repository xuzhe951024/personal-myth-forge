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
from myth_forge_api.print_fulfillment_readiness import (
    build_print_fulfillment_readiness_report,
)
from myth_forge_api.providers.factory import (
    build_npc_director,
    build_npc_tick_runtime,
    build_three_d_provider,
)
from myth_forge_api.provider_handoff import build_provider_handoff_report
from myth_forge_api.visual_regression import check_visual_artifacts

LOCAL_REPORT_DIR = Path("services/backend/.local")
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
    steps = [*_default_steps(), *_extra_step_definitions(extra_steps or {})]
    step_results = [_run_step(step, selected_repo_root) for step in steps]
    summary = _summary(step_results)
    status = _overall_status(summary)
    report = {
        "kind": "final_local_report_refresh_report",
        "status": status,
        "summary": summary,
        "steps": step_results,
        "steps_by_id": {step["id"]: step for step in step_results},
        "operator_actions": _operator_actions(step_results),
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
            "visual_regression_local",
            "Visual regression",
            "visual-regression-local.json",
            lambda repo_root: check_visual_artifacts(repo_root).report,
        ),
        _step(
            "final_acceptance_local",
            "Safe final acceptance",
            "final-acceptance-local.json",
            _safe_final_acceptance_report,
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
            lambda repo_root: run_mobile_deploy_preflight_evidence(
                repo_root=repo_root,
            ).report,
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


def _run_step(step: RefreshStepDefinition, repo_root: Path) -> dict[str, Any]:
    started_at = time.perf_counter()
    try:
        report = step.runner(repo_root)
        if step.output_path is not None:
            _write_json(repo_root=repo_root, relative_path=step.output_path, report=report)
        raw_status = _raw_status(report)
        status = _normalized_status(raw_status)
        return {
            "id": step.id,
            "label": step.label,
            "status": status,
            "raw_status": raw_status,
            "exit_code": _step_exit_code(status),
            "kind": report.get("kind", "unknown"),
            "summary": report.get("summary", {}),
            "output": step.output_path.as_posix() if step.output_path else None,
            "accepted_blocked": status == "blocked",
            "writes_repo_local_report": step.output_path is not None,
            "elapsed_seconds": round(time.perf_counter() - started_at, 4),
        }
    except Exception as exc:
        return {
            "id": step.id,
            "label": step.label,
            "status": "failed",
            "raw_status": "failed",
            "exit_code": 1,
            "kind": "unknown",
            "summary": {},
            "output": step.output_path.as_posix() if step.output_path else None,
            "accepted_blocked": False,
            "writes_repo_local_report": False,
            "elapsed_seconds": round(time.perf_counter() - started_at, 4),
            "error": str(exc),
        }


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
        command_runner=_blocked_final_acceptance_command_runner,
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
    if status in {"passed", "ready", "repaired"}:
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


def _operator_actions(steps: list[dict[str, Any]]) -> list[str]:
    actions: list[str] = []
    for step in steps:
        if step["status"] == "failed":
            actions.append(f"fix final-local-report-refresh step {step['id']}")
        elif step["status"] == "blocked":
            actions.append(f"review refreshed {step['id']} report")
    return actions[:12]


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
