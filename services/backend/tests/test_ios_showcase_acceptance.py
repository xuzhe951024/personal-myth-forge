import json
from pathlib import Path

from myth_forge_api.ios_showcase_acceptance import run_ios_showcase_acceptance


def test_ios_showcase_acceptance_passes_complete_fixture(tmp_path) -> None:
    write_complete_ios_showcase_fixture(tmp_path)

    result = run_ios_showcase_acceptance(repo_root=tmp_path)

    assert result.exit_code == 0
    assert result.report["kind"] == "ios_showcase_acceptance_report"
    assert result.report["status"] == "succeeded"
    assert result.report["summary"] == {"passed": 32, "failed": 0}
    assert [item["id"] for item in result.report["required_features"]] == [
        "camera_capture",
        "guided_scan",
        "arkit_scan_package",
        "capture_generation_readiness",
        "mobile_3d_generation_input_review",
        "capture_generation_receipt",
        "forge_progress_receipt",
        "mobile_generation_result_receipt",
        "live_provider_consent_interface",
        "capture_upload",
        "context_capsule_review",
        "mobile_forge_readiness_summary",
        "three_d_preview",
        "mobile_artifact_actions",
        "npc_ritual_scene",
        "npc_agent",
        "mobile_npc_agent_mode",
        "mobile_npc_agent_tick_summary",
        "print_quote",
        "mobile_print_fulfillment_receipt",
        "provider_readiness",
        "final_showcase",
        "mobile_final_acceptance_readiness",
        "mobile_3d_evaluation_readiness",
        "ios_deploy_runbook",
        "mobile_final_operator_handoff",
        "mobile_final_launch_mode",
        "device_preflight",
        "backend_health_probe",
        "demo_script",
        "showcase_autopilot",
        "deploy_config",
    ]
    assert all(item["status"] == "passed" for item in result.report["required_features"])
    assert result.report["safety"] == {
        "global_mutation": False,
        "runs_xcode": False,
        "runs_swiftpm": False,
        "provider_secrets_in_report": False,
        "raw_media_in_report": False,
        "absolute_paths_in_report": False,
    }


def test_ios_showcase_acceptance_fails_missing_camera_without_absolute_paths(tmp_path) -> None:
    write_complete_ios_showcase_fixture(tmp_path)
    (tmp_path / "apps/mobile/ios/App/CameraCaptureView.swift").unlink()

    result = run_ios_showcase_acceptance(repo_root=tmp_path)
    report_text = json.dumps(result.report)
    features = {item["id"]: item for item in result.report["required_features"]}

    assert result.exit_code == 1
    assert result.report["status"] == "failed"
    assert result.report["summary"] == {"passed": 31, "failed": 1}
    assert features["camera_capture"]["status"] == "failed"
    assert {
        "file": "apps/mobile/ios/App/CameraCaptureView.swift",
        "contains": "UIImagePickerController",
    } in features["camera_capture"]["missing"]
    assert str(tmp_path) not in report_text
    assert "/Users/" not in report_text
    assert "sk-" not in report_text
    assert "data:image" not in report_text


def test_ios_showcase_acceptance_fails_missing_arkit_scan_package_without_absolute_paths(
    tmp_path,
) -> None:
    write_complete_ios_showcase_fixture(tmp_path)
    (
        tmp_path
        / "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ARKitScanPackageBuilder.swift"
    ).unlink()

    result = run_ios_showcase_acceptance(repo_root=tmp_path)
    report_text = json.dumps(result.report)
    features = {item["id"]: item for item in result.report["required_features"]}

    assert result.exit_code == 1
    assert result.report["status"] == "failed"
    assert result.report["summary"] == {"passed": 31, "failed": 1}
    assert features["arkit_scan_package"]["status"] == "failed"
    assert {
        "file": "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ARKitScanPackageBuilder.swift",
        "contains": "ARKitScanPackageBuilder",
    } in features["arkit_scan_package"]["missing"]
    assert str(tmp_path) not in report_text
    assert "/Users/" not in report_text
    assert "sk-" not in report_text
    assert "data:image" not in report_text


