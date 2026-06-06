from __future__ import annotations

import json
import re
from base64 import b64encode
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Path as PathParam, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

from myth_forge_api.config import load_settings
from myth_forge_api.domain.models import (
    CAPTURE_ID_PATTERN,
    SESSION_ID_PATTERN,
    MythSession,
    MythSessionFromCaptureRequest,
    MythSessionHistory,
    MythSessionRequest,
    NPCAutonomyRun,
    NPCAutonomyRunRequest,
    NPCAgentTick,
    NPCAgentTickRequest,
    ObjectCapture,
    ObjectCaptureMetadata,
    ProviderReadinessResponse,
)
from myth_forge_api.domain.pipeline import create_demo_myth_session
from myth_forge_api.providers.capture_store import CaptureStore, CaptureStoreError, CaptureUpload
from myth_forge_api.providers.factory import (
    build_capture_store,
    build_myth_session_store,
    build_npc_director,
    build_npc_tick_runtime,
    build_three_d_provider,
)
from myth_forge_api.providers.image_preparation import (
    ImagePreparationError,
    prepare_provider_source_image,
)
from myth_forge_api.providers.npc import OpenAINPCProviderError
from myth_forge_api.providers.readiness import build_provider_readiness
from myth_forge_api.providers.three_d import MeshyProviderError, ThreeDSourceAsset, ThreeDSourceImage

DEMO_DIR = Path(__file__).parent / "demo"
THREE_D_SOURCE_IMAGE_CONTENT_TYPES = {"image/heic", "image/heif", "image/jpeg", "image/png"}

app = FastAPI(
    title="Personal Myth Forge API",
    version="0.1.0",
    description="Backend contract for the Personal Myth Forge v0.1 prototype.",
)
app.mount("/demo/static", StaticFiles(directory=DEMO_DIR), name="demo-static")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/v1/provider-readiness", response_model=ProviderReadinessResponse)
def provider_readiness() -> ProviderReadinessResponse:
    return build_provider_readiness(load_settings())


@app.get("/demo", include_in_schema=False)
def demo() -> FileResponse:
    return FileResponse(DEMO_DIR / "index.html")


@app.post("/v1/object-captures", response_model=ObjectCapture)
async def create_object_capture(
    metadata_json: str = Form(...),
    files: list[UploadFile] = File(...),
) -> ObjectCapture:
    try:
        metadata = ObjectCaptureMetadata.model_validate(json.loads(metadata_json))
        uploads = [
            CaptureUpload(
                filename=file.filename or "capture",
                content_type=file.content_type or "application/octet-stream",
                data=await file.read(),
            )
            for file in files
        ]
        return build_capture_store().save_capture(metadata=metadata, files=uploads)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=422, detail="metadata_json must be valid JSON.") from exc
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail="metadata_json failed validation.") from exc
    except CaptureStoreError as exc:
        raise HTTPException(status_code=exc.status_code, detail=_safe_provider_error(exc)) from exc


@app.get("/v1/object-captures/{capture_id}", response_model=ObjectCapture)
def get_object_capture(
    capture_id: str = PathParam(..., pattern=CAPTURE_ID_PATTERN),
) -> ObjectCapture:
    capture = build_capture_store().get_capture(capture_id)
    if capture is None:
        raise HTTPException(status_code=404, detail="Object capture not found.")
    return capture


@app.get("/v1/myth-sessions/{session_id}", response_model=MythSession)
def get_myth_session(session_id: str = PathParam(..., pattern=SESSION_ID_PATTERN)) -> MythSession:
    session = build_myth_session_store().get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Myth session not found.")
    return session


@app.get("/v1/myth-sessions/{session_id}/history", response_model=MythSessionHistory)
def get_myth_session_history(
    session_id: str = PathParam(..., pattern=SESSION_ID_PATTERN),
) -> MythSessionHistory:
    history = build_myth_session_store().get_history(session_id)
    if history is None:
        raise HTTPException(status_code=404, detail="Myth session not found.")
    return history


@app.post("/v1/myth-sessions/from-capture", response_model=MythSession)
def create_myth_session_from_capture(request: MythSessionFromCaptureRequest) -> MythSession:
    capture_store = build_capture_store()
    capture = capture_store.get_capture(request.capture_id)
    if capture is None:
        raise HTTPException(status_code=404, detail="Object capture not found.")
    observation = capture.object_observation.model_copy(
        update={
            "capture_id": capture.capture_id,
            "media_refs": [item.uri for item in capture.media_items],
        }
    )
    try:
        source_images, source_assets = _capture_generation_sources(capture, capture_store)
        session = create_demo_myth_session(
            object_observation=observation,
            context_capsule=request.context_capsule,
            three_d_provider=build_three_d_provider(),
            npc_director=build_npc_director(),
            source_images=source_images,
            source_assets=source_assets,
        )
        build_myth_session_store().save_session(session)
        return session
    except CaptureStoreError as exc:
        raise HTTPException(status_code=exc.status_code, detail=_safe_provider_error(exc)) from exc
    except ImagePreparationError as exc:
        raise HTTPException(status_code=422, detail=_safe_provider_error(exc)) from exc
    except (MeshyProviderError, OpenAINPCProviderError, ValueError) as exc:
        raise HTTPException(status_code=502, detail=_safe_provider_error(exc)) from exc


@app.post("/v1/myth-sessions", response_model=MythSession)
def create_myth_session(request: MythSessionRequest) -> MythSession:
    try:
        session = create_demo_myth_session(
            object_observation=request.object_observation,
            context_capsule=request.context_capsule,
            three_d_provider=build_three_d_provider(),
            npc_director=build_npc_director(),
        )
        build_myth_session_store().save_session(session)
        return session
    except (MeshyProviderError, OpenAINPCProviderError, ValueError) as exc:
        raise HTTPException(status_code=502, detail=_safe_provider_error(exc)) from exc


