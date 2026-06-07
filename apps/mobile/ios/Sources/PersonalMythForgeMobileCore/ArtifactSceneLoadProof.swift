import Foundation

public enum ArtifactSceneLoadProofStatus: String, Codable, Equatable, Sendable {
    case waiting
    case loaded
    case conversionRequired
    case failed
    case unavailable
}

public struct ArtifactSceneLoadProof: Codable, Equatable, Sendable {
    public let status: ArtifactSceneLoadProofStatus
    public let title: String
    public let detail: String
    public let canOpenScene: Bool

    public init(
        status: ArtifactSceneLoadProofStatus,
        title: String,
        detail: String,
        canOpenScene: Bool
    ) {
        self.status = status
        self.title = title
        self.detail = detail
        self.canOpenScene = canOpenScene
    }
}

public enum ArtifactSceneLoadProofBuilder {
    public static func build(
        preparedAsset: PreparedArtifactAsset?,
        sceneLoadError: String?
    ) -> ArtifactSceneLoadProof {
        guard let preparedAsset else {
            return proof(
                .waiting,
                title: "SceneKit load proof: Waiting",
                detail: "Generated asset is still preparing.",
                canOpenScene: false
            )
        }

        switch preparedAsset.status {
        case .localSceneReady, .cachedSceneReady:
            return proof(
                .loaded,
                title: "SceneKit load proof: Loaded",
                detail: "SceneKit parsed the generated scene asset.",
                canOpenScene: true
            )
        case .cachedRequiresConversion:
            return proof(
                .conversionRequired,
                title: "SceneKit load proof: Conversion needed",
                detail: "Cached GLB/GLTF needs conversion before SceneKit can parse it.",
                canOpenScene: false
            )
        case .sceneLoadFailed:
            let errorDetail = sceneLoadError.map { " \($0)" } ?? ""
            return proof(
                .failed,
                title: "SceneKit load proof: Failed",
                detail: "SceneKit could not parse the generated scene asset.\(errorDetail)",
                canOpenScene: false
            )
        case .downloadFailed:
            return proof(
                .unavailable,
                title: "SceneKit load proof: Download failed",
                detail: "The generated scene asset was not cached.",
                canOpenScene: false
            )
        default:
            return proof(
                .unavailable,
                title: "SceneKit load proof: Unavailable",
                detail: preparedAsset.statusDetail,
                canOpenScene: false
            )
        }
    }

    private static func proof(
        _ status: ArtifactSceneLoadProofStatus,
        title: String,
        detail: String,
        canOpenScene: Bool
    ) -> ArtifactSceneLoadProof {
        ArtifactSceneLoadProof(
            status: status,
            title: sanitize(title),
            detail: sanitize(detail),
            canOpenScene: canOpenScene
        )
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
