from __future__ import annotations

from myth_forge_api.domain.models import GeneratedAsset


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