def test_ios_showcase_acceptance_fails_missing_capture_generation_readiness_without_absolute_paths(
    tmp_path,
) -> None:
    write_complete_ios_showcase_fixture(tmp_path)
    (
        tmp_path
        / "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/CaptureGenerationReadiness.swift"
    ).unlink()

    result = run_ios_showcase_acceptance(repo_root=tmp_path)
    report_text = json.dumps(result.report)
    features = {item["id"]: item for item in result.report["required_features"]}

    assert result.exit_code == 1
    assert result.report["status"] == "failed"
    assert result.report["summary"] == {"passed": 31, "failed": 1}
    assert features["capture_generation_readiness"]["status"] == "failed"
    assert {
        "file": "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/CaptureGenerationReadiness.swift",
        "contains": "CaptureGenerationReadinessBuilder",
    } in features["capture_generation_readiness"]["missing"]
    assert str(tmp_path) not in report_text
    assert "/Users/" not in report_text
    assert "sk-" not in report_text
    assert "data:image" not in report_text


def test_ios_showcase_acceptance_fails_missing_3d_generation_input_review_without_absolute_paths(
    tmp_path,
) -> None:
    write_complete_ios_showcase_fixture(tmp_path)
    (
        tmp_path
        / "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ThreeDGenerationInputReview.swift"
    ).unlink()

    result = run_ios_showcase_acceptance(repo_root=tmp_path)
    report_text = json.dumps(result.report)
    features = {item["id"]: item for item in result.report["required_features"]}

    assert result.exit_code == 1
    assert result.report["status"] == "failed"
    assert result.report["summary"] == {"passed": 31, "failed": 1}
    assert features["mobile_3d_generation_input_review"]["status"] == "failed"
    assert {
        "file": "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ThreeDGenerationInputReview.swift",
        "contains": "ThreeDGenerationInputReviewBuilder",
    } in features["mobile_3d_generation_input_review"]["missing"]
    assert str(tmp_path) not in report_text
    assert "/Users/" not in report_text
    assert "sk-" not in report_text
    assert "data:image" not in report_text


def test_ios_showcase_acceptance_fails_missing_capture_generation_receipt_without_absolute_paths(
    tmp_path,
) -> None:
    write_complete_ios_showcase_fixture(tmp_path)
    (
        tmp_path
        / "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/CaptureGenerationReceipt.swift"
    ).unlink()

    result = run_ios_showcase_acceptance(repo_root=tmp_path)
    report_text = json.dumps(result.report)
    features = {item["id"]: item for item in result.report["required_features"]}

    assert result.exit_code == 1
    assert result.report["status"] == "failed"
    assert result.report["summary"] == {"passed": 31, "failed": 1}
    assert features["capture_generation_receipt"]["status"] == "failed"
    assert {
        "file": "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/CaptureGenerationReceipt.swift",
        "contains": "CaptureGenerationReceiptBuilder",
    } in features["capture_generation_receipt"]["missing"]
    assert str(tmp_path) not in report_text
    assert "/Users/" not in report_text
    assert "sk-" not in report_text
    assert "data:image" not in report_text


def test_ios_showcase_acceptance_fails_missing_forge_progress_receipt_without_absolute_paths(
    tmp_path,
) -> None:
    write_complete_ios_showcase_fixture(tmp_path)
    (
        tmp_path
        / "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ForgeProgressReceipt.swift"
    ).unlink()

    result = run_ios_showcase_acceptance(repo_root=tmp_path)
    report_text = json.dumps(result.report)
    features = {item["id"]: item for item in result.report["required_features"]}

    assert result.exit_code == 1
    assert result.report["status"] == "failed"
    assert result.report["summary"] == {"passed": 31, "failed": 1}
    assert features["forge_progress_receipt"]["status"] == "failed"
    assert {
        "file": "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ForgeProgressReceipt.swift",
        "contains": "ForgeProgressReceiptBuilder",
    } in features["forge_progress_receipt"]["missing"]
    assert str(tmp_path) not in report_text
    assert "/Users/" not in report_text
    assert "sk-" not in report_text
    assert "data:image" not in report_text


