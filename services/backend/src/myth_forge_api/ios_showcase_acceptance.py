from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SourceRequirement:
    file: str
    contains: str


@dataclass(frozen=True)
class FeatureRequirement:
    id: str
    label: str
    requirements: tuple[SourceRequirement, ...]


@dataclass(frozen=True)
class IOSShowcaseAcceptanceResult:
    exit_code: int
    report: dict[str, Any]


FEATURES = (
    FeatureRequirement(
        id="camera_capture",
        label="Camera capture",
        requirements=(
            SourceRequirement("apps/mobile/ios/App/CameraCaptureView.swift", "UIImagePickerController"),
            SourceRequirement("apps/mobile/ios/App/CameraCaptureView.swift", "jpegData(compressionQuality:"),
            SourceRequirement("apps/mobile/ios/App/CaptureFormView.swift", "Take Photo"),
            SourceRequirement(
                "apps/mobile/ios/App/ForgeRootView.swift",
                "CameraCaptureMediaBuilder.singlePhotoSelection",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/CameraCaptureMediaBuilder.swift",
                "camera-capture.jpg",
            ),
        ),
    ),
    FeatureRequirement(
        id="guided_scan",
        label="Guided scan",
        requirements=(
            SourceRequirement("apps/mobile/ios/App/GuidedScanCaptureView.swift", "ObjectCaptureSession"),
            SourceRequirement("apps/mobile/ios/App/GuidedScanCaptureView.swift", "ObjectCaptureView(session:"),
            SourceRequirement("apps/mobile/ios/App/ForgeRootView.swift", "GuidedScanPhotoSetBuilder.mediaDrafts"),
        ),
    ),
    FeatureRequirement(
        id="capture_upload",
        label="Capture upload",
        requirements=(
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ForgeFlowService.swift",
                "uploadObjectCapture",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ForgeFlowService.swift",
                "createMythSessionFromCapture",
            ),
        ),
    ),
    FeatureRequirement(
        id="three_d_preview",
        label="3D preview",
        requirements=(
            SourceRequirement("apps/mobile/ios/App/Artifact3DPreviewView.swift", "ArtifactAssetPreparer.live()"),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ArtifactAssetPreparation.swift",
                "ArtifactAssetPreparer",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ArtifactAssetPreparation.swift",
                "ios_scene_asset",
            ),
        ),
    ),
    FeatureRequirement(
        id="npc_ritual_scene",
        label="NPC ritual scene",
        requirements=(
            SourceRequirement("apps/mobile/ios/App/Artifact3DPreviewView.swift", "NPCRitualSceneBuilder.build"),
            SourceRequirement("apps/mobile/ios/App/Artifact3DPreviewView.swift", "addNPCRitualOverlay"),
            SourceRequirement(
                "apps/mobile/ios/App/ArtifactSummaryView.swift",
                "Artifact3DPreviewView(session: session, latestTick: latestTick)",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/ForgeRootView.swift",
                "ArtifactSummaryView(session: readySession, latestTick: latestNPCTick)",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/NPCRitualScene.swift",
                "NPCRitualSceneBuilder",
            ),
        ),
    ),
    FeatureRequirement(
        id="npc_agent",
        label="NPC agent",
        requirements=(
            SourceRequirement("apps/mobile/ios/App/NPCTickView.swift", "Run Autonomy"),
            SourceRequirement("apps/mobile/ios/App/ForgeRootView.swift", "runMythSessionAutonomy"),
        ),
    ),
    FeatureRequirement(
        id="print_quote",
        label="Print quote",
        requirements=(
            SourceRequirement("apps/mobile/ios/App/PrintQuoteReviewView.swift", "Get Quote"),
            SourceRequirement("apps/mobile/ios/App/ForgeRootView.swift", "createPrintQuote"),
        ),
    ),
    FeatureRequirement(
        id="provider_readiness",
        label="Provider readiness",
        requirements=(
            SourceRequirement("apps/mobile/ios/App/ProviderReadinessView.swift", "missingEnv"),
            SourceRequirement("apps/mobile/ios/App/ForgeRootView.swift", "getProviderReadiness"),
        ),
    ),
    FeatureRequirement(
        id="final_showcase",
        label="Final showcase",
        requirements=(
            SourceRequirement("apps/mobile/ios/App/FinalShowcaseSummaryView.swift", "Final Showcase"),
            SourceRequirement("apps/mobile/ios/App/ForgeRootView.swift", "FinalShowcaseSummaryBuilder"),
        ),
    ),
    FeatureRequirement(
        id="device_preflight",
        label="Device preflight",
        requirements=(
            SourceRequirement("apps/mobile/ios/App/DevicePreflightView.swift", "Device Preflight"),
            SourceRequirement("apps/mobile/ios/App/DevicePreflightView.swift", "backendBaseURL"),
            SourceRequirement("apps/mobile/ios/App/ForgeRootView.swift", "DevicePreflightSummaryBuilder.build"),
            SourceRequirement("apps/mobile/ios/App/ForgeRootView.swift", "DevicePreflightView(summary:"),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/DevicePreflight.swift",
                "DevicePreflightSummaryBuilder",
            ),
            SourceRequirement(
                "apps/mobile/ios/PersonalMythForge.xcodeproj/project.pbxproj",
                "DevicePreflightView.swift",
            ),
        ),
    ),
    FeatureRequirement(
        id="backend_health_probe",
        label="Backend health probe",
        requirements=(
            SourceRequirement("apps/mobile/ios/App/DevicePreflightView.swift", "Check"),
            SourceRequirement("apps/mobile/ios/App/DevicePreflightView.swift", "checkBackend"),
            SourceRequirement("apps/mobile/ios/App/ForgeRootView.swift", "getBackendHealth()"),
            SourceRequirement("apps/mobile/ios/App/ForgeRootView.swift", "checkBackendHealth"),
            SourceRequirement("apps/mobile/ios/App/ForgeRootView.swift", "backendHealthProbe"),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/DevicePreflight.swift",
                "BackendHealthProbe",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PersonalMythForgeAPIClient.swift",
                "getBackendHealth",
            ),
        ),
    ),
    FeatureRequirement(
        id="demo_script",
        label="Demo script",
        requirements=(
            SourceRequirement("apps/mobile/ios/App/DemoScriptView.swift", "Demo Script"),
            SourceRequirement("apps/mobile/ios/App/ForgeRootView.swift", "DemoScriptBuilder.build"),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/DemoScript.swift",
                "DemoScriptBuilder",
            ),
            SourceRequirement(
                "apps/mobile/ios/PersonalMythForge.xcodeproj/project.pbxproj",
                "DemoScriptView.swift",
            ),
        ),
    ),
    FeatureRequirement(
        id="showcase_autopilot",
        label="Showcase autopilot",
        requirements=(
            SourceRequirement("apps/mobile/ios/App/DemoScriptView.swift", "ShowcaseAutopilotPlan"),
            SourceRequirement("apps/mobile/ios/App/DemoScriptView.swift", "Button(action: runAutopilot)"),
            SourceRequirement("apps/mobile/ios/App/ForgeRootView.swift", "ShowcaseAutopilotPlanner.plan"),
            SourceRequirement("apps/mobile/ios/App/ForgeRootView.swift", "runShowcaseAutopilot"),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ShowcaseAutopilot.swift",
                "ShowcaseAutopilotPlanner",
            ),
        ),
    ),
    FeatureRequirement(
        id="deploy_config",
        label="Deploy config",
        requirements=(
            SourceRequirement("apps/mobile/ios/Config/Deployment.xcconfig", "PMF_BACKEND_BASE_URL"),
            SourceRequirement(
                "apps/mobile/ios/Config/Deployment.local.xcconfig.example",
                "PMF_BACKEND_BASE_URL",
            ),
            SourceRequirement("apps/mobile/ios/App/Info.plist", "NSCameraUsageDescription"),
            SourceRequirement("apps/mobile/ios/App/Info.plist", "$(PMF_BACKEND_BASE_URL)"),
        ),
    ),
)


