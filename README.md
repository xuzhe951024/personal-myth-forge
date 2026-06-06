# Personal Myth Forge

`Personal Myth Forge` is an early-stage mobile-first game prototype where a player's real-world object and personal context are transformed into a mythic 3D artifact, interpreted by autonomous NPCs, and optionally converted into a printable physical relic.

## v0.1 Goal

Build a vertical slice that proves the core loop:

1. Capture or upload a real-world object from mobile.
2. Convert the object plus a personal context capsule into a myth seed.
3. Generate a free-form 3D game asset.
4. Let NPCs independently interpret and react to the artifact.
5. Produce a print-ready derivative and quote it through a print provider.

## Repository Layout

- `services/backend/` - FastAPI service for AI orchestration, NPC planning, 3D generation adapters, and print provider adapters.
- `apps/mobile/` - iOS-first mobile client notes, SwiftPM client scaffold, and future Unity integration notes.
- `packages/personal-myth-skill/` - Future MCP/agent skill interface for personal context capsules.
- `docs/` - Product design, iteration roadmap, and implementation plans.

## Local Backend

```bash
make backend-test
make backend-lint
make backend-dev
```

Open the first local demo at:

```text
http://127.0.0.1:8080/demo
```

The demo defaults to the deterministic local 3D provider, so it does not require external API
keys.

Upload a local object capture, then create a myth session from that capture:

```bash
curl -X POST http://127.0.0.1:8080/v1/object-captures \
  -F 'metadata_json={"label":"old brass key","materials":["metal","brass"],"source":"phone_capture","capture_mode":"single_photo","visual_notes":"worn teeth"}' \
  -F 'files=@/path/to/key.jpg;type=image/jpeg'

curl -X POST http://127.0.0.1:8080/v1/myth-sessions/from-capture \
  -H 'Content-Type: application/json' \
  -d @apps/mobile/fixtures/myth-session-from-capture.json
```

Set `CAPTURE_STORAGE_DIR` to override the local ignored capture storage directory.
The default local path is intended for development artifacts, not durable user
storage.

To route NPC interpretation through OpenAI structured output:

```bash
export OPENAI_API_KEY=...
export NPC_PROVIDER=openai
make backend-dev
```

## 3D Provider Spike

Generate local asset metadata from a prompt:

```bash
cd services/backend
uv run python -m myth_forge_api.cli generate-asset \
  --provider local \
  --prompt "Create a brass key relic worshiped by a tiny village."
```

Generate a real Meshy GLB when `MESHY_API_KEY` is available:

```bash
export MESHY_API_KEY=...
cd services/backend
uv run python -m myth_forge_api.cli generate-asset \
  --provider meshy \
  --prompt "Create a weathered key worshiped by a tiny village."
```

Use `THREE_D_PROVIDER=meshy` to route `POST /v1/myth-sessions` through Meshy. Keep
`THREE_D_PROVIDER=local` for fast local demos and tests.

P0.11 adds capture-aware 3D generation for the from-capture flow. When
`POST /v1/myth-sessions/from-capture` is called, the backend safely reads local
JPEG/PNG reference media, converts it into a provider-only data URI source image,
passes scan assets as local capture references, and routes Meshy requests through
Image-to-3D when an image source is present. Prompt-only CLI and direct session
generation still use the text-to-3D path.

Run a small 3D prompt evaluation report:

```bash
cd services/backend
printf "Create a brass key relic.\nCreate a moon cup relic.\n" > /tmp/p0.5-prompts.txt
uv run python -m myth_forge_api.cli evaluate-3d \
  --provider local \
  --prompts-file /tmp/p0.5-prompts.txt \
  --output /tmp/p0.5-3d-eval.json
```

## Mobile Client Scaffold

Run the P0.7 Swift mobile core contract tests:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
```

This validates the typed iOS-side models, multipart request builder, API client,
and reducer without requiring a global Xcode developer directory change.

P0.8 also includes an Xcode app shell at:

```text
apps/mobile/ios/PersonalMythForge.xcodeproj
```

Open that project in full Xcode for simulator or device deployment work. On this
machine, local verification stays SwiftPM-only:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
```

The app shell exposes `PMFBackendBaseURL` in `Info.plist` for the first API
client wiring; provider API keys stay on the backend.

P0.9 adds an iOS scan capture draft layer in the SwiftPM mobile core. It
validates `single_photo`, `photo_set`, `manual_upload`, and `arkit_scan` inputs
before building backend upload payloads. The API client now accepts image media
plus GLB, USDZ, and binary scan assets while still generating safe multipart
filenames such as `media_0.jpg` and `scan_0.glb`.

Run the no-simulator acceptance checks:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
```

View the static mobile storyboard evidence:

```bash
cd docs/superpowers/verification
python3 -m http.server 8128 --bind 127.0.0.1
```

Then open:

```text
http://127.0.0.1:8128/p0.9-ios-scan-capture.html
```

P0.10 adds the iOS forge flow orchestration layer. `ForgeFlowService` validates a
`CaptureDraft`, uploads it through `POST /v1/object-captures`, calls
`POST /v1/myth-sessions/from-capture`, and drives the mobile reducer into the
ready state with generated asset, NPC, world, and print candidate data.

Run the local checks:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
```

View the P0.10 static storyboard evidence:

```text
http://127.0.0.1:8128/p0.10-ios-forge-flow.html
```

