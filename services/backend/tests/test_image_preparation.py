from io import BytesIO

import pytest
from PIL import Image
from pillow_heif import register_heif_opener

from myth_forge_api.providers.image_preparation import (
    ImagePreparationError,
    prepare_provider_source_image,
)


def test_prepare_provider_source_image_passes_jpeg_through() -> None:
    prepared = prepare_provider_source_image("image/jpeg", b"fake-jpeg")

    assert prepared.content_type == "image/jpeg"
    assert prepared.data == b"fake-jpeg"


def test_prepare_provider_source_image_passes_png_through() -> None:
    prepared = prepare_provider_source_image("image/png", b"fake-png")

    assert prepared.content_type == "image/png"
    assert prepared.data == b"fake-png"


def test_prepare_provider_source_image_converts_heif_to_jpeg() -> None:
    heif_bytes = _tiny_heif_bytes()

    prepared = prepare_provider_source_image("image/heif", heif_bytes)

    assert prepared.content_type == "image/jpeg"
    assert prepared.data.startswith(b"\xff\xd8")
    with Image.open(BytesIO(prepared.data)) as image:
        assert image.format == "JPEG"
        assert image.mode == "RGB"
        assert image.size == (2, 2)


def test_prepare_provider_source_image_raises_sanitized_error_for_invalid_heic() -> None:
    with pytest.raises(ImagePreparationError) as exc_info:
        prepare_provider_source_image("image/heic", b"not-a-heic")

    message = str(exc_info.value)
    assert "Could not prepare image/heic capture media for 3D generation." in message
    assert "not-a-heic" not in message


def _tiny_heif_bytes() -> bytes:
    register_heif_opener(thumbnails=False)
    image = Image.new("RGB", (2, 2), color=(120, 40, 200))
    buffer = BytesIO()
    image.save(buffer, format="HEIF", quality=80)
    return buffer.getvalue()
