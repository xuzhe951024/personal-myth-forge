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

For an iPhone on the same LAN, run the backend on a device-reachable interface:

```bash
make backend-device-demo
```

Then point `PMF_BACKEND_BASE_URL` in the ignored iOS local config at the Mac LAN
address, such as `http://192.168.1.10:8080`. `backend-dev` remains the
localhost/browser path; `backend-device-demo` does not change firewall, signing,
or Apple SDK license state.

Create or update that ignored iOS local config from explicit user-owned values:

```bash
DEVELOPMENT_TEAM=ABCDE12345 \
PRODUCT_BUNDLE_IDENTIFIER=com.example.personalmythforge \
PMF_BACKEND_BASE_URL=http://192.168.1.10:8080 \
make mobile-write-deploy-config
```

Then validate the local config and backend health gate:

```bash
make mobile-deploy-preflight
```

`mobile-write-deploy-config` writes only
`apps/mobile/ios/Config/Deployment.local.xcconfig`, which is ignored by git. It
does not store provider keys and does not mutate Xcode, signing, keychain, or
global developer settings.

The demo defaults to the deterministic local 3D provider, so it does not require external API
keys.

When final Meshy/OpenAI/Treatstock and iOS deploy resources are available, use
one ignored resource file to apply the full local handoff:

```bash
mkdir -p services/backend/.local
cp services/backend/final-resources.env.example services/backend/.local/final-resources.env
$EDITOR services/backend/.local/final-resources.env
make final-resources-preflight
make final-apply-resources
```

`final-resources-preflight` is read-only: it checks missing keys, unknown keys,
loopback iPhone backend URLs, and Treatstock key dependencies without writing
config files or calling providers. `final-apply-resources` writes only
`services/backend/.env` and
`apps/mobile/ios/Config/Deployment.local.xcconfig`, both ignored by git. Its
output redacts provider keys and it does not call Meshy/OpenAI/Treatstock, start
servers, run Xcode, sign apps, touch keychain, accept Apple licenses, or mutate
global machine state. The lower-level `backend-write-provider-env` and
`mobile-write-deploy-config` targets remain available for separate handoff
steps.

Then validate configured provider readiness explicitly:

```bash
cd services/backend
uv run python -m myth_forge_api.cli provider-handoff --require-core-real
```

The unified resource file can set `PRINT_PROVIDER=treatstock` plus
`TREATSTOCK_API_KEY` for live quote handoff. Use `PRINT_PROVIDER=local` for a
no-key print quote demo.

Preview the final demo launch lane without writing secrets or calling live
providers:

```bash
make final-demo-launch
```

Run the full local final rehearsal from the project root:

```bash
make final-rehearsal-local
```

This writes the canonical ignored local reports needed for handoff review:

- `services/backend/.local/3d-evaluation-local.json`
- `services/backend/.local/npc-evaluation-local.json`
- `services/backend/.local/final-acceptance-local.json`
- `services/backend/.local/final-demo-launch-local.json`
- `services/backend/.local/ios-deploy-runbook-local.json`

`final-rehearsal-local` runs only local/no-key gates by default. The final
acceptance and iOS deploy runbook wrappers treat exit `2` as a valid
report-written state, so expected local iPhone/Xcode blockers do not stop the
rehearsal. Exit `1` still fails the target. The command does not call live
providers, apply secrets, start servers, run Xcode, accept Apple licenses, or
mutate global machine state.

For the final key-backed handoff, fill the one-file resource bundle, apply it,
then run the configured launch report:

```bash
mkdir -p services/backend/.local
cp services/backend/final-resources.env.example services/backend/.local/final-resources.env
$EDITOR services/backend/.local/final-resources.env
make final-resources-preflight
make final-apply-resources
make final-configured-preflight
make final-handoff-index
cd services/backend
uv run python -m myth_forge_api.cli final-demo-launch \
  --mode configured \
  --repo-root ../.. \
  --output .local/final-demo-launch-configured.json
```

The launch report includes the `final_resources_preflight` report and uses
`apply_final_resources` as the single resource application phase for backend
provider settings and iOS deployment config. It also consolidates backend
device-server commands, provider readiness,
local/configured final acceptance, iOS deploy preflight, and the Xcode build
gate. It never starts servers, calls Meshy/OpenAI/Treatstock, or changes
Xcode/signing/global machine state by itself. Live provider calls remain
explicitly gated behind `final-acceptance --provider-mode configured
--require-real-core --allow-live-provider-calls`.

`make final-configured-preflight` writes the ignored
`services/backend/.local/final-configured-preflight.json` handoff packet. It
combines the final resources preflight, current provider readiness, backend/iOS
resource handoff, configured launch report, and configured iOS deploy runbook.
The command is read-only: it does not call live providers, apply secrets, start
servers, run Xcode, touch signing/keychain, or write backend/iOS config files.
Exit `2` still writes a usable blocked packet; exit `0` means the configured
handoff is ready enough for the next operator step.

`make final-handoff-index` writes
`services/backend/.local/final-handoff-index.json` as the final operator index
across the local rehearsal lane, configured preflight lane, device deploy path,
and consent-gated configured final acceptance command. It is read-only and does
not run rehearsal, apply resources, call live providers, start servers, run
Xcode, touch signing/keychain, or write backend/iOS config files. Exit `2`
means the index was written with remaining blockers; exit `0` means the saved
handoff state is ready enough for the next configured operator step.

`make ios-device-launch-certificate` writes
`services/backend/.local/ios-device-launch-certificate.json` as the final
Mac-side certificate for starting the physical iPhone sequence. It composes the
final handoff index, current iOS deployment config, iOS deploy runbook, and final
demo launch report into one sanitized packet with device gates, operator command
order, and live-provider consent state. The command is read-only: it does not
start servers, run the deploy preflight, call Meshy/OpenAI/Treatstock, run
Xcode, touch signing/keychain, accept Apple licenses, or write backend/iOS
config files. Exit `2` still writes a blocked certificate for review; exit `0`
means the checkout is ready enough to begin `make backend-device-demo`,
`make mobile-deploy-preflight`, and the manual Xcode build gate.

