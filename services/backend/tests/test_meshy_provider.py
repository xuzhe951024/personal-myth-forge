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
                "model_urls": {
                    "glb": "https://assets.example/refined.glb",
                    "usdz": "https://assets.example/refined.usdz",
                },
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
    assert len(asset.variants) == 2
    assert asset.variants[0].role == "game_asset"
    assert asset.variants[0].uri == "https://assets.example/refined.glb"
    assert asset.variants[1].role == "ios_scene_asset"
    assert asset.variants[1].format == "usdz"
    assert asset.variants[1].uri == "https://assets.example/refined.usdz"
    assert asset.variants[1].is_scene_loadable is True
    assert [request.method for request in requests] == ["POST", "GET", "POST", "GET"]
    assert preview_payload["mode"] == "preview"
    assert preview_payload["target_formats"] == ["glb", "usdz"]
    assert preview_payload["moderation"] is True
    assert refine_payload["mode"] == "refine"
    assert refine_payload["preview_task_id"] == "preview-123"
    assert refine_payload["target_formats"] == ["glb", "usdz"]
    assert asset.generation_provenance is not None
    assert asset.generation_provenance.input_mode == "text_prompt"
    assert asset.generation_provenance.provider_route == "/openapi/v2/text-to-3d"
    assert asset.generation_provenance.source_image_count == 0
    assert asset.generation_provenance.selected_source_image_count == 0
    assert asset.generation_provenance.source_asset_count == 0
    assert asset.generation_provenance.raw_sources_included is False


