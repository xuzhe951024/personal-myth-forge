import json
from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image
from pillow_heif import register_heif_opener

from myth_forge_api.domain.models import GeneratedAsset
from myth_forge_api.main import app
from myth_forge_api.providers.capture_store import LocalCaptureStore
from myth_forge_api.providers.three_d import MeshyProviderError, ThreeDGenerationRequest


class RecordingThreeDProvider:
    provider_name = "recording"

    def __init__(self) -> None:
        self.calls: list[ThreeDGenerationRequest] = []

    def generate_game_asset(self, request: ThreeDGenerationRequest) -> GeneratedAsset:
        self.calls.append(request)
        return GeneratedAsset(
            kind="game_asset",
            provider=self.provider_name,
            format="glb",
            uri=f"recording://{request.session_id}.glb",
            prompt=request.prompt,
            moderation_status="needs_review",
        )


class LeakingThreeDProvider:
    provider_name = "leaking"

    def generate_game_asset(self, request: ThreeDGenerationRequest) -> GeneratedAsset:
        raise MeshyProviderError(
            "provider echoed image_url=data:image/jpeg;base64,ZmFrZS1qcGVn "
            "path=/tmp/personal-myth-forge/captures/cap_0123456789abcdef/media_1.jpg "
            "ref=local-capture://cap_0123456789abcdef/media_1.jpg "
            "Authorization=Bearer test-secret raw=test-secret"
        )


def _client_with_store(tmp_path, monkeypatch) -> TestClient:
    store = LocalCaptureStore(root_dir=tmp_path)
    monkeypatch.setattr("myth_forge_api.main.build_capture_store", lambda: store)
    return TestClient(app)


def _metadata_json() -> str:
    return json.dumps(
        {
            "label": "old brass key",
            "materials": ["metal", "brass"],
            "source": "phone_capture",
            "capture_mode": "single_photo",
            "visual_notes": "worn teeth",
        }
    )


def _guided_scan_metadata_json() -> str:
    return json.dumps(
        {
            "label": "carved wooden fox",
            "materials": ["wood"],
            "source": "phone_capture",
            "capture_mode": "guided_scan",
            "visual_notes": "captured from many angles",
        }
    )


