from __future__ import annotations

import json
import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Literal

from myth_forge_api.acceptance import DemoAcceptanceResult, ProviderMode, run_demo_acceptance
from myth_forge_api.arkit_scan_generation_acceptance import (
    ARKitScanGenerationAcceptanceResult,
    run_arkit_scan_generation_acceptance,
)
from myth_forge_api.capture_acceptance import (
    Capture3DAcceptanceResult,
    run_capture_3d_acceptance,
)
from myth_forge_api.capture_scene_handoff_acceptance import (
    CaptureSceneHandoffAcceptanceResult,
    run_capture_scene_handoff_acceptance,
)
from myth_forge_api.config import load_settings
from myth_forge_api.ios_backend_handoff_acceptance import (
    IOSBackendHandoffAcceptanceResult,
    run_ios_backend_handoff_acceptance,
)
from myth_forge_api.ios_showcase_acceptance import (
    IOSShowcaseAcceptanceResult,
    run_ios_showcase_acceptance,
)
from myth_forge_api.local_asset_handoff_acceptance import (
    LocalAssetHandoffAcceptanceResult,
    run_local_asset_handoff_acceptance,
)
from myth_forge_api.mobile_final_launch_readiness_acceptance import (
    MobileFinalLaunchReadinessAcceptanceResult,
    run_mobile_final_launch_readiness_acceptance,
)
from myth_forge_api.npc_agent_provider_acceptance import (
    NPCAgentProviderAcceptanceResult,
    run_npc_agent_provider_acceptance,
)
from myth_forge_api.operator_actions import (
    add_mobile_deploy_validation_command,
    normalize_operator_action,
)
from myth_forge_api.print_acceptance import (
    PrintQuoteAcceptanceResult,
    run_print_quote_acceptance,
)
from myth_forge_api.provider_handoff import build_provider_handoff_report
from myth_forge_api.resource_template_acceptance import (
    ResourceTemplateAcceptanceResult,
    run_resource_template_acceptance,
)

Profile = Literal["quick", "full"]

@dataclass(frozen=True)
class CommandExecutionResult:
    exit_code: int
    stdout: str
    stderr: str
    elapsed_seconds: float


@dataclass(frozen=True)
class InlineCheckResult:
    exit_code: int
    report: dict[str, Any]


@dataclass(frozen=True)
class FinalAcceptanceResult:
    exit_code: int
    report: dict[str, Any]


@dataclass(frozen=True)
class CommandCheckDefinition:
    id: str
    label: str
    command: list[str]


CommandRunner = Callable[[list[str], Path], CommandExecutionResult]
ProviderHandoffRunner = Callable[[bool], InlineCheckResult]
DemoAcceptanceRunner = Callable[..., DemoAcceptanceResult]
Capture3DAcceptanceRunner = Callable[[], Capture3DAcceptanceResult | InlineCheckResult]
ARKitScanGenerationAcceptanceRunner = Callable[
    [],
    ARKitScanGenerationAcceptanceResult | InlineCheckResult,
]
PrintQuoteAcceptanceRunner = Callable[[], PrintQuoteAcceptanceResult | InlineCheckResult]
IOSShowcaseAcceptanceRunner = Callable[[], IOSShowcaseAcceptanceResult | InlineCheckResult]
IOSBackendHandoffAcceptanceRunner = Callable[
    [],
    IOSBackendHandoffAcceptanceResult | InlineCheckResult,
]
ResourceTemplateAcceptanceRunner = Callable[
    [],
    ResourceTemplateAcceptanceResult | InlineCheckResult,
]
MobileFinalLaunchReadinessAcceptanceRunner = Callable[
    [],
    MobileFinalLaunchReadinessAcceptanceResult | InlineCheckResult,
]
LocalAssetHandoffAcceptanceRunner = Callable[
    [],
    LocalAssetHandoffAcceptanceResult | InlineCheckResult,
]
NPCAgentProviderAcceptanceRunner = Callable[
    [],
    NPCAgentProviderAcceptanceResult | InlineCheckResult,
]
CaptureSceneHandoffAcceptanceRunner = Callable[
    [],
    CaptureSceneHandoffAcceptanceResult | InlineCheckResult,
]