def test_ios_showcase_acceptance_fails_missing_generation_result_receipt_without_absolute_paths(
    tmp_path,
) -> None:
    write_complete_ios_showcase_fixture(tmp_path)
    (
        tmp_path
        / "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/GenerationResultReceipt.swift"
    ).unlink()

    result = run_ios_showcase_acceptance(repo_root=tmp_path)
    report_text = json.dumps(result.report)
    features = {item["id"]: item for item in result.report["required_features"]}

    assert result.exit_code == 1
    assert result.report["status"] == "failed"
    assert result.report["summary"] == {"passed": 31, "failed": 1}
    assert features["mobile_generation_result_receipt"]["status"] == "failed"
    assert {
        "file": "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/GenerationResultReceipt.swift",
        "contains": "GenerationResultReceiptBuilder",
    } in features["mobile_generation_result_receipt"]["missing"]
    assert str(tmp_path) not in report_text
    assert "/Users/" not in report_text
    assert "sk-" not in report_text
    assert "data:image" not in report_text


def test_ios_showcase_acceptance_fails_missing_live_provider_consent_without_absolute_paths(
    tmp_path,
) -> None:
    write_complete_ios_showcase_fixture(tmp_path)
    (
        tmp_path
        / "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/LiveProviderConsentSummary.swift"
    ).unlink()

    result = run_ios_showcase_acceptance(repo_root=tmp_path)
    report_text = json.dumps(result.report)
    features = {item["id"]: item for item in result.report["required_features"]}

    assert result.exit_code == 1
    assert result.report["status"] == "failed"
    assert result.report["summary"] == {"passed": 31, "failed": 1}
    assert features["live_provider_consent_interface"]["status"] == "failed"
    assert {
        "file": "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/LiveProviderConsentSummary.swift",
        "contains": "LiveProviderConsentSummaryBuilder",
    } in features["live_provider_consent_interface"]["missing"]
    assert str(tmp_path) not in report_text
    assert "/Users/" not in report_text
    assert "sk-" not in report_text
    assert "data:image" not in report_text


def test_ios_showcase_acceptance_fails_missing_print_fulfillment_receipt_without_absolute_paths(
    tmp_path,
) -> None:
    write_complete_ios_showcase_fixture(tmp_path)
    (
        tmp_path
        / "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PrintFulfillmentReceipt.swift"
    ).unlink()

    result = run_ios_showcase_acceptance(repo_root=tmp_path)
    report_text = json.dumps(result.report)
    features = {item["id"]: item for item in result.report["required_features"]}

    assert result.exit_code == 1
    assert result.report["status"] == "failed"
    assert result.report["summary"] == {"passed": 31, "failed": 1}
    assert features["mobile_print_fulfillment_receipt"]["status"] == "failed"
    assert {
        "file": "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PrintFulfillmentReceipt.swift",
        "contains": "PrintFulfillmentReceiptBuilder",
    } in features["mobile_print_fulfillment_receipt"]["missing"]
    assert str(tmp_path) not in report_text
    assert "/Users/" not in report_text
    assert "sk-" not in report_text
    assert "data:image" not in report_text


def test_ios_showcase_acceptance_fails_missing_local_network_usage_without_absolute_paths(
    tmp_path,
) -> None:
    write_complete_ios_showcase_fixture(tmp_path)
    plist_path = tmp_path / "apps/mobile/ios/App/Info.plist"
    plist_path.write_text(
        "NSCameraUsageDescription $(PMF_BACKEND_BASE_URL) "
        "PMFFinalLaunchMode $(PMF_FINAL_LAUNCH_MODE)",
        encoding="utf-8",
    )

    result = run_ios_showcase_acceptance(repo_root=tmp_path)
    report_text = json.dumps(result.report)
    features = {item["id"]: item for item in result.report["required_features"]}

    assert result.exit_code == 1
    assert result.report["status"] == "failed"
    assert result.report["summary"] == {"passed": 31, "failed": 1}
    assert features["deploy_config"]["status"] == "failed"
    assert {
        "file": "apps/mobile/ios/App/Info.plist",
        "contains": "NSLocalNetworkUsageDescription",
    } in features["deploy_config"]["missing"]
    assert str(tmp_path) not in report_text
    assert "/Users/" not in report_text
    assert "sk-" not in report_text
    assert "data:image" not in report_text


