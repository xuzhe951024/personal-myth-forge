import json
from pathlib import Path

from myth_forge_api.acceptance import DemoAcceptanceResult
from myth_forge_api.final_acceptance import (
    CommandExecutionResult,
    InlineCheckResult,
    run_final_acceptance,
)


def test_final_acceptance_quick_profile_classifies_known_local_blockers(tmp_path) -> None:
    commands: list[list[str]] = []

    def command_runner(command: list[str], cwd: Path) -> CommandExecutionResult:
        commands.append(command)
        if command == ["make", "mobile-deploy-preflight"]:
            return CommandExecutionResult(
                exit_code=2,
                stdout="",
                stderr="Missing DEVELOPMENT_TEAM in /Users/zhexu/private/Deployment.local.xcconfig.",
                elapsed_seconds=0.01,
            )
        if command == ["make", "mobile-xcode-build"]:
            return CommandExecutionResult(
                exit_code=69,
                stdout="",
                stderr="Agreeing to the Xcode/iOS license requires admin privileges.",
                elapsed_seconds=0.02,
            )
        return CommandExecutionResult(exit_code=0, stdout="ok", stderr="", elapsed_seconds=0.01)

    result = run_final_acceptance(
        profile="quick",
        provider_mode="local",
        require_real_core=False,
        repo_root=tmp_path,
        command_runner=command_runner,
        provider_handoff_runner=lambda require_core_real: InlineCheckResult(
            exit_code=0,
            report={"kind": "provider_handoff_report", "core_real_ready": False},
        ),
        demo_acceptance_runner=lambda **kwargs: DemoAcceptanceResult(
            exit_code=0,
            report={
                "kind": "demo_acceptance_report",
                "mode": kwargs["provider_mode"],
                "status": "succeeded",
            },
        ),
    )

    assert result.exit_code == 2
    assert result.report["kind"] == "final_acceptance_report"
    assert result.report["profile"] == "quick"
    assert result.report["overall_status"] == "blocked"
    assert result.report["summary"] == {
        "passed": 2,
        "blocked": 2,
        "failed": 0,
        "skipped": 0,
    }
    checks = {check["id"]: check for check in result.report["checks"]}
    assert list(checks) == [
        "provider_handoff",
        "demo_acceptance",
        "mobile_deploy_preflight",
        "mobile_xcode_build",
    ]
    assert checks["provider_handoff"]["status"] == "passed"
    assert checks["demo_acceptance"]["status"] == "passed"
    assert checks["mobile_deploy_preflight"]["status"] == "blocked"
    assert checks["mobile_deploy_preflight"]["classification"] == (
        "blocked_by_local_ios_deploy_config"
    )
    assert checks["mobile_xcode_build"]["status"] == "blocked"
    assert checks["mobile_xcode_build"]["classification"] == "blocked_by_apple_sdk_license"
    assert commands == [
        ["make", "mobile-deploy-preflight"],
        ["make", "mobile-xcode-build"],
    ]
    assert "backend_lint" not in checks
    assert "/Users/zhexu/private" not in json.dumps(result.report)


def test_final_acceptance_strict_provider_mode_blocks_and_sanitizes(tmp_path) -> None:
    command_calls = 0

    def command_runner(command: list[str], cwd: Path) -> CommandExecutionResult:
        nonlocal command_calls
        command_calls += 1
        return CommandExecutionResult(exit_code=0, stdout="ok", stderr="", elapsed_seconds=0.01)

    result = run_final_acceptance(
        profile="quick",
        provider_mode="configured",
        require_real_core=True,
        repo_root=tmp_path,
        command_runner=command_runner,
        provider_handoff_runner=lambda require_core_real: InlineCheckResult(
            exit_code=2,
            report={
                "kind": "provider_handoff_report",
                "missing_env": ["MESHY_API_KEY", "OPENAI_API_KEY"],
                "error": "api_key=sk-meshy-secret raw=private",
            },
        ),
        demo_acceptance_runner=lambda **kwargs: DemoAcceptanceResult(
            exit_code=2,
            report={
                "kind": "demo_acceptance_report",
                "status": "not_ready",
                "error": (
                    "Authorization=Bearer sk-openai-secret "
                    "data:image/png;base64,AAAA /tmp/private/photo.png "
                    "/Users/zhexu/Codex/personal-myth-forge/private.glb"
                ),
            },
        ),
    )

    report_text = json.dumps(result.report)
    checks = {check["id"]: check for check in result.report["checks"]}

    assert result.exit_code == 2
    assert result.report["overall_status"] == "blocked"
    assert checks["provider_handoff"]["status"] == "blocked"
    assert checks["provider_handoff"]["classification"] == (
        "blocked_by_provider_configuration"
    )
    assert checks["demo_acceptance"]["status"] == "blocked"
    assert checks["demo_acceptance"]["classification"] == (
        "blocked_by_provider_configuration"
    )
    assert command_calls == 2
    assert "sk-meshy-secret" not in report_text
    assert "sk-openai-secret" not in report_text
    assert "Authorization" not in report_text
    assert "raw=private" not in report_text
    assert "data:image" not in report_text
    assert "/tmp/private" not in report_text
    assert "/Users/zhexu/Codex/personal-myth-forge" not in report_text


def test_final_acceptance_full_profile_includes_backend_and_swift_checks(tmp_path) -> None:
    commands: list[list[str]] = []

    def command_runner(command: list[str], cwd: Path) -> CommandExecutionResult:
        commands.append(command)
        return CommandExecutionResult(exit_code=0, stdout="ok", stderr="", elapsed_seconds=0.01)

    result = run_final_acceptance(
        profile="full",
        provider_mode="local",
        require_real_core=False,
        repo_root=tmp_path,
        command_runner=command_runner,
        provider_handoff_runner=lambda require_core_real: InlineCheckResult(
            exit_code=0,
            report={"kind": "provider_handoff_report"},
        ),
        demo_acceptance_runner=lambda **kwargs: DemoAcceptanceResult(
            exit_code=0,
            report={"kind": "demo_acceptance_report", "status": "succeeded"},
        ),
    )

    check_ids = [check["id"] for check in result.report["checks"]]

    assert result.exit_code == 0
    assert result.report["overall_status"] == "passed"
    assert result.report["summary"] == {
        "passed": 9,
        "blocked": 0,
        "failed": 0,
        "skipped": 0,
    }
    assert check_ids == [
        "provider_handoff",
        "demo_acceptance",
        "backend_lint",
        "backend_test",
        "swift_project_checks",
        "swift_core_contract_tests",
        "swift_app_compile_check",
        "mobile_deploy_preflight",
        "mobile_xcode_build",
    ]
    assert commands == [
        ["make", "backend-lint"],
        ["make", "backend-test"],
        [
            "swift",
            "run",
            "--package-path",
            "apps/mobile/ios",
            "PersonalMythForgeMobileProjectChecks",
        ],
        [
            "swift",
            "run",
            "--package-path",
            "apps/mobile/ios",
            "PersonalMythForgeMobileCoreContractTests",
        ],
        [
            "swift",
            "build",
            "--package-path",
            "apps/mobile/ios",
            "--product",
            "PersonalMythForgeMobileAppCompileCheck",
        ],
        ["make", "mobile-deploy-preflight"],
        ["make", "mobile-xcode-build"],
    ]
