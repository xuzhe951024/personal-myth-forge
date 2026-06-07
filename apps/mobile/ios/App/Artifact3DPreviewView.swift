import PersonalMythForgeMobileCore
import SceneKit
import SwiftUI

#if os(iOS)
import UIKit
private typealias PlatformColor = UIColor

private func artifactSceneColor(red: CGFloat, green: CGFloat, blue: CGFloat, alpha: CGFloat = 1) -> PlatformColor {
    UIColor(red: red, green: green, blue: blue, alpha: alpha)
}
#elseif os(macOS)
import AppKit
private typealias PlatformColor = NSColor

private func artifactSceneColor(red: CGFloat, green: CGFloat, blue: CGFloat, alpha: CGFloat = 1) -> PlatformColor {
    NSColor(calibratedRed: red, green: green, blue: blue, alpha: alpha)
}
#endif

struct Artifact3DPreviewView: View {
    let session: MythSession?
    let latestTick: NPCAgentTick?
    private let preparer: ArtifactAssetPreparer
    @State private var preparedAsset: PreparedArtifactAsset?
    @State private var sceneLoadProof = ArtifactSceneLoadProofBuilder.build(
        preparedAsset: nil,
        sceneLoadError: nil
    )

    init(
        session: MythSession?,
        latestTick: NPCAgentTick? = nil,
        preparer: ArtifactAssetPreparer = ArtifactAssetPreparer.live()
    ) {
        self.session = session
        self.latestTick = latestTick
        self.preparer = preparer
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("3D Artifact Preview")
                .font(.headline)

            if let session {
                let preview = preparedAsset?.preview ?? ArtifactPreviewState(session: session)
                let ritualScene = NPCRitualSceneBuilder.build(session: session, latestTick: latestTick)
                let handoffSummary = ArtifactHandoffActionBuilder.build(
                    session: session,
                    preparedAsset: preparedAsset
                )

                SceneView(scene: Self.previewScene(for: preparedAsset, fallback: preview, ritualScene: ritualScene),
                    options: [.allowsCameraControl, .autoenablesDefaultLighting]
                )
                .frame(height: 220)
                .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))