FULL_REGRESSION_COMMANDS = [
    CommandCheckDefinition(
        id="backend_lint",
        label="Backend lint",
        command=["make", "backend-lint"],
    ),
    CommandCheckDefinition(
        id="backend_test",
        label="Backend tests",
        command=["make", "backend-test"],
    ),
    CommandCheckDefinition(
        id="swift_project_checks",
        label="Swift project checks",
        command=[
            "swift",
            "run",
            "--package-path",
            "apps/mobile/ios",
            "PersonalMythForgeMobileProjectChecks",
        ],
    ),
    CommandCheckDefinition(
        id="swift_core_contract_tests",
        label="Swift core contract tests",
        command=[
            "swift",
            "run",
            "--package-path",
            "apps/mobile/ios",
            "PersonalMythForgeMobileCoreContractTests",
        ],
    ),
    CommandCheckDefinition(
        id="swift_app_compile_check",
        label="Swift app compile check",
        command=[
            "swift",
            "build",
            "--package-path",
            "apps/mobile/ios",
            "--product",
            "PersonalMythForgeMobileAppCompileCheck",
        ],
    ),
]

MOBILE_GATE_COMMANDS = [
    CommandCheckDefinition(
        id="mobile_deploy_preflight",
        label="iOS deploy preflight",
        command=["make", "mobile-deploy-preflight"],
    ),
    CommandCheckDefinition(
        id="mobile_xcode_build",
        label="Xcode build gate",
        command=["make", "mobile-xcode-build"],
    ),
]


