from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from dotenv import load_dotenv

DEFAULT_CAPTURE_STORAGE_DIR = str(Path(__file__).resolve().parents[2] / ".local" / "captures")
DEFAULT_MYTH_SESSION_STORAGE_DIR = str(
    Path(__file__).resolve().parents[2] / ".local" / "myth-sessions"
)


@dataclass(frozen=True)
class Settings:
    three_d_provider: str = "local"
    meshy_api_key: str | None = None
    meshy_api_base_url: str = "https://api.meshy.ai"
    meshy_poll_interval_seconds: float = 5.0
    meshy_max_wait_seconds: float = 600.0
    npc_provider: str = "local"
    openai_api_key: str | None = None
    openai_npc_model: str = "gpt-4.1-mini"
    openai_api_base_url: str | None = None
    capture_storage_dir: str = DEFAULT_CAPTURE_STORAGE_DIR
    myth_session_storage_dir: str = DEFAULT_MYTH_SESSION_STORAGE_DIR


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    load_dotenv()
    source = env or os.environ
    return Settings(
        three_d_provider=source.get("THREE_D_PROVIDER", "local").strip().lower(),
        meshy_api_key=source.get("MESHY_API_KEY") or None,
        meshy_api_base_url=source.get("MESHY_API_BASE_URL", "https://api.meshy.ai"),
        meshy_poll_interval_seconds=float(source.get("MESHY_POLL_INTERVAL_SECONDS", "5")),
        meshy_max_wait_seconds=float(source.get("MESHY_MAX_WAIT_SECONDS", "600")),
        npc_provider=source.get("NPC_PROVIDER", "local").strip().lower(),
        openai_api_key=source.get("OPENAI_API_KEY") or None,
        openai_npc_model=source.get("OPENAI_NPC_MODEL", "gpt-4.1-mini"),
        openai_api_base_url=source.get("OPENAI_API_BASE_URL") or None,
        capture_storage_dir=source.get("CAPTURE_STORAGE_DIR") or DEFAULT_CAPTURE_STORAGE_DIR,
        myth_session_storage_dir=source.get("MYTH_SESSION_STORAGE_DIR")
        or DEFAULT_MYTH_SESSION_STORAGE_DIR,
    )
