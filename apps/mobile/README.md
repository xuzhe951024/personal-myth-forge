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

## P0.17 NPC Agent Runtime Trace

P0.17 adds mobile-readable NPC agent traces to the myth session contract. The
existing `npc_reactions` still drive the visible village response, while new
fields expose the runtime layer:

- `npc_agent_runtime`
- `npc_agent_traces`
- per-NPC `belief`, `intention`, `proposed_action`, `rationale`, and
  `confidence`

`MythSession` in the Swift core decodes missing trace fields as empty defaults,
so older backend responses still load. `NPCReactionsView` renders compact trace
rows when traces are present.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
```

Visual evidence lives at:

```text
docs/superpowers/verification/p0.17-npc-agent-runtime.html
docs/superpowers/verification/assets/p0.17-npc-agent-runtime-390x844.png
```

Remaining gaps after P0.17 are long-term NPC memory, multi-turn runtime ticks,
Unity movement/action execution, voice NPCs, full Xcode simulator/device
deployment, and live ARKit mesh capture.

## P0.18 Xcode iOS Build Gate

P0.18 adds the first repeatable Xcode project build command for the checked-in
iOS app target:

```bash
make mobile-xcode-build
```

The script behind that target uses `PersonalMythForge.xcodeproj`, the shared
`PersonalMythForge` scheme, `generic/platform=iOS`, local DerivedData under
`apps/mobile/ios/.build/xcode-derived-data`, and `CODE_SIGNING_ALLOWED=NO` plus
`CODE_SIGNING_REQUIRED=NO`. It uses `DEVELOPER_DIR` only as a per-command
environment variable and falls back to `/Applications/Xcode.app/Contents/Developer`.

This remains a build gate, not deployment. It does not run `xcode-select`, accept
the Apple SDK license, launch a simulator, install to a device, archive, or set
up signing. On this machine, the command currently reaches Xcode but is blocked
until the Apple SDK license is accepted in Terminal.

Run the full local source gates with:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
make backend-lint
make backend-test
make mobile-xcode-build
```

Visual evidence lives at:

```text
docs/superpowers/verification/p0.18-xcode-ios-build-gate.html
docs/superpowers/verification/assets/p0.18-xcode-ios-build-gate-390x844.png
```

Remaining gaps after P0.18 are simulator/device installation, signing,
long-running device capture testing, live ARKit mesh capture, richer Unity
movement/action execution, and real provider-key runs.

## P0.19 Guided Scan Entry

P0.19 adds `guided_scan` as a first-class capture mode for the iOS app shell.
`CaptureDraft` validates it as 2-12 image uploads, and
`GuidedScanPhotoSetBuilder` turns Object Capture image directories into sorted
upload media. The app layer adds:

- `Start Guided Scan` in `CaptureFormView`.
- `GuidedScanCaptureView`, an iOS-only RealityKit `ObjectCaptureSession` sheet
  with a macOS fallback so local SwiftPM checks keep running.
- `ForgeRootView.loadGuidedScanDirectory`, which imports the completed photo
  directory into `CaptureMediaSelection(mode: .guidedScan, media: ...)`.

This is a guided photo-set handoff, not local mesh reconstruction. The app and
backend accept JPEG, PNG, HEIC, and HEIF for `guided_scan`. P0.21 adds
backend-side HEIC/HEIF preparation so decodable iPhone captures can become
Meshy-compatible JPEG Image-to-3D inputs during generation.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
make mobile-xcode-build
```

Visual evidence lives at:

```text
docs/superpowers/verification/p0.19-guided-scan-entry.html
docs/superpowers/verification/assets/p0.19-guided-scan-entry-390x844.png
```

Remaining gaps after P0.19 are Apple SDK license acceptance on this machine,
real device Object Capture validation, local reconstruction/photogrammetry,
simulator/device installation, signing, and Unity movement/action execution.

## P0.20 Provider Readiness Preflight

P0.20 adds a backend readiness contract and mobile display for final key/API
handoff. The backend endpoint:

```http
GET /v1/provider-readiness
```

returns rows for `three_d`, `npc`, `print`, and `capture_storage`. Each row
includes the selected provider, readiness status, demo readiness,
real-provider readiness, missing environment variable names, capabilities, and
notes. It never returns raw key values or local absolute storage paths.

The Swift mobile core adds `ProviderReadinessResponse`,
`ProviderReadinessItem`, and `PersonalMythForgeAPIClient.getProviderReadiness()`.
`ForgeRootView` loads the contract on display and renders
`ProviderReadinessView` above the capture form. A missing backend preflight is
shown as non-blocking status text; the app still keeps the forge flow available
for local demos.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
make mobile-xcode-build
```

