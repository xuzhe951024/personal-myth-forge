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

To route NPC interpretation and stateless NPC ticks through OpenAI structured output:

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

P0.18 adds a no-global-pollution Xcode iOS build gate for the checked-in app
project. The command uses the shared `PersonalMythForge` scheme, a generic iOS
destination, repo-local DerivedData, and disabled signing flags:

```bash
make mobile-xcode-build
```

On a fresh Xcode install, this command may stop at Apple's SDK license gate until
the user accepts the license in Terminal. The repository does not run
`xcode-select`, accept licenses, launch simulators, install to devices, archive,
or configure signing.

Static evidence lives at:

```text
docs/superpowers/verification/p0.18-xcode-ios-build-gate.html
docs/superpowers/verification/assets/p0.18-xcode-ios-build-gate-390x844.png
```

This still does not solve simulator/device installation, signing, live ARKit mesh
capture, Unity movement execution, or real provider-key runs.

P0.19 adds the first guided scan entry for the iOS app shell. The mobile capture
contract now includes `guided_scan`, and the SwiftUI app exposes a `Start Guided
Scan` action that presents an iOS-only RealityKit `ObjectCaptureSession` sheet
behind compile guards. Completed sessions are imported as 2-12 guided photos and
fed into the existing capture upload and myth-session creation flow.

This iteration deliberately uploads guided photo sets, not a locally
reconstructed mesh. JPEG, PNG, HEIC, and HEIF are accepted by the app/backend
capture contract. P0.21 adds backend-side HEIC/HEIF preparation so decodable
iPhone image captures can become Meshy-compatible JPEG Image-to-3D inputs during
generation.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
make backend-lint
make backend-test
make mobile-xcode-build
```

Static evidence lives at:

```text
docs/superpowers/verification/p0.19-guided-scan-entry.html
docs/superpowers/verification/assets/p0.19-guided-scan-entry-390x844.png
```

On this machine `make mobile-xcode-build` still stops at the Apple SDK license
gate. P0.19 does not claim simulator/device installation, real Object Capture
device runtime validation, local photogrammetry reconstruction, or Unity village
import.

P0.20 adds a provider readiness preflight for the final API/key handoff. The
backend exposes:

```http
GET /v1/provider-readiness
```

The response reports 3D, NPC, print, and capture-storage readiness without
returning secret values. Local stubs count as demo-ready but not
real-provider-ready; Meshy and OpenAI become real-provider-ready only when their
backend environment variables are present. The iOS app decodes this contract and
shows a compact readiness strip above the forge form.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
make backend-lint
make backend-test
make mobile-xcode-build
```

Static evidence lives at:

```text
docs/superpowers/verification/p0.20-provider-readiness.html
docs/superpowers/verification/assets/p0.20-provider-readiness-390x844.png
```

P0.20 does not create provider keys, store secrets in the mobile app, run live
Meshy/OpenAI calls, implement print fulfillment, or bypass the Apple SDK license
gate.

P0.21 adds backend HEIC/HEIF-to-JPEG provider input preparation for iOS capture
flows. The upload and manifest contract still accepts and records original
`image/heic` and `image/heif` files. During
`POST /v1/myth-sessions/from-capture`, the backend reads local capture media,
converts decodable HEIC/HEIF reference images into JPEG bytes, and builds
provider-only `data:image/jpeg;base64,...` source images before calling the 3D
provider. Raw media bytes, data URIs, local filesystem paths, and provider keys
are not returned to mobile clients.