P0.11 completes the backend half of capture-aware 3D generation. Uploaded
reference images and scan asset refs now reach the 3D provider contract, and the
Meshy adapter chooses Image-to-3D when an image source exists. View the static
provider-contract evidence:

```text
http://127.0.0.1:8128/p0.11-capture-aware-3d.html
```

This is still no-simulator evidence. Real media picking, ARKit scanning, public
or storage-backed media delivery, multi-image/scan remesh, real provider-key
runs, and iOS 3D rendering remain later work. Provider API keys stay on the
backend.

P0.12 adds the iOS source-level device media input bridge. `ForgeRootView` now
uses PhotosPicker for photo input and fileImporter for manual/scan files,
loading selected media into `CaptureMediaSelection` and then into the existing
`ForgeFlowService` path. Static source-level evidence lives at:

```text
docs/superpowers/verification/p0.12-ios-device-media-input.html
docs/superpowers/verification/assets/p0.12-ios-device-media-input-390x844.png
```

This remains no-simulator evidence. Live camera capture, ARKit mesh capture
runtime, full simulator/device deployment, and iOS 3D rendering are still
separate work.

P0.13 adds a local SwiftPM compile gate for the SwiftUI app source. The package
now includes `PersonalMythForgeMobileAppCompileCheck`, which compiles
`apps/mobile/ios/App` against `PersonalMythForgeMobileCore` without changing
global Xcode settings:

```bash
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
```

This gate caught and fixed app-source API availability and Swift 6 concurrency
issues that source-string checks did not cover. Static evidence lives at:

```text
docs/superpowers/verification/p0.13-ios-app-compile-gate.html
docs/superpowers/verification/assets/p0.13-ios-app-compile-gate-390x844.png
```

This is still not a simulator build, device install, signing pass, ARKit mesh
capture, or iOS 3D renderer screenshot.

P0.14 adds a SwiftPM-compiled SceneKit artifact preview surface to the iOS app
source. `ArtifactPreviewState` classifies generated asset readiness in the
mobile core, and `Artifact3DPreviewView` renders a SceneKit proxy artifact in
`ArtifactSummaryView` while preserving the caveat that Meshy GLB download,
cache, and import/conversion are later work.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
```

Static evidence lives at:

```text
docs/superpowers/verification/p0.14-ios-3d-artifact-preview.html
docs/superpowers/verification/assets/p0.14-ios-3d-artifact-preview-390x844.png
```

This is still not a real provider asset download/cache/import path, GLB runtime
conversion, simulator/device deployment, live ARKit mesh capture, or the richer
3D village scene.

P0.15 adds the mobile generated asset handoff layer. `ArtifactAssetPreparer`
downloads backend-provided HTTP(S) generated asset URIs, stores them in an
app-local cache, and returns a local SceneKit URL for directly loadable formats
such as USDZ. `Artifact3DPreviewView` uses that prepared asset and attempts
`SCNScene(url:)` before falling back to the proxy artifact.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
```

Static evidence lives at:

```text
docs/superpowers/verification/p0.15-ios-generated-asset-handoff.html
docs/superpowers/verification/assets/p0.15-ios-generated-asset-handoff-390x844.png
```

This still does not solve provider-side USDZ export, GLB runtime conversion,
simulator/device deployment, live ARKit mesh capture, or Unity village import.

P0.16 adds a generated asset variant contract. The backend keeps
`generated_asset` as the primary game asset, usually GLB, and now also returns
`generated_asset.variants` for alternate files from the same generation. The
local provider returns a deterministic USDZ `ios_scene_asset` variant, and the
Meshy adapter requests GLB plus USDZ and maps `model_urls.usdz` into that
variant when present.

The iOS models decode missing `variants` as an empty list for older responses.
`ArtifactAssetPreparer` now prefers a scene-loadable `ios_scene_asset` before
falling back to the primary asset, so a backend-provided USDZ can become the
SceneKit handoff path without sending provider API keys to the mobile app.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
make backend-lint
make backend-test
```

Static evidence lives at:

```text
docs/superpowers/verification/p0.16-asset-variant-contract.html
docs/superpowers/verification/assets/p0.16-asset-variant-contract-390x844.png
```

This still does not solve runtime GLB import, provider conversion retries when
USDZ is absent, simulator/device deployment, live ARKit mesh capture, print
asset repair, or Unity village import.

P0.17 adds the first explicit NPC agent runtime trace contract. The backend now
returns `npc_agent_runtime` plus `npc_agent_traces` alongside the existing
player-facing `npc_reactions`. The deterministic local runtime forms one trace
per NPC with belief, intention, proposed action, rationale, and confidence, then
derives visible reactions that the world arbitrator can resolve.

The OpenAI NPC path can parse structured traces when present and synthesizes
conservative trace rows from valid reactions when a provider/mock omits them.
Provider secrets still stay backend-only, and raw personal data is not included;
the runtime only sees approved context capsule summaries.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
make backend-lint
make backend-test
```

Static evidence lives at:

```text
docs/superpowers/verification/p0.17-npc-agent-runtime.html
docs/superpowers/verification/assets/p0.17-npc-agent-runtime-390x844.png
```

This still does not solve long-term NPC memory, multi-turn agent ticking, Unity
movement execution, voice NPCs, simulator/device deployment, or live ARKit mesh
capture.
