import Foundation

do {
    let repositoryRoot = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
    let iosRoot = repositoryRoot.appendingPathComponent("apps/mobile/ios")
    let appRoot = iosRoot.appendingPathComponent("App")
    let projectFile = iosRoot.appendingPathComponent("PersonalMythForge.xcodeproj/project.pbxproj")
    let plistFile = appRoot.appendingPathComponent("Info.plist")

    let project = try readText(projectFile)
    let plist = try readPropertyList(plistFile)

    try requireContains(project, "PersonalMythForge", "Xcode project target name")
    try requireContains(project, #"productType = "com.apple.product-type.application""#, "iOS app product type")
    try requireContains(project, "IPHONEOS_DEPLOYMENT_TARGET = 17.0", "iOS deployment target")
    try requireContains(project, "INFOPLIST_FILE = App/Info.plist", "Info.plist build setting")

    for file in [
        "AppConfiguration.swift",
        "PersonalMythForgeApp.swift",
        "ForgeRootView.swift",
        "CaptureFormView.swift",
        "ArtifactSummaryView.swift",
        "WorldResolutionView.swift",
        "NPCReactionsView.swift",
        "PMFJSON.swift",
        "PMFModels.swift",
        "CaptureID.swift",
        "MultipartFormDataBuilder.swift",
        "PersonalMythForgeAPIClient.swift",
        "ForgeFlowReducer.swift",
    ] {
        try requireContains(project, file, "Xcode project file reference")
    }

    try requirePlistString(plist, key: "CFBundleDisplayName", expected: "Personal Myth Forge")
    try requirePlistString(plist, key: "CFBundleIdentifier", expected: "com.personalmythforge.app")
    try requirePlistString(plist, key: "PMFBackendBaseURL", expected: "http://127.0.0.1:8080")
    try requirePlistText(plist, key: "NSCameraUsageDescription")
    try requirePlistText(plist, key: "NSPhotoLibraryUsageDescription")
    try requirePlistText(plist, key: "NSPhotoLibraryAddUsageDescription")

    try scanForMobileSecrets(in: appRoot)

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

private func scanForMobileSecrets(in directory: URL) throws {
    let secretMarkers = [
        "OPENAI_API_KEY",
        "MESHY_API_KEY",
        "TREATSTOCK_API_KEY",
        "api_key",
        "Bearer ",
    ]
    guard let enumerator = FileManager.default.enumerator(
        at: directory,
        includingPropertiesForKeys: nil
    ) else {
        throw ProjectCheckError.missingFile(directory.path)
    }
    for case let url as URL in enumerator where url.pathExtension == "swift" || url.pathExtension == "plist" {
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
        case let .missingPlistKey(key):
            return "Missing required Info.plist key: \(key)"
        case let .invalidPlistValue(key, value):
            return "Invalid Info.plist value for \(key): \(value)"
        case let .secretMarker(file, marker):
            return "Mobile app file \(file) contains forbidden secret marker \(marker)"
        }
    }
}