                Text(preparedAsset?.statusTitle ?? preview.statusTitle)
                    .font(.subheadline.weight(.semibold))
                Text(preparedAsset?.statusDetail ?? preview.statusDetail)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                Text(sceneLoadProof.title)
                    .font(.caption)
                    .foregroundStyle(sceneLoadProof.canOpenScene ? Color.green : Color.secondary)
                Text(sceneLoadProof.detail)
                    .font(.caption2)
                    .foregroundStyle(.secondary)
                    .lineLimit(2)
                Text("\(preview.providerLabel) \(preview.formatLabel)")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                Text("NPC ritual: \(Self.ritualStatusText(ritualScene))")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .lineLimit(2)
                Text(Self.assetReferenceText(preparedAsset: preparedAsset, fallback: preview))
                    .font(.caption2)
                    .foregroundStyle(.secondary)
                    .lineLimit(2)
                    .textSelection(.enabled)
                ArtifactHandoffActionsView(
                    summary: handoffSummary,
                    cachedURL: preparedAsset?.cachedURL,
                    retry: retryAssetPreparation
                )
            } else {
                SceneView(scene: Self.placeholderScene(),
                    options: [.autoenablesDefaultLighting]
                )
                .frame(height: 180)
                .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))

                Text("Generated artifact preview appears after forging.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
        }
        .task(id: session?.sessionId) {
            guard let session else {
                await MainActor.run {
                    preparedAsset = nil
                    sceneLoadProof = ArtifactSceneLoadProofBuilder.build(
                        preparedAsset: nil,
                        sceneLoadError: nil
                    )
                }
                return
            }
            await prepareAsset(for: session)
        }
    }

    private func prepareAsset(for session: MythSession) async {
        await MainActor.run {
            preparedAsset = nil
            sceneLoadProof = ArtifactSceneLoadProofBuilder.build(
                preparedAsset: nil,
                sceneLoadError: nil
            )
        }
        let asset = await preparer.prepare(session: session)
        guard !Task.isCancelled else {
            return
        }
        let sceneLoadResult = Self.verifySceneLoad(for: asset)
        guard !Task.isCancelled else {
            return
        }
        await MainActor.run {
            guard !Task.isCancelled else {
                return
            }
            preparedAsset = sceneLoadResult.preparedAsset
            sceneLoadProof = sceneLoadResult.proof
        }
    }

    private func retryAssetPreparation() {
        guard let session else {
            return
        }
        Task {
            await prepareAsset(for: session)
        }
    }

    private static func previewScene(
        for preparedAsset: PreparedArtifactAsset?,
        fallback preview: ArtifactPreviewState,
        ritualScene: NPCRitualScene
    ) -> SCNScene {
        if let sceneURL = preparedAsset?.sceneURL,
           let scene = try? SCNScene(url: sceneURL, options: nil) {
            addNPCRitualOverlay(to: scene, ritualScene: ritualScene)
            return scene
        }

        let scene = placeholderScene()
        let titleNode = SCNNode()
        titleNode.name = preview.title
        scene.rootNode.addChildNode(titleNode)
        addNPCRitualOverlay(to: scene, ritualScene: ritualScene)
        return scene
    }

    private static func verifySceneLoad(
        for preparedAsset: PreparedArtifactAsset
    ) -> (preparedAsset: PreparedArtifactAsset, proof: ArtifactSceneLoadProof) {
        guard let sceneURL = preparedAsset.sceneURL else {
            return (
                preparedAsset,
                ArtifactSceneLoadProofBuilder.build(
                    preparedAsset: preparedAsset,
                    sceneLoadError: nil
                )
            )
        }

        do {
            _ = try SCNScene(url: sceneURL, options: nil)
            return (
                preparedAsset,
                ArtifactSceneLoadProofBuilder.build(
                    preparedAsset: preparedAsset,
                    sceneLoadError: nil
                )
            )
        } catch {
            let failedAsset = preparedAsset.sceneLoadFailure(detail: "SceneKit could not parse the cached generated asset.")
            return (
                failedAsset,
                ArtifactSceneLoadProofBuilder.build(
                    preparedAsset: failedAsset,
                    sceneLoadError: error.localizedDescription
                )
            )
        }
    }

    private static func placeholderScene() -> SCNScene {
        let scene = SCNScene()
        scene.background.contents = ArtifactScenePalette.background

        let camera = SCNCamera()
        let cameraNode = SCNNode()
        cameraNode.camera = camera
        cameraNode.position = SCNVector3(0, 1.4, 4.2)
        cameraNode.eulerAngles.x = -.pi / 12
        scene.rootNode.addChildNode(cameraNode)

        let pedestal = SCNCylinder(radius: 0.72, height: 0.18)
        pedestal.materials = [ArtifactScenePalette.pedestalMaterial()]
        let pedestalNode = SCNNode(geometry: pedestal)
        pedestalNode.position = SCNVector3(0, -0.45, 0)
        scene.rootNode.addChildNode(pedestalNode)

        let relic = SCNTorus(ringRadius: 0.58, pipeRadius: 0.045)
        relic.materials = [ArtifactScenePalette.relicMaterial()]
        let relicNode = SCNNode(geometry: relic)
        relicNode.eulerAngles.x = .pi / 2.9
        relicNode.eulerAngles.y = .pi / 7
        scene.rootNode.addChildNode(relicNode)

        let light = SCNLight()
        light.type = .omni
        light.intensity = 900
        let lightNode = SCNNode()
        lightNode.light = light
        lightNode.position = SCNVector3(0.8, 1.6, 2.4)
        scene.rootNode.addChildNode(lightNode)

        return scene
    }

    private static func addNPCRitualOverlay(to scene: SCNScene, ritualScene: NPCRitualScene) {
        for actor in ritualScene.actors {
            let markerHeight = npcMarkerHeight(for: actor.stance)
            let marker = SCNCylinder(radius: 0.075, height: markerHeight)
            marker.materials = [ArtifactScenePalette.npcMaterial(for: actor.stance)]

            let markerNode = SCNNode(geometry: marker)
            markerNode.name = "\(actor.name) \(actor.stance.rawValue): \(actor.action)"
            markerNode.position = SCNVector3(
                Float(actor.positionX),
                Float(-0.35 + markerHeight / 2),
                Float(actor.positionZ)
            )
            scene.rootNode.addChildNode(markerNode)

            let halo = SCNTorus(ringRadius: 0.15, pipeRadius: 0.012)
            halo.materials = [ArtifactScenePalette.npcHaloMaterial(for: actor.stance)]
            let haloNode = SCNNode(geometry: halo)
            haloNode.name = "\(actor.name) ritual ring"
            haloNode.eulerAngles.x = .pi / 2
            haloNode.position = SCNVector3(Float(actor.positionX), -0.36, Float(actor.positionZ))
            scene.rootNode.addChildNode(haloNode)
        }
    }

    private static func npcMarkerHeight(for stance: NPCRitualStance) -> CGFloat {
        switch stance {
        case .acting:
            return 0.48
        case .debating:
            return 0.4
        case .watching:
            return 0.32
        }
    }

    private static func ritualStatusText(_ ritualScene: NPCRitualScene) -> String {
        let status = ritualScene.actors.map { actor in
            "\(actor.name) \(actor.stance.rawValue)"
        }
        return status.isEmpty ? "waiting" : status.joined(separator: " | ")
    }

    private static func assetReferenceText(
        preparedAsset: PreparedArtifactAsset?,
        fallback preview: ArtifactPreviewState
    ) -> String {
        if let cachedURL = preparedAsset?.cachedURL {
            let filename = cachedURL.lastPathComponent.trimmingCharacters(in: .whitespacesAndNewlines)
            return filename.isEmpty ? "Cached generated asset" : "Cached: \(filename)"
        }
        if preview.uri.lowercased().hasPrefix("file://") {
            return "Local generated asset"
        }
        return preview.uri
    }
}