def run_final_acceptance(
    *,
    profile: Profile = "quick",
    provider_mode: ProviderMode = "local",
    require_real_core: bool = False,
    allow_live_provider_calls: bool = False,
    npc_steps: int = 3,
    repo_root: str | Path | None = None,
    command_runner: CommandRunner | None = None,
    provider_handoff_runner: ProviderHandoffRunner | None = None,
    demo_acceptance_runner: DemoAcceptanceRunner | None = None,
    capture_3d_acceptance_runner: Capture3DAcceptanceRunner | None = None,
    arkit_scan_generation_acceptance_runner: (
        ARKitScanGenerationAcceptanceRunner | None
    ) = None,
    print_quote_acceptance_runner: PrintQuoteAcceptanceRunner | None = None,
    ios_showcase_acceptance_runner: IOSShowcaseAcceptanceRunner | None = None,
    ios_backend_handoff_acceptance_runner: IOSBackendHandoffAcceptanceRunner | None = None,
    resource_template_acceptance_runner: ResourceTemplateAcceptanceRunner | None = None,
    mobile_final_launch_readiness_acceptance_runner: (
        MobileFinalLaunchReadinessAcceptanceRunner | None
    ) = None,
    local_asset_handoff_acceptance_runner: LocalAssetHandoffAcceptanceRunner | None = None,
    npc_agent_provider_acceptance_runner: NPCAgentProviderAcceptanceRunner | None = None,
    capture_scene_handoff_acceptance_runner: CaptureSceneHandoffAcceptanceRunner | None = None,
) -> FinalAcceptanceResult:
    if profile not in ("quick", "full"):
        raise ValueError(f"Unsupported final acceptance profile: {profile}")
    if provider_mode not in ("local", "configured"):
        raise ValueError(f"Unsupported provider mode: {provider_mode}")

    started_at = time.perf_counter()
    selected_repo_root = _repo_root(repo_root)
    selected_command_runner = command_runner or _subprocess_command_runner
    selected_provider_handoff_runner = provider_handoff_runner or _run_provider_handoff
    selected_demo_acceptance_runner = demo_acceptance_runner or run_demo_acceptance
    selected_capture_3d_acceptance_runner = (
        capture_3d_acceptance_runner or run_capture_3d_acceptance
    )
    selected_arkit_scan_generation_acceptance_runner = (
        arkit_scan_generation_acceptance_runner or run_arkit_scan_generation_acceptance
    )
    selected_print_quote_acceptance_runner = (
        print_quote_acceptance_runner or run_print_quote_acceptance
    )
    selected_ios_showcase_acceptance_runner = (
        ios_showcase_acceptance_runner
        or (lambda: run_ios_showcase_acceptance(repo_root=selected_repo_root))
    )
    selected_ios_backend_handoff_acceptance_runner = (
        ios_backend_handoff_acceptance_runner
        or (lambda: run_ios_backend_handoff_acceptance(repo_root=selected_repo_root))
    )
    selected_resource_template_acceptance_runner = (
        resource_template_acceptance_runner
        or (lambda: run_resource_template_acceptance(repo_root=selected_repo_root))
    )
    selected_mobile_final_launch_readiness_acceptance_runner = (
        mobile_final_launch_readiness_acceptance_runner
        or (
            lambda: run_mobile_final_launch_readiness_acceptance(
                repo_root=selected_repo_root
            )
        )
    )
    selected_local_asset_handoff_acceptance_runner = (
        local_asset_handoff_acceptance_runner
        or (lambda: run_local_asset_handoff_acceptance(repo_root=selected_repo_root))
    )
    selected_npc_agent_provider_acceptance_runner = (
        npc_agent_provider_acceptance_runner
        or (lambda: run_npc_agent_provider_acceptance(repo_root=selected_repo_root))
    )
    selected_capture_scene_handoff_acceptance_runner = (
        capture_scene_handoff_acceptance_runner or run_capture_scene_handoff_acceptance
    )

    checks: list[dict[str, Any]] = []
    checks.append(
        _run_inline_check(
            check_id="provider_handoff",
            label="Provider handoff readiness",
            runner=lambda: selected_provider_handoff_runner(require_real_core),
            require_real_core=require_real_core,
        )
    )
    checks.append(
        _run_inline_check(
            check_id="demo_acceptance",
            label="Demo acceptance",
            runner=lambda: selected_demo_acceptance_runner(
                provider_mode=provider_mode,
                npc_steps=npc_steps,
                require_real_core=require_real_core,
                allow_live_provider_calls=allow_live_provider_calls,
            ),
            require_real_core=require_real_core,
        )
    )
    checks.append(
        _run_inline_check(
            check_id="npc_agent_provider_acceptance",
            label="NPC agent provider source acceptance",
            runner=selected_npc_agent_provider_acceptance_runner,
            require_real_core=False,
        )
    )
    checks.append(
        _run_inline_check(
            check_id="capture_3d_acceptance",
            label="Capture-to-3D acceptance",
            runner=selected_capture_3d_acceptance_runner,
            require_real_core=False,
        )
    )
    checks.append(
        _run_inline_check(
            check_id="arkit_scan_generation_acceptance",
            label="ARKit scan generation acceptance",
            runner=selected_arkit_scan_generation_acceptance_runner,
            require_real_core=False,
        )
    )
    checks.append(
        _run_inline_check(
            check_id="print_quote_acceptance",
            label="Print quote acceptance",
            runner=selected_print_quote_acceptance_runner,
            require_real_core=False,
        )
    )
    checks.append(
        _run_inline_check(
            check_id="ios_showcase_acceptance",
            label="iOS showcase source acceptance",
            runner=selected_ios_showcase_acceptance_runner,
            require_real_core=False,
        )
    )
    checks.append(
        _run_inline_check(
            check_id="ios_backend_handoff_acceptance",
            label="iPhone backend handoff source acceptance",
            runner=selected_ios_backend_handoff_acceptance_runner,
            require_real_core=False,
        )
    )
    checks.append(
        _run_inline_check(
            check_id="resource_template_acceptance",
            label="Resource template source acceptance",
            runner=selected_resource_template_acceptance_runner,
            require_real_core=False,
        )
    )
    checks.append(
        _run_inline_check(
            check_id="mobile_final_launch_readiness_acceptance",
            label="Mobile final launch readiness acceptance",
            runner=selected_mobile_final_launch_readiness_acceptance_runner,
            require_real_core=False,
        )
    )
    checks.append(
        _run_inline_check(
            check_id="local_asset_handoff_acceptance",
            label="Local generated asset handoff acceptance",
            runner=selected_local_asset_handoff_acceptance_runner,
            require_real_core=False,
        )
    )
    checks.append(
        _run_inline_check(
            check_id="capture_scene_handoff_acceptance",
            label="Capture-to-scene asset handoff acceptance",
            runner=selected_capture_scene_handoff_acceptance_runner,
            require_real_core=False,
        )
    )

    for definition in _command_checks_for_profile(profile):
        checks.append(
            _run_command_check(
                definition=definition,
                repo_root=selected_repo_root,
                command_runner=selected_command_runner,
            )
        )

    summary = _summary(checks)
    overall_status = _overall_status(summary)
    exit_code = _exit_code_for_status(overall_status)
    first_blocker = _first_blocker(checks)
    report = {
        "kind": "final_acceptance_report",
        "profile": profile,
        "provider_mode": provider_mode,
        "require_real_core": require_real_core,
        "allow_live_provider_calls": allow_live_provider_calls,
        "status": overall_status,
        "overall_status": overall_status,
        "summary": summary,
        "first_blocker": first_blocker,
        "next_action": _next_action(first_blocker),
        "operator_actions": _operator_actions(checks),
        "checks": checks,
        "timings": {"total_elapsed_seconds": round(time.perf_counter() - started_at, 4)},
        "safety": _safety_summary(),
    }
    return FinalAcceptanceResult(
        exit_code=exit_code,
        report=_sanitize_report(report, selected_repo_root),
    )