This makes HEIC-only guided scans eligible for Meshy Image-to-3D when the
source images decode successfully. Invalid HEIC/HEIF input returns a sanitized
422 instead of silently falling back to text-to-3D.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
make backend-lint
make backend-test
make mobile-xcode-build
```

Regression evidence lives at:

```text
docs/superpowers/verification/2026-06-06-p0.21-heic-meshy-inputs-regression.md
```

P0.21 does not run live Meshy/OpenAI calls, create provider keys, validate on a
real iPhone, implement local photogrammetry reconstruction, add print
fulfillment, configure signing, or bypass the Apple SDK license gate.

P0.22 adds the first explicit NPC continuation loop. The backend exposes:

```http
POST /v1/npc-ticks
```

The request carries the current `MythSession`, a `tick_index`, and short
`recent_events`. The local tick runtime returns `NPCAgentTick` with three new
agent traces, three reactions, and a `WorldResolution` from the existing world
arbitrator. Recent events influence the local runtime without being echoed
verbatim, so data URIs, secrets, and raw personal payloads are not returned.

The iOS app adds an `Advance Village` action below the initial NPC response.
`NPCTickView` renders the latest runtime, NPC intentions, accepted/rejected
actions, and visible world changes. This is still stateless and user-triggered;
it does not add background autonomous loops or persistent tick history.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
make backend-lint
make backend-test
make mobile-xcode-build
```

Static evidence lives at:

```text
docs/superpowers/verification/p0.22-npc-agent-ticks.html
docs/superpowers/verification/assets/p0.22-npc-agent-ticks-390x844.png
```

P0.22 does not persist server-side sessions, add live OpenAI tick generation,
execute Unity character movement, configure signing, or bypass the Apple SDK
license gate.

P0.23 routes the NPC tick loop through the same provider switch used by initial
NPC reactions. When the backend runs with:

```bash
export OPENAI_API_KEY=...
export NPC_PROVIDER=openai
```

`POST /v1/myth-sessions` uses `OpenAINPCDirector` for the first structured NPC
reaction batch and `POST /v1/npc-ticks` uses `OpenAINPCTickRuntime` for the next
structured NPC action tick. Both paths share `OPENAI_NPC_MODEL` and
`OPENAI_API_BASE_URL`; no OpenAI key is stored in or sent to the iOS app.

The OpenAI tick prompt receives approved myth session fields and an aggregate
recent-event count. It does not include raw `recent_events`, data URIs, local
capture paths, provider keys, or media payloads. The generated actions are still
passed through the world arbitrator before they are returned to mobile clients.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
make backend-lint
make backend-test
make mobile-xcode-build
```

Static evidence lives at:

```text
docs/superpowers/verification/p0.23-openai-npc-tick-provider.html
docs/superpowers/verification/assets/p0.23-openai-npc-tick-provider-390x844.png
```

P0.23 does not run a live OpenAI request in automated tests, persist tick
history, add background loops, execute Unity movement, configure signing, or
bypass the Apple SDK license gate.

P0.24 adds a provider handoff smoke report for the final API/key handoff. It is
a configuration-level check: it reads backend settings, reuses
`GET /v1/provider-readiness` semantics, writes a sanitized JSON report, and does
not call Meshy or OpenAI by default.

Prepare a backend-only `.env` from `.env.example`:

```bash
THREE_D_PROVIDER=meshy
NPC_PROVIDER=openai
MESHY_API_KEY=...
OPENAI_API_KEY=...
```

Then run:

```bash
cd services/backend
uv run python -m myth_forge_api.cli provider-handoff \
  --require-core-real \
  --output /tmp/personal-myth-forge-provider-handoff.json
```

The report includes selected providers, demo readiness, real-provider
readiness, missing env names, backend-only secret policy, and next commands.
`--require-core-real` returns exit code `2` until the core demo providers
(`three_d`, `npc`, and `capture_storage`) are real-provider-ready. Print remains
reported but does not block core iOS/AI/3D handoff readiness.

Static evidence lives at:

```text
docs/superpowers/verification/p0.24-provider-handoff-smoke.html
docs/superpowers/verification/assets/p0.24-provider-handoff-smoke-390x844.png
```

P0.24 does not create provider keys, run live Meshy/OpenAI calls, mutate global
environment state, implement print fulfillment, configure signing, or bypass the
Apple SDK license gate.

P0.25 adds a project-local iOS deployment handoff. The checked-in Xcode target
now uses `apps/mobile/ios/Config/Deployment.xcconfig` for bundle id, signing
style, and `PMF_BACKEND_BASE_URL`. Machine-specific values belong in the ignored
`apps/mobile/ios/Config/Deployment.local.xcconfig`.

Prepare local device deployment values:

```bash
cp apps/mobile/ios/Config/Deployment.local.xcconfig.example \
  apps/mobile/ios/Config/Deployment.local.xcconfig
