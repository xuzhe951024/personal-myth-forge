from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SourceRequirement:
    file: str
    contains: str
    all_contains: tuple[str, ...] = ()


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
        id="arkit_scan_package",
        label="ARKit scan package",
        requirements=(
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ARKitScanPackageBuilder.swift",
                "ARKitScanPackageBuilder",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ARKitScanPackageBuilder.swift",
                "maximumReferenceImages = 11",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ARKitScanPackageBuilder.swift",
                "CaptureMediaSelection(mode: .arkitScan",
            ),
            SourceRequirement("apps/mobile/ios/App/ForgeRootView.swift", "arkitScanPackageSelection"),
            SourceRequirement(
                "apps/mobile/ios/App/ForgeRootView.swift",
                "ARKitScanPackageBuilder.selection",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testARKitScanPackageBuilderBuildsReadySelection",
            ),
        ),
    ),
    FeatureRequirement(
        id="capture_generation_readiness",
        label="Capture generation readiness",
        requirements=(
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/CaptureGenerationReadiness.swift",
                "CaptureGenerationReadinessBuilder",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/CaptureGenerationReadiness.swift",
                "maximumProviderSourceImages = 4",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/CaptureGenerationReadiness.swift",
                "CaptureGenerationRoute",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/CaptureGenerationReadiness.swift",
                "displayLabel",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/ForgeRootView.swift",
                "CaptureGenerationReadinessBuilder.build",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/ForgeRootView.swift",
                "captureGenerationReadiness.route.displayLabel",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/CaptureFormView.swift",
                "generationReadinessTitle",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/CaptureFormView.swift",
                "generationReadinessRouteLabel",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/CaptureFormView.swift",
                "generationReadinessDetail",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testCaptureGenerationReadinessMarksGuidedScanMultiImageRoute",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testCaptureGenerationReadinessMarksARKitScanAssetRoute",
            ),
        ),
    ),
    FeatureRequirement(
        id="mobile_3d_generation_input_review",
        label="Mobile 3D generation input review",
        requirements=(
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ThreeDGenerationInputReview.swift",
                "ThreeDGenerationInputReviewBuilder",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ThreeDGenerationInputReview.swift",
                "provider images",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ThreeDGenerationInputReview.swift",
                "Raw capture files withheld.",
            ),
            SourceRequirement("apps/mobile/ios/App/ThreeDGenerationInputReviewView.swift", "3D Generation Input"),
            SourceRequirement(
                "apps/mobile/ios/App/CaptureFormView.swift",
                "ThreeDGenerationInputReviewView(review: generationInputReview)",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/ForgeRootView.swift",
                "generationInputReview: threeDGenerationInputReview",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/ForgeRootView.swift",
                "ThreeDGenerationInputReviewBuilder.build",
            ),
            SourceRequirement(
                "apps/mobile/ios/PersonalMythForge.xcodeproj/project.pbxproj",
                "ThreeDGenerationInputReviewView.swift",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testThreeDGenerationInputReviewShowsGuidedScanProviderSelection",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testThreeDGenerationInputReviewRedactsUnsafeText",
            ),
        ),
    ),
    FeatureRequirement(
        id="capture_generation_receipt",
        label="Capture generation receipt",
        requirements=(
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/CaptureGenerationReceipt.swift",
                "CaptureGenerationReceiptBuilder",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/CaptureGenerationReceipt.swift",
                "Capture-to-3D proof missing",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/CaptureGenerationReceipt.swift",
                "raw sources",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/CaptureGenerationReceipt.swift",
                "Raw capture media withheld.",
            ),
            SourceRequirement("apps/mobile/ios/App/CaptureGenerationReceiptView.swift", "Capture-to-3D"),
            SourceRequirement(
                "apps/mobile/ios/App/ForgeRootView.swift",
                "CaptureGenerationReceiptView(receipt: captureGenerationReceipt)",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/ForgeRootView.swift",
                "capture: state.capture",
            ),
            SourceRequirement(
                "apps/mobile/ios/PersonalMythForge.xcodeproj/project.pbxproj",
                "CaptureGenerationReceiptView.swift",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testCaptureGenerationReceiptShowsReadyGuidedScanGeneration",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testCaptureGenerationReceiptRedactsUnsafeText",
            ),
        ),
    ),
    FeatureRequirement(
        id="forge_progress_receipt",
        label="Forge progress receipt",
        requirements=(
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ForgeProgressReceipt.swift",
                "ForgeProgressReceiptBuilder",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ForgeProgressReceipt.swift",
                "ForgeProgressReceiptRow",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ForgeProgressReceipt.swift",
                "Raw capture media stays off this receipt.",
            ),
            SourceRequirement("apps/mobile/ios/App/ForgeProgressReceiptView.swift", "Forge Progress"),
            SourceRequirement(
                "apps/mobile/ios/App/CaptureFormView.swift",
                "ForgeProgressReceiptView(receipt: forgeProgressReceipt)",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/ForgeRootView.swift",
                "forgeProgressReceipt: forgeProgressReceipt",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/ForgeRootView.swift",
                "ForgeProgressReceiptBuilder.build",
            ),
            SourceRequirement(
                "apps/mobile/ios/PersonalMythForge.xcodeproj/project.pbxproj",
                "ForgeProgressReceiptView.swift",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testForgeProgressReceiptShowsReadyProviderAndNPCRuntime",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testForgeProgressReceiptRedactsUnsafeFailure",
            ),
        ),
    ),
    FeatureRequirement(
        id="mobile_generation_result_receipt",
        label="Mobile generation result receipt",
        requirements=(
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/GenerationResultReceipt.swift",
                "GenerationResultReceiptBuilder",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/GenerationResultReceipt.swift",
                "Raw provider URIs and prompts withheld.",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/GenerationResultReceipt.swift",
                "scene-loadable iOS asset",
            ),
            SourceRequirement("apps/mobile/ios/App/GenerationResultReceiptView.swift", "3D Generation Result"),
            SourceRequirement(
                "apps/mobile/ios/App/ArtifactSummaryView.swift",
                "GenerationResultReceiptBuilder.build(session: session)",
            ),
            SourceRequirement(
                "apps/mobile/ios/PersonalMythForge.xcodeproj/project.pbxproj",
                "GenerationResultReceiptView.swift",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testGenerationResultReceiptShowsCompleteForgeResult",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testGenerationResultReceiptRedactsUnsafeText",
            ),
        ),
    ),
    FeatureRequirement(
        id="live_provider_consent_interface",
        label="Live provider consent interface",
        requirements=(
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/LiveProviderConsentSummary.swift",
                "LiveProviderConsentSummaryBuilder",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/LiveProviderConsentSummary.swift",
                "canRunConfiguredAcceptance",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/LiveProviderConsentSummary.swift",
                "no live calls by default",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/LiveProviderConsentSummary.swift",
                "Provider keys remain backend-only.",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/LiveProviderConsentSummary.swift",
                "liveEvidenceRow",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/LiveProviderConsentSummary.swift",
                "configuredBundleRow",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/LiveProviderConsentSummary.swift",
                "liveProviderEvidence",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/LiveProviderConsentSummary.swift",
                "configuredLiveEvidenceBundle",
            ),
            SourceRequirement("apps/mobile/ios/App/LiveProviderConsentView.swift", "Live Provider Consent"),
            SourceRequirement(
                "apps/mobile/ios/App/LiveProviderConsentView.swift",
                "summary.consentFlag",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/ForgeRootView.swift",
                "LiveProviderConsentView(summary: liveProviderConsentSummary)",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/ForgeRootView.swift",
                "LiveProviderConsentSummaryBuilder.build",
            ),
            SourceRequirement(
                "apps/mobile/ios/PersonalMythForge.xcodeproj/project.pbxproj",
                "LiveProviderConsentView.swift",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testLiveProviderConsentSummaryShowsReadyConfiguredConsent",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testLiveProviderConsentSummaryRedactsUnsafeText",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testLiveProviderConsentSummaryShowsReadyLiveEvidence",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testLiveProviderConsentSummaryShowsConfiguredBundleRow",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testLiveProviderConsentSummaryBlocksConfiguredAcceptanceWithoutBundle",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testLiveProviderConsentSummaryBlocksMissingLiveEvidence",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testLiveProviderConsentSummaryRedactsUnsafeLiveEvidenceBlocker",
            ),
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
        id="context_capsule_review",
        label="Context capsule review",
        requirements=(
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ContextCapsuleReview.swift",
                "ContextCapsuleReviewBuilder",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/ContextCapsuleReviewView.swift",
                "Context Capsule Review",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/CaptureFormView.swift",
                "ContextCapsuleReviewView(",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/CaptureFormView.swift",
                "isContextCapsuleApproved",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/ForgeRootView.swift",
                "ContextCapsuleReviewBuilder.build",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/ForgeRootView.swift",
                "guard isContextCapsuleApproved else",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testContextCapsuleReviewMarksApprovedSummaryReady",
            ),
        ),
    ),
    FeatureRequirement(
        id="mobile_forge_readiness_summary",
        label="Mobile Forge readiness summary",
        requirements=(
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ForgeReadinessSummary.swift",
                "ForgeReadinessSummaryBuilder",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ForgeReadinessSummary.swift",
                "routeLabel",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ForgeReadinessSummary.swift",
                "canForge",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ForgeReadinessSummary.swift",
                "ForgeActionGateBuilder",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ForgeReadinessSummary.swift",
                "disabledReason",
            ),
            SourceRequirement("apps/mobile/ios/App/CaptureFormView.swift", "Forge Readiness"),
            SourceRequirement(
                "apps/mobile/ios/App/CaptureFormView.swift",
                "forgeReadinessSummary.routeLabel",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/CaptureFormView.swift",
                "forgeActionGate.isEnabled",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/CaptureFormView.swift",
                "forgeActionGate.detail",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/ForgeRootView.swift",
                "ForgeReadinessSummaryBuilder.build",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/ForgeRootView.swift",
                "forgeReadinessSummary: forgeReadinessSummary",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/ForgeRootView.swift",
                "ForgeActionGateBuilder.build",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/ForgeRootView.swift",
                "forgeActionGate: forgeActionGate",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testForgeReadinessMarksLocalDemoReady",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testForgeActionGateEnablesLocalDemoForge",
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
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ArtifactAssetPreparation.swift",
                "sceneLoadFailed",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ArtifactSceneLoadProof.swift",
                "ArtifactSceneLoadProofBuilder",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/Artifact3DPreviewView.swift",
                "SceneKit load proof",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ArtifactGenerationProvenanceSummary.swift",
                "ArtifactGenerationProvenanceSummaryBuilder",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ArtifactGenerationProvenanceSummary.swift",
                "sourceAssetCount",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ArtifactGenerationProvenanceSummary.swift",
                "privacySummary",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/ArtifactSummaryView.swift",
                "ArtifactGenerationProvenanceSummaryBuilder.build",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testArtifactGenerationProvenanceSummaryShowsScanAssets",
            ),
        ),
    ),
    FeatureRequirement(
        id="mobile_artifact_actions",
        label="Mobile artifact actions",
        requirements=(
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ArtifactHandoffActions.swift",
                "ArtifactHandoffActionBuilder",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/ArtifactHandoffActionsView.swift",
                "Artifact Handoff",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/ArtifactHandoffActionsView.swift",
                "ShareLink",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/Artifact3DPreviewView.swift",
                "ArtifactHandoffActionsView(",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testArtifactHandoffActionsOpenAndShareSceneAsset",
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
                "onSceneLoadProofChange: onSceneLoadProofChange",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/ForgeRootView.swift",
                "sceneLoadProof = proof",
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
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/NPCAgentTickSummary.swift",
                'autonomyTitle: "Run Autonomy"',
            ),
            SourceRequirement("apps/mobile/ios/App/ForgeRootView.swift", "runMythSessionAutonomy"),
        ),
    ),
    FeatureRequirement(
        id="mobile_npc_agent_mode",
        label="Mobile NPC agent mode",
        requirements=(
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/NPCAgentModeSummary.swift",
                "NPCAgentModeSummaryBuilder",
            ),
            SourceRequirement("apps/mobile/ios/App/NPCAgentModeView.swift", "NPC Agent Mode"),
            SourceRequirement(
                "apps/mobile/ios/App/ForgeRootView.swift",
                "NPCAgentModeSummaryBuilder.build",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testNPCAgentModeShowsOpenAIReadyRuntime",
            ),
        ),
    ),
    FeatureRequirement(
        id="mobile_npc_agent_tick_summary",
        label="Mobile NPC agent tick summary",
        requirements=(
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/NPCAgentTickSummary.swift",
                "NPCAgentTickSummaryBuilder",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/NPCAgentTickSummary.swift",
                "decisionLabel",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/NPCAgentTickSummary.swift",
                "privacyNotes",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/NPCAgentTickSummary.swift",
                "NPCAgentActionGateBuilder",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/NPCAgentTickSummary.swift",
                "canRunAutonomy",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/NPCAgentTickSummary.swift",
                "disabledReason",
            ),
            SourceRequirement("apps/mobile/ios/App/NPCTickView.swift", "let summary: NPCAgentTickSummary"),
            SourceRequirement("apps/mobile/ios/App/NPCTickView.swift", "let actionGate: NPCAgentActionGate"),
            SourceRequirement("apps/mobile/ios/App/NPCTickView.swift", "summary.decisionLabel"),
            SourceRequirement("apps/mobile/ios/App/NPCTickView.swift", "actionGate.canRunAutonomy"),
            SourceRequirement("apps/mobile/ios/App/NPCTickView.swift", "actionGate.canAdvanceVillage"),
            SourceRequirement("apps/mobile/ios/App/NPCTickView.swift", "actionGate.detail"),
            SourceRequirement(
                "apps/mobile/ios/App/ForgeRootView.swift",
                "NPCAgentTickSummaryBuilder.build",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/ForgeRootView.swift",
                "NPCAgentActionGateBuilder.build",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/ForgeRootView.swift",
                "summary: npcAgentTickSummary",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/ForgeRootView.swift",
                "actionGate: npcAgentActionGate",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testNPCAgentTickSummaryShowsLatestTickResolution",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testNPCAgentActionGateEnablesLocalDemoActions",
            ),
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
        id="mobile_print_fulfillment_receipt",
        label="Mobile print fulfillment receipt",
        requirements=(
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PrintFulfillmentReceipt.swift",
                "PrintFulfillmentReceiptBuilder",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PrintFulfillmentReceipt.swift",
                "Checkout/payment links stay withheld",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PrintFulfillmentReceipt.swift",
                "canHandOffToProvider",
            ),
            SourceRequirement("apps/mobile/ios/App/PrintFulfillmentReceiptView.swift", "Print Fulfillment"),
            SourceRequirement(
                "apps/mobile/ios/App/PrintQuoteReviewView.swift",
                "PrintFulfillmentReceiptView(receipt: fulfillmentReceipt)",
            ),
            SourceRequirement("apps/mobile/ios/App/PrintQuoteReviewView.swift", "Approve Print Handoff"),
            SourceRequirement("apps/mobile/ios/App/ForgeRootView.swift", "isPrintQuoteApproved"),
            SourceRequirement(
                "apps/mobile/ios/App/ForgeRootView.swift",
                "PrintFulfillmentReceiptBuilder.build",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/ForgeRootView.swift",
                "fulfillmentReceipt: printFulfillmentReceipt",
            ),
            SourceRequirement(
                "apps/mobile/ios/PersonalMythForge.xcodeproj/project.pbxproj",
                "PrintFulfillmentReceiptView.swift",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testPrintFulfillmentReceiptRequiresApprovalBeforeHandoff",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testPrintFulfillmentReceiptBlocksAndRedactsUnsafeText",
            ),
        ),
    ),
    FeatureRequirement(
        id="final_print_fulfillment_readiness",
        label="Final print fulfillment readiness",
        requirements=(
            SourceRequirement(
                "services/backend/src/myth_forge_api/print_fulfillment_readiness.py",
                "build_print_fulfillment_readiness_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/print_fulfillment_readiness.py",
                "print_fulfillment_readiness_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/print_fulfillment_readiness.py",
                "configured_treatstock_quote",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_demo_launch.py",
                "print_fulfillment_readiness",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_showcase_readiness.py",
                "print_fulfillment",
            ),
            SourceRequirement("services/backend/src/myth_forge_api/cli.py", "print-fulfillment-readiness"),
            SourceRequirement("Makefile", "print-fulfillment-readiness:"),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "PrintFulfillmentReadinessReport",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "printFulfillmentReadiness",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "printFulfillmentReadinessRows",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/FinalLaunchStatusView.swift",
                "Print Fulfillment",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testDecodesPrintFulfillmentReadinessFromFinalLaunchPayload",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryRedactsUnsafePrintFulfillmentReadiness",
            ),
        ),
    ),
    FeatureRequirement(
        id="final_resource_requirements_manifest",
        label="Final resource requirements manifest",
        requirements=(
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_resource_requirements.py",
                "build_final_resource_requirements_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_resource_requirements.py",
                "final_resource_requirements_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_resource_requirements.py",
                "first_blocker",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_resource_requirements.py",
                "next_action",
            ),
            SourceRequirement(
                "services/backend/scripts/init_final_resources.sh",
                "final-resources.env initialized",
            ),
            SourceRequirement(
                "services/backend/scripts/init_final_resources.sh",
                "make final-resource-init",
            ),
            SourceRequirement(
                "services/backend/scripts/init_final_resources.sh",
                "must stay untracked",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/cli.py",
                "final-resource-requirements",
            ),
            SourceRequirement("Makefile", "final-resource-init:"),
            SourceRequirement(
                "Makefile",
                "scripts/init_final_resources.sh",
            ),
            SourceRequirement("Makefile", "final-resource-requirements:"),
            SourceRequirement("Makefile", "write_resource_handoff.sh"),
            SourceRequirement("Makefile", "write_final_resources_preflight.sh"),
            SourceRequirement("Makefile", "write_final_resource_requirements.sh"),
            SourceRequirement(
                "services/backend/scripts/write_resource_handoff.sh",
                ".local/resource-handoff.json",
            ),
            SourceRequirement(
                "services/backend/scripts/write_resource_handoff.sh",
                "accepted resource handoff exit code",
            ),
            SourceRequirement(
                "services/backend/scripts/write_final_resources_preflight.sh",
                ".local/final-resources-preflight.json",
            ),
            SourceRequirement(
                "services/backend/scripts/write_final_resources_preflight.sh",
                "accepted final resources preflight exit code",
            ),
            SourceRequirement(
                "services/backend/scripts/write_final_resource_requirements.sh",
                ".local/final-resource-requirements.json",
            ),
            SourceRequirement(
                "services/backend/scripts/write_final_resource_requirements.sh",
                "accepted final resource requirements exit code",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_demo_launch.py",
                "final_resource_requirements",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_demo_launch.py",
                "final_resource_fill_guide",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_resource_fill_guide.py",
                "first_blocker",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "FinalResourceRequirementsReport",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "resolutionMode: String?",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "applyNote: String?",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "FinalResourceRequirementsNextAction",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "finalResourceRequirements",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "FinalResourceFillGuideReport",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "FinalResourceFillGuideFirstBlocker",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "firstBlocker: FinalResourceFillGuideFirstBlocker?",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "finalResourceFillGuide",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "resourceRequirementRows",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "appendApplyTimeDetail",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "Next input:",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "resourceFillGuideRows",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "resourceFillGuideFirstBlockerRow",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "Resource requirements",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "Fill guide",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/FinalLaunchStatusView.swift",
                "Resource Requirements",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/FinalLaunchStatusView.swift",
                "Resource Fill Guide",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testDecodesFinalResourceRequirementsFromFinalLaunchPayload",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryShowsBlockedResourceRequirements",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryShowsResourceRequirementsNextAction",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testDecodesFinalResourceAutoBackendURLHandoffFields",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryShowsAutoBackendURLHandoff",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "apply_time_auto",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "write_deploy_local_config.sh",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testDecodesFinalResourceFillGuideFromFinalLaunchPayload",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryShowsResourceFillGuide",
            ),
        ),
    ),
    FeatureRequirement(
        id="final_resource_apply_preview",
        label="Final resource apply preview",
        requirements=(
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_resource_apply_preview.py",
                "build_final_resource_apply_preview_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_resource_apply_preview.py",
                "final_resource_apply_preview_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_resource_apply_preview.py",
                "first_blocker",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/cli.py",
                "final-resource-apply-preview",
            ),
            SourceRequirement("Makefile", "final-resource-apply-preview:"),
            SourceRequirement("Makefile", "write_final_resource_apply_preview.sh"),
            SourceRequirement(
                "services/backend/scripts/write_final_resource_apply_preview.sh",
                ".local/final-resource-apply-preview.json",
            ),
            SourceRequirement(
                "services/backend/scripts/write_final_resource_apply_preview.sh",
                "accepted final resource apply preview exit code",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_demo_launch.py",
                "final_resource_apply_preview",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "FinalResourceApplyPreviewReport",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "FinalResourceApplyPreviewFirstBlocker",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "firstBlocker: FinalResourceApplyPreviewFirstBlocker?",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "finalResourceApplyPreview",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "applyPreviewRows",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "applyPreviewFirstBlockerRow",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "applyPreviewSlotRow",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "Apply preview",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/FinalLaunchStatusView.swift",
                "Apply Preview",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testDecodesFinalResourceApplyPreviewFromFinalLaunchPayload",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryShowsResourceApplyPreview",
            ),
        ),
    ),
    FeatureRequirement(
        id="provider_readiness",
        label="Provider readiness",
        requirements=(
            SourceRequirement("apps/mobile/ios/App/ProviderReadinessView.swift", "missingEnv"),
            SourceRequirement("apps/mobile/ios/App/ForgeRootView.swift", "getProviderReadiness"),
            SourceRequirement("Makefile", "write_provider_handoff.sh"),
            SourceRequirement(
                "services/backend/scripts/write_provider_handoff.sh",
                ".local/provider-handoff.json",
            ),
            SourceRequirement(
                "services/backend/scripts/write_provider_handoff.sh",
                "accepted provider handoff exit code",
            ),
        ),
    ),
    FeatureRequirement(
        id="final_showcase",
        label="Final showcase",
        requirements=(
            SourceRequirement("apps/mobile/ios/App/FinalShowcaseSummaryView.swift", "Final Showcase"),
            SourceRequirement("apps/mobile/ios/App/ForgeRootView.swift", "FinalShowcaseSummaryBuilder"),
            SourceRequirement(
                "apps/mobile/ios/App/ForgeRootView.swift",
                "finalLaunchSummary: finalLaunchMobileSummary",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalShowcaseSummary.swift",
                "finalLaunchSummary: FinalLaunchMobileSummary?",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalShowcaseSummary.swift",
                "npcEvaluationStage",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalShowcaseSummary.swift",
                "localSmokeStage",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalShowcaseSummary.swift",
                "Local Smoke",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalShowcaseSummary.swift",
                "providerHandoffStage",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalShowcaseSummary.swift",
                "Provider Handoff",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalShowcaseSummary.swift",
                "configuredEvidenceBundleRows",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalShowcaseSummary.swift",
                "iosDeployStage",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalShowcaseSummary.swift",
                "iOS Deploy",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalShowcaseSummary.swift",
                "threeDEvaluationStage",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalShowcaseSummary.swift",
                "operatorHandoffStage",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalShowcaseSummary.swift",
                "finalLaunchStage",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalShowcaseSummary.swift",
                '"npc_evaluation"',
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalShowcaseSummary.swift",
                '"local_smoke"',
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalShowcaseSummary.swift",
                '"provider_handoff"',
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalShowcaseSummary.swift",
                '"ios_deploy"',
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalShowcaseSummary.swift",
                '"three_d_evaluation"',
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalShowcaseSummary.swift",
                '"operator_handoff"',
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalShowcaseSummary.swift",
                '"final_launch"',
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalShowcaseSummaryIncludesBlockedFinalLaunchDigest",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalShowcaseSummaryIncludesReadyFinalLaunchDigest",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalShowcaseSummaryIncludesReadyProviderHandoffDigest",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalShowcaseSummaryBlocksProviderHandoffDigest",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalShowcaseSummaryBlocksProviderHandoffOnConfiguredEvidenceBundle",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalShowcaseSummaryRedactsUnsafeConfiguredBundleProviderHandoff",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalShowcaseSummaryRedactsUnsafeProviderHandoffDigest",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalShowcaseSummaryIncludesReadyLocalSmokeDigest",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalShowcaseSummaryBlocksFailedLocalSmokeDigest",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalShowcaseSummaryIncludesReadyIOSDeployDigest",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalShowcaseSummaryBlocksIOSDeployDigest",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalShowcaseSummaryRedactsUnsafeIOSDeployDigest",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalShowcaseSummaryIncludesReadyThreeDEvaluationDigest",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalShowcaseSummaryWaitsForMissingThreeDEvaluationDigest",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalShowcaseSummaryWaitsForMissingNPCEvaluationDigest",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalShowcaseSummaryRedactsUnsafeThreeDEvaluationDigest",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalShowcaseSummaryRedactsUnsafeFinalLaunchDigest",
            ),
        ),
    ),
    FeatureRequirement(
        id="mobile_final_acceptance_readiness",
        label="Mobile final acceptance readiness",
        requirements=(
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_acceptance_readiness.py",
                "build_final_acceptance_readiness_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_acceptance_readiness.py",
                "_freshness_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_acceptance_readiness.py",
                "final_acceptance_freshness",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_acceptance_readiness.py",
                "MOBILE_DEPLOY_PREFLIGHT_EVIDENCE_PATH",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_acceptance_readiness.py",
                "_enrich_mobile_preflight_blocker",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_demo_launch.py",
                "final_acceptance_readiness",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/npc_agent_evaluation_readiness.py",
                "build_npc_agent_evaluation_readiness_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_demo_launch.py",
                "npc_agent_evaluation_readiness",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "FinalAcceptanceFreshness",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "FinalAcceptanceReadinessReport",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "NPCAgentEvaluationReadinessReport",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "npcAgentEvaluationReadiness",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "freshness: FinalAcceptanceFreshness?",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "acceptanceRows",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "npcEvaluationRows",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                'freshness.status == "stale"',
            ),
            SourceRequirement("apps/mobile/ios/App/FinalLaunchStatusView.swift", "Acceptance"),
            SourceRequirement("apps/mobile/ios/App/FinalLaunchStatusView.swift", "NPC Evaluation"),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testDecodesFinalAcceptanceFreshnessFromFinalLaunchPayload",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryShowsStaleFinalAcceptanceFreshness",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryShowsBlockedFinalAcceptance",
            ),
            SourceRequirement(
                "services/backend/tests/test_final_acceptance_readiness.py",
                "test_final_acceptance_readiness_enriches_mobile_preflight_blocker_with_saved_next_action",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testDecodesNPCAgentEvaluationReadinessFromFinalLaunchPayload",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryShowsReadyNPCAgentEvaluation",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryShowsBlockedNPCAgentEvaluation",
            ),
        ),
    ),
    FeatureRequirement(
        id="mobile_3d_evaluation_readiness",
        label="Mobile 3D evaluation readiness",
        requirements=(
            SourceRequirement(
                "services/backend/src/myth_forge_api/three_d_evaluation_readiness.py",
                "build_three_d_evaluation_readiness_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/three_d_evaluation_readiness.py",
                "LOCAL_THREE_D_EVALUATION_COMMAND",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/three_d_evaluation_readiness.py",
                "make backend-evaluate-3d",
            ),
            SourceRequirement("Makefile", "backend-evaluate-3d:"),
            SourceRequirement("Makefile", "backend-evaluate-local:"),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_demo_launch.py",
                "three_d_evaluation_readiness",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_operator_handoff.py",
                "three_d_evaluation",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_operator_handoff.py",
                "LOCAL_THREE_D_EVALUATION_COMMAND",
            ),
            SourceRequirement(
                "services/backend/tests/test_three_d_evaluation_readiness.py",
                "test_three_d_evaluation_readiness_ready_report",
            ),
            SourceRequirement(
                "services/backend/tests/test_evaluation_make_targets.py",
                "test_evaluation_make_targets_dry_run_expected_local_commands",
            ),
            SourceRequirement(
                "services/backend/tests/test_final_demo_launch.py",
                "test_final_demo_launch_embeds_three_d_evaluation_readiness",
            ),
            SourceRequirement(
                "services/backend/tests/test_final_demo_launch.py",
                "test_final_demo_launch_operator_handoff_includes_three_d_evaluation_step",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "ThreeDEvaluationReadinessReport",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "threeDEvaluationReadiness",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "threeDEvaluationRows",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "threeDEvaluationRows(from:",
            ),
            SourceRequirement("apps/mobile/ios/App/FinalLaunchStatusView.swift", "3D Evaluation"),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testDecodesThreeDEvaluationReadinessFromFinalLaunchPayload",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryShowsReadyThreeDEvaluation",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryShowsBlockedThreeDEvaluation",
            ),
        ),
    ),
    FeatureRequirement(
        id="mobile_visual_regression_readiness",
        label="Mobile visual regression readiness",
        requirements=(
            SourceRequirement(
                "services/backend/src/myth_forge_api/visual_regression_readiness.py",
                "build_visual_regression_readiness_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/visual_regression_readiness.py",
                "make visual-regression-local",
            ),
            SourceRequirement("Makefile", "visual-regression-local:"),
            SourceRequirement(
                "Makefile",
                "--output .local/visual-regression-local.json",
            ),
            SourceRequirement(
                "Makefile",
                "final-local-report-refresh-local:",
            ),
            SourceRequirement(
                "Makefile",
                "final-demo-launch-local:",
            ),
            SourceRequirement(
                "Makefile",
                "final-demo-launch: final-demo-launch-local",
            ),
            SourceRequirement(
                "Makefile",
                "services/backend/scripts/write_final_local_report_refresh.sh",
            ),
            SourceRequirement(
                "Makefile",
                "final-rehearsal-local: backend-evaluate-local visual-regression-local "
                "final-acceptance-local final-demo-launch-local ios-deploy-runbook-local "
                "final-local-report-refresh-local",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_handoff_index.py",
                "visual_regression",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_device_launch_rehearsal.py",
                "visual_regression",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_demo_launch.py",
                "visual_regression_readiness",
            ),
            SourceRequirement(
                "services/backend/tests/test_visual_regression_readiness.py",
                "test_visual_regression_readiness_ready_from_saved_report",
            ),
            SourceRequirement(
                "services/backend/tests/test_final_demo_launch.py",
                "test_final_demo_launch_embeds_visual_regression_readiness",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "VisualRegressionReadinessReport",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "visualRegressionReadiness",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "visualRegressionRows",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "visualRegressionRows(from:",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/FinalLaunchStatusView.swift",
                "Visual Regression",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testDecodesVisualRegressionReadinessFromFinalLaunchPayload",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryShowsReadyVisualRegression",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryShowsBlockedVisualRegression",
            ),
        ),
    ),
    FeatureRequirement(
        id="mobile_local_showcase_smoke",
        label="Mobile local showcase smoke",
        requirements=(
            SourceRequirement(
                "services/backend/src/myth_forge_api/local_showcase_smoke.py",
                "build_local_showcase_smoke_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/local_showcase_smoke.py",
                "local_showcase_smoke_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/cli.py",
                "local-showcase-smoke",
            ),
            SourceRequirement("Makefile", "local-showcase-smoke:"),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_demo_launch.py",
                "local_showcase_smoke",
            ),
            SourceRequirement(
                "services/backend/tests/test_local_showcase_smoke.py",
                "test_local_showcase_smoke_runs_full_http_loop",
            ),
            SourceRequirement(
                "services/backend/tests/test_final_demo_launch.py",
                "test_final_demo_launch_embeds_local_showcase_smoke",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "LocalShowcaseSmokeReport",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "localShowcaseSmoke",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "localShowcaseSmokeRows",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "provider_calls=",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/FinalLaunchStatusView.swift",
                "Local Smoke",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testDecodesLocalShowcaseSmokeFromFinalLaunchPayload",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryShowsLocalShowcaseSmoke",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryRedactsUnsafeLocalShowcaseSmoke",
            ),
        ),
    ),
    FeatureRequirement(
        id="showcase_visual_regression_index",
        label="Showcase visual regression index",
        requirements=(
            SourceRequirement(
                "services/backend/src/myth_forge_api/visual_regression.py",
                "DEFAULT_VISUAL_ARTIFACTS",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/visual_regression.py",
                "p0.12_ios_device_media_input",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/visual_regression.py",
                "p0.19_guided_scan_entry",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/visual_regression.py",
                "p0.98_capture_generation_receipt",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/visual_regression.py",
                "p0.103_generation_result_receipt",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/visual_regression.py",
                "p0.118_scene_load_proof",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/visual_regression.py",
                "p0.82_npc_agent_tick_summary",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/visual_regression.py",
                "p0.101_print_fulfillment_receipt",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/visual_regression.py",
                "p0.214_showcase_evidence_visual",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/visual_regression.py",
                "p0.215_final_demo_launch_local_alias",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/visual_regression.py",
                "p0.216_final_showcase_next_action",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/visual_regression.py",
                "p0.217_final_resource_next_action",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/visual_regression.py",
                "p0.218_final_demo_launch_next_action",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/visual_regression.py",
                "p0.221_mobile_auto_backend_url_handoff",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/visual_regression.py",
                "p0.222_final_showcase_device_action_bundle",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/visual_regression.py",
                "p0.223_preflight_evidence_device_actions",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/visual_regression.py",
                "p0.224_xcode_evidence_device_action",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/visual_regression.py",
                "p0.100_live_provider_consent",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/visual_regression.py",
                "p0.112_ios_device_launch_rehearsal",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/visual_regression.py",
                "p0.119_visual_regression_handoff",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/visual_regression.py",
                "p0.186_configured_acceptance_command_visual",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/visual_regression.py",
                "p0.189_device_blocker_handoff",
            ),
            SourceRequirement(
                "services/backend/tests/test_visual_regression.py",
                "test_default_visual_artifacts_cover_full_showcase_flow",
            ),
            SourceRequirement(
                "services/backend/tests/test_visual_regression.py",
                "test_visual_regression_default_passes_checked_in_showcase_artifacts",
            ),
            SourceRequirement(
                "services/backend/tests/test_visual_regression.py",
                "test_visual_regression_cli_writes_showcase_report",
            ),
            SourceRequirement("README.md", "full-showcase visual index"),
            SourceRequirement("README.md", "30 static 390x844 iPhone evidence artifacts"),
            SourceRequirement("README.md", "configured acceptance command visual"),
            SourceRequirement("README.md", "device blocker handoff visual"),
        ),
    ),
    FeatureRequirement(
        id="mobile_live_provider_evidence",
        label="Mobile live provider evidence",
        requirements=(
            SourceRequirement(
                "services/backend/src/myth_forge_api/live_provider_evidence.py",
                "build_live_provider_evidence_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/live_provider_evidence.py",
                "live_provider_evidence_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/live_provider_evidence.py",
                "make live-provider-evidence",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/cli.py",
                "live-provider-evidence",
            ),
            SourceRequirement("Makefile", "live-provider-evidence:"),
            SourceRequirement("Makefile", "write_live_provider_evidence.sh"),
            SourceRequirement(
                "services/backend/scripts/write_live_provider_evidence.sh",
                ".local/live-provider-evidence.json",
            ),
            SourceRequirement(
                "services/backend/scripts/write_live_provider_evidence.sh",
                "accepted live provider evidence exit code",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_demo_launch.py",
                "live_provider_evidence",
            ),
            SourceRequirement(
                "services/backend/tests/test_live_provider_evidence.py",
                "test_live_provider_evidence_missing_reports_without_running_commands",
            ),
            SourceRequirement(
                "services/backend/tests/test_final_demo_launch.py",
                "test_final_demo_launch_embeds_live_provider_evidence",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "LiveProviderEvidenceReport",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "liveProviderEvidence",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "liveProviderEvidenceRows",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "Live evidence",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/FinalLaunchStatusView.swift",
                "Live Evidence",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testDecodesLiveProviderEvidenceFromFinalLaunchPayload",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryShowsMissingLiveProviderEvidence",
            ),
        ),
    ),
    FeatureRequirement(
        id="ios_deploy_runbook",
        label="iOS deploy runbook",
        requirements=(
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_deploy_runbook.py",
                "build_ios_deploy_runbook_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_deploy_runbook.py",
                "build_three_d_evaluation_readiness_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_deploy_runbook.py",
                "LOCAL_THREE_D_EVALUATION_COMMAND",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_deploy_runbook.py",
                "LOCAL_NPC_EVALUATION_COMMAND",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_deploy_runbook.py",
                "LOCAL_FINAL_ACCEPTANCE_COMMAND",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_deploy_runbook.py",
                "three_d_evaluation",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_deploy_runbook.py",
                "IOS_DEPLOY_RUNBOOK_COMMAND",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/cli.py",
                "ios-deploy-runbook",
            ),
            SourceRequirement("Makefile", "ios-deploy-runbook:"),
            SourceRequirement("Makefile", "ios-deploy-runbook-local:"),
            SourceRequirement("Makefile", "backend-evaluate-3d:"),
            SourceRequirement("Makefile", "backend-evaluate-npc:"),
            SourceRequirement("Makefile", "backend-evaluate-local:"),
            SourceRequirement(
                "services/backend/scripts/write_ios_deploy_runbook_local.sh",
                "accepted iOS deploy runbook exit code $status",
            ),
            SourceRequirement(
                "services/backend/scripts/write_ios_deploy_runbook_local.sh",
                "services/backend/.local/ios-deploy-runbook-local.json",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_demo_launch.py",
                "ios_deploy_runbook",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_demo_launch.py",
                "ios_device_launch_rehearsal_readiness",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_demo_launch.py",
                "ios_device_evidence_bundle",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_device_evidence_bundle.py",
                "build_ios_device_evidence_bundle_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_device_evidence_bundle.py",
                "ios_device_evidence_bundle_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_device_launch_rehearsal_readiness.py",
                "build_ios_device_launch_rehearsal_readiness_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_device_launch_rehearsal_readiness.py",
                "ios_device_launch_rehearsal_readiness_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_device_launch_rehearsal_readiness.py",
                "_freshness_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_device_launch_rehearsal_readiness.py",
                "ios_device_launch_rehearsal_freshness",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_device_launch_rehearsal_readiness.py",
                "stale_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_device_launch_rehearsal_readiness.py",
                "rerun make ios-device-launch-rehearsal",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_operator_handoff.py",
                "ios_deploy_runbook",
            ),
            SourceRequirement(
                "services/backend/tests/test_ios_deploy_runbook.py",
                "test_ios_deploy_runbook_ready_local_inputs_preserve_command_order",
            ),
            SourceRequirement(
                "services/backend/tests/test_ios_deploy_runbook.py",
                "test_ios_deploy_runbook_blocks_and_redacts_failed_3d_evaluation",
            ),
            SourceRequirement(
                "services/backend/tests/test_final_rehearsal_scripts.py",
                "test_write_ios_deploy_runbook_local_accepts_blocked_report_exit_code",
            ),
            SourceRequirement(
                "services/backend/tests/test_final_demo_launch.py",
                "test_final_demo_launch_embeds_ios_deploy_runbook",
            ),
            SourceRequirement(
                "services/backend/tests/test_final_operator_handoff.py",
                "test_operator_handoff_includes_ios_deploy_runbook_before_deploy_preflight",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "IOSDeployRunbookReport",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "iosDeployRunbook",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "IOSDeviceEvidenceBundleReport",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "iosDeviceEvidenceBundle",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "IOSDeviceLaunchRehearsalReadinessReport",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "iosDeviceLaunchRehearsalReadiness",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "deployRunbookRows",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "deployRunbookCommandRows",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "deployRunbookSafetyRows",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "deviceEvidenceRows",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "launchRehearsalRows",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "rehearsalFreshnessRow",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "Freshness:",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/FinalLaunchStatusView.swift",
                "iOS Deploy Runbook",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/FinalLaunchStatusView.swift",
                "Deploy Commands",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/FinalLaunchStatusView.swift",
                "Deploy Safety",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/FinalLaunchStatusView.swift",
                "Device Evidence",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/FinalLaunchStatusView.swift",
                "Launch Rehearsal",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testDecodesIOSDeployRunbookFromFinalLaunchPayload",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryShowsPartialIOSDeployRunbook",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryShowsThreeDEvaluationIOSDeployRunbookSlot",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryShowsBlockedIOSDeployRunbook",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryRedactsUnsafeIOSDeployRunbook",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testDecodesIOSDeviceEvidenceBundleFromFinalLaunchPayload",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryShowsIOSDeviceEvidenceBundle",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryRedactsUnsafeIOSDeviceEvidenceBundle",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testDecodesIOSDeviceLaunchRehearsalReadinessFromFinalLaunchPayload",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testDecodesIOSDeviceLaunchRehearsalFreshnessFromFinalLaunchPayload",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryShowsBlockedIOSDeviceLaunchRehearsal",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryShowsReadyIOSDeviceLaunchRehearsal",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryShowsStaleIOSDeviceLaunchRehearsalFreshness",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryRedactsUnsafeIOSDeviceLaunchRehearsal",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "ResourceHandoffReport",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "resourceReport",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "resourceHandoffRows",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "resourceHandoffBackendRows",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "resourceHandoffIOSRows",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/FinalLaunchStatusView.swift",
                "Resource Handoff",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/FinalLaunchStatusView.swift",
                "Backend Resources",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/FinalLaunchStatusView.swift",
                "iOS Resources",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testDecodesResourceHandoffFromFinalLaunchPayload",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryShowsMissingResourceHandoff",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryShowsReadyResourceHandoff",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryRedactsUnsafeResourceHandoff",
            ),
        ),
    ),
    FeatureRequirement(
        id="mobile_final_operator_handoff",
        label="Mobile final operator handoff",
        requirements=(
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_operator_handoff.py",
                "build_final_operator_handoff_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_acceptance_readiness.py",
                'LOCAL_FINAL_ACCEPTANCE_COMMAND = "make final-acceptance-local"',
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_operator_handoff.py",
                "npc_agent_evaluation",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_operator_handoff.py",
                "LOCAL_NPC_EVALUATION_COMMAND",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/npc_agent_evaluation_readiness.py",
                "make backend-evaluate-npc",
            ),
            SourceRequirement("Makefile", "final-acceptance-local:"),
            SourceRequirement("Makefile", "final-rehearsal-local:"),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileProjectChecks/main.swift",
                "final-local-report-refresh-local:",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileProjectChecks/main.swift",
                "final-demo-launch-local:",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileProjectChecks/main.swift",
                "final-demo-launch: final-demo-launch-local",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileProjectChecks/main.swift",
                "services/backend/scripts/write_final_local_report_refresh.sh",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileProjectChecks/main.swift",
                "final-rehearsal-local: backend-evaluate-local visual-regression-local "
                "final-acceptance-local final-demo-launch-local ios-deploy-runbook-local "
                "final-local-report-refresh-local",
            ),
            SourceRequirement("Makefile", "backend-evaluate-npc:"),
            SourceRequirement("Makefile", "backend-evaluate-local:"),
            SourceRequirement(
                "services/backend/scripts/write_final_acceptance_local.sh",
                "accepted final acceptance exit code $status",
            ),
            SourceRequirement(
                "services/backend/scripts/write_final_acceptance_local.sh",
                "services/backend/.local/final-acceptance-local.json",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_demo_launch.py",
                "final_operator_handoff",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_demo_launch.py",
                "npc_agent_evaluation_readiness=npc_agent_evaluation_readiness",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "FinalOperatorHandoffReport",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "finalOperatorHandoff",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "handoffRows",
            ),
            SourceRequirement("apps/mobile/ios/App/FinalLaunchStatusView.swift", "Next"),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryShowsHandoffNextActions",
            ),
            SourceRequirement(
                "services/backend/tests/test_final_demo_launch.py",
                "test_final_demo_launch_operator_handoff_includes_npc_evaluation_step",
            ),
            SourceRequirement(
                "services/backend/tests/test_final_rehearsal_scripts.py",
                "test_final_rehearsal_make_targets_dry_run_expected_order",
            ),
        ),
    ),
    FeatureRequirement(
        id="configured_handoff_preflight",
        label="Configured handoff preflight",
        requirements=(
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_configured_preflight.py",
                "build_final_configured_preflight_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_configured_preflight.py",
                "final_configured_preflight_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_configured_preflight.py",
                "build_provider_handoff_report",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileProjectChecks/main.swift",
                "build_provider_handoff_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_configured_preflight.py",
                "build_ios_deploy_runbook_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_configured_preflight.py",
                '"provider_calls": False',
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_configured_preflight.py",
                '"writes_backend_env": False',
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_configured_preflight.py",
                '"writes_ios_deploy_config": False',
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/cli.py",
                "final-configured-preflight",
            ),
            SourceRequirement("Makefile", "final-configured-preflight:"),
            SourceRequirement("Makefile", "write_final_configured_preflight.sh"),
            SourceRequirement("Makefile", "write_final_configured_evidence_plan.sh"),
            SourceRequirement("Makefile", "write_configured_live_evidence_bundle.sh"),
            SourceRequirement(
                "services/backend/scripts/write_final_configured_preflight.sh",
                ".local/final-configured-preflight.json",
            ),
            SourceRequirement(
                "services/backend/scripts/write_final_configured_preflight.sh",
                "accepted final configured preflight exit code",
            ),
            SourceRequirement(
                "services/backend/scripts/write_final_configured_evidence_plan.sh",
                ".local/final-configured-evidence-plan.json",
            ),
            SourceRequirement(
                "services/backend/scripts/write_final_configured_evidence_plan.sh",
                "accepted final configured evidence plan exit code",
            ),
            SourceRequirement(
                "services/backend/scripts/write_configured_live_evidence_bundle.sh",
                ".local/configured-live-evidence-bundle.json",
            ),
            SourceRequirement(
                "services/backend/scripts/write_configured_live_evidence_bundle.sh",
                "accepted configured live evidence bundle exit code",
            ),
            SourceRequirement(
                "services/backend/tests/test_final_configured_preflight.py",
                "test_configured_preflight_is_ready_with_configured_handoff_inputs",
            ),
            SourceRequirement(
                "services/backend/tests/test_cli.py",
                "test_cli_final_configured_preflight_writes_report_and_returns_result_code",
            ),
        ),
    ),
    FeatureRequirement(
        id="final_handoff_index",
        label="Final handoff index",
        requirements=(
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_handoff_index.py",
                "build_final_handoff_index_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_handoff_index.py",
                "final_handoff_index_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_handoff_index.py",
                "build_final_configured_preflight_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_handoff_index.py",
                "operator_sequence",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_handoff_index.py",
                "source_reports",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_handoff_index.py",
                "first_blocker",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_handoff_index.py",
                "visual_regression",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_handoff_index.py",
                '"provider_calls": False',
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_handoff_index.py",
                '"writes_backend_env": False',
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_handoff_index.py",
                '"writes_ios_deploy_config": False',
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/cli.py",
                "final-handoff-index",
            ),
            SourceRequirement("Makefile", "final-handoff-index:"),
            SourceRequirement("Makefile", "write_final_handoff_index.sh"),
            SourceRequirement(
                "services/backend/scripts/write_final_handoff_index.sh",
                ".local/final-handoff-index.json",
            ),
            SourceRequirement(
                "services/backend/scripts/write_final_handoff_index.sh",
                "accepted final handoff index exit code",
            ),
            SourceRequirement(
                "services/backend/tests/test_final_handoff_index.py",
                "test_final_handoff_index_ready_when_local_and_configured_inputs_are_ready",
            ),
            SourceRequirement(
                "services/backend/tests/test_cli.py",
                "test_cli_final_handoff_index_writes_report_and_returns_result_code",
            ),
        ),
    ),
    FeatureRequirement(
        id="ios_device_launch_certificate",
        label="iOS device launch certificate",
        requirements=(
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_device_launch_certificate.py",
                "build_ios_device_launch_certificate_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_device_launch_certificate.py",
                "ios_device_launch_certificate_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_device_launch_certificate.py",
                "build_final_handoff_index_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_device_launch_certificate.py",
                "build_ios_deploy_runbook_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_device_launch_certificate.py",
                "build_final_demo_launch_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_device_launch_certificate.py",
                "first_blocker",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_device_launch_certificate.py",
                "device_gates",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_device_launch_certificate.py",
                "operator_sequence",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_device_launch_certificate.py",
                '"provider_calls": False',
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_device_launch_certificate.py",
                '"xcode_or_signing": False',
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_device_launch_certificate.py",
                '"keychain_writes": False',
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/cli.py",
                "ios-device-launch-certificate",
            ),
            SourceRequirement("Makefile", "ios-device-launch-certificate:"),
            SourceRequirement("Makefile", "write_ios_device_launch_certificate.sh"),
            SourceRequirement(
                "services/backend/scripts/write_ios_device_launch_certificate.sh",
                ".local/ios-device-launch-certificate.json",
            ),
            SourceRequirement(
                "services/backend/scripts/write_ios_device_launch_certificate.sh",
                "accepted iOS device launch certificate exit code",
            ),
            SourceRequirement(
                "services/backend/tests/test_ios_device_launch_certificate.py",
                "test_ios_device_launch_certificate_ready_with_configured_inputs",
            ),
            SourceRequirement(
                "services/backend/tests/test_ios_device_launch_certificate.py",
                "test_ios_device_launch_certificate_cli_writes_report_and_makefile_target",
            ),
        ),
    ),
    FeatureRequirement(
        id="ios_deploy_apply_preview_gate",
        label="iOS deploy apply preview gate",
        requirements=(
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_deploy_runbook.py",
                "build_final_resource_apply_preview_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_deploy_runbook.py",
                "preview_final_resource_apply",
            ),
            SourceRequirement(
                "services/backend/tests/test_ios_deploy_runbook.py",
                "final_resource_apply_preview",
            ),
            SourceRequirement(
                "services/backend/tests/test_ios_device_launch_certificate.py",
                "make final-resource-apply-preview",
            ),
        ),
    ),
    FeatureRequirement(
        id="ios_device_launch_rehearsal",
        label="iOS device launch rehearsal",
        requirements=(
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_device_launch_rehearsal.py",
                "build_ios_device_launch_rehearsal_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_device_launch_rehearsal.py",
                "ios_device_launch_rehearsal_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_device_launch_rehearsal.py",
                "LOCAL_REPORT_SOURCES",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_device_launch_rehearsal.py",
                "visual_regression",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_device_launch_rehearsal.py",
                "REHEARSAL_REPORT_SOURCES",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_device_launch_rehearsal.py",
                "final_configured_preflight",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_device_launch_rehearsal.py",
                "final_handoff_index",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_device_launch_rehearsal.py",
                "ios_device_launch_certificate",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_device_launch_rehearsal.py",
                "operator_actions",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_device_launch_rehearsal.py",
                "first_blocker",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_device_launch_rehearsal.py",
                '"provider_calls": False',
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_device_launch_rehearsal.py",
                '"xcode_or_signing": False',
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_device_launch_rehearsal.py",
                '"keychain_writes": False',
            ),
            SourceRequirement(
                "services/backend/scripts/write_ios_device_launch_rehearsal.sh",
                "run_report_command",
            ),
            SourceRequirement(
                "services/backend/scripts/write_ios_device_launch_rehearsal.sh",
                "accepted $label exit code",
            ),
            SourceRequirement(
                "services/backend/scripts/write_ios_device_launch_rehearsal.sh",
                "final-configured-preflight",
            ),
            SourceRequirement("Makefile", "write_ios_device_evidence_bundle.sh"),
            SourceRequirement(
                "services/backend/scripts/write_ios_device_evidence_bundle.sh",
                ".local/ios-device-evidence-bundle.json",
            ),
            SourceRequirement(
                "services/backend/scripts/write_ios_device_evidence_bundle.sh",
                "accepted iOS device evidence bundle exit code",
            ),
            SourceRequirement(
                "services/backend/scripts/write_ios_device_launch_rehearsal.sh",
                "final-handoff-index",
            ),
            SourceRequirement(
                "services/backend/scripts/write_ios_device_launch_rehearsal.sh",
                "ios-device-launch-certificate",
            ),
            SourceRequirement(
                "services/backend/scripts/write_ios_device_launch_rehearsal.sh",
                "ios-device-launch-rehearsal",
            ),
            SourceRequirement(
                "services/backend/scripts/write_ios_device_launch_rehearsal.sh",
                "final launch rehearsal sync",
            ),
            SourceRequirement(
                "services/backend/scripts/write_ios_device_launch_rehearsal.sh",
                "final-demo-launch",
            ),
            SourceRequirement(
                "services/backend/scripts/write_ios_device_launch_rehearsal.sh",
                "--mode local",
            ),
            SourceRequirement(
                "services/backend/scripts/write_ios_device_launch_rehearsal.sh",
                ".local/final-demo-launch-local.json",
            ),
            SourceRequirement(
                "services/backend/scripts/write_ios_device_launch_rehearsal.sh",
                "services/backend/.local/ios-device-launch-rehearsal.json",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/cli.py",
                "ios-device-launch-rehearsal",
            ),
            SourceRequirement("Makefile", "ios-device-launch-rehearsal:"),
            SourceRequirement(
                "Makefile",
                "services/backend/scripts/write_ios_device_launch_rehearsal.sh",
            ),
            SourceRequirement(
                "services/backend/tests/test_ios_device_launch_rehearsal.py",
                "test_ios_device_launch_rehearsal_partial_when_saved_reports_are_ready_with_manual_gates",
            ),
            SourceRequirement(
                "services/backend/tests/test_ios_device_launch_rehearsal.py",
                "test_ios_device_launch_rehearsal_cli_writes_report_and_makefile_target",
            ),
        ),
    ),
    FeatureRequirement(
        id="mobile_final_launch_mode",
        label="Mobile final launch mode",
        requirements=(
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "FinalLaunchMode",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "FinalResourcesPreflightItem",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "items: [FinalResourcesPreflightItem]",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "displayLabel",
            ),
            SourceRequirement("apps/mobile/ios/App/AppConfiguration.swift", "PMFFinalLaunchMode"),
            SourceRequirement("apps/mobile/ios/App/AppConfiguration.swift", "FinalLaunchMode.safe"),
            SourceRequirement("apps/mobile/ios/App/ForgeRootView.swift", "finalLaunchMode"),
            SourceRequirement(
                "apps/mobile/ios/App/ForgeRootView.swift",
                'Picker("Final launch mode"',
            ),
            SourceRequirement("apps/mobile/ios/App/ForgeRootView.swift", "FinalLaunchMode.allCases"),
            SourceRequirement(
                "apps/mobile/ios/App/ForgeRootView.swift",
                "loadFinalDemoLaunch(mode: finalLaunchMode)",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/ForgeRootView.swift",
                "getFinalDemoLaunch(mode: mode.rawValue)",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/ForgeRootView.swift",
                ".onChange(of: finalLaunchMode)",
            ),
            SourceRequirement("apps/mobile/ios/App/Info.plist", "PMFFinalLaunchMode"),
            SourceRequirement("apps/mobile/ios/App/Info.plist", "$(PMF_FINAL_LAUNCH_MODE)"),
            SourceRequirement(
                "apps/mobile/ios/Config/Deployment.xcconfig",
                "PMF_FINAL_LAUNCH_MODE",
            ),
            SourceRequirement(
                "apps/mobile/ios/Config/Deployment.local.xcconfig.example",
                "PMF_FINAL_LAUNCH_MODE",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchModeDefaultsToLocalForUnsafeValues",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testGetConfiguredFinalDemoLaunchBuildsGETRequest",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "modePolicyRows",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "liveCallPolicy",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "launchReceiptRows",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "firstBlockerReceiptRow",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_demo_launch.py",
                "first_blocker",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_demo_launch.py",
                "next_action",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_demo_launch.py",
                "_apply_concrete_mobile_preflight_next_action",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_demo_launch.py",
                "validation_command",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_demo_launch.py",
                "_phase_blocker_with_nested_hint",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "FinalDemoLaunchFirstBlocker",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "FinalDemoLaunchNextAction",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "validationCommand: String?",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "firstBlocker: FinalDemoLaunchFirstBlocker?",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "nextAction: FinalDemoLaunchNextAction?",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "status: String?",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "report.firstBlocker",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "launchStatus(_ report: FinalDemoLaunchReport)",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "Next action:",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryUsesTopLevelFirstBlockerReceipt",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryShowsFinalDemoLaunchNextAction",
            ),
            SourceRequirement(
                "services/backend/tests/test_final_demo_launch.py",
                "test_local_final_demo_launch_mobile_preflight_blocker_includes_saved_evidence_detail",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryPrefersTopLevelStatus",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "resourceChecklistRows",
            ),
            SourceRequirement("apps/mobile/ios/App/FinalLaunchStatusView.swift", "Launch Receipt"),
            SourceRequirement("apps/mobile/ios/App/FinalLaunchStatusView.swift", "Resource Checklist"),
            SourceRequirement("apps/mobile/ios/App/FinalLaunchStatusView.swift", "Mode"),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryShowsConfiguredModePolicy",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryShowsAcceptanceBlockerReceipt",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryShowsReadyConfiguredReceipt",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryShowsMissingResourceChecklist",
            ),
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
                "apps/mobile/ios/App/ForgeRootView.swift",
                "finalLaunchSummary: finalLaunchMobileSummary",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/DemoScript.swift",
                "DemoScriptBuilder",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/DemoScript.swift",
                "final_launch",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/DemoScript.swift",
                "three_d_evaluation",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/DemoScript.swift",
                "npc_evaluation",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/DemoScript.swift",
                "threeDEvaluationStep",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/DemoScript.swift",
                "npcEvaluationStep",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/DemoScript.swift",
                "FinalLaunchMobileSummary",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testDemoScriptShowsBlockedFinalLaunch",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testDemoScriptShowsReadyNPCEvaluationBeforeFinalLaunch",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testDemoScriptShowsReadyThreeDEvaluationBeforeNPCEvaluation",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testDemoScriptWaitsForMissingThreeDEvaluation",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testDemoScriptBlocksAndRedactsFailedThreeDEvaluation",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testDemoScriptWaitsForMissingNPCEvaluation",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testDemoScriptBlocksAndRedactsFailedNPCEvaluation",
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
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ShowcaseAutopilot.swift",
                'script.step(id: "final_launch")',
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ShowcaseAutopilot.swift",
                'script.step(id: "three_d_evaluation")',
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ShowcaseAutopilot.swift",
                'script.step(id: "npc_evaluation")',
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testShowcaseAutopilotBlocksOnFinalLaunchBlocker",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testShowcaseAutopilotWaitsForMissingNPCEvaluation",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testShowcaseAutopilotWaitsForMissingThreeDEvaluation",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testShowcaseAutopilotBlocksOnFailedThreeDEvaluation",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testShowcaseAutopilotBlocksOnFailedNPCEvaluation",
            ),
        ),
    ),
    FeatureRequirement(
        id="final_showcase_readiness_ledger",
        label="Final showcase readiness ledger",
        requirements=(
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_showcase_readiness.py",
                "final_showcase_readiness_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_showcase_readiness.py",
                "next_action",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_showcase_readiness.py",
                "build_local_showcase_smoke_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_showcase_readiness.py",
                "local_showcase_smoke",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_showcase_readiness.py",
                "_report_blocker_detail",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_demo_launch.py",
                "final_showcase_readiness",
            ),
            SourceRequirement("services/backend/src/myth_forge_api/cli.py", "final-showcase-readiness"),
            SourceRequirement("Makefile", "final-showcase-readiness:"),
            SourceRequirement("Makefile", "write_final_showcase_readiness.sh"),
            SourceRequirement(
                "services/backend/scripts/write_final_showcase_readiness.sh",
                ".local/final-showcase-readiness.json",
            ),
            SourceRequirement(
                "services/backend/scripts/write_final_showcase_readiness.sh",
                "accepted final showcase readiness exit code",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "FinalShowcaseReadinessReport",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "FinalShowcaseReadinessNextAction",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "finalShowcaseReadiness",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "showcaseReadinessRows",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "Next action:",
            ),
            SourceRequirement(
                "apps/mobile/ios/App/FinalLaunchStatusView.swift",
                "Showcase Readiness",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testDecodesFinalShowcaseReadinessFromFinalLaunchPayload",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryRedactsUnsafeFinalShowcaseReadiness",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryShowsFinalShowcaseNextAction",
            ),
            SourceRequirement(
                "services/backend/tests/test_final_showcase_readiness.py",
                "test_final_showcase_readiness_blocks_failed_local_showcase_smoke",
            ),
            SourceRequirement(
                "services/backend/tests/test_final_showcase_readiness.py",
                "test_final_showcase_readiness_functional_regression_uses_concrete_preflight_action",
            ),
        ),
    ),
    FeatureRequirement(
        id="mobile_final_showcase_device_action_bundle",
        label="Mobile final showcase device action bundle",
        requirements=(
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_showcase_readiness.py",
                "device_action_bundle",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_showcase_readiness.py",
                "_device_action_bundle",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_showcase_readiness.py",
                "make backend-device-demo",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_showcase_readiness.py",
                "mobile_deploy_preflight_evidence",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_showcase_readiness.py",
                "mobile_xcode_build_evidence",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_showcase_readiness.py",
                "make mobile-xcode-build-evidence",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_showcase_readiness.py",
                "validation_command",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_showcase_readiness.py",
                "_device_action_child_next_action",
            ),
            SourceRequirement(
                "services/backend/tests/test_final_showcase_readiness.py",
                "test_final_showcase_readiness_next_action_uses_preflight_child_action",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/mobile_deploy_preflight_evidence.py",
                "first_blocker",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/mobile_deploy_preflight_evidence.py",
                "next_action",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/mobile_deploy_preflight_evidence.py",
                "validation_command",
            ),
            SourceRequirement(
                "services/backend/tests/test_mobile_deploy_preflight_evidence.py",
                "test_preflight_evidence_blocks_missing_config_with_actions",
            ),
            SourceRequirement(
                "services/backend/tests/test_final_showcase_readiness.py",
                "test_final_showcase_readiness_includes_ios_device_action_bundle",
            ),
            SourceRequirement(
                "services/backend/tests/test_final_showcase_readiness.py",
                "test_final_showcase_readiness_marks_preflight_actions_ready_with_evidence",
            ),
            SourceRequirement(
                "services/backend/tests/test_final_showcase_readiness.py",
                "test_final_showcase_readiness_maps_blocked_mobile_xcode_build_evidence",
            ),
            SourceRequirement(
                "services/backend/tests/test_final_showcase_readiness.py",
                "test_final_showcase_readiness_marks_xcode_action_ready_with_evidence",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "FinalShowcaseDeviceActionBundle",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "evidenceStatus: String?",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "validationCommand: String?",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "deviceActionBundle: FinalShowcaseDeviceActionBundle?",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "showcaseDeviceActionBundleRows",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "selectedShowcaseDeviceActions",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "Device actions",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "evidenceStatus",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "validationCommand",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "make mobile-deploy-preflight",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "make mobile-deploy-preflight-evidence",
            ),
            SourceRequirement(
                "Makefile",
                "write_mobile_deploy_preflight_evidence.sh",
            ),
            SourceRequirement(
                "services/backend/scripts/write_mobile_deploy_preflight_evidence.sh",
                ".local/mobile-deploy-preflight-evidence.json",
            ),
            SourceRequirement(
                "services/backend/scripts/write_mobile_deploy_preflight_evidence.sh",
                "accepted mobile deploy preflight evidence exit code",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "make mobile-xcode-build-evidence",
            ),
            SourceRequirement(
                "Makefile",
                "write_mobile_xcode_build_evidence.sh",
            ),
            SourceRequirement(
                "services/backend/scripts/write_mobile_xcode_build_evidence.sh",
                ".local/mobile-xcode-build-evidence.json",
            ),
            SourceRequirement(
                "services/backend/scripts/write_mobile_xcode_build_evidence.sh",
                "accepted mobile Xcode build evidence exit code",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testDecodesFinalShowcaseReadinessFromFinalLaunchPayload",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryShowsFinalShowcaseDeviceActionBundle",
            ),
        ),
    ),
    FeatureRequirement(
        id="final_showcase_apply_preview_ledger",
        label="Final showcase apply preview ledger",
        requirements=(
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_showcase_readiness.py",
                "build_final_resource_apply_preview_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_showcase_readiness.py",
                "final_resource_apply_preview",
            ),
            SourceRequirement(
                "services/backend/tests/test_final_showcase_readiness.py",
                "final_resource_apply_preview:missing",
            ),
            SourceRequirement(
                "services/backend/tests/test_final_showcase_readiness.py",
                "final_resource_apply_preview:ready",
            ),
        ),
    ),
    FeatureRequirement(
        id="final_external_action_ledger",
        label="Final external action ledger",
        requirements=(
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_external_action_ledger.py",
                "build_final_external_action_ledger_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_external_action_ledger.py",
                "final_external_action_ledger_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_external_action_ledger.py",
                "global_machine_actions",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_external_action_ledger.py",
                "requires_cost_consent_for_live_actions",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_demo_launch.py",
                "final_external_action_ledger",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/cli.py",
                "final-external-action-ledger",
            ),
            SourceRequirement("Makefile", "final-external-action-ledger:"),
            SourceRequirement(
                "Makefile",
                "write_final_external_action_ledger.sh",
            ),
            SourceRequirement(
                "services/backend/scripts/write_final_external_action_ledger.sh",
                ".local/final-external-action-ledger.json",
            ),
            SourceRequirement(
                "services/backend/scripts/write_final_external_action_ledger.sh",
                "accepted final external action ledger exit code",
            ),
            SourceRequirement(
                "services/backend/tests/test_final_external_action_ledger.py",
                "test_external_action_ledger_blocks_missing_resources_without_running_actions",
            ),
            SourceRequirement(
                "services/backend/tests/test_cli.py",
                "test_cli_final_external_action_ledger_writes_report_and_returns_result_code",
            ),
            SourceRequirement(
                "services/backend/tests/test_final_demo_launch.py",
                "test_final_demo_launch_embeds_final_external_action_ledger",
            ),
            SourceRequirement("README.md", "P0.128"),
        ),
    ),
    FeatureRequirement(
        id="mobile_external_action_ledger",
        label="Mobile external action ledger",
        requirements=(
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "FinalExternalActionLedgerReport",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "finalExternalActionLedger",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "externalActionLedgerRows",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "externalActionLedgerRows && from: report.finalExternalActionLedger",
                (
                    "externalActionLedgerRows",
                    "from: report.finalExternalActionLedger",
                ),
            ),
            SourceRequirement(
                "apps/mobile/ios/App/FinalLaunchStatusView.swift",
                "External Actions",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testDecodesFinalExternalActionLedgerFromFinalLaunchPayload",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryShowsExternalActionLedger",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryRedactsUnsafeExternalActionLedger",
            ),
            SourceRequirement("README.md", "P0.129"),
        ),
    ),
    FeatureRequirement(
        id="final_launch_closure_packet",
        label="Final launch closure packet",
        requirements=(
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_launch_closure_packet.py",
                "build_final_launch_closure_packet_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_launch_closure_packet.py",
                "final_launch_closure_packet_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_launch_closure_packet.py",
                "requires_cost_consent_for_live_actions",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_launch_closure_packet.py",
                "first_blocker",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_demo_launch.py",
                "final_launch_closure_packet",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/cli.py",
                "final-launch-closure-packet",
            ),
            SourceRequirement("Makefile", "final-launch-closure-packet:"),
            SourceRequirement(
                "Makefile",
                "write_final_launch_closure_packet.sh",
            ),
            SourceRequirement(
                "services/backend/scripts/write_final_launch_closure_packet.sh",
                ".local/final-launch-closure-packet.json",
            ),
            SourceRequirement(
                "services/backend/scripts/write_final_launch_closure_packet.sh",
                "accepted final launch closure packet exit code",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_local_report_refresh.py",
                "build_final_launch_closure_packet_report",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_local_report_refresh.py",
                "final-launch-closure-packet.json",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_local_report_refresh.py",
                "first_blocker",
            ),
            SourceRequirement(
                "services/backend/tests/test_final_launch_closure_packet.py",
                "test_final_launch_closure_packet_blocks_missing_final_actions",
            ),
            SourceRequirement(
                "services/backend/tests/test_cli.py",
                "test_cli_final_launch_closure_packet_writes_report_and_returns_result_code",
            ),
            SourceRequirement(
                "services/backend/tests/test_final_demo_launch.py",
                "test_final_demo_launch_embeds_final_launch_closure_packet",
            ),
        ),
    ),
    FeatureRequirement(
        id="mobile_final_launch_closure_packet",
        label="Mobile final launch closure packet",
        requirements=(
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "FinalLaunchClosurePacketReport",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "FinalLaunchClosurePacketBlocker",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "firstBlocker: FinalLaunchClosurePacketBlocker?",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift",
                "finalLaunchClosurePacket",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "closurePacketRows",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "closurePacketFirstBlockerRow",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift",
                "closurePacketRows && from: report.finalLaunchClosurePacket",
                (
                    "closurePacketRows",
                    "from: report.finalLaunchClosurePacket",
                ),
            ),
            SourceRequirement(
                "apps/mobile/ios/App/FinalLaunchStatusView.swift",
                "Closure Packet",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testDecodesFinalLaunchClosurePacketFromFinalLaunchPayload",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryShowsFinalLaunchClosurePacket",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryRedactsUnsafeFinalLaunchClosurePacket",
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
            SourceRequirement("apps/mobile/ios/App/Info.plist", "NSLocalNetworkUsageDescription"),
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
        requirement_evidence = _requirement_evidence(requirement)
        if _matches_requirement(root / requirement.file, requirement):
            evidence.append(f"{requirement.file}::{requirement_evidence}")
        else:
            missing.append({"file": requirement.file, "contains": requirement_evidence})
    return {
        "id": feature.id,
        "label": feature.label,
        "status": "passed" if not missing else "failed",
        "evidence": evidence,
        "missing": missing,
    }


def _matches_requirement(path: Path, requirement: SourceRequirement) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return False
    if requirement.all_contains:
        return all(token in text for token in requirement.all_contains)
    return requirement.contains in text


def _requirement_evidence(requirement: SourceRequirement) -> str:
    if requirement.all_contains:
        return " && ".join(requirement.all_contains)
    return requirement.contains


def _sanitize_report(report: dict[str, Any]) -> dict[str, Any]:
    text = json.dumps(report)
    if "/Users/" in text or "data:image" in text or "sk-" in text:
        raise ValueError("iOS showcase acceptance report contains unsafe text.")
    return report
