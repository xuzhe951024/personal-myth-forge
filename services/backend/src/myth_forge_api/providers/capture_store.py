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


class CaptureStore(Protocol):
    def save_capture(
        self,
        metadata: ObjectCaptureMetadata,
        files: list[CaptureUpload],
    ) -> ObjectCapture:
        ...

    def get_capture(self, capture_id: str) -> ObjectCapture | None:
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
        self._validate_files(files)
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

    def _validate_files(self, files: list[CaptureUpload]) -> None:
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
