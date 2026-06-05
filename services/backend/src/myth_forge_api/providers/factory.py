from __future__ import annotations

from myth_forge_api.config import Settings, load_settings
from myth_forge_api.providers.npc import LocalNPCDirector, NPCDirector, OpenAINPCDirector
from myth_forge_api.providers.three_d import LocalThreeDProvider, MeshyThreeDProvider, ThreeDProvider


def build_three_d_provider(settings: Settings | None = None) -> ThreeDProvider:
    selected_settings = settings or load_settings()
    if selected_settings.three_d_provider == "local":
        return LocalThreeDProvider()
    if selected_settings.three_d_provider == "meshy":
        return MeshyThreeDProvider.from_settings(selected_settings)
    raise ValueError(f"Unsupported THREE_D_PROVIDER: {selected_settings.three_d_provider}")


def build_npc_director(settings: Settings | None = None) -> NPCDirector:
    selected_settings = settings or load_settings()
    if selected_settings.npc_provider == "local":
        return LocalNPCDirector()
    if selected_settings.npc_provider == "openai":
        return OpenAINPCDirector.from_settings(selected_settings)
    raise ValueError(f"Unsupported NPC_PROVIDER: {selected_settings.npc_provider}")