def _repo_root(repo_root: str | Path | None) -> Path:
    if repo_root is not None:
        return Path(repo_root)
    return Path(__file__).resolve().parents[4]


def _command_checks_for_profile(profile: Profile) -> list[CommandCheckDefinition]:
    if profile == "quick":
        return MOBILE_GATE_COMMANDS
    return [*FULL_REGRESSION_COMMANDS, *MOBILE_GATE_COMMANDS]


def _run_inline_check(
    *,
    check_id: str,
    label: str,
    runner: Callable[
        [],
        InlineCheckResult
        | DemoAcceptanceResult
        | Capture3DAcceptanceResult
        | ARKitScanGenerationAcceptanceResult
        | PrintQuoteAcceptanceResult
        | IOSShowcaseAcceptanceResult
        | IOSBackendHandoffAcceptanceResult
        | ResourceTemplateAcceptanceResult
        | MobileFinalLaunchReadinessAcceptanceResult
        | LocalAssetHandoffAcceptanceResult
        | NPCAgentProviderAcceptanceResult
        | CaptureSceneHandoffAcceptanceResult
    ],
    require_real_core: bool,
) -> dict[str, Any]:
    started_at = time.perf_counter()
    try:
        result = runner()
        status, classification = _classify_inline_result(
            check_id=check_id,
            exit_code=result.exit_code,
            require_real_core=require_real_core,
        )
        return {
            "id": check_id,
            "label": label,
            "kind": "in_process",
            "status": status,
            "classification": classification,
            "exit_code": result.exit_code,
            "elapsed_seconds": round(time.perf_counter() - started_at, 4),
            "report": result.report,
        }
    except Exception as exc:
        return {
            "id": check_id,
            "label": label,
            "kind": "in_process",
            "status": "failed",
            "classification": "runner_failed",
            "exit_code": 1,
            "elapsed_seconds": round(time.perf_counter() - started_at, 4),
            "error": str(exc),
        }


def _classify_inline_result(
    *,
    check_id: str,
    exit_code: int,
    require_real_core: bool,
) -> tuple[str, str]:
    if exit_code == 0:
        return "passed", "ready"
    if exit_code == 2 and check_id == "demo_acceptance":
        return "blocked", "blocked_by_provider_configuration"
    if (
        exit_code == 2
        and require_real_core
        and check_id in {"provider_handoff", "demo_acceptance"}
    ):
        return "blocked", "blocked_by_provider_configuration"
    return "failed", "runner_failed"


def _run_command_check(
    *,
    definition: CommandCheckDefinition,
    repo_root: Path,
    command_runner: CommandRunner,
) -> dict[str, Any]:
    started_at = time.perf_counter()
    try:
        result = command_runner(definition.command, repo_root)
        status, classification = _classify_command_result(definition.id, result)
        report = {
            "id": definition.id,
            "label": definition.label,
            "kind": "command",
            "status": status,
            "classification": classification,
            "command": definition.command,
            "exit_code": result.exit_code,
            "elapsed_seconds": result.elapsed_seconds,
        }
        if result.stdout:
            report["stdout_tail"] = _tail(result.stdout)
        if result.stderr:
            report["stderr_tail"] = _tail(result.stderr)
        return report
    except Exception as exc:
        return {
            "id": definition.id,
            "label": definition.label,
            "kind": "command",
            "status": "failed",
            "classification": "runner_failed",
            "command": definition.command,
            "exit_code": 1,
            "elapsed_seconds": round(time.perf_counter() - started_at, 4),
            "error": str(exc),
        }


