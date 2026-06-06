import Foundation

public struct ArtifactPreviewState: Equatable, Sendable {
    public let title: String
    public let providerLabel: String
    public let formatLabel: String
    public let uri: String
    public let isSceneLoadable: Bool
    public let statusTitle: String
    public let statusDetail: String

    public init(session: MythSession) {
        self.init(asset: session.generatedAsset, title: session.mythSeed.title)
    }

    public init(asset: GeneratedAsset, title: String) {
        let normalizedFormat = asset.format
            .trimmingCharacters(in: .whitespacesAndNewlines)
            .lowercased()
        let trimmedURI = asset.uri.trimmingCharacters(in: .whitespacesAndNewlines)
        let trimmedTitle = title.trimmingCharacters(in: .whitespacesAndNewlines)
        let trimmedProvider = asset.provider.trimmingCharacters(in: .whitespacesAndNewlines)

        self.title = trimmedTitle.isEmpty ? "Generated Artifact" : trimmedTitle
        self.providerLabel = trimmedProvider.isEmpty ? "unknown" : trimmedProvider
        self.formatLabel = normalizedFormat.isEmpty ? "Unknown" : normalizedFormat.uppercased()
        self.uri = trimmedURI
        self.isSceneLoadable = Self.isSceneLoadable(format: normalizedFormat, uri: trimmedURI)

        let status = Self.status(
            format: normalizedFormat,
            uri: trimmedURI,
            isSceneLoadable: isSceneLoadable
        )
        self.statusTitle = status.title
        self.statusDetail = status.detail
    }

    private static func isSceneLoadable(format: String, uri: String) -> Bool {
        guard uri.lowercased().hasPrefix("file://") else {
            return false
        }
        return ["dae", "scn", "usd", "usdz"].contains(format)
    }

    private static func status(
        format: String,
        uri: String,
        isSceneLoadable: Bool
    ) -> (title: String, detail: String) {
        if uri.isEmpty {
            return (
                "Awaiting 3D asset",
                "The myth session has not returned a usable generated asset URI yet."
            )
        }
        if format.isEmpty {
            return (
                "Awaiting 3D asset format",
                "The myth session returned an asset URI, but it still needs a usable 3D format."
            )
        }
        if isSceneLoadable {
            return (
                "Local scene asset ready",
                "This local asset can be handed to SceneKit in a device build."
            )
        }
        if ["glb", "gltf"].contains(format) {
            return (
                "Generated 3D asset ready",
                "This provider asset is ready for the later download/import step before direct iOS scene loading."
            )
        }
        return (
            "Preview proxy active",
            "The app can show the generated artifact proxy while this format waits for an import path."
        )
    }
}
