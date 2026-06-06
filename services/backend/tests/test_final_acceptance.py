import json
from pathlib import Path

from myth_forge_api.acceptance import DemoAcceptanceResult
from myth_forge_api.final_acceptance import (
    CommandExecutionResult,
    InlineCheckResult,
    run_final_acceptance,
)
from myth_forge_api.ios_backend_handoff_acceptance import (
    IOSBackendHandoffAcceptanceResult,
)
from myth_forge_api.ios_showcase_acceptance import IOSShowcaseAcceptanceResult


def passing_ios_showcase_result() -> IOSShowcaseAcceptanceResult:
    return IOSShowcaseAcceptanceResult(
        exit_code=0,
        report={
            "kind": "ios_showcase_acceptance_report",
            "status": "succeeded",
            "summary": {"passed": 15, "failed": 0},
        },
    )


def passing_ios_backend_handoff_result() -> IOSBackendHandoffAcceptanceResult:
    return IOSBackendHandoffAcceptanceResult(
        exit_code=0,
        report={
            "kind": "ios_backend_handoff_acceptance_report",
            "status": "succeeded",
            "summary": {"passed": 7, "failed": 0},
        },
    )


def passing_resource_template_result() -> InlineCheckResult:
    return InlineCheckResult(
        exit_code=0,
        report={
            "kind": "resource_template_acceptance_report",
            "status": "succeeded",
            "summary": {"passed": 7, "failed": 0},
        },
    )


def passing_local_asset_handoff_result() -> InlineCheckResult:
    return InlineCheckResult(
        exit_code=0,
        report={
            "kind": "local_asset_handoff_acceptance_report",
            "status": "succeeded",
            "summary": {"passed": 6, "failed": 0},
        },
    )


def passing_capture_scene_handoff_result() -> InlineCheckResult:
    return InlineCheckResult(
        exit_code=0,
        report={
            "kind": "capture_scene_handoff_acceptance_report",
            "status": "succeeded",
            "summary": {"passed": 8, "failed": 0},
        },
    )


