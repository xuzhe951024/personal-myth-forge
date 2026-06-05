from myth_forge_api.domain.models import (
    CaptureMediaItem,
    ObjectCapture,
    ObjectCaptureMetadata,
    ObjectObservation,
)


def test_object_capture_manifest_serializes_without_bytes_or_local_paths() -> None:
    capture = ObjectCapture(
        capture_id="cap_test",
        status="ready",
        source="phone_capture",
        capture_mode="single_photo",
        object_observation=ObjectObservation(
            label="old brass key",
            materials=["metal", "brass"],
            source="phone_capture",
            visual_notes="worn teeth",
        ),
        media_items=[
            CaptureMediaItem(
                media_id="media_0",
                role="reference_image",
                content_type="image/jpeg",
                byte_size=4,
                uri="local-capture://cap_test/media_0.jpg",
                moderation_status="needs_review",
            )
        ],
        created_at="2026-06-05T00:00:00Z",
    )

    payload = capture.model_dump(mode="json")

    assert payload["capture_id"] == "cap_test"
    assert payload["media_items"][0]["uri"] == "local-capture://cap_test/media_0.jpg"
    assert "bytes" not in str(payload).lower()
    assert "/Users/" not in str(payload)


def test_capture_metadata_creates_object_observation() -> None:
    metadata = ObjectCaptureMetadata(
        label="ceramic cup",
        materials=["ceramic"],
        source="manual_upload",
        capture_mode="single_photo",
        visual_notes="blue glaze",
    )

    observation = metadata.to_object_observation()

    assert observation.label == "ceramic cup"
    assert observation.materials == ["ceramic"]
    assert observation.source == "manual_upload"
    assert observation.visual_notes == "blue glaze"
