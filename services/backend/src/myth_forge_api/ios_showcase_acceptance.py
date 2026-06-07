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
        id="ios_deploy_runbook",
        label="iOS deploy runbook",
        requirements=(
            SourceRequirement(
                "services/backend/src/myth_forge_api/ios_deploy_runbook.py",
                "build_ios_deploy_runbook_report",
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
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_demo_launch.py",
                "ios_deploy_runbook",
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
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testDecodesIOSDeployRunbookFromFinalLaunchPayload",
            ),
            SourceRequirement(
                "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
                "testFinalLaunchMobileSummaryShowsPartialIOSDeployRunbook",
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
                "services/backend/src/myth_forge_api/final_operator_handoff.py",
                "npc_agent_evaluation",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/final_operator_handoff.py",
                "LOCAL_NPC_EVALUATION_COMMAND",
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
                "npc_evaluation",
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
                "testShowcaseAutopilotBlocksOnFailedNPCEvaluation",
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
