import json
from pathlib import Path

from myth_forge_api.ios_showcase_acceptance import run_ios_showcase_acceptance


def test_ios_showcase_acceptance_passes_complete_fixture(tmp_path) -> None:
    write_complete_ios_showcase_fixture(tmp_path)

    result = run_ios_showcase_acceptance(repo_root=tmp_path)

    assert result.exit_code == 0
    assert result.report["kind"] == "ios_showcase_acceptance_report"
    assert result.report["status"] == "succeeded"
    assert result.report["summary"] == {"passed": 13, "failed": 0}
    assert [item["id"] for item in result.report["required_features"]] == [
        "camera_capture",
        "guided_scan",
        "capture_upload",
        "three_d_preview",
        "npc_ritual_scene",
        "npc_agent",
        "print_quote",
        "provider_readiness",
        "final_showcase",
        "device_preflight",
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
    assert result.report["summary"] == {"passed": 12, "failed": 1}
    assert features["camera_capture"]["status"] == "failed"
    assert {
        "file": "apps/mobile/ios/App/CameraCaptureView.swift",
        "contains": "UIImagePickerController",
    } in features["camera_capture"]["missing"]
    assert str(tmp_path) not in report_text
    assert "/Users/" not in report_text
    assert "sk-" not in report_text
    assert "data:image" not in report_text


def write_complete_ios_showcase_fixture(root: Path) -> None:
    files = {
        "apps/mobile/ios/App/CameraCaptureView.swift": (
            "UIImagePickerController jpegData(compressionQuality:"
        ),
        "apps/mobile/ios/App/CaptureFormView.swift": "Take Photo",
        "apps/mobile/ios/App/ForgeRootView.swift": (
            "CameraCaptureMediaBuilder.singlePhotoSelection "
            "GuidedScanPhotoSetBuilder.mediaDrafts getProviderReadiness "
            "runMythSessionAutonomy createPrintQuote FinalShowcaseSummaryBuilder "
            "DevicePreflightSummaryBuilder.build DevicePreflightView(summary: "
            "DemoScriptBuilder.build ArtifactSummaryView(session: readySession, latestTick: latestNPCTick) "
            "ShowcaseAutopilotPlanner.plan runShowcaseAutopilot"
        ),
        "apps/mobile/ios/App/GuidedScanCaptureView.swift": (
            "ObjectCaptureSession ObjectCaptureView(session:"
        ),
        "apps/mobile/ios/App/ArtifactSummaryView.swift": (
            "Artifact3DPreviewView(session: session, latestTick: latestTick)"
        ),
        "apps/mobile/ios/App/Artifact3DPreviewView.swift": (
            "ArtifactAssetPreparer.live() NPCRitualSceneBuilder.build addNPCRitualOverlay"
        ),
        "apps/mobile/ios/App/NPCTickView.swift": "Run Autonomy",
        "apps/mobile/ios/App/PrintQuoteReviewView.swift": "Get Quote",
        "apps/mobile/ios/App/ProviderReadinessView.swift": "missingEnv",
        "apps/mobile/ios/App/FinalShowcaseSummaryView.swift": "Final Showcase",
        "apps/mobile/ios/App/DevicePreflightView.swift": "Device Preflight backendBaseURL",
        "apps/mobile/ios/App/DemoScriptView.swift": (
            "Demo Script ShowcaseAutopilotPlan Button(action: runAutopilot)"
        ),
        "apps/mobile/ios/App/Info.plist": "NSCameraUsageDescription $(PMF_BACKEND_BASE_URL)",
        "apps/mobile/ios/Config/Deployment.xcconfig": "PMF_BACKEND_BASE_URL",
        "apps/mobile/ios/Config/Deployment.local.xcconfig.example": "PMF_BACKEND_BASE_URL",
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/CameraCaptureMediaBuilder.swift": (
            "camera-capture.jpg"
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ForgeFlowService.swift": (
            "uploadObjectCapture createMythSessionFromCapture"
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ArtifactAssetPreparation.swift": (
            "ArtifactAssetPreparer ios_scene_asset"
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/NPCRitualScene.swift": (
            "NPCRitualSceneBuilder"
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/DemoScript.swift": (
            "DemoScriptBuilder"
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ShowcaseAutopilot.swift": (
            "ShowcaseAutopilotPlanner"
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/DevicePreflight.swift": (
            "DevicePreflightSummaryBuilder"
        ),
        "apps/mobile/ios/PersonalMythForge.xcodeproj/project.pbxproj": (
            "CameraCaptureView.swift GuidedScanCaptureView.swift Artifact3DPreviewView.swift "
            "NPCTickView.swift PrintQuoteReviewView.swift ProviderReadinessView.swift "
            "FinalShowcaseSummaryView.swift DevicePreflightView.swift DemoScriptView.swift"
        ),
    }
    for relative_path, contents in files.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding="utf-8")
