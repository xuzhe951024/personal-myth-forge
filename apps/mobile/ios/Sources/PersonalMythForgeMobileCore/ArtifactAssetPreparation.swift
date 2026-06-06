import Foundation

public enum PreparedArtifactAssetStatus: String, Equatable, Sendable {
    case awaitingAsset
    case localSceneReady
    case cachedSceneReady
    case cachedRequiresConversion
    case unsupportedURI
    case unsupportedFormat
    case downloadFailed
}

public struct PreparedArtifactAsset: Equatable, Sendable {
    public let preview: ArtifactPreviewState
    public let sourceURI: String
    public let cachedURL: URL?
    public let sceneURL: URL?
    public let status: PreparedArtifactAssetStatus
    public let statusTitle: String
    public let statusDetail: String

    public init(
        preview: ArtifactPreviewState,
        sourceURI: String,
        cachedURL: URL?,
        sceneURL: URL?,
        status: PreparedArtifactAssetStatus,
        statusTitle: String,
        statusDetail: String
    ) {
        self.preview = preview
        self.sourceURI = sourceURI
        self.cachedURL = cachedURL
        self.sceneURL = sceneURL
        self.status = status
        self.statusTitle = statusTitle
        self.statusDetail = statusDetail
    }
}

public protocol ArtifactAssetDownloader: Sendable {
    func download(from url: URL) async throws -> Data
}

public protocol ArtifactAssetCache: Sendable {
    func store(data: Data, filename: String) async throws -> URL
}

public struct URLSessionArtifactAssetDownloader: ArtifactAssetDownloader, Sendable {
    public init() {}

    public func download(from url: URL) async throws -> Data {
        let (data, response) = try await URLSession.shared.data(from: url)
        guard let httpResponse = response as? HTTPURLResponse else {
            throw ForgeFlowError.transport("Expected HTTP response.")
        }
        guard (200...299).contains(httpResponse.statusCode) else {
            throw ForgeFlowError.httpStatus(httpResponse.statusCode, "Generated asset download failed.")
        }
        return data
    }
}

public struct FileSystemArtifactAssetCache: ArtifactAssetCache, Sendable {
    public let rootDirectory: URL

    public init(rootDirectory: URL) {
        self.rootDirectory = rootDirectory
    }

    public func store(data: Data, filename: String) async throws -> URL {
        try FileManager.default.createDirectory(
            at: rootDirectory,
            withIntermediateDirectories: true
        )
        let destination = rootDirectory.appendingPathComponent(filename)
        try data.write(to: destination, options: [.atomic])
        return destination
    }
}

public struct ArtifactAssetPreparer: Sendable {
    private static let sceneKitFormats: Set<String> = ["dae", "scn", "usd", "usdz"]
    private static let conversionRequiredFormats: Set<String> = ["glb", "gltf"]

    private let downloader: any ArtifactAssetDownloader
    private let cache: any ArtifactAssetCache

    public init(downloader: any ArtifactAssetDownloader, cache: any ArtifactAssetCache) {
        self.downloader = downloader
        self.cache = cache
    }

    public static func live() -> ArtifactAssetPreparer {
        let cacheRoot = FileManager.default.urls(for: .cachesDirectory, in: .userDomainMask)
            .first?
            .appendingPathComponent("PersonalMythForge", isDirectory: true)
            .appendingPathComponent("GeneratedAssets", isDirectory: true)
            ?? FileManager.default.temporaryDirectory
                .appendingPathComponent("PersonalMythForge", isDirectory: true)
                .appendingPathComponent("GeneratedAssets", isDirectory: true)

        return ArtifactAssetPreparer(
            downloader: URLSessionArtifactAssetDownloader(),
            cache: FileSystemArtifactAssetCache(rootDirectory: cacheRoot)
        )
    }

    public func prepare(session: MythSession) async -> PreparedArtifactAsset {
        let preview = ArtifactPreviewState(session: session)
        let format = session.generatedAsset.format
            .trimmingCharacters(in: .whitespacesAndNewlines)
            .lowercased()
        let uri = preview.uri

        guard !uri.isEmpty else {
            return PreparedArtifactAsset(
                preview: preview,
                sourceURI: uri,
                cachedURL: nil,
                sceneURL: nil,
                status: .awaitingAsset,
                statusTitle: preview.statusTitle,
                statusDetail: preview.statusDetail
            )
        }

        guard let sourceURL = URL(string: uri), let scheme = sourceURL.scheme?.lowercased() else {
            return unsupportedURI(preview: preview, sourceURI: uri)
        }

        if scheme == "file" {
            return prepareLocalAsset(preview: preview, sourceURL: sourceURL, format: format)
        }

        guard scheme == "http" || scheme == "https" else {
            return unsupportedURI(preview: preview, sourceURI: uri)
        }

        do {
            let data = try await downloader.download(from: sourceURL)
            let cachedURL = try await cache.store(
                data: data,
                filename: cacheFilename(
                    sessionId: session.sessionId,
                    provider: session.generatedAsset.provider,
                    format: format
                )
            )
            return prepareCachedAsset(preview: preview, sourceURL: sourceURL, cachedURL: cachedURL, format: format)
        } catch {
            return PreparedArtifactAsset(
                preview: preview,
                sourceURI: uri,
                cachedURL: nil,
                sceneURL: nil,
                status: .downloadFailed,
                statusTitle: "Generated asset download failed",
                statusDetail: "The app could not cache the generated asset for local 3D handoff."
            )
        }
    }