```

Then fill:

```xcconfig
DEVELOPMENT_TEAM = YOUR_TEAM_ID
PRODUCT_BUNDLE_IDENTIFIER = com.example.personalmythforge
PMF_BACKEND_BASE_URL = http://192.168.1.10:8080
```

`PMF_BACKEND_BASE_URL` must use a Mac/LAN address reachable from iPhone, not
`127.0.0.1` or `localhost`.

Run:

```bash
make mobile-deploy-preflight
make mobile-xcode-build
```

`make mobile-deploy-preflight` exits `2` until the ignored local config provides
the required Team ID and iPhone-reachable backend URL. `make mobile-xcode-build`
still requires Apple's SDK license to be accepted outside Codex on this machine.

Static evidence lives at:

```text
docs/superpowers/verification/p0.25-ios-deploy-config.html
docs/superpowers/verification/assets/p0.25-ios-deploy-config-390x844.png
```

P0.25 does not create an Apple developer team, commit provisioning values, store
provider keys in the app, install to a real device, mutate global Xcode settings,
or bypass the Apple SDK license gate.

P0.26 adds local mobile demo continuity. The iOS app now saves the latest
showable `MythSession` and local NPC tick history to an Application Support JSON
snapshot. On relaunch, the app restores the generated relic, NPC/world response,
and saved tick count into the existing review UI.

The snapshot stores only structured session and tick metadata returned by the
backend. It does not store raw photos, scan binaries, PhotosPicker state, local
file URLs, provider keys, bearer tokens, or raw personal source documents. The
restored run can be cleared from the app UI.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
```

Static evidence lives at:

```text
docs/superpowers/verification/p0.26-mobile-demo-snapshot.html
docs/superpowers/verification/assets/p0.26-mobile-demo-snapshot-390x844.png
```

P0.26 does not add server-side NPC memory, background autonomous loops, print
fulfillment, live provider-key runs, or real device installation.

P0.27 adds backend-owned local myth session history. `POST /v1/myth-sessions`
and `POST /v1/myth-sessions/from-capture` now save the generated session to an
ignored JSON store, and `POST /v1/npc-ticks` appends generated ticks to that
session history. Readback endpoints are:

```http
GET /v1/myth-sessions/{session_id}
GET /v1/myth-sessions/{session_id}/history
```

Set `MYTH_SESSION_STORAGE_DIR` to override the default local store at
`services/backend/.local/myth-sessions`. The demo history keeps at most 24 NPC
ticks per session, sanitizes raw media data URIs and obvious provider secrets
before writing JSON, and persists no raw capture files or provider keys.

The iOS core now decodes `MythSessionHistory` and has GET client methods for
session/history recovery. This is a local demo recovery layer, not production
account memory, autonomous background NPC memory, print fulfillment, or a raw
personal-source archive.

Static evidence lives at:

```text
docs/superpowers/verification/p0.27-backend-session-history.html
docs/superpowers/verification/assets/p0.27-backend-session-history-390x844.png
```

P0.28 wires backend history into the visible iOS restore flow. On launch, the
app still restores the local `DemoRunSnapshot` first so a demo remains visible
offline. If that restored session id matches the backend `myth_<16 hex>`
contract, the app then calls:

```http
GET /v1/myth-sessions/{session_id}/history
```

Successful sync replaces the visible ready session and NPC tick history with
backend history, then refreshes the local snapshot. Failed sync leaves the
local restored run visible and shows a non-blocking fallback status. Provider
keys, raw media, local file URLs, and raw personal source documents remain out
of the mobile app.

Static evidence lives at:

```text
docs/superpowers/verification/p0.28-mobile-backend-history-sync.html
docs/superpowers/verification/assets/p0.28-mobile-backend-history-sync-390x844.png
```

P0.29 makes stored backend history the primary NPC advance path. For sessions
that already exist in the local myth session store, the backend now exposes:

```http
POST /v1/myth-sessions/{session_id}/npc-ticks
```

