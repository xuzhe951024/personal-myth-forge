import json
from pathlib import Path

from myth_forge_api.mobile_final_launch_readiness_acceptance import (
    EndpointProbeResponse,
    run_mobile_final_launch_readiness_acceptance,
)


REPO_ROOT = Path(__file__).resolve().parents[3]


def test_mobile_final_launch_readiness_acceptance_checks_endpoint_source_and_safety() -> None:
    result = run_mobile_final_launch_readiness_acceptance(repo_root=REPO_ROOT)

    assert result.exit_code == 0
    assert result.report["kind"] == "mobile_final_launch_readiness_acceptance_report"
    assert result.report["status"] == "succeeded"
    assert result.report["summary"] == {"passed": 4, "failed": 0}

    checks = {check["id"]: check for check in result.report["checks"]}
    assert list(checks) == [
        "endpoint_local_report",
        "endpoint_invalid_mode",
        "mobile_source",
        "safety",
    ]
    assert checks["endpoint_local_report"]["status"] == "passed"
    assert result.report["endpoint"]["local_status_code"] == 200
    assert result.report["endpoint"]["kind"] == "final_demo_launch_report"
    assert result.report["endpoint"]["mode"] == "local"
    assert result.report["endpoint"]["live_calls_by_default"] is False
    assert result.report["endpoint"]["invalid_mode_status_code"] == 422
    assert result.report["mobile_source"]["failed_requirements"] == []
    assert result.report["safety"] == {
        "global_mutation": False,
        "live_provider_calls_by_default": False,
        "provider_secrets_in_report": False,
        "raw_media_in_report": False,
        "payment_links_in_report": False,
        "absolute_paths_in_report": False,
    }
    report_text = json.dumps(result.report)
    assert "sk-" not in report_text
    assert "Authorization" not in report_text
    assert "data:image" not in report_text
    assert "checkout_url" not in report_text
    assert "/Users/" not in report_text


def test_mobile_final_launch_readiness_acceptance_fails_missing_mobile_source(
    tmp_path: Path,
) -> None:
    result = run_mobile_final_launch_readiness_acceptance(repo_root=tmp_path)

    assert result.exit_code == 1
    assert result.report["status"] == "failed"
    checks = {check["id"]: check for check in result.report["checks"]}
    assert checks["endpoint_local_report"]["status"] == "passed"
    assert checks["endpoint_invalid_mode"]["status"] == "passed"
    assert checks["mobile_source"]["status"] == "failed"
    assert result.report["mobile_source"]["failed_requirements"]
    assert any(
        requirement["file"] == "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift"
        for requirement in result.report["mobile_source"]["failed_requirements"]
    )


def test_mobile_final_launch_readiness_acceptance_fails_unsafe_endpoint_payload(
    tmp_path: Path,
) -> None:
    _write_minimal_mobile_source(tmp_path)

    def fake_endpoint_getter(path: str) -> EndpointProbeResponse:
        if path.endswith("mode=live"):
            return EndpointProbeResponse(status_code=422, payload={"detail": "invalid"}, text="invalid")
        return EndpointProbeResponse(
            status_code=200,
            payload={
                "kind": "final_demo_launch_report",
                "mode": "local",
                "live_call_policy": {"live_calls_by_default": False},
                "safety": {"global_mutation": False},
                "error": "Authorization=Bearer sk-mobile-secret data:image/png;base64,AAAA",
            },
            text="Authorization=Bearer sk-mobile-secret data:image/png;base64,AAAA",
        )

    result = run_mobile_final_launch_readiness_acceptance(
        repo_root=tmp_path,
        endpoint_getter=fake_endpoint_getter,
    )

    assert result.exit_code == 1
    checks = {check["id"]: check for check in result.report["checks"]}
    assert checks["safety"]["status"] == "failed"
    assert "sk-mobile-secret" not in json.dumps(result.report)
    assert "Authorization" not in json.dumps(result.report)
    assert "data:image" not in json.dumps(result.report)


def _write_minimal_mobile_source(root: Path) -> None:
    files: dict[str, str] = {
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift": "\n".join(
            [
                "FinalDemoLaunchReport",
                "FinalDemoLaunchPhase",
                "FinalDemoLaunchLiveCallPolicy",
                "FinalDemoLaunchSafety",
                "FinalResourcesPreflightReport",
                "FinalResourcesFileStatus",
                "FinalResourcesPreflightSummary",
            ]
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PersonalMythForgeAPIClient.swift": "\n".join(
            [
                "getFinalDemoLaunch",
                "/v1/final-demo-launch",
                "\"local\", \"configured\"",
                "Unsupported final demo launch mode.",
            ]
        ),
        "apps/mobile/ios/App/ForgeRootView.swift": "\n".join(
            [
                "finalDemoLaunch",
                "loadFinalDemoLaunch",
                "getFinalDemoLaunch(mode: \"local\")",
                "DevicePreflightSummaryBuilder.build",
            ]
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/DevicePreflight.swift": "\n".join(
            [
                "final_launch",
                "FinalDemoLaunchReport",
                "final_resources",
                "Final Resources",
                "Final launch readiness is read-only.",
                "case \"ready\"",
                "required = Set([\"backend_url\", \"providers\", \"final_launch\", \"final_resources\", \"local_demo\"])",
            ]
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift": "\n".join(
            [
                "testDecodesFinalDemoLaunchPayload",
                "testGetFinalDemoLaunchBuildsGETRequest",
                "testGetFinalDemoLaunchRejectsInvalidModeBeforeNetwork",
                "testDevicePreflightMapsFinalLaunchPartialToWaiting",
                "testDevicePreflightMapsMissingFinalResourcesPreflightToWaiting",
                "testDevicePreflightMarksReadyFinalResourcesPreflight",
                "testDevicePreflightBlocksAndRedactsFinalResourcesPreflight",
                "testDevicePreflightBlocksAndRedactsFinalLaunchError",
            ]
        ),
    }
    for relative_path, text in files.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
