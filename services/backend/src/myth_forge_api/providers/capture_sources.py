from __future__ import annotations

from base64 import b64encode

from myth_forge_api.domain.models import ObjectCapture
from myth_forge_api.providers.capture_store import CaptureStore
from myth_forge_api.providers.image_preparation import prepare_provider_source_image
from myth_forge_api.providers.three_d import ThreeDSourceAsset, ThreeDSourceImage

THREE_D_SOURCE_IMAGE_CONTENT_TYPES = {"image/heic", "image/heif", "image/jpeg", "image/png"}


def build_capture_generation_sources(
    capture: ObjectCapture,
    capture_store: CaptureStore,
) -> tuple[tuple[ThreeDSourceImage, ...], tuple[ThreeDSourceAsset, ...]]:
    source_images: list[ThreeDSourceImage] = []
    source_assets: list[ThreeDSourceAsset] = []
    for item in capture.media_items:
        if item.role == "reference_image" and item.content_type in THREE_D_SOURCE_IMAGE_CONTENT_TYPES:
            payload = capture_store.read_media(capture.capture_id, item.media_id)
            prepared = prepare_provider_source_image(payload.content_type, payload.data)
            source_images.append(
                ThreeDSourceImage(
                    uri=payload.uri,
                    content_type=prepared.content_type,
                    data_uri=_media_data_uri(prepared.content_type, prepared.data),
                )
            )
        elif item.role == "scan_asset":
            source_assets.append(
                ThreeDSourceAsset(
                    uri=item.uri,
                    content_type=item.content_type,
                )
            )
    return tuple(source_images), tuple(source_assets)


def _media_data_uri(content_type: str, data: bytes) -> str:
    encoded = b64encode(data).decode("ascii")
    return f"data:{content_type};base64,{encoded}"
