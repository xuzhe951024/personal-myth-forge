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
    let deployConfig = try readText(deployConfigFile)
    let deployLocalExample = try readText(deployLocalExampleFile)
    let sharedScheme = try readText(sharedSchemeFile)
    let gitignore = try readText(gitignoreFile)
    let makefile = try readText(makefileFile)
    let captureFormView = try readText(appRoot.appendingPathComponent("CaptureFormView.swift"))
    let forgeRootView = try readText(appRoot.appendingPathComponent("ForgeRootView.swift"))
    let artifactSummaryView = try readText(appRoot.appendingPathComponent("ArtifactSummaryView.swift"))
    let artifact3DPreviewView = try readText(appRoot.appendingPathComponent("Artifact3DPreviewView.swift"))
    let guidedScanCaptureView = try readText(appRoot.appendingPathComponent("GuidedScanCaptureView.swift"))
    let providerReadinessView = try readText(appRoot.appendingPathComponent("ProviderReadinessView.swift"))
    let npcReactionsView = try readText(appRoot.appendingPathComponent("NPCReactionsView.swift"))
    let npcTickView = try readText(appRoot.appendingPathComponent("NPCTickView.swift"))
    let demoSnapshotStatusView = try readText(appRoot.appendingPathComponent("DemoSnapshotStatusView.swift"))
    let printQuoteReviewView = try readText(appRoot.appendingPathComponent("PrintQuoteReviewView.swift"))
    let finalShowcaseSummaryView = try readText(appRoot.appendingPathComponent("FinalShowcaseSummaryView.swift"))
    let devicePreflightView = try readText(appRoot.appendingPathComponent("DevicePreflightView.swift"))
    let demoScriptView = try readText(appRoot.appendingPathComponent("DemoScriptView.swift"))
    let cameraCaptureView = try readText(appRoot.appendingPathComponent("CameraCaptureView.swift"))
    let pmfModels = try readText(coreRoot.appendingPathComponent("PMFModels.swift"))
    let mythSessionID = try readText(coreRoot.appendingPathComponent("MythSessionID.swift"))
    let demoRunSnapshot = try readText(coreRoot.appendingPathComponent("DemoRunSnapshot.swift"))
    let artifactAssetPreparation = try readText(coreRoot.appendingPathComponent("ArtifactAssetPreparation.swift"))
    let npcRitualScene = try readText(coreRoot.appendingPathComponent("NPCRitualScene.swift"))
    let showcaseAutopilot = try readText(coreRoot.appendingPathComponent("ShowcaseAutopilot.swift"))
    let devicePreflight = try readText(coreRoot.appendingPathComponent("DevicePreflight.swift"))
    let guidedScanPhotoSetBuilder = try readText(coreRoot.appendingPathComponent("GuidedScanPhotoSetBuilder.swift"))
    let arkitScanPackageBuilder = try readText(coreRoot.appendingPathComponent("ARKitScanPackageBuilder.swift"))
    let captureGenerationReadiness = try readText(
        coreRoot.appendingPathComponent("CaptureGenerationReadiness.swift")
    )
    let apiClient = try readText(coreRoot.appendingPathComponent("PersonalMythForgeAPIClient.swift"))
    let contractTests = try readText(
        iosRoot.appendingPathComponent("Sources/PersonalMythForgeMobileCoreContractTests/main.swift")
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
    try requireContains(deployConfig, #"#include? "Deployment.local.xcconfig""#, "optional local deployment include")
    try requireContains(deployLocalExample, "DEVELOPMENT_TEAM = YOUR_TEAM_ID", "local deployment team example")
    try requireContains(deployLocalExample, "PRODUCT_BUNDLE_IDENTIFIER = com.example.personalmythforge", "local bundle id example")
    try requireContains(deployLocalExample, "PMF_BACKEND_BASE_URL = http://192.168.1.10:8080", "device backend URL example")
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
    try requireContains(captureFormView, "chooseCapture", "capture button closure")
    try requireContains(captureFormView, "let takePhoto: () -> Void", "camera action form input")
    try requireContains(captureFormView, "Take Photo", "single photo camera action")
    try requireContains(captureFormView, "startGuidedScan", "guided scan button closure")
    try requireContains(captureFormView, "forgeMyth", "forge button closure")
    try requireContains(captureFormView, "PhotosPicker", "photo picker app shell source")
    try requireContains(captureFormView, "Start Guided Scan", "guided scan primary action")
    try requireContains(captureFormView, "Guided scan", "guided scan mode label")
    try requireContains(captureFormView, "let isMediaReadyForUpload", "media readiness form input")
    try requireContains(captureFormView, ".disabled(!isMediaReadyForUpload)", "disabled forge button source")
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
    try requireContains(forgeRootView, "FinalShowcaseSummaryView(", "final showcase summary view wiring")
    try requireContains(forgeRootView, "FinalShowcaseSummaryBuilder.build", "final showcase summary builder wiring")
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
    try requireContains(forgeRootView, "DevicePreflightSummaryBuilder.build", "device preflight summary wiring")
    try requireContains(forgeRootView, "DevicePreflightView(summary:", "device preflight view wiring")
    try requireContains(forgeRootView, "finalDemoLaunch", "final demo launch root state")
    try requireContains(forgeRootView, "loadFinalDemoLaunch", "final demo launch app load path")
    try requireContains(forgeRootView, "getFinalDemoLaunch(mode: \"local\")", "final demo launch API call")
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
    try requireContains(npcTickView, "Run Autonomy", "autonomy run button label")
    try requireContains(npcTickView, "runAutonomy", "autonomy run button action")
    try requireContains(finalShowcaseSummaryView, "Final Showcase", "final showcase summary title")
    try requireContains(finalShowcaseSummaryView, "privacyNotes", "final showcase privacy note rendering")
    try requireContains(devicePreflightView, "Device Preflight", "device preflight title")
    try requireContains(devicePreflightView, "backendBaseURL", "device preflight backend URL")
    try requireContains(devicePreflightView, "checkBackend", "device preflight check action")
    try requireContains(devicePreflightView, "Check", "device preflight check button")
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
    try requireContains(pmfModels, "FinalDemoLaunchReport", "final demo launch report model")
    try requireContains(pmfModels, "FinalDemoLaunchPhase", "final demo launch phase model")
    try requireContains(pmfModels, "FinalResourcesPreflightReport", "final resources preflight report model")
    try requireContains(pmfModels, "FinalResourcesFileStatus", "final resources file status model")
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
    try requireContains(artifactSummaryView, "let latestTick: NPCAgentTick?", "artifact summary latest tick input")
    try requireContains(
        artifactSummaryView,
        "generationProvenance",
        "artifact summary provenance display"
    )
    try requireContains(
        artifactSummaryView,
        "selectedSourceImageCount",
        "artifact summary selected source image count"
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
        contractTests,
        "testARKitScanPackageBuilderBuildsReadySelection",
        "ARKit scan package contract test"
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
    try requireContains(npcTickView, "Advance Village", "npc tick action label")
    try requireContains(npcTickView, "tickHistoryCount", "npc tick history count input")
    try requireContains(npcTickView, "agentRuntime", "npc tick runtime display")
    try requireContains(npcTickView, "acceptedActions", "npc tick accepted actions")
    try requireContains(npcTickView, "rejectedActions", "npc tick rejected actions")
    try requireContains(npcTickView, "visibleChanges", "npc tick visible changes")
    try requireNotContains(npcTickView, "sk-", "npc tick secret sample")
    try requireContains(demoScriptView, "ShowcaseAutopilotPlan", "demo script autopilot input")
    try requireContains(demoScriptView, "Button(action: runAutopilot)", "demo script autopilot button")
    try requireContains(showcaseAutopilot, "ShowcaseAutopilotPlanner", "showcase autopilot core planner")
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