private enum ArtifactScenePalette {
    static var background: PlatformColor {
        artifactSceneColor(red: 0.045, green: 0.05, blue: 0.06)
    }

    static func pedestalMaterial() -> SCNMaterial {
        let material = SCNMaterial()
        material.diffuse.contents = artifactSceneColor(red: 0.72, green: 0.74, blue: 0.76)
        material.roughness.contents = 0.82
        return material
    }

    static func relicMaterial() -> SCNMaterial {
        let material = SCNMaterial()
        material.diffuse.contents = artifactSceneColor(red: 0.05, green: 0.73, blue: 0.68)
        material.metalness.contents = 0.7
        material.roughness.contents = 0.34
        return material
    }

    static func npcMaterial(for stance: NPCRitualStance) -> SCNMaterial {
        let material = SCNMaterial()
        material.diffuse.contents = npcColor(for: stance)
        material.emission.contents = npcColor(for: stance, alpha: 0.16)
        material.roughness.contents = 0.54
        return material
    }

    static func npcHaloMaterial(for stance: NPCRitualStance) -> SCNMaterial {
        let material = SCNMaterial()
        material.diffuse.contents = npcColor(for: stance, alpha: 0.48)
        material.emission.contents = npcColor(for: stance, alpha: 0.22)
        material.isDoubleSided = true
        return material
    }

    private static func npcColor(for stance: NPCRitualStance, alpha: CGFloat = 1) -> PlatformColor {
        switch stance {
        case .acting:
            return artifactSceneColor(red: 0.95, green: 0.7, blue: 0.22, alpha: alpha)
        case .debating:
            return artifactSceneColor(red: 0.55, green: 0.72, blue: 0.96, alpha: alpha)
        case .watching:
            return artifactSceneColor(red: 0.68, green: 0.86, blue: 0.58, alpha: alpha)
        }
    }
}