@app.post("/v1/npc-ticks", response_model=NPCAgentTick)
def create_npc_tick(request: NPCAgentTickRequest) -> NPCAgentTick:
    try:
        tick = build_npc_tick_runtime().generate_tick(request)
        build_myth_session_store().append_tick(request.session, tick)
        return tick
    except OpenAINPCProviderError as exc:
        raise HTTPException(status_code=502, detail=_safe_provider_error(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=_safe_provider_error(exc)) from exc


@app.post("/v1/myth-sessions/{session_id}/npc-ticks", response_model=MythSessionHistory)
def advance_myth_session_npc_tick(
    session_id: str = PathParam(..., pattern=SESSION_ID_PATTERN),
) -> MythSessionHistory:
    store = build_myth_session_store()
    history = store.get_history(session_id)
    if history is None:
        raise HTTPException(status_code=404, detail="Myth session not found.")
    try:
        request = NPCAgentTickRequest(
            session=history.session,
            tick_index=_next_history_tick_index(history),
            recent_events=_history_recent_events(history),
        )
        tick = build_npc_tick_runtime().generate_tick(request)
        return store.append_tick(history.session, tick)
    except OpenAINPCProviderError as exc:
        raise HTTPException(status_code=502, detail=_safe_provider_error(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=_safe_provider_error(exc)) from exc


@app.post("/v1/myth-sessions/{session_id}/autonomy-runs", response_model=NPCAutonomyRun)
def run_myth_session_autonomy(
    request: NPCAutonomyRunRequest,
    session_id: str = PathParam(..., pattern=SESSION_ID_PATTERN),
) -> NPCAutonomyRun:
    store = build_myth_session_store()
    history = store.get_history(session_id)
    if history is None:
        raise HTTPException(status_code=404, detail="Myth session not found.")
    try:
        return _run_bounded_autonomy(store, history, request.step_count)
    except OpenAINPCProviderError as exc:
        raise HTTPException(status_code=502, detail=_safe_provider_error(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=_safe_provider_error(exc)) from exc


def _run_bounded_autonomy(
    store,
    history: MythSessionHistory,
    step_count: int,
) -> NPCAutonomyRun:
    started_tick_index = _next_history_tick_index(history)
    current_history = history
    completed_ticks: list[NPCAgentTick] = []
    runtime = build_npc_tick_runtime()
    for _ in range(step_count):
        request = NPCAgentTickRequest(
            session=current_history.session,
            tick_index=_next_history_tick_index(current_history),
            recent_events=_history_recent_events(current_history),
        )
        tick = runtime.generate_tick(request)
        current_history = store.append_tick(current_history.session, tick)
        completed_ticks.append(tick)

    return NPCAutonomyRun(
        session_id=history.session_id,
        requested_steps=step_count,
        completed_steps=len(completed_ticks),
        started_tick_index=started_tick_index,
        completed_tick_index=completed_ticks[-1].tick_index,
        agent_runtime=completed_ticks[-1].agent_runtime,
        history=current_history,
    )


def _next_history_tick_index(history: MythSessionHistory) -> int:
    if not history.npc_ticks:
        return 1
    return max(tick.tick_index for tick in history.npc_ticks) + 1


def _history_recent_events(history: MythSessionHistory) -> list[str]:
    if history.npc_ticks:
        return history.npc_ticks[-1].world_resolution.visible_changes
    return history.session.world_resolution.visible_changes


def _capture_generation_sources(
    capture: ObjectCapture,
    capture_store: CaptureStore,
) -> tuple[tuple[ThreeDSourceImage, ...], tuple[ThreeDSourceAsset, ...]]:
    source_images: list[ThreeDSourceImage] = []
    source_assets: list[ThreeDSourceAsset] = []
    for item in capture.media_items:
        if (
            item.role == "reference_image"
            and item.content_type in THREE_D_SOURCE_IMAGE_CONTENT_TYPES
        ):
            payload = capture_store.read_media(capture.capture_id, item.media_id)
            prepared = prepare_provider_source_image(payload.content_type, payload.data)
            source_images.append(
                ThreeDSourceImage(
                    uri=payload.uri,
                    content_type=prepared.content_type,
                    data_uri=_media_data_uri(prepared.content_type, prepared.data),
                )
            )
        elif item.role == "scan_asset":
            source_assets.append(
                ThreeDSourceAsset(
                    uri=item.uri,
                    content_type=item.content_type,
                )
            )
    return tuple(source_images), tuple(source_assets)


def _media_data_uri(content_type: str, data: bytes) -> str:
    encoded = b64encode(data).decode("ascii")
    return f"data:{content_type};base64,{encoded}"


def _safe_provider_error(exc: Exception) -> str:
    message = str(exc)
    replacements = [
        r"data:[A-Za-z0-9.+-]+/[A-Za-z0-9.+-]+;base64,[A-Za-z0-9+/=_-]+",
        r"local-capture://[^\s,;\"']+",
        r"(?:/[A-Za-z0-9._-]+){2,}/[^\s,;\"']+",
        r"Authorization\s*[=:]\s*Bearer\s+[A-Za-z0-9._:-]+",
        r"Bearer\s+[A-Za-z0-9._:-]+",
        r"raw=[^\s,;]+",
        r"api[_-]?key\s*[=:]\s*[^\s,;]+",
    ]
    for pattern in replacements:
        message = re.sub(pattern, "[redacted]", message, flags=re.IGNORECASE)
    return message
