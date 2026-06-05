import json

import pytest

from myth_forge_api.domain.models import ObjectCaptureMetadata
from myth_forge_api.providers.capture_store import (
    CaptureContentTypeError,
    CaptureFileTooLargeError,
    CaptureUpload,
    LocalCaptureStore,
    TooManyCaptureFilesError,
)


def _metadata() -> ObjectCaptureMetadata:
    return ObjectCaptureMetadata(
        label="old brass key",
        materials=["metal", "brass"],
        source="phone_capture",
        capture_mode="single_photo",
        visual_notes="worn teeth",
    )


def test_local_capture_store_writes_generated_names_and_manifest(tmp_path) -> None:
    store = LocalCaptureStore(root_dir=tmp_path, max_file_bytes=1024)

    capture = store.save_capture(
        metadata=_metadata(),
        files=[
            CaptureUpload(
                filename="../../secret.jpg",
                content_type="image/jpeg",
                data=b"fake",
            )
        ],
    )

    manifest_path = tmp_path / capture.capture_id / "manifest.json"
    saved_media = tmp_path / capture.capture_id / "media_0.jpg"

    assert capture.capture_id.startswith("cap_")
    assert capture.media_items[0].uri.startswith(f"local-capture://{capture.capture_id}/")
    assert saved_media.read_bytes() == b"fake"
    assert manifest_path.exists()
    assert "../../secret" not in json.dumps(json.loads(manifest_path.read_text()))
    assert store.get_capture(capture.capture_id) == capture


def test_local_capture_store_rejects_too_many_files(tmp_path) -> None:
    store = LocalCaptureStore(root_dir=tmp_path, max_files=1)

    with pytest.raises(TooManyCaptureFilesError):
        store.save_capture(
            metadata=_metadata(),
            files=[
                CaptureUpload(filename="a.jpg", content_type="image/jpeg", data=b"a"),
                CaptureUpload(filename="b.jpg", content_type="image/jpeg", data=b"b"),
            ],
        )


def test_local_capture_store_rejects_oversized_file(tmp_path) -> None:
    store = LocalCaptureStore(root_dir=tmp_path, max_file_bytes=2)

    with pytest.raises(CaptureFileTooLargeError):
        store.save_capture(
            metadata=_metadata(),
            files=[CaptureUpload(filename="a.jpg", content_type="image/jpeg", data=b"abc")],
        )


def test_local_capture_store_rejects_unsupported_content_type(tmp_path) -> None:
    store = LocalCaptureStore(root_dir=tmp_path)

    with pytest.raises(CaptureContentTypeError):
        store.save_capture(
            metadata=_metadata(),
            files=[CaptureUpload(filename="a.txt", content_type="text/plain", data=b"abc")],
        )


def test_local_capture_store_rejects_path_traversal_capture_id(tmp_path) -> None:
    store = LocalCaptureStore(root_dir=tmp_path / "captures")
    store.root_dir.mkdir()
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

    assert store.get_capture("..") is None
