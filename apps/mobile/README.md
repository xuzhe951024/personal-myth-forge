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

## Local Device Config Handoff

For a physical iPhone demo, run the backend on a LAN-reachable interface:

```bash
make backend-device-demo
```

Then write the ignored local iOS deploy config from explicit values:

```bash
DEVELOPMENT_TEAM=ABCDE12345 \
PRODUCT_BUNDLE_IDENTIFIER=com.example.personalmythforge \
PMF_BACKEND_BASE_URL=http://192.168.1.10:8080 \
make mobile-write-deploy-config
```

Validate the handoff before opening Xcode or connecting a device:

```bash
make mobile-deploy-preflight
```

The writer only creates `apps/mobile/ios/Config/Deployment.local.xcconfig`. That
file is ignored by git, should not contain provider keys, and is guarded against
being tracked. The preflight then checks required signing values, rejects
loopback backend URLs for device demos, and calls `$PMF_BACKEND_BASE_URL/health`.

P0.63 adds a consolidated final demo launch report for the operator handoff:

```bash
make final-demo-launch
```

That local mode is a no-key dry run. After backend provider keys and iOS deploy
values are supplied through the unified final resource file, apply them and run
configured mode:

```bash
mkdir -p services/backend/.local
cp services/backend/final-resources.env.example services/backend/.local/final-resources.env
$EDITOR services/backend/.local/final-resources.env
make final-resources-preflight
make final-apply-resources
cd services/backend
uv run python -m myth_forge_api.cli final-demo-launch --mode configured --repo-root ../..
```

The read-only preflight checks the final resources file before any ignored
config is written. The launch report then shows `final_resources_preflight` and
`apply_final_resources`, followed by the backend device-server, provider
readiness, configured final acceptance, deploy preflight, and Xcode build-gate
commands. It does not store mobile provider secrets and does not mutate Xcode,
signing, or global developer settings.

P0.64 exposes the same sanitized status through:

```http
GET /v1/final-demo-launch?mode=local
```

`ForgeRootView` loads that report and passes it into `DevicePreflightSummary`.
The device preflight panel now includes a `Final Launch` row so the operator can
see the final launch lane state directly on the phone.

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
MESHY_API_KEY=... \
OPENAI_API_KEY=... \
make backend-write-provider-env

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
make backend-device-demo
make mobile-deploy-preflight
```

Without local values, this intentionally exits `2` and reports the missing Team
ID plus the loopback backend URL. After the local config is filled, it prints
the bundle id and backend URL without exposing secrets. `backend-device-demo`
binds the FastAPI backend to `0.0.0.0:8080`; use it when
`PMF_BACKEND_BASE_URL` points at the Mac LAN address from a physical iPhone.

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
configured path. Leaving off `--allow-live-provider-calls` is a safe dry check
that blocks before Meshy/OpenAI calls once live providers are ready; add the
flag only for intentional live validation:

```bash
cd services/backend
uv run python -m myth_forge_api.cli demo-acceptance \
  --provider-mode configured \
  --require-real-core \
  --allow-live-provider-calls \
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
`--provider-mode configured --require-real-core --allow-live-provider-calls`
only after backend-only Meshy/OpenAI keys are supplied and you intentionally
want the live provider validation run. Without the consent flag, configured
mode blocks before contacting live providers.

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

## P0.38 Print Quote Handoff

P0.38 keeps the mobile UI unchanged and adds the backend contract the app will
eventually call from a print review screen:

```http
POST /v1/print-quotes
```

The request carries a backend-produced `print_candidate`, quantity, material,
finish, and shipping country. The current local provider returns a deterministic
`draft_quote` for review:

- provider `local_stub`
- `USD 16.00` per item
- five production days and six shipping days
- `requires_user_approval: true`
- no checkout/payment URL

Provider readiness now has `PRINT_PROVIDER`, `TREATSTOCK_API_KEY`, and
`SCULPTEO_API_KEY` slots for future live quote adapters. Configured
Treatstock/Sculpteo keys are not returned to the app, and those providers are
not returned to the app. Treatstock becomes real-provider-ready in P0.62;
Sculpteo remains a future adapter.

