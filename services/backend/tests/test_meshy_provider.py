import json

import httpx
import pytest

from myth_forge_api.providers.three_d import (
    MeshyConfigurationError,
    MeshyProviderError,
    MeshyTaskTimeoutError,
    MeshyThreeDProvider,
    ThreeDGenerationRequest,
    ThreeDSourceImage,
)


def test_meshy_provider_creates_preview_refines_and_returns_glb() -> None:
    requests: list[httpx.Request] = []
    responses = [
        httpx.Response(200, json={"result": "preview-123"}),
        httpx.Response(
            200,
            json={
                "id": "preview-123",
                "status": "SUCCEEDED",
                "model_urls": {"glb": "https://assets.example/preview.glb"},
            },
        ),
        httpx.Response(200, json={"result": "refine-456"}),
        httpx.Response(
            200,
            json={
                "id": "refine-456",
                "status": "SUCCEEDED",
                "model_urls": {"glb": "https://assets.example/refined.glb"},
            },
        ),
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return responses.pop(0)

    client = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://api.meshy.test",
    )
    provider = MeshyThreeDProvider(
        api_key="test-key",
        client=client,
        poll_interval_seconds=0,
        max_wait_seconds=1,
    )

    asset = provider.generate_game_asset(_request())

    preview_payload = json.loads(requests[0].content)
    refine_payload = json.loads(requests[2].content)
    assert asset.provider == "meshy"
    assert asset.uri == "https://assets.example/refined.glb"
    assert [request.method for request in requests] == ["POST", "GET", "POST", "GET"]
    assert preview_payload["mode"] == "preview"
    assert preview_payload["target_formats"] == ["glb"]
    assert preview_payload["moderation"] is True
    assert refine_payload["mode"] == "refine"
    assert refine_payload["preview_task_id"] == "preview-123"


def test_meshy_provider_uses_image_to_3d_when_source_image_exists() -> None:
    requests: list[httpx.Request] = []
    responses = [
        httpx.Response(200, json={"result": "image-task-789"}),
        httpx.Response(
            200,
            json={
                "id": "image-task-789",
                "status": "SUCCEEDED",
                "model_urls": {"glb": "https://assets.example/image.glb"},
            },
        ),
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return responses.pop(0)

    client = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://api.meshy.test",
    )
    provider = MeshyThreeDProvider(
        api_key="test-key",
        client=client,
        poll_interval_seconds=0,
        max_wait_seconds=1,
    )
    data_uri = "data:image/jpeg;base64,ZmFrZQ=="

    asset = provider.generate_game_asset(
        _request(
            source_images=(
                ThreeDSourceImage(
                    uri="local-capture://cap_0123456789abcdef/media_0.jpg",
                    content_type="image/jpeg",
                    data_uri=data_uri,
                ),
            )
        )
    )

    image_payload = json.loads(requests[0].content)
    assert asset.provider == "meshy"
    assert asset.uri == "https://assets.example/image.glb"
    assert asset.prompt == "Create a shrine key."
    assert [request.method for request in requests] == ["POST", "GET"]
    assert [request.url.path for request in requests] == [
        "/openapi/v1/image-to-3d",
        "/openapi/v1/image-to-3d/image-task-789",
    ]
    assert image_payload["image_url"] == data_uri
    assert image_payload["target_formats"] == ["glb"]
    assert image_payload["enable_pbr"] is True
    assert image_payload["should_remesh"] is True
    assert image_payload["should_texture"] is True
    assert "mode" not in image_payload


def test_meshy_provider_requires_api_key() -> None:
    provider = MeshyThreeDProvider(api_key="")

    with pytest.raises(MeshyConfigurationError):
        provider.generate_game_asset(_request())


def test_meshy_provider_raises_for_failed_task() -> None:
    responses = [
        httpx.Response(200, json={"result": "preview-123"}),
        httpx.Response(
            200,
            json={
                "id": "preview-123",
                "status": "FAILED",
                "task_error": {"message": "content moderation rejected prompt"},
            },
        ),
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        return responses.pop(0)

    client = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://api.meshy.test",
    )
    provider = MeshyThreeDProvider(
        api_key="test-key",
        client=client,
        poll_interval_seconds=0,
        max_wait_seconds=1,
    )

    with pytest.raises(MeshyProviderError, match="content moderation rejected prompt"):
        provider.generate_game_asset(_request())


def test_meshy_provider_times_out_when_task_never_finishes() -> None:
    responses = [
        httpx.Response(200, json={"result": "preview-123"}),
        httpx.Response(200, json={"id": "preview-123", "status": "IN_PROGRESS", "progress": 50}),
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        if responses:
            return responses.pop(0)
        return httpx.Response(
            200,
            json={"id": "preview-123", "status": "IN_PROGRESS", "progress": 50},
        )

    client = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://api.meshy.test",
    )
    provider = MeshyThreeDProvider(
        api_key="test-key",
        client=client,
        poll_interval_seconds=0,
        max_wait_seconds=0,
    )

    with pytest.raises(MeshyTaskTimeoutError):
        provider.generate_game_asset(_request())


def _request(
    source_images: tuple[ThreeDSourceImage, ...] = (),
) -> ThreeDGenerationRequest:
    return ThreeDGenerationRequest(
        session_id="myth_test",
        prompt="Create a shrine key.",
        source_images=source_images,
    )