Visual evidence lives at:

```text
docs/superpowers/verification/p0.20-provider-readiness.html
docs/superpowers/verification/assets/p0.20-provider-readiness-390x844.png
```

Remaining gaps after P0.20 are accepting the Apple SDK license on this machine,
real device Object Capture validation, real Meshy/OpenAI key runs, print
fulfillment adapters, signing, and Unity movement/action execution.

## P0.21 HEIC Meshy Inputs

P0.21 keeps the mobile upload contract unchanged while making iPhone HEIC/HEIF
photos usable by Meshy Image-to-3D. Capture manifests still record original
`image/heic` and `image/heif` media items with their `local-capture://` URIs.
When the app calls `POST /v1/myth-sessions/from-capture`, the backend prepares
provider-facing source images:

- JPEG and PNG pass through unchanged.
- Decodable HEIC and HEIF media is converted into JPEG bytes.
- The resulting `ThreeDSourceImage` keeps the original capture URI but uses
  `content_type: image/jpeg` and a backend-only JPEG data URI.
- Invalid HEIC/HEIF returns a sanitized 422 response instead of silently falling
  back to text-to-3D.

No provider keys, raw media bytes, local filesystem paths, or data URIs are
returned to the mobile app.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
make mobile-xcode-build
```

Regression evidence lives at:

```text
docs/superpowers/verification/2026-06-06-p0.21-heic-meshy-inputs-regression.md
```

Remaining gaps after P0.21 are Apple SDK license acceptance on this machine,
real device Object Capture validation, live Meshy/OpenAI key runs, print
fulfillment adapters, signing, and Unity movement/action execution.

## P0.22 NPC Agent Ticks

P0.22 adds a stateless backend tick loop so the mobile demo can advance NPCs
after the first myth session. The backend endpoint:

```http
POST /v1/npc-ticks
```

accepts the current `MythSession`, a `tick_index`, and short `recent_events`.
It returns `NPCAgentTick` with the same mobile-readable trace and arbitration
shapes used by the initial session:

- `npc_agent_traces`
- `npc_reactions`
- `world_resolution`

The local tick runtime generates deterministic next actions for Mara, Ior, and
Senn, then runs those actions through the existing world arbitrator. It uses
recent event counts without echoing event text, so secrets, data URIs, and raw
personal payloads do not come back to the app.

The Swift mobile core adds `NPCAgentTick` and
`PersonalMythForgeAPIClient.createNPCAgentTick(...)`. `ForgeRootView` renders
`NPCTickView` below the village response with an explicit `Advance Village`
button, runtime label, NPC intentions, accepted/rejected actions, and visible
changes.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
make backend-lint
make backend-test
make mobile-xcode-build
```

Visual evidence lives at:

```text
docs/superpowers/verification/p0.22-npc-agent-ticks.html
docs/superpowers/verification/assets/p0.22-npc-agent-ticks-390x844.png
```

Remaining gaps after P0.22 are persistent server-side tick history, live OpenAI
tick generation, Unity movement execution, real device validation, signing, and
Apple SDK license acceptance on this machine.

## P0.23 OpenAI NPC Tick Provider

P0.23 keeps the iOS contract stable while making the backend tick runtime
provider-driven. When the backend is configured with `NPC_PROVIDER=openai` and
`OPENAI_API_KEY`, `POST /v1/npc-ticks` returns the same `NPCAgentTick` shape but
uses `agent_runtime: openai_tick_structured_runtime`.

The mobile app does not receive or store provider keys. `NPCTickView` already
renders the backend runtime label, NPC traces, accepted/rejected actions, and
visible world changes. This means the same `Advance Village` control works for
local deterministic ticks and OpenAI structured ticks.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
make backend-lint
make backend-test
make mobile-xcode-build
```

Visual evidence lives at:

```text
docs/superpowers/verification/p0.23-openai-npc-tick-provider.html
docs/superpowers/verification/assets/p0.23-openai-npc-tick-provider-390x844.png
```

Remaining gaps after P0.23 are live provider-key acceptance testing, persistent
server-side tick history, Unity movement execution, real device validation,
signing, and Apple SDK license acceptance on this machine.

## P0.24 Provider Handoff Smoke

P0.24 adds a backend CLI handoff report for the moment when Meshy and OpenAI
keys are supplied. The mobile app still does not receive provider secrets. It
continues to read readiness metadata and call the same backend APIs.

Backend handoff command:

```bash
cd services/backend
uv run python -m myth_forge_api.cli provider-handoff \
  --require-core-real \
  --output /tmp/personal-myth-forge-provider-handoff.json
