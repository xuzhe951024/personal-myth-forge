from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Protocol

import httpx

from myth_forge_api.domain.models import GeneratedAsset, GeneratedAssetVariant

MESHY_GAME_ASSET_TARGET_FORMATS = ["glb", "usdz"]
MESHY_IMAGE_TO_3D_CONTENT_TYPES = {"image/jpeg", "image/png"}


@dataclass(frozen=True)
class ThreeDSourceImage:
    uri: str
    content_type: str
    data_uri: str


@dataclass(frozen=True)
class ThreeDSourceAsset:
    uri: str
    content_type: str


@dataclass(frozen=True)
class ThreeDGenerationRequest:
    session_id: str
    prompt: str
    source_images: tuple[ThreeDSourceImage, ...] = ()
    source_assets: tuple[ThreeDSourceAsset, ...] = ()


class ThreeDProvider(Protocol):
    provider_name: str

    def generate_game_asset(self, request: ThreeDGenerationRequest) -> GeneratedAsset:
        ...


class LocalThreeDProvider:
    """Deterministic stand-in for Meshy, Tripo, Rodin, or a self-hosted 3D model."""

    provider_name = "local_stub"

    def generate_game_asset(self, request: ThreeDGenerationRequest) -> GeneratedAsset:
        glb_uri = f"local://generated-assets/{request.session_id}.glb"
        usdz_uri = f"local://generated-assets/{request.session_id}.usdz"
        return GeneratedAsset(
            kind="game_asset",
            provider=self.provider_name,
            format="glb",
            uri=glb_uri,
            prompt=_prompt_with_source_summary(request),
            moderation_status="needs_review",
            variants=[
                GeneratedAssetVariant(
                    role="game_asset",
                    format="glb",
                    uri=glb_uri,
                    is_scene_loadable=False,
                ),
                GeneratedAssetVariant(
                    role="ios_scene_asset",
                    format="usdz",
                    uri=usdz_uri,
                    is_scene_loadable=True,
                ),
            ],
        )


class MeshyThreeDProvider:
    provider_name = "meshy"
    _text_to_3d_path = "/openapi/v2/text-to-3d"
    _image_to_3d_path = "/openapi/v1/image-to-3d"

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

    def generate_game_asset(self, request: ThreeDGenerationRequest) -> GeneratedAsset:
        supported_source_image = _first_meshy_supported_source_image(request.source_images)
        if supported_source_image:
            return self._generate_image_asset(request, supported_source_image)
        return self._generate_text_asset(request)

    def _generate_text_asset(self, request: ThreeDGenerationRequest) -> GeneratedAsset:
        preview_task_id = self._create_task(
            self._text_to_3d_path,
            {
                "mode": "preview",
                "prompt": request.prompt[:600],
                "target_formats": MESHY_GAME_ASSET_TARGET_FORMATS,
                "moderation": True,
            }
        )
        self._poll_task(self._text_to_3d_path, preview_task_id)
        refine_task_id = self._create_task(
            self._text_to_3d_path,
            {
                "mode": "refine",
                "preview_task_id": preview_task_id,
                "target_formats": MESHY_GAME_ASSET_TARGET_FORMATS,
                "moderation": True,
            }
        )
        refined_task = self._poll_task(self._text_to_3d_path, refine_task_id)
        return self._asset_from_task(request=request, task=refined_task)

    def _generate_image_asset(
        self,
        request: ThreeDGenerationRequest,
        source_image: ThreeDSourceImage,
    ) -> GeneratedAsset:
        task_id = self._create_task(
            self._image_to_3d_path,
            {
                "image_url": source_image.data_uri,
                "enable_pbr": True,
                "should_remesh": True,
                "target_formats": MESHY_GAME_ASSET_TARGET_FORMATS,
                "should_texture": True,
            },
        )
        task = self._poll_task(self._image_to_3d_path, task_id)
        return self._asset_from_task(request=request, task=task)

    def _asset_from_task(
        self,
        request: ThreeDGenerationRequest,
        task: dict[str, object],
    ) -> GeneratedAsset:
        glb_uri = task.get("model_urls", {}).get("glb")
        if not glb_uri:
            raise MeshyProviderError("Meshy task succeeded but did not return a GLB URL.")
        usdz_uri = task.get("model_urls", {}).get("usdz")
        variants = [
            GeneratedAssetVariant(
                role="game_asset",
                format="glb",
                uri=str(glb_uri),
                is_scene_loadable=False,
            )
        ]
        if usdz_uri:
            variants.append(
                GeneratedAssetVariant(
                    role="ios_scene_asset",
                    format="usdz",
                    uri=str(usdz_uri),
                    is_scene_loadable=True,
                )
            )
        return GeneratedAsset(
            kind="game_asset",
            provider=self.provider_name,
            format="glb",
            uri=str(glb_uri),
            prompt=request.prompt,
            moderation_status="needs_review",
            variants=variants,
        )

    def _create_task(self, path: str, payload: dict[str, object]) -> str:
        response = self.client.post(
            path,
            headers=self._headers(),
            json=payload,
        )
        data = self._response_json(response)
        task_id = data.get("result")
        if not isinstance(task_id, str) or not task_id:
            raise MeshyProviderError("Meshy create task response did not include a task id.")
        return task_id

    def _poll_task(self, path: str, task_id: str) -> dict[str, object]:
        deadline = time.monotonic() + self.max_wait_seconds

        while True:
            response = self.client.get(
                f"{path}/{task_id}",
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


def _prompt_with_source_summary(request: ThreeDGenerationRequest) -> str:
    if not request.source_images and not request.source_assets:
        return request.prompt
    return (
        f"{request.prompt}\n\n"
        f"Provider input summary: source_images={len(request.source_images)}; "
        f"source_assets={len(request.source_assets)}."
    )


def _first_meshy_supported_source_image(
    source_images: tuple[ThreeDSourceImage, ...],
) -> ThreeDSourceImage | None:
    for source_image in source_images:
        if source_image.content_type.lower() in MESHY_IMAGE_TO_3D_CONTENT_TYPES:
            return source_image
    return None


def _task_error_message(data: dict[str, object]) -> str:
    task_error = data.get("task_error")
    if isinstance(task_error, dict):
        message = task_error.get("message")
        if isinstance(message, str) and message:
            return message
    return "no provider message"
