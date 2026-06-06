# Mobile App

The v0.1 client is iOS-first. P0.7 adds a native SwiftPM mobile core scaffold
under `apps/mobile/ios` so the capture-to-myth API loop can be tested locally
without changing global Xcode settings. Unity remains a later candidate for the
full 3D village scene once Unity is available locally.

## Responsibilities

- Capture or upload real-world object imagery.
- Send an object observation and personal context capsule to the backend.
- Render the generated myth artifact in a small village scene.
- Present NPC reactions as text, animation state, movement, and world changes.
- Show the print candidate review screen before any fulfillment action.

## Backend Contract

The first client integration can still call the direct metadata endpoint for local
smoke tests:

```http
POST /v1/myth-sessions
```

with:

```json
{
  "object_observation": {
    "label": "old brass key",
    "materials": ["metal"],
    "source": "phone_capture"
  },
  "context_capsule": {
    "current_theme": "deadline pressure",
    "desired_tone": "tender, strange"
  }
}
```

The backend returns a complete myth session with NPC reactions, generated asset metadata, and a print candidate.

The P0.6 mobile capture path uses a two-call flow:

1. Upload object media and metadata with `POST /v1/object-captures`.
2. Create a session with `POST /v1/myth-sessions/from-capture`.

See `apps/mobile/contracts/capture-api.md` for the API contract and
`apps/mobile/fixtures/` for request payload examples. Local development stores
capture media under the backend `CAPTURE_STORAGE_DIR` setting and returns only
manifest URIs, never raw bytes.

## Unity Setup Notes

Create the Unity project in this directory when Unity is available locally. Use AR Foundation for future AR/camera paths, but v0.1 can start with camera upload plus a regular 3D scene.

## P0.7 iOS Scaffold

Run the local Swift contract tests with:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
```

The current machine's `xcodebuild` points at Command Line Tools, so simulator or
device builds are intentionally deferred. Do not run `xcode-select` or switch the
global developer directory as part of the local test path.

The SwiftUI files under `apps/mobile/ios/App` started as source scaffolding in
P0.7 and are now referenced by the P0.8 Xcode app shell. API keys and provider
secrets must not be committed into the mobile app; use backend-side provider
configuration instead.

## P0.8 Xcode App Shell

P0.8 adds:

```text
apps/mobile/ios/PersonalMythForge.xcodeproj
apps/mobile/ios/App/Info.plist
apps/mobile/ios/App/AppConfiguration.swift
```

Open `PersonalMythForge.xcodeproj` in full Xcode to continue simulator or device
deployment work. The current local environment only has Command Line Tools
selected, so do not run `xcode-select` as part of the repository verification
path.

Run the project-shell inspector with:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
```

Then run the mobile core contract tests:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
```

`PMFBackendBaseURL` in `App/Info.plist` exposes the backend URL for the first API
client wiring. Provider API keys stay on the backend; the mobile app should
never commit OpenAI, Meshy, or print provider secrets.

## P0.9 Scan Capture Draft

P0.9 adds a SwiftPM-verifiable capture draft layer for:

- `single_photo`
- `photo_set`
- `manual_upload`
- `arkit_scan`

The draft layer converts mobile input state into `ObjectCaptureMetadata` plus
`[CaptureUpload]`, then the API client writes safe multipart filenames for image
and scan assets. Supported scan upload content types are:

- `model/gltf-binary` -> `scan_N.glb`
- `model/vnd.usdz+zip` -> `scan_N.usdz`
- `application/octet-stream` -> `scan_N.bin`

This iteration does not wire the live camera, PhotosPicker, or ARKit capture
runtime. It prepares the app source, validation rules, and backend upload
contract so a later full-Xcode/device iteration can attach real capture inputs.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
```

Visual evidence lives at:

```text
docs/superpowers/verification/p0.9-ios-scan-capture.html
docs/superpowers/verification/assets/p0.9-ios-scan-capture-390x844.png
```

## P0.10 Forge Flow Orchestrator

P0.10 adds `ForgeFlowService` to the SwiftPM mobile core. It turns a valid
`CaptureDraft` and `ContextCapsule` into the real backend two-call flow:

1. `uploadObjectCapture(metadata:media:)`
2. `createMythSessionFromCapture(captureId:context:)`

The service emits reducer states for editing, uploading, creating the session,
and ready/error outcomes. `ForgeRootView` now wires the `Forge Myth` button to
that service through source-checked SwiftUI code, while still using sample media
until a later device iteration adds PhotosPicker, fileImporter, or ARKit input.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
```

Visual evidence lives at:

```text
docs/superpowers/verification/p0.10-ios-forge-flow.html
docs/superpowers/verification/assets/p0.10-ios-forge-flow-390x844.png
```

## P0.11 Capture-Aware 3D Generation

P0.11 keeps the iOS surface unchanged and completes the backend/provider data
path behind the existing from-capture flow. When the app creates a myth session
from an uploaded capture, the backend now reads local JPEG/PNG reference media
through the capture store, converts it into a provider-only data URI, and passes
scan asset references alongside the myth prompt. Meshy uses Image-to-3D when an
image source exists; prompt-only generation continues to use Text-to-3D.

Run:

```bash
make backend-lint
make backend-test
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
```

Visual evidence lives at:

```text
docs/superpowers/verification/p0.11-capture-aware-3d.html
docs/superpowers/verification/assets/p0.11-capture-aware-3d-390x844.png
```

Remaining device-facing gaps are unchanged: real PhotosPicker/fileImporter
media selection, ARKit scanning, public or storage-backed media delivery,
multi-image/scan remesh, real provider-key runs, and iOS 3D rendering.

## P0.12 Device Media Input Bridge

P0.12 replaces the app shell's sample media fallback with source-level real
input wiring:

- PhotosPicker for `single_photo`, `photo_set`, and ARKit reference photos.
- fileImporter for `manual_upload` and ARKit scan/model files.
- `CaptureMediaSelection` in the SwiftPM core to summarize selected media,
  enforce mode-level readiness, and build the existing `CaptureDraft`.
- `ForgeRootView` loads selected photo/file bytes into `CaptureMediaDraft`
  values before calling `ForgeFlowService`.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
```