def _subprocess_command_runner(command: list[str], cwd: Path) -> CommandExecutionResult:
    started_at = time.perf_counter()
    completed = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )
    return CommandExecutionResult(
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        elapsed_seconds=round(time.perf_counter() - started_at, 4),
    )


def _classify_command_result(
    check_id: str,
    result: CommandExecutionResult,
) -> tuple[str, str]:
    if result.exit_code == 0:
        return "passed", "command_succeeded"
    output = f"{result.stdout}\n{result.stderr}".lower()
    if (
        check_id == "mobile_deploy_preflight"
        and result.exit_code == 2
        and "backend health" in output
    ):
        return "blocked", "blocked_by_local_ios_backend_health"
    if check_id == "mobile_deploy_preflight" and result.exit_code == 2:
        return "blocked", "blocked_by_local_ios_deploy_config"
    if check_id == "mobile_xcode_build":
        if result.exit_code == 127 or "could not find xcodebuild" in output:
            return "blocked", "blocked_by_xcode_installation"
        if (
            result.exit_code == 69
            or "error 69" in output
            or ("license" in output and ("xcode" in output or "sdk" in output))
        ):
            return "blocked", "blocked_by_apple_sdk_license"
    return "failed", "command_failed"


def _run_provider_handoff(require_core_real: bool) -> InlineCheckResult:
    report = build_provider_handoff_report(load_settings())
    if require_core_real and not report["core_real_ready"]:
        return InlineCheckResult(exit_code=2, report=report)
    return InlineCheckResult(exit_code=0, report=report)


def _summary(checks: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "passed": sum(1 for check in checks if check["status"] == "passed"),
        "blocked": sum(1 for check in checks if check["status"] == "blocked"),
        "failed": sum(1 for check in checks if check["status"] == "failed"),
        "skipped": sum(1 for check in checks if check["status"] == "skipped"),
    }


def _operator_actions(checks: list[dict[str, Any]]) -> list[str]:
    actions: list[str] = []
    for check in checks:
        status = str(check.get("status", ""))
        if status not in {"blocked", "failed"}:
            continue
        check_id = str(check.get("id", "check"))
        classification = str(check.get("classification", ""))
        label = str(check.get("label", check_id))
        if (
            check_id == "mobile_deploy_preflight"
            and classification == "blocked_by_local_ios_backend_health"
        ):
            actions.append("start backend-device-demo and rerun mobile deploy preflight")
        elif check_id == "mobile_deploy_preflight":
            actions.append("provide iOS deploy config and rerun mobile deploy preflight")
        elif check_id == "mobile_xcode_build":
            actions.append("resolve Xcode build gate outside the app")
        elif classification == "blocked_by_provider_configuration":
            actions.append(
                "provide backend provider keys in "
                "services/backend/.local/final-resources.env and rerun final acceptance"
            )
        elif status == "failed":
            actions.append(f"fix {check_id}: {label}")
        else:
            command = check.get("command")
            if isinstance(command, list) and command:
                joined_command = " ".join(str(part) for part in command)
                actions.append(f"unblock {check_id}: {joined_command}")
            else:
                actions.append(f"unblock {check_id}: {label}")
    return _dedupe([_validation_aware_action(action) for action in actions])[:6]


def _first_blocker(checks: list[dict[str, Any]]) -> dict[str, Any] | None:
    for check in checks:
        if str(check.get("status", "")) in {"blocked", "failed"}:
            return _check_blocker(check)
    return None


def _check_blocker(check: dict[str, Any]) -> dict[str, Any]:
    child_blocker = _child_blocker(check)
    if child_blocker is not None:
        return child_blocker
    check_id = str(check.get("id", "check"))
    classification = str(check.get("classification", ""))
    return {
        "id": check_id,
        "label": str(check.get("label", check_id)),
        "status": str(check.get("status", "blocked")),
        "classification": classification,
        "command": _blocker_command(check_id, classification, check),
        "detail": _blocker_detail(check),
        "validation_command": _validation_command(check_id, check),
    }


