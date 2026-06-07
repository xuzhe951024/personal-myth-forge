import Foundation

do {
    let repositoryRoot = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
    let iosRoot = repositoryRoot.appendingPathComponent("apps/mobile/ios")
    let appRoot = iosRoot.appendingPathComponent("App")
    let coreRoot = iosRoot.appendingPathComponent("Sources/PersonalMythForgeMobileCore")
    let packageFile = iosRoot.appendingPathComponent("Package.swift")
    let projectFile = iosRoot.appendingPathComponent("PersonalMythForge.xcodeproj/project.pbxproj")
    let plistFile = appRoot.appendingPathComponent("Info.plist")
    let xcodeBuildGateScriptFile = iosRoot.appendingPathComponent("scripts/xcode_build_gate.sh")
    let deployPreflightScriptFile = iosRoot.appendingPathComponent("scripts/deploy_preflight.sh")
    let deployConfigWriterScriptFile = iosRoot.appendingPathComponent("scripts/write_deploy_local_config.sh")
    let backendEnvWriterScriptFile = repositoryRoot.appendingPathComponent(
        "services/backend/scripts/write_backend_env.sh"
    )
    let finalAcceptanceLocalScriptFile = repositoryRoot.appendingPathComponent(
        "services/backend/scripts/write_final_acceptance_local.sh"
    )
    let iosDeployRunbookLocalScriptFile = repositoryRoot.appendingPathComponent(
        "services/backend/scripts/write_ios_deploy_runbook_local.sh"
    )
    let deployConfigFile = iosRoot.appendingPathComponent("Config/Deployment.xcconfig")
    let deployLocalExampleFile = iosRoot.appendingPathComponent("Config/Deployment.local.xcconfig.example")
    let sharedSchemeFile = iosRoot.appendingPathComponent(
        "PersonalMythForge.xcodeproj/xcshareddata/xcschemes/PersonalMythForge.xcscheme"
    )
    let gitignoreFile = repositoryRoot.appendingPathComponent(".gitignore")
    let makefileFile = repositoryRoot.appendingPathComponent("Makefile")

    let packageManifest = try readText(packageFile)
    let project = try readText(projectFile)
    let plist = try readPropertyList(plistFile)
    let xcodeBuildGateScript = try readText(xcodeBuildGateScriptFile)
    let deployPreflightScript = try readText(deployPreflightScriptFile)
    let deployConfigWriterScript = try readText(deployConfigWriterScriptFile)
    let backendEnvWriterScript = try readText(backendEnvWriterScriptFile)
    let finalAcceptanceLocalScript = try readText(finalAcceptanceLocalScriptFile)
    let iosDeployRunbookLocalScript = try readText(iosDeployRunbookLocalScriptFile)
    let deployConfig = try readText(deployConfigFile)
    let deployLocalExample = try readText(deployLocalExampleFile)
    let sharedScheme = try readText(sharedSchemeFile)
    let gitignore = try readText(gitignoreFile)
    let makefile = try readText(makefileFile)
    let appConfiguration = try readText(appRoot.appendingPathComponent("AppConfiguration.swift"))
    let captureFormView = try readText(appRoot.appendingPathComponent("CaptureFormView.swift"))
    let captureGenerationReceiptView = try readText(appRoot.appendingPathComponent("CaptureGenerationReceiptView.swift"))
    let forgeProgressReceiptView = try readText(appRoot.appendingPathComponent("ForgeProgressReceiptView.swift"))
    let liveProviderConsentView = try readText(appRoot.appendingPathComponent("LiveProviderConsentView.swift"))
    let printFulfillmentReceiptView = try readText(appRoot.appendingPathComponent("PrintFulfillmentReceiptView.swift"))
    let threeDGenerationInputReviewView = try readText(
        appRoot.appendingPathComponent("ThreeDGenerationInputReviewView.swift")
    )
    let generationResultReceiptView = try readText(
        appRoot.appendingPathComponent("GenerationResultReceiptView.swift")
    )
    let forgeRootView = try readText(appRoot.appendingPathComponent("ForgeRootView.swift"))
    let artifactSummaryView = try readText(appRoot.appendingPathComponent("ArtifactSummaryView.swift"))
    let artifact3DPreviewView = try readText(appRoot.appendingPathComponent("Artifact3DPreviewView.swift"))
    let artifactHandoffActionsView = try readText(appRoot.appendingPathComponent("ArtifactHandoffActionsView.swift"))
    let guidedScanCaptureView = try readText(appRoot.appendingPathComponent("GuidedScanCaptureView.swift"))
    let providerReadinessView = try readText(appRoot.appendingPathComponent("ProviderReadinessView.swift"))
    let npcReactionsView = try readText(appRoot.appendingPathComponent("NPCReactionsView.swift"))
    let npcTickView = try readText(appRoot.appendingPathComponent("NPCTickView.swift"))
    let npcAgentModeView = try readText(appRoot.appendingPathComponent("NPCAgentModeView.swift"))
    let demoSnapshotStatusView = try readText(appRoot.appendingPathComponent("DemoSnapshotStatusView.swift"))
    let printQuoteReviewView = try readText(appRoot.appendingPathComponent("PrintQuoteReviewView.swift"))
    let finalShowcaseSummaryView = try readText(appRoot.appendingPathComponent("FinalShowcaseSummaryView.swift"))
    let devicePreflightView = try readText(appRoot.appendingPathComponent("DevicePreflightView.swift"))
    let finalLaunchStatusView = try readText(appRoot.appendingPathComponent("FinalLaunchStatusView.swift"))
    let contextCapsuleReviewView = try readText(appRoot.appendingPathComponent("ContextCapsuleReviewView.swift"))
    let demoScriptView = try readText(appRoot.appendingPathComponent("DemoScriptView.swift"))
    let cameraCaptureView = try readText(appRoot.appendingPathComponent("CameraCaptureView.swift"))
    let pmfModels = try readText(coreRoot.appendingPathComponent("PMFModels.swift"))
    let mythSessionID = try readText(coreRoot.appendingPathComponent("MythSessionID.swift"))
    let demoRunSnapshot = try readText(coreRoot.appendingPathComponent("DemoRunSnapshot.swift"))
    let artifactAssetPreparation = try readText(coreRoot.appendingPathComponent("ArtifactAssetPreparation.swift"))
    let artifactGenerationProvenanceSummary = try readText(
        coreRoot.appendingPathComponent("ArtifactGenerationProvenanceSummary.swift")
    )
    let artifactHandoffActions = try readText(coreRoot.appendingPathComponent("ArtifactHandoffActions.swift"))
    let npcAgentModeSummary = try readText(coreRoot.appendingPathComponent("NPCAgentModeSummary.swift"))
    let npcAgentTickSummary = try readText(coreRoot.appendingPathComponent("NPCAgentTickSummary.swift"))
    let npcRitualScene = try readText(coreRoot.appendingPathComponent("NPCRitualScene.swift"))
    let demoScript = try readText(coreRoot.appendingPathComponent("DemoScript.swift"))
    let showcaseAutopilot = try readText(coreRoot.appendingPathComponent("ShowcaseAutopilot.swift"))
    let devicePreflight = try readText(coreRoot.appendingPathComponent("DevicePreflight.swift"))
    let finalShowcaseSummary = try readText(coreRoot.appendingPathComponent("FinalShowcaseSummary.swift"))
    let finalLaunchMobileSummary = try readText(
        coreRoot.appendingPathComponent("FinalLaunchMobileSummary.swift")
    )
    let liveProviderConsentSummary = try readText(
        coreRoot.appendingPathComponent("LiveProviderConsentSummary.swift")
    )
    let contextCapsuleReview = try readText(coreRoot.appendingPathComponent("ContextCapsuleReview.swift"))
    let forgeReadinessSummary = try readText(coreRoot.appendingPathComponent("ForgeReadinessSummary.swift"))
    let guidedScanPhotoSetBuilder = try readText(coreRoot.appendingPathComponent("GuidedScanPhotoSetBuilder.swift"))
    let arkitScanPackageBuilder = try readText(coreRoot.appendingPathComponent("ARKitScanPackageBuilder.swift"))
    let captureGenerationReadiness = try readText(
        coreRoot.appendingPathComponent("CaptureGenerationReadiness.swift")
    )
    let threeDGenerationInputReview = try readText(
        coreRoot.appendingPathComponent("ThreeDGenerationInputReview.swift")
    )
    let generationResultReceipt = try readText(coreRoot.appendingPathComponent("GenerationResultReceipt.swift"))
    let captureGenerationReceipt = try readText(
        coreRoot.appendingPathComponent("CaptureGenerationReceipt.swift")
    )
    let forgeProgressReceipt = try readText(coreRoot.appendingPathComponent("ForgeProgressReceipt.swift"))
    let printFulfillmentReceipt = try readText(coreRoot.appendingPathComponent("PrintFulfillmentReceipt.swift"))
    let apiClient = try readText(coreRoot.appendingPathComponent("PersonalMythForgeAPIClient.swift"))
    let contractTests = try readText(
        iosRoot.appendingPathComponent("Sources/PersonalMythForgeMobileCoreContractTests/main.swift")
    )
    let finalOperatorHandoff = try readText(
        repositoryRoot.appendingPathComponent("services/backend/src/myth_forge_api/final_operator_handoff.py")
    )
    let finalAcceptanceReadiness = try readText(
        repositoryRoot.appendingPathComponent("services/backend/src/myth_forge_api/final_acceptance_readiness.py")
    )
    let finalDemoLaunch = try readText(
        repositoryRoot.appendingPathComponent("services/backend/src/myth_forge_api/final_demo_launch.py")
    )
    let finalDemoLaunchTests = try readText(
        repositoryRoot.appendingPathComponent("services/backend/tests/test_final_demo_launch.py")
    )
    let threeDEvaluationReadiness = try readText(
        repositoryRoot.appendingPathComponent("services/backend/src/myth_forge_api/three_d_evaluation_readiness.py")
    )
    let threeDEvaluationReadinessTests = try readText(
        repositoryRoot.appendingPathComponent("services/backend/tests/test_three_d_evaluation_readiness.py")
    )
    let npcAgentEvaluationReadiness = try readText(
        repositoryRoot.appendingPathComponent("services/backend/src/myth_forge_api/npc_agent_evaluation_readiness.py")
    )
    let evaluationMakeTargetsTests = try readText(
        repositoryRoot.appendingPathComponent("services/backend/tests/test_evaluation_make_targets.py")
    )
    let iosDeployRunbook = try readText(
        repositoryRoot.appendingPathComponent("services/backend/src/myth_forge_api/ios_deploy_runbook.py")
    )
    let iosDeployRunbookTests = try readText(
        repositoryRoot.appendingPathComponent("services/backend/tests/test_ios_deploy_runbook.py")
    )
    let finalRehearsalScriptsTests = try readText(
        repositoryRoot.appendingPathComponent("services/backend/tests/test_final_rehearsal_scripts.py")
    )

    try requireContains(packageManifest, ".iOS(.v17)", "Swift package iOS platform")
    try requireContains(packageManifest, ".macOS(.v13)", "Swift package macOS test platform")
    try requireContains(
        packageManifest,
        "PersonalMythForgeMobileAppCompileCheck",
        "SwiftPM app compile product"
    )
    try requireContains(packageManifest, #"path: "App""#, "SwiftPM app compile target path")
    try requireContains(
        packageManifest,
        #"exclude: ["Info.plist"]"#,
        "SwiftPM app compile target plist exclusion"
    )
    try requireContains(
        packageManifest,
        #"dependencies: ["PersonalMythForgeMobileCore"]"#,
        "SwiftPM app compile target core dependency"
    )
    try requireContains(project, "PersonalMythForge", "Xcode project target name")
    try requireContains(project, #"productType = "com.apple.product-type.application""#, "iOS app product type")
    try requireContains(project, "IPHONEOS_DEPLOYMENT_TARGET = 17.0", "iOS deployment target")
    try requireContains(project, "INFOPLIST_FILE = App/Info.plist", "Info.plist build setting")
    try requireContains(project, "XCLocalSwiftPackageReference", "local Swift package reference")
    try requireContains(project, "relativePath = .", "local package relative path")
    try requireContains(project, "XCSwiftPackageProductDependency", "Swift package product dependency")
    try requireContains(project, "productName = PersonalMythForgeMobileCore", "core package product dependency")
    try requireContains(project, "packageProductDependencies", "target package dependency list")
    try requireContains(project, "PersonalMythForgeMobileCore in Frameworks", "linked core product")
    try requireContains(gitignore, "apps/mobile/ios/Config/Deployment.local.xcconfig", "ignored local iOS deployment config")
    try requireContains(deployConfig, "PRODUCT_BUNDLE_IDENTIFIER = com.personalmythforge.app", "deployment bundle id default")
    try requireContains(deployConfig, "DEVELOPMENT_TEAM =", "deployment team slot")
    try requireContains(deployConfig, "CODE_SIGN_STYLE = Automatic", "automatic signing style")
    try requireContains(deployConfig, "PMF_BACKEND_BASE_URL = http://127.0.0.1:8080", "local backend default")
    try requireContains(deployConfig, "PMF_FINAL_LAUNCH_MODE = local", "final launch mode default")
    try requireContains(deployConfig, #"#include? "Deployment.local.xcconfig""#, "optional local deployment include")
    try requireContains(deployLocalExample, "DEVELOPMENT_TEAM = YOUR_TEAM_ID", "local deployment team example")
    try requireContains(deployLocalExample, "PRODUCT_BUNDLE_IDENTIFIER = com.example.personalmythforge", "local bundle id example")
    try requireContains(deployLocalExample, "PMF_BACKEND_BASE_URL = http://192.168.1.10:8080", "device backend URL example")
    try requireContains(deployLocalExample, "PMF_FINAL_LAUNCH_MODE = local", "local final launch mode example")
    try requireContains(project, "Deployment.xcconfig", "deployment xcconfig project reference")
    try requireContains(project, "baseConfigurationReference = 10B000000000000000000301", "target deployment base configuration")
    try requireNotContains(project, "DEVELOPMENT_TEAM = \"\";", "empty team in target build settings")
    try requireNotContains(project, "PRODUCT_BUNDLE_IDENTIFIER = com.personalmythforge.app;", "inline bundle id in target build settings")
    try requireContains(xcodeBuildGateScript, "DEVELOPER_DIR", "Xcode gate per-command developer dir")
    try requireContains(
        xcodeBuildGateScript,
        "/Applications/Xcode.app/Contents/Developer",
        "Xcode gate default developer dir"
    )
    try requireContains(xcodeBuildGateScript, "xcodebuild", "Xcode gate command")
    try requireContains(xcodeBuildGateScript, "-project", "Xcode gate project argument")
    try requireContains(xcodeBuildGateScript, "PersonalMythForge.xcodeproj", "Xcode gate project path")
    try requireContains(xcodeBuildGateScript, "-scheme", "Xcode gate scheme argument")
    try requireContains(xcodeBuildGateScript, "PersonalMythForge", "Xcode gate scheme name")
    try requireContains(xcodeBuildGateScript, "generic/platform=iOS", "Xcode gate generic iOS destination")
    try requireContains(xcodeBuildGateScript, "-derivedDataPath", "Xcode gate derived data argument")
    try requireContains(xcodeBuildGateScript, ".build/xcode-derived-data", "Xcode gate local derived data")
    try requireContains(xcodeBuildGateScript, "CODE_SIGNING_ALLOWED=NO", "Xcode gate signing disabled")
    try requireContains(
        xcodeBuildGateScript,
        "CODE_SIGNING_REQUIRED=NO",
        "Xcode gate signing requirement disabled"
    )
    try requireContains(xcodeBuildGateScript, #"exec "$XCODEBUILD""#, "Xcode gate calls configured xcodebuild")
    try requireNotContains(xcodeBuildGateScript, "xcode-select", "Xcode gate global developer dir mutation")
    try requireContains(deployPreflightScript, "Deployment.local.xcconfig", "deploy preflight local config")
    try requireContains(deployPreflightScript, "DEVELOPMENT_TEAM", "deploy preflight team check")
    try requireContains(deployPreflightScript, "PRODUCT_BUNDLE_IDENTIFIER", "deploy preflight bundle check")
    try requireContains(deployPreflightScript, "PMF_BACKEND_BASE_URL", "deploy preflight backend URL check")
    try requireContains(deployPreflightScript, "PMF_FINAL_LAUNCH_MODE", "deploy preflight final launch mode check")
    try requireContains(deployPreflightScript, "local|configured", "deploy preflight final launch mode allowlist")
    try requireContains(deployPreflightScript, "Final launch mode:", "deploy preflight final launch mode output")
    try requireContains(deployPreflightScript, "127.0.0.1", "deploy preflight loopback guard")
    try requireContains(deployPreflightScript, "/health", "deploy preflight backend health endpoint")
    try requireContains(deployPreflightScript, "urllib.request", "deploy preflight python health request")
    try requireContains(deployPreflightScript, "curl", "deploy preflight curl health fallback")
    try requireContains(deployPreflightScript, "timeout=3", "deploy preflight python timeout")
    try requireContains(deployPreflightScript, "--max-time 3", "deploy preflight curl timeout")
    try requireContains(deployPreflightScript, "Backend health: ok", "deploy preflight health success output")
    try requireNotContains(deployPreflightScript, "sudo", "deploy preflight no sudo")
    try requireNotContains(deployPreflightScript, "xcode-select", "deploy preflight no global developer mutation")
    try requireNotContains(deployPreflightScript, "xcodebuild -license", "deploy preflight no license mutation")
    try requireContains(
        sharedScheme,
        #"BlueprintIdentifier = "10E000000000000000000001""#,
        "shared Xcode scheme target identifier"
    )
    try requireContains(sharedScheme, #"BlueprintName = "PersonalMythForge""#, "shared Xcode scheme app target")
    try requireContains(sharedScheme, #"BuildableName = "PersonalMythForge.app""#, "shared Xcode scheme buildable app")
    try requireContains(
        sharedScheme,
        #"ReferencedContainer = "container:PersonalMythForge.xcodeproj""#,
        "shared Xcode scheme container"
    )
    try requireContains(makefile, ".PHONY: mobile-xcode-build", "mobile Xcode Make phony target")
    try requireContains(makefile, "mobile-xcode-build:", "mobile Xcode Make target")
    try requireContains(
        makefile,
        "apps/mobile/ios/scripts/xcode_build_gate.sh",
        "mobile Xcode Make target script"
    )
    try requireContains(makefile, ".PHONY: mobile-deploy-preflight", "mobile deploy preflight phony target")
    try requireContains(makefile, "mobile-deploy-preflight:", "mobile deploy preflight target")
    try requireContains(
        makefile,
        "apps/mobile/ios/scripts/deploy_preflight.sh",
        "mobile deploy preflight script"
    )
    try requireContains(makefile, ".PHONY: mobile-write-deploy-config", "mobile deploy config writer phony target")
    try requireContains(makefile, "mobile-write-deploy-config:", "mobile deploy config writer target")
    try requireContains(
        makefile,
        "apps/mobile/ios/scripts/write_deploy_local_config.sh",
        "mobile deploy config writer script"
    )
    try requireContains(makefile, ".PHONY: backend-write-provider-env", "backend provider env writer phony target")
    try requireContains(makefile, "backend-write-provider-env:", "backend provider env writer target")
    try requireContains(
        makefile,
        "services/backend/scripts/write_backend_env.sh",
        "backend provider env writer script"
    )
    try requireContains(makefile, ".PHONY: ios-deploy-runbook", "iOS deploy runbook Make phony target")
    try requireContains(makefile, "ios-deploy-runbook:", "iOS deploy runbook Make target")
    try requireContains(makefile, "ios-deploy-runbook-local:", "iOS deploy runbook local wrapper target")
    try requireContains(makefile, "myth_forge_api.cli ios-deploy-runbook", "iOS deploy runbook CLI target")
    try requireContains(
        makefile,
        "services/backend/scripts/write_ios_deploy_runbook_local.sh",
        "iOS deploy runbook local wrapper script"
    )
    try requireContains(makefile, "final-acceptance-local:", "final acceptance local wrapper target")
    try requireContains(
        makefile,
        "services/backend/scripts/write_final_acceptance_local.sh",
        "final acceptance local wrapper script"
    )
    try requireContains(
        makefile,
        "final-rehearsal-local: backend-evaluate-local final-acceptance-local final-demo-launch ios-deploy-runbook-local",
        "final rehearsal local target order"
    )
    try requireContains(makefile, "backend-evaluate-3d:", "backend 3D evaluation Make target")
    try requireContains(makefile, "backend-evaluate-npc:", "backend NPC evaluation Make target")
    try requireContains(makefile, "backend-evaluate-local:", "combined backend local evaluation Make target")
    try requireContains(makefile, "--output .local/3d-evaluation-local.json", "3D evaluation local report output")
    try requireContains(makefile, "--output .local/npc-evaluation-local.json", "NPC evaluation local report output")
    try requireContains(makefile, "--output .local/final-demo-launch-local.json", "final demo launch local report output")
    try requireContains(finalAcceptanceLocalScript, "accepted final acceptance exit code $status", "final acceptance local accepts blocked report")
    try requireContains(finalAcceptanceLocalScript, "services/backend/.local/final-acceptance-local.json", "final acceptance local report path")
    try requireContains(iosDeployRunbookLocalScript, "accepted iOS deploy runbook exit code $status", "iOS deploy runbook local accepts blocked report")
    try requireContains(iosDeployRunbookLocalScript, "services/backend/.local/ios-deploy-runbook-local.json", "iOS deploy runbook local report path")
    try requireNotContains(finalAcceptanceLocalScript, "sudo", "final acceptance local wrapper no sudo")
    try requireNotContains(iosDeployRunbookLocalScript, "sudo", "iOS deploy runbook local wrapper no sudo")
    try requireContains(
        finalAcceptanceReadiness,
        #"LOCAL_FINAL_ACCEPTANCE_COMMAND = "make final-acceptance-local""#,
        "final acceptance readiness canonical Make target"
    )
    try requireContains(
        iosDeployRunbook,
        "LOCAL_FINAL_ACCEPTANCE_COMMAND",
        "iOS deploy runbook uses canonical final acceptance command"
    )
    try requireContains(
        finalDemoLaunch,
        "LOCAL_FINAL_ACCEPTANCE_COMMAND",
        "final demo launch uses canonical final acceptance command"
    )
    try requireContains(
        finalRehearsalScriptsTests,
        "test_final_rehearsal_make_targets_dry_run_expected_order",
        "final rehearsal Make target order test"
    )
    try requireContains(deployConfigWriterScript, "DEVELOPMENT_TEAM", "deploy config writer team key")
    try requireContains(deployConfigWriterScript, "PRODUCT_BUNDLE_IDENTIFIER", "deploy config writer bundle key")
    try requireContains(deployConfigWriterScript, "PMF_BACKEND_BASE_URL", "deploy config writer backend key")
    try requireContains(
        deployConfigWriterScript,
        "Deployment.local.xcconfig must stay untracked.",
        "deploy config writer tracked local config guard"
    )
    try requireContains(deployConfigWriterScript, "chmod 600", "deploy config writer local file mode")
    try requireNotContains(deployConfigWriterScript, "sudo", "deploy config writer no sudo")
    try requireNotContains(deployConfigWriterScript, "xcode-select", "deploy config writer no global developer mutation")
    try requireNotContains(deployConfigWriterScript, "xcodebuild -license", "deploy config writer no license mutation")
    try requireNotContains(deployConfigWriterScript, "security ", "deploy config writer no keychain mutation")
    try requireNotContains(deployConfigWriterScript, "codesign", "deploy config writer no signing")
    try requireNotContains(deployConfigWriterScript, "api.openai.com", "deploy config writer no OpenAI call")
    try requireNotContains(deployConfigWriterScript, "api.meshy.ai", "deploy config writer no Meshy call")
    try requireContains(backendEnvWriterScript, "MESHY_API_KEY", "backend env writer Meshy key")
    try requireContains(backendEnvWriterScript, "OPENAI_API_KEY", "backend env writer OpenAI key")
    try requireContains(backendEnvWriterScript, "THREE_D_PROVIDER=meshy", "backend env writer Meshy provider selection")
    try requireContains(backendEnvWriterScript, "NPC_PROVIDER=openai", "backend env writer OpenAI NPC selection")
    try requireContains(backendEnvWriterScript, "configured (redacted)", "backend env writer redaction")
    try requireContains(
        backendEnvWriterScript,
        "services/backend/.env must stay untracked",
        "backend env writer tracked env guard"
    )
    try requireContains(backendEnvWriterScript, "chmod 600", "backend env writer local file mode")
    try requireNotContains(backendEnvWriterScript, "curl ", "backend env writer no provider network call")
    try requireNotContains(
        backendEnvWriterScript,
        "urllib.request",
        "backend env writer no Python provider network call"
    )
    try requireNotContains(backendEnvWriterScript, "sudo", "backend env writer no sudo")
    try requireNotContains(backendEnvWriterScript, "xcode-select", "backend env writer no global developer mutation")
    try requireNotContains(backendEnvWriterScript, "xcodebuild -license", "backend env writer no license mutation")
    try requireNotContains(backendEnvWriterScript, "security ", "backend env writer no keychain mutation")
    try requireNotContains(backendEnvWriterScript, "codesign", "backend env writer no signing")

    for file in [
        "AppConfiguration.swift",
        "PersonalMythForgeApp.swift",
        "ForgeRootView.swift",
        "CaptureFormView.swift",
        "CaptureGenerationReceiptView.swift",
        "ForgeProgressReceiptView.swift",
        "LiveProviderConsentView.swift",
        "PrintFulfillmentReceiptView.swift",
        "ThreeDGenerationInputReviewView.swift",
        "GenerationResultReceiptView.swift",
        "ArtifactSummaryView.swift",
        "Artifact3DPreviewView.swift",
        "GuidedScanCaptureView.swift",
        "ProviderReadinessView.swift",
        "WorldResolutionView.swift",
        "NPCReactionsView.swift",
        "NPCTickView.swift",
        "DemoSnapshotStatusView.swift",
        "PrintQuoteReviewView.swift",
        "FinalShowcaseSummaryView.swift",
        "DevicePreflightView.swift",
        "FinalLaunchStatusView.swift",
        "ContextCapsuleReviewView.swift",
        "CameraCaptureView.swift",
    ] {
        try requireContains(project, file, "Xcode project file reference")
    }
    try requirePBXSectionContains(
        project,
        sectionName: "PBXSourcesBuildPhase",
        "10A000000000000000000008 /* Artifact3DPreviewView.swift in Sources */,",
        "3D preview Xcode source membership"
    )
    try requirePBXSectionContains(
        project,
        sectionName: "PBXSourcesBuildPhase",
        "10A000000000000000000009 /* GuidedScanCaptureView.swift in Sources */,",
        "guided scan Xcode source membership"
    )
    try requirePBXSectionContains(
        project,
        sectionName: "PBXSourcesBuildPhase",
        "10A000000000000000000010 /* ProviderReadinessView.swift in Sources */,",
        "provider readiness Xcode source membership"
    )
    try requirePBXSectionContains(
        project,
        sectionName: "PBXSourcesBuildPhase",
        "10A000000000000000000011 /* NPCTickView.swift in Sources */,",
        "npc tick Xcode source membership"
    )
    try requirePBXSectionContains(
        project,
        sectionName: "PBXSourcesBuildPhase",
        "10A000000000000000000012 /* DemoSnapshotStatusView.swift in Sources */,",
        "demo snapshot status Xcode source membership"
    )
    try requirePBXSectionContains(
        project,
        sectionName: "PBXSourcesBuildPhase",
        "10A000000000000000000013 /* PrintQuoteReviewView.swift in Sources */,",
        "print quote review Xcode source membership"
    )
    try requirePBXSectionContains(
        project,
        sectionName: "PBXSourcesBuildPhase",
        "10A000000000000000000014 /* FinalShowcaseSummaryView.swift in Sources */,",
        "final showcase summary Xcode source membership"
    )
    try requirePBXSectionContains(
        project,
        sectionName: "PBXSourcesBuildPhase",
        "10A000000000000000000015 /* CameraCaptureView.swift in Sources */,",
        "camera capture Xcode source membership"
    )
    try requirePBXSectionContains(
        project,
        sectionName: "PBXSourcesBuildPhase",
        "10A000000000000000000017 /* DevicePreflightView.swift in Sources */,",
        "device preflight Xcode source membership"
    )
    try requirePBXSectionContains(
        project,
        sectionName: "PBXSourcesBuildPhase",
        "10A000000000000000000018 /* FinalLaunchStatusView.swift in Sources */,",
        "final launch status Xcode source membership"
    )
    try requirePBXSectionContains(
        project,
        sectionName: "PBXSourcesBuildPhase",
        "10A000000000000000000019 /* ContextCapsuleReviewView.swift in Sources */,",
        "context capsule review Xcode source membership"
    )
    try requirePBXSectionContains(
        project,
        sectionName: "PBXSourcesBuildPhase",
        "10A000000000000000000022 /* CaptureGenerationReceiptView.swift in Sources */,",
        "capture generation receipt Xcode source membership"
    )
    try requirePBXSectionContains(
        project,
        sectionName: "PBXSourcesBuildPhase",
        "10A000000000000000000023 /* ForgeProgressReceiptView.swift in Sources */,",
        "forge progress receipt Xcode source membership"
    )
    try requirePBXSectionContains(
        project,
        sectionName: "PBXSourcesBuildPhase",
        "10A000000000000000000024 /* LiveProviderConsentView.swift in Sources */,",
        "live provider consent Xcode source membership"
    )
    try requirePBXSectionContains(
        project,
        sectionName: "PBXSourcesBuildPhase",
        "10A000000000000000000025 /* PrintFulfillmentReceiptView.swift in Sources */,",
        "print fulfillment receipt Xcode source membership"
    )
    try requirePBXSectionContains(
        project,
        sectionName: "PBXSourcesBuildPhase",
        "10A000000000000000000026 /* ThreeDGenerationInputReviewView.swift in Sources */,",
        "3D generation input review Xcode source membership"
    )
    try requirePBXSectionContains(
        project,
        sectionName: "PBXSourcesBuildPhase",
        "10A000000000000000000027 /* GenerationResultReceiptView.swift in Sources */,",
        "3D generation result receipt Xcode source membership"
    )
    for file in [
        "PMFJSON.swift",
        "PMFModels.swift",
        "CaptureID.swift",
        "MultipartFormDataBuilder.swift",
        "PersonalMythForgeAPIClient.swift",
        "ForgeFlowReducer.swift",
    ] {
        try requireNotContains(project, "\(file) in Sources", "core source compiled directly into app target")
    }

    try requirePlistString(plist, key: "CFBundleDisplayName", expected: "Personal Myth Forge")
    try requirePlistString(plist, key: "CFBundleIdentifier", expected: "$(PRODUCT_BUNDLE_IDENTIFIER)")
    try requirePlistString(plist, key: "PMFBackendBaseURL", expected: "$(PMF_BACKEND_BASE_URL)")
    try requirePlistString(plist, key: "PMFFinalLaunchMode", expected: "$(PMF_FINAL_LAUNCH_MODE)")
    try requirePlistText(plist, key: "NSCameraUsageDescription")
    try requirePlistText(plist, key: "NSPhotoLibraryUsageDescription")
    try requirePlistText(plist, key: "NSPhotoLibraryAddUsageDescription")
    try requirePlistText(plist, key: "NSLocalNetworkUsageDescription")
    try requireNestedPlistBool(
        plist,
        dictionaryKey: "NSAppTransportSecurity",
        key: "NSAllowsLocalNetworking",
        expected: true
    )
    try requireContains(captureFormView, "CaptureMode", "capture mode app shell source")
    try requireContains(captureFormView, "generationReadinessTitle", "capture generation readiness title")
    try requireContains(captureFormView, "generationReadinessRouteLabel", "capture generation readiness route label")
    try requireContains(captureFormView, "generationReadinessDetail", "capture generation readiness detail")
    try requireContains(
        captureFormView,
        "let generationInputReview: ThreeDGenerationInputReview",
        "capture form 3D generation input review input"
    )
    try requireContains(
        captureFormView,
        "ThreeDGenerationInputReviewView(review: generationInputReview)",
        "capture form 3D generation input review panel"
    )
    try requireContains(captureFormView, "isContextCapsuleApproved", "capture form context approval binding")
    try requireContains(captureFormView, "ContextCapsuleReviewView(", "capture form context review wiring")
    try requireContains(captureFormView, "Forge Readiness", "capture form forge readiness panel")
    try requireContains(
        captureFormView,
        "forgeReadinessSummary.routeLabel",
        "capture form forge readiness route display"
    )
    try requireContains(
        captureFormView,
        "forgeReadinessSummary.privacyNotes",
        "capture form forge readiness privacy notes"
    )
    try requireContains(captureFormView, "forgeActionGate.detail", "capture form forge action detail")
    try requireContains(captureFormView, "forgeActionGate.isEnabled", "capture form forge action gate")
    try requireContains(
        captureFormView,
        "let forgeActionGate: ForgeActionGate",
        "capture form forge action gate input"
    )
    try requireContains(
        captureFormView,
        "let forgeProgressReceipt: ForgeProgressReceipt",
        "capture form forge progress receipt input"
    )
    try requireContains(
        captureFormView,
        "ForgeProgressReceiptView(receipt: forgeProgressReceipt)",
        "capture form forge progress receipt view"
    )
    try requireContains(captureFormView, "chooseCapture", "capture button closure")
    try requireContains(captureFormView, "let takePhoto: () -> Void", "camera action form input")
    try requireContains(captureFormView, "Take Photo", "single photo camera action")
    try requireContains(captureFormView, "startGuidedScan", "guided scan button closure")
    try requireContains(captureFormView, "forgeMyth", "forge button closure")
    try requireContains(captureFormView, "PhotosPicker", "photo picker app shell source")
    try requireContains(captureFormView, "Start Guided Scan", "guided scan primary action")
    try requireContains(captureFormView, "Guided scan", "guided scan mode label")
    try requireContains(captureFormView, "let isMediaReadyForUpload", "media readiness form input")
    try requireContains(
        captureFormView,
        ".disabled(!forgeActionGate.isEnabled)",
        "disabled forge button source"
    )
    try requireContains(
        captureFormView,
        "mobileTextInputAutocapitalizationDisabled()",
        "portable text input capitalization helper use"
    )
    try requireContains(captureFormView, "#if os(iOS)", "iOS-only text input capitalization guard")
    try requireNotContains(
        captureFormView,
        "TextField(\"Object label\", text: $objectLabel)\n                .textInputAutocapitalization(.never)",
        "direct object label iOS-only text input modifier"
    )
    try requireNotContains(
        captureFormView,
        "TextField(\"Materials\", text: $materials)\n                .textInputAutocapitalization(.never)",
        "direct materials iOS-only text input modifier"
    )
    try requireNotContains(captureFormView, "Future Xcode target wires", "capture button no-op comment")
    try requireNotContains(captureFormView, "Future Xcode target triggers", "forge button no-op comment")
    try requireNotContains(captureFormView, "captureActionTitle", "unused sample-era capture title")
    try requireContains(forgeRootView, "selectedCaptureMode", "capture mode root state")
    try requireContains(forgeRootView, "isContextCapsuleApproved", "context capsule approval state")
    try requireContains(forgeRootView, "ContextCapsuleReviewBuilder.build", "context capsule review builder wiring")
    try requireContains(forgeRootView, "forgeReadinessSummary", "forge readiness root summary property")
    try requireContains(
        forgeRootView,
        "ForgeReadinessSummaryBuilder.build",
        "forge readiness root builder wiring"
    )
    try requireContains(
        forgeRootView,
        "forgeReadinessSummary: forgeReadinessSummary",
        "forge readiness capture form handoff"
    )
    try requireContains(forgeRootView, "forgeActionGate", "forge action gate root property")
    try requireContains(
        forgeRootView,
        "ForgeActionGateBuilder.build",
        "forge action gate root builder wiring"
    )
    try requireContains(
        forgeRootView,
        "forgeActionGate: forgeActionGate",
        "forge action gate capture form handoff"
    )
    try requireContains(
        forgeRootView,
        "forgeProgressReceipt: forgeProgressReceipt",
        "forge progress receipt capture form handoff"
    )
    try requireContains(
        forgeRootView,
        "private var forgeProgressReceipt: ForgeProgressReceipt",
        "forge progress root property"
    )
    try requireContains(
        forgeRootView,
        "ForgeProgressReceiptBuilder.build",
        "forge progress builder wiring"
    )
    try requireContains(forgeRootView, "isContextCapsuleApproved = false", "context approval reset")
    try requireContains(forgeRootView, "guard isContextCapsuleApproved else", "forge context approval guard")
    try requireContains(forgeRootView, "isCameraCapturePresented", "camera sheet root state")
    try requireContains(forgeRootView, "CameraCaptureView(", "camera sheet root wiring")
    try requireContains(
        forgeRootView,
        "CameraCaptureMediaBuilder.singlePhotoSelection",
        "camera media builder wiring"
    )
    try requireContains(forgeRootView, "isGuidedScanPresented", "guided scan sheet state")
    try requireContains(forgeRootView, "providerReadiness", "provider readiness root state")
    try requireContains(forgeRootView, "latestNPCTick", "npc tick root state")
    try requireContains(forgeRootView, "printQuote", "print quote root state")
    try requireContains(forgeRootView, "isLoadingPrintQuote", "print quote loading state")
    try requireContains(forgeRootView, "printQuoteError", "print quote error state")
    try requireContains(forgeRootView, "isPrintQuoteApproved", "print quote approval root state")
    try requireContains(
        forgeRootView,
        "isPrintQuoteApproved = false",
        "print quote approval reset"
    )
    try requireContains(
        forgeRootView,
        "isPrintQuoteApproved = !quote.requiresUserApproval",
        "print quote approval default from quote"
    )
    try requireContains(
        forgeRootView,
        "fulfillmentReceipt: printFulfillmentReceipt",
        "print fulfillment receipt view handoff"
    )
    try requireContains(
        forgeRootView,
        "isPrintQuoteApproved: $isPrintQuoteApproved",
        "print fulfillment approval binding"
    )
    try requireContains(
        forgeRootView,
        "private var printFulfillmentReceipt: PrintFulfillmentReceipt",
        "print fulfillment root property"
    )
    try requireContains(
        forgeRootView,
        "PrintFulfillmentReceiptBuilder.build",
        "print fulfillment builder wiring"
    )
    try requireContains(forgeRootView, "FinalShowcaseSummaryView(", "final showcase summary view wiring")
    try requireContains(forgeRootView, "FinalShowcaseSummaryBuilder.build", "final showcase summary builder wiring")
    try requireContains(
        forgeRootView,
        "finalLaunchSummary: finalLaunchMobileSummary",
        "final showcase launch digest root wiring"
    )
    try requireContains(
        forgeRootView,
        "CaptureGenerationReadinessBuilder.build",
        "capture generation readiness root wiring"
    )
    try requireContains(
        forgeRootView,
        "captureGenerationReadiness.route.displayLabel",
        "capture generation readiness route label wiring"
    )
    try requireContains(
        forgeRootView,
        "generationInputReview: threeDGenerationInputReview",
        "3D generation input review capture form handoff"
    )
    try requireContains(
        forgeRootView,
        "private var threeDGenerationInputReview: ThreeDGenerationInputReview",
        "3D generation input review root property"
    )
    try requireContains(
        forgeRootView,
        "ThreeDGenerationInputReviewBuilder.build",
        "3D generation input review builder wiring"
    )
    try requireContains(
        forgeRootView,
        "CaptureGenerationReceiptView(receipt: captureGenerationReceipt)",
        "capture generation receipt view wiring"
    )
    try requireContains(
        forgeRootView,
        "private var captureGenerationReceipt: CaptureGenerationReceipt",
        "capture generation receipt root property"
    )
    try requireContains(
        forgeRootView,
        "capture: state.capture",
        "capture generation receipt uploaded capture wiring"
    )
    try requireContains(forgeRootView, "DevicePreflightSummaryBuilder.build", "device preflight summary wiring")
    try requireContains(forgeRootView, "DevicePreflightView(summary:", "device preflight view wiring")
    try requireContains(forgeRootView, "FinalLaunchStatusView(", "final launch status root wiring")
    try requireContains(
        forgeRootView,
        "FinalLaunchMobileSummaryBuilder.build",
        "final launch mobile summary root wiring"
    )
    try requireContains(
        forgeRootView,
        "LiveProviderConsentView(summary: liveProviderConsentSummary)",
        "live provider consent view wiring"
    )
    try requireContains(
        forgeRootView,
        "LiveProviderConsentSummaryBuilder.build",
        "live provider consent summary root wiring"
    )
    try requireContains(forgeRootView, "finalDemoLaunch", "final demo launch root state")
    try requireContains(forgeRootView, "finalLaunchMode", "final launch mode root state")
    try requireContains(forgeRootView, "Picker(\"Final launch mode\"", "final launch mode segmented control")
    try requireContains(forgeRootView, "FinalLaunchMode.allCases", "final launch mode options")
    try requireContains(forgeRootView, "loadFinalDemoLaunch", "final demo launch app load path")
    try requireContains(forgeRootView, "loadFinalDemoLaunch(mode: finalLaunchMode)", "configured launch load path")
    try requireContains(forgeRootView, "getFinalDemoLaunch(mode: mode.rawValue)", "final demo launch API call")
    try requireContains(forgeRootView, ".onChange(of: finalLaunchMode)", "final launch mode reload hook")
    try requireContains(forgeRootView, "backendHealthProbe", "backend health probe root state")
    try requireContains(forgeRootView, "isCheckingBackendHealth", "backend health loading state")
    try requireContains(forgeRootView, "getBackendHealth()", "backend health API call")
    try requireContains(forgeRootView, "checkBackendHealth", "backend health action")
    try requireBefore(
        forgeRootView,
        "FinalShowcaseSummaryView(",
        "ProviderReadinessView(",
        "final showcase summary before provider readiness"
    )
    try requireContains(forgeRootView, "PrintQuoteReviewView(", "print quote review view wiring")
    try requireContains(forgeRootView, "createPrintQuote", "print quote API call")
    try requireContains(forgeRootView, "clearPrintQuoteState", "stale print quote clearing")
    try requireContains(forgeRootView, "createNPCAgentTick", "npc tick API call")
    try requireContains(
        forgeRootView,
        "advanceBackendNPCTick",
        "server-owned npc tick app path"
    )
    try requireContains(
        forgeRootView,
        "advanceStatelessNPCTick",
        "stateless npc tick fallback app path"
    )
    try requireContains(
        forgeRootView,
        "advanceMythSessionHistory",
        "server-owned npc history API call"
    )
    try requireContains(
        forgeRootView,
        "applyBackendHistory(history)",
        "server-owned npc history application"
    )
    try requireContains(forgeRootView, "isRunningAutonomy", "autonomy run loading state")
    try requireContains(forgeRootView, "runAutonomy", "autonomy run app action")
    try requireContains(forgeRootView, "runMythSessionAutonomy", "autonomy run API call")
    try requireContains(
        forgeRootView,
        "applyBackendHistory(run.history)",
        "autonomy run history application"
    )
    try requireContains(forgeRootView, "ShowcaseAutopilotPlanner.plan", "showcase autopilot planner wiring")
    try requireContains(forgeRootView, "runShowcaseAutopilot", "showcase autopilot root action")
    try requireContains(
        forgeRootView,
        "switch showcaseAutopilotPlan.action",
        "showcase autopilot action dispatch"
    )
    try requireContains(
        forgeRootView,
        "finalLaunchSummary: finalLaunchMobileSummary",
        "demo script final launch summary wiring"
    )
    try requireContains(
        forgeRootView,
        "MythSessionID.isValid(session.sessionId)",
        "server-owned npc tick id guard"
    )
    try requireContains(forgeRootView, "NPCTickView(", "npc tick view wiring")
    try requireContains(
        forgeRootView,
        "ArtifactSummaryView(session: readySession, latestTick: latestNPCTick)",
        "npc ritual latest tick summary wiring"
    )
    try requireContains(forgeRootView, "demoSnapshotStore", "demo snapshot store app state")
    try requireContains(forgeRootView, "restoreDemoRunSnapshot", "demo snapshot restore app path")
    try requireContains(forgeRootView, "saveDemoRunSnapshot", "demo snapshot save app path")
    try requireContains(forgeRootView, "clearDemoRunSnapshot", "demo snapshot clear app path")
    try requireContains(forgeRootView, "npcTickHistory", "npc tick history app state")
    try requireContains(forgeRootView, "DemoSnapshotStatusView(", "demo snapshot status view wiring")
    try requireContains(forgeRootView, "isSyncingBackendHistory", "backend history sync loading state")
    try requireContains(forgeRootView, "backendHistoryStatusText", "backend history sync status text")
    try requireContains(forgeRootView, "syncBackendHistory", "backend history sync app path")
    try requireContains(forgeRootView, "getMythSessionHistory", "backend history GET call")
    try requireContains(forgeRootView, "applyBackendHistory", "backend history app state application")
    try requireContains(forgeRootView, "MythSessionID.isValid", "backend history id guard")
    try requireContains(
        forgeRootView,
        "Backend history not reachable; using local demo state.",
        "backend history fallback status"
    )
    try requireContains(forgeRootView, "ForgeFlowService", "forge flow service source wiring")
    try requireContains(forgeRootView, "forgeService.forge", "forge flow service call")
    try requireContains(forgeRootView, "getProviderReadiness()", "provider readiness API load")
    try requireContains(
        forgeRootView,
        "ProviderReadinessView(readiness:",
        "provider readiness view wiring"
    )
    try requireContains(forgeRootView, "fileImporter", "file importer app shell source")
    try requireContains(
        forgeRootView,
        ".sheet(isPresented: $isGuidedScanPresented)",
        "guided scan sheet presentation"
    )
    try requireContains(forgeRootView, "GuidedScanCaptureView(", "guided scan view wiring")
    try requireContains(forgeRootView, "loadGuidedScanDirectory", "guided scan directory loader")
    try requireContains(
        forgeRootView,
        "GuidedScanPhotoSetBuilder.mediaDrafts",
        "guided scan photo importer wiring"
    )
    try requireContains(forgeRootView, "arkitScanPackageSelection", "ARKit scan package bridge helper")
    try requireContains(
        forgeRootView,
        "ARKitScanPackageBuilder.selection",
        "app source references ARKit scan package builder"
    )
    try requireContains(
        forgeRootView,
        "ARKitScanExportFile(",
        "app source converts imported scan export"
    )
    try requireContains(
        forgeRootView,
        "ARKitScanReferenceImageFile(",
        "app source converts ARKit reference images"
    )
    try requireContains(forgeRootView, "loadTransferable(type: Data.self)", "photo data loading source")
    try requireContains(forgeRootView, "UTType", "file content type source")
    try requireContains(forgeRootView, "CaptureMediaSelection", "capture media selection source")
    try requireContains(forgeRootView, "switch selectedCaptureMode", "file importer selected mode source")
    try requireContains(forgeRootView, "guard selectedCaptureMode == mode else", "stale photo load guard")
    try requireContains(forgeRootView, "CaptureInputLoadError.unreadablePhoto", "partial photo load failure source")
    try requireContains(npcAgentTickSummary, #"autonomyTitle: "Run Autonomy""#, "autonomy run button label")
    try requireContains(npcTickView, "runAutonomy", "autonomy run button action")
    try requireContains(finalShowcaseSummaryView, "Final Showcase", "final showcase summary title")
    try requireContains(finalShowcaseSummaryView, "privacyNotes", "final showcase privacy note rendering")
    try requireContains(
        finalShowcaseSummary,
        "finalLaunchSummary: FinalLaunchMobileSummary?",
        "final showcase launch summary input"
    )
    try requireContains(finalShowcaseSummary, "npcEvaluationStage", "final showcase npc evaluation digest")
    try requireContains(finalShowcaseSummary, "threeDEvaluationStage", "final showcase 3D evaluation digest")
    try requireContains(finalShowcaseSummary, "operatorHandoffStage", "final showcase operator handoff digest")
    try requireContains(finalShowcaseSummary, "finalLaunchStage", "final showcase final launch digest")
    try requireContains(finalShowcaseSummary, #""three_d_evaluation""#, "final showcase 3D evaluation stage id")
    try requireContains(finalShowcaseSummary, #""npc_evaluation""#, "final showcase npc evaluation stage id")
    try requireContains(finalShowcaseSummary, #""operator_handoff""#, "final showcase handoff stage id")
    try requireContains(finalShowcaseSummary, #""final_launch""#, "final showcase launch stage id")
    try requireContains(
        contractTests,
        "testFinalShowcaseSummaryIncludesBlockedFinalLaunchDigest",
        "blocked final showcase launch digest contract test"
    )
    try requireContains(
        contractTests,
        "testFinalShowcaseSummaryIncludesReadyFinalLaunchDigest",
        "ready final showcase launch digest contract test"
    )
    try requireContains(
        contractTests,
        "testFinalShowcaseSummaryIncludesReadyThreeDEvaluationDigest",
        "ready 3D evaluation final showcase digest contract test"
    )
    try requireContains(
        contractTests,
        "testFinalShowcaseSummaryWaitsForMissingThreeDEvaluationDigest",
        "missing 3D evaluation final showcase digest contract test"
    )
    try requireContains(
        contractTests,
        "testFinalShowcaseSummaryWaitsForMissingNPCEvaluationDigest",
        "missing npc evaluation final showcase digest contract test"
    )
    try requireContains(
        contractTests,
        "testFinalShowcaseSummaryRedactsUnsafeThreeDEvaluationDigest",
        "redacted 3D evaluation final showcase digest contract test"
    )
    try requireContains(
        contractTests,
        "testFinalShowcaseSummaryRedactsUnsafeFinalLaunchDigest",
        "redacted final showcase launch digest contract test"
    )
    try requireContains(devicePreflightView, "Device Preflight", "device preflight title")
    try requireContains(devicePreflightView, "backendBaseURL", "device preflight backend URL")
    try requireContains(devicePreflightView, "checkBackend", "device preflight check action")
    try requireContains(devicePreflightView, "Check", "device preflight check button")
    try requireContains(finalLaunchStatusView, "Final Launch Status", "final launch status title")
    try requireContains(finalLaunchStatusView, "Mode", "final launch mode policy section")
    try requireContains(
        finalLaunchStatusView,
        "modePolicyRows",
        "final launch mode policy row rendering"
    )
    try requireContains(
        finalLaunchStatusView,
        "resourceActions",
        "final launch status resource action rendering"
    )
    try requireContains(finalLaunchStatusView, "Acceptance", "final launch acceptance section")
    try requireContains(
        finalLaunchStatusView,
        "acceptanceRows",
        "final launch acceptance row rendering"
    )
    try requireContains(finalLaunchStatusView, "iOS Deploy Runbook", "final launch iOS deploy runbook section")
    try requireContains(finalLaunchStatusView, "Deploy Commands", "final launch iOS deploy command section")
    try requireContains(finalLaunchStatusView, "Deploy Safety", "final launch iOS deploy safety section")
    try requireContains(finalLaunchStatusView, "Next", "final launch operator handoff section")
    try requireContains(
        finalLaunchStatusView,
        "handoffRows",
        "final launch operator handoff row rendering"
    )
    try requireContains(finalLaunchStatusView, "commandRows", "final launch status command rendering")
    try requireContains(contextCapsuleReviewView, "Context Capsule Review", "context capsule review title")
    try requireContains(contextCapsuleReviewView, "Approve Capsule", "context capsule approval toggle")
    try requireContains(contextCapsuleReviewView, "privacyNotes", "context capsule privacy notes")
    try requireContains(devicePreflight, "DevicePreflightSummaryBuilder", "device preflight core builder")
    try requireContains(devicePreflight, "BackendHealthProbe", "backend health probe core type")
    try requireContains(devicePreflight, "final_launch", "device preflight final launch item")
    try requireContains(devicePreflight, "final_resources", "device preflight final resources item")
    try requireContains(devicePreflight, "Final Resources", "device preflight final resources label")
    try requireContains(devicePreflight, "FinalDemoLaunchReport", "device preflight final launch model")
    try requireContains(devicePreflight, "Final launch readiness is read-only.", "device preflight final launch safety note")
    try requireContains(apiClient, "getBackendHealth", "backend health API client method")
    try requireContains(apiClient, "getFinalDemoLaunch", "final demo launch API client method")
    try requireContains(apiClient, "/v1/final-demo-launch", "final demo launch API endpoint")
    try requireContains(apiClient, "Unsupported final demo launch mode", "final launch mode guard")
    try requireContains(appConfiguration, "PMFFinalLaunchMode", "final launch mode plist lookup")
    try requireContains(appConfiguration, "FinalLaunchMode.safe", "safe final launch mode config")
    try requireContains(pmfModels, "FinalLaunchMode", "final launch mode model")
    try requireContains(pmfModels, "case configured", "configured final launch mode")
    try requireContains(pmfModels, "displayLabel", "final launch mode display label")
    try requireContains(pmfModels, "FinalDemoLaunchReport", "final demo launch report model")
    try requireContains(pmfModels, "FinalDemoLaunchPhase", "final demo launch phase model")
    try requireContains(pmfModels, "FinalResourcesPreflightReport", "final resources preflight report model")
    try requireContains(pmfModels, "FinalResourcesFileStatus", "final resources file status model")
    try requireContains(
        pmfModels,
        "FinalAcceptanceReadinessReport",
        "final acceptance readiness model"
    )
    try requireContains(
        pmfModels,
        "NPCAgentEvaluationReadinessReport",
        "NPC Agent evaluation readiness model"
    )
    try requireContains(
        pmfModels,
        "ThreeDEvaluationReadinessReport",
        "3D evaluation readiness model"
    )
    try requireContains(
        pmfModels,
        "ThreeDEvaluationReadinessInputModes",
        "3D evaluation input mode coverage model"
    )
    try requireContains(pmfModels, "FinalAcceptanceFreshness", "final acceptance freshness model")
    try requireContains(
        pmfModels,
        "freshness: FinalAcceptanceFreshness?",
        "final acceptance freshness field"
    )
    try requireContains(
        pmfModels,
        "finalAcceptanceReadiness",
        "final demo launch final acceptance readiness field"
    )
    try requireContains(
        pmfModels,
        "threeDEvaluationReadiness",
        "final demo launch 3D evaluation readiness field"
    )
    try requireContains(
        pmfModels,
        "npcAgentEvaluationReadiness",
        "final demo launch NPC Agent evaluation readiness field"
    )
    try requireContains(
        pmfModels,
        "FinalOperatorHandoffReport",
        "final operator handoff model"
    )
    try requireContains(
        pmfModels,
        "finalOperatorHandoff",
        "final demo launch final operator handoff field"
    )
    try requireContains(
        pmfModels,
        "IOSDeployRunbookReport",
        "iOS deploy runbook model"
    )
    try requireContains(
        pmfModels,
        "iosDeployRunbook",
        "final demo launch iOS deploy runbook field"
    )
    try requireContains(
        pmfModels,
        "ResourceHandoffReport",
        "resource handoff model"
    )
    try requireContains(
        pmfModels,
        "resourceReport",
        "final demo launch resource handoff field"
    )
    try requireContains(pmfModels, "FinalResourcesPreflightItem", "final resources preflight item model")
    try requireContains(
        pmfModels,
        "items: [FinalResourcesPreflightItem]",
        "final resources preflight items"
    )
    try requireContains(finalLaunchMobileSummary, "FinalLaunchMobileSummaryBuilder", "final launch summary builder")
    try requireContains(finalLaunchMobileSummary, "FinalLaunchMobileStatus", "final launch summary status")
    try requireContains(finalLaunchMobileSummary, "launchReceiptRows", "final launch receipt rows")
    try requireContains(finalLaunchMobileSummary, "launchReceiptRows(from:", "final launch receipt builder")
    try requireContains(finalLaunchMobileSummary, "firstBlockerReceiptRow", "final launch receipt blocker row")
    try requireContains(finalLaunchMobileSummary, "freshness.status == \"stale\"", "final launch stale freshness handling")
    try requireContains(finalLaunchMobileSummary, "modePolicyRows", "final launch summary mode policy rows")
    try requireContains(finalLaunchMobileSummary, "liveCallPolicy", "final launch summary live policy mapping")
    try requireContains(finalLaunchMobileSummary, "resourceChecklistRows", "final launch resource checklist rows")
    try requireContains(finalLaunchMobileSummary, "resourceChecklistRow", "final launch resource checklist row builder")
    try requireContains(liveProviderConsentSummary, "LiveProviderConsentSummaryBuilder", "live provider consent builder")
    try requireContains(liveProviderConsentSummary, "LiveProviderConsentStatus", "live provider consent status")
    try requireContains(liveProviderConsentSummary, "canRunConfiguredAcceptance", "live provider consent ready gate")
    try requireContains(liveProviderConsentSummary, "no live calls by default", "live provider no-default-call policy")
    try requireContains(liveProviderConsentSummary, "Provider keys remain backend-only.", "live provider secret boundary")
    try requireContains(liveProviderConsentSummary, "sanitize", "live provider consent redaction")
    try requireContains(liveProviderConsentView, "Live Provider Consent", "live provider consent view title")
    try requireContains(liveProviderConsentView, "summary.consentFlag", "live provider consent flag rendering")
    try requireContains(liveProviderConsentView, "summary.privacyNotes", "live provider consent privacy rendering")
    try requireContains(
        threeDGenerationInputReview,
        "ThreeDGenerationInputReviewBuilder",
        "3D generation input review builder"
    )
    try requireContains(
        threeDGenerationInputReview,
        "selectedProviderSourceCount",
        "3D generation input review provider source count"
    )
    try requireContains(
        threeDGenerationInputReview,
        "provider images",
        "3D generation input review selected provider image copy"
    )
    try requireContains(
        threeDGenerationInputReview,
        "Raw capture files withheld.",
        "3D generation input review privacy note"
    )
    try requireContains(threeDGenerationInputReview, "canForge3D", "3D generation input review forge gate")
    try requireContains(threeDGenerationInputReview, "sanitize", "3D generation input review redaction")
    try requireContains(
        threeDGenerationInputReviewView,
        "3D Generation Input",
        "3D generation input review view title"
    )
    try requireContains(
        threeDGenerationInputReviewView,
        "review.routeLabel",
        "3D generation input review route rendering"
    )
    try requireContains(
        threeDGenerationInputReviewView,
        "review.privacyNotes",
        "3D generation input review privacy rendering"
    )
    try requireContains(
        generationResultReceipt,
        "GenerationResultReceiptBuilder",
        "3D generation result receipt builder"
    )
    try requireContains(
        generationResultReceipt,
        "canPresentResult",
        "3D generation result presentation gate"
    )
    try requireContains(
        generationResultReceipt,
        "Raw provider URIs and prompts withheld.",
        "3D generation result privacy note"
    )
    try requireContains(
        generationResultReceipt,
        "scene-loadable iOS asset",
        "3D generation result iOS scene proof"
    )
    try requireContains(generationResultReceipt, "npcAgentTraces", "3D generation result NPC trace proof")
    try requireContains(generationResultReceipt, "sanitize", "3D generation result redaction")
    try requireContains(
        generationResultReceiptView,
        "3D Generation Result",
        "3D generation result view title"
    )
    try requireContains(
        generationResultReceiptView,
        "receipt.routeLabel",
        "3D generation result route rendering"
    )
    try requireContains(
        generationResultReceiptView,
        "receipt.privacyNotes",
        "3D generation result privacy rendering"
    )
    try requireContains(
        printFulfillmentReceipt,
        "PrintFulfillmentReceiptBuilder",
        "print fulfillment receipt builder"
    )
    try requireContains(
        printFulfillmentReceipt,
        "PrintFulfillmentReceiptRow",
        "print fulfillment receipt row"
    )
    try requireContains(
        printFulfillmentReceipt,
        "Checkout/payment links stay withheld",
        "print fulfillment checkout boundary"
    )
    try requireContains(printFulfillmentReceipt, "canHandOffToProvider", "print fulfillment handoff gate")
    try requireContains(printFulfillmentReceipt, "sanitize", "print fulfillment redaction")
    try requireContains(printFulfillmentReceiptView, "Print Fulfillment", "print fulfillment view title")
    try requireContains(printFulfillmentReceiptView, "receipt.privacyNotes", "print fulfillment privacy rendering")
    try requireContains(
        printQuoteReviewView,
        "PrintFulfillmentReceiptView(receipt: fulfillmentReceipt)",
        "print quote review fulfillment receipt"
    )
    try requireContains(printQuoteReviewView, "Approve Print Handoff", "print quote approval toggle")
    try requireContains(
        printQuoteReviewView,
        "@Binding var isPrintQuoteApproved",
        "print quote approval binding input"
    )
    try requireContains(
        contractTests,
        "testThreeDGenerationInputReviewWaitsForCaptureMedia",
        "3D generation input review waiting contract test"
    )
    try requireContains(
        contractTests,
        "testThreeDGenerationInputReviewShowsGuidedScanProviderSelection",
        "3D generation input review guided scan contract test"
    )
    try requireContains(
        contractTests,
        "testThreeDGenerationInputReviewShowsARKitScanPackage",
        "3D generation input review ARKit scan contract test"
    )
    try requireContains(
        contractTests,
        "testThreeDGenerationInputReviewShowsMeshyReadyRoute",
        "3D generation input review Meshy-ready contract test"
    )
    try requireContains(
        contractTests,
        "testThreeDGenerationInputReviewRedactsUnsafeText",
        "3D generation input review redaction contract test"
    )
    try requireContains(
        contractTests,
        "testGenerationResultReceiptWaitsForForge",
        "3D generation result waiting contract test"
    )
    try requireContains(
        contractTests,
        "testGenerationResultReceiptShowsCompleteForgeResult",
        "3D generation result ready contract test"
    )
    try requireContains(
        contractTests,
        "testGenerationResultReceiptRequiresIOSSceneVariant",
        "3D generation result iOS scene contract test"
    )
    try requireContains(
        contractTests,
        "testGenerationResultReceiptRedactsUnsafeText",
        "3D generation result redaction contract test"
    )
    try requireContains(
        contractTests,
        "testPrintFulfillmentReceiptRequiresApprovalBeforeHandoff",
        "print fulfillment approval required test"
    )
    try requireContains(
        contractTests,
        "testPrintFulfillmentReceiptShowsApprovedProviderHandoff",
        "print fulfillment approved handoff test"
    )
    try requireContains(
        contractTests,
        "testPrintFulfillmentReceiptBlocksAndRedactsUnsafeText",
        "print fulfillment redaction test"
    )
    try requireContains(finalLaunchMobileSummary, "resourceHandoffRows", "final launch resource handoff rows")
    try requireContains(
        finalLaunchMobileSummary,
        "resourceHandoffBackendRows",
        "final launch backend resource handoff rows"
    )
    try requireContains(
        finalLaunchMobileSummary,
        "resourceHandoffIOSRows",
        "final launch iOS resource handoff rows"
    )
    try requireContains(finalLaunchMobileSummary, "acceptanceRows", "final launch summary acceptance rows")
    try requireContains(finalLaunchMobileSummary, "threeDEvaluationRows", "final launch summary 3D evaluation rows")
    try requireContains(
        finalLaunchMobileSummary,
        "threeDEvaluationRows(from:",
        "final launch summary 3D evaluation row builder"
    )
    try requireContains(finalLaunchMobileSummary, "npcEvaluationRows", "final launch summary NPC evaluation rows")
    try requireContains(
        finalLaunchMobileSummary,
        "npcEvaluationRows(from:",
        "final launch summary NPC evaluation row builder"
    )
    try requireContains(finalLaunchMobileSummary, "deployRunbookRows", "final launch iOS deploy runbook rows")
    try requireContains(
        finalLaunchMobileSummary,
        "deployRunbookCommandRows",
        "final launch iOS deploy command rows"
    )
    try requireContains(
        finalLaunchMobileSummary,
        "deployRunbookSafetyRows",
        "final launch iOS deploy safety rows"
    )
    try requireContains(
        finalLaunchMobileSummary,
        "deployRunbookRows(from:",
        "final launch iOS deploy runbook row builder"
    )
    try requireContains(finalLaunchMobileSummary, "handoffRows", "final launch summary handoff rows")
    try requireContains(
        threeDEvaluationReadiness,
        "build_three_d_evaluation_readiness_report",
        "3D evaluation readiness report builder"
    )
    try requireContains(
        threeDEvaluationReadiness,
        "LOCAL_THREE_D_EVALUATION_COMMAND",
        "3D evaluation readiness local command"
    )
    try requireContains(
        threeDEvaluationReadiness,
        "make backend-evaluate-3d",
        "3D evaluation readiness Make command"
    )
    try requireContains(
        threeDEvaluationReadinessTests,
        "test_three_d_evaluation_readiness_ready_report",
        "3D evaluation readiness ready report test"
    )
    try requireContains(
        evaluationMakeTargetsTests,
        "test_evaluation_make_targets_dry_run_expected_local_commands",
        "evaluation Make target dry-run test"
    )
    try requireContains(
        finalOperatorHandoff,
        "three_d_evaluation",
        "final operator handoff 3D evaluation step"
    )
    try requireContains(
        finalOperatorHandoff,
        "LOCAL_THREE_D_EVALUATION_COMMAND",
        "final operator handoff 3D evaluation command"
    )
    try requireContains(
        finalDemoLaunch,
        "three_d_evaluation_readiness=three_d_evaluation_readiness",
        "final demo launch passes 3D evaluation readiness to handoff"
    )
    try requireContains(
        finalOperatorHandoff,
        "npc_agent_evaluation",
        "final operator handoff NPC evaluation step"
    )
    try requireContains(
        finalOperatorHandoff,
        "LOCAL_NPC_EVALUATION_COMMAND",
        "final operator handoff NPC evaluation command"
    )
    try requireContains(
        npcAgentEvaluationReadiness,
        "make backend-evaluate-npc",
        "NPC evaluation readiness Make command"
    )
    try requireContains(
        finalDemoLaunch,
        "npc_agent_evaluation_readiness=npc_agent_evaluation_readiness",
        "final demo launch passes NPC evaluation readiness to handoff"
    )
    try requireContains(
        iosDeployRunbook,
        "build_ios_deploy_runbook_report",
        "iOS deploy runbook report builder"
    )
    try requireContains(
        iosDeployRunbook,
        "build_three_d_evaluation_readiness_report",
        "iOS deploy runbook 3D evaluation readiness input"
    )
    try requireContains(
        iosDeployRunbook,
        "LOCAL_THREE_D_EVALUATION_COMMAND",
        "iOS deploy runbook 3D evaluation Make command"
    )
    try requireContains(
        iosDeployRunbook,
        "LOCAL_NPC_EVALUATION_COMMAND",
        "iOS deploy runbook NPC evaluation Make command"
    )
    try requireContains(
        iosDeployRunbook,
        "three_d_evaluation",
        "iOS deploy runbook 3D evaluation slot id"
    )
    try requireContains(
        iosDeployRunbook,
        "IOS_DEPLOY_RUNBOOK_COMMAND",
        "iOS deploy runbook command constant"
    )
    try requireContains(
        finalOperatorHandoff,
        "ios_deploy_runbook",
        "final operator handoff iOS deploy runbook step"
    )
    try requireContains(
        finalDemoLaunch,
        "ios_deploy_runbook=ios_deploy_runbook",
        "final demo launch passes iOS deploy runbook to handoff"
    )
    try requireContains(
        iosDeployRunbookTests,
        "test_ios_deploy_runbook_ready_local_inputs_preserve_command_order",
        "iOS deploy runbook command order test"
    )
    try requireContains(
        iosDeployRunbookTests,
        "test_ios_deploy_runbook_blocks_and_redacts_failed_3d_evaluation",
        "iOS deploy runbook blocked 3D evaluation test"
    )
    try requireContains(
        contractTests,
        "testFinalLaunchMobileSummaryShowsThreeDEvaluationIOSDeployRunbookSlot",
        "mobile final launch iOS deploy runbook 3D evaluation slot test"
    )
    try requireContains(
        finalDemoLaunchTests,
        "test_final_demo_launch_embeds_three_d_evaluation_readiness",
        "final demo launch 3D evaluation readiness test"
    )
    try requireContains(
        finalDemoLaunchTests,
        "test_final_demo_launch_operator_handoff_includes_three_d_evaluation_step",
        "final demo launch 3D evaluation handoff test"
    )
    try requireContains(
        finalDemoLaunchTests,
        "test_final_demo_launch_operator_handoff_includes_npc_evaluation_step",
        "final demo launch NPC evaluation handoff test"
    )
    try requireContains(
        finalDemoLaunchTests,
        "test_final_demo_launch_embeds_ios_deploy_runbook",
        "final demo launch iOS deploy runbook test"
    )
    try requireContains(finalLaunchStatusView, "Launch Receipt", "final launch receipt section")
    try requireContains(finalLaunchStatusView, "Resource Checklist", "final launch resource checklist section")
    try requireContains(finalLaunchStatusView, "Resource Handoff", "final launch resource handoff section")
    try requireContains(finalLaunchStatusView, "Backend Resources", "final launch backend resources section")
    try requireContains(finalLaunchStatusView, "iOS Resources", "final launch iOS resources section")
    try requireContains(finalLaunchStatusView, "3D Evaluation", "final launch 3D evaluation section")
    try requireContains(finalLaunchStatusView, "NPC Evaluation", "final launch NPC evaluation section")
    try requireContains(
        contractTests,
        "testFinalLaunchMobileSummaryShowsAcceptanceBlockerReceipt",
        "final launch acceptance blocker receipt test"
    )
    try requireContains(
        contractTests,
        "testFinalLaunchMobileSummaryShowsReadyConfiguredReceipt",
        "final launch ready configured receipt test"
    )
    try requireContains(
        contractTests,
        "testDecodesFinalAcceptanceFreshnessFromFinalLaunchPayload",
        "final acceptance freshness decode test"
    )
    try requireContains(
        contractTests,
        "testFinalLaunchMobileSummaryShowsStaleFinalAcceptanceFreshness",
        "final acceptance stale freshness summary test"
    )
    try requireContains(
        contractTests,
        "testDecodesThreeDEvaluationReadinessFromFinalLaunchPayload",
        "3D evaluation readiness decode test"
    )
    try requireContains(
        contractTests,
        "testFinalLaunchMobileSummaryShowsReadyThreeDEvaluation",
        "3D evaluation ready summary test"
    )
    try requireContains(
        contractTests,
        "testFinalLaunchMobileSummaryShowsBlockedThreeDEvaluation",
        "3D evaluation blocked summary test"
    )
    try requireContains(
        contractTests,
        "testDecodesNPCAgentEvaluationReadinessFromFinalLaunchPayload",
        "NPC Agent evaluation readiness decode test"
    )
    try requireContains(
        contractTests,
        "testFinalLaunchMobileSummaryShowsReadyNPCAgentEvaluation",
        "NPC Agent evaluation ready summary test"
    )
    try requireContains(
        contractTests,
        "testFinalLaunchMobileSummaryShowsBlockedNPCAgentEvaluation",
        "NPC Agent evaluation blocked summary test"
    )
    try requireContains(
        contractTests,
        "testDecodesIOSDeployRunbookFromFinalLaunchPayload",
        "iOS deploy runbook decode test"
    )
    try requireContains(
        contractTests,
        "testFinalLaunchMobileSummaryShowsPartialIOSDeployRunbook",
        "iOS deploy runbook partial summary test"
    )
    try requireContains(
        contractTests,
        "testFinalLaunchMobileSummaryShowsBlockedIOSDeployRunbook",
        "iOS deploy runbook blocked summary test"
    )
    try requireContains(
        contractTests,
        "testFinalLaunchMobileSummaryRedactsUnsafeIOSDeployRunbook",
        "iOS deploy runbook redaction test"
    )
    try requireContains(
        contractTests,
        "testDecodesResourceHandoffFromFinalLaunchPayload",
        "resource handoff decode test"
    )
    try requireContains(
        contractTests,
        "testFinalLaunchMobileSummaryShowsMissingResourceHandoff",
        "resource handoff missing summary test"
    )
    try requireContains(
        contractTests,
        "testFinalLaunchMobileSummaryShowsReadyResourceHandoff",
        "resource handoff ready summary test"
    )
    try requireContains(
        contractTests,
        "testFinalLaunchMobileSummaryRedactsUnsafeResourceHandoff",
        "resource handoff redaction test"
    )
    try requireContains(
        contractTests,
        "testDecodesFinalResourcesPreflightItemsFromFinalLaunchPayload",
        "final resources item decode test"
    )
    try requireContains(
        contractTests,
        "testFinalLaunchMobileSummaryShowsMissingResourceChecklist",
        "final resources checklist summary test"
    )
    try requireContains(
        contractTests,
        "testLiveProviderConsentSummaryWaitsForProviderReadiness",
        "live provider consent waiting test"
    )
    try requireContains(
        contractTests,
        "testLiveProviderConsentSummaryBlocksMissingConfiguredProviders",
        "live provider consent blocked test"
    )
    try requireContains(
        contractTests,
        "testLiveProviderConsentSummaryShowsReadyConfiguredConsent",
        "live provider consent ready test"
    )
    try requireContains(
        contractTests,
        "testLiveProviderConsentSummaryRedactsUnsafeText",
        "live provider consent redaction test"
    )
    try requireContains(
        finalLaunchMobileSummary,
        "Final acceptance ready.",
        "final launch acceptance ready copy"
    )
    try requireContains(
        finalLaunchMobileSummary,
        "Final operator handoff ready.",
        "final launch operator handoff ready copy"
    )
    try requireContains(finalLaunchMobileSummary, "sanitize", "final launch summary redaction")
    try requireContains(contextCapsuleReview, "ContextCapsuleReviewBuilder", "context capsule review builder")
    try requireContains(contextCapsuleReview, "ContextCapsuleReviewStatus", "context capsule review status")
    try requireContains(contextCapsuleReview, "No raw email", "context capsule raw source privacy note")
    try requireContains(contextCapsuleReview, "sanitize", "context capsule review redaction")
    try requireContains(forgeReadinessSummary, "ForgeReadinessSummaryBuilder", "forge readiness builder")
    try requireContains(forgeReadinessSummary, "ForgeReadinessSummaryStatus", "forge readiness status")
    try requireContains(forgeReadinessSummary, "ForgeActionGate", "forge action gate model")
    try requireContains(forgeReadinessSummary, "ForgeActionGateBuilder", "forge action gate builder")
    try requireContains(forgeReadinessSummary, "disabledReason", "forge action disabled reason")
    try requireContains(forgeReadinessSummary, "routeLabel", "forge readiness route label")
    try requireContains(forgeReadinessSummary, "canForge", "forge readiness forge gate")
    try requireContains(forgeReadinessSummary, "sanitize", "forge readiness redaction")
    try requireContains(
        forgeRootView,
        ".onChange(of: selectedCaptureMode) { mode in",
        "macOS 13-compatible capture mode onChange"
    )
    try requireNotContains(
        forgeRootView,
        ".onChange(of: selectedCaptureMode) { _, mode in",
        "macOS 14-only capture mode onChange"
    )
    try requireNotContains(
        forgeRootView,
        ".onChange(of: selectedSinglePhotoItem?.itemIdentifier) { _, _ in",
        "macOS 14-only single photo onChange"
    )
    try requireNotContains(
        forgeRootView,
        ".onChange(of: selectedPhotoItems.map(\\.itemIdentifier)) { _, _ in",
        "macOS 14-only photo set onChange"
    )
    try requireContains(
        forgeRootView,
        "startAccessingSecurityScopedResource",
        "security scoped file access"
    )
    try requireNotContains(forgeRootView, "switch mode", "undefined capture mode switch")
    try requireNotContains(forgeRootView, "sampleMedia", "sample media fallback")
    try requireNotContains(forgeRootView, "sample-image", "sample image bytes")
    try requireNotContains(forgeRootView, "scan-glb", "sample scan bytes")
    try requireContains(
        guidedScanCaptureView,
        "#if os(iOS) && canImport(RealityKit)",
        "iOS-only RealityKit object capture guard"
    )
    try requireContains(guidedScanCaptureView, "import RealityKit", "RealityKit guided scan import")
    try requireContains(guidedScanCaptureView, "ObjectCaptureSession", "Object Capture session source")
    try requireContains(
        guidedScanCaptureView,
        "ObjectCaptureView(session:",
        "Object Capture camera view source"
    )
    try requireContains(
        guidedScanCaptureView,
        "start(imagesDirectory:",
        "Object Capture image directory start"
    )
    try requireContains(
        guidedScanCaptureView,
        "numberOfShotsTakenUpdates",
        "Object Capture shot count observation"
    )
    try requireContains(
        guidedScanCaptureView,
        "Object Capture is only available on supported iOS devices.",
        "non-iOS guided scan fallback"
    )
    try requireContains(cameraCaptureView, "UIImagePickerController", "UIKit camera picker source")
    try requireContains(cameraCaptureView, "jpegData(compressionQuality:", "camera JPEG conversion source")
    try requireContains(cameraCaptureView, "Camera unavailable", "camera unsupported fallback")
    try requireContains(
        providerReadinessView,
        "ProviderReadinessResponse",
        "provider readiness response model use"
    )
    try requireContains(
        providerReadinessView,
        "overallDemoReady",
        "provider readiness demo status"
    )
    try requireContains(
        providerReadinessView,
        "overallRealReady",
        "provider readiness real status"
    )
    try requireContains(
        providerReadinessView,
        "missingEnv",
        "provider readiness missing env display"
    )
    try requireNotContains(
        providerReadinessView,
        "sk-",
        "provider readiness secret sample"
    )
    try requireContains(
        artifactSummaryView,
        "Artifact3DPreviewView(session: session, latestTick: latestTick)",
        "artifact summary 3D preview wiring"
    )
    try requireContains(
        artifactSummaryView,
        "GenerationResultReceiptView(",
        "artifact summary generation result receipt wiring"
    )
    try requireContains(
        artifactSummaryView,
        "GenerationResultReceiptBuilder.build(session: session)",
        "artifact summary generation result receipt builder"
    )
    try requireContains(artifactSummaryView, "let latestTick: NPCAgentTick?", "artifact summary latest tick input")
    try requireContains(
        artifactSummaryView,
        "generationProvenance",
        "artifact summary provenance display"
    )
    try requireContains(
        artifactSummaryView,
        "ArtifactGenerationProvenanceSummaryBuilder.build",
        "artifact summary provenance summary builder"
    )
    try requireContains(
        artifactGenerationProvenanceSummary,
        "ArtifactGenerationProvenanceSummaryBuilder",
        "generation provenance summary builder"
    )
    try requireContains(
        artifactGenerationProvenanceSummary,
        "sourceAssetCount",
        "generation provenance scan asset count"
    )
    try requireContains(
        artifactGenerationProvenanceSummary,
        "selectionReason",
        "generation provenance selection reason"
    )
    try requireContains(
        artifactGenerationProvenanceSummary,
        "privacySummary",
        "generation provenance privacy summary"
    )
    try requireContains(
        contractTests,
        "testArtifactGenerationProvenanceSummaryShowsScanAssets",
        "generation provenance scan asset test"
    )
    try requireContains(artifact3DPreviewView, "import SceneKit", "SceneKit preview source")
    try requireContains(artifact3DPreviewView, "SceneView(scene:", "SwiftUI SceneKit scene view")
    try requireContains(artifact3DPreviewView, "ArtifactPreviewState", "artifact preview state usage")
    try requireContains(artifact3DPreviewView, "SCNScene", "SceneKit scene construction")
    try requireContains(artifact3DPreviewView, "SCNCylinder", "artifact pedestal geometry")
    try requireContains(artifact3DPreviewView, "SCNTorus", "myth artifact proxy geometry")
    try requireContains(artifact3DPreviewView, "NPCRitualSceneBuilder.build", "NPC ritual scene builder")
    try requireContains(artifact3DPreviewView, "addNPCRitualOverlay", "NPC ritual scene overlay")
    try requireContains(artifact3DPreviewView, "NPC ritual", "NPC ritual scene status copy")
    try requireContains(npcRitualScene, "NPCRitualSceneBuilder", "NPC ritual scene model builder")
    try requireContains(artifactAssetPreparation, "ArtifactAssetPreparer", "asset preparation service")
    try requireContains(artifactHandoffActions, "ArtifactHandoffActionBuilder", "artifact action builder")
    try requireContains(artifactHandoffActions, "ArtifactHandoffActionSummary", "artifact action summary")
    try requireContains(artifactHandoffActionsView, "Artifact Handoff", "artifact action panel title")
    try requireContains(artifactHandoffActionsView, "ShareLink", "cached asset share action")
    try requireContains(artifactHandoffActionsView, "Retry Download", "retry download action")
    try requireContains(
        artifact3DPreviewView,
        "ArtifactHandoffActionBuilder.build",
        "artifact action summary wiring"
    )
    try requireContains(
        artifact3DPreviewView,
        "ArtifactHandoffActionsView(",
        "artifact action panel wiring"
    )
    try requireNotContains(
        artifact3DPreviewView,
        "cachedURL?.absoluteString",
        "artifact preview avoids full local cached paths"
    )
    try requireContains(project, "ArtifactHandoffActionsView.swift", "artifact action Xcode file reference")
    try requireContains(guidedScanPhotoSetBuilder, "GuidedScanPhotoSetBuilder", "guided scan importer")
    try requireContains(
        guidedScanPhotoSetBuilder,
        "maximumImportedImages = 12",
        "guided scan importer upload cap"
    )
    try requireContains(arkitScanPackageBuilder, "ARKitScanPackageBuilder", "ARKit scan package builder")
    try requireContains(arkitScanPackageBuilder, "ARKitScanExportFile", "ARKit scan export file")
    try requireContains(
        arkitScanPackageBuilder,
        "maximumReferenceImages = 11",
        "ARKit scan reference cap"
    )
    try requireContains(
        arkitScanPackageBuilder,
        "CaptureMediaSelection(mode: .arkitScan",
        "ARKit scan selection output"
    )
    try requireContains(
        captureGenerationReadiness,
        "CaptureGenerationReadinessBuilder",
        "capture generation readiness builder"
    )
    try requireContains(
        captureGenerationReadiness,
        "maximumProviderSourceImages = 4",
        "Meshy multi-image source cap"
    )
    try requireContains(
        captureGenerationReadiness,
        "CaptureGenerationRoute",
        "capture generation route model"
    )
    try requireContains(
        captureGenerationReadiness,
        "displayLabel",
        "capture generation route display label"
    )
    try requireContains(
        captureGenerationReceipt,
        "CaptureGenerationReceiptBuilder",
        "capture generation receipt builder"
    )
    try requireContains(
        captureGenerationReceipt,
        "Capture-to-3D proof missing",
        "capture generation receipt missing provenance state"
    )
    try requireContains(
        captureGenerationReceipt,
        "raw sources",
        "capture generation receipt raw source row"
    )
    try requireContains(
        captureGenerationReceipt,
        "Raw capture media withheld.",
        "capture generation receipt privacy note"
    )
    try requireContains(
        captureGenerationReceipt,
        "sanitize",
        "capture generation receipt redaction"
    )
    try requireContains(
        captureGenerationReceiptView,
        "Capture-to-3D",
        "capture generation receipt view title"
    )
    try requireContains(
        captureGenerationReceiptView,
        "statusBadge",
        "capture generation receipt status badge"
    )
    try requireContains(
        captureGenerationReceiptView,
        "receipt.privacyNotes",
        "capture generation receipt privacy rendering"
    )
    try requireContains(
        forgeProgressReceipt,
        "ForgeProgressReceiptBuilder",
        "forge progress receipt builder"
    )
    try requireContains(
        forgeProgressReceipt,
        "ForgeProgressReceiptRow",
        "forge progress receipt rows"
    )
    try requireContains(
        forgeProgressReceipt,
        "Raw capture media stays off this receipt.",
        "forge progress receipt privacy note"
    )
    try requireContains(
        forgeProgressReceipt,
        "sanitize",
        "forge progress receipt redaction"
    )
    try requireContains(
        forgeProgressReceiptView,
        "Forge Progress",
        "forge progress receipt view title"
    )
    try requireContains(
        forgeProgressReceiptView,
        "statusBadge",
        "forge progress receipt status badge"
    )
    try requireContains(
        forgeProgressReceiptView,
        "receipt.privacyNotes",
        "forge progress receipt privacy rendering"
    )
    try requireContains(
        contractTests,
        "testARKitScanPackageBuilderBuildsReadySelection",
        "ARKit scan package contract test"
    )
    try requireContains(
        contractTests,
        "testCaptureGenerationReceiptShowsReadyGuidedScanGeneration",
        "capture generation receipt ready contract test"
    )
    try requireContains(
        contractTests,
        "testCaptureGenerationReceiptRedactsUnsafeText",
        "capture generation receipt redaction contract test"
    )
    try requireContains(
        contractTests,
        "testForgeProgressReceiptShowsReadyProviderAndNPCRuntime",
        "forge progress receipt ready contract test"
    )
    try requireContains(
        contractTests,
        "testForgeProgressReceiptRedactsUnsafeFailure",
        "forge progress receipt redaction contract test"
    )
    try requireContains(artifactAssetPreparation, "FileSystemArtifactAssetCache", "asset cache implementation")
    try requireContains(
        artifactAssetPreparation,
        "URLSessionArtifactAssetDownloader",
        "asset downloader implementation"
    )
    try requireContains(artifact3DPreviewView, "ArtifactAssetPreparer.live()", "live asset preparer wiring")
    try requireContains(pmfModels, "GeneratedAssetVariant", "generated asset variant model")
    try requireContains(pmfModels, "variants: [GeneratedAssetVariant]", "generated asset variants")
    try requireContains(pmfModels, "GeneratedAssetProvenance", "generated asset provenance model")
    try requireContains(
        pmfModels,
        "generationProvenance: GeneratedAssetProvenance?",
        "optional generated asset provenance"
    )
    try requireContains(pmfModels, "NPCAgentTrace", "npc agent trace model")
    try requireContains(pmfModels, "npcAgentTraces: [NPCAgentTrace]", "npc agent traces model")
    try requireContains(mythSessionID, "MythSessionID", "myth session id validator")
    try requireContains(mythSessionID, "myth_", "myth session id prefix")
    try requireContains(
        apiClient,
        "advanceMythSessionHistory",
        "server-owned npc history client method"
    )
    try requireContains(
        apiClient,
        "/v1/myth-sessions/\\(sessionId)/npc-ticks",
        "server-owned npc history endpoint"
    )
    try requireContains(demoRunSnapshot, "DemoRunSnapshot", "demo run snapshot model")
    try requireContains(demoRunSnapshot, "maximumStoredTicks = 12", "demo snapshot tick cap")
    try requireContains(demoRunSnapshot, "DemoRunSnapshotFileStore", "demo snapshot file store")
    try requireContains(demoRunSnapshot, ".applicationSupportDirectory", "demo snapshot application support storage")
    try requireContains(demoRunSnapshot, ".atomic", "demo snapshot atomic write")
    try requireContains(npcReactionsView, "npcAgentRuntime", "npc agent runtime display")
    try requireContains(npcReactionsView, "npcAgentTraces", "npc agent trace display")
    try requireContains(npcReactionsView, "proposedAction", "npc proposed action display")
    try requireContains(npcTickView, "NPCAgentTick", "npc tick model usage")
    try requireContains(npcAgentTickSummary, #"advanceTitle: "Advance Village""#, "npc tick action label")
    try requireContains(npcTickView, "tickHistoryCount", "npc tick history count input")
    try requireContains(npcTickView, "agentRuntime", "npc tick runtime display")
    try requireContains(npcTickView, "acceptedActions", "npc tick accepted actions")
    try requireContains(npcTickView, "rejectedActions", "npc tick rejected actions")
    try requireContains(npcTickView, "visibleChanges", "npc tick visible changes")
    try requireContains(npcTickView, "let summary: NPCAgentTickSummary", "npc tick summary input")
    try requireContains(npcTickView, "summary.decisionLabel", "npc tick summary decision display")
    try requireContains(npcTickView, "summary.privacyNotes", "npc tick privacy notes display")
    try requireContains(npcTickView, "let actionGate: NPCAgentActionGate", "npc action gate view input")
    try requireContains(npcTickView, "actionGate.canRunAutonomy", "npc autonomy action gate")
    try requireContains(npcTickView, "actionGate.canAdvanceVillage", "npc advance action gate")
    try requireContains(npcTickView, "actionGate.detail", "npc action gate detail")
    try requireNotContains(npcTickView, "sk-", "npc tick secret sample")
    try requireContains(npcAgentModeSummary, "NPCAgentModeSummaryBuilder", "npc agent mode summary builder")
    try requireContains(npcAgentModeSummary, "NPCAgentModeStatus", "npc agent mode status")
    try requireContains(npcAgentTickSummary, "NPCAgentTickSummaryBuilder", "npc agent tick summary builder")
    try requireContains(npcAgentTickSummary, "NPCAgentTickSummaryStatus", "npc agent tick summary status")
    try requireContains(npcAgentTickSummary, "NPCAgentActionGateBuilder", "npc agent action gate builder")
    try requireContains(npcAgentTickSummary, "canRunAutonomy", "npc action gate autonomy flag")
    try requireContains(npcAgentTickSummary, "disabledReason", "npc action gate disabled reason")
    try requireContains(npcAgentTickSummary, "decisionLabel", "npc agent tick decision summary")
    try requireContains(npcAgentTickSummary, "privacyNotes", "npc agent tick privacy notes")
    try requireContains(npcAgentModeView, "NPC Agent Mode", "npc agent mode title")
    try requireContains(npcAgentModeView, "summary.missingEnv", "npc agent missing env display")
    try requireContains(npcAgentModeView, "providerLabel", "npc agent provider display")
    try requireContains(forgeRootView, "NPCAgentModeSummaryBuilder.build", "npc agent mode root wiring")
    try requireContains(forgeRootView, "NPCAgentModeView(summary:", "npc agent mode view wiring")
    try requireContains(forgeRootView, "NPCAgentTickSummaryBuilder.build", "npc agent tick summary root wiring")
    try requireContains(forgeRootView, "summary: npcAgentTickSummary", "npc agent tick summary view wiring")
    try requireContains(forgeRootView, "npcAgentActionGate: NPCAgentActionGate", "npc action gate root property")
    try requireContains(forgeRootView, "NPCAgentActionGateBuilder.build", "npc action gate root builder wiring")
    try requireContains(forgeRootView, "actionGate: npcAgentActionGate", "npc action gate view handoff")
    try requireContains(
        contractTests,
        "testNPCAgentTickSummaryShowsLatestTickResolution",
        "npc agent tick summary contract test"
    )
    try requireContains(
        contractTests,
        "testNPCAgentActionGateEnablesLocalDemoActions",
        "npc action gate local demo contract test"
    )
    try requireContains(
        contractTests,
        "testForgeReadinessMarksLocalDemoReady",
        "forge readiness local demo contract test"
    )
    try requireContains(
        contractTests,
        "testForgeActionGateEnablesLocalDemoForge",
        "forge action gate local demo contract test"
    )
    try requireContains(project, "NPCAgentModeView.swift", "npc agent mode Xcode file reference")
    try requireContains(demoScriptView, "ShowcaseAutopilotPlan", "demo script autopilot input")
    try requireContains(demoScriptView, "Button(action: runAutopilot)", "demo script autopilot button")
    try requireContains(demoScript, "final_launch", "demo script final launch step")
    try requireContains(demoScript, "three_d_evaluation", "demo script 3D evaluation step")
    try requireContains(demoScript, "npc_evaluation", "demo script NPC evaluation step")
    try requireContains(demoScript, "threeDEvaluationStep", "demo script 3D evaluation builder")
    try requireContains(demoScript, "npcEvaluationStep", "demo script NPC evaluation builder")
    try requireContains(demoScript, "FinalLaunchMobileSummary", "demo script final launch summary input")
    try requireContains(showcaseAutopilot, "ShowcaseAutopilotPlanner", "showcase autopilot core planner")
    try requireContains(
        showcaseAutopilot,
        #"script.step(id: "final_launch")"#,
        "autopilot final launch step handling"
    )
    try requireContains(
        showcaseAutopilot,
        #"script.step(id: "three_d_evaluation")"#,
        "autopilot 3D evaluation step handling"
    )
    try requireContains(
        showcaseAutopilot,
        #"script.step(id: "npc_evaluation")"#,
        "autopilot NPC evaluation step handling"
    )
    try requireContains(
        contractTests,
        "testDemoScriptShowsBlockedFinalLaunch",
        "demo script final launch contract test"
    )
    try requireContains(
        contractTests,
        "testDemoScriptShowsReadyNPCEvaluationBeforeFinalLaunch",
        "demo script ready NPC evaluation contract test"
    )
    try requireContains(
        contractTests,
        "testDemoScriptShowsReadyThreeDEvaluationBeforeNPCEvaluation",
        "demo script ready 3D evaluation contract test"
    )
    try requireContains(
        contractTests,
        "testDemoScriptWaitsForMissingThreeDEvaluation",
        "demo script missing 3D evaluation contract test"
    )
    try requireContains(
        contractTests,
        "testDemoScriptBlocksAndRedactsFailedThreeDEvaluation",
        "demo script blocked 3D evaluation contract test"
    )
    try requireContains(
        contractTests,
        "testDemoScriptWaitsForMissingNPCEvaluation",
        "demo script missing NPC evaluation contract test"
    )
    try requireContains(
        contractTests,
        "testDemoScriptBlocksAndRedactsFailedNPCEvaluation",
        "demo script blocked NPC evaluation contract test"
    )
    try requireContains(
        contractTests,
        "testShowcaseAutopilotBlocksOnFinalLaunchBlocker",
        "autopilot final launch contract test"
    )
    try requireContains(
        contractTests,
        "testShowcaseAutopilotWaitsForMissingThreeDEvaluation",
        "autopilot missing 3D evaluation contract test"
    )
    try requireContains(
        contractTests,
        "testShowcaseAutopilotBlocksOnFailedThreeDEvaluation",
        "autopilot blocked 3D evaluation contract test"
    )
    try requireContains(
        contractTests,
        "testShowcaseAutopilotWaitsForMissingNPCEvaluation",
        "autopilot missing NPC evaluation contract test"
    )
    try requireContains(
        contractTests,
        "testShowcaseAutopilotBlocksOnFailedNPCEvaluation",
        "autopilot blocked NPC evaluation contract test"
    )
    try requireContains(demoSnapshotStatusView, "Restored Demo Run", "demo snapshot restored label")
    try requireContains(demoSnapshotStatusView, "Clear", "demo snapshot clear action")
    try requireContains(
        demoSnapshotStatusView,
        "isSyncingBackendHistory",
        "demo snapshot backend sync progress input"
    )
    try requireContains(
        demoSnapshotStatusView,
        "backendHistoryStatusText",
        "demo snapshot backend status input"
    )
    try requireContains(
        demoSnapshotStatusView,
        "ProgressView",
        "demo snapshot backend sync progress indicator"
    )
    try requireNotContains(demoSnapshotStatusView, "file://", "demo snapshot no local path display")
    try requireContains(printQuoteReviewView, "PrintQuote", "print quote model use")
    try requireContains(printQuoteReviewView, "Get Quote", "print quote button label")
    try requireContains(printQuoteReviewView, "Quoting...", "print quote loading label")
    try requireContains(printQuoteReviewView, "requiresUserApproval", "print quote approval display")
    try requireContains(printQuoteReviewView, "estimatedPriceCents", "print quote price display")
    try requireContains(printQuoteReviewView, "quote.checkoutUrl == nil", "checkout action withheld")
    try requireNotContains(printQuoteReviewView, "OpenURLAction", "no checkout URL opening")
    try requireNotContains(printQuoteReviewView, "sk-", "no provider secret sample")
    try requireContains(
        artifactAssetPreparation,
        "preferredSceneVariant",
        "scene variant selection"
    )
    try requireContains(
        artifact3DPreviewView,
        ".task(id: session?.sessionId)",
        "session-scoped asset preparation task"
    )
    try requireContains(artifact3DPreviewView, "PreparedArtifactAsset", "prepared asset state")
    try requireContains(artifact3DPreviewView, "SCNScene(url:", "local SceneKit asset loading")
    try requireContains(
        artifact3DPreviewView,
        "guard !Task.isCancelled else",
        "cancelled asset preparation does not overwrite preview state"
    )

    try scanForMobileSecrets(in: [appRoot, coreRoot], additionalFiles: [packageFile, projectFile, plistFile])

    print("PersonalMythForgeMobileProjectChecks passed")
} catch {
    fputs("Project check failed: \(error)\n", stderr)
    exit(1)
}

private func readText(_ url: URL) throws -> String {
    guard FileManager.default.fileExists(atPath: url.path) else {
        throw ProjectCheckError.missingFile(url.path)
    }
    return try String(contentsOf: url, encoding: .utf8)
}

private func readPropertyList(_ url: URL) throws -> [String: Any] {
    guard FileManager.default.fileExists(atPath: url.path) else {
        throw ProjectCheckError.missingFile(url.path)
    }
    let data = try Data(contentsOf: url)
    guard let plist = try PropertyListSerialization.propertyList(from: data, options: [], format: nil) as? [String: Any] else {
        throw ProjectCheckError.invalidPlist(url.path)
    }
    return plist
}

private func requireContains(_ haystack: String, _ needle: String, _ label: String) throws {
    if !haystack.contains(needle) {
        throw ProjectCheckError.missingText(label, needle)
    }
}

private func requireNotContains(_ haystack: String, _ needle: String, _ label: String) throws {
    if haystack.contains(needle) {
        throw ProjectCheckError.unexpectedText(label, needle)
    }
}

private func requireBefore(_ text: String, _ first: String, _ second: String, _ label: String) throws {
    guard let firstRange = text.range(of: first) else {
        throw ProjectCheckError.missingText(label, first)
    }
    guard let secondRange = text.range(of: second) else {
        throw ProjectCheckError.missingText(label, second)
    }
    if firstRange.lowerBound >= secondRange.lowerBound {
        throw ProjectCheckError.unexpectedText(label, "\(first) after \(second)")
    }
}

private func requirePBXSectionContains(
    _ project: String,
    sectionName: String,
    _ needle: String,
    _ label: String
) throws {
    let beginMarker = "/* Begin \(sectionName) section */"
    let endMarker = "/* End \(sectionName) section */"
    guard let beginRange = project.range(of: beginMarker),
          let endRange = project.range(of: endMarker, range: beginRange.upperBound..<project.endIndex)
    else {
        throw ProjectCheckError.missingText("\(label) section", beginMarker)
    }

    let section = project[beginRange.upperBound..<endRange.lowerBound]
    if !section.contains(needle) {
        throw ProjectCheckError.missingText(label, needle)
    }
}

private func requirePlistString(_ plist: [String: Any], key: String, expected: String) throws {
    guard let value = plist[key] as? String else {
        throw ProjectCheckError.missingPlistKey(key)
    }
    if value != expected {
        throw ProjectCheckError.invalidPlistValue(key, value)
    }
}

private func requirePlistText(_ plist: [String: Any], key: String) throws {
    guard let value = plist[key] as? String, !value.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
        throw ProjectCheckError.missingPlistKey(key)
    }
}

private func requireNestedPlistBool(
    _ plist: [String: Any],
    dictionaryKey: String,
    key: String,
    expected: Bool
) throws {
    guard let dictionary = plist[dictionaryKey] as? [String: Any] else {
        throw ProjectCheckError.missingPlistKey(dictionaryKey)
    }
    guard let value = dictionary[key] as? Bool else {
        throw ProjectCheckError.missingPlistKey("\(dictionaryKey).\(key)")
    }
    if value != expected {
        throw ProjectCheckError.invalidPlistValue("\(dictionaryKey).\(key)", String(value))
    }
}

private func scanForMobileSecrets(in directories: [URL], additionalFiles: [URL]) throws {
    let secretMarkers = [
        "OPENAI_API_KEY",
        "MESHY_API_KEY",
        "TREATSTOCK_API_KEY",
        "api_key",
        "Bearer ",
    ]
    var files = additionalFiles
    for directory in directories {
        guard let enumerator = FileManager.default.enumerator(
            at: directory,
            includingPropertiesForKeys: nil
        ) else {
            throw ProjectCheckError.missingFile(directory.path)
        }
        for case let url as URL in enumerator where url.pathExtension == "swift" || url.pathExtension == "plist" {
            files.append(url)
        }
    }

    for url in files {
        let text = try readText(url)
        for marker in secretMarkers where text.contains(marker) {
            throw ProjectCheckError.secretMarker(url.lastPathComponent, marker)
        }
    }
}

private enum ProjectCheckError: Error, CustomStringConvertible {
    case missingFile(String)
    case invalidPlist(String)
    case missingText(String, String)
    case unexpectedText(String, String)
    case missingPlistKey(String)
    case invalidPlistValue(String, String)
    case secretMarker(String, String)

    var description: String {
        switch self {
        case let .missingFile(path):
            return "Missing required file: \(path)"
        case let .invalidPlist(path):
            return "Invalid property list: \(path)"
        case let .missingText(label, text):
            return "Missing \(label): \(text)"
        case let .unexpectedText(label, text):
            return "Unexpected \(label): \(text)"
        case let .missingPlistKey(key):
            return "Missing required Info.plist key: \(key)"
        case let .invalidPlistValue(key, value):
            return "Invalid Info.plist value for \(key): \(value)"
        case let .secretMarker(file, marker):
            return "Mobile app file \(file) contains forbidden secret marker \(marker)"
        }
    }
}