Run:

```bash
cd services/backend
uv run python -m myth_forge_api.cli final-acceptance \
  --profile quick \
  --provider-mode local \
  --output /tmp/personal-myth-forge-final-acceptance.json
```

Expected local summary after P0.38 is `passed=4`, `blocked=2`, `failed=0`.
The new passing check is `print_quote_acceptance`; local deploy config and the
Apple SDK license remain blocked on this machine.

Visual evidence lives at:

```text
docs/superpowers/verification/p0.38-print-quote-handoff.html
docs/superpowers/verification/assets/p0.38-print-quote-handoff-390x844.png
```

## P0.39 Mobile Print Quote Review

P0.39 connects the P0.38 quote contract to the iOS app source. A ready myth
session now renders `PrintQuoteReviewView` below the NPC controls. The panel
shows the backend-produced `print_candidate`, then lets the user tap `Get Quote`
to call:

```http
POST /v1/print-quotes
```

The Swift mobile core adds `PrintQuoteRequest`, `PrintQuote`, and
`PersonalMythForgeAPIClient.createPrintQuote(...)`. The app sends the current
session's print candidate with local review defaults:

- quantity `1`
- material `standard_resin`
- finish `matte`
- ship-to country `US`

The local backend returns a `draft_quote` for `USD 16.00`, five production days,
six shipping days, and `requires_user_approval: true`. The app displays that as
review information only. It does not open checkout URLs, submit orders, collect
payment, or store provider keys.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
```

Final acceptance quick remains `passed=4`, `blocked=2`, `failed=0`; the blocked
checks are still local deploy config and the Apple SDK license on this machine.

Visual evidence lives at:

```text
docs/superpowers/verification/p0.39-mobile-print-quote-review.html
docs/superpowers/verification/assets/p0.39-mobile-print-quote-review-390x844.png
```

## P0.40 Resource Handoff Bundle

P0.40 adds one backend CLI report for the final operator resource handoff. It
consolidates:

- backend-only Meshy/OpenAI provider settings and keys
- print provider key slots for future Treatstock/Sculpteo work
- iOS `Deployment.local.xcconfig` values for Team ID, bundle id, and backend URL
- the Apple SDK license/build gate
- next commands for resource handoff, final acceptance, deploy preflight, and
  Xcode build

Run:

```bash
cd services/backend
uv run python -m myth_forge_api.cli resource-handoff \
  --repo-root ../.. \
  --output /tmp/personal-myth-forge-resource-handoff.json
```

The mobile app still receives only backend-generated state and readiness
metadata. Meshy, OpenAI, Treatstock, and Sculpteo key values stay in backend
configuration, not iOS source, `Info.plist`, screenshots, or error text. The
default report exits `2` until a local `Deployment.local.xcconfig` supplies an
Apple Team ID and a non-loopback backend URL reachable from iPhone.
Use `make backend-write-provider-env` to create the ignored backend
`services/backend/.env` before running this report. The writer redacts command
output and does not make provider network calls.

Visual evidence lives at:

```text
docs/superpowers/verification/p0.40-resource-handoff-bundle.html
docs/superpowers/verification/assets/p0.40-resource-handoff-bundle-390x844.png
```

## P0.41 Final Showcase Summary

P0.41 adds a compact `Final Showcase` panel near the top of `ForgeRootView`.
The summary is computed on-device from state the app already has:

- current capture media readiness
- generated 3D asset provider, format, and provenance input mode
- initial NPC agent runtime plus saved NPC tick count
- print candidate or quote state
- backend provider readiness
- fixed privacy notes for raw media, provider keys, checkout links, and local
  file paths

The Swift mobile core owns `FinalShowcaseSummaryBuilder`, so the readiness rules
are covered by contract tests. The SwiftUI panel is source-checked and compiled
through the existing app compile gate. This does not add a new backend endpoint,
call live providers, install to a device, configure signing, or store secrets in
the app.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
```