def test_final_acceptance_quick_profile_classifies_known_local_blockers(tmp_path) -> None:
    commands: list[list[str]] = []
    demo_calls: list[dict[str, object]] = []

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
        demo_acceptance_runner=lambda **kwargs: (
            demo_calls.append(kwargs)
            or DemoAcceptanceResult(
                exit_code=0,
                report={
                    "kind": "demo_acceptance_report",
                    "mode": kwargs["provider_mode"],
                    "status": "succeeded",
                },
            )
        ),
        capture_3d_acceptance_runner=lambda: InlineCheckResult(
            exit_code=0,
            report={
                "kind": "capture_3d_acceptance_report",
                "status": "succeeded",
                "source_image_count": 3,
                "provider_request_source_image_count": 3,
                "generation_provenance": {"input_mode": "multi_image"},
            },
        ),
        print_quote_acceptance_runner=lambda: InlineCheckResult(
            exit_code=0,
            report={
                "kind": "print_quote_acceptance_report",
                "status": "succeeded",
                "quote_status": "draft_quote",
                "provider": "local_stub",
                "estimated_price_cents": 1600,
            },
        ),
        ios_showcase_acceptance_runner=passing_ios_showcase_result,
        ios_backend_handoff_acceptance_runner=passing_ios_backend_handoff_result,
        resource_template_acceptance_runner=passing_resource_template_result,
        local_asset_handoff_acceptance_runner=passing_local_asset_handoff_result,
        capture_scene_handoff_acceptance_runner=passing_capture_scene_handoff_result,
    )

    assert result.exit_code == 2
    assert result.report["kind"] == "final_acceptance_report"
    assert result.report["profile"] == "quick"
    assert result.report["allow_live_provider_calls"] is False
    assert result.report["overall_status"] == "blocked"
    assert result.report["summary"] == {
        "passed": 9,
        "blocked": 2,
        "failed": 0,
        "skipped": 0,
    }
    checks = {check["id"]: check for check in result.report["checks"]}
    assert list(checks) == [
        "provider_handoff",
        "demo_acceptance",
        "capture_3d_acceptance",
        "print_quote_acceptance",
        "ios_showcase_acceptance",
        "ios_backend_handoff_acceptance",
        "resource_template_acceptance",
        "local_asset_handoff_acceptance",
        "capture_scene_handoff_acceptance",
        "mobile_deploy_preflight",
        "mobile_xcode_build",
    ]
    assert checks["provider_handoff"]["status"] == "passed"
    assert checks["demo_acceptance"]["status"] == "passed"
    assert checks["capture_3d_acceptance"]["status"] == "passed"
    assert checks["capture_3d_acceptance"]["report"]["source_image_count"] == 3
    assert checks["print_quote_acceptance"]["status"] == "passed"
    assert checks["print_quote_acceptance"]["report"]["quote_status"] == "draft_quote"
    assert checks["ios_showcase_acceptance"]["status"] == "passed"
    assert checks["ios_showcase_acceptance"]["report"]["summary"] == {
        "passed": 15,
        "failed": 0,
    }
    assert checks["ios_backend_handoff_acceptance"]["status"] == "passed"
    assert checks["ios_backend_handoff_acceptance"]["report"]["summary"] == {
        "passed": 7,
        "failed": 0,
    }
    assert checks["resource_template_acceptance"]["status"] == "passed"
    assert checks["resource_template_acceptance"]["report"]["summary"] == {
        "passed": 7,
        "failed": 0,
    }
    assert checks["local_asset_handoff_acceptance"]["status"] == "passed"
    assert checks["local_asset_handoff_acceptance"]["report"]["summary"] == {
        "passed": 6,
        "failed": 0,
    }
    assert checks["capture_scene_handoff_acceptance"]["status"] == "passed"
    assert checks["capture_scene_handoff_acceptance"]["report"]["summary"] == {
        "passed": 8,
        "failed": 0,
    }
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
    assert demo_calls == [
        {
            "provider_mode": "local",
            "npc_steps": 3,
            "require_real_core": False,
            "allow_live_provider_calls": False,
        }
    ]
    assert "backend_lint" not in checks
    assert "/Users/zhexu/private" not in json.dumps(result.report)