    private func prepareLocalAsset(
        preview: ArtifactPreviewState,
        sourceURL: URL,
        format: String
    ) -> PreparedArtifactAsset {
        if Self.sceneKitFormats.contains(format) {
            return PreparedArtifactAsset(
                preview: preview,
                sourceURI: preview.uri,
                cachedURL: sourceURL,
                sceneURL: sourceURL,
                status: .localSceneReady,
                statusTitle: "Local SceneKit asset ready",
                statusDetail: "This generated asset is already available as a local SceneKit-loadable file."
            )
        }

        return unsupportedFormat(preview: preview, sourceURI: preview.uri, cachedURL: sourceURL)
    }

    private func prepareCachedAsset(
        preview: ArtifactPreviewState,
        sourceURL: URL,
        cachedURL: URL,
        format: String
    ) -> PreparedArtifactAsset {
        if Self.sceneKitFormats.contains(format) {
            return PreparedArtifactAsset(
                preview: preview,
                sourceURI: sourceURL.absoluteString,
                cachedURL: cachedURL,
                sceneURL: cachedURL,
                status: .cachedSceneReady,
                statusTitle: "Cached SceneKit asset ready",
                statusDetail: "The generated asset has been downloaded into the app cache and can be handed to SceneKit."
            )
        }

        if Self.conversionRequiredFormats.contains(format) {
            return PreparedArtifactAsset(
                preview: preview,
                sourceURI: sourceURL.absoluteString,
                cachedURL: cachedURL,
                sceneURL: nil,
                status: .cachedRequiresConversion,
                statusTitle: "Cached asset needs conversion",
                statusDetail: "The generated GLB/GLTF asset is cached locally, but it still needs conversion before direct SceneKit loading."
            )
        }

        return unsupportedFormat(preview: preview, sourceURI: sourceURL.absoluteString, cachedURL: cachedURL)
    }

    private func unsupportedURI(preview: ArtifactPreviewState, sourceURI: String) -> PreparedArtifactAsset {
        PreparedArtifactAsset(
            preview: preview,
            sourceURI: sourceURI,
            cachedURL: nil,
            sceneURL: nil,
            status: .unsupportedURI,
            statusTitle: "Unsupported asset URI",
            statusDetail: "The generated asset URI must be a local file or an HTTP(S) URL before the app can prepare it."
        )
    }

    private func unsupportedFormat(
        preview: ArtifactPreviewState,
        sourceURI: String,
        cachedURL: URL?
    ) -> PreparedArtifactAsset {
        PreparedArtifactAsset(
            preview: preview,
            sourceURI: sourceURI,
            cachedURL: cachedURL,
            sceneURL: nil,
            status: .unsupportedFormat,
            statusTitle: "Unsupported 3D asset format",
            statusDetail: "The generated asset is available, but this format is not yet supported by the iOS handoff path."
        )
    }

    private func cacheFilename(sessionId: String, provider: String, format: String) -> String {
        let safeSession = safeFilenameComponent(sessionId, fallback: "myth-session")
        let safeProvider = safeFilenameComponent(provider, fallback: "provider")
        let safeFormat = safeFilenameComponent(format, fallback: "asset")
        return "\(safeSession)-\(safeProvider).\(safeFormat)"
    }

    private func safeFilenameComponent(_ value: String, fallback: String) -> String {
        let allowed = CharacterSet.alphanumerics.union(CharacterSet(charactersIn: "_-"))
        let trimmed = value.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        let scalars = trimmed.unicodeScalars.map { scalar in
            allowed.contains(scalar) ? Character(scalar) : "-"
        }
        let sanitized = String(scalars)
            .split(separator: "-", omittingEmptySubsequences: true)
            .joined(separator: "-")
        return sanitized.isEmpty ? fallback : sanitized
    }
}