The endpoint loads `MythSessionHistory`, derives the next tick index and recent
events from backend-owned tick history, runs the configured NPC tick runtime,
appends the new tick, and returns updated `MythSessionHistory`. The older
stateless `POST /v1/npc-ticks` endpoint remains available for compatibility.

The iOS app now prefers the session-scoped endpoint for valid `myth_<16 hex>`
session ids and applies the returned history through the existing backend
history restore path. If the server-owned advance path is unavailable, the
current visible demo state remains on screen. Provider keys and raw media still
stay backend-only.

Static evidence lives at:

```text
docs/superpowers/verification/p0.29-server-owned-npc-advance.html
docs/superpowers/verification/assets/p0.29-server-owned-npc-advance-390x844.png
```

P0.30 adds a user-triggered bounded NPC autonomy run on top of the stored
backend history path:

```http
POST /v1/myth-sessions/{session_id}/autonomy-runs
```

The request body accepts `step_count` from `1` to `3` and defaults to `3`. The
backend loads the stored `MythSessionHistory`, runs the configured NPC tick
runtime one step at a time, appends each tick before creating the next request,
and returns an `NPCAutonomyRun` summary plus the updated history. This is a
bounded foreground action, not a background daemon.

The iOS core decodes `NPCAutonomyRun` and calls
`runMythSessionAutonomy(sessionId:stepCount:)`. `ForgeRootView` exposes a
`Run Autonomy` control beside `Advance Village`, then applies `run.history`
through the same backend history path used by restore and server-owned single
tick advance. Provider keys, raw media, and raw personal source documents remain
backend-only.

Static evidence lives at:

```text
docs/superpowers/verification/p0.30-bounded-autonomous-npc-run.html
docs/superpowers/verification/assets/p0.30-bounded-autonomous-npc-run-390x844.png
```

P0.31 adds a backend demo acceptance harness for final API/key handoff. The
local mode runs the integrated backend loop without Meshy/OpenAI keys or live
provider calls:

```bash
cd services/backend
uv run python -m myth_forge_api.cli demo-acceptance \
  --provider-mode local \
  --npc-steps 3 \
  --output /tmp/personal-myth-forge-demo-acceptance.json
```

After backend-only provider keys are supplied, configured strict mode uses the
same report schema and exits `2` before provider calls until the core real
provider set is ready:

```bash
cd services/backend
uv run python -m myth_forge_api.cli demo-acceptance \
  --provider-mode configured \
  --require-real-core \
  --npc-steps 3 \
  --output /tmp/personal-myth-forge-demo-acceptance.json
```

The report summarizes provider readiness, generated asset/scene variant,
initial NPC runtime, bounded NPC ticks, and safety policy. It does not include
provider secrets, raw media, local file paths, or raw personal source bodies.

Static evidence lives at:

```text
docs/superpowers/verification/p0.31-integrated-demo-acceptance.html
docs/superpowers/verification/assets/p0.31-integrated-demo-acceptance-390x844.png
```

P0.32 adds a single final acceptance report that collects the key handoff,
backend demo acceptance, and local iOS/Xcode gates without changing global
machine state:

```bash
cd services/backend
uv run python -m myth_forge_api.cli final-acceptance \
  --profile quick \
  --provider-mode local \
  --output /tmp/personal-myth-forge-final-acceptance.json
```

The quick profile runs provider handoff, local demo acceptance,
`make mobile-deploy-preflight`, and `make mobile-xcode-build`. On this machine
the command is expected to exit `2` until local iOS deploy config and the Apple
SDK license gate are handled; those states are reported as `blocked`, not as
product failures.

Run the full local regression profile before final review:

```bash
cd services/backend
uv run python -m myth_forge_api.cli final-acceptance \
  --profile full \
  --provider-mode local \
  --output /tmp/personal-myth-forge-final-acceptance.json
```

After backend-only Meshy/OpenAI keys are supplied, use configured strict mode:

```bash
cd services/backend
uv run python -m myth_forge_api.cli final-acceptance \
  --profile quick \
  --provider-mode configured \
  --require-real-core \
  --output /tmp/personal-myth-forge-final-acceptance.json
```

