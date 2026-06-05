from __future__ import annotations

import time
from typing import Protocol

import httpx

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
    _text_to_3d_path = "/openapi/v2/text-to-3d"

    def __init__(
        self,
        api_key: str | None,
        api_base_url: str = "https://api.meshy.ai",
        client: httpx.Client | None = None,
        poll_interval_seconds: float = 5.0,
        max_wait_seconds: float = 600.0,
    ) -> None:
        self.api_key = api_key
        self.api_base_url = api_base_url
        self.client = client or httpx.Client(base_url=api_base_url, timeout=30)
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
        preview_task_id = self._create_task(
            {
                "mode": "preview",
                "prompt": prompt[:600],
                "target_formats": ["glb"],
                "moderation": True,
            }
        )
        self._poll_task(preview_task_id)
        refine_task_id = self._create_task(
            {
                "mode": "refine",
                "preview_task_id": preview_task_id,
                "target_formats": ["glb"],
                "moderation": True,
            }
        )
        refined_task = self._poll_task(refine_task_id)
        glb_uri = refined_task.get("model_urls", {}).get("glb")
        if not glb_uri:
            raise MeshyProviderError("Meshy task succeeded but did not return a GLB URL.")

        return GeneratedAsset(
            kind="game_asset",
            provider=self.provider_name,
            format="glb",
            uri=glb_uri,
            prompt=prompt,
            moderation_status="needs_review",
        )

    def _create_task(self, payload: dict[str, object]) -> str:
        response = self.client.post(
            self._text_to_3d_path,
            headers=self._headers(),
            json=payload,
        )
        data = self._response_json(response)
        task_id = data.get("result")
        if not isinstance(task_id, str) or not task_id:
            raise MeshyProviderError("Meshy create task response did not include a task id.")
        return task_id

    def _poll_task(self, task_id: str) -> dict[str, object]:
        deadline = time.monotonic() + self.max_wait_seconds

        while True:
            response = self.client.get(
                f"{self._text_to_3d_path}/{task_id}",
                headers=self._headers(),
            )
            data = self._response_json(response)
            status = data.get("status")
            if status == "SUCCEEDED":
                return data
            if status in {"FAILED", "EXPIRED", "CANCELED"}:
                message = _task_error_message(data)
                raise MeshyProviderError(f"Meshy task {task_id} ended with {status}: {message}")
            if time.monotonic() >= deadline:
                raise MeshyTaskTimeoutError(f"Timed out waiting for Meshy task {task_id}.")
            if self.poll_interval_seconds > 0:
                time.sleep(self.poll_interval_seconds)

    def _headers(self) -> dict[str, str]:
        if not self.api_key:
            raise MeshyConfigurationError("MESHY_API_KEY is required for Meshy generation.")
        return {"Authorization": f"Bearer {self.api_key}"}

    @staticmethod
    def _response_json(response: httpx.Response) -> dict[str, object]:
        try:
            data = response.json()
        except ValueError:
            data = {}
        if response.is_error:
            message = _provider_error_message(data) or response.text
            raise MeshyProviderError(f"Meshy API {response.status_code}: {message}")
        if not isinstance(data, dict):
            raise MeshyProviderError("Meshy response was not a JSON object.")
        return data


class MeshyProviderError(RuntimeError):
    pass


class MeshyConfigurationError(MeshyProviderError):
    pass


class MeshyTaskTimeoutError(MeshyProviderError):
    pass


def _provider_error_message(data: dict[str, object]) -> str | None:
    for key in ("message", "error"):
        value = data.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _task_error_message(data: dict[str, object]) -> str:
    task_error = data.get("task_error")
    if isinstance(task_error, dict):
        message = task_error.get("message")
        if isinstance(message, str) and message:
            return message
    return "no provider message"