Visual evidence lives at:

```text
docs/superpowers/verification/p0.41-final-showcase-summary.html
docs/superpowers/verification/assets/p0.41-final-showcase-summary-390x844.png
```

## P0.42 iOS Camera Capture Bridge

P0.42 adds a direct `Take Photo` action to single-photo mode in
`CaptureFormView`. On iOS, `CameraCaptureView` wraps `UIImagePickerController`
behind compile guards, converts the captured image into JPEG bytes, and passes
those bytes through `CameraCaptureMediaBuilder.singlePhotoSelection(...)`.

The resulting media selection uses the existing upload contract:

- mode `single_photo`
- filename `camera-capture.jpg`
- content type `image/jpeg`
- no provider keys or raw media in demo snapshots

`Choose Photo` remains visible as a fallback for simulator/source-level demos.
This iteration does not claim real iPhone camera validation; that remains part
of final device acceptance after local signing and LAN backend configuration.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
```

Visual evidence lives at:

```text
docs/superpowers/verification/p0.42-ios-camera-capture-bridge.html
docs/superpowers/verification/assets/p0.42-ios-camera-capture-bridge-390x844.png
```

## P0.43 iOS Showcase Acceptance

P0.43 adds a backend-side source acceptance check named
`ios_showcase_acceptance`. It is included in
`final-acceptance --profile quick` and verifies that the checked-in iOS source
still contains the complete minimal showcase surface:

- `Take Photo` camera capture
- guided Object Capture scan entry
- capture upload and myth session creation
- SceneKit/asset handoff preview
- NPC agent advance/autonomy controls
- print quote review
- provider readiness display
- final showcase summary
- project-local deploy config and camera permission strings

This check only reads repository files. It does not run SwiftPM, Xcode,
simulators, devices, provider APIs, or network calls. The full profile and
separate Swift checks still provide compile evidence, while final device
acceptance still requires local signing, LAN backend configuration, Apple SDK
license acceptance, and a real iPhone run.

Expected quick final acceptance on a local no-key checkout:

```text
passed=5, blocked=2, failed=0
```

The blocked checks remain `mobile_deploy_preflight` and `mobile_xcode_build`.

Visual evidence lives at:

```text
docs/superpowers/verification/p0.43-ios-showcase-acceptance.html
docs/superpowers/verification/assets/p0.43-ios-showcase-acceptance-390x844.png
```

## P0.44 Live Provider Consent Gate

P0.44 keeps mobile secrets backend-only and makes the final Meshy/OpenAI
provider validation explicit. `demo-acceptance` and `final-acceptance` now
default to no live provider calls. If `.env` selects ready Meshy/OpenAI
providers, configured mode exits `2` before contacting them unless the operator
passes `--allow-live-provider-calls`.

Safe local acceptance remains:

```bash
cd services/backend
uv run python -m myth_forge_api.cli final-acceptance \
  --profile quick \
  --provider-mode local \
  --output /tmp/personal-myth-forge-final-acceptance.json
```

Intentional live provider validation is:

```bash
cd services/backend
uv run python -m myth_forge_api.cli final-acceptance \
  --profile quick \
  --provider-mode configured \
  --require-real-core \
  --allow-live-provider-calls \
  --output /tmp/personal-myth-forge-final-acceptance.json