```

`core_real_ready` checks the providers needed for the first iOS/AI/3D demo:
`three_d`, `npc`, and `capture_storage`. Print fulfillment remains visible in
the report but does not block the minimum mobile demo.

Visual evidence lives at:

```text
docs/superpowers/verification/p0.24-provider-handoff-smoke.html
docs/superpowers/verification/assets/p0.24-provider-handoff-smoke-390x844.png
```

Remaining gaps after P0.24 are live provider-key runs, real device validation,
signing, Unity movement execution, persistent tick history, print fulfillment,
and Apple SDK license acceptance on this machine.

## P0.25 iOS Deploy Config

P0.25 moves device deployment inputs into project-local Xcode configuration
files. The app target uses:

```text
apps/mobile/ios/Config/Deployment.xcconfig
```

for shared defaults, including `PRODUCT_BUNDLE_IDENTIFIER`,
`CODE_SIGN_STYLE = Automatic`, and `PMF_BACKEND_BASE_URL`. The real local device
values stay in the ignored file:

```text
apps/mobile/ios/Config/Deployment.local.xcconfig
```

Create it from the example:

```bash
cp apps/mobile/ios/Config/Deployment.local.xcconfig.example \
  apps/mobile/ios/Config/Deployment.local.xcconfig
```

Then set:

- `DEVELOPMENT_TEAM` to the Apple Team ID for local signing.
- `PRODUCT_BUNDLE_IDENTIFIER` to a unique bundle id owned by that team.
- `PMF_BACKEND_BASE_URL` to a Mac/LAN URL reachable from iPhone, such as
  `http://192.168.1.10:8080`.

Run:

```bash
make mobile-deploy-preflight
```

Without local values, this intentionally exits `2` and reports the missing Team
ID plus the loopback backend URL. After the local config is filled, it prints
the bundle id and backend URL without exposing secrets.

After Apple's SDK license is accepted outside Codex, run:

```bash
make mobile-xcode-build
```

Visual evidence lives at:

```text
docs/superpowers/verification/p0.25-ios-deploy-config.html
docs/superpowers/verification/assets/p0.25-ios-deploy-config-390x844.png
```

Remaining gaps after P0.25 are accepting the Apple SDK license on this machine,
real device installation, real Meshy/OpenAI key runs, Unity movement execution,
persistent tick history, and print fulfillment.

## P0.26 Mobile Demo Snapshot

P0.26 adds local continuity for the iOS demo. After a successful forge, the app
saves a versioned `DemoRunSnapshot` containing:

- the latest `MythSession`
- up to 12 local `NPCAgentTick` values for that session
- the snapshot save timestamp

On launch, `ForgeRootView` loads the snapshot and restores the generated relic,
world response, NPC traces, and latest tick history into the same review UI. A
compact `DemoSnapshotStatusView` shows the restored title, saved timestamp, tick
count, and a clear action.

The snapshot is local-only Application Support data. It does not persist raw
capture media, scan binaries, picker state, local file URLs, provider keys,
bearer tokens, or raw personal source documents.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
```

Visual evidence lives at:

```text
docs/superpowers/verification/p0.26-mobile-demo-snapshot.html
docs/superpowers/verification/assets/p0.26-mobile-demo-snapshot-390x844.png
```

Remaining gaps after P0.26 are server-side NPC memory, autonomous background
loops, accepting the Apple SDK license on this machine, real device installation,
real Meshy/OpenAI key runs, Unity movement execution, and print fulfillment.

## P0.27 Backend Session History

P0.27 adds a backend local history contract for demo recovery across clients.
The backend now writes generated myth sessions and NPC ticks into an ignored
JSON store and exposes:

```http
GET /v1/myth-sessions/{session_id}
GET /v1/myth-sessions/{session_id}/history
```

`MYTH_SESSION_STORAGE_DIR` can override the default
`services/backend/.local/myth-sessions` path. The store keeps a bounded history
of 24 NPC ticks per session and sanitizes raw media data URIs, bearer tokens,
API keys, and raw provider payload markers before writing JSON.

The Swift mobile core adds `MythSessionHistory`,
`getMythSession(sessionId:)`, and `getMythSessionHistory(sessionId:)`. Session
ids are validated before network calls using the backend `myth_<16 hex>`
contract.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
make backend-lint
make backend-test
```

