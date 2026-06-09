import json
from pathlib import Path

from myth_forge_api.config import Settings
from myth_forge_api.final_showcase_readiness import (
    build_final_showcase_readiness_report,
)
from myth_forge_api.local_showcase_smoke import LocalShowcaseSmokeResult


def test_final_showcase_readiness_blocks_missing_objective_evidence(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )

    assert result.exit_code == 2
    assert result.report["kind"] == "final_showcase_readiness_report"
    assert result.report["status"] == "blocked"
    assert [row["id"] for row in result.report["capabilities"]] == [
        "ios_deployable",
        "capture_scanning",
        "local_showcase_smoke",
        "game_asset_3d_generation",
        "ai_agent_npc",
        "print_fulfillment",
        "provider_key_handoff",
        "functional_regression",
        "visual_regression",
        "privacy_safety",
    ]
    assert result.report["capabilities_by_id"]["capture_scanning"]["status"] == (
        "blocked"
    )
    local_smoke = result.report["capabilities_by_id"]["local_showcase_smoke"]
    assert local_smoke["status"] == "ready"
    assert local_smoke["command"] == "make local-showcase-smoke"
    assert "local_showcase_smoke_report:succeeded" in local_smoke["evidence"]
    assert "http_steps:6" in local_smoke["evidence"]
    assert "npc_ticks:2" in local_smoke["evidence"]
    assert "downloads:3" in local_smoke["evidence"]
    assert result.report["evidence"]["local_showcase_smoke"]["kind"] == (
        "local_showcase_smoke_report"
    )
    assert result.report["evidence"]["local_showcase_smoke"]["status"] == "succeeded"
    assert result.report["capabilities_by_id"]["game_asset_3d_generation"][
        "status"
    ] == "blocked"
    assert result.report["capabilities_by_id"]["ai_agent_npc"]["status"] == "blocked"
    assert result.report["capabilities_by_id"]["print_fulfillment"][
        "status"
    ] == "blocked"
    provider_handoff = result.report["capabilities_by_id"]["provider_key_handoff"]
    assert result.report["evidence"]["final_resource_apply_preview"]["kind"] == (
        "final_resource_apply_preview_report"
    )
    assert result.report["evidence"]["final_resource_apply_preview"]["status"] == "missing"
    assert provider_handoff["command"] == "make final-resource-apply-preview"
    assert "final_resource_apply_preview:missing" in provider_handoff["evidence"]
    assert any(
        action == "make final-resource-apply-preview"
        for action in result.report["operator_actions"]
    )
    assert result.report["first_blocker"]["id"] == "ios_deployable"
    assert result.report["next_action"] == {
        "id": "ios_deployable",
        "label": "iOS deployable",
        "status": "blocked",
        "classification": "ios_rehearsal_missing",
        "command": "make ios-device-launch-rehearsal",
        "detail": "iOS deploy runbook and device launch rehearsal must both be ready.",
        "source": "first_blocker",
    }
    assert "make final-rehearsal-local" in result.report["commands"]
    assert "make final-showcase-readiness" in result.report["commands"]
    assert result.report["safety"]["commands_run"] is False
    assert result.report["safety"]["live_provider_calls"] is False


def test_final_showcase_readiness_includes_ios_device_action_bundle(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )

    bundle = result.report["device_action_bundle"]
    assert bundle["id"] == "ios_device_manual_actions"
    assert bundle["label"] == "iOS Device Manual Actions"
    assert bundle["status"] == "blocked"
    assert bundle["summary"]["actions"] >= 4
    assert bundle["summary"]["manual"] == bundle["summary"]["actions"]
    assert bundle["summary"]["blocked"] >= 1
    assert bundle["summary"]["xcode_or_signing"] == 1
    assert bundle["summary"]["global_actions"] == 0
    assert bundle["summary"]["provider_calls"] == 0
    assert bundle["first_action"]["id"] == "start_backend_device_demo"
    assert bundle["first_action"]["command"] == "make backend-device-demo"
    assert [action["id"] for action in bundle["actions"][:4]] == [
        "start_backend_device_demo",
        "run_mobile_deploy_preflight",
        "resolve_xcode_build_gate",
        "run_ios_device_launch_rehearsal",
    ]
    assert bundle["actions"][0]["blocks"] == [
        "ios_deployable",
        "functional_regression",
    ]
    assert bundle["actions"][2]["xcode_or_signing"] is True
    assert bundle["safety"]["commands_run"] is False
    assert bundle["safety"]["global_mutation"] is False
    assert bundle["safety"]["provider_calls"] is False


def test_final_showcase_readiness_maps_missing_mobile_deploy_preflight_evidence(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )

    evidence = result.report["evidence"]["mobile_deploy_preflight_evidence"]
    bundle = result.report["device_action_bundle"]
    actions = {action["id"]: action for action in bundle["actions"]}
    preflight = actions["run_mobile_deploy_preflight"]

    assert evidence["kind"] == "mobile_deploy_preflight_evidence_report"
    assert evidence["status"] == "missing"
    assert preflight["status"] == "blocked"
    assert preflight["evidence_status"] == "missing"
    assert preflight["evidence_source"] == (
        "services/backend/.local/mobile-deploy-preflight-evidence.json"
    )
    assert preflight["validation_command"] == "make mobile-deploy-preflight-evidence"


