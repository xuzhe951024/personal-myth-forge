# First Showable Demo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a runnable mobile-first local web demo for Personal Myth Forge with provider injection, optional Meshy text-to-3D generation, and a CLI for 3D prompt spikes.

**Architecture:** Keep `POST /v1/myth-sessions` as the canonical session API. Add settings and provider factories so the existing deterministic local provider remains the default while `MeshyThreeDProvider` can be selected by environment or CLI. Serve a small browser demo from FastAPI at `/demo`; it posts the existing request shape and renders the returned `MythSession`.

**Tech Stack:** Python 3.10, FastAPI, Pydantic v2, httpx, python-dotenv, pytest, ruff, static HTML/CSS/JavaScript.

---

### Task 1: Settings And Provider Injection

**Files:**
- Create: `services/backend/src/myth_forge_api/config.py`
- Create: `services/backend/src/myth_forge_api/providers/factory.py`
- Modify: `services/backend/src/myth_forge_api/domain/pipeline.py`
- Modify: `services/backend/src/myth_forge_api/providers/three_d.py`
- Modify: `services/backend/src/myth_forge_api/providers/printing.py`
- Modify: `services/backend/tests/test_myth_pipeline.py`
- Create: `services/backend/tests/test_provider_factory.py`

- [x] **Step 1: Write failing test for injected 3D provider**

Add this test to `services/backend/tests/test_myth_pipeline.py`:

```python
from myth_forge_api.domain.models import GeneratedAsset


class RecordingThreeDProvider:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def generate_game_asset(self, session_id: str, prompt: str) -> GeneratedAsset:
        self.calls.append((session_id, prompt))
        return GeneratedAsset(
            kind="game_asset",
            provider="recording",
            format="glb",
            uri=f"recording://{session_id}.glb",
            prompt=prompt,
            moderation_status="needs_review",
        )


def test_pipeline_accepts_injected_three_d_provider() -> None:
    provider = RecordingThreeDProvider()

    session = create_demo_myth_session(
        object_observation={
            "label": "silver spoon",
            "materials": ["metal"],
            "source": "manual_upload",
        },
        context_capsule={
            "current_theme": "making peace with change",
            "desired_tone": "gentle and uncanny",
        },
        three_d_provider=provider,
    )

    assert session.generated_asset.provider == "recording"
    assert provider.calls == [(session.session_id, session.myth_seed.generation_prompt)]
```

- [x] **Step 2: Run the test and verify it fails**

Run: `cd services/backend && uv run pytest tests/test_myth_pipeline.py::test_pipeline_accepts_injected_three_d_provider -q`

Expected: fail because `create_demo_myth_session` does not accept `three_d_provider`.

- [x] **Step 3: Implement provider protocols and pipeline injection**

Add `ThreeDProvider` to `providers/three_d.py`:

```python
from typing import Protocol


class ThreeDProvider(Protocol):
    provider_name: str

    def generate_game_asset(self, session_id: str, prompt: str) -> GeneratedAsset:
        ...
```

Add `PrintProvider` to `providers/printing.py`:

```python
from typing import Protocol


class PrintProvider(Protocol):
    provider_name: str

    def create_print_candidate(self, generated_asset: GeneratedAsset) -> PrintCandidate:
        ...
```

Update `create_demo_myth_session` signature:

```python
def create_demo_myth_session(
    object_observation: ObjectObservation | Mapping[str, Any],
    context_capsule: ContextCapsule | Mapping[str, Any],
    three_d_provider: ThreeDProvider | None = None,
    print_provider: PrintProvider | None = None,
) -> MythSession:
    observation = _coerce_object_observation(object_observation)
    capsule = _coerce_context_capsule(context_capsule)
    session_id = _stable_session_id(observation, capsule)
    object_card = _create_object_card(observation)
    myth_seed = _create_myth_seed(object_card, capsule)
    selected_three_d_provider = three_d_provider or LocalThreeDProvider()
    generated_asset = selected_three_d_provider.generate_game_asset(
        session_id=session_id,
        prompt=myth_seed.generation_prompt,
    )
    npc_reactions = _create_npc_reactions(object_card, myth_seed)
    selected_print_provider = print_provider or LocalPrintProvider()
    print_candidate = selected_print_provider.create_print_candidate(generated_asset)
    return MythSession(...)
```

- [x] **Step 4: Run the injection test and full backend tests**

Run:

```bash
cd services/backend
uv run pytest tests/test_myth_pipeline.py::test_pipeline_accepts_injected_three_d_provider -q
uv run pytest
```

Expected: injection test passes, then all tests pass.

- [x] **Step 5: Write failing tests for settings and provider factory**