def test_upload_object_capture_returns_manifest(tmp_path, monkeypatch) -> None:
    client = _client_with_store(tmp_path, monkeypatch)

    response = client.post(
        "/v1/object-captures",
        data={"metadata_json": _metadata_json()},
        files={"files": ("key.jpg", b"fake-jpeg", "image/jpeg")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["capture_id"].startswith("cap_")
    assert payload["object_observation"]["label"] == "old brass key"
    assert payload["media_items"][0]["uri"].startswith("local-capture://")
    assert "fake-jpeg" not in response.text
    assert str(tmp_path) not in response.text


def test_upload_object_capture_accepts_guided_scan_images(tmp_path, monkeypatch) -> None:
    client = _client_with_store(tmp_path, monkeypatch)

    response = client.post(
        "/v1/object-captures",
        data={"metadata_json": _guided_scan_metadata_json()},
        files=[
            ("files", ("fox-front.jpg", b"front-jpeg", "image/jpeg")),
            ("files", ("fox-side.png", b"side-png", "image/png")),
        ],
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["capture_mode"] == "guided_scan"
    assert [item["role"] for item in payload["media_items"]] == [
        "reference_image",
        "reference_image",
    ]
    assert [item["content_type"] for item in payload["media_items"]] == [
        "image/jpeg",
        "image/png",
    ]
    assert "front-jpeg" not in response.text
    assert "side-png" not in response.text
    assert str(tmp_path) not in response.text


def test_upload_object_capture_rejects_guided_scan_with_too_few_images(
    tmp_path,
    monkeypatch,
) -> None:
    client = _client_with_store(tmp_path, monkeypatch)

    response = client.post(
        "/v1/object-captures",
        data={"metadata_json": _guided_scan_metadata_json()},
        files=[("files", ("fox-front.jpg", b"front-jpeg", "image/jpeg"))],
    )

    assert response.status_code == 422
    assert "front-jpeg" not in response.text


def test_upload_object_capture_rejects_guided_scan_with_scan_asset(
    tmp_path,
    monkeypatch,
) -> None:
    client = _client_with_store(tmp_path, monkeypatch)

    response = client.post(
        "/v1/object-captures",
        data={"metadata_json": _guided_scan_metadata_json()},
        files=[
            ("files", ("fox-front.jpg", b"front-jpeg", "image/jpeg")),
            ("files", ("fox.glb", b"fake-glb", "model/gltf-binary")),
        ],
    )

    assert response.status_code == 422
    assert "front-jpeg" not in response.text
    assert "fake-glb" not in response.text


def test_get_object_capture_returns_manifest(tmp_path, monkeypatch) -> None:
    client = _client_with_store(tmp_path, monkeypatch)
    created = client.post(
        "/v1/object-captures",
        data={"metadata_json": _metadata_json()},
        files={"files": ("key.jpg", b"fake-jpeg", "image/jpeg")},
    ).json()

    response = client.get(f"/v1/object-captures/{created['capture_id']}")

    assert response.status_code == 200
    assert response.json()["capture_id"] == created["capture_id"]


def test_get_object_capture_returns_404_for_missing_capture(tmp_path, monkeypatch) -> None:
    client = _client_with_store(tmp_path, monkeypatch)

    response = client.get("/v1/object-captures/cap_0000000000000000")

    assert response.status_code == 404


def test_get_object_capture_rejects_path_traversal_id(tmp_path, monkeypatch) -> None:
    client = _client_with_store(tmp_path / "captures", monkeypatch)
    (tmp_path / "captures").mkdir()
    escaped_manifest = tmp_path / "manifest.json"
    escaped_manifest.write_text(
        json.dumps(
            {
                "capture_id": "cap_0000000000000000",
                "status": "ready",
                "source": "phone_capture",
                "capture_mode": "single_photo",
                "object_observation": {
                    "label": "escaped manifest",
                    "materials": [],
                    "source": "phone_capture",
                },
                "media_items": [],
                "created_at": "2026-06-05T00:00:00+00:00",
            }
        ),
        encoding="utf-8",
    )

    response = client.get("/v1/object-captures/%2E%2E")

    assert response.status_code == 422
    assert "escaped manifest" not in response.text


def test_upload_object_capture_rejects_unsupported_content_type(tmp_path, monkeypatch) -> None:
    client = _client_with_store(tmp_path, monkeypatch)

    response = client.post(
        "/v1/object-captures",
        data={"metadata_json": _metadata_json()},
        files={"files": ("key.txt", b"not-media", "text/plain")},
    )

    assert response.status_code == 415


def test_upload_object_capture_rejects_invalid_metadata_shape(tmp_path, monkeypatch) -> None:
    client = _client_with_store(tmp_path, monkeypatch)

    response = client.post(
        "/v1/object-captures",
        data={"metadata_json": json.dumps({})},
        files={"files": ("key.jpg", b"fake-jpeg", "image/jpeg")},
    )

    assert response.status_code == 422
    assert "Internal Server Error" not in response.text


def test_upload_object_capture_rejects_too_many_files(tmp_path, monkeypatch) -> None:
    store = LocalCaptureStore(root_dir=tmp_path, max_files=1)
    monkeypatch.setattr("myth_forge_api.main.build_capture_store", lambda: store)
    client = TestClient(app)

    response = client.post(
        "/v1/object-captures",
        data={"metadata_json": _metadata_json()},
        files=[
            ("files", ("a.jpg", b"a", "image/jpeg")),
            ("files", ("b.jpg", b"b", "image/jpeg")),
        ],
    )

    assert response.status_code == 413


def test_upload_object_capture_rejects_oversized_file(tmp_path, monkeypatch) -> None:
    store = LocalCaptureStore(root_dir=tmp_path, max_file_bytes=2)
    monkeypatch.setattr("myth_forge_api.main.build_capture_store", lambda: store)
    client = TestClient(app)

    response = client.post(
        "/v1/object-captures",
        data={"metadata_json": _metadata_json()},
        files={"files": ("key.jpg", b"abc", "image/jpeg")},
    )

    assert response.status_code == 413


def test_create_myth_session_from_capture(tmp_path, monkeypatch) -> None:
    client = _client_with_store(tmp_path, monkeypatch)
    created = client.post(
        "/v1/object-captures",
        data={"metadata_json": _metadata_json()},
        files={"files": ("key.jpg", b"fake-jpeg", "image/jpeg")},
    ).json()

    response = client.post(
        "/v1/myth-sessions/from-capture",
        json={
            "capture_id": created["capture_id"],
            "context_capsule": {
                "current_theme": "deadline pressure",
                "desired_tone": "tender and strange",
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready_for_review"
    assert payload["object_card"]["label"] == "old brass key"
    assert created["capture_id"] in payload["object_card"]["symbolic_reading"]


def test_create_myth_session_from_arkit_scan_capture_includes_media_refs(
    tmp_path,
    monkeypatch,
) -> None:
    client = _client_with_store(tmp_path, monkeypatch)
    metadata = json.dumps(
        {
            "label": "small idol",
            "materials": ["stone"],
            "source": "phone_capture",
            "capture_mode": "arkit_scan",
            "visual_notes": "rough scan bundle",
        }
    )
    created = client.post(
        "/v1/object-captures",
        data={"metadata_json": metadata},
        files=[
            ("files", ("idol.glb", b"fake-glb", "model/gltf-binary")),
            ("files", ("reference.jpg", b"fake-jpeg", "image/jpeg")),
        ],
    ).json()

    response = client.post(
        "/v1/myth-sessions/from-capture",
        json={
            "capture_id": created["capture_id"],
            "context_capsule": {
                "current_theme": "deadline pressure",
                "desired_tone": "tender and strange",
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready_for_review"
    assert payload["object_card"]["label"] == "small idol"
    assert payload["object_card"]["source"] == "phone_capture"
    assert "media_refs: 2" in payload["object_card"]["symbolic_reading"]
    assert "capture_id:" in payload["object_card"]["symbolic_reading"]
    assert "local-capture://" not in response.text


def test_create_myth_session_from_capture_passes_media_sources_to_3d_provider(
    tmp_path,
    monkeypatch,
) -> None:
    store = LocalCaptureStore(root_dir=tmp_path)
    provider = RecordingThreeDProvider()
    monkeypatch.setattr("myth_forge_api.main.build_capture_store", lambda: store)
    monkeypatch.setattr("myth_forge_api.main.build_three_d_provider", lambda: provider)
    client = TestClient(app)
    metadata = json.dumps(
        {
            "label": "small idol",
            "materials": ["stone"],
            "source": "phone_capture",
            "capture_mode": "arkit_scan",
            "visual_notes": "rough scan bundle",
        }
    )
    created = client.post(
        "/v1/object-captures",
        data={"metadata_json": metadata},
        files=[
            ("files", ("idol.glb", b"fake-glb", "model/gltf-binary")),
            ("files", ("reference.jpg", b"fake-jpeg", "image/jpeg")),
        ],
    ).json()

    response = client.post(
        "/v1/myth-sessions/from-capture",
        json={
            "capture_id": created["capture_id"],
            "context_capsule": {
                "current_theme": "deadline pressure",
                "desired_tone": "tender and strange",
            },
        },
    )

    assert response.status_code == 200
    assert len(provider.calls) == 1
    generation_request = provider.calls[0]
    assert len(generation_request.source_images) == 1
    assert len(generation_request.source_assets) == 1
    assert generation_request.source_images[0].uri == (
        f"local-capture://{created['capture_id']}/media_1.jpg"
    )
    assert generation_request.source_images[0].content_type == "image/jpeg"
    assert generation_request.source_images[0].data_uri.startswith(
        "data:image/jpeg;base64,"
    )
    assert "ZmFrZS1qcGVn" in generation_request.source_images[0].data_uri
    assert generation_request.source_assets[0].uri == (
        f"local-capture://{created['capture_id']}/media_0.glb"
    )
    assert generation_request.source_assets[0].content_type == "model/gltf-binary"
    assert "data:image" not in response.text
    assert "ZmFrZS1qcGVn" not in response.text
    assert "fake-jpeg" not in response.text
    assert "fake-glb" not in response.text


def test_create_myth_session_from_guided_scan_capture_passes_images_to_3d_provider(
    tmp_path,
    monkeypatch,
) -> None:
    store = LocalCaptureStore(root_dir=tmp_path)
    provider = RecordingThreeDProvider()
    monkeypatch.setattr("myth_forge_api.main.build_capture_store", lambda: store)
    monkeypatch.setattr("myth_forge_api.main.build_three_d_provider", lambda: provider)
    client = TestClient(app)

    created_response = client.post(
        "/v1/object-captures",
        data={"metadata_json": _guided_scan_metadata_json()},
        files=[
            ("files", ("fox-front.jpg", b"front-jpeg", "image/jpeg")),
            ("files", ("fox-side.png", b"side-png", "image/png")),
        ],
    )

    assert created_response.status_code == 200
    created = created_response.json()
    response = client.post(
        "/v1/myth-sessions/from-capture",
        json={
            "capture_id": created["capture_id"],
            "context_capsule": {
                "current_theme": "deadline pressure",
                "desired_tone": "tender and strange",
            },
        },
    )

    assert response.status_code == 200
    assert len(provider.calls) == 1
    generation_request = provider.calls[0]
    assert len(generation_request.source_images) == 2
    assert len(generation_request.source_assets) == 0
    assert [image.uri for image in generation_request.source_images] == [
        f"local-capture://{created['capture_id']}/media_0.jpg",
        f"local-capture://{created['capture_id']}/media_1.png",
    ]
    assert [image.content_type for image in generation_request.source_images] == [
        "image/jpeg",
        "image/png",
    ]
    assert all(
        image.data_uri.startswith(f"data:{image.content_type};base64,")
        for image in generation_request.source_images
    )
    assert "data:image" not in response.text
    assert "front-jpeg" not in response.text
    assert "side-png" not in response.text
    assert str(tmp_path) not in response.text


def test_create_myth_session_from_guided_scan_capture_passes_heic_images_to_3d_provider(
    tmp_path,
    monkeypatch,
) -> None:
    store = LocalCaptureStore(root_dir=tmp_path)
    provider = RecordingThreeDProvider()
    monkeypatch.setattr("myth_forge_api.main.build_capture_store", lambda: store)
    monkeypatch.setattr("myth_forge_api.main.build_three_d_provider", lambda: provider)
    client = TestClient(app)

    created_response = client.post(
        "/v1/object-captures",
        data={"metadata_json": _guided_scan_metadata_json()},
        files=[
            ("files", ("fox-front.heic", _tiny_heif_bytes(), "image/heic")),
            ("files", ("fox-side.heif", _tiny_heif_bytes(), "image/heif")),
        ],
    )

    assert created_response.status_code == 200
    created = created_response.json()
    response = client.post(
        "/v1/myth-sessions/from-capture",
        json={
            "capture_id": created["capture_id"],
            "context_capsule": {
                "current_theme": "deadline pressure",
                "desired_tone": "tender and strange",
            },
        },
    )

    assert response.status_code == 200
    assert len(provider.calls) == 1
    generation_request = provider.calls[0]
    assert len(generation_request.source_images) == 2
    assert len(generation_request.source_assets) == 0
    assert [image.uri for image in generation_request.source_images] == [
        f"local-capture://{created['capture_id']}/media_0.heic",
        f"local-capture://{created['capture_id']}/media_1.heif",
    ]
    assert [image.content_type for image in generation_request.source_images] == [
        "image/jpeg",
        "image/jpeg",
    ]
    assert all(
        image.data_uri.startswith("data:image/jpeg;base64,")
        for image in generation_request.source_images
    )
    assert "front-heic" not in response.text
    assert "side-heif" not in response.text


def test_create_myth_session_from_capture_redacts_image_preparation_error(
    tmp_path,
    monkeypatch,
) -> None:
    store = LocalCaptureStore(root_dir=tmp_path)
    monkeypatch.setattr("myth_forge_api.main.build_capture_store", lambda: store)
    client = TestClient(app)

    created_response = client.post(
        "/v1/object-captures",
        data={"metadata_json": _guided_scan_metadata_json()},
        files=[
            ("files", ("fox-front.heic", b"front-heic", "image/heic")),
            ("files", ("fox-side.heif", b"side-heif", "image/heif")),
        ],
    )

    assert created_response.status_code == 200
    created = created_response.json()
    response = client.post(
        "/v1/myth-sessions/from-capture",
        json={
            "capture_id": created["capture_id"],
            "context_capsule": {
                "current_theme": "deadline pressure",
                "desired_tone": "tender and strange",
            },
        },
    )

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert "Could not prepare image/heic capture media for 3D generation." in detail
    assert "front-heic" not in response.text
    assert "side-heif" not in response.text
    assert str(tmp_path) not in response.text


def test_create_myth_session_from_capture_redacts_provider_error_media_details(
    tmp_path,
    monkeypatch,
) -> None:
    store = LocalCaptureStore(root_dir=tmp_path)
    monkeypatch.setattr("myth_forge_api.main.build_capture_store", lambda: store)
    monkeypatch.setattr("myth_forge_api.main.build_three_d_provider", lambda: LeakingThreeDProvider())
    client = TestClient(app)
    created = client.post(
        "/v1/object-captures",
        data={"metadata_json": _metadata_json()},
        files={"files": ("key.jpg", b"fake-jpeg", "image/jpeg")},
    ).json()

    response = client.post(
        "/v1/myth-sessions/from-capture",
        json={
            "capture_id": created["capture_id"],
            "context_capsule": {
                "current_theme": "deadline pressure",
                "desired_tone": "tender and strange",
            },
        },
    )

    assert response.status_code == 502
    detail = response.json()["detail"]
    assert "[redacted]" in detail
    assert "data:image" not in detail
    assert "ZmFrZS1qcGVn" not in detail
    assert "/tmp/personal-myth-forge" not in detail
    assert "local-capture://" not in detail
    assert "test-secret" not in detail
    assert "Authorization" not in detail
    assert "raw=" not in detail


def test_create_myth_session_from_capture_preserves_capture_store_error_status(
    tmp_path,
    monkeypatch,
) -> None:
    client = _client_with_store(tmp_path, monkeypatch)
    created = client.post(
        "/v1/object-captures",
        data={"metadata_json": _metadata_json()},
        files={"files": ("key.jpg", b"fake-jpeg", "image/jpeg")},
    ).json()
    (tmp_path / created["capture_id"] / "media_0.jpg").unlink()

    response = client.post(
        "/v1/myth-sessions/from-capture",
        json={
            "capture_id": created["capture_id"],
            "context_capsule": {
                "current_theme": "deadline pressure",
                "desired_tone": "tender and strange",
            },
        },
    )

    assert response.status_code == 404
    assert "fake-jpeg" not in response.text
    assert str(tmp_path) not in response.text


def _tiny_heif_bytes() -> bytes:
    register_heif_opener(thumbnails=False)
    image = Image.new("RGB", (2, 2), color=(180, 80, 40))
    buffer = BytesIO()
    image.save(buffer, format="HEIF", quality=80)
    return buffer.getvalue()


def test_create_myth_session_from_capture_returns_404_for_missing_capture(
    tmp_path,
    monkeypatch,
) -> None:
    client = _client_with_store(tmp_path, monkeypatch)

    response = client.post(
        "/v1/myth-sessions/from-capture",
        json={
            "capture_id": "cap_0000000000000000",
            "context_capsule": {
                "current_theme": "deadline pressure",
                "desired_tone": "tender and strange",
            },
        },
    )

    assert response.status_code == 404


def test_create_myth_session_from_capture_rejects_path_traversal_id(
    tmp_path,
    monkeypatch,
) -> None:
    client = _client_with_store(tmp_path / "captures", monkeypatch)
    (tmp_path / "captures").mkdir()
    escaped_manifest = tmp_path / "manifest.json"
    escaped_manifest.write_text(
        json.dumps(
            {
                "capture_id": "cap_0000000000000000",
                "status": "ready",
                "source": "phone_capture",
                "capture_mode": "single_photo",
                "object_observation": {
                    "label": "escaped manifest",
                    "materials": [],
                    "source": "phone_capture",
                },
                "media_items": [],
                "created_at": "2026-06-05T00:00:00+00:00",
            }
        ),
        encoding="utf-8",
    )

    response = client.post(
        "/v1/myth-sessions/from-capture",
        json={
            "capture_id": "..",
            "context_capsule": {
                "current_theme": "deadline pressure",
                "desired_tone": "tender and strange",
            },
        },
    )

    assert response.status_code == 422
    assert "escaped manifest" not in response.text