`make ios-device-launch-rehearsal` runs the safe final rehearsal sequence and
writes `services/backend/.local/ios-device-launch-rehearsal.json`. It refreshes
local/no-key reports, configured preflight, final handoff index, and the iOS
device launch certificate, accepting exit `2` as "blocked report written" for
each step. The wrapper still does not call live providers, apply resources,
write backend/iOS config, start servers, run deploy preflight, run Xcode, touch
signing/keychain, accept Apple licenses, or mutate global machine state. Use it
before the final iPhone operator pass when you want the complete ignored JSON
evidence set regenerated in one command.

The same sanitized launch status is available to the iPhone app:

```bash
curl http://127.0.0.1:8080/v1/final-demo-launch?mode=local
```

The mobile device preflight panel loads this read-only report and shows a
`Final Launch` row alongside backend, provider, local demo, and saved NPC
history checks. The endpoint does not write config files, start servers, call
live providers, or expose secret values.

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

Run the final no-key local evaluation reports from the project root:

```bash
make backend-evaluate-3d
make backend-evaluate-npc
make backend-evaluate-local
```

The first two targets write `services/backend/.local/3d-evaluation-local.json`
and `services/backend/.local/npc-evaluation-local.json`; the combined target
runs both in that order.

P0.90 adds this `evaluate-npc` suite for final OpenAI NPC quality handoff. The
default command is no-key and local. The report includes NPC ids, agent trace
counts, proposed-action/plan alignment, world-arbitration counts, elapsed time,
and manual review fields. Switching to `--provider openai` requires backend-only
`OPENAI_API_KEY`; no OpenAI key is stored in or sent to the iOS app.

P0.91 surfaces the saved NPC Agent evaluation readiness through the read-only
`/v1/final-demo-launch` report and the iPhone `Final Launch Status` panel. The
backend reads only `services/backend/.local/npc-evaluation-local.json`; it does
not run `evaluate-npc`, call OpenAI/Meshy, write config files, or expose raw
private context. To create or refresh the local readiness report:

```bash
make backend-evaluate-npc
```

Then inspect the iPhone-facing launch readiness payload:

```bash
curl http://127.0.0.1:8080/v1/final-demo-launch?mode=local
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

Prepare a backend-only `.env` through the project-local writer:

```bash
MESHY_API_KEY=... \
OPENAI_API_KEY=... \
make backend-write-provider-env
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
make backend-device-demo
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
same report schema. Leaving off `--allow-live-provider-calls` is a safe dry
handoff check: it exits `2` before Meshy/OpenAI calls once live providers are
ready. Add the flag only for the intentional live provider validation run:

```bash
cd services/backend
uv run python -m myth_forge_api.cli demo-acceptance \
  --provider-mode configured \
  --require-real-core \
  --allow-live-provider-calls \
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
  --allow-live-provider-calls \
  --output /tmp/personal-myth-forge-final-acceptance.json
```

Without `--allow-live-provider-calls`, strict mode exits `2` before live
provider calls once Meshy/OpenAI are ready. Final acceptance reports redact
provider secrets, bearer tokens, raw payload markers, data URIs, and local
filesystem paths.

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
Meshy quality handoff. The project-root no-key readiness command is:

```bash
make backend-evaluate-3d
```

The underlying CLI still supports custom output paths and live provider runs:

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

P0.37 adds the capture-to-3D acceptance gate to final acceptance. The quick
profile now creates a synthetic local `guided_scan` capture, reads three stored
source images through the same backend preparation helper used by
`POST /v1/myth-sessions/from-capture`, and proves those images reached the 3D
provider request.

Run:

```bash
cd services/backend
uv run python -m myth_forge_api.cli final-acceptance \
  --profile quick \
  --provider-mode local \
  --output /tmp/personal-myth-forge-final-acceptance.json
```

Expected local summary is `passed=3`, `blocked=2`, `failed=0`: provider
handoff, demo acceptance, and `capture_3d_acceptance` pass; iOS deploy
preflight and Xcode build remain blocked until local signing/LAN URL and Apple
SDK license are handled. The capture acceptance report must not include raw
`data:image` payloads, `local-capture://` URIs, local filesystem paths, or
provider secrets.

Static evidence lives at:

```text
docs/superpowers/verification/p0.37-capture-3d-acceptance-gate.html
docs/superpowers/verification/assets/p0.37-capture-3d-acceptance-gate-390x844.png
```

P0.38 adds the first print quote handoff contract for printable relic review.
The backend exposes a safe local draft quote endpoint:

```http
POST /v1/print-quotes
```

Create a local request from an existing print candidate shape:

```bash
cat >/tmp/print-quote-request.json <<'JSON'
{
  "print_candidate": {
    "kind": "print_asset",
    "source_asset_uri": "local://generated-assets/myth_test.glb",
    "provider": "local_stub",
    "format": "3mf",
    "uri": "local://print-candidates/myth_test.3mf",
    "requires_user_approval": true,
    "approval_reason": "review before fulfillment",
    "printability_notes": ["stable base", "repair thin parts"]
  },
  "quantity": 1,
  "material": "standard_resin",
  "finish": "matte",
  "ship_to_country": "US"
}
JSON

curl -X POST http://127.0.0.1:8080/v1/print-quotes \
  -H 'Content-Type: application/json' \
  -d @/tmp/print-quote-request.json
```

The local provider returns a deterministic `draft_quote`, `USD 16.00` per item,
and `requires_user_approval: true`. `PRINT_PROVIDER=treatstock` and
`PRINT_PROVIDER=sculpteo` now have backend config/readiness slots. Treatstock is
implemented in P0.62; Sculpteo remains a future adapter.

Run final acceptance:

```bash
cd services/backend
uv run python -m myth_forge_api.cli final-acceptance \
  --profile quick \
  --provider-mode local \
  --output /tmp/personal-myth-forge-final-acceptance.json
```