```

## P0.45 iPhone Backend Handoff

P0.45 makes the real-device backend launch path explicit without running a
device, mutating Xcode settings, or changing global machine state. Local
Mac/browser development still uses:

```bash
make backend-dev
```

For a physical iPhone on the same LAN, start:

```bash
make backend-device-demo
```

Then set `PMF_BACKEND_BASE_URL` in the ignored
`apps/mobile/ios/Config/Deployment.local.xcconfig` to the Mac LAN URL, not
`127.0.0.1`. Quick final acceptance now includes
`ios_backend_handoff_acceptance`, which verifies the Make target, LAN URL
example, loopback guard, Info.plist handoff, and runtime config lookup. On this
machine the expected quick summary is `passed=6, blocked=2, failed=0`; the
remaining blockers are local signing config and the Apple SDK/Xcode license
gate.

## P0.49 Mobile Demo Script

P0.49 adds a compact `Demo Script` panel to the iOS app. It appears below the
final showcase summary and turns current app state into a live operator
checklist:

- Capture Object
- Forge Myth
- Load 3D Scene
- Run NPC Autonomy
- Request Print Quote
- Check Resources

The script marks each step as waiting, current, complete, optional, or blocked
and keeps the next action visible at the top of the panel. It uses only typed
state already present in the app: media selection, myth session, NPC tick count,
print quote, provider readiness, and provider readiness errors.

The Swift core builder redacts unsafe details before they can be displayed or
encoded. Raw media, local paths, checkout links, and provider secrets are not
included in the script.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
```

`ios_showcase_acceptance` now checks `demo_script` as a tenth source feature.

## P0.50 NPC Ritual Scene

P0.50 turns the existing SceneKit artifact preview into a spatial NPC ritual
surface for the iPhone showcase. `NPCRitualSceneBuilder` derives three visible
NPC actors from the myth session and latest NPC tick, including stance, action,
emotion, and fixed positions around the relic.

`Artifact3DPreviewView` now overlays simple SceneKit NPC markers and ritual
rings on either the downloaded scene asset or the fallback proxy artifact. The
latest tick controls the visible action when present; if the tick only contains
one or two NPC traces, the builder backfills remaining actors from the session
so the scene still shows three NPCs.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
```

`ios_showcase_acceptance` now checks `npc_ritual_scene` as the eleventh source
feature. This is still the native iOS demo surface; richer Unity village
rendering remains a later step.

## P0.51 Showcase Autopilot

P0.51 adds an operator-controlled autopilot button to the `Demo Script` panel.
The new `ShowcaseAutopilotPlanner` lives in the Swift mobile core and chooses
one next safe action from current typed app state:

- run forge when capture media is ready and no session exists
- run backend NPC autonomy for backend-owned myth sessions
- advance one NPC tick for legacy/local sessions
- request a print quote after three NPC ticks
- wait, block, or mark the demo ready when no action should run

The button is disabled while forge, autonomy, NPC advance, or quote loading is
already in progress. It does not auto-run on launch and it does not call any
new API path; `ForgeRootView` dispatches to the existing `forgeMyth`,
`runAutonomy`, `advanceNPCTick`, and `requestPrintQuote` actions.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
```

`ios_showcase_acceptance` now checks `showcase_autopilot` as the twelfth source
feature.

## P0.52 Device Preflight

P0.52 adds a `Device Preflight` panel immediately below `Final Showcase` in
`ForgeRootView`. The panel uses `DevicePreflightSummaryBuilder` from the Swift
mobile core to classify the iPhone demo handoff before an operator starts the
showcase:

- loopback backend URLs are blocked because an iPhone cannot reach them
- private LAN backend URLs are no longer blocked by URL shape
- provider readiness errors or missing provider setup are surfaced without
  provider secrets
- the local final showcase state and saved NPC tick history are summarized

The panel does not run Xcode, sign the app, mutate local developer settings, or
make live provider calls. It is a visible checklist for the values that still
need to be correct when the app moves from source-level verification to a
physical iPhone.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
```

`ios_showcase_acceptance` now checks `device_preflight` as the thirteenth source
feature.

## P0.53 Backend Health Probe

P0.53 adds a manual `Check` action to the `Device Preflight` panel. The action
calls `GET /health` on the configured `PMFBackendBaseURL` and updates the
backend row:

- loopback URLs stay blocked for physical iPhone demos
- non-loopback URLs wait until the operator runs the check
- `status=ok` marks backend health ready
- request failures, non-2xx responses, and non-ok health payloads block the
  preflight with safe generic text

The check does not run automatically, poll in the background, call provider
APIs, or mutate Xcode/signing settings. It is a quick LAN/firewall/server
reachability step before the operator starts capture, 3D generation, NPC
autonomy, or print quote actions.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
```