Visual evidence lives at:

```text
docs/superpowers/verification/p0.27-backend-session-history.html
docs/superpowers/verification/assets/p0.27-backend-session-history-390x844.png
```

Remaining gaps after P0.27 are production account memory, background autonomous
NPC loops, server-authoritative world simulation, accepting the Apple SDK
license on this machine, real device installation, real provider-key runs, Unity
movement execution, and print fulfillment.

## P0.28 Mobile Backend History Sync

P0.28 connects the P0.27 backend history contract to the app's restored demo
surface. `ForgeRootView` now restores the local `DemoRunSnapshot` immediately,
then non-blockingly calls backend history for valid `myth_<16 hex>` session ids:

```http
GET /v1/myth-sessions/{session_id}/history
```

When backend history is available, the app replaces the visible ready session
and NPC tick history with the backend record and refreshes the local snapshot.
When the backend is unavailable, the app keeps the local restored run visible
and shows a compact fallback status.

The Swift core adds `MythSessionID` so session id validation is shared by the
API client and app source. `DemoRunSnapshot(history:savedAt:)` converts backend
history into the compact local snapshot format.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
make backend-lint
make backend-test
```

Visual evidence lives at:

```text
docs/superpowers/verification/p0.28-mobile-backend-history-sync.html
docs/superpowers/verification/assets/p0.28-mobile-backend-history-sync-390x844.png
```

Remaining gaps after P0.28 are production account sync, server-authoritative
autonomous NPC memory, background tick loops, accepting the Apple SDK license on
this machine, real device installation, real provider-key runs, Unity movement
execution, and print fulfillment.

## P0.29 Server-Owned NPC Advance

P0.29 moves the primary NPC advance path from client-supplied session payloads
to backend-owned stored history. The backend now exposes:

```http
POST /v1/myth-sessions/{session_id}/npc-ticks
```

The endpoint loads the saved `MythSessionHistory`, computes the next tick index
from stored ticks, derives recent events from the latest stored world changes,
runs the configured NPC tick runtime, appends the new tick, and returns updated
history.

`PersonalMythForgeAPIClient.advanceMythSessionHistory(sessionId:)` calls this
endpoint. `ForgeRootView` prefers it for valid backend session ids and applies
the returned history with the same `applyBackendHistory(_:)` path used by app
restore. The stateless `POST /v1/npc-ticks` call remains as a fallback for
legacy/non-backend session ids.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
make backend-lint
make backend-test
```

Visual evidence lives at:

```text
docs/superpowers/verification/p0.29-server-owned-npc-advance.html
docs/superpowers/verification/assets/p0.29-server-owned-npc-advance-390x844.png
```

Remaining gaps after P0.29 are true background autonomous NPC loops, production
account memory, accepting the Apple SDK license on this machine, real device
installation, real Meshy/OpenAI key runs, Unity movement execution, and print
fulfillment.

## P0.30 Bounded Autonomous NPC Run

P0.30 adds a foreground `Run Autonomy` control for valid backend myth sessions.
Instead of requiring three separate taps on `Advance Village`, the app calls:

```http
POST /v1/myth-sessions/{session_id}/autonomy-runs
```

with a bounded `step_count` from `1` to `3`. The backend appends each generated
NPC tick to stored history before generating the next one, then returns an
`NPCAutonomyRun` response containing the requested/completed step counts,
started/completed tick indexes, runtime name, and updated `MythSessionHistory`.

