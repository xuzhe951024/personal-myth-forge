import json

from fastapi.testclient import TestClient

from myth_forge_api.domain.models import GeneratedAsset
from myth_forge_api.main import app
from myth_forge_api.providers.capture_store import LocalCaptureStore
from myth_forge_api.providers.three_d import ThreeDGenerationRequest


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
    assert f"local-capture://{created['capture_id']}/media_0.glb" in payload["object_card"][
        "symbolic_reading"
    ]
    assert f"local-capture://{created['capture_id']}/media_1.jpg" in payload["object_card"][
        "symbolic_reading"
    ]


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