def test_final_showcase_readiness_marks_preflight_actions_ready_with_evidence(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_mobile_deploy_preflight_evidence_ready(repo_root)

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )

    bundle = result.report["device_action_bundle"]
    actions = {action["id"]: action for action in bundle["actions"]}

    assert result.exit_code == 2
    assert result.report["evidence"]["mobile_deploy_preflight_evidence"][
        "status"
    ] == "ready"
    assert actions["start_backend_device_demo"]["status"] == "ready"
    assert actions["start_backend_device_demo"]["evidence_status"] == "ready"
    assert actions["run_mobile_deploy_preflight"]["status"] == "ready"
    assert actions["run_mobile_deploy_preflight"]["evidence_status"] == "ready"
    assert actions["run_mobile_deploy_preflight"]["evidence_detail"] == (
        "iOS deploy preflight passed."
    )
    assert actions["resolve_xcode_build_gate"]["status"] == "blocked"
    assert bundle["first_action"]["id"] == "resolve_xcode_build_gate"
    assert bundle["summary"]["ready"] == 2
    assert bundle["summary"]["blocked"] == 2


def test_final_showcase_readiness_maps_missing_mobile_xcode_build_evidence(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )

    evidence = result.report["evidence"]["mobile_xcode_build_evidence"]
    actions = {
        action["id"]: action
        for action in result.report["device_action_bundle"]["actions"]
    }
    xcode = actions["resolve_xcode_build_gate"]

    assert evidence["kind"] == "mobile_xcode_build_evidence_report"
    assert evidence["status"] == "missing"
    assert xcode["status"] == "blocked"
    assert xcode["evidence_status"] == "missing"
    assert xcode["evidence_source"] == (
        "services/backend/.local/mobile-xcode-build-evidence.json"
    )
    assert xcode["validation_command"] == "make mobile-xcode-build-evidence"


def test_final_showcase_readiness_maps_blocked_mobile_xcode_build_evidence(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_mobile_xcode_build_evidence_blocked(repo_root)

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )

    actions = {
        action["id"]: action
        for action in result.report["device_action_bundle"]["actions"]
    }
    xcode = actions["resolve_xcode_build_gate"]

    assert result.report["evidence"]["mobile_xcode_build_evidence"][
        "status"
    ] == "blocked"
    assert xcode["status"] == "blocked"
    assert xcode["evidence_status"] == "blocked"
    assert xcode["evidence_detail"] == "Apple SDK license agreement is not accepted."
    assert xcode["validation_command"] == "make mobile-xcode-build-evidence"
    assert xcode["operator_actions"] == [
        "accept the Xcode license outside Codex, then rerun make mobile-xcode-build-evidence"
    ]


def test_final_showcase_readiness_marks_xcode_action_ready_with_evidence(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_mobile_deploy_preflight_evidence_ready(repo_root)
    _write_mobile_xcode_build_evidence_ready(repo_root)

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )

    bundle = result.report["device_action_bundle"]
    actions = {action["id"]: action for action in bundle["actions"]}

    assert actions["start_backend_device_demo"]["status"] == "ready"
    assert actions["run_mobile_deploy_preflight"]["status"] == "ready"
    assert actions["resolve_xcode_build_gate"]["status"] == "ready"
    assert actions["resolve_xcode_build_gate"]["evidence_status"] == "ready"
    assert actions["resolve_xcode_build_gate"]["evidence_detail"] == (
        "Xcode build gate passed with code signing disabled."
    )
    assert actions["run_ios_device_launch_rehearsal"]["status"] == "blocked"
    assert bundle["first_action"]["id"] == "run_ios_device_launch_rehearsal"
    assert bundle["summary"]["ready"] == 3
    assert bundle["summary"]["blocked"] == 1