def test_final_acceptance_classifies_mobile_backend_health_blocker(tmp_path) -> None:
    def command_runner(command: list[str], cwd: Path) -> CommandExecutionResult:
        if command == ["make", "mobile-deploy-preflight"]:
            return CommandExecutionResult(
                exit_code=2,
                stdout="",
                stderr="Backend health check failed. Start backend-device-demo.",
                elapsed_seconds=0.01,
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
        capture_3d_acceptance_runner=lambda: InlineCheckResult(
            exit_code=0,
            report={"kind": "capture_3d_acceptance_report", "status": "succeeded"},
        ),
        print_quote_acceptance_runner=lambda: InlineCheckResult(
            exit_code=0,
            report={"kind": "print_quote_acceptance_report", "status": "succeeded"},
        ),
        ios_showcase_acceptance_runner=passing_ios_showcase_result,
        ios_backend_handoff_acceptance_runner=passing_ios_backend_handoff_result,
        resource_template_acceptance_runner=passing_resource_template_result,
        local_asset_handoff_acceptance_runner=passing_local_asset_handoff_result,
        capture_scene_handoff_acceptance_runner=passing_capture_scene_handoff_result,
    )

    checks = {check["id"]: check for check in result.report["checks"]}
    assert result.exit_code == 2
    assert checks["mobile_deploy_preflight"]["status"] == "blocked"
    assert checks["mobile_deploy_preflight"]["classification"] == (
        "blocked_by_local_ios_backend_health"
    )
    assert checks["mobile_xcode_build"]["status"] == "passed"
    assert checks["mobile_deploy_preflight"]["stderr_tail"] == (
        "Backend health check failed. Start backend-device-demo."
    )


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
        capture_3d_acceptance_runner=lambda: InlineCheckResult(
            exit_code=0,
            report={
                "kind": "capture_3d_acceptance_report",
                "status": "succeeded",
                "error": (
                    "data:image/png;base64,AAAA "
                    "local-capture://cap_0123456789abcdef/media_0.png "
                    "/tmp/personal-myth-forge/capture.png "
                    "Authorization=Bearer capture-secret"
                ),
            },
        ),
        print_quote_acceptance_runner=lambda: InlineCheckResult(
            exit_code=0,
            report={
                "kind": "print_quote_acceptance_report",
                "status": "succeeded",
                "error": (
                    "api_key=treatstock-secret "
                    "checkout_url=https://pay.example/private "
                    "/tmp/personal-myth-forge/print.3mf"
                ),
            },
        ),
        ios_showcase_acceptance_runner=passing_ios_showcase_result,
        ios_backend_handoff_acceptance_runner=passing_ios_backend_handoff_result,
        resource_template_acceptance_runner=passing_resource_template_result,
        local_asset_handoff_acceptance_runner=passing_local_asset_handoff_result,
        capture_scene_handoff_acceptance_runner=passing_capture_scene_handoff_result,
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
    assert checks["capture_3d_acceptance"]["status"] == "passed"
    assert checks["print_quote_acceptance"]["status"] == "passed"
    assert checks["ios_showcase_acceptance"]["status"] == "passed"
    assert checks["resource_template_acceptance"]["status"] == "passed"
    assert checks["local_asset_handoff_acceptance"]["status"] == "passed"
    assert checks["capture_scene_handoff_acceptance"]["status"] == "passed"
    assert command_calls == 2
    assert "sk-meshy-secret" not in report_text
    assert "sk-openai-secret" not in report_text
    assert "Authorization" not in report_text
    assert "raw=private" not in report_text
    assert "data:image" not in report_text
    assert "/tmp/private" not in report_text
    assert "/Users/zhexu/Codex/personal-myth-forge" not in report_text
    assert "capture-secret" not in report_text
    assert "local-capture://" not in report_text
    assert "treatstock-secret" not in report_text
    assert "https://pay.example/private" not in report_text


def test_final_acceptance_passes_explicit_live_provider_consent_to_demo_runner(
    tmp_path,
) -> None:
    demo_calls: list[dict[str, object]] = []

    result = run_final_acceptance(
        profile="quick",
        provider_mode="configured",
        require_real_core=True,
        allow_live_provider_calls=True,
        repo_root=tmp_path,
        command_runner=lambda command, cwd: CommandExecutionResult(
            exit_code=0,
            stdout="ok",
            stderr="",
            elapsed_seconds=0.01,
        ),
        provider_handoff_runner=lambda require_core_real: InlineCheckResult(
            exit_code=0,
            report={"kind": "provider_handoff_report", "core_real_ready": True},
        ),
        demo_acceptance_runner=lambda **kwargs: (
            demo_calls.append(kwargs)
            or DemoAcceptanceResult(
                exit_code=0,
                report={"kind": "demo_acceptance_report", "status": "succeeded"},
            )
        ),
        capture_3d_acceptance_runner=lambda: InlineCheckResult(
            exit_code=0,
            report={"kind": "capture_3d_acceptance_report", "status": "succeeded"},
        ),
        print_quote_acceptance_runner=lambda: InlineCheckResult(
            exit_code=0,
            report={"kind": "print_quote_acceptance_report", "status": "succeeded"},
        ),
        ios_showcase_acceptance_runner=passing_ios_showcase_result,
        ios_backend_handoff_acceptance_runner=passing_ios_backend_handoff_result,
        resource_template_acceptance_runner=passing_resource_template_result,
        local_asset_handoff_acceptance_runner=passing_local_asset_handoff_result,
        capture_scene_handoff_acceptance_runner=passing_capture_scene_handoff_result,
    )

    assert result.exit_code == 0
    assert result.report["allow_live_provider_calls"] is True
    assert demo_calls == [
        {
            "provider_mode": "configured",
            "npc_steps": 3,
            "require_real_core": True,
            "allow_live_provider_calls": True,
        }
    ]