`PersonalMythForgeAPIClient.runMythSessionAutonomy(sessionId:stepCount:)`
performs the POST with a small JSON body. `ForgeRootView.runAutonomy()` requests
three steps and applies `run.history` through the same `applyBackendHistory(_:)`
path used by launch restore, backend history sync, and server-owned single tick
advance. Legacy non-backend session ids are rejected before network calls with
a compact UI message.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
make backend-lint
make backend-test
```

Visual evidence lives at:

```text
docs/superpowers/verification/p0.30-bounded-autonomous-npc-run.html
docs/superpowers/verification/assets/p0.30-bounded-autonomous-npc-run-390x844.png
```

Remaining gaps after P0.30 are true background autonomous NPC loops, production
account memory, accepting the Apple SDK license on this machine, real device
installation, real Meshy/OpenAI key runs, Unity movement execution, and print
fulfillment.

## P0.31 Integrated Demo Acceptance

P0.31 adds a backend CLI acceptance report for the final key handoff and demo
review. It is intentionally backend-first: the mobile app still receives no
provider secrets, and the command can be run before iOS signing/device work is
unblocked.

Run the no-key local integrated acceptance path:

```bash
cd services/backend
uv run python -m myth_forge_api.cli demo-acceptance \
  --provider-mode local \
  --npc-steps 3 \
  --output /tmp/personal-myth-forge-demo-acceptance.json
```

After backend `.env` contains Meshy/OpenAI selection and keys, run the strict
configured path:

```bash
cd services/backend
uv run python -m myth_forge_api.cli demo-acceptance \
  --provider-mode configured \
  --require-real-core \
  --npc-steps 3 \
  --output /tmp/personal-myth-forge-demo-acceptance.json
```

Strict configured mode exits `2` before provider calls until `three_d`, `npc`,
and `capture_storage` are real-provider-ready. Successful reports include the
3D asset provider/format, SceneKit-loadable scene variant when present, initial
NPC runtime, completed bounded NPC ticks, and safety policy.

Visual evidence lives at:

```text
docs/superpowers/verification/p0.31-integrated-demo-acceptance.html
docs/superpowers/verification/assets/p0.31-integrated-demo-acceptance-390x844.png
```

Remaining gaps after P0.31 are accepting the Apple SDK license on this machine,
real device installation, live Meshy/OpenAI key acceptance runs, real device
Object Capture validation, Unity movement execution, background NPC loops,
production account memory, and print fulfillment.

## P0.32 Final Acceptance Report

P0.32 adds one backend CLI command that gathers the mobile-facing deploy gates
alongside provider handoff and demo acceptance:

```bash
cd services/backend
uv run python -m myth_forge_api.cli final-acceptance \
  --profile quick \
  --provider-mode local \
  --output /tmp/personal-myth-forge-final-acceptance.json
```

The quick profile runs:

- provider handoff readiness
- local demo acceptance
- `make mobile-deploy-preflight`
- `make mobile-xcode-build`

Until `apps/mobile/ios/Config/Deployment.local.xcconfig` contains local signing
and iPhone-reachable backend settings, deploy preflight is reported as
`blocked_by_local_ios_deploy_config`. Until the Apple SDK license gate is
handled locally, the Xcode build gate is reported as
`blocked_by_apple_sdk_license`. The command returns `2` for those blockers so
they remain visible without being treated as code failures.

Use `--profile full` to include backend lint/tests and SwiftPM project,
contract, and app compile checks in the same report. Use
`--provider-mode configured --require-real-core` after backend-only Meshy/OpenAI
keys are supplied; strict mode exits before live provider calls until the core
provider set is ready.

Visual evidence lives at:

```text
docs/superpowers/verification/p0.32-final-acceptance-report.html
docs/superpowers/verification/assets/p0.32-final-acceptance-report-390x844.png
```

## P0.33 Meshy Multi-Image Guided Scan

P0.33 makes the existing guided scan photo set materially useful for Meshy.
When the backend prepares two or more JPEG/PNG reference images from an iPhone
guided scan, `MeshyThreeDProvider` calls:

```http
POST /openapi/v1/multi-image-to-3d
```

Provider routing is now:

- 2-4 prepared JPEG/PNG images -> Meshy multi-image-to-3D
- 5+ prepared JPEG/PNG images -> first four images sent to Meshy
- 1 prepared JPEG/PNG image -> Meshy image-to-3D
- 0 prepared images -> Meshy text-to-3D

The mobile app still uploads private capture media only to the backend. The
backend reads local capture storage, converts HEIC/HEIF to JPEG when needed,
creates backend-only data URIs for Meshy, and returns only generated asset
metadata to the app. No Meshy/OpenAI key or raw media data is stored in the iOS
client.

Visual evidence lives at:

```text
docs/superpowers/verification/p0.33-meshy-multi-image-guided-scan.html
docs/superpowers/verification/assets/p0.33-meshy-multi-image-guided-scan-390x844.png
```

Remaining gaps after P0.33 are accepting the Apple SDK license on this machine,
real iPhone deployment, live Meshy/OpenAI key acceptance runs, real device
guided scan quality evaluation, Unity movement execution, production NPC memory,
and print fulfillment.

## P0.34 Generation Provenance Contract

P0.34 adds an optional `generation_provenance` block to generated assets so the
app and acceptance reports can show how a 3D artifact was generated without
exposing source media. The iOS model decodes:

- `input_mode`: `text_prompt`, `single_image`, or `multi_image`
- provider route, such as `/openapi/v1/multi-image-to-3d`
- total and selected source image counts
- source asset count
- `raw_sources_included`, currently `false`

`ArtifactSummaryView` renders a compact generation block only when this field
is present. Older stored sessions without provenance still decode because the
field is optional.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
```