def run_ios_showcase_acceptance(repo_root: str | Path | None = None) -> IOSShowcaseAcceptanceResult:
    root = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[4]
    required_features = [_evaluate_feature(root, feature) for feature in FEATURES]
    failed = sum(1 for feature in required_features if feature["status"] == "failed")
    passed = len(required_features) - failed
    status = "succeeded" if failed == 0 else "failed"
    report = {
        "kind": "ios_showcase_acceptance_report",
        "status": status,
        "required_features": required_features,
        "summary": {"passed": passed, "failed": failed},
        "safety": {
            "global_mutation": False,
            "runs_xcode": False,
            "runs_swiftpm": False,
            "provider_secrets_in_report": False,
            "raw_media_in_report": False,
            "absolute_paths_in_report": False,
        },
    }
    return IOSShowcaseAcceptanceResult(
        exit_code=0 if failed == 0 else 1,
        report=_sanitize_report(report),
    )


def _evaluate_feature(root: Path, feature: FeatureRequirement) -> dict[str, Any]:
    evidence: list[str] = []
    missing: list[dict[str, str]] = []
    for requirement in feature.requirements:
        if _contains(root / requirement.file, requirement.contains):
            evidence.append(f"{requirement.file}::{requirement.contains}")
        else:
            missing.append({"file": requirement.file, "contains": requirement.contains})
    return {
        "id": feature.id,
        "label": feature.label,
        "status": "passed" if not missing else "failed",
        "evidence": evidence,
        "missing": missing,
    }


def _contains(path: Path, expected: str) -> bool:
    try:
        return expected in path.read_text(encoding="utf-8")
    except OSError:
        return False


def _sanitize_report(report: dict[str, Any]) -> dict[str, Any]:
    text = json.dumps(report)
    if "/Users/" in text or "data:image" in text or "sk-" in text:
        raise ValueError("iOS showcase acceptance report contains unsafe text.")
    return report
