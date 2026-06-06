from __future__ import annotations

from myth_forge_api.config import Settings, load_settings
from myth_forge_api.providers.capture_store import CaptureStore, LocalCaptureStore
from myth_forge_api.providers.npc import LocalNPCDirector, NPCDirector, OpenAINPCDirector
from myth_forge_api.providers.npc_ticks import (
    LocalNPCTickRuntime,
    NPCTickRuntime,
    OpenAINPCTickRuntime,
)
from myth_forge_api.providers.printing import LocalPrintProvider, PrintProvider, TreatstockPrintProvider
from myth_forge_api.providers.session_store import LocalMythSessionStore, MythSessionStore
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


def build_npc_tick_runtime(settings: Settings | None = None) -> NPCTickRuntime:
    selected_settings = settings or load_settings()
    if selected_settings.npc_provider == "local":
        return LocalNPCTickRuntime()
    if selected_settings.npc_provider == "openai":
        return OpenAINPCTickRuntime.from_settings(selected_settings)
    raise ValueError(f"Unsupported NPC_PROVIDER: {selected_settings.npc_provider}")


def build_print_provider(settings: Settings | None = None) -> PrintProvider:
    selected_settings = settings or load_settings()
    if selected_settings.print_provider == "local":
        return LocalPrintProvider()
    if selected_settings.print_provider == "treatstock":
        return TreatstockPrintProvider.from_settings(selected_settings)
    raise ValueError(
        f"PRINT_PROVIDER={selected_settings.print_provider} is not implemented for live quotes."
    )


def build_capture_store(settings: Settings | None = None) -> CaptureStore:
    selected_settings = settings or load_settings()
    return LocalCaptureStore(root_dir=selected_settings.capture_storage_dir)


def build_myth_session_store(settings: Settings | None = None) -> MythSessionStore:
    selected_settings = settings or load_settings()
    return LocalMythSessionStore(root_dir=selected_settings.myth_session_storage_dir)
