# First Showable Demo Design

## Product Goal

Create the first local demo that can be opened in a browser and shown on a phone-sized viewport. A user enters a real-world object observation and an approved personal context capsule, generates a myth session, sees the object card, myth seed, NPC interpretations, game asset metadata, and print candidate review state, and can optionally route game asset generation through Meshy when a `MESHY_API_KEY` is available.

This demo is not the final Unity/iOS vertical slice. It is a backend-first proof surface that validates the core loop and gives the project a working integration point for the later Unity client.

## Scope

Included:

- A mobile-first local web demo served by FastAPI at `/demo`.
- The existing `POST /v1/myth-sessions` endpoint remains the canonical session API.
- A `ThreeDProvider` protocol so the pipeline can use either local deterministic generation or Meshy.
- A provider factory controlled by environment variables.
- A `MeshyThreeDProvider` for text-to-3D GLB generation.
- A CLI for generating one asset from a prompt and for running a prompt batch file.
- Tests that keep local demo behavior deterministic and unit-test Meshy request/response handling without calling the real API.
- Documentation for running the local demo and the Meshy spike.

Excluded for this first demo:

- Unity project creation or iOS device deployment.
- Real object camera upload and vision classification.
- Full autonomous NPC runtime with persistent memory.
- Treatstock/Sculpteo quote creation or order placement.
- Real print repair workflow beyond the existing print candidate placeholder.

## Architecture

```text
Browser / phone viewport
  -> FastAPI /demo static shell
  -> POST /v1/myth-sessions
  -> create_demo_myth_session(...)
  -> ThreeDProvider selected by settings
       local_stub: deterministic metadata, no external calls
       meshy: preview task -> poll -> refine task -> poll -> GLB URL
  -> LocalPrintProvider
  -> MythSession JSON rendered in demo UI
```

The backend keeps provider code behind small interfaces. The domain pipeline accepts a `ThreeDProvider` and `PrintProvider`; the FastAPI route uses a factory to choose defaults from environment variables. Tests can inject local or fake providers directly.

## Demo UX

The first screen is the actual demo, not a landing page. It uses a compact mobile-first layout with:

- Object fields: label, source, materials, visual notes.
- Context capsule fields: current theme, desired tone, recent milestone.
- A generate button.
- A review surface showing session status, myth seed, NPC reactions, game asset, and print candidate.
- A 3D asset area that displays:
  - A linked GLB and embedded viewer when the generated asset URI is browser-loadable.
  - A procedural placeholder when the provider returns `local://`.

The UI copy should be functional and in-world enough for a demo, but it should not explain implementation details or ask the viewer to read docs.

## Meshy Provider Behavior

The Meshy provider uses the official text-to-3D v2 flow:

1. Create a preview task with `mode: "preview"`, the myth prompt, `target_formats: ["glb"]`, and moderation enabled.
2. Poll the preview task until it reaches a terminal status.
3. Create a refine task with `mode: "refine"` and the completed preview task id.
4. Poll the refine task until it succeeds.
5. Return a `GeneratedAsset` with provider `meshy`, format `glb`, URI from `model_urls.glb`, prompt, and moderation status `needs_review`.

Failures return typed provider exceptions. The API maps provider errors to a blocked myth session only when the provider is selected for the session path. The CLI exits non-zero and prints a concise error message.

## Configuration

Environment variables:

- `THREE_D_PROVIDER=local` or `meshy`; default `local`.
- `MESHY_API_KEY`; required only when `THREE_D_PROVIDER=meshy` or the CLI provider is `meshy`.
- `MESHY_API_BASE_URL`; default `https://api.meshy.ai`.
- `MESHY_POLL_INTERVAL_SECONDS`; default `5`.
- `MESHY_MAX_WAIT_SECONDS`; default `600`.

The local demo must run without any external API key.

## Data Flow

`POST /v1/myth-sessions` receives the existing `MythSessionRequest`. The pipeline creates the object card and myth seed first, then passes `session_id` and `myth_seed.generation_prompt` into the selected 3D provider. The returned `GeneratedAsset` is included in `MythSession.generated_asset`, and the print provider derives `MythSession.print_candidate` from that asset.

The CLI accepts a raw myth prompt. It bypasses object-card and NPC generation and exercises only the selected 3D provider, returning asset JSON for quick Meshy quality checks.

## Error Handling

- Missing `MESHY_API_KEY` for Meshy raises a configuration error before making network calls.
- Meshy HTTP 400/401/402/429 and 5xx responses become provider errors that include status code and provider message when available.
- Task statuses `FAILED`, `EXPIRED`, or unknown terminal states become provider errors.
- Poll timeout becomes a provider timeout error.
- Local demo form failures render an inline error and keep the previous result visible if one exists.

## Testing

Tests cover:

- Pipeline can inject a custom `ThreeDProvider`.
- Provider factory defaults to local and selects Meshy from settings.
- Meshy provider sends preview and refine requests with the expected payloads.
- Meshy provider polls and returns a GLB asset from a successful fake task sequence.
- Meshy provider surfaces missing key, failed task, and timeout errors.
- `POST /v1/myth-sessions` still returns a deterministic local session by default.
- `/demo` serves the web demo shell.
- CLI with local provider emits JSON without external calls.

No unit test calls the real Meshy API. Real Meshy runs are manual spike commands documented in the README.

## Acceptance Criteria

- `make backend-lint` passes.
- `make backend-test` passes.
- `make backend-dev` serves the API.
- Opening `http://127.0.0.1:8080/demo` shows a mobile-first demo UI.
- Submitting the default local demo form returns and renders a complete myth session.
- `THREE_D_PROVIDER=local` requires no external secrets.
- The Meshy CLI path can be run with `MESHY_API_KEY` and returns a GLB URL or a clear provider error.
- Existing personal context privacy boundary remains intact: the backend accepts only user-provided capsule fields and never reads raw private data.

## Approach Decision

Three approaches were considered:

- Backend-only Meshy adapter: fastest technical spike, but not showable to non-engineers.
- Web demo only with local provider: showable, but does not move the critical 3D provider risk.
- Web demo plus optional Meshy provider and CLI: slightly larger, but it creates both a showable surface and the right technical path for 20-prompt 3D quality evaluation.

The chosen approach is the third option.