Create `services/backend/tests/test_provider_factory.py`:

```python
from myth_forge_api.config import Settings
from myth_forge_api.providers.factory import build_three_d_provider
from myth_forge_api.providers.three_d import LocalThreeDProvider, MeshyThreeDProvider


def test_provider_factory_defaults_to_local_provider() -> None:
    provider = build_three_d_provider(Settings())

    assert isinstance(provider, LocalThreeDProvider)


def test_provider_factory_selects_meshy_provider() -> None:
    provider = build_three_d_provider(
        Settings(three_d_provider="meshy", meshy_api_key="test-key")
    )

    assert isinstance(provider, MeshyThreeDProvider)
```

- [x] **Step 6: Run provider factory tests and verify they fail**

Run: `cd services/backend && uv run pytest tests/test_provider_factory.py -q`

Expected: fail because `config.py`, `factory.py`, and `MeshyThreeDProvider` do not exist.

- [x] **Step 7: Implement settings and factory skeleton**

Create `config.py`:

```python
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    three_d_provider: str = "local"
    meshy_api_key: str | None = None
    meshy_api_base_url: str = "https://api.meshy.ai"
    meshy_poll_interval_seconds: float = 5.0
    meshy_max_wait_seconds: float = 600.0


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    load_dotenv()
    source = env or os.environ
    return Settings(
        three_d_provider=source.get("THREE_D_PROVIDER", "local").strip().lower(),
        meshy_api_key=source.get("MESHY_API_KEY") or None,
        meshy_api_base_url=source.get("MESHY_API_BASE_URL", "https://api.meshy.ai"),
        meshy_poll_interval_seconds=float(source.get("MESHY_POLL_INTERVAL_SECONDS", "5")),
        meshy_max_wait_seconds=float(source.get("MESHY_MAX_WAIT_SECONDS", "600")),
    )
```

Create `providers/factory.py`:

```python
from myth_forge_api.config import Settings, load_settings
from myth_forge_api.providers.three_d import LocalThreeDProvider, MeshyThreeDProvider, ThreeDProvider


def build_three_d_provider(settings: Settings | None = None) -> ThreeDProvider:
    selected_settings = settings or load_settings()
    if selected_settings.three_d_provider == "local":
        return LocalThreeDProvider()
    if selected_settings.three_d_provider == "meshy":
        return MeshyThreeDProvider.from_settings(selected_settings)
    raise ValueError(f"Unsupported THREE_D_PROVIDER: {selected_settings.three_d_provider}")
```

Add a temporary `MeshyThreeDProvider` class that raises `NotImplementedError` only in `generate_game_asset`, not during construction.

- [x] **Step 8: Run provider factory tests**

Run: `cd services/backend && uv run pytest tests/test_provider_factory.py -q`

Expected: provider factory tests pass.

- [x] **Step 9: Commit Task 1**

Run:

```bash
git add services/backend/src/myth_forge_api services/backend/tests/test_myth_pipeline.py services/backend/tests/test_provider_factory.py
git commit -m "feat: add provider injection and settings"
```

### Task 2: Meshy Provider And CLI

**Files:**
- Modify: `services/backend/pyproject.toml`
- Modify: `services/backend/src/myth_forge_api/providers/three_d.py`
- Create: `services/backend/src/myth_forge_api/cli.py`
- Create: `services/backend/tests/test_meshy_provider.py`
- Create: `services/backend/tests/test_cli.py`

- [x] **Step 1: Move `httpx` into runtime dependencies**

Modify `services/backend/pyproject.toml` so `[project].dependencies` includes `httpx>=0.27.0` and `[dependency-groups].dev` keeps pytest and ruff.

Run: `cd services/backend && uv lock`

Expected: `uv.lock` updates successfully.

- [x] **Step 2: Write failing Meshy success test**

Create `services/backend/tests/test_meshy_provider.py` with an `httpx.MockTransport` sequence:

```python
import httpx

from myth_forge_api.providers.three_d import MeshyThreeDProvider


def test_meshy_provider_creates_preview_refines_and_returns_glb() -> None:
    requests: list[httpx.Request] = []
    responses = [
        httpx.Response(200, json={"result": "preview-123"}),
        httpx.Response(200, json={"id": "preview-123", "status": "SUCCEEDED", "model_urls": {"glb": "https://assets.example/preview.glb"}}),
        httpx.Response(200, json={"result": "refine-456"}),
        httpx.Response(200, json={"id": "refine-456", "status": "SUCCEEDED", "model_urls": {"glb": "https://assets.example/refined.glb"}}),
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return responses.pop(0)

    client = httpx.Client(transport=httpx.MockTransport(handler), base_url="https://api.meshy.test")
    provider = MeshyThreeDProvider(
        api_key="test-key",
        client=client,
        poll_interval_seconds=0,
        max_wait_seconds=1,
    )

    asset = provider.generate_game_asset("myth_test", "Create a shrine key.")

    assert asset.provider == "meshy"
    assert asset.uri == "https://assets.example/refined.glb"
    assert [request.method for request in requests] == ["POST", "GET", "POST", "GET"]
```