Expected local summary after P0.38 is `passed=4`, `blocked=2`, `failed=0`.
The new passing check is `print_quote_acceptance`; the blocked checks remain
local iOS deploy config and the Apple SDK license on this machine. Reports must
not include checkout/payment identifiers, provider keys, raw media payloads, or
local filesystem paths.

Static evidence lives at:

```text
docs/superpowers/verification/p0.38-print-quote-handoff.html
docs/superpowers/verification/assets/p0.38-print-quote-handoff-390x844.png
```

P0.39 wires that print quote contract into the iOS app source. When a myth
session is ready, the mobile UI now shows a `Print Quote` review panel with the
current print candidate, a `Get Quote` action, and the returned local
`draft_quote` summary.

The Swift API client calls:

```http
POST /v1/print-quotes
```

with the ready session's `print_candidate` and default review preferences:
`quantity=1`, `material=standard_resin`, `finish=matte`, and
`ship_to_country=US`. The local backend quote remains deterministic at
`USD 16.00`; the mobile view shows production/shipping days and user approval
requirements. It does not show a checkout/payment action or store provider keys
in the app.

Run the mobile checks:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
```

Expected final acceptance summary remains `passed=4`, `blocked=2`, `failed=0`.
The remaining blockers are unchanged: local iOS deploy config and the Apple SDK
license on this machine.

Static evidence lives at:

```text
docs/superpowers/verification/p0.39-mobile-print-quote-review.html
docs/superpowers/verification/assets/p0.39-mobile-print-quote-review-390x844.png
```

P0.40 adds a consolidated final resource handoff bundle for the operator
resource stage. It reads backend settings and project-local iOS deploy config,
then writes one sanitized JSON report covering Meshy/OpenAI provider keys,
print provider key slots, iOS signing/backend URL values, the Apple SDK manual
gate, next commands, and safety checks.

Run:

```bash
cd services/backend
uv run python -m myth_forge_api.cli resource-handoff \
  --repo-root ../.. \
  --output /tmp/personal-myth-forge-resource-handoff.json
```

The command is configuration-only: it does not call Meshy, OpenAI, Treatstock,
Sculpteo, or Apple services; does not mutate `.env`, Xcode, signing, keychain,
or license state; and never prints provider key values. On a default local
checkout it exits `2` with a safe blocked report until the backend gets
`THREE_D_PROVIDER=meshy`, `MESHY_API_KEY`, `NPC_PROVIDER=openai`,
`OPENAI_API_KEY`, and the ignored iOS deploy config gets a Team ID plus an
iPhone-reachable LAN backend URL.

Use `make backend-write-provider-env` before this report to write the ignored
backend `.env` from explicit Meshy/OpenAI values with redacted command output.

Static evidence lives at:

```text
docs/superpowers/verification/p0.40-resource-handoff-bundle.html
docs/superpowers/verification/assets/p0.40-resource-handoff-bundle-390x844.png
```

P0.41 adds a mobile `Final Showcase` summary panel. The Swift mobile core now
computes a `FinalShowcaseSummary` from existing app state: capture readiness,
generated 3D asset/provenance, NPC agent output and saved tick count, print
quote state, provider readiness, and privacy/resource boundaries.

The app renders that summary near the top of `ForgeRootView`, before the
detailed provider, capture, artifact, NPC, and print panels. It is local
presentation logic only: it does not add a backend endpoint, call external
providers, expose provider keys, surface checkout URLs, store raw capture media,
or mutate Xcode state.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
```

Static evidence lives at:

```text
docs/superpowers/verification/p0.41-final-showcase-summary.html
docs/superpowers/verification/assets/p0.41-final-showcase-summary-390x844.png
```

P0.42 adds a direct iOS `Take Photo` bridge for the single-photo capture mode.
The SwiftUI app now presents `CameraCaptureView`, uses UIKit's camera picker
behind iOS compile guards, converts a captured image to JPEG bytes, and feeds it
through `CameraCaptureMediaBuilder.singlePhotoSelection(...)` into the same
capture upload path used by PhotosPicker.

Provider keys still stay backend-only, and camera bytes are not written into
demo snapshots. This is source-level and static visual evidence only on this
machine; final device acceptance still requires running the app on an iPhone
with signing, a LAN-reachable backend URL, and camera permission.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
```

Static evidence lives at:

```text
docs/superpowers/verification/p0.42-ios-camera-capture-bridge.html
docs/superpowers/verification/assets/p0.42-ios-camera-capture-bridge-390x844.png
```

P0.43 adds a source-only iOS showcase acceptance gate to the final acceptance
report. `final-acceptance --profile quick` now includes
`ios_showcase_acceptance`, which reads checked-in source/project files and
verifies that the mobile showcase still includes:

- camera capture
- guided scan
- capture upload
- 3D preview
- NPC agent controls
- print quote review
- provider readiness
- final showcase summary
- deploy configuration slots

The check does not run Xcode, SwiftPM, simulators, devices, provider APIs, or
network calls. It is not a replacement for the full Swift compile/profile checks
or real iPhone validation. On the default local checkout, quick final acceptance
now expects `passed=5`, `blocked=2`, `failed=0`; the blocked checks remain iOS
deploy preflight and Xcode build gate.

Run:

```bash
cd services/backend
uv run python -m myth_forge_api.cli final-acceptance \
  --profile quick \
  --provider-mode local \
  --output /tmp/personal-myth-forge-final-acceptance.json
```

Static evidence lives at:

```text
docs/superpowers/verification/p0.43-ios-showcase-acceptance.html
docs/superpowers/verification/assets/p0.43-ios-showcase-acceptance-390x844.png
```

P0.44 adds an explicit live-provider consent gate for acceptance commands. The
default `demo-acceptance` and `final-acceptance` behavior remains safe for local
and CI-style runs: even if `.env` contains Meshy/OpenAI keys, configured mode
will not contact live providers unless `--allow-live-provider-calls` is present.
This keeps routine verification no-cost while preserving one clear final handoff
command for intentional live validation.

Run the safe local final check:

```bash
cd services/backend
uv run python -m myth_forge_api.cli final-acceptance \
  --profile quick \
  --provider-mode local \
  --output /tmp/personal-myth-forge-final-acceptance.json