def test_meshy_provider_uses_image_to_3d_when_source_image_exists() -> None:
    requests: list[httpx.Request] = []
    responses = [
        httpx.Response(200, json={"result": "image-task-789"}),
        httpx.Response(
            200,
            json={
                "id": "image-task-789",
                "status": "SUCCEEDED",
                "model_urls": {
                    "glb": "https://assets.example/image.glb",
                    "usdz": "https://assets.example/image.usdz",
                },
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
    assert [variant.format for variant in asset.variants] == ["glb", "usdz"]
    assert asset.variants[1].role == "ios_scene_asset"
    assert asset.variants[1].uri == "https://assets.example/image.usdz"
    assert [request.method for request in requests] == ["POST", "GET"]
    assert [request.url.path for request in requests] == [
        "/openapi/v1/image-to-3d",
        "/openapi/v1/image-to-3d/image-task-789",
    ]
    assert image_payload["image_url"] == data_uri
    assert image_payload["target_formats"] == ["glb", "usdz"]
    assert image_payload["enable_pbr"] is True
    assert image_payload["should_remesh"] is True
    assert image_payload["should_texture"] is True
    assert "mode" not in image_payload
    assert asset.generation_provenance is not None
    assert asset.generation_provenance.input_mode == "single_image"
    assert asset.generation_provenance.provider_route == "/openapi/v1/image-to-3d"
    assert asset.generation_provenance.source_image_count == 1
    assert asset.generation_provenance.selected_source_image_count == 1
    assert asset.generation_provenance.raw_sources_included is False


def test_meshy_provider_uses_multi_image_to_3d_for_guided_scan_images() -> None:
    requests: list[httpx.Request] = []
    responses = [
        httpx.Response(200, json={"result": "multi-image-task-123"}),
        httpx.Response(
            200,
            json={
                "id": "multi-image-task-123",
                "status": "SUCCEEDED",
                "model_urls": {
                    "glb": "https://assets.example/multi.glb",
                    "usdz": "https://assets.example/multi.usdz",
                },
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

    asset = provider.generate_game_asset(
        _request(
            source_images=(
                _source_image("front", "image/jpeg"),
                _source_image("side", "image/png"),
            )
        )
    )

    multi_payload = json.loads(requests[0].content)
    assert asset.provider == "meshy"
    assert asset.uri == "https://assets.example/multi.glb"
    assert [variant.format for variant in asset.variants] == ["glb", "usdz"]
    assert asset.variants[1].role == "ios_scene_asset"
    assert [request.method for request in requests] == ["POST", "GET"]
    assert [request.url.path for request in requests] == [
        "/openapi/v1/multi-image-to-3d",
        "/openapi/v1/multi-image-to-3d/multi-image-task-123",
    ]
    assert multi_payload["image_urls"] == [
        "data:image/jpeg;base64,front",
        "data:image/png;base64,side",
    ]
    assert multi_payload["target_formats"] == ["glb", "usdz"]
    assert multi_payload["enable_pbr"] is True
    assert multi_payload["should_texture"] is True
    assert "image_url" not in multi_payload
    assert asset.generation_provenance is not None
    assert asset.generation_provenance.input_mode == "multi_image"
    assert asset.generation_provenance.provider_route == "/openapi/v1/multi-image-to-3d"
    assert asset.generation_provenance.source_image_count == 2
    assert asset.generation_provenance.selected_source_image_count == 2
    assert asset.generation_provenance.max_source_images == 4
    assert asset.generation_provenance.raw_sources_included is False


def test_meshy_provider_limits_multi_image_input_to_first_four_supported_images() -> None:
    requests: list[httpx.Request] = []
    responses = [
        httpx.Response(200, json={"result": "multi-image-task-123"}),
        httpx.Response(
            200,
            json={
                "id": "multi-image-task-123",
                "status": "SUCCEEDED",
                "model_urls": {"glb": "https://assets.example/multi.glb"},
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

    asset = provider.generate_game_asset(
        _request(
            source_images=tuple(_source_image(f"angle-{index}", "image/jpeg") for index in range(5))
        )
    )

    multi_payload = json.loads(requests[0].content)
    assert [request.url.path for request in requests] == [
        "/openapi/v1/multi-image-to-3d",
        "/openapi/v1/multi-image-to-3d/multi-image-task-123",
    ]
    assert multi_payload["image_urls"] == [
        "data:image/jpeg;base64,angle-0",
        "data:image/jpeg;base64,angle-1",
        "data:image/jpeg;base64,angle-2",
        "data:image/jpeg;base64,angle-3",
    ]
    assert asset.generation_provenance is not None
    assert asset.generation_provenance.input_mode == "multi_image"
    assert asset.generation_provenance.source_image_count == 5
    assert asset.generation_provenance.selected_source_image_count == 4
    assert asset.generation_provenance.max_source_images == 4


def test_meshy_provider_filters_unsupported_images_before_multi_image_routing() -> None:
    requests: list[httpx.Request] = []
    responses = [
        httpx.Response(200, json={"result": "multi-image-task-123"}),
        httpx.Response(
            200,
            json={
                "id": "multi-image-task-123",
                "status": "SUCCEEDED",
                "model_urls": {"glb": "https://assets.example/multi.glb"},
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

    provider.generate_game_asset(
        _request(
            source_images=(
                _source_image("raw-heic", "image/heic"),
                _source_image("front", "image/jpeg"),
                _source_image("side", "image/png"),
            )
        )
    )

    multi_payload = json.loads(requests[0].content)
    assert [request.url.path for request in requests] == [
        "/openapi/v1/multi-image-to-3d",
        "/openapi/v1/multi-image-to-3d/multi-image-task-123",
    ]
    assert multi_payload["image_urls"] == [
        "data:image/jpeg;base64,front",
        "data:image/png;base64,side",
    ]


def test_meshy_provider_uses_supported_image_when_guided_scan_includes_heic() -> None:
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

    provider.generate_game_asset(
        _request(
            source_images=(
                ThreeDSourceImage(
                    uri="local-capture://cap_0123456789abcdef/media_0.heic",
                    content_type="image/heic",
                    data_uri="data:image/heic;base64,ZmFrZQ==",
                ),
                ThreeDSourceImage(
                    uri="local-capture://cap_0123456789abcdef/media_1.png",
                    content_type="image/png",
                    data_uri="data:image/png;base64,cG5n",
                ),
            )
        )
    )

    image_payload = json.loads(requests[0].content)
    assert [request.url.path for request in requests] == [
        "/openapi/v1/image-to-3d",
        "/openapi/v1/image-to-3d/image-task-789",
    ]
    assert image_payload["image_url"] == "data:image/png;base64,cG5n"


def test_meshy_provider_uses_image_to_3d_for_prepared_heic_source_image() -> None:
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

    asset = provider.generate_game_asset(
        _request(
            source_images=(
                ThreeDSourceImage(
                    uri="local-capture://cap_0123456789abcdef/media_0.heic",
                    content_type="image/jpeg",
                    data_uri="data:image/jpeg;base64,dHJhbnNjb2RlZA==",
                ),
            )
        )
    )

    image_payload = json.loads(requests[0].content)
    assert asset.uri == "https://assets.example/image.glb"
    assert [request.method for request in requests] == ["POST", "GET"]
    assert [request.url.path for request in requests] == [
        "/openapi/v1/image-to-3d",
        "/openapi/v1/image-to-3d/image-task-789",
    ]
    assert image_payload["image_url"] == "data:image/jpeg;base64,dHJhbnNjb2RlZA=="
    assert image_payload["target_formats"] == ["glb", "usdz"]


def test_meshy_provider_keeps_glb_only_asset_when_usdz_is_missing() -> None:
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

    assert asset.uri == "https://assets.example/refined.glb"
    assert [variant.format for variant in asset.variants] == ["glb"]
    assert asset.variants[0].is_scene_loadable is False


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


def _source_image(name: str, content_type: str) -> ThreeDSourceImage:
    extension = content_type.split("/")[-1]
    return ThreeDSourceImage(
        uri=f"local-capture://cap_0123456789abcdef/{name}.{extension}",
        content_type=content_type,
        data_uri=f"data:{content_type};base64,{name}",
    )
