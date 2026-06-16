from __future__ import annotations

import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from fastapi import FastAPI

from myth_forge_api.config import Settings
from myth_forge_api.providers.capture_store import CaptureStore
from myth_forge_api.providers.factory import (
    build_capture_store as build_configured_capture_store,
    build_myth_session_store as build_configured_myth_session_store,
    build_npc_director as build_configured_npc_director,
    build_npc_tick_runtime as build_configured_npc_tick_runtime,
    build_print_provider as build_configured_print_provider,
    build_three_d_provider as build_configured_three_d_provider,
)


@contextmanager
def local_acceptance_app(
    *,
    capture_store: CaptureStore | None = None,
) -> Iterator[FastAPI]:
    import myth_forge_api.main as api_main

    with tempfile.TemporaryDirectory(prefix="pmf-local-acceptance-app-") as temp_dir:
        root_dir = Path(temp_dir)
        settings = Settings(
            three_d_provider="local",
            npc_provider="local",
            print_provider="local",
            capture_storage_dir=str(root_dir / "captures"),
            myth_session_storage_dir=str(root_dir / "myth-sessions"),
        )
        originals = {
            "build_three_d_provider": api_main.build_three_d_provider,
            "build_npc_director": api_main.build_npc_director,
            "build_npc_tick_runtime": api_main.build_npc_tick_runtime,
            "build_print_provider": api_main.build_print_provider,
            "build_capture_store": api_main.build_capture_store,
            "build_myth_session_store": api_main.build_myth_session_store,
        }
        try:
            api_main.build_three_d_provider = lambda: build_configured_three_d_provider(
                settings
            )
            api_main.build_npc_director = lambda: build_configured_npc_director(settings)
            api_main.build_npc_tick_runtime = (
                lambda: build_configured_npc_tick_runtime(settings)
            )
            api_main.build_print_provider = lambda: build_configured_print_provider(
                settings
            )
            api_main.build_capture_store = (
                lambda: capture_store
                if capture_store is not None
                else build_configured_capture_store(settings)
            )
            api_main.build_myth_session_store = lambda: (
                build_configured_myth_session_store(settings)
            )
            yield api_main.app
        finally:
            for name, original in originals.items():
                setattr(api_main, name, original)
