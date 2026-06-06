from __future__ import annotations

import json
import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Literal

from myth_forge_api.acceptance import DemoAcceptanceResult, ProviderMode, run_demo_acceptance
from myth_forge_api.capture_acceptance import (
    Capture3DAcceptanceResult,
    run_capture_3d_acceptance,
)
from myth_forge_api.config import load_settings
from myth_forge_api.ios_showcase_acceptance import (
    IOSShowcaseAcceptanceResult,
    run_ios_showcase_acceptance,
)
from myth_forge_api.print_acceptance import (
    PrintQuoteAcceptanceResult,
    run_print_quote_acceptance,
)
from myth_forge_api.providers.readiness import build_provider_readiness

Profile = Literal["quick", "full"]

CORE_PROVIDER_KINDS = ["three_d", "npc", "capture_storage"]
BACKEND_ONLY_ENV = [
    "MESHY_API_KEY",
    "OPENAI_API_KEY",
    "TREATSTOCK_API_KEY",
    "SCULPTEO_API_KEY",
]


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
PrintQuoteAcceptanceRunner = Callable[[], PrintQuoteAcceptanceResult | InlineCheckResult]
IOSShowcaseAcceptanceRunner = Callable[[], IOSShowcaseAcceptanceResult | InlineCheckResult]


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
    print_quote_acceptance_runner: PrintQuoteAcceptanceRunner | None = None,
    ios_showcase_acceptance_runner: IOSShowcaseAcceptanceRunner | None = None,
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
    selected_print_quote_acceptance_runner = (
        print_quote_acceptance_runner or run_print_quote_acceptance
    )
    selected_ios_showcase_acceptance_runner = (
        ios_showcase_acceptance_runner
        or (lambda: run_ios_showcase_acceptance(repo_root=selected_repo_root))
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
            check_id="capture_3d_acceptance",
            label="Capture-to-3D acceptance",
            runner=selected_capture_3d_acceptance_runner,
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
    report = {
        "kind": "final_acceptance_report",
        "profile": profile,
        "provider_mode": provider_mode,
        "require_real_core": require_real_core,
        "allow_live_provider_calls": allow_live_provider_calls,
        "overall_status": overall_status,
        "summary": summary,
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
        | PrintQuoteAcceptanceResult
        | IOSShowcaseAcceptanceResult,
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
    readiness = build_provider_readiness(load_settings())
    provider_items = [item.model_dump(mode="json") for item in readiness.providers]
    provider_by_kind = {item["kind"]: item for item in provider_items}
    core_items = [
        provider_by_kind[kind]
        for kind in CORE_PROVIDER_KINDS
        if kind in provider_by_kind
    ]
    missing_env = sorted(
        {
            env_name
            for provider in provider_items
            for env_name in provider.get("missing_env", [])
        }
    )
    core_real_ready = all(provider["is_real_provider_ready"] for provider in core_items)
    report = {
        "kind": "provider_handoff_report",
        "mode": "configuration",
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
    }
    if require_core_real and not core_real_ready:
        return InlineCheckResult(exit_code=2, report=report)
    return InlineCheckResult(exit_code=0, report=report)


def _summary(checks: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "passed": sum(1 for check in checks if check["status"] == "passed"),
        "blocked": sum(1 for check in checks if check["status"] == "blocked"),
        "failed": sum(1 for check in checks if check["status"] == "failed"),
        "skipped": sum(1 for check in checks if check["status"] == "skipped"),
    }


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
