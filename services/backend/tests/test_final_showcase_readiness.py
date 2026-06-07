import json
from pathlib import Path

from myth_forge_api.config import Settings
from myth_forge_api.final_showcase_readiness import (
    build_final_showcase_readiness_report,
)


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
    assert "make final-rehearsal-local" in result.report["commands"]
    assert "make final-showcase-readiness" in result.report["commands"]
    assert result.report["safety"]["commands_run"] is False
    assert result.report["safety"]["live_provider_calls"] is False


def test_final_showcase_readiness_marks_local_proof_partial_until_live_and_device(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(
        tmp_path,
        local_config=(
            "DEVELOPMENT_TEAM = TEAM12345\n"
            "PRODUCT_BUNDLE_IDENTIFIER = com.example.personalmythforge\n"
            "PMF_BACKEND_BASE_URL = http://192.168.1.10:8080\n"
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
    assert (
        "copy services/backend/final-resources.env.example to "
        "services/backend/.local/final-resources.env"
    ) in actions
    assert "provide iOS deploy config and rerun mobile deploy preflight" in actions
    assert "rerun make visual-regression-local and review failed artifacts" in actions
    assert "make final-showcase-readiness" in actions
    assert len(actions) <= 32
    assert actions.count("make print-fulfillment-readiness") == 1


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


def _write_final_resources(repo_root: Path) -> None:
    _write_text(
        repo_root / "services/backend/.local/final-resources.env",
        "\n".join(
            [
                "MESHY_API_KEY=sk-meshy-test",
                "OPENAI_API_KEY=sk-openai-test",
                "PRINT_PROVIDER=local",
                "DEVELOPMENT_TEAM=TEAM12345",
                "PRODUCT_BUNDLE_IDENTIFIER=com.example.personalmythforge",
                "PMF_BACKEND_BASE_URL=http://192.168.1.10:8080",
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


def _write_ios_device_launch_rehearsal_with_actions(repo_root: Path) -> None:
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
            "operator_actions": [
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
            ],
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


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_json(path: Path, payload: dict[str, object]) -> None:
    import json

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
