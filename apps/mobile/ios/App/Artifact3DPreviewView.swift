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
    private let preparer: ArtifactAssetPreparer
    @State private var preparedAsset: PreparedArtifactAsset?

    init(session: MythSession?, preparer: ArtifactAssetPreparer = ArtifactAssetPreparer.live()) {
        self.session = session
        self.preparer = preparer
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("3D Artifact Preview")
                .font(.headline)

            if let session {
                let preview = preparedAsset?.preview ?? ArtifactPreviewState(session: session)

                SceneView(scene: Self.previewScene(for: preparedAsset, fallback: preview),
                    options: [.allowsCameraControl, .autoenablesDefaultLighting]
                )
                .frame(height: 220)
                .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))

                Text(preparedAsset?.statusTitle ?? preview.statusTitle)
                    .font(.subheadline.weight(.semibold))
                Text(preparedAsset?.statusDetail ?? preview.statusDetail)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                Text("\(preview.providerLabel) \(preview.formatLabel)")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                Text(preparedAsset?.cachedURL?.absoluteString ?? preview.uri)
                    .font(.caption2)
                    .foregroundStyle(.secondary)
                    .lineLimit(2)
                    .textSelection(.enabled)
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
                }
                return
            }
            await prepareAsset(for: session)
        }
    }

    private func prepareAsset(for session: MythSession) async {
        await MainActor.run {
            preparedAsset = nil
        }
        let asset = await preparer.prepare(session: session)
        await MainActor.run {
            preparedAsset = asset
        }
    }

    private static func previewScene(
        for preparedAsset: PreparedArtifactAsset?,
        fallback preview: ArtifactPreviewState
    ) -> SCNScene {
        if let sceneURL = preparedAsset?.sceneURL,
           let scene = try? SCNScene(url: sceneURL, options: nil) {
            return scene
        }

        let scene = placeholderScene()
        let titleNode = SCNNode()
        titleNode.name = preview.title
        scene.rootNode.addChildNode(titleNode)
        return scene
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
}