```

Run the intentional live provider check only after confirming backend-only keys
and quota:

```bash
cd services/backend
uv run python -m myth_forge_api.cli final-acceptance \
  --profile quick \
  --provider-mode configured \
  --require-real-core \
  --allow-live-provider-calls \
  --output /tmp/personal-myth-forge-final-acceptance.json
```

P0.45 adds the iPhone backend launch handoff. The new `backend-device-demo`
target runs the FastAPI app on `0.0.0.0:8080`, which is the backend mode to use
when `PMF_BACKEND_BASE_URL` points to the Mac's LAN address from a real iPhone.
Final acceptance now includes `ios_backend_handoff_acceptance`, a source-only
gate that verifies the device backend target, LAN URL example, loopback preflight
guard, and app config lookup are all present.

Run:

```bash
make backend-device-demo
```

Expected quick final acceptance on this local checkout is now
`passed=6`, `blocked=2`, `failed=0`; the two blockers remain local iOS signing
config and the Apple SDK/Xcode license gate.

P0.46 adds a source-only resource template acceptance gate. It verifies that the
checked-in templates expose every final resource slot the operator must fill:
Meshy/OpenAI provider settings, print provider key slots, local capture/session
storage overrides, and iPhone deployment values. It also verifies that local
destination files are ignored by git and that templates/reports contain no
provider secrets, raw media, local absolute paths, or payment links.

Run:

```bash
cd services/backend
uv run python -m myth_forge_api.cli resource-template-acceptance \
  --repo-root ../.. \
  --output /tmp/personal-myth-forge-resource-template-acceptance.json
```

P0.47 makes local generated scene assets downloadable by the iOS app. Local demo
sessions now expose a SceneKit-loadable `ios_scene_asset` as a backend-served DAE
URL:

```http
GET /v1/generated-assets/{session_id}/game.glb
GET /v1/generated-assets/{session_id}/scene.dae
```

When an iPhone calls the backend through `PMF_BACKEND_BASE_URL`, local
`generated_asset` and `ios_scene_asset` URLs are rewritten to the same
device-reachable backend base URL. Meshy HTTP(S) URLs are left untouched. The
local assets are deterministic demo geometry only; they contain no raw capture
media, provider keys, local filesystem paths, or personal source text.

Expected quick final acceptance on this local checkout is now
`passed=8`, `blocked=2`, `failed=0`; the two blockers remain local iOS signing
config and the Apple SDK/Xcode license gate.

Static evidence lives at:

```text
docs/superpowers/verification/p0.47-local-scene-asset-handoff.html
docs/superpowers/verification/assets/p0.47-local-scene-asset-handoff-390x844.png
```

P0.48 adds an integrated capture-to-scene handoff acceptance gate. It uploads a
synthetic guided scan through `POST /v1/object-captures`, creates a session with
`POST /v1/myth-sessions/from-capture`, verifies multi-image generation
provenance, then downloads the returned backend-served assets:

```http
GET /v1/generated-assets/{session_id}/game.glb
GET /v1/generated-assets/{session_id}/scene.dae
```

The new final acceptance check is `capture_scene_handoff_acceptance`. It proves
that the current mobile scan path can reach an iOS-loadable local scene asset
without calling Meshy/OpenAI or exposing raw scan media, `local-capture://`
references, local filesystem paths, provider tokens, or personal source text in
the report.

Run:

```bash
cd services/backend
uv run pytest tests/test_capture_scene_handoff_acceptance.py tests/test_final_acceptance.py -q
uv run python -m myth_forge_api.cli final-acceptance \
  --profile quick \
  --repo-root ../.. \
  --output /tmp/personal-myth-forge-final-acceptance-p0.48.json
```

Expected quick final acceptance on this local checkout is now
`passed=9`, `blocked=2`, `failed=0`; the two blockers remain local iOS signing
config and the Apple SDK/Xcode license gate.

Static evidence lives at:

```text
docs/superpowers/verification/p0.48-capture-scene-handoff-acceptance.html
docs/superpowers/verification/assets/p0.48-capture-scene-handoff-acceptance-390x844.png
```

P0.49 adds an in-app mobile `Demo Script` panel for the final iPhone showcase.
The panel derives a short ordered script from existing typed app state and
highlights the next action:

1. Capture Object
2. Forge Myth
3. Load 3D Scene
4. Run NPC Autonomy
5. Request Print Quote
6. Check Resources

The source-only `ios_showcase_acceptance` gate now verifies this script panel,
its Swift core builder, the `ForgeRootView` wiring, and the Xcode project file
reference. Its internal summary moves to `passed=10`, `failed=0`.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
cd services/backend
uv run pytest tests/test_ios_showcase_acceptance.py tests/test_final_acceptance.py -q
```

Expected quick final acceptance on this local checkout remains
`passed=9`, `blocked=2`, `failed=0`; the two blockers remain local iOS signing
config and the Apple SDK/Xcode license gate.

Static evidence lives at:

```text
docs/superpowers/verification/p0.49-mobile-demo-script.html
docs/superpowers/verification/assets/p0.49-mobile-demo-script-390x844.png
```

P0.50 upgrades the iOS 3D artifact preview into a small NPC ritual scene. The
Swift core now builds a deterministic `NPCRitualScene` from the myth session and
the latest NPC agent tick. The SceneKit preview overlays three NPC markers
around the artifact with stable positions and stance colors for acting,
debating, and watching.

The latest tick wins when available, but sparse tick data is backfilled from the
session so the final iPhone demo keeps three visible NPCs around the relic. This
is still the native SwiftUI/SceneKit showcase layer, not Unity.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
cd services/backend
uv run pytest tests/test_ios_showcase_acceptance.py tests/test_final_acceptance.py -q
```

The source-only `ios_showcase_acceptance` gate now includes
`npc_ritual_scene` and reports `passed=11`, `failed=0` when the mobile showcase
source is complete.

Static evidence lives at:

```text
docs/superpowers/verification/p0.50-npc-ritual-scene.html
docs/superpowers/verification/assets/p0.50-npc-ritual-scene-390x844.png
```