def test_ios_showcase_acceptance_fails_missing_3d_evaluation_readiness_without_absolute_paths(
    tmp_path,
) -> None:
    write_complete_ios_showcase_fixture(tmp_path)
    (
        tmp_path
        / "services/backend/src/myth_forge_api/three_d_evaluation_readiness.py"
    ).unlink()

    result = run_ios_showcase_acceptance(repo_root=tmp_path)
    report_text = json.dumps(result.report)
    features = {item["id"]: item for item in result.report["required_features"]}

    assert result.exit_code == 1
    assert result.report["status"] == "failed"
    assert result.report["summary"] == {"passed": 31, "failed": 1}
    assert features["mobile_3d_evaluation_readiness"]["status"] == "failed"
    assert {
        "file": "services/backend/src/myth_forge_api/three_d_evaluation_readiness.py",
        "contains": "build_three_d_evaluation_readiness_report",
    } in features["mobile_3d_evaluation_readiness"]["missing"]
    assert str(tmp_path) not in report_text
    assert "/Users/" not in report_text
    assert "sk-" not in report_text
    assert "data:image" not in report_text


def write_complete_ios_showcase_fixture(root: Path) -> None:
    files = {
        "apps/mobile/ios/App/CameraCaptureView.swift": (
            "UIImagePickerController jpegData(compressionQuality:"
        ),
        "apps/mobile/ios/App/CaptureFormView.swift": (
            "Take Photo generationReadinessTitle generationReadinessRouteLabel "
            "generationReadinessDetail ContextCapsuleReviewView( isContextCapsuleApproved "
            "Forge Readiness forgeReadinessSummary.routeLabel forgeReadinessSummary.privacyNotes "
            "forgeActionGate.isEnabled forgeActionGate.detail "
            "ThreeDGenerationInputReviewView(review: generationInputReview) "
            "ForgeProgressReceiptView(receipt: forgeProgressReceipt)"
        ),
        "apps/mobile/ios/App/CaptureGenerationReceiptView.swift": (
            "Capture-to-3D statusBadge receipt.privacyNotes"
        ),
        "apps/mobile/ios/App/ForgeProgressReceiptView.swift": (
            "Forge Progress statusBadge receipt.privacyNotes"
        ),
        "apps/mobile/ios/App/LiveProviderConsentView.swift": (
            "Live Provider Consent summary.consentFlag summary.privacyNotes"
        ),
        "apps/mobile/ios/App/PrintFulfillmentReceiptView.swift": (
            "Print Fulfillment receipt.privacyNotes"
        ),
        "apps/mobile/ios/App/ThreeDGenerationInputReviewView.swift": (
            "3D Generation Input review.routeLabel review.privacyNotes"
        ),
        "apps/mobile/ios/App/GenerationResultReceiptView.swift": (
            "3D Generation Result receipt.routeLabel receipt.privacyNotes"
        ),
        "apps/mobile/ios/App/ForgeRootView.swift": (
            "CameraCaptureMediaBuilder.singlePhotoSelection "
            "GuidedScanPhotoSetBuilder.mediaDrafts getProviderReadiness "
            "runMythSessionAutonomy createPrintQuote FinalShowcaseSummaryBuilder "
            "DevicePreflightSummaryBuilder.build DevicePreflightView(summary: "
            "getBackendHealth() checkBackendHealth backendHealthProbe "
            "DemoScriptBuilder.build ArtifactSummaryView(session: readySession, latestTick: latestNPCTick) "
            "finalLaunchSummary: finalLaunchMobileSummary "
            "ShowcaseAutopilotPlanner.plan runShowcaseAutopilot "
            "finalLaunchMode Picker(\"Final launch mode\" FinalLaunchMode.allCases "
            "loadFinalDemoLaunch(mode: finalLaunchMode) getFinalDemoLaunch(mode: mode.rawValue) "
            ".onChange(of: finalLaunchMode) "
            "arkitScanPackageSelection ARKitScanPackageBuilder.selection "
            "CaptureGenerationReadinessBuilder.build captureGenerationReadiness.route.displayLabel "
            "generationInputReview: threeDGenerationInputReview "
            "ThreeDGenerationInputReviewBuilder.build "
            "CaptureGenerationReceiptView(receipt: captureGenerationReceipt) capture: state.capture "
            "forgeProgressReceipt: forgeProgressReceipt ForgeProgressReceiptBuilder.build "
            "LiveProviderConsentView(summary: liveProviderConsentSummary) "
            "LiveProviderConsentSummaryBuilder.build "
            "isPrintQuoteApproved PrintFulfillmentReceiptBuilder.build "
            "fulfillmentReceipt: printFulfillmentReceipt "
            "ContextCapsuleReviewBuilder.build guard isContextCapsuleApproved else "
            "ForgeReadinessSummaryBuilder.build forgeReadinessSummary: forgeReadinessSummary "
            "ForgeActionGateBuilder.build forgeActionGate: forgeActionGate "
            "NPCAgentModeSummaryBuilder.build NPCAgentModeView(summary: "
            "NPCAgentTickSummaryBuilder.build summary: npcAgentTickSummary "
            "NPCAgentActionGateBuilder.build actionGate: npcAgentActionGate"
        ),
        "apps/mobile/ios/App/GuidedScanCaptureView.swift": (
            "ObjectCaptureSession ObjectCaptureView(session:"
        ),
        "apps/mobile/ios/App/ArtifactSummaryView.swift": (
            "Artifact3DPreviewView(session: session, latestTick: latestTick) "
            "GenerationResultReceiptBuilder.build(session: session) "
            "ArtifactGenerationProvenanceSummaryBuilder.build"
        ),
        "apps/mobile/ios/App/Artifact3DPreviewView.swift": (
            "ArtifactAssetPreparer.live() NPCRitualSceneBuilder.build addNPCRitualOverlay "
            "ArtifactHandoffActionsView("
        ),
        "apps/mobile/ios/App/ArtifactHandoffActionsView.swift": (
            "Artifact Handoff ShareLink Retry Download"
        ),
        "apps/mobile/ios/App/NPCTickView.swift": (
            "let summary: NPCAgentTickSummary summary.decisionLabel "
            "let actionGate: NPCAgentActionGate actionGate.canRunAutonomy "
            "actionGate.canAdvanceVillage actionGate.detail"
        ),
        "apps/mobile/ios/App/NPCAgentModeView.swift": (
            "NPC Agent Mode summary.missingEnv providerLabel"
        ),
        "apps/mobile/ios/App/PrintQuoteReviewView.swift": (
            "Get Quote PrintFulfillmentReceiptView(receipt: fulfillmentReceipt) "
            "Approve Print Handoff"
        ),
        "apps/mobile/ios/App/ProviderReadinessView.swift": "missingEnv",
        "apps/mobile/ios/App/FinalShowcaseSummaryView.swift": "Final Showcase",
        "apps/mobile/ios/App/FinalLaunchStatusView.swift": (
            "Mode Acceptance 3D Evaluation NPC Evaluation iOS Deploy Runbook Deploy Commands Deploy Safety "
            "Resource Handoff Backend Resources iOS Resources Next handoffRows Launch Receipt "
            "Resource Checklist"
        ),
        "apps/mobile/ios/App/DevicePreflightView.swift": (
            "Device Preflight backendBaseURL Check checkBackend"
        ),
        "apps/mobile/ios/App/ContextCapsuleReviewView.swift": (
            "Context Capsule Review Approve Capsule privacyNotes"
        ),
        "apps/mobile/ios/App/DemoScriptView.swift": (
            "Demo Script ShowcaseAutopilotPlan Button(action: runAutopilot)"
        ),
        "apps/mobile/ios/App/Info.plist": (
            "NSCameraUsageDescription NSLocalNetworkUsageDescription "
            "$(PMF_BACKEND_BASE_URL) PMFFinalLaunchMode $(PMF_FINAL_LAUNCH_MODE)"
        ),
        "apps/mobile/ios/Config/Deployment.xcconfig": (
            "PMF_BACKEND_BASE_URL PMF_FINAL_LAUNCH_MODE"
        ),
        "apps/mobile/ios/Config/Deployment.local.xcconfig.example": (
            "PMF_BACKEND_BASE_URL PMF_FINAL_LAUNCH_MODE"
        ),
        "apps/mobile/ios/App/AppConfiguration.swift": (
            "PMFFinalLaunchMode FinalLaunchMode.safe"
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/CameraCaptureMediaBuilder.swift": (
            "camera-capture.jpg"
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ARKitScanPackageBuilder.swift": (
            "ARKitScanPackageBuilder maximumReferenceImages = 11 "
            "CaptureMediaSelection(mode: .arkitScan"
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/CaptureGenerationReadiness.swift": (
            "CaptureGenerationReadinessBuilder maximumProviderSourceImages = 4 "
            "CaptureGenerationRoute displayLabel"
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ThreeDGenerationInputReview.swift": (
            "ThreeDGenerationInputReviewBuilder provider images "
            "Raw capture files withheld. canForge3D"
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/CaptureGenerationReceipt.swift": (
            "CaptureGenerationReceiptBuilder Capture-to-3D proof missing raw sources "
            "Raw capture media withheld."
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ForgeProgressReceipt.swift": (
            "ForgeProgressReceiptBuilder ForgeProgressReceiptRow "
            "Raw capture media stays off this receipt. sanitize"
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/GenerationResultReceipt.swift": (
            "GenerationResultReceiptBuilder Raw provider URIs and prompts withheld. "
            "scene-loadable iOS asset"
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/LiveProviderConsentSummary.swift": (
            "LiveProviderConsentSummaryBuilder canRunConfiguredAcceptance "
            "no live calls by default Provider keys remain backend-only. sanitize"
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PrintFulfillmentReceipt.swift": (
            "PrintFulfillmentReceiptBuilder Checkout/payment links stay withheld "
            "canHandOffToProvider"
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ContextCapsuleReview.swift": (
            "ContextCapsuleReviewBuilder"
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ForgeReadinessSummary.swift": (
            "ForgeReadinessSummaryBuilder routeLabel canForge ForgeActionGateBuilder disabledReason"
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalShowcaseSummary.swift": (
            "finalLaunchSummary: FinalLaunchMobileSummary? "
            "threeDEvaluationStage npcEvaluationStage operatorHandoffStage finalLaunchStage "
            '"three_d_evaluation" "npc_evaluation" "operator_handoff" "final_launch"'
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift": (
            "testARKitScanPackageBuilderBuildsReadySelection "
            "testCaptureGenerationReadinessMarksGuidedScanMultiImageRoute "
            "testCaptureGenerationReadinessMarksARKitScanAssetRoute "
            "testThreeDGenerationInputReviewWaitsForCaptureMedia "
            "testThreeDGenerationInputReviewShowsGuidedScanProviderSelection "
            "testThreeDGenerationInputReviewShowsARKitScanPackage "
            "testThreeDGenerationInputReviewShowsMeshyReadyRoute "
            "testThreeDGenerationInputReviewRedactsUnsafeText "
            "testCaptureGenerationReceiptShowsReadyGuidedScanGeneration "
            "testCaptureGenerationReceiptRedactsUnsafeText "
            "testForgeProgressReceiptShowsReadyProviderAndNPCRuntime "
            "testForgeProgressReceiptRedactsUnsafeFailure "
            "testGenerationResultReceiptShowsCompleteForgeResult "
            "testGenerationResultReceiptRedactsUnsafeText "
            "testLiveProviderConsentSummaryShowsReadyConfiguredConsent "
            "testLiveProviderConsentSummaryRedactsUnsafeText "
            "testPrintFulfillmentReceiptRequiresApprovalBeforeHandoff "
            "testPrintFulfillmentReceiptBlocksAndRedactsUnsafeText "
            "testContextCapsuleReviewMarksApprovedSummaryReady "
            "testForgeReadinessMarksLocalDemoReady "
            "testForgeActionGateEnablesLocalDemoForge "
            "testFinalShowcaseSummaryIncludesBlockedFinalLaunchDigest "
            "testFinalShowcaseSummaryIncludesReadyFinalLaunchDigest "
            "testFinalShowcaseSummaryIncludesReadyThreeDEvaluationDigest "
            "testFinalShowcaseSummaryWaitsForMissingThreeDEvaluationDigest "
            "testFinalShowcaseSummaryWaitsForMissingNPCEvaluationDigest "
            "testFinalShowcaseSummaryRedactsUnsafeThreeDEvaluationDigest "
            "testFinalShowcaseSummaryRedactsUnsafeFinalLaunchDigest "
            "testArtifactHandoffActionsOpenAndShareSceneAsset "
            "testArtifactGenerationProvenanceSummaryShowsScanAssets "
            "testDemoScriptShowsBlockedFinalLaunch "
            "testDemoScriptShowsReadyThreeDEvaluationBeforeNPCEvaluation "
            "testDemoScriptWaitsForMissingThreeDEvaluation "
            "testDemoScriptBlocksAndRedactsFailedThreeDEvaluation "
            "testDemoScriptShowsReadyNPCEvaluationBeforeFinalLaunch "
            "testDemoScriptWaitsForMissingNPCEvaluation "
            "testDemoScriptBlocksAndRedactsFailedNPCEvaluation "
            "testShowcaseAutopilotBlocksOnFinalLaunchBlocker "
            "testShowcaseAutopilotWaitsForMissingThreeDEvaluation "
            "testShowcaseAutopilotBlocksOnFailedThreeDEvaluation "
            "testShowcaseAutopilotWaitsForMissingNPCEvaluation "
            "testShowcaseAutopilotBlocksOnFailedNPCEvaluation "
            "testNPCAgentModeShowsOpenAIReadyRuntime "
            "testNPCAgentTickSummaryShowsLatestTickResolution "
            "testNPCAgentActionGateEnablesLocalDemoActions "
            "testFinalLaunchMobileSummaryShowsBlockedFinalAcceptance "
            "testFinalLaunchMobileSummaryShowsHandoffNextActions "
            "testFinalLaunchMobileSummaryShowsMissingResourceChecklist "
            "testFinalLaunchMobileSummaryShowsAcceptanceBlockerReceipt "
            "testFinalLaunchMobileSummaryShowsReadyConfiguredReceipt "
            "testDecodesFinalAcceptanceFreshnessFromFinalLaunchPayload "
            "testFinalLaunchMobileSummaryShowsStaleFinalAcceptanceFreshness "
            "testDecodesThreeDEvaluationReadinessFromFinalLaunchPayload "
            "testFinalLaunchMobileSummaryShowsReadyThreeDEvaluation "
            "testFinalLaunchMobileSummaryShowsBlockedThreeDEvaluation "
            "testDecodesNPCAgentEvaluationReadinessFromFinalLaunchPayload "
            "testFinalLaunchMobileSummaryShowsReadyNPCAgentEvaluation "
            "testFinalLaunchMobileSummaryShowsBlockedNPCAgentEvaluation "
            "testDecodesIOSDeployRunbookFromFinalLaunchPayload "
            "testFinalLaunchMobileSummaryShowsPartialIOSDeployRunbook "
            "testFinalLaunchMobileSummaryShowsThreeDEvaluationIOSDeployRunbookSlot "
            "testFinalLaunchMobileSummaryShowsBlockedIOSDeployRunbook "
            "testFinalLaunchMobileSummaryRedactsUnsafeIOSDeployRunbook "
            "testDecodesResourceHandoffFromFinalLaunchPayload "
            "testFinalLaunchMobileSummaryShowsMissingResourceHandoff "
            "testFinalLaunchMobileSummaryShowsReadyResourceHandoff "
            "testFinalLaunchMobileSummaryRedactsUnsafeResourceHandoff "
            "testFinalLaunchModeDefaultsToLocalForUnsafeValues "
            "testGetConfiguredFinalDemoLaunchBuildsGETRequest "
            "testFinalLaunchMobileSummaryShowsConfiguredModePolicy"
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ForgeFlowService.swift": (
            "uploadObjectCapture createMythSessionFromCapture"
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ArtifactAssetPreparation.swift": (
            "ArtifactAssetPreparer ios_scene_asset"
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ArtifactGenerationProvenanceSummary.swift": (
            "ArtifactGenerationProvenanceSummaryBuilder sourceAssetCount privacySummary"
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ArtifactHandoffActions.swift": (
            "ArtifactHandoffActionBuilder"
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/NPCRitualScene.swift": (
            "NPCRitualSceneBuilder"
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/NPCAgentModeSummary.swift": (
            "NPCAgentModeSummaryBuilder"
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/NPCAgentTickSummary.swift": (
            "NPCAgentTickSummaryBuilder decisionLabel privacyNotes "
            'NPCAgentActionGateBuilder canRunAutonomy disabledReason autonomyTitle: "Run Autonomy"'
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/DemoScript.swift": (
            "DemoScriptBuilder final_launch three_d_evaluation npc_evaluation "
            "threeDEvaluationStep npcEvaluationStep FinalLaunchMobileSummary"
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ShowcaseAutopilot.swift": (
            'ShowcaseAutopilotPlanner script.step(id: "final_launch") '
            'script.step(id: "three_d_evaluation") '
            'script.step(id: "npc_evaluation")'
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/DevicePreflight.swift": (
            "DevicePreflightSummaryBuilder BackendHealthProbe"
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift": (
            "FinalAcceptanceReadinessReport FinalOperatorHandoffReport finalOperatorHandoff "
            "FinalLaunchMode displayLabel FinalResourcesPreflightItem FinalAcceptanceFreshness "
            "ThreeDEvaluationReadinessReport threeDEvaluationReadiness "
            "NPCAgentEvaluationReadinessReport npcAgentEvaluationReadiness "
            "IOSDeployRunbookReport iosDeployRunbook "
            "ResourceHandoffReport resourceReport "
            "items: [FinalResourcesPreflightItem] freshness: FinalAcceptanceFreshness?"
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift": (
            "acceptanceRows handoffRows modePolicyRows liveCallPolicy resourceChecklistRows "
            "launchReceiptRows firstBlockerReceiptRow freshness.status == \"stale\" "
            "threeDEvaluationRows threeDEvaluationRows(from: "
            "npcEvaluationRows deployRunbookRows deployRunbookCommandRows deployRunbookSafetyRows "
            "resourceHandoffRows resourceHandoffBackendRows resourceHandoffIOSRows"
        ),
        "services/backend/src/myth_forge_api/final_acceptance_readiness.py": (
            "build_final_acceptance_readiness_report _freshness_report final_acceptance_freshness"
        ),
        "services/backend/src/myth_forge_api/npc_agent_evaluation_readiness.py": (
            "build_npc_agent_evaluation_readiness_report"
        ),
        "services/backend/src/myth_forge_api/three_d_evaluation_readiness.py": (
            "build_three_d_evaluation_readiness_report LOCAL_THREE_D_EVALUATION_COMMAND"
        ),
        "services/backend/src/myth_forge_api/ios_deploy_runbook.py": (
            "build_ios_deploy_runbook_report build_three_d_evaluation_readiness_report "
            "three_d_evaluation IOS_DEPLOY_RUNBOOK_COMMAND"
        ),
        "services/backend/src/myth_forge_api/cli.py": "ios-deploy-runbook",
        "Makefile": "ios-deploy-runbook:",
        "services/backend/src/myth_forge_api/final_operator_handoff.py": (
            "three_d_evaluation LOCAL_THREE_D_EVALUATION_COMMAND "
            "build_final_operator_handoff_report npc_agent_evaluation LOCAL_NPC_EVALUATION_COMMAND "
            "ios_deploy_runbook"
        ),
        "services/backend/src/myth_forge_api/final_demo_launch.py": (
            "final_acceptance_readiness three_d_evaluation_readiness npc_agent_evaluation_readiness "
            "final_operator_handoff three_d_evaluation_readiness=three_d_evaluation_readiness "
            "npc_agent_evaluation_readiness=npc_agent_evaluation_readiness ios_deploy_runbook"
        ),
        "services/backend/tests/test_final_demo_launch.py": (
            "test_final_demo_launch_embeds_three_d_evaluation_readiness "
            "test_final_demo_launch_operator_handoff_includes_three_d_evaluation_step "
            "test_final_demo_launch_operator_handoff_includes_npc_evaluation_step "
            "test_final_demo_launch_embeds_ios_deploy_runbook"
        ),
        "services/backend/tests/test_three_d_evaluation_readiness.py": (
            "test_three_d_evaluation_readiness_ready_report"
        ),
        "services/backend/tests/test_ios_deploy_runbook.py": (
            "test_ios_deploy_runbook_ready_local_inputs_preserve_command_order "
            "test_ios_deploy_runbook_blocks_and_redacts_failed_3d_evaluation"
        ),
        "services/backend/tests/test_final_operator_handoff.py": (
            "test_operator_handoff_includes_ios_deploy_runbook_before_deploy_preflight"
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PersonalMythForgeAPIClient.swift": (
            "getBackendHealth getFinalDemoLaunch"
        ),
        "apps/mobile/ios/PersonalMythForge.xcodeproj/project.pbxproj": (
            "CameraCaptureView.swift GuidedScanCaptureView.swift Artifact3DPreviewView.swift "
            "NPCTickView.swift PrintQuoteReviewView.swift ProviderReadinessView.swift "
            "FinalShowcaseSummaryView.swift DevicePreflightView.swift DemoScriptView.swift "
            "NPCAgentModeView.swift CaptureGenerationReceiptView.swift ForgeProgressReceiptView.swift "
            "LiveProviderConsentView.swift PrintFulfillmentReceiptView.swift "
            "ThreeDGenerationInputReviewView.swift GenerationResultReceiptView.swift"
        ),
    }
    for relative_path, contents in files.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding="utf-8")
