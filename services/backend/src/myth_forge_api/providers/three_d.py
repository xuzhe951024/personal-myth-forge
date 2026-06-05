from __future__ import annotations

from typing import Protocol

from myth_forge_api.domain.models import GeneratedAsset


class ThreeDProvider(Protocol):
    provider_name: str

    def generate_game_asset(self, session_id: str, prompt: str) -> GeneratedAsset:
        ...


class LocalThreeDProvider:
    """Deterministic stand-in for Meshy, Tripo, Rodin, or a self-hosted 3D model."""

    provider_name = "local_stub"

    def generate_game_asset(self, session_id: str, prompt: str) -> GeneratedAsset:
        return GeneratedAsset(
            kind="game_asset",
            provider=self.provider_name,
            format="glb",
            uri=f"local://generated-assets/{session_id}.glb",
            prompt=prompt,
            moderation_status="needs_review",
        )


class MeshyThreeDProvider:
    provider_name = "meshy"

    def __init__(
        self,
        api_key: str | None,
        api_base_url: str = "https://api.meshy.ai",
        poll_interval_seconds: float = 5.0,
        max_wait_seconds: float = 600.0,
    ) -> None:
        self.api_key = api_key
        self.api_base_url = api_base_url
        self.poll_interval_seconds = poll_interval_seconds
        self.max_wait_seconds = max_wait_seconds

    @classmethod
    def from_settings(cls, settings: object) -> "MeshyThreeDProvider":
        return cls(
            api_key=getattr(settings, "meshy_api_key"),
            api_base_url=getattr(settings, "meshy_api_base_url"),
            poll_interval_seconds=getattr(settings, "meshy_poll_interval_seconds"),
            max_wait_seconds=getattr(settings, "meshy_max_wait_seconds"),
        )

    def generate_game_asset(self, session_id: str, prompt: str) -> GeneratedAsset:
        raise NotImplementedError(
            f"{self.provider_name} generation is implemented in the Meshy provider task."
        )