Visual evidence lives at:

```text
docs/superpowers/verification/p0.12-ios-device-media-input.html
docs/superpowers/verification/assets/p0.12-ios-device-media-input-390x844.png
```

Remaining gaps after P0.12 are live camera capture, ARKit mesh capture runtime,
full simulator/device deployment, iOS 3D rendering, and real provider-key runs.

## P0.13 App Compile Gate

P0.13 adds a SwiftPM executable target that compiles the SwiftUI app source
under the local Command Line Tools environment:

```bash
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
```

The gate covers `apps/mobile/ios/App` with `Info.plist` excluded and links the
app shell against `PersonalMythForgeMobileCore`. It caught and fixed:

- iOS-only text input capitalization used directly in `CaptureFormView`.
- macOS 14-only two-argument `onChange` overloads in `ForgeRootView`.
- Swift 6 Sendable/MainActor issues in the forge flow callback path.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
```

Visual evidence lives at:

```text
docs/superpowers/verification/p0.13-ios-app-compile-gate.html
docs/superpowers/verification/assets/p0.13-ios-app-compile-gate-390x844.png
```

Remaining gaps after P0.13 are full Xcode simulator/device deployment, live
ARKit mesh capture, iOS 3D rendering, and real provider-key runs.

## P0.14 iOS 3D Artifact Preview

P0.14 adds the first native 3D artifact preview surface to the app source.
`ArtifactPreviewState` lives in `PersonalMythForgeMobileCore` and classifies
whether a generated asset can be loaded directly by SceneKit. The app layer adds
`Artifact3DPreviewView`, which imports SceneKit, builds an `SCNScene` proxy
artifact, and embeds it in `ArtifactSummaryView`.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
```

Visual evidence lives at:

```text
docs/superpowers/verification/p0.14-ios-3d-artifact-preview.html
docs/superpowers/verification/assets/p0.14-ios-3d-artifact-preview-390x844.png
```

Remaining gaps after P0.14 are actual generated asset download/cache/import,
GLB runtime conversion or USDZ handoff, full Xcode simulator/device deployment,
live ARKit mesh capture, richer 3D village rendering, and real provider-key
runs.

## P0.15 Generated Asset Handoff

P0.15 adds a tested local handoff path for backend-provided generated assets.
`ArtifactAssetPreparer` downloads remote HTTP(S) generated asset URIs, writes
them through an app-local cache abstraction, and returns a `PreparedArtifactAsset`
with `sceneURL` populated for SceneKit-loadable formats. GLB/GLTF assets are
cached but explicitly marked as conversion-required.

`Artifact3DPreviewView` now starts asset preparation when a ready myth session
appears. If the prepared asset has a local `sceneURL`, the view attempts
`SCNScene(url:)`; otherwise it keeps the P0.14 proxy geometry and displays the
handoff status.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
```

Visual evidence lives at:

```text
docs/superpowers/verification/p0.15-ios-generated-asset-handoff.html
docs/superpowers/verification/assets/p0.15-ios-generated-asset-handoff-390x844.png
```

Remaining gaps after P0.15 are provider-side USDZ export or GLB-to-USDZ
conversion, runtime GLB import, full Xcode simulator/device deployment, live
ARKit mesh capture, richer 3D village rendering, and real provider-key runs.

## P0.16 Asset Variant Contract

P0.16 makes the backend generated asset contract multi-format while preserving
the existing primary `generated_asset` fields. New responses may include
`generated_asset.variants`, starting with:

- `game_asset` GLB as the primary in-game asset.
- `ios_scene_asset` USDZ when the backend/provider has a SceneKit-loadable
  derivative.

`GeneratedAsset` in the Swift core decodes missing `variants` as `[]`, so older
fixtures and backend responses remain valid. `ArtifactAssetPreparer` now checks
`preferredSceneVariant` first and downloads/caches that USDZ before falling back
to the primary GLB path.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
```

Visual evidence lives at:

```text
docs/superpowers/verification/p0.16-asset-variant-contract.html
docs/superpowers/verification/assets/p0.16-asset-variant-contract-390x844.png
```

Remaining gaps after P0.16 are runtime GLB import, conversion retry when USDZ is
missing, full Xcode simulator/device deployment, live ARKit mesh capture, richer
3D village rendering, and print asset repair.
