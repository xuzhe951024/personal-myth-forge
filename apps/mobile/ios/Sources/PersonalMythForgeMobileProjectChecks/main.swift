import Foundation

do {
    let repositoryRoot = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
    let iosRoot = repositoryRoot.appendingPathComponent("apps/mobile/ios")
    let appRoot = iosRoot.appendingPathComponent("App")
    let coreRoot = iosRoot.appendingPathComponent("Sources/PersonalMythForgeMobileCore")
    let packageFile = iosRoot.appendingPathComponent("Package.swift")
    let projectFile = iosRoot.appendingPathComponent("PersonalMythForge.xcodeproj/project.pbxproj")
    let plistFile = appRoot.appendingPathComponent("Info.plist")

    let packageManifest = try readText(packageFile)
    let project = try readText(projectFile)
    let plist = try readPropertyList(plistFile)
    let captureFormView = try readText(appRoot.appendingPathComponent("CaptureFormView.swift"))
    let forgeRootView = try readText(appRoot.appendingPathComponent("ForgeRootView.swift"))
    let artifactSummaryView = try readText(appRoot.appendingPathComponent("ArtifactSummaryView.swift"))
    let artifact3DPreviewView = try readText(appRoot.appendingPathComponent("Artifact3DPreviewView.swift"))
    let artifactAssetPreparation = try readText(coreRoot.appendingPathComponent("ArtifactAssetPreparation.swift"))

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

    for file in [
        "AppConfiguration.swift",
        "PersonalMythForgeApp.swift",
        "ForgeRootView.swift",
        "CaptureFormView.swift",
        "ArtifactSummaryView.swift",
        "Artifact3DPreviewView.swift",
        "WorldResolutionView.swift",
        "NPCReactionsView.swift",
    ] {
        try requireContains(project, file, "Xcode project file reference")
    }
    try requirePBXSectionContains(
        project,
        sectionName: "PBXSourcesBuildPhase",
        "10A000000000000000000008 /* Artifact3DPreviewView.swift in Sources */,",
        "3D preview Xcode source membership"
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
    try requirePlistString(plist, key: "PMFBackendBaseURL", expected: "http://127.0.0.1:8080")
    try requirePlistText(plist, key: "NSCameraUsageDescription")
    try requirePlistText(plist, key: "NSPhotoLibraryUsageDescription")
    try requirePlistText(plist, key: "NSPhotoLibraryAddUsageDescription")
    try requireNestedPlistBool(
        plist,
        dictionaryKey: "NSAppTransportSecurity",
        key: "NSAllowsLocalNetworking",
        expected: true
    )
    try requireContains(captureFormView, "CaptureMode", "capture mode app shell source")
    try requireContains(captureFormView, "Scan readiness", "scan readiness app shell source")
    try requireContains(captureFormView, "chooseCapture", "capture button closure")
    try requireContains(captureFormView, "forgeMyth", "forge button closure")
    try requireContains(captureFormView, "PhotosPicker", "photo picker app shell source")
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
    try requireContains(forgeRootView, "ForgeFlowService", "forge flow service source wiring")
    try requireContains(forgeRootView, "forgeService.forge", "forge flow service call")
    try requireContains(forgeRootView, "fileImporter", "file importer app shell source")
    try requireContains(forgeRootView, "loadTransferable(type: Data.self)", "photo data loading source")
    try requireContains(forgeRootView, "UTType", "file content type source")
    try requireContains(forgeRootView, "CaptureMediaSelection", "capture media selection source")
    try requireContains(forgeRootView, "switch selectedCaptureMode", "file importer selected mode source")
    try requireContains(forgeRootView, "guard selectedCaptureMode == mode else", "stale photo load guard")
    try requireContains(forgeRootView, "CaptureInputLoadError.unreadablePhoto", "partial photo load failure source")
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
        artifactSummaryView,
        "Artifact3DPreviewView(session: session)",
        "artifact summary 3D preview wiring"
    )
    try requireContains(artifact3DPreviewView, "import SceneKit", "SceneKit preview source")
    try requireContains(artifact3DPreviewView, "SceneView(scene:", "SwiftUI SceneKit scene view")
    try requireContains(artifact3DPreviewView, "ArtifactPreviewState", "artifact preview state usage")
    try requireContains(artifact3DPreviewView, "SCNScene", "SceneKit scene construction")
    try requireContains(artifact3DPreviewView, "SCNCylinder", "artifact pedestal geometry")
    try requireContains(artifact3DPreviewView, "SCNTorus", "myth artifact proxy geometry")
    try requireContains(artifactAssetPreparation, "ArtifactAssetPreparer", "asset preparation service")
    try requireContains(artifactAssetPreparation, "FileSystemArtifactAssetCache", "asset cache implementation")
    try requireContains(
        artifactAssetPreparation,
        "URLSessionArtifactAssetDownloader",
        "asset downloader implementation"
    )
    try requireContains(artifact3DPreviewView, "ArtifactAssetPreparer.live()", "live asset preparer wiring")
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