- [x] **Step 3: Run Meshy success test and verify it fails**

Run: `cd services/backend && uv run pytest tests/test_meshy_provider.py::test_meshy_provider_creates_preview_refines_and_returns_glb -q`

Expected: fail because the provider is not implemented.

- [x] **Step 4: Implement Meshy provider**

Implement in `providers/three_d.py`:

```python
class MeshyProviderError(RuntimeError):
    pass


class MeshyConfigurationError(MeshyProviderError):
    pass


class MeshyTaskTimeoutError(MeshyProviderError):
    pass
```

`MeshyThreeDProvider.generate_game_asset` should:

- Require a non-empty API key.
- POST `/openapi/v2/text-to-3d` with `{"mode": "preview", "prompt": prompt[:600], "target_formats": ["glb"], "moderation": True}`.
- Poll `GET /openapi/v2/text-to-3d/{preview_task_id}` until `SUCCEEDED`.
- POST refine with `{"mode": "refine", "preview_task_id": preview_task_id, "target_formats": ["glb"], "moderation": True}`.
- Poll refine until `SUCCEEDED`.
- Return `GeneratedAsset(kind="game_asset", provider="meshy", format="glb", uri=refined_task["model_urls"]["glb"], prompt=prompt, moderation_status="needs_review")`.

- [x] **Step 5: Run Meshy success test**

Run: `cd services/backend && uv run pytest tests/test_meshy_provider.py::test_meshy_provider_creates_preview_refines_and_returns_glb -q`

Expected: pass.

- [x] **Step 6: Write failing Meshy error tests**

Add tests for:

```python
def test_meshy_provider_requires_api_key() -> None:
    provider = MeshyThreeDProvider(api_key="")
    with pytest.raises(MeshyConfigurationError):
        provider.generate_game_asset("myth_test", "Create a shrine key.")


def test_meshy_provider_raises_for_failed_task() -> None:
    # POST returns preview id; first GET returns FAILED with task_error.message.
    # Expected: MeshyProviderError contains the provider message.


def test_meshy_provider_times_out_when_task_never_finishes() -> None:
    # POST returns preview id; GET always returns IN_PROGRESS.
    # Expected: MeshyTaskTimeoutError.
```

- [x] **Step 7: Run and implement until error tests pass**

Run: `cd services/backend && uv run pytest tests/test_meshy_provider.py -q`

Expected: all Meshy provider tests pass.

- [x] **Step 8: Write failing CLI local test**

Create `services/backend/tests/test_cli.py`:

```python
import json

from myth_forge_api.cli import main


def test_cli_generates_local_asset_json(capsys) -> None:
    exit_code = main(["generate-asset", "--provider", "local", "--prompt", "Create a tiny moon cup."])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["provider"] == "local_stub"
    assert payload["format"] == "glb"
```

- [x] **Step 9: Run CLI test and verify it fails**

Run: `cd services/backend && uv run pytest tests/test_cli.py -q`

Expected: fail because `cli.py` does not exist.

- [x] **Step 10: Implement CLI**

Create `cli.py` with `argparse` subcommands:

- `generate-asset --prompt TEXT --provider local|meshy`
- `generate-batch --prompts-file PATH --provider local|meshy`

The CLI builds the selected provider, emits JSON to stdout, returns `0` on success, returns `1` on provider errors, and writes provider errors to stderr.

- [x] **Step 11: Run CLI and provider tests**

Run:

```bash
cd services/backend
uv run pytest tests/test_meshy_provider.py tests/test_cli.py -q
```

Expected: all selected tests pass.

- [x] **Step 12: Commit Task 2**

Run:

```bash
git add services/backend/pyproject.toml services/backend/uv.lock services/backend/src/myth_forge_api/providers/three_d.py services/backend/src/myth_forge_api/cli.py services/backend/tests/test_meshy_provider.py services/backend/tests/test_cli.py
git commit -m "feat: add meshy provider and asset CLI"
```

### Task 3: FastAPI Demo Surface

**Files:**
- Modify: `services/backend/src/myth_forge_api/main.py`
- Create: `services/backend/src/myth_forge_api/demo/index.html`
- Create: `services/backend/src/myth_forge_api/demo/styles.css`
- Create: `services/backend/src/myth_forge_api/demo/app.js`
- Modify: `services/backend/tests/test_api_contract.py`