def test_final_showcase_readiness_blocks_failed_local_showcase_smoke(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo_root = _write_deploy_config(tmp_path)

    def fake_local_smoke() -> LocalShowcaseSmokeResult:
        return LocalShowcaseSmokeResult(
            exit_code=1,
            report={
                "kind": "local_showcase_smoke_report",
                "status": "failed",
                "summary": {
                    "passed": 0,
                    "failed": 1,
                    "http_steps": 1,
                    "npc_ticks": 0,
                    "downloads": 0,
                },
                "steps": [
                    {
                        "id": "upload_guided_scan_capture",
                        "status": "failed",
                        "detail": "HTTP 500",
                    }
                ],
                "safety": {
                    "provider_calls": False,
                    "live_provider_calls": False,
                    "global_mutation": False,
                    "starts_server": False,
                    "writes_repo_local_media": False,
                    "uses_temporary_storage": True,
                    "provider_secrets_in_report": False,
                    "raw_media_in_report": False,
                    "local_paths_in_report": False,
                    "payment_links_in_report": False,
                },
            },
        )

    monkeypatch.setattr(
        "myth_forge_api.final_showcase_readiness.build_local_showcase_smoke_report",
        fake_local_smoke,
    )

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    local_smoke = result.report["capabilities_by_id"]["local_showcase_smoke"]

    assert result.exit_code == 2
    assert local_smoke["status"] == "blocked"
    assert local_smoke["classification"] == "local_showcase_smoke_failed"
    assert local_smoke["command"] == "make local-showcase-smoke"
    assert "local_showcase_smoke_report:failed" in local_smoke["evidence"]


def test_final_showcase_readiness_marks_local_proof_partial_until_live_and_device(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(
        tmp_path,
        local_config=(
            "DEVELOPMENT_TEAM = TEAM12345\n"
            "PRODUCT_BUNDLE_IDENTIFIER = com.zhexu.personalmythforge.dev\n"
            "PMF_BACKEND_BASE_URL = http://10.0.0.24:8080\n"
        ),
    )
    _write_capture_source_acceptance(repo_root)
    _write_final_resources(repo_root)
    _write_three_d_evaluation(repo_root)
    _write_npc_evaluation(repo_root)
    _write_visual_regression(repo_root)
    _write_final_acceptance_ready(repo_root)

    result = build_final_showcase_readiness_report(
        settings=Settings(
            three_d_provider="meshy",
            meshy_api_key="sk-meshy-test",
            npc_provider="openai",
            openai_api_key="sk-openai-test",
        ),
        repo_root=repo_root,
    )
    rows = result.report["capabilities_by_id"]

    assert result.exit_code == 2
    assert result.report["status"] == "partial"
    assert rows["ios_deployable"]["status"] == "partial"
    assert rows["capture_scanning"]["status"] == "ready"
    assert rows["game_asset_3d_generation"]["status"] == "partial"
    assert rows["ai_agent_npc"]["status"] == "partial"
    assert rows["print_fulfillment"]["status"] == "partial"
    assert rows["print_fulfillment"]["classification"] == "missing_configured_treatstock_quote"
    assert rows["provider_key_handoff"]["status"] == "partial"
    assert result.report["evidence"]["final_resource_apply_preview"]["status"] == "ready"
    assert "final_resource_apply_preview:ready" in rows["provider_key_handoff"]["evidence"]
    assert rows["provider_key_handoff"]["command"] == "make live-provider-evidence"
    assert rows["functional_regression"]["status"] == "ready"
    assert rows["visual_regression"]["status"] == "ready"
    assert result.report["first_blocker"]["id"] == "ios_deployable"
    assert any(
        "live provider evidence" in action
        for action in result.report["operator_actions"]
    )


def test_final_showcase_readiness_gates_provider_handoff_on_configured_bundle(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(
        tmp_path,
        local_config=(
            "DEVELOPMENT_TEAM = TEAM12345\n"
            "PRODUCT_BUNDLE_IDENTIFIER = com.zhexu.personalmythforge.dev\n"
            "PMF_BACKEND_BASE_URL = http://10.0.0.24:8080\n"
        ),
    )
    _write_capture_source_acceptance(repo_root)
    _write_final_resources(repo_root)
    _write_three_d_evaluation(repo_root)
    _write_npc_evaluation(repo_root)
    _write_visual_regression(repo_root)
    _write_final_acceptance_ready(repo_root)
    _write_live_provider_evidence_ready(repo_root)

    result = build_final_showcase_readiness_report(
        settings=Settings(
            three_d_provider="meshy",
            meshy_api_key="sk-meshy-test",
            npc_provider="openai",
            openai_api_key="sk-openai-test",
        ),
        repo_root=repo_root,
    )
    provider_handoff = result.report["capabilities_by_id"]["provider_key_handoff"]

    assert result.exit_code == 2
    assert provider_handoff["status"] == "partial"
    assert provider_handoff["classification"] == "configured_evidence_bundle_unproven"
    assert provider_handoff["command"] == "make configured-live-evidence-bundle"
    assert "configured_live_evidence_bundle:missing" in provider_handoff["evidence"]
    assert result.report["evidence"]["configured_live_evidence_bundle"]["status"] == "missing"
    assert any(
        "configured evidence bundle" in action
        for action in result.report["operator_actions"]
    )


def test_final_showcase_readiness_marks_provider_handoff_ready_with_configured_bundle(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(
        tmp_path,
        local_config=(
            "DEVELOPMENT_TEAM = TEAM12345\n"
            "PRODUCT_BUNDLE_IDENTIFIER = com.zhexu.personalmythforge.dev\n"
            "PMF_BACKEND_BASE_URL = http://10.0.0.24:8080\n"
        ),
    )
    _write_capture_source_acceptance(repo_root)
    _write_final_resources(repo_root)
    _write_three_d_evaluation(repo_root)
    _write_npc_evaluation(repo_root)
    _write_visual_regression(repo_root)
    _write_final_acceptance_ready(repo_root)
    _write_live_provider_evidence_ready(repo_root)
    _write_configured_live_evidence_bundle(repo_root, status="ready")

    result = build_final_showcase_readiness_report(
        settings=Settings(
            three_d_provider="meshy",
            meshy_api_key="sk-meshy-test",
            npc_provider="openai",
            openai_api_key="sk-openai-test",
        ),
        repo_root=repo_root,
    )
    provider_handoff = result.report["capabilities_by_id"]["provider_key_handoff"]

    assert provider_handoff["status"] == "ready"
    assert provider_handoff["classification"] == "provider_handoff_ready"
    assert "configured_live_evidence_bundle:ready" in provider_handoff["evidence"]
    assert result.report["evidence"]["configured_live_evidence_bundle"]["status"] == "ready"
    assert "make configured-live-evidence-bundle" in result.report["commands"]


def test_final_showcase_readiness_promotes_nested_operator_actions(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_capture_source_acceptance(repo_root)
    _write_three_d_evaluation(repo_root)
    _write_npc_evaluation(repo_root)
    _write_visual_regression_blocked(repo_root)
    _write_final_acceptance_blocked_with_actions(repo_root)
    _write_ios_device_launch_rehearsal_with_actions(repo_root)

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    actions = result.report["operator_actions"]

    assert result.exit_code == 2
    assert actions[0] == "final_rehearsal_local: final_acceptance_local: action 1"
    assert "final_handoff_index: run make final-configured-preflight" in actions
    assert "ios_device_launch_certificate: run make final-handoff-index" in actions
    assert (
        "run make live-provider-evidence after configured provider evidence files are refreshed"
        in actions
    )
    assert "make print-fulfillment-readiness" in actions
    assert "run make final-resource-init" in actions
    assert "provide iOS deploy config and rerun mobile deploy preflight" in actions
    assert "rerun make visual-regression-local and review failed artifacts" in actions
    assert "make final-showcase-readiness" in actions
    assert len(actions) <= 32
    assert actions.count("make print-fulfillment-readiness") == 1


def test_final_showcase_readiness_surfaces_final_resource_repair_action(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_final_resources(
        repo_root,
        bundle_identifier="com.example.personalmythforge",
        backend_base_url="http://192.168.1.10:8080",
    )

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )

    assert result.exit_code == 2
    assert result.report["evidence"]["final_resource_apply_preview"]["status"] == "blocked"
    assert "run make final-resource-repair" in result.report["operator_actions"]


def test_final_showcase_readiness_normalizes_legacy_final_resource_copy_action(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_capture_source_acceptance(repo_root)
    _write_three_d_evaluation(repo_root)
    _write_npc_evaluation(repo_root)
    _write_visual_regression_blocked(repo_root)
    _write_final_acceptance_blocked_with_actions(repo_root)
    _write_ios_device_launch_rehearsal_with_actions(
        repo_root,
        extra_actions=[
            (
                "final_rehearsal_local: ios_deploy_runbook_local: "
                "copy services/backend/final-resources.env.example to "
                "services/backend/.local/final-resources.env"
            ),
        ],
    )

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    actions = result.report["operator_actions"]
    report_text = json.dumps(result.report)

    assert result.exit_code == 2
    assert "run make final-resource-init" in actions
    assert "services/backend/final-resources.env.example" not in report_text
    assert "final_handoff_index: run make final-configured-preflight" in actions
    assert "ios_device_launch_certificate: run make final-handoff-index" in actions


def test_final_showcase_readiness_sanitizes_secrets_paths_and_private_context(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_final_acceptance_blocked_with_unsafe_detail(repo_root)

    result = build_final_showcase_readiness_report(
        settings=Settings(openai_api_key="sk-openai-secret"),
        repo_root=repo_root,
    )
    report_text = json.dumps(result.report)

    assert "sk-openai-secret" not in report_text
    assert str(tmp_path) not in report_text
    assert "private_message:" not in report_text
    assert "raw_context:" not in report_text
    assert "[redacted]" in report_text or "[home]" in report_text


def test_final_showcase_readiness_sanitizes_configured_bundle_detail(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    unsafe_detail = (
        "Authorization Bearer sk-provider /Users/zhexu/private "
        "file:///tmp/private.glb checkout_url"
    )
    _write_live_provider_evidence_ready(repo_root)
    _write_configured_live_evidence_bundle(
        repo_root,
        status="blocked",
        detail=unsafe_detail,
    )

    result = build_final_showcase_readiness_report(
        settings=Settings(
            three_d_provider="meshy",
            meshy_api_key="sk-meshy-test",
            npc_provider="openai",
            openai_api_key="sk-openai-test",
        ),
        repo_root=repo_root,
    )
    report_text = json.dumps(result.report)

    assert "sk-provider" not in report_text
    assert "sk-meshy-test" not in report_text
    assert "/Users/" not in report_text
    assert "file:///" not in report_text
    assert "checkout_url" not in report_text


def _write_deploy_config(tmp_path: Path, local_config: str | None = None) -> Path:
    repo_root = tmp_path / "repo"
    config_dir = repo_root / "apps/mobile/ios/Config"
    config_dir.mkdir(parents=True)
    (config_dir / "Deployment.xcconfig").write_text(
        "\n".join(
            [
                "PRODUCT_BUNDLE_IDENTIFIER = com.personalmythforge.app",
                "DEVELOPMENT_TEAM =",
                "CODE_SIGN_STYLE = Automatic",
                "PMF_BACKEND_BASE_URL = http://127.0.0.1:8080",
                '#include? "Deployment.local.xcconfig"',
            ]
        ),
        encoding="utf-8",
    )
    if local_config is not None:
        (config_dir / "Deployment.local.xcconfig").write_text(
            local_config,
            encoding="utf-8",
        )
    return repo_root


def _write_capture_source_acceptance(repo_root: Path) -> None:
    _write_text(
        repo_root / "apps/mobile/ios/App/CameraCaptureView.swift",
        "UIImagePickerController\njpegData(compressionQuality:\n",
    )
    _write_text(
        repo_root / "apps/mobile/ios/App/CaptureFormView.swift",
        "\n".join(
            [
                "Take Photo",
                "generationReadinessTitle",
                "generationReadinessRouteLabel",
                "generationReadinessDetail",
                "ThreeDGenerationInputReviewView(review: generationInputReview)",
            ]
        ),
    )
    _write_text(
        repo_root / "apps/mobile/ios/App/ForgeRootView.swift",
        "\n".join(
            [
                "CameraCaptureMediaBuilder.singlePhotoSelection",
                "GuidedScanPhotoSetBuilder.mediaDrafts",
                "arkitScanPackageSelection",
                "ARKitScanPackageBuilder.selection",
                "CaptureGenerationReadinessBuilder.build",
                "captureGenerationReadiness.route.displayLabel",
                "generationInputReview: threeDGenerationInputReview",
                "ThreeDGenerationInputReviewBuilder.build",
                "CaptureGenerationReceiptView(receipt: captureGenerationReceipt)",
                "capture: state.capture",
                "isPrintQuoteApproved",
                "PrintFulfillmentReceiptBuilder.build",
                "fulfillmentReceipt: printFulfillmentReceipt",
            ]
        ),
    )
    _write_text(
        repo_root / "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/CameraCaptureMediaBuilder.swift",
        "camera-capture.jpg",
    )
    _write_text(
        repo_root / "apps/mobile/ios/App/GuidedScanCaptureView.swift",
        "ObjectCaptureSession\nObjectCaptureView(session:",
    )
    _write_text(
        repo_root / "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ARKitScanPackageBuilder.swift",
        "\n".join(
            [
                "ARKitScanPackageBuilder",
                "maximumReferenceImages = 11",
                "CaptureMediaSelection(mode: .arkitScan",
            ]
        ),
    )
    _write_text(
        repo_root / "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/CaptureGenerationReadiness.swift",
        "\n".join(
            [
                "CaptureGenerationReadinessBuilder",
                "maximumProviderSourceImages = 4",
                "CaptureGenerationRoute",
                "displayLabel",
            ]
        ),
    )
    _write_text(
        repo_root / "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ThreeDGenerationInputReview.swift",
        "\n".join(
            [
                "ThreeDGenerationInputReviewBuilder",
                "provider images",
                "Raw capture files withheld.",
            ]
        ),
    )
    _write_text(
        repo_root / "apps/mobile/ios/App/ThreeDGenerationInputReviewView.swift",
        "3D Generation Input",
    )
    _write_text(
        repo_root / "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/CaptureGenerationReceipt.swift",
        "\n".join(
            [
                "CaptureGenerationReceiptBuilder",
                "Capture-to-3D proof missing",
                "raw sources",
                "Raw capture media withheld.",
            ]
        ),
    )
    _write_text(
        repo_root / "apps/mobile/ios/App/CaptureGenerationReceiptView.swift",
        "Capture-to-3D",
    )
    _write_text(
        repo_root / "apps/mobile/ios/PersonalMythForge.xcodeproj/project.pbxproj",
        "\n".join(
            [
                "ThreeDGenerationInputReviewView.swift",
                "CaptureGenerationReceiptView.swift",
                "PrintFulfillmentReceiptView.swift",
            ]
        ),
    )
    _write_text(
        repo_root / "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
        "\n".join(
            [
                "testARKitScanPackageBuilderBuildsReadySelection",
                "testCaptureGenerationReadinessMarksGuidedScanMultiImageRoute",
                "testCaptureGenerationReadinessMarksARKitScanAssetRoute",
                "testThreeDGenerationInputReviewShowsGuidedScanProviderSelection",
                "testThreeDGenerationInputReviewRedactsUnsafeText",
                "testCaptureGenerationReceiptShowsReadyGuidedScanGeneration",
                "testCaptureGenerationReceiptRedactsUnsafeText",
                "testPrintFulfillmentReceiptRequiresApprovalBeforeHandoff",
                "testPrintFulfillmentReceiptBlocksAndRedactsUnsafeText",
            ]
        ),
    )
    _write_text(
        repo_root / "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PrintFulfillmentReceipt.swift",
        "\n".join(
            [
                "PrintFulfillmentReceiptBuilder",
                "Checkout/payment links stay withheld",
                "canHandOffToProvider",
            ]
        ),
    )
    _write_text(
        repo_root / "apps/mobile/ios/App/PrintFulfillmentReceiptView.swift",
        "Print Fulfillment",
    )
    _write_text(
        repo_root / "apps/mobile/ios/App/PrintQuoteReviewView.swift",
        "PrintFulfillmentReceiptView(receipt: fulfillmentReceipt) Approve Print Handoff",
    )


def _write_final_resources(
    repo_root: Path,
    *,
    bundle_identifier: str = "com.zhexu.personalmythforge.dev",
    backend_base_url: str = "http://10.0.0.24:8080",
) -> None:
    _write_text(
        repo_root / "services/backend/.local/final-resources.env",
        "\n".join(
            [
                "MESHY_API_KEY=sk-meshy-test",
                "OPENAI_API_KEY=sk-openai-test",
                "PRINT_PROVIDER=local",
                "DEVELOPMENT_TEAM=TEAM12345",
                f"PRODUCT_BUNDLE_IDENTIFIER={bundle_identifier}",
                f"PMF_BACKEND_BASE_URL={backend_base_url}",
                "PMF_FINAL_LAUNCH_MODE=local",
            ]
        ),
    )


def _write_three_d_evaluation(repo_root: Path) -> None:
    _write_json(
        repo_root / "services/backend/.local/3d-evaluation-local.json",
        {
            "kind": "three_d_evaluation_report",
            "suite": "default-v0",
            "provider": "local",
            "total_cases": 20,
            "succeeded": 20,
            "failed": 0,
            "coverage": {
                "input_modes": {
                    "text_prompt": 20,
                    "single_image": 0,
                    "multi_image": 0,
                    "unknown": 0,
                },
                "variant_roles": {
                    "game_asset": 20,
                    "ios_scene_asset": 20,
                },
                "scene_loadable_cases": 20,
            },
            "cases": [],
        },
    )


def _write_npc_evaluation(repo_root: Path) -> None:
    _write_json(
        repo_root / "services/backend/.local/npc-evaluation-local.json",
        {
            "kind": "npc_agent_evaluation_report",
            "suite": "default-v0",
            "provider": "local",
            "tick_steps": 2,
            "total_cases": 6,
            "succeeded": 6,
            "failed": 0,
            "coverage": {
                "expected_npc_sets": 6,
                "trace_sets": 6,
                "proposed_action_plan_matches": 6,
                "tick_steps_completed": 12,
                "world_resolution_steps": 12,
            },
            "cases": [],
        },
    )


def _write_visual_regression(repo_root: Path) -> None:
    _write_json(
        repo_root / "services/backend/.local/visual-regression-local.json",
        {
            "kind": "visual_regression_report",
            "status": "passed",
            "summary": {"passed": 10, "failed": 0},
            "artifacts": [
                {
                    "id": "p0.119_visual_regression_handoff",
                    "status": "passed",
                },
                {
                    "id": "p0.101_print_fulfillment_receipt",
                    "status": "passed",
                }
            ],
        },
    )


def _write_visual_regression_blocked(repo_root: Path) -> None:
    _write_json(
        repo_root / "services/backend/.local/visual-regression-local.json",
        {
            "kind": "visual_regression_report",
            "status": "failed",
            "summary": {"passed": 9, "failed": 1},
            "artifacts": [
                {
                    "id": "p0.136_final_showcase_action_ledger",
                    "status": "failed",
                    "detail": "Action ledger visual evidence is stale.",
                }
            ],
        },
    )


def _write_final_acceptance_ready(repo_root: Path) -> None:
    _write_json(
        repo_root / "services/backend/.local/final-acceptance-local.json",
        {
            "kind": "final_acceptance_report",
            "overall_status": "passed",
            "summary": {"passed": 14, "blocked": 0, "failed": 0, "skipped": 0},
            "checks": [],
        },
    )


def _write_final_acceptance_blocked_with_actions(repo_root: Path) -> None:
    _write_json(
        repo_root / "services/backend/.local/final-acceptance-local.json",
        {
            "kind": "final_acceptance_report",
            "overall_status": "blocked",
            "summary": {"passed": 12, "blocked": 1, "failed": 0, "skipped": 0},
            "checks": [
                {
                    "id": "mobile_deploy_preflight",
                    "label": "Mobile deploy preflight",
                    "status": "blocked",
                    "classification": "blocked_by_local_ios_deploy_config",
                    "command": ["make", "mobile-deploy-preflight"],
                    "detail": "iOS deploy config is missing.",
                }
            ],
        },
    )


def _write_ios_device_launch_rehearsal_with_actions(
    repo_root: Path,
    *,
    extra_actions: list[str] | None = None,
) -> None:
    operator_actions = [
        "final_rehearsal_local: final_acceptance_local: action 1",
        "final_rehearsal_local: final_acceptance_local: action 2",
        "final_rehearsal_local: ios_deploy_runbook_local: action 1",
        "final_rehearsal_local: ios_deploy_runbook_local: action 2",
        "final_configured_preflight: action 1",
        "final_configured_preflight: action 2",
        "final_handoff_index: run make final-rehearsal-local",
        "final_handoff_index: run make final-configured-preflight",
        "ios_device_launch_certificate: run make final-handoff-index",
        "ios_device_launch_certificate: provide iOS deploy config",
    ]
    if extra_actions:
        operator_actions[2:2] = extra_actions
    _write_json(
        repo_root / "services/backend/.local/ios-device-launch-rehearsal.json",
        {
            "kind": "ios_device_launch_rehearsal_report",
            "status": "blocked",
            "summary": {
                "ready": 0,
                "missing": 0,
                "blocked": 1,
                "partial": 0,
                "manual": 0,
                "live": 0,
            },
            "sequence": [],
            "operator_actions": operator_actions,
            "commands": ["make ios-device-launch-rehearsal"],
            "safety": {
                "provider_calls": False,
                "live_provider_calls": False,
                "writes_backend_env": False,
                "writes_ios_deploy_config": False,
                "global_mutation": False,
                "xcode_or_signing": False,
                "keychain_writes": False,
                "provider_secrets_in_report": False,
                "raw_media_in_report": False,
                "payment_links_in_report": False,
                "local_paths_in_report": False,
            },
        },
    )


def _write_final_acceptance_blocked_with_unsafe_detail(repo_root: Path) -> None:
    _write_json(
        repo_root / "services/backend/.local/final-acceptance-local.json",
        {
            "kind": "final_acceptance_report",
            "overall_status": "blocked",
            "summary": {"passed": 12, "blocked": 1, "failed": 0, "skipped": 0},
            "checks": [
                {
                    "id": "private_context_guard",
                    "label": "Private context guard",
                    "status": "blocked",
                    "classification": "blocked_by_private_context",
                    "command": ["make", "final-acceptance-local"],
                    "stderr_tail": (
                        f"private_message: hello from {repo_root}/private "
                        "raw_context: bearer sk-openai-secret"
                    ),
                }
            ],
        },
    )


def _write_live_provider_evidence_ready(
    repo_root: Path,
    *,
    configured_launch_status: str = "ready",
    provider_detail: str = "Meshy and OpenAI providers are ready.",
) -> None:
    local_dir = repo_root / "services/backend/.local"
    _write_json(
        local_dir / "provider-handoff.json",
        {
            "kind": "provider_handoff_report",
            "core_real_ready": True,
            "missing_env": [],
            "detail": provider_detail,
        },
    )
    _write_json(
        local_dir / "3d-evaluation-configured.json",
        {
            "kind": "three_d_evaluation_report",
            "provider": "meshy",
            "succeeded": 20,
            "failed": 0,
        },
    )
    _write_json(
        local_dir / "npc-evaluation-configured.json",
        {
            "kind": "npc_agent_evaluation_report",
            "provider": "openai",
            "succeeded": 6,
            "failed": 0,
        },
    )
    _write_json(
        local_dir / "final-acceptance-configured.json",
        {
            "kind": "final_acceptance_report",
            "overall_status": "passed",
            "summary": {"passed": 14, "blocked": 0, "failed": 0, "skipped": 0},
        },
    )
    _write_json(
        local_dir / "final-demo-launch-configured.json",
        {
            "kind": "final_demo_launch_report",
            "mode": "configured",
            "overall_status": configured_launch_status,
        },
    )


def _write_configured_live_evidence_bundle(
    repo_root: Path,
    *,
    status: str,
    detail: str = "Configured evidence bundle is ready.",
) -> None:
    operator_actions = []
    current_blocker = None
    if status != "ready":
        operator_actions = [
            f"run make configured-live-evidence-bundle to refresh configured evidence bundle: {detail}"
        ]
        current_blocker = {
            "id": "configured_live_evidence_bundle",
            "label": "Configured live evidence bundle",
            "status": status,
            "command": "make configured-live-evidence-bundle",
            "detail": detail,
        }
    _write_json(
        repo_root / "services/backend/.local/configured-live-evidence-bundle.json",
        {
            "kind": "configured_live_evidence_bundle_report",
            "status": status,
            "summary": {
                "evidence_files": 5,
                "evidence_ready": 5 if status == "ready" else 4,
                "evidence_missing": 0,
                "evidence_blocked": 0 if status == "ready" else 1,
                "commands": 10,
                "commands_ready": 10 if status == "ready" else 9,
                "commands_run": 0,
            },
            "current_blocker": current_blocker,
            "operator_actions": operator_actions,
            "commands": ["make configured-live-evidence-bundle"],
            "safety": {
                "commands_run": False,
                "provider_calls": False,
                "live_provider_calls": False,
                "writes_backend_env": False,
                "writes_ios_deploy_config": False,
                "global_mutation": False,
                "xcode_or_signing": False,
                "keychain_writes": False,
                "provider_secrets_in_report": False,
                "raw_private_context_in_report": False,
                "raw_media_in_report": False,
                "payment_links_in_report": False,
                "local_paths_in_report": False,
            },
        },
    )


def _write_mobile_deploy_preflight_evidence_ready(repo_root: Path) -> None:
    _write_json(
        repo_root / "services/backend/.local/mobile-deploy-preflight-evidence.json",
        {
            "kind": "mobile_deploy_preflight_evidence_report",
            "status": "ready",
            "command": "make mobile-deploy-preflight",
            "script": "apps/mobile/ios/scripts/deploy_preflight.sh",
            "exit_code": 0,
            "checks": [
                {
                    "id": "deploy_preflight",
                    "label": "iOS deploy preflight",
                    "status": "ready",
                    "detail": "iOS deploy preflight passed.",
                },
                {
                    "id": "backend_health",
                    "label": "Backend health",
                    "status": "ready",
                    "detail": "Backend health: ok",
                },
            ],
            "stdout_lines": [
                "iOS deploy preflight passed.",
                "Backend health: ok",
            ],
            "stderr_lines": [],
            "operator_actions": [],
            "safety": {
                "commands_run": True,
                "provider_calls": False,
                "live_provider_calls": False,
                "writes_backend_env": False,
                "writes_ios_deploy_config": False,
                "global_mutation": False,
                "xcode_or_signing": False,
                "keychain_writes": False,
                "provider_secrets_in_report": False,
                "local_paths_in_report": False,
            },
        },
    )


def _write_mobile_xcode_build_evidence_blocked(repo_root: Path) -> None:
    _write_json(
        repo_root / "services/backend/.local/mobile-xcode-build-evidence.json",
        {
            "kind": "mobile_xcode_build_evidence_report",
            "status": "blocked",
            "classification": "blocked_by_apple_sdk_license",
            "command": "make mobile-xcode-build",
            "script": "apps/mobile/ios/scripts/xcode_build_gate.sh",
            "exit_code": 69,
            "checks": [
                {
                    "id": "xcode_license",
                    "label": "Xcode license",
                    "status": "blocked",
                    "detail": "Apple SDK license agreement is not accepted.",
                }
            ],
            "stdout_lines": [],
            "stderr_lines": [
                "Apple SDK license agreement is not accepted.",
            ],
            "operator_actions": [
                "accept the Xcode license outside Codex, then rerun make mobile-xcode-build-evidence"
            ],
            "safety": {
                "commands_run": True,
                "provider_calls": False,
                "live_provider_calls": False,
                "writes_backend_env": False,
                "writes_ios_deploy_config": False,
                "global_mutation": False,
                "xcode_or_signing": True,
                "code_signing_allowed": False,
                "keychain_writes": False,
                "provider_secrets_in_report": False,
                "local_paths_in_report": False,
                "writes_derived_data": True,
                "derived_data_path": "apps/mobile/ios/.build/xcode-derived-data",
            },
        },
    )


def _write_mobile_xcode_build_evidence_ready(repo_root: Path) -> None:
    _write_json(
        repo_root / "services/backend/.local/mobile-xcode-build-evidence.json",
        {
            "kind": "mobile_xcode_build_evidence_report",
            "status": "ready",
            "classification": "ready",
            "command": "make mobile-xcode-build",
            "script": "apps/mobile/ios/scripts/xcode_build_gate.sh",
            "exit_code": 0,
            "checks": [
                {
                    "id": "xcode_build_gate",
                    "label": "Xcode build gate",
                    "status": "ready",
                    "detail": "Xcode build gate passed with code signing disabled.",
                }
            ],
            "stdout_lines": [
                "Xcode build gate passed with code signing disabled.",
            ],
            "stderr_lines": [],
            "operator_actions": [],
            "safety": {
                "commands_run": True,
                "provider_calls": False,
                "live_provider_calls": False,
                "writes_backend_env": False,
                "writes_ios_deploy_config": False,
                "global_mutation": False,
                "xcode_or_signing": True,
                "code_signing_allowed": False,
                "keychain_writes": False,
                "provider_secrets_in_report": False,
                "local_paths_in_report": False,
                "writes_derived_data": True,
                "derived_data_path": "apps/mobile/ios/.build/xcode-derived-data",
            },
        },
    )


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_json(path: Path, payload: dict[str, object]) -> None:
    import json

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
