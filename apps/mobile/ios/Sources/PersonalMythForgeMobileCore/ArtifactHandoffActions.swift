import Foundation

public enum ArtifactHandoffActionKind: String, Codable, Equatable, Sendable {
    case openScene
    case shareCachedAsset
    case convertRequired
    case retryDownload
    case waiting
}

public enum ArtifactHandoffActionStatus: String, Codable, Equatable, Sendable {
    case waiting
    case ready
    case attention
}

public struct ArtifactHandoffAction: Codable, Equatable, Sendable {
    public var kind: ArtifactHandoffActionKind
    public var title: String
    public var detail: String
    public var status: ArtifactHandoffActionStatus
    public var isEnabled: Bool
    public var isPrimary: Bool

    public init(
        kind: ArtifactHandoffActionKind,
        title: String,
        detail: String,
        status: ArtifactHandoffActionStatus,
        isEnabled: Bool,
        isPrimary: Bool
    ) {
        self.kind = kind
        self.title = title
        self.detail = detail
        self.status = status
        self.isEnabled = isEnabled
        self.isPrimary = isPrimary
    }
}

public struct ArtifactHandoffActionSummary: Codable, Equatable, Sendable {
    public var title: String
    public var detail: String
    public var actions: [ArtifactHandoffAction]
    public var canOpenScene: Bool
    public var canShareCachedAsset: Bool

    public init(
        title: String,
        detail: String,
        actions: [ArtifactHandoffAction],
        canOpenScene: Bool,
        canShareCachedAsset: Bool
    ) {
        self.title = title
        self.detail = detail
        self.actions = actions
        self.canOpenScene = canOpenScene
        self.canShareCachedAsset = canShareCachedAsset
    }
}

public enum ArtifactHandoffActionBuilder {
    public static func build(
        session: MythSession?,
        preparedAsset: PreparedArtifactAsset?
    ) -> ArtifactHandoffActionSummary {
        guard session != nil else {
            return summary(
                title: "Forge an artifact first",
                detail: "Capture or import an object, approve the context capsule, then forge.",
                actions: [
                    action(
                        kind: .waiting,
                        title: "Waiting for Artifact",
                        detail: "No generated 3D artifact is available yet.",
                        status: .waiting,
                        isEnabled: false,
                        isPrimary: false
                    ),
                ],
                canOpenScene: false,
                canShareCachedAsset: false
            )
        }

        guard let preparedAsset else {
            return summary(
                title: "Preparing generated asset",
                detail: "The app is preparing the generated artifact for local preview.",
                actions: [
                    action(
                        kind: .waiting,
                        title: "Preparing Asset",
                        detail: "Download and cache status will appear here.",
                        status: .waiting,
                        isEnabled: false,
                        isPrimary: false
                    ),
                ],
                canOpenScene: false,
                canShareCachedAsset: false
            )
        }

        switch preparedAsset.status {
        case .localSceneReady, .cachedSceneReady:
            return sceneReadySummary(preparedAsset)
        case .cachedRequiresConversion:
            return conversionRequiredSummary(preparedAsset)
        case .downloadFailed:
            return retrySummary()
        case .sceneLoadFailed:
            return retrySummary(
                title: "SceneKit load failed",
                detail: "The generated artifact was cached, but SceneKit could not parse it for preview.",
                actionTitle: "Retry Scene Load"
            )
        case .unsupportedURI:
            return blockedSummary(
                title: "Unsupported asset URI",
                detail: "The generated artifact needs a local file or HTTP(S) URL before mobile handoff.",
                status: .attention
            )
        case .unsupportedFormat:
            return blockedSummary(
                title: "Unsupported 3D format",
                detail: "This generated format is available, but the iPhone handoff cannot open it yet.",
                status: .attention
            )
        case .awaitingAsset:
            return blockedSummary(
                title: "Awaiting 3D asset",
                detail: "The backend has not returned a generated asset URI yet.",
                status: .waiting
            )
        case .awaitingFormat:
            return blockedSummary(
                title: "Awaiting 3D format",
                detail: "The backend returned an asset URI, but not a usable 3D format.",
                status: .waiting
            )
        case .cancelled:
            return blockedSummary(
                title: "Asset preparation cancelled",
                detail: "The current preparation task was cancelled before updating the preview.",
                status: .waiting
            )
        }
    }