Visual evidence lives at:

```text
docs/superpowers/verification/p0.34-generation-provenance-contract.html
docs/superpowers/verification/assets/p0.34-generation-provenance-contract-390x844.png
```

## P0.35 3D Provider Evaluation Suite

P0.35 is backend-first but directly supports the final iPhone demo handoff. It
adds a fixed `default-v0` suite of 20 non-private 3D generation cases so Meshy
quality can be evaluated consistently once backend-only keys are provided.

Run the no-key local suite:

```bash
cd services/backend
uv run python -m myth_forge_api.cli evaluate-3d \
  --provider local \
  --suite default-v0 \
  --output /tmp/personal-myth-forge-3d-eval.json
```

The report records case category, generated asset provenance, asset variants,
SceneKit-loadable coverage, elapsed time, sanitized errors, and manual review
fields for later artifact scoring. `--provider meshy` uses the same suite after
`MESHY_API_KEY` is supplied on the backend. The mobile app still receives only
generated asset metadata and never stores provider secrets or raw source media.

Visual evidence lives at:

```text
docs/superpowers/verification/p0.35-3d-provider-evaluation-suite.html
docs/superpowers/verification/assets/p0.35-3d-provider-evaluation-suite-390x844.png
```

## P0.36 Media-Backed 3D Evaluation

P0.36 is still backend-first, but it specifically protects the iOS guided scan
handoff. The new `guided-scan-smoke-v0` suite sends synthetic source images
through the 3D provider contract so local runs can verify the same single-image
and multi-image routes used by uploaded phone captures.

Run the no-key smoke suite:

```bash
cd services/backend
uv run python -m myth_forge_api.cli evaluate-3d \
  --provider local \
  --suite guided-scan-smoke-v0 \
  --output /tmp/personal-myth-forge-guided-scan-eval.json
```

The expected local report has three cases, source image counts `1 / 2 / 4`, and
coverage `single_image=1`, `multi_image=2`. The suite uses non-private
synthetic PNG data URIs internally and does not write raw media, local file
paths, or provider secrets into reports. Live iPhone media manifests and real
Meshy runs still require device/provider validation.

Visual evidence lives at:

```text
docs/superpowers/verification/p0.36-media-backed-3d-evaluation.html
docs/superpowers/verification/assets/p0.36-media-backed-3d-evaluation-390x844.png
```

## P0.37 Capture 3D Acceptance Gate

P0.37 brings the guided scan source-image route into the final acceptance
report. The backend quick acceptance profile now runs a local no-key
`capture_3d_acceptance` check that creates a synthetic `guided_scan` capture,
reads three stored source images through the same preparation helper used by
`POST /v1/myth-sessions/from-capture`, and verifies that the 3D provider
receives a multi-image request.

Run:

```bash
cd services/backend
uv run python -m myth_forge_api.cli final-acceptance \
  --profile quick \
  --provider-mode local \
  --output /tmp/personal-myth-forge-final-acceptance.json
```

Expected local summary after P0.37 is `passed=3`, `blocked=2`, `failed=0`.
The blocked checks remain local iOS deploy config and the Apple SDK license on
this machine. The report does not include raw `data:image` payloads,
`local-capture://` URIs, local paths, or provider secrets.

Visual evidence lives at:

```text
docs/superpowers/verification/p0.37-capture-3d-acceptance-gate.html
docs/superpowers/verification/assets/p0.37-capture-3d-acceptance-gate-390x844.png
```