P0.51 adds a safe `Showcase Autopilot` control to the mobile `Demo Script`
panel. The Swift core planner reads the current demo script, forge phase, ready
session, NPC tick count, print quote, provider readiness, and loading flags,
then selects exactly one next action:

- forge the myth session
- run backend NPC autonomy
- advance one legacy NPC tick
- request a print quote
- wait, block, or mark the loop ready

The button never auto-starts on app launch and does not create a background
retry loop. It only dispatches one existing app action when tapped, keeping the
final iPhone demo operator-controlled while reducing step-order risk.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
cd services/backend
uv run pytest tests/test_ios_showcase_acceptance.py tests/test_final_acceptance.py -q
```

The source-only `ios_showcase_acceptance` gate now includes
`showcase_autopilot` and reports `passed=12`, `failed=0` when the mobile
showcase source is complete.

Static evidence lives at:

```text
docs/superpowers/verification/p0.51-showcase-autopilot.html
docs/superpowers/verification/assets/p0.51-showcase-autopilot-390x844.png
```

P0.52 adds a compact `Device Preflight` panel to the iOS app source. It appears
after the final showcase summary and before the demo script, then summarizes the
state that matters before a physical iPhone demo:

- whether `PMF_BACKEND_BASE_URL` is still loopback or uses a LAN-reachable URL
- whether backend provider readiness has loaded and is demo-ready
- whether the local final showcase state is ready
- whether saved NPC history exists for restore/resume

The panel is derived from typed Swift core state through
`DevicePreflightSummaryBuilder`; provider keys, checkout links, raw media, and
local paths remain redacted or backend-only. The source-only
`ios_showcase_acceptance` gate now includes `device_preflight` and reports
`passed=13`, `failed=0` when the mobile showcase source is complete.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
cd services/backend
uv run pytest tests/test_ios_showcase_acceptance.py tests/test_final_acceptance.py -q
```

Static evidence lives at:

```text
docs/superpowers/verification/p0.52-device-preflight.html
docs/superpowers/verification/assets/p0.52-device-preflight-390x844.png
```

P0.53 adds a manual backend health probe to the same `Device Preflight` panel.
The panel now includes a compact `Check` action that calls the configured
`PMFBackendBaseURL` `/health` endpoint once per tap and folds the result into
the backend row:

- loopback URLs still block physical iPhone demos
- unchecked non-loopback URLs wait for the operator to tap `Check`
- `{"status":"ok"}` marks backend health ready
- failed, non-2xx, or non-ok health responses block the device preflight

This proves LAN/firewall/server reachability from inside the app source path
before capture, 3D generation, NPC autonomy, or print quote actions. The source
only `ios_showcase_acceptance` gate now includes `backend_health_probe` and
reports `passed=14`, `failed=0` when the mobile showcase source is complete.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
cd services/backend
uv run pytest tests/test_ios_showcase_acceptance.py tests/test_final_acceptance.py -q
```

Static evidence lives at:

```text
docs/superpowers/verification/p0.53-backend-health-probe.html
docs/superpowers/verification/assets/p0.53-backend-health-probe-390x844.png
```

P0.54 upgrades the command-line iOS deploy preflight. After local signing,
bundle id, and `PMF_BACKEND_BASE_URL` values are present and non-loopback,
`make mobile-deploy-preflight` now calls the configured backend `/health`
endpoint:

```bash
make mobile-deploy-preflight
```

It passes only when the backend responds with `status=ok`. Missing backend
processes, wrong LAN URLs, firewall issues, and non-ok health payloads exit `2`
with a safe `Backend health check failed` message. The script uses project-local
files only, does not run Xcode, does not mutate global developer settings, and
does not call Meshy/OpenAI/print providers.

Static evidence lives at:

```text
docs/superpowers/verification/p0.54-deploy-health-preflight.html
docs/superpowers/verification/assets/p0.54-deploy-health-preflight-390x844.png
```

P0.57 adds an ARKit/Object Capture scan package bridge in the SwiftPM mobile
core. `ARKitScanPackageBuilder` takes one exported scan model plus optional
reference images, validates GLB/USDZ/binary and HEIC/HEIF/JPEG/PNG media,
normalizes content types, caps references at 11, and returns a ready
`CaptureMediaSelection(mode: .arkitScan)` for the existing upload and
capture-to-3D path. `ForgeRootView` now uses that bridge when attaching ARKit
scan imports and reference images.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
```

Static evidence lives at:

```text
docs/superpowers/verification/p0.57-arkit-scan-package.html
docs/superpowers/verification/assets/p0.57-arkit-scan-package-390x844.png
```

P0.58 adds the ARKit scan package bridge to the source-only iOS showcase
acceptance gate. `final-acceptance --profile quick` now includes nested
`ios_showcase_acceptance` evidence for `arkit_scan_package`, which checks the
mobile core builder, the `ForgeRootView` bridge, and the Swift contract test
coverage. This remains source-only; it does not run Xcode, device capture, or
provider calls.

Run:

```bash
cd services/backend
uv run pytest tests/test_ios_showcase_acceptance.py tests/test_final_acceptance.py -q
uv run python -m myth_forge_api.cli final-acceptance \
  --profile quick \
  --provider-mode local \
  --repo-root ../.. \
  --output /tmp/personal-myth-forge-final-acceptance-p0.58.json
```

Static evidence lives at:

```text
docs/superpowers/verification/p0.58-arkit-showcase-acceptance.html
docs/superpowers/verification/assets/p0.58-arkit-showcase-acceptance-390x844.png
```

P0.59 replaces the mobile form's static scan readiness copy with a
SwiftPM-tested `CaptureGenerationReadinessBuilder`. The app now summarizes the
actual 3D generation route for capture media:

- guided scans with enough photos show the `multi_image` path, total photo
  count, and the provider cap of four prepared images.
- ARKit scan packages show the `scan_asset` path with scan asset plus reference
  counts.
- provider readiness is folded into the same mobile summary, including
  local-demo-only Meshy key guidance, missing `MESHY_API_KEY`, and redacted
  backend readiness errors.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