    private static func sceneReadySummary(_ preparedAsset: PreparedArtifactAsset) -> ArtifactHandoffActionSummary {
        var actions = [
            action(
                kind: .openScene,
                title: "SceneKit Preview Ready",
                detail: "The preview is using a SceneKit-loadable generated artifact.",
                status: .ready,
                isEnabled: preparedAsset.sceneURL != nil,
                isPrimary: true
            ),
        ]

        if let cachedURL = preparedAsset.cachedURL {
            actions.append(shareAction(cachedURL: cachedURL))
        }

        return summary(
            title: "SceneKit handoff ready",
            detail: "The generated artifact is ready for the in-app 3D preview.",
            actions: actions,
            canOpenScene: preparedAsset.sceneURL != nil,
            canShareCachedAsset: preparedAsset.cachedURL != nil
        )
    }

    private static func conversionRequiredSummary(
        _ preparedAsset: PreparedArtifactAsset
    ) -> ArtifactHandoffActionSummary {
        var actions = [
            action(
                kind: .convertRequired,
                title: "Convert Before SceneKit",
                detail: "Cached GLB/GLTF needs conversion before direct SceneKit loading.",
                status: .attention,
                isEnabled: false,
                isPrimary: true
            ),
        ]

        if let cachedURL = preparedAsset.cachedURL {
            actions.append(shareAction(cachedURL: cachedURL))
        }

        return summary(
            title: "Conversion required",
            detail: "The generated artifact is cached, but it needs conversion before direct iPhone scene loading.",
            actions: actions,
            canOpenScene: false,
            canShareCachedAsset: preparedAsset.cachedURL != nil
        )
    }

    private static func retrySummary(
        title: String = "Asset download failed",
        detail: String = "The app could not cache the generated artifact for local preview.",
        actionTitle: String = "Retry Download"
    ) -> ArtifactHandoffActionSummary {
        summary(
            title: title,
            detail: detail,
            actions: [
                action(
                    kind: .retryDownload,
                    title: actionTitle,
                    detail: "Try preparing the generated artifact again.",
                    status: .attention,
                    isEnabled: true,
                    isPrimary: true
                ),
            ],
            canOpenScene: false,
            canShareCachedAsset: false
        )
    }

    private static func blockedSummary(
        title: String,
        detail: String,
        status: ArtifactHandoffActionStatus
    ) -> ArtifactHandoffActionSummary {
        summary(
            title: title,
            detail: detail,
            actions: [
                action(
                    kind: .waiting,
                    title: title,
                    detail: detail,
                    status: status,
                    isEnabled: false,
                    isPrimary: false
                ),
            ],
            canOpenScene: false,
            canShareCachedAsset: false
        )
    }

    private static func shareAction(cachedURL: URL) -> ArtifactHandoffAction {
        let filename = safeFilename(from: cachedURL)
        return action(
            kind: .shareCachedAsset,
            title: "Share Cached Asset",
            detail: "Cached as \(filename).",
            status: .ready,
            isEnabled: true,
            isPrimary: false
        )
    }

    private static func summary(
        title: String,
        detail: String,
        actions: [ArtifactHandoffAction],
        canOpenScene: Bool,
        canShareCachedAsset: Bool
    ) -> ArtifactHandoffActionSummary {
        ArtifactHandoffActionSummary(
            title: sanitize(title),
            detail: sanitize(detail),
            actions: actions,
            canOpenScene: canOpenScene,
            canShareCachedAsset: canShareCachedAsset
        )
    }

    private static func action(
        kind: ArtifactHandoffActionKind,
        title: String,
        detail: String,
        status: ArtifactHandoffActionStatus,
        isEnabled: Bool,
        isPrimary: Bool
    ) -> ArtifactHandoffAction {
        ArtifactHandoffAction(
            kind: kind,
            title: sanitize(title),
            detail: sanitize(detail),
            status: status,
            isEnabled: isEnabled,
            isPrimary: isPrimary
        )
    }

    private static func safeFilename(from url: URL) -> String {
        let name = url.lastPathComponent.trimmingCharacters(in: .whitespacesAndNewlines)
        if name.isEmpty {
            return "generated-asset"
        }
        return sanitize(name)
    }

    private static func sanitize(_ text: String) -> String {
        var sanitized = text
        let patterns = [
            #"sk-[A-Za-z0-9._-]+"#,
            #"Bearer\s+[A-Za-z0-9._~+/\-=:-]+"#,
            #"Authorization"#,
            #"api[_-]?key\s*[=:]\s*[^\s,;"']+"#,
            #"local-capture://[^\s,;"']+"#,
            #"file://[^\s,;"']+"#,
            #"/Users/[^\s,;"']+"#,
            #"/tmp/[^\s,;"']+"#,
            #"checkout_url"#,
            #"https?://checkout\.[^\s,;"']+"#,
            #"https?://pay\.[^\s,;"']+"#,
        ]
        for pattern in patterns {
            sanitized = sanitized.replacingOccurrences(
                of: pattern,
                with: "[withheld]",
                options: .regularExpression
            )
        }
        return sanitized
    }
}
