from __future__ import annotations

import re
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from myth_forge_api.domain.models import MythSession, MythSessionRequest
from myth_forge_api.domain.pipeline import create_demo_myth_session
from myth_forge_api.providers.factory import build_npc_director, build_three_d_provider
from myth_forge_api.providers.npc import OpenAINPCProviderError
from myth_forge_api.providers.three_d import MeshyProviderError

DEMO_DIR = Path(__file__).parent / "demo"

app = FastAPI(
    title="Personal Myth Forge API",
    version="0.1.0",
    description="Backend contract for the Personal Myth Forge v0.1 prototype.",
)
app.mount("/demo/static", StaticFiles(directory=DEMO_DIR), name="demo-static")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/demo", include_in_schema=False)
def demo() -> FileResponse:
    return FileResponse(DEMO_DIR / "index.html")


@app.post("/v1/myth-sessions", response_model=MythSession)
def create_myth_session(request: MythSessionRequest) -> MythSession:
    try:
        return create_demo_myth_session(
            object_observation=request.object_observation,
            context_capsule=request.context_capsule,
            three_d_provider=build_three_d_provider(),
            npc_director=build_npc_director(),
        )
    except (MeshyProviderError, OpenAINPCProviderError, ValueError) as exc:
        raise HTTPException(status_code=502, detail=_safe_provider_error(exc)) from exc


def _safe_provider_error(exc: Exception) -> str:
    message = str(exc)
    replacements = [
        r"Authorization\s*[=:]\s*Bearer\s+[A-Za-z0-9._:-]+",
        r"Bearer\s+[A-Za-z0-9._:-]+",
        r"raw=[^\s,;]+",
        r"api[_-]?key\s*[=:]\s*[^\s,;]+",
    ]
    for pattern in replacements:
        message = re.sub(pattern, "[redacted]", message, flags=re.IGNORECASE)
    return message