```

Static evidence lives at:

```text
docs/superpowers/verification/p0.59-capture-generation-readiness.html
docs/superpowers/verification/assets/p0.59-capture-generation-readiness-390x844.png
```

P0.60 adds the capture generation readiness layer to the source-only iOS
showcase acceptance gate nested inside quick final acceptance. The new
`capture_generation_readiness` feature checks the mobile core builder, the
`ForgeRootView` route-label wiring, the `CaptureFormView` title/route/detail
display inputs, and the Swift contract tests for guided scan and ARKit scan
readiness.

Run:

```bash
cd services/backend
uv run pytest tests/test_ios_showcase_acceptance.py tests/test_final_acceptance.py -q
uv run python -m myth_forge_api.cli final-acceptance \
  --profile quick \
  --provider-mode local \
  --repo-root ../.. \
  --output /tmp/personal-myth-forge-final-acceptance-p0.60.json
```

The nested iOS showcase source summary now reports `passed=16`, `failed=0`
when all checked-in source evidence is present. This remains source-only and
does not run Xcode, device capture, or provider calls.

Static evidence lives at:

```text
docs/superpowers/verification/p0.60-capture-readiness-showcase-acceptance.html
docs/superpowers/verification/assets/p0.60-capture-readiness-showcase-acceptance-390x844.png
```

P0.61 adds a dedicated source/config final acceptance gate for the OpenAI AI
Agent NPC provider path. The new `npc_agent_provider_acceptance` check proves
that the backend has:

- `OpenAINPCDirector` for the initial structured NPC reaction batch.
- `OpenAINPCTickRuntime` for stateless structured NPC ticks.
- `NPC_PROVIDER=openai` factory wiring for both paths.
- readiness/resource handoff coverage for `OPENAI_API_KEY` and backend-only key
  handling.
- backend and mobile documentation that mobile clients receive generated NPC
  state only, never provider keys.

Run:

```bash
cd services/backend
uv run pytest tests/test_npc_agent_provider_acceptance.py tests/test_final_acceptance.py -q
uv run python -m myth_forge_api.cli final-acceptance \
  --profile quick \
  --provider-mode local \
  --repo-root ../.. \
  --output /tmp/personal-myth-forge-final-acceptance-p0.61.json
```

This gate is intentionally source/config only. It does not call OpenAI, create
keys, persist tick history, execute Unity movement, or change the local
deterministic NPC fallback.

Static evidence lives at:

```text
docs/superpowers/verification/p0.61-npc-agent-provider-acceptance.html
docs/superpowers/verification/assets/p0.61-npc-agent-provider-acceptance-390x844.png
```

P0.62 adds the first third-party print quote adapter path. When
`PRINT_PROVIDER=treatstock` and backend-only `TREATSTOCK_API_KEY` are configured,
`POST /v1/print-quotes` uses the official Treatstock printable-pack flow:

- upload a public STL/PLY/3MF candidate URL to `/api/v2/printable-packs`
- request costs from `/api/v2/printable-pack-costs/`
- return the lowest price as a `draft_quote`
- include a checkout handoff URL when Treatstock returns one
- keep `requires_user_approval: true`

Local sessions now also expose a downloadable placeholder 3MF candidate at:

```http
GET /v1/print-candidates/{session_id}/print.3mf
```

The adapter does not place Treatstock orders, collect shipping/contact/payment
details, or upload local private files. Live Treatstock calls only happen when
the backend is explicitly configured with `PRINT_PROVIDER=treatstock`; automated
tests use fake clients and never call Treatstock. `TREATSTOCK_API_BASE_URL` is
available for sandbox/test routing.

Run:

```bash
cd services/backend
uv run pytest tests/test_provider_adapters.py tests/test_config.py \
  tests/test_provider_factory.py tests/test_provider_readiness.py \
  tests/test_api_contract.py tests/test_print_acceptance.py \
  tests/test_final_acceptance.py -q
```

Static evidence lives at:

```text
docs/superpowers/verification/p0.62-treatstock-print-quote-adapter.html
docs/superpowers/verification/assets/p0.62-treatstock-print-quote-adapter-390x844.png
```

P0.65 closes the acceptance loop for the mobile Final Launch readiness path.
The new `mobile_final_launch_readiness_acceptance` gate is now part of quick
and full final acceptance. It checks the real
`GET /v1/final-demo-launch?mode=local` endpoint, invalid-mode rejection, Swift
model/API/root-view/device-preflight/contract-test wiring, and safety flags for
read-only no-secret no-live-call launch reports.

Run:

```bash
cd services/backend
uv run pytest tests/test_mobile_final_launch_readiness_acceptance.py \
  tests/test_final_acceptance.py -q
uv run python -m myth_forge_api.cli final-acceptance \
  --profile quick \
  --provider-mode local \
  --repo-root ../..
```

On this machine the quick final acceptance should now report `11 passed, 2
blocked, 0 failed`. The remaining blocked checks are local device/Xcode gates:
`mobile_deploy_preflight` and `mobile_xcode_build`.

Static evidence lives at:

```text
docs/superpowers/verification/p0.65-mobile-final-launch-readiness-acceptance.html
docs/superpowers/verification/assets/p0.65-mobile-final-launch-readiness-acceptance-390x844.png
```

P0.66 adds a unified final resource apply path for the last operator handoff.
The tracked `services/backend/final-resources.env.example` documents all values
needed for configured Meshy 3D generation, OpenAI NPC Agent ticks, optional
Treatstock quote handoff, and iPhone deployment. The filled copy lives at
`services/backend/.local/final-resources.env` and remains ignored.

Run:

```bash
mkdir -p services/backend/.local
cp services/backend/final-resources.env.example services/backend/.local/final-resources.env
$EDITOR services/backend/.local/final-resources.env
make final-apply-resources
cd services/backend
uv run pytest tests/test_final_resource_apply_script.py \
  tests/test_backend_env_writer_script.py \
  tests/test_resource_template_acceptance.py -q