`ios_showcase_acceptance` now checks `backend_health_probe` as the fourteenth
source feature.

## P0.54 Deploy Health Preflight

P0.54 extends `make mobile-deploy-preflight` so the command-line iOS deploy
check validates the configured backend before Xcode/device work starts. After
the ignored local config provides `DEVELOPMENT_TEAM`,
`PRODUCT_BUNDLE_IDENTIFIER`, and a non-loopback `PMF_BACKEND_BASE_URL`, the
script calls:

```text
GET $PMF_BACKEND_BASE_URL/health
```

It passes only when the backend returns `status=ok`. Backend health failures
are classified separately in final acceptance as
`blocked_by_local_ios_backend_health`, while missing local config remains
`blocked_by_local_ios_deploy_config`.

The script stays project-local: no `sudo`, no `xcode-select`, no license
mutation, no provider calls, and no simulator/device execution.

## P0.57 ARKit Scan Package Bridge

P0.57 adds a pure SwiftPM mobile-core bridge for the post-device-scan handoff.
`ARKitScanPackageBuilder` packages one ARKit/Object Capture scan export with up
to 11 reference images into a `CaptureMediaSelection(mode: .arkitScan)`.

The builder validates:

- scan assets: `model/gltf-binary`, `model/vnd.usdz+zip`,
  `application/octet-stream`
- reference images: `image/heic`, `image/heif`, `image/jpeg`, `image/png`
- per-file size against `CaptureDraft.maxFileBytes`

`ForgeRootView` uses the bridge when imported ARKit scan assets and selected
reference photos are combined, while the UI and backend upload contract stay on
the existing capture-to-myth path.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
```

Visual evidence lives at:

```text
docs/superpowers/verification/p0.57-arkit-scan-package.html
docs/superpowers/verification/assets/p0.57-arkit-scan-package-390x844.png
```

## P0.58 ARKit Showcase Acceptance

P0.58 adds `arkit_scan_package` to the source-only
`ios_showcase_acceptance` gate that is nested inside quick final acceptance.
The new feature checks that:

- `ARKitScanPackageBuilder.swift` exists and returns
  `CaptureMediaSelection(mode: .arkitScan)`
- `ForgeRootView` references `ARKitScanPackageBuilder.selection`
- the Swift contract tests include
  `testARKitScanPackageBuilderBuildsReadySelection`

The gate now reports 15 iOS showcase source features when complete. This is
still not a device install, live ARKit capture run, Xcode build, or provider-key
run; those remain final handoff steps.

Run:

```bash
cd services/backend
uv run pytest tests/test_ios_showcase_acceptance.py tests/test_final_acceptance.py -q
```

Visual evidence lives at:

```text
docs/superpowers/verification/p0.58-arkit-showcase-acceptance.html
docs/superpowers/verification/assets/p0.58-arkit-showcase-acceptance-390x844.png
```

## P0.59 Capture Generation Readiness

P0.59 adds `CaptureGenerationReadinessBuilder` to the SwiftPM mobile core and
wires it into the capture form. The form no longer displays fixed scan hints
such as `2+ photos` or `mesh + reference`; it shows the actual generation route
that will be handed to the backend:

- `multi_image` for ready guided scans and photo sets, capped at four prepared
  provider images for Meshy.
- `scan_asset` for ARKit scan packages and uploaded scan files.
- `single_image` for one-photo routes.
- `waiting` or `needsAttention` when media or provider setup is not ready.

The summary also merges backend provider readiness into the mobile capture
panel. Local demos stay available without provider keys, while live 3D runs
clearly call out `MESHY_API_KEY` when Meshy is selected but not configured.
Provider errors are redacted before display.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
```

Visual evidence lives at:

```text
docs/superpowers/verification/p0.59-capture-generation-readiness.html
docs/superpowers/verification/assets/p0.59-capture-generation-readiness-390x844.png
```

## P0.60 Capture Readiness Showcase Acceptance

