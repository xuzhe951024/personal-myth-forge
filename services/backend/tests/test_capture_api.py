import json

from fastapi.testclient import TestClient

from myth_forge_api.main import app
from myth_forge_api.providers.capture_store import LocalCaptureStore


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
