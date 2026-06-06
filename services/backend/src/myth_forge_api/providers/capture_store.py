from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol
from uuid import uuid4

from myth_forge_api.domain.models import (
    CAPTURE_ID_PATTERN,
    CaptureMediaItem,
    ObjectCapture,
    ObjectCaptureMetadata,
)

ACCEPTED_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/heic": ".heic",
    "image/heif": ".heif",
    "model/gltf-binary": ".glb",
    "model/vnd.usdz+zip": ".usdz",
    "application/octet-stream": ".bin",
}
IMAGE_CONTENT_TYPES = {"image/jpeg", "image/png", "image/heic", "image/heif"}
DEFAULT_MAX_FILES = 12
DEFAULT_MAX_FILE_BYTES = 10 * 1024 * 1024
CAPTURE_ID_RE = re.compile(CAPTURE_ID_PATTERN)


@dataclass(frozen=True)
class CaptureUpload:
    filename: str
    content_type: str
    data: bytes


@dataclass(frozen=True)
class CaptureMediaPayload:
    media_id: str
    uri: str
    content_type: str
    data: bytes


class CaptureStore(Protocol):
    def save_capture(
        self,
        metadata: ObjectCaptureMetadata,
        files: list[CaptureUpload],
    ) -> ObjectCapture:
        ...

    def get_capture(self, capture_id: str) -> ObjectCapture | None:
        ...

    def read_media(self, capture_id: str, media_id: str) -> CaptureMediaPayload:
        ...


class CaptureStoreError(RuntimeError):
    status_code = 400


class EmptyCaptureUploadError(CaptureStoreError):
    status_code = 422


class TooManyCaptureFilesError(CaptureStoreError):
    status_code = 413


class CaptureFileTooLargeError(CaptureStoreError):
    status_code = 413


class CaptureContentTypeError(CaptureStoreError):
    status_code = 415


class CaptureModeMediaError(CaptureStoreError):
    status_code = 422


class CaptureMediaNotFoundError(CaptureStoreError):
    status_code = 404


class LocalCaptureStore:
    def __init__(
        self,
        root_dir: str | Path,
        max_files: int = DEFAULT_MAX_FILES,
        max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
    ) -> None:
        self.root_dir = Path(root_dir)
        self.max_files = max_files
        self.max_file_bytes = max_file_bytes

    def save_capture(
        self,
        metadata: ObjectCaptureMetadata,
        files: list[CaptureUpload],
    ) -> ObjectCapture:
        self._validate_files(metadata, files)
        capture_id = f"cap_{uuid4().hex[:16]}"
        capture_dir = self.root_dir / capture_id
        capture_dir.mkdir(parents=True, exist_ok=False)

        media_items: list[CaptureMediaItem] = []
        for index, upload in enumerate(files):
            media_id = f"media_{index}"
            extension = ACCEPTED_CONTENT_TYPES[upload.content_type]
            filename = f"{media_id}{extension}"
            media_path = capture_dir / filename
            media_path.write_bytes(upload.data)
            role = "reference_image" if upload.content_type in IMAGE_CONTENT_TYPES else "scan_asset"
            media_items.append(
                CaptureMediaItem(
                    media_id=media_id,
                    role=role,
                    content_type=upload.content_type,
                    byte_size=len(upload.data),
                    uri=f"local-capture://{capture_id}/{filename}",
                    moderation_status="needs_review",
                )
            )

        capture = ObjectCapture(
            capture_id=capture_id,
            status="ready",
            source=metadata.source,
            capture_mode=metadata.capture_mode,
            object_observation=metadata.to_object_observation(),
            media_items=media_items,
            created_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        )
        (capture_dir / "manifest.json").write_text(
            json.dumps(capture.model_dump(mode="json"), indent=2),
            encoding="utf-8",
        )
        return capture

    def get_capture(self, capture_id: str) -> ObjectCapture | None:
        if CAPTURE_ID_RE.fullmatch(capture_id) is None:
            return None
        root_dir = self.root_dir.resolve()
        manifest_path = (self.root_dir / capture_id / "manifest.json").resolve()
        try:
            manifest_path.relative_to(root_dir)
        except ValueError:
            return None
        if not manifest_path.exists():
            return None
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        return ObjectCapture.model_validate(data)

    def read_media(self, capture_id: str, media_id: str) -> CaptureMediaPayload:
        capture = self.get_capture(capture_id)
        if capture is None:
            raise CaptureMediaNotFoundError(f"Capture media not found: {capture_id}/{media_id}")

        item = next((item for item in capture.media_items if item.media_id == media_id), None)
        if item is None:
            raise CaptureMediaNotFoundError(f"Capture media not found: {capture_id}/{media_id}")

        uri_prefix = f"local-capture://{capture.capture_id}/"
        if not item.uri.startswith(uri_prefix):
            raise CaptureMediaNotFoundError(f"Capture media not found: {capture_id}/{media_id}")

        filename = item.uri.removeprefix(uri_prefix)
        if not filename or "/" in filename or "\\" in filename:
            raise CaptureMediaNotFoundError(f"Capture media not found: {capture_id}/{media_id}")

        capture_dir = (self.root_dir / capture.capture_id).resolve()
        media_path = (capture_dir / filename).resolve()
        try:
            media_path.relative_to(capture_dir)
        except ValueError as exc:
            raise CaptureMediaNotFoundError(
                f"Capture media not found: {capture_id}/{media_id}"
            ) from exc
        if not media_path.is_file():
            raise CaptureMediaNotFoundError(f"Capture media not found: {capture_id}/{media_id}")

        return CaptureMediaPayload(
            media_id=item.media_id,
            uri=item.uri,
            content_type=item.content_type,
            data=media_path.read_bytes(),
        )

    def _validate_files(self, metadata: ObjectCaptureMetadata, files: list[CaptureUpload]) -> None:
        if not files:
            raise EmptyCaptureUploadError("At least one capture file is required.")
        if len(files) > self.max_files:
            raise TooManyCaptureFilesError(f"At most {self.max_files} capture files are allowed.")
        for upload in files:
            if upload.content_type not in ACCEPTED_CONTENT_TYPES:
                raise CaptureContentTypeError(
                    f"Unsupported capture content type: {upload.content_type}"
                )
            if len(upload.data) > self.max_file_bytes:
                raise CaptureFileTooLargeError(
                    f"Capture file exceeds {self.max_file_bytes} bytes."
                )
        self._validate_mode_media(metadata, files)

    def _validate_mode_media(
        self,
        metadata: ObjectCaptureMetadata,
        files: list[CaptureUpload],
    ) -> None:
        image_count = sum(1 for upload in files if upload.content_type in IMAGE_CONTENT_TYPES)
        scan_asset_count = len(files) - image_count
        capture_mode = metadata.capture_mode

        if capture_mode == "single_photo":
            if len(files) != 1 or image_count != 1:
                raise CaptureModeMediaError("single_photo requires exactly one image file.")
        elif capture_mode in {"photo_set", "guided_scan"}:
            if not (2 <= len(files) <= self.max_files) or image_count != len(files):
                raise CaptureModeMediaError(f"{capture_mode} requires 2-12 image files.")
        elif capture_mode == "arkit_scan":
            if scan_asset_count < 1:
                raise CaptureModeMediaError("arkit_scan requires at least one scan asset.")
