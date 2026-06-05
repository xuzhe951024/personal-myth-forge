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
