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
