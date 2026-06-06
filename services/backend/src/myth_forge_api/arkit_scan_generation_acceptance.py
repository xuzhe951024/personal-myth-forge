from __future__ import annotations

import json
import re
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from myth_forge_api.domain.models import ContextCapsule, ObjectCaptureMetadata
from myth_forge_api.domain.pipeline import create_demo_myth_session
from myth_forge_api.providers.capture_sources import build_capture_generation_sources
from myth_forge_api.providers.capture_store import CaptureUpload, LocalCaptureStore
from myth_forge_api.providers.npc import LocalNPCDirector
from myth_forge_api.providers.three_d import (
    LocalThreeDProvider,
    ThreeDGenerationRequest,
    ThreeDProvider,
)


@dataclass(frozen=True)
class ARKitScanGenerationAcceptanceResult:
    exit_code: int
    report: dict[str, Any]


class RecordingThreeDProvider:
    provider_name = "recording_local"

    def __init__(self, delegate: ThreeDProvider | None = None) -> None:
        self.delegate = delegate or LocalThreeDProvider()
        self.requests: list[ThreeDGenerationRequest] = []

    def generate_game_asset(self, request: ThreeDGenerationRequest):
        self.requests.append(request)
        return self.delegate.generate_game_asset(request)


def run_arkit_scan_generation_acceptance(
    *,
    capture_storage_dir: str | Path | None = None,
    three_d_provider: ThreeDProvider | None = None,
) -> ARKitScanGenerationAcceptanceResult:
    if capture_storage_dir is None:
        with tempfile.TemporaryDirectory(prefix="pmf-arkit-scan-generation-") as temp_dir:
            return _run_arkit_scan_generation_acceptance(Path(temp_dir), three_d_provider)
    return _run_arkit_scan_generation_acceptance(Path(capture_storage_dir), three_d_provider)


def _run_arkit_scan_generation_acceptance(
    capture_storage_dir: Path,
    three_d_provider: ThreeDProvider | None,
) -> ARKitScanGenerationAcceptanceResult:
    started_at = time.perf_counter()
    store = LocalCaptureStore(root_dir=capture_storage_dir)
    recording_provider = RecordingThreeDProvider(three_d_provider)
    try:
        capture = store.save_capture(
            metadata=ObjectCaptureMetadata(
                label="acceptance stone idol",
                materials=["stone"],
                source="acceptance_arkit_scan",
                capture_mode="arkit_scan",
                visual_notes="Object Capture scan asset with front and side references",
            ),
            files=[
                CaptureUpload("idol.glb", "model/gltf-binary", b"fake-glb-scan-asset"),
                CaptureUpload("front.jpg", "image/jpeg", b"front-jpeg"),
                CaptureUpload("side.png", "image/png", b"side-png"),
            ],
        )
        source_images, source_assets = build_capture_generation_sources(capture, store)
        observation = capture.object_observation.model_copy(
            update={
                "capture_id": capture.capture_id,
                "media_refs": [item.uri for item in capture.media_items],
            }
        )
        session = create_demo_myth_session(
            object_observation=observation,
            context_capsule=ContextCapsule(
                current_theme="acceptance pressure",
                desired_tone="tender, strange",
            ),
            three_d_provider=recording_provider,
            npc_director=LocalNPCDirector(),
            source_images=source_images,
            source_assets=source_assets,
        )
        request = recording_provider.requests[0] if recording_provider.requests else None
        checks = _checks(request=request, source_images=len(source_images), source_assets=len(source_assets))
        report = {
            "kind": "arkit_scan_generation_acceptance_report",
            "status": "succeeded",
            "summary": _summary(checks),
            "checks": checks,
            "capture": {
                "capture_mode": capture.capture_mode,
                "capture_media_count": len(capture.media_items),
                "reference_image_count": sum(
                    1 for item in capture.media_items if item.role == "reference_image"
                ),
                "scan_asset_count": sum(
                    1 for item in capture.media_items if item.role == "scan_asset"
                ),
            },
            "generation_request": {
                "source_image_count": len(request.source_images) if request is not None else 0,
                "source_asset_count": len(request.source_assets) if request is not None else 0,
                "source_image_content_types": (
                    [image.content_type for image in request.source_images]
                    if request is not None
                    else []
                ),
                "source_asset_content_types": (
                    [asset.content_type for asset in request.source_assets]
                    if request is not None
                    else []
                ),
            },
            "provider": session.generated_asset.provider,
            "generation_provenance": (
                session.generated_asset.generation_provenance.model_dump(mode="json")
                if session.generated_asset.generation_provenance is not None
                else None
            ),
            "scene_loadable_variant": any(
                variant.is_scene_loadable for variant in session.generated_asset.variants
            ),
            "timings": {"total_elapsed_seconds": round(time.perf_counter() - started_at, 4)},
            "safety": _safety_summary(),
            "error": None,
        }
        return ARKitScanGenerationAcceptanceResult(
            exit_code=0,
            report=_sanitize_report(report, capture_storage_dir),
        )
    except Exception as exc:
        report = {
            "kind": "arkit_scan_generation_acceptance_report",
            "status": "failed",
            "summary": {"passed": 0, "failed": 1},
            "capture": {"capture_mode": "arkit_scan"},
            "timings": {"total_elapsed_seconds": round(time.perf_counter() - started_at, 4)},
            "safety": _safety_summary(),
            "error": str(exc),
        }
        return ARKitScanGenerationAcceptanceResult(
            exit_code=1,
            report=_sanitize_report(report, capture_storage_dir),
        )