P0.60 adds `capture_generation_readiness` to the source-only
`ios_showcase_acceptance` gate that is nested inside quick final acceptance.
The new feature checks that:

- `CaptureGenerationReadiness.swift` exists and defines the builder, route
  model, route display label, and Meshy four-image source cap.
- `ForgeRootView` builds readiness from current media/provider state and passes
  the route display label into the form.
- `CaptureFormView` renders readiness title, route label, and detail.
- Swift contract tests include guided-scan multi-image and ARKit scan asset
  readiness coverage.

The gate now reports 16 iOS showcase source features when complete. This is
still not a device install, live ARKit capture run, Xcode build, or provider-key
run; those remain final handoff steps.

Run:

```bash
cd services/backend
uv run pytest tests/test_ios_showcase_acceptance.py tests/test_final_acceptance.py -q
```

Visual evidence lives at:

```text
docs/superpowers/verification/p0.60-capture-readiness-showcase-acceptance.html
docs/superpowers/verification/assets/p0.60-capture-readiness-showcase-acceptance-390x844.png
```

## P0.61 NPC Agent Provider Acceptance

P0.61 adds a backend source/config gate named
`npc_agent_provider_acceptance` to quick and full final acceptance. It verifies
that `NPC_PROVIDER=openai` is wired to `OpenAINPCDirector` and
`OpenAINPCTickRuntime`, that structured output contracts are present for NPC
reactions and ticks, and that readiness/resource handoff docs keep
`OPENAI_API_KEY` backend-only.

The mobile app still receives the same decoded `npc_agent_runtime`,
`npc_agent_traces`, reactions, and world-resolution payloads. No provider keys
or raw private context are stored in the app. The gate does not make live OpenAI
calls; it proves that the checked-in source has the AI Agent provider path ready
for the final resource handoff.

Run:

```bash
cd services/backend
uv run pytest tests/test_npc_agent_provider_acceptance.py tests/test_final_acceptance.py -q
```

Visual evidence lives at:

```text
docs/superpowers/verification/p0.61-npc-agent-provider-acceptance.html
docs/superpowers/verification/assets/p0.61-npc-agent-provider-acceptance-390x844.png
```

## P0.62 Treatstock Print Quote Adapter

P0.62 keeps the mobile contract stable while making the backend print quote
provider-driven. When the backend is configured with `PRINT_PROVIDER=treatstock`
and `TREATSTOCK_API_KEY`, the same `createPrintQuote` API call can return a
Treatstock-backed `draft_quote` from a downloadable STL/PLY/3MF print candidate
URL.

Local demo sessions now rewrite the backend-produced `printCandidate.uri` to a
downloadable 3MF endpoint:

```http
GET /v1/print-candidates/{session_id}/print.3mf
```

The app still stores no Treatstock key, checkout secret, shipping address, or
payment data. Treatstock order creation remains outside the app flow until a
future explicit approval/fulfillment step.

Run:

```bash
cd services/backend
uv run pytest tests/test_provider_adapters.py tests/test_api_contract.py tests/test_print_acceptance.py -q
```

Visual evidence lives at:

```text
docs/superpowers/verification/p0.62-treatstock-print-quote-adapter.html
docs/superpowers/verification/assets/p0.62-treatstock-print-quote-adapter-390x844.png
```

## P0.71 Mobile Final Resources Preflight

The Device Preflight panel now shows a separate `Final Resources` row from the
backend `final_resources_preflight` report. This lets the iPhone operator see
whether `services/backend/.local/final-resources.env` is missing, blocked, or
ready before running the final apply step.

The app still never reads provider keys or local resource files directly. It
only decodes the backend's sanitized final launch report and redacts unsafe
details before display.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
cd services/backend
uv run pytest tests/test_mobile_final_launch_readiness_acceptance.py -q
```

Visual evidence lives at:

```text
docs/superpowers/verification/p0.71-mobile-final-resources-preflight.html
docs/superpowers/verification/assets/p0.71-mobile-final-resources-preflight-390x844.png
```