def test_final_acceptance_classifies_demo_consent_gate_as_blocked(tmp_path) -> None:
    result = run_final_acceptance(
        profile="quick",
        provider_mode="configured",
        require_real_core=False,
        repo_root=tmp_path,
        command_runner=lambda command, cwd: CommandExecutionResult(
            exit_code=0,
            stdout="ok",
            stderr="",
            elapsed_seconds=0.01,
        ),
        provider_handoff_runner=lambda require_core_real: InlineCheckResult(
            exit_code=0,
            report={"kind": "provider_handoff_report", "core_real_ready": True},
        ),
        demo_acceptance_runner=lambda **kwargs: DemoAcceptanceResult(
            exit_code=2,
            report={
                "kind": "demo_acceptance_report",
                "status": "not_ready",
                "live_provider_consent_required": True,
                "error": "Live provider calls require --allow-live-provider-calls.",
            },
        ),
        capture_3d_acceptance_runner=lambda: InlineCheckResult(
            exit_code=0,
            report={"kind": "capture_3d_acceptance_report", "status": "succeeded"},
        ),
        print_quote_acceptance_runner=lambda: InlineCheckResult(
            exit_code=0,
            report={"kind": "print_quote_acceptance_report", "status": "succeeded"},
        ),
        ios_showcase_acceptance_runner=passing_ios_showcase_result,
        ios_backend_handoff_acceptance_runner=passing_ios_backend_handoff_result,
        resource_template_acceptance_runner=passing_resource_template_result,
        local_asset_handoff_acceptance_runner=passing_local_asset_handoff_result,
        capture_scene_handoff_acceptance_runner=passing_capture_scene_handoff_result,
    )

    checks = {check["id"]: check for check in result.report["checks"]}

    assert result.exit_code == 2
    assert result.report["overall_status"] == "blocked"
    assert checks["demo_acceptance"]["status"] == "blocked"
    assert checks["demo_acceptance"]["classification"] == (
        "blocked_by_provider_configuration"
    )


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
        capture_3d_acceptance_runner=lambda: InlineCheckResult(
            exit_code=0,
            report={
                "kind": "capture_3d_acceptance_report",
                "status": "succeeded",
                "source_image_count": 3,
            },
        ),
        print_quote_acceptance_runner=lambda: InlineCheckResult(
            exit_code=0,
            report={
                "kind": "print_quote_acceptance_report",
                "status": "succeeded",
                "quote_status": "draft_quote",
                "provider": "local_stub",
                "estimated_price_cents": 1600,
            },
        ),
        ios_showcase_acceptance_runner=passing_ios_showcase_result,
        ios_backend_handoff_acceptance_runner=passing_ios_backend_handoff_result,
        resource_template_acceptance_runner=passing_resource_template_result,
        local_asset_handoff_acceptance_runner=passing_local_asset_handoff_result,
        capture_scene_handoff_acceptance_runner=passing_capture_scene_handoff_result,
    )

    check_ids = [check["id"] for check in result.report["checks"]]

    assert result.exit_code == 0
    assert result.report["overall_status"] == "passed"
    assert result.report["summary"] == {
        "passed": 16,
        "blocked": 0,
        "failed": 0,
        "skipped": 0,
    }
    assert check_ids == [
        "provider_handoff",
        "demo_acceptance",
        "capture_3d_acceptance",
        "print_quote_acceptance",
        "ios_showcase_acceptance",
        "ios_backend_handoff_acceptance",
        "resource_template_acceptance",
        "local_asset_handoff_acceptance",
        "capture_scene_handoff_acceptance",
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
