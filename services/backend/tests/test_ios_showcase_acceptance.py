import json
from pathlib import Path

from myth_forge_api.ios_showcase_acceptance import run_ios_showcase_acceptance


def test_ios_showcase_acceptance_passes_complete_fixture(tmp_path) -> None:
    write_complete_ios_showcase_fixture(tmp_path)

    result = run_ios_showcase_acceptance(repo_root=tmp_path)

    assert result.exit_code == 0
    assert result.report["kind"] == "ios_showcase_acceptance_report"
    assert result.report["status"] == "succeeded"
    assert result.report["summary"] == {"passed": 22, "failed": 0}
    assert [item["id"] for item in result.report["required_features"]] == [
        "camera_capture",
        "guided_scan",
        "arkit_scan_package",
        "capture_generation_readiness",
        "capture_upload",
        "context_capsule_review",
        "three_d_preview",
        "mobile_artifact_actions",
        "npc_ritual_scene",
        "npc_agent",
        "mobile_npc_agent_mode",
        "print_quote",
        "provider_readiness",
        "final_showcase",
        "mobile_final_acceptance_readiness",
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
    assert result.report["summary"] == {"passed": 21, "failed": 1}
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
    assert result.report["summary"] == {"passed": 21, "failed": 1}
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
    assert result.report["summary"] == {"passed": 21, "failed": 1}
    assert features["capture_generation_readiness"]["status"] == "failed"
    assert {
        "file": "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/CaptureGenerationReadiness.swift",
        "contains": "CaptureGenerationReadinessBuilder",
    } in features["capture_generation_readiness"]["missing"]
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
    assert result.report["summary"] == {"passed": 21, "failed": 1}
    assert features["deploy_config"]["status"] == "failed"
    assert {
        "file": "apps/mobile/ios/App/Info.plist",
        "contains": "NSLocalNetworkUsageDescription",
    } in features["deploy_config"]["missing"]
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
            "generationReadinessDetail ContextCapsuleReviewView( isContextCapsuleApproved"
        ),
        "apps/mobile/ios/App/ForgeRootView.swift": (
            "CameraCaptureMediaBuilder.singlePhotoSelection "
            "GuidedScanPhotoSetBuilder.mediaDrafts getProviderReadiness "
            "runMythSessionAutonomy createPrintQuote FinalShowcaseSummaryBuilder "
            "DevicePreflightSummaryBuilder.build DevicePreflightView(summary: "
            "getBackendHealth() checkBackendHealth backendHealthProbe "
            "DemoScriptBuilder.build ArtifactSummaryView(session: readySession, latestTick: latestNPCTick) "
            "ShowcaseAutopilotPlanner.plan runShowcaseAutopilot "
            "finalLaunchMode Picker(\"Final launch mode\" FinalLaunchMode.allCases "
            "loadFinalDemoLaunch(mode: finalLaunchMode) getFinalDemoLaunch(mode: mode.rawValue) "
            ".onChange(of: finalLaunchMode) "
            "arkitScanPackageSelection ARKitScanPackageBuilder.selection "
            "CaptureGenerationReadinessBuilder.build captureGenerationReadiness.route.displayLabel "
            "ContextCapsuleReviewBuilder.build guard isContextCapsuleApproved else "
            "NPCAgentModeSummaryBuilder.build NPCAgentModeView(summary:"
        ),
        "apps/mobile/ios/App/GuidedScanCaptureView.swift": (
            "ObjectCaptureSession ObjectCaptureView(session:"
        ),
        "apps/mobile/ios/App/ArtifactSummaryView.swift": (
            "Artifact3DPreviewView(session: session, latestTick: latestTick)"
        ),
        "apps/mobile/ios/App/Artifact3DPreviewView.swift": (
            "ArtifactAssetPreparer.live() NPCRitualSceneBuilder.build addNPCRitualOverlay "
            "ArtifactHandoffActionsView("
        ),
        "apps/mobile/ios/App/ArtifactHandoffActionsView.swift": (
            "Artifact Handoff ShareLink Retry Download"
        ),
        "apps/mobile/ios/App/NPCTickView.swift": "Run Autonomy",
        "apps/mobile/ios/App/NPCAgentModeView.swift": (
            "NPC Agent Mode summary.missingEnv providerLabel"
        ),
        "apps/mobile/ios/App/PrintQuoteReviewView.swift": "Get Quote",
        "apps/mobile/ios/App/ProviderReadinessView.swift": "missingEnv",
        "apps/mobile/ios/App/FinalShowcaseSummaryView.swift": "Final Showcase",
        "apps/mobile/ios/App/FinalLaunchStatusView.swift": "Mode Acceptance Next handoffRows",
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
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ContextCapsuleReview.swift": (
            "ContextCapsuleReviewBuilder"
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift": (
            "testARKitScanPackageBuilderBuildsReadySelection "
            "testCaptureGenerationReadinessMarksGuidedScanMultiImageRoute "
            "testCaptureGenerationReadinessMarksARKitScanAssetRoute "
            "testContextCapsuleReviewMarksApprovedSummaryReady "
            "testArtifactHandoffActionsOpenAndShareSceneAsset "
            "testNPCAgentModeShowsOpenAIReadyRuntime "
            "testFinalLaunchMobileSummaryShowsBlockedFinalAcceptance "
            "testFinalLaunchMobileSummaryShowsHandoffNextActions "
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
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ArtifactHandoffActions.swift": (
            "ArtifactHandoffActionBuilder"
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/NPCRitualScene.swift": (
            "NPCRitualSceneBuilder"
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/NPCAgentModeSummary.swift": (
            "NPCAgentModeSummaryBuilder"
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/DemoScript.swift": (
            "DemoScriptBuilder"
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ShowcaseAutopilot.swift": (
            "ShowcaseAutopilotPlanner"
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/DevicePreflight.swift": (
            "DevicePreflightSummaryBuilder BackendHealthProbe"
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift": (
            "FinalAcceptanceReadinessReport FinalOperatorHandoffReport finalOperatorHandoff "
            "FinalLaunchMode displayLabel"
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift": (
            "acceptanceRows handoffRows modePolicyRows liveCallPolicy"
        ),
        "services/backend/src/myth_forge_api/final_acceptance_readiness.py": (
            "build_final_acceptance_readiness_report"
        ),
        "services/backend/src/myth_forge_api/final_operator_handoff.py": (
            "build_final_operator_handoff_report"
        ),
        "services/backend/src/myth_forge_api/final_demo_launch.py": (
            "final_acceptance_readiness final_operator_handoff"
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PersonalMythForgeAPIClient.swift": (
            "getBackendHealth getFinalDemoLaunch"
        ),
        "apps/mobile/ios/PersonalMythForge.xcodeproj/project.pbxproj": (
            "CameraCaptureView.swift GuidedScanCaptureView.swift Artifact3DPreviewView.swift "
            "NPCTickView.swift PrintQuoteReviewView.swift ProviderReadinessView.swift "
            "FinalShowcaseSummaryView.swift DevicePreflightView.swift DemoScriptView.swift "
            "NPCAgentModeView.swift"
        ),
    }
    for relative_path, contents in files.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding="utf-8")