```

The apply script validates required resources before writing, rejects unknown
keys and loopback iPhone backend URLs, requires `TREATSTOCK_API_KEY` when
`PRINT_PROVIDER=treatstock`, and prints only redacted key status.

Static evidence lives at:

```text
docs/superpowers/verification/p0.66-unified-resource-apply.html
docs/superpowers/verification/assets/p0.66-unified-resource-apply-390x844.png
```

P0.67 adds an ARKit/Object Capture scan generation acceptance gate. The existing
`capture_3d_acceptance` gate proves guided-scan reference images reach the 3D
provider request; the new `arkit_scan_generation_acceptance` gate covers the
Object Capture path by storing a synthetic `arkit_scan` package with one GLB scan
asset plus two reference images, building backend generation sources, and
running the normal myth-session pipeline with a recording local 3D provider.

Run:

```bash
cd services/backend
uv run pytest tests/test_arkit_scan_generation_acceptance.py \
  tests/test_final_acceptance.py -q
uv run python -m myth_forge_api.cli final-acceptance \
  --profile quick \
  --provider-mode local \
  --repo-root ../.. \
  --output .local/final-acceptance-p0.67.json
```

On this machine the quick final acceptance should report `12 passed, 2 blocked,
0 failed`. The new gate is local-only by default, does not call Meshy, and
reports only counts, content types, provenance, and safety flags.

Static evidence lives at:

```text
docs/superpowers/verification/p0.67-arkit-scan-generation-acceptance.html
docs/superpowers/verification/assets/p0.67-arkit-scan-generation-acceptance-390x844.png
```

P0.68 adds iOS local network privacy readiness for the physical-device demo.
The app already reads `PMF_BACKEND_BASE_URL` from deployment config and allows
local networking through App Transport Security; it now also declares
`NSLocalNetworkUsageDescription` so the iPhone build has a clear purpose string
for connecting to the LAN-hosted backend.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
cd services/backend
uv run pytest tests/test_ios_showcase_acceptance.py -q
```

Quick final acceptance includes the strengthened `ios_showcase_acceptance`
`deploy_config` source gate. This does not run Xcode, sign the app, accept Apple
licenses, or call providers.

Static evidence lives at:

```text
docs/superpowers/verification/p0.68-ios-local-network-readiness.html
docs/superpowers/verification/assets/p0.68-ios-local-network-readiness-390x844.png
```

P0.69 updates the final demo launch report to make `make
final-apply-resources` the single primary resource application step. The older
`backend-write-provider-env` and `mobile-write-deploy-config` commands remain
available for lower-level debugging, but local and configured final launch
command lists now point at the unified one-file handoff.

Run:

```bash
cd services/backend
uv run pytest tests/test_final_demo_launch.py \
  tests/test_resource_handoff.py \
  tests/test_resource_template_acceptance.py -q
```

The report phase id to inspect is `apply_final_resources`; in local no-key mode
the overall launch can still be usable while this phase is blocked or partial.
It becomes ready only when the unified apply command has both the core
Meshy/OpenAI backend resources and iOS deploy config readiness. The report is
still configuration-only and never calls live providers.

Static evidence lives at:

```text
docs/superpowers/verification/p0.69-final-launch-unified-apply.html
docs/superpowers/verification/assets/p0.69-final-launch-unified-apply-390x844.png
```

P0.70 adds a read-only preflight for the unified final resource file. It checks
`services/backend/.local/final-resources.env` before the apply step, reports
missing/unknown keys, blocks loopback iPhone backend URLs, and requires
`TREATSTOCK_API_KEY` when `PRINT_PROVIDER=treatstock`. Reports expose only key
names and redacted configured status.

Run:

```bash
make final-resources-preflight
cd services/backend
uv run pytest tests/test_final_resources_preflight.py \
  tests/test_final_demo_launch.py \
  tests/test_resource_template_acceptance.py -q
```

`final-demo-launch` now includes a top-level `final_resources_preflight` object.
The `apply_final_resources` phase is `missing` when the final resources file is
absent, `blocked` when the file is invalid, and `ready` when the file can be
applied.

Static evidence lives at:

```text
docs/superpowers/verification/p0.70-final-resources-preflight.html
docs/superpowers/verification/assets/p0.70-final-resources-preflight-390x844.png
```

P0.71 surfaces that backend preflight inside the iPhone Device Preflight panel.
`FinalDemoLaunchReport` now decodes `final_resources_preflight`, and
`DevicePreflightSummaryBuilder` adds a `Final Resources` row. Missing resource
files show as waiting, blocked resource files show as blocked, and ready files
show as ready. Details still pass through mobile redaction, so provider keys and
local paths are withheld.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
cd services/backend
uv run pytest tests/test_mobile_final_launch_readiness_acceptance.py -q
```

Static evidence lives at:

```text
docs/superpowers/verification/p0.71-mobile-final-resources-preflight.html
docs/superpowers/verification/assets/p0.71-mobile-final-resources-preflight-390x844.png
```

P0.72 adds a read-only `Final Launch Status` panel to the iPhone app. The app
already fetches `/v1/final-demo-launch`; it now maps that sanitized backend
report into mobile phase rows, final resource actions, and command rows so the
operator can see the next Mac-side launch step without leaving the device demo.

The panel does not run commands, read resource files, or expose provider keys.
All report strings pass through mobile redaction before display.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
cd services/backend
uv run pytest tests/test_mobile_final_launch_readiness_acceptance.py -q
```

Static evidence lives at:

```text
docs/superpowers/verification/p0.72-mobile-final-launch-status.html
docs/superpowers/verification/assets/p0.72-mobile-final-launch-status-390x844.png
```

P0.73 adds an explicit mobile `Context Capsule Review` step. The iPhone app now
requires the operator to approve the manually entered summary capsule before
`Forge Myth` can run. Editing the theme or tone clears approval, and
`forgeMyth` has a source-level guard in addition to the disabled button state.