- [x] **Step 1: Write failing `/demo` route test**

Add to `services/backend/tests/test_api_contract.py`:

```python
def test_demo_route_serves_mobile_first_shell() -> None:
    client = TestClient(app)

    response = client.get("/demo")

    assert response.status_code == 200
    assert "Personal Myth Forge" in response.text
    assert "myth-form" in response.text
```

- [x] **Step 2: Run route test and verify it fails**

Run: `cd services/backend && uv run pytest tests/test_api_contract.py::test_demo_route_serves_mobile_first_shell -q`

Expected: fail with 404.

- [x] **Step 3: Implement demo route and static mount**

In `main.py`, add:

```python
from pathlib import Path

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

DEMO_DIR = Path(__file__).parent / "demo"
app.mount("/demo/static", StaticFiles(directory=DEMO_DIR), name="demo-static")


@app.get("/demo", include_in_schema=False)
def demo() -> FileResponse:
    return FileResponse(DEMO_DIR / "index.html")
```

- [x] **Step 4: Create HTML/CSS/JS demo files**

`index.html` should include a real form, a result region, links to `/demo/static/styles.css` and `/demo/static/app.js`, and semantic sections for artifact, NPCs, and print review.

`app.js` should build the existing `MythSessionRequest` shape, submit it to `/v1/myth-sessions`, and render the JSON result without external state.

`styles.css` should be mobile-first, readable at 390px width, and use stable dimensions for form controls, action buttons, and the artifact stage.

- [x] **Step 5: Run demo route test**

Run: `cd services/backend && uv run pytest tests/test_api_contract.py::test_demo_route_serves_mobile_first_shell -q`

Expected: pass.

- [x] **Step 6: Wire API route to provider factory**

Modify `main.py` so `create_myth_session` calls:

```python
create_demo_myth_session(
    object_observation=request.object_observation,
    context_capsule=request.context_capsule,
    three_d_provider=build_three_d_provider(),
)
```

Keep default behavior deterministic because `THREE_D_PROVIDER` defaults to `local`.

- [x] **Step 7: Run API contract tests**

Run: `cd services/backend && uv run pytest tests/test_api_contract.py -q`

Expected: existing API test and demo route test pass.

- [x] **Step 8: Commit Task 3**

Run:

```bash
git add services/backend/src/myth_forge_api/main.py services/backend/src/myth_forge_api/demo services/backend/tests/test_api_contract.py
git commit -m "feat: add local web demo"
```

### Task 4: Documentation And Verification

**Files:**
- Modify: `README.md`
- Modify: `.env.example`
- Modify: `Makefile`
- Modify: `docs/iteration-roadmap.md`

- [x] **Step 1: Update commands and env docs**

Document:

```bash
make backend-test
make backend-lint
make backend-dev
open http://127.0.0.1:8080/demo
cd services/backend && uv run python -m myth_forge_api.cli generate-asset --provider local --prompt "Create a brass key relic."
```

Document Meshy:

```bash
export MESHY_API_KEY=...
cd services/backend
uv run python -m myth_forge_api.cli generate-asset --provider meshy --prompt "Create a weathered key worshiped by a tiny village."
```

- [x] **Step 2: Add Makefile CLI helper**

Add:

```make
backend-demo:
	cd services/backend && uv run uvicorn myth_forge_api.main:app --reload --port 8080

backend-generate-local:
	cd services/backend && uv run python -m myth_forge_api.cli generate-asset --provider local --prompt "Create a brass key relic worshiped by a tiny village."
```

- [x] **Step 3: Update roadmap**

Mark the first showable local web demo as the bridge between P0 and P1. Keep Unity import as the next milestone after Meshy prompt quality validation.

- [x] **Step 4: Run full verification**

Run:

```bash
make backend-lint
make backend-test
cd services/backend && uv run python -m myth_forge_api.cli generate-asset --provider local --prompt "Create a brass key relic."
```

Expected: lint passes, tests pass, CLI prints JSON with `provider` equal to `local_stub`.

- [x] **Step 5: Start server and verify demo HTML**

Run:

```bash
cd services/backend
uv run uvicorn myth_forge_api.main:app --port 8080
```

In another command:

```bash
curl -s http://127.0.0.1:8080/demo | rg "Personal Myth Forge|myth-form"
curl -s http://127.0.0.1:8080/health
```

Expected: `/demo` returns the shell and `/health` returns `{"status":"ok"}`.

- [x] **Step 6: Commit Task 4**

Run:

```bash
git add README.md .env.example Makefile docs/iteration-roadmap.md
git commit -m "docs: document first demo workflow"
```