Strict mode exits `2` before live provider calls until the core provider set is
real-provider-ready. Final acceptance reports redact provider secrets, bearer
tokens, raw payload markers, data URIs, and local filesystem paths.

Static evidence lives at:

```text
docs/superpowers/verification/p0.32-final-acceptance-report.html
docs/superpowers/verification/assets/p0.32-final-acceptance-report-390x844.png
```

P0.33 routes multi-image guided scans to Meshy's Multi-Image to 3D endpoint when
the backend has at least two prepared JPEG/PNG reference images. The Meshy
adapter now selects provider input like this:

- 2-4 supported images: `/openapi/v1/multi-image-to-3d`
- 5+ supported images: first four images sent to `/openapi/v1/multi-image-to-3d`
- 1 supported image: existing `/openapi/v1/image-to-3d`
- 0 supported images: existing text-to-3D preview/refine path

HEIC/HEIF guided scan photos are still converted to provider-safe JPEGs before
the 3D provider sees them. Automated tests use `httpx.MockTransport` and do not
make live Meshy calls or require `MESHY_API_KEY`.

Static evidence lives at:

```text
docs/superpowers/verification/p0.33-meshy-multi-image-guided-scan.html
docs/superpowers/verification/assets/p0.33-meshy-multi-image-guided-scan-390x844.png
```

P0.34 adds a safe generated asset provenance contract. Backend-generated
`GeneratedAsset` responses can now include optional `generation_provenance`
with:

- `input_mode`: `text_prompt`, `single_image`, or `multi_image`
- provider route used by the 3D adapter
- total and selected source image counts
- source asset count
- `raw_sources_included`, which remains `false` for current providers

The field is included in demo acceptance reports and decoded by the iOS app.
The mobile artifact summary renders the generation mode and selected/source
image count when available. The contract intentionally does not return raw
capture media, provider-only data URIs, local file paths, or provider secrets.

Static evidence lives at:

```text
docs/superpowers/verification/p0.34-generation-provenance-contract.html
docs/superpowers/verification/assets/p0.34-generation-provenance-contract-390x844.png
```

P0.35 adds a canonical 20-case 3D provider evaluation suite for the final
Meshy quality handoff. It extends `evaluate-3d` with:

```bash
cd services/backend
uv run python -m myth_forge_api.cli evaluate-3d \
  --provider local \
  --suite default-v0 \
  --output /tmp/personal-myth-forge-3d-eval.json
```

The report includes suite/category metadata, generated asset provenance,
variant coverage, SceneKit-loadable coverage, elapsed time, sanitized errors,
and empty manual review fields for later quality scoring. Custom prompt files
still work and are reported as `custom-prompts`. Running the same suite through
Meshy is opt-in and requires backend-only `MESHY_API_KEY`; final acceptance does
not automatically spend provider credits.

Static evidence lives at:

```text
docs/superpowers/verification/p0.35-3d-provider-evaluation-suite.html
docs/superpowers/verification/assets/p0.35-3d-provider-evaluation-suite-390x844.png
```

P0.36 adds a media-backed guided scan smoke suite for the 3D provider contract.
It uses synthetic non-private PNG data URIs internally to exercise source-image
provider paths, while the written report only records source image counts,
roles, and sanitized provenance.

Run the no-key local media route smoke:

```bash
cd services/backend
uv run python -m myth_forge_api.cli evaluate-3d \
  --provider local \
  --suite guided-scan-smoke-v0 \
  --output /tmp/personal-myth-forge-guided-scan-eval.json
```

Expected local coverage is one `single_image` case and two `multi_image` cases
with source image counts `1 / 2 / 4`. Running the same suite through Meshy is
opt-in and requires backend-only `MESHY_API_KEY`; reports must not contain raw
`data:image` payloads, provider keys, or local file paths.

Static evidence lives at:

```text
docs/superpowers/verification/p0.36-media-backed-3d-evaluation.html
docs/superpowers/verification/assets/p0.36-media-backed-3d-evaluation-390x844.png
```