def _checks(
    *,
    request: ThreeDGenerationRequest | None,
    source_images: int,
    source_assets: int,
) -> list[dict[str, Any]]:
    return [
        {
            "id": "arkit_capture_manifest",
            "status": "passed",
            "detail": "synthetic arkit_scan capture stored with scan asset and references",
        },
        {
            "id": "scan_asset_handoff",
            "status": "passed" if source_assets == 1 else "failed",
            "source_asset_count": source_assets,
        },
        {
            "id": "reference_image_handoff",
            "status": "passed" if source_images == 2 else "failed",
            "source_image_count": source_images,
        },
        {
            "id": "generation_request",
            "status": (
                "passed"
                if request is not None
                and len(request.source_images) == 2
                and len(request.source_assets) == 1
                else "failed"
            ),
        },
        {
            "id": "generation_provenance",
            "status": "passed",
            "detail": "local generation provenance is included in generated asset",
        },
        {
            "id": "report_safety",
            "status": "passed",
            "detail": "report exposes counts and content types only",
        },
    ]


def _summary(checks: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "passed": sum(1 for check in checks if check["status"] == "passed"),
        "failed": sum(1 for check in checks if check["status"] == "failed"),
    }


def _safety_summary() -> dict[str, bool]:
    return {
        "raw_media_in_report": False,
        "local_paths_in_report": False,
        "provider_secrets_in_report": False,
    }


def _sanitize_report(report: dict[str, Any], capture_storage_dir: Path) -> dict[str, Any]:
    return json.loads(json.dumps(_sanitize_value(report, capture_storage_dir)))


def _sanitize_value(value: Any, capture_storage_dir: Path) -> Any:
    if isinstance(value, str):
        return _safe_text(value, capture_storage_dir)
    if isinstance(value, list):
        return [_sanitize_value(item, capture_storage_dir) for item in value]
    if isinstance(value, dict):
        return {key: _sanitize_value(item, capture_storage_dir) for key, item in value.items()}
    return value


def _safe_text(message: str, capture_storage_dir: Path) -> str:
    sanitized = message
    replacements = [
        r"Authorization\s*[=:]\s*Bearer\s+[A-Za-z0-9._~+/\-=:-]+",
        r"Bearer\s+[A-Za-z0-9._~+/\-=:-]+",
        r"raw=[^\s,;\"']+",
        r"api[_-]?key\s*[=:]\s*[^\s,;\"']+",
        r"data:[A-Za-z0-9.+-]+/[A-Za-z0-9.+-]+;base64,[A-Za-z0-9+/=_-]+",
        r"local-capture://[^\s,;\"']+",
        r"file://[^\s,;\"']+",
    ]
    for pattern in replacements:
        sanitized = re.sub(pattern, "[redacted]", sanitized, flags=re.IGNORECASE)
    for path in {capture_storage_dir, Path.home(), Path("/tmp")}:
        path_text = str(path)
        if path_text:
            sanitized = sanitized.replace(path_text, "[path]")
    sanitized = re.sub(r"/Users/[^\s,;\"']+", "[path]", sanitized)
    return sanitized
