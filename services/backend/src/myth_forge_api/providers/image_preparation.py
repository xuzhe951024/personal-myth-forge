from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

from PIL import Image, UnidentifiedImageError
from pillow_heif import register_heif_opener

PASSTHROUGH_IMAGE_CONTENT_TYPES = {"image/jpeg", "image/png"}
TRANSCODE_TO_JPEG_CONTENT_TYPES = {"image/heic", "image/heif"}


@dataclass(frozen=True)
class PreparedSourceImage:
    content_type: str
    data: bytes


class ImagePreparationError(RuntimeError):
    pass


def prepare_provider_source_image(content_type: str, data: bytes) -> PreparedSourceImage:
    normalized_content_type = content_type.lower()
    if normalized_content_type in PASSTHROUGH_IMAGE_CONTENT_TYPES:
        return PreparedSourceImage(content_type=normalized_content_type, data=data)
    if normalized_content_type in TRANSCODE_TO_JPEG_CONTENT_TYPES:
        return PreparedSourceImage(
            content_type="image/jpeg",
            data=_transcode_heif_to_jpeg(normalized_content_type, data),
        )
    return PreparedSourceImage(content_type=normalized_content_type, data=data)


def _transcode_heif_to_jpeg(content_type: str, data: bytes) -> bytes:
    register_heif_opener(thumbnails=False)
    try:
        with Image.open(BytesIO(data)) as image:
            rgb_image = image.convert("RGB")
            output = BytesIO()
            rgb_image.save(output, format="JPEG", quality=92, optimize=True)
            return output.getvalue()
    except (OSError, UnidentifiedImageError, ValueError) as exc:
        raise ImagePreparationError(
            f"Could not prepare {content_type} capture media for 3D generation."
        ) from exc
