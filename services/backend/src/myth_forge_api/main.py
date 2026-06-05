from __future__ import annotations

from fastapi import FastAPI

from myth_forge_api.domain.models import MythSession, MythSessionRequest
from myth_forge_api.domain.pipeline import create_demo_myth_session

app = FastAPI(
    title="Personal Myth Forge API",
    version="0.1.0",
    description="Backend contract for the Personal Myth Forge v0.1 prototype.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/myth-sessions", response_model=MythSession)
def create_myth_session(request: MythSessionRequest) -> MythSession:
    return create_demo_myth_session(
        object_observation=request.object_observation,
        context_capsule=request.context_capsule,
    )