This keeps the first demo privacy boundary concrete: no raw email, chat,
calendar, document, or file bodies are read by the app; only the approved
summary capsule is sent to the backend.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
cd services/backend
uv run pytest tests/test_ios_showcase_acceptance.py -q
```

Static evidence lives at:

```text
docs/superpowers/verification/p0.73-mobile-context-capsule-review.html
docs/superpowers/verification/assets/p0.73-mobile-context-capsule-review-390x844.png
```

P0.74 adds mobile `Artifact Handoff` actions beneath the 3D preview. The iPhone
app now turns prepared generated-asset state into explicit rows for SceneKit
preview readiness, cached asset sharing, GLB/GLTF conversion requirements, and
download retry.

The action builder is pure Swift mobile core code, so it can be contract-tested
without a simulator or live Meshy call. Display strings redact provider secrets,
checkout fields, and full local paths; share uses the cached app-sandbox URL
only when the existing asset preparer has produced one.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
cd services/backend
uv run pytest tests/test_ios_showcase_acceptance.py -q
```

Static evidence lives at:

```text
docs/superpowers/verification/p0.74-mobile-artifact-actions.html
docs/superpowers/verification/assets/p0.74-mobile-artifact-actions-390x844.png
```

P0.75 adds a mobile `NPC Agent Mode` panel above the NPC autonomy controls.
The iPhone app now makes the NPC runtime state explicit: local deterministic
demo mode, OpenAI-backed AI Agent readiness, or missing backend setup such as
`OPENAI_API_KEY`.

The mode summary is pure Swift mobile core code. It combines session runtime,
latest tick runtime, tick history, and backend NPC provider readiness, then
redacts unsafe strings before the SwiftUI layer renders provider/runtime
labels, trace counts, missing env names, and privacy notes.

Run:

```bash
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
cd services/backend
uv run pytest tests/test_ios_showcase_acceptance.py -q
```

Static evidence lives at:

```text
docs/superpowers/verification/p0.75-mobile-npc-agent-mode.html
docs/superpowers/verification/assets/p0.75-mobile-npc-agent-mode-390x844.png
```

P0.76 embeds a read-only `final_acceptance_readiness` report in
`/v1/final-demo-launch`. The backend reads the latest saved local final
acceptance JSON at `services/backend/.local/final-acceptance-local.json` and
summarizes whether it is missing, blocked, or ready. It does not run Xcode,
deployment scripts, provider calls, or signing commands during API handling.

The iPhone `Final Launch Status` panel now renders an `Acceptance` section so
the operator can see blocked gates such as `mobile_deploy_preflight` and
`mobile_xcode_build`, including their safe classifications and Mac-side
commands. All rows are redacted before display.

Run:

```bash
cd services/backend
uv run pytest tests/test_final_acceptance_readiness.py tests/test_final_demo_launch.py tests/test_ios_showcase_acceptance.py -q
cd ../..
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
```

Static evidence lives at:

```text
docs/superpowers/verification/p0.76-final-acceptance-readiness.html
docs/superpowers/verification/assets/p0.76-final-acceptance-readiness-390x844.png
```

P0.77 embeds a read-only `final_operator_handoff` report in
`/v1/final-demo-launch`. It consolidates the final Mac-side operation sequence:
resource preflight, unified apply, LAN backend startup, local final acceptance,
iOS deploy preflight, Xcode build gate, and optional configured live-provider
acceptance.

The iPhone `Final Launch Status` panel now renders a `Next` section with the
first safe operator actions from that handoff. The app still does not execute
Mac commands, trigger Xcode, deploy to a device, accept Apple licenses, mutate
global state, or call Meshy/OpenAI/Treatstock. Display rows are redacted before
they reach the phone.

Run:

```bash
cd services/backend
uv run pytest tests/test_final_operator_handoff.py tests/test_final_demo_launch.py tests/test_ios_showcase_acceptance.py -q
cd ../..
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
```

Static evidence lives at:

```text
docs/superpowers/verification/p0.77-final-operator-handoff.html
docs/superpowers/verification/assets/p0.77-final-operator-handoff-390x844.png
```

P0.78 adds a mobile final launch mode handoff. `PMF_FINAL_LAUNCH_MODE` now lives
in the final resource bundle and iOS deployment config, defaults to `local`, and
is exposed to the app through `PMFFinalLaunchMode`.

The iPhone Final Launch surface has a segmented `Local` / `Configured` control.
Switching it reloads `/v1/final-demo-launch` with the selected mode, so an
operator can inspect the no-key local demo lane or the configured provider/key
lane from the phone. This remains read-only: the app does not run Mac commands,
trigger Xcode, accept Apple licenses, mutate global state, or call
Meshy/OpenAI/Treatstock by switching modes.

Run:

```bash
cd services/backend
uv run pytest tests/test_final_resources_preflight.py tests/test_final_resource_apply_script.py tests/test_ios_showcase_acceptance.py tests/test_mobile_final_launch_readiness_acceptance.py -q
cd ../..
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
swift run --package-path apps/mobile/ios PersonalMythForgeMobileCoreContractTests
swift build --package-path apps/mobile/ios --product PersonalMythForgeMobileAppCompileCheck
```

Static evidence lives at:

```text
docs/superpowers/verification/p0.78-mobile-final-launch-mode.html
docs/superpowers/verification/assets/p0.78-mobile-final-launch-mode-390x844.png
```

P0.79 extends the physical-device deploy preflight to validate the final launch
mode before the iPhone demo. `mobile-deploy-preflight` now reads
`PMF_FINAL_LAUNCH_MODE` from the merged deployment config, accepts only `local`
or `configured`, and prints the selected mode on success.

This catches hand-edited local config mistakes before backend health checks and
before any Xcode build gate. It still does not run Xcode, mutate signing state,
accept licenses, or call live providers.

Run:

```bash
cd services/backend
uv run pytest tests/test_ios_deploy_preflight_script.py tests/test_ios_deploy_config_writer_script.py -q
cd ../..
swift run --package-path apps/mobile/ios PersonalMythForgeMobileProjectChecks
```

Static evidence lives at:

```text
docs/superpowers/verification/p0.79-deploy-preflight-launch-mode.html
docs/superpowers/verification/assets/p0.79-deploy-preflight-launch-mode-390x844.png
```