def _child_blocker(check: dict[str, Any]) -> dict[str, Any] | None:
    report = check.get("report")
    if not isinstance(report, dict):
        return None
    child = report.get("next_action") or report.get("first_blocker")
    if not isinstance(child, dict):
        return None
    child_blocker = dict(child)
    child_blocker.pop("source", None)
    child_blocker.setdefault("status", str(check.get("status", "blocked")))
    child_blocker.setdefault(
        "classification",
        str(check.get("classification", "blocked")),
    )
    child_blocker.setdefault(
        "validation_command",
        _validation_command(str(check.get("id")), check),
    )
    return child_blocker


def _next_action(first_blocker: dict[str, Any] | None) -> dict[str, Any] | None:
    if first_blocker is None:
        return None
    return {**first_blocker, "source": "first_blocker"}


def _blocker_command(
    check_id: str,
    classification: str,
    check: dict[str, Any],
) -> str:
    if check_id == "mobile_deploy_preflight":
        if classification == "blocked_by_local_ios_backend_health":
            return (
                "start backend-device-demo before device checks: make backend-device-demo; "
                "rerun make mobile-deploy-preflight"
            )
        return "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig"
    if check_id == "mobile_xcode_build":
        return (
            "accept the Xcode license outside Codex, then rerun "
            "make mobile-xcode-build-evidence"
        )
    if classification == "blocked_by_provider_configuration":
        return "make provider-handoff"
    command = check.get("command")
    if isinstance(command, list) and command:
        return " ".join(str(part) for part in command)
    return f"inspect {check_id}"


def _validation_command(check_id: str, check: dict[str, Any]) -> str:
    if check_id == "mobile_deploy_preflight":
        return "make mobile-deploy-preflight"
    if check_id == "mobile_xcode_build":
        return "make mobile-xcode-build-evidence"
    if check_id in {"provider_handoff", "demo_acceptance"}:
        return "make final-acceptance-local"
    command = check.get("command")
    if isinstance(command, list) and command:
        return " ".join(str(part) for part in command)
    return "make final-acceptance-local"


def _blocker_detail(check: dict[str, Any]) -> str:
    for field in ("stderr_tail", "stdout_tail", "error"):
        value = check.get(field)
        if isinstance(value, str) and value:
            return value
    return str(check.get("label", check.get("id", "Final acceptance check blocked.")))


def _validation_aware_action(action: str) -> str:
    return add_mobile_deploy_validation_command(normalize_operator_action(action))


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        deduped.append(value)
    return deduped


def _overall_status(summary: dict[str, int]) -> str:
    if summary["failed"] > 0:
        return "failed"
    if summary["blocked"] > 0:
        return "blocked"
    return "passed"


def _exit_code_for_status(status: str) -> int:
    if status == "passed":
        return 0
    if status == "blocked":
        return 2
    return 1


def _tail(text: str, limit: int = 1200) -> str:
    if len(text) <= limit:
        return text
    return text[-limit:]


def _safety_summary() -> dict[str, Any]:
    return {
        "global_mutation": False,
        "live_provider_calls_by_default": False,
        "mobile_secret_policy": "Provider secrets stay on the backend.",
        "raw_media_in_report": False,
        "raw_personal_source_in_report": False,
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
    replacements = [
        r"Authorization\s*[=:]\s*Bearer\s+[A-Za-z0-9._~+/\-=:-]+",
        r"Bearer\s+[A-Za-z0-9._~+/\-=:-]+",
        r"raw=[^\s,;\"']+",
        r"api[_-]?key\s*[=:]\s*[^\s,;\"']+",
        r"data:[A-Za-z0-9.+-]+/[A-Za-z0-9.+-]+;base64,[A-Za-z0-9+/=_-]+",
        r"local-capture://[^\s,;\"']+",
        r"https?://pay\.[^\s,;\"']+",
        r"https?://checkout\.[^\s,;\"']+",
        r"file://[^\s,;\"']+",
    ]
    for pattern in replacements:
        sanitized = re.sub(pattern, "[redacted]", sanitized, flags=re.IGNORECASE)
    for path in {repo_root, Path.home(), Path("/tmp")}:
        path_text = str(path)
        if path_text:
            sanitized = sanitized.replace(path_text, "[path]")
    sanitized = re.sub(r"/Users/[^\s,;\"']+", "[path]", sanitized)
    return sanitized
