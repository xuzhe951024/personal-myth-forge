from __future__ import annotations

import json
import re
import tempfile
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from myth_forge_api.providers.capture_store import LocalCaptureStore


@dataclass(frozen=True)
class CaptureSceneHandoffAcceptanceResult:
    exit_code: int
    report: dict[str, Any]


def run_capture_scene_handoff_acceptance(
    *,
    capture_storage_dir: str | Path | None = None,
) -> CaptureSceneHandoffAcceptanceResult:
    if capture_storage_dir is None:
        with tempfile.TemporaryDirectory(prefix="pmf-capture-scene-handoff-") as temp_dir:
            return _run_capture_scene_handoff_acceptance(Path(temp_dir))
    return _run_capture_scene_handoff_acceptance(Path(capture_storage_dir))


def _run_capture_scene_handoff_acceptance(
    capture_storage_dir: Path,
) -> CaptureSceneHandoffAcceptanceResult:
    import myth_forge_api.main as api_main

    store = LocalCaptureStore(root_dir=capture_storage_dir)
    original_build_capture_store = api_main.build_capture_store
    temporary_patch_restored = False
    try:
        api_main.build_capture_store = lambda: store
        client = _test_client(api_main.app)
        capture_response = client.post(
            "/v1/object-captures",
            data={
                "metadata_json": json.dumps(
                    {
                        "label": "acceptance brass key",
                        "materials": ["metal", "brass"],
                        "source": "acceptance_harness",
                        "capture_mode": "guided_scan",
                        "visual_notes": "front and side guided scan references",
                    }
                )
            },
            files=[
                ("files", ("front.jpg", b"front-jpeg", "image/jpeg")),
                ("files", ("side.png", b"side-png", "image/png")),
            ],
        )
        capture_payload = _json_payload(capture_response)
        session_response = client.post(
            "/v1/myth-sessions/from-capture",
            json={
                "capture_id": capture_payload.get("capture_id"),
                "context_capsule": {
                    "current_theme": "acceptance pressure",
                    "desired_tone": "tender, strange",
                },
            },
        )
        session_payload = _json_payload(session_response)
        game_asset = _game_asset(session_payload)
        scene_asset = _scene_asset(session_payload)
        game_response = client.get(game_asset.get("uri", "")) if game_asset else None
        scene_response = client.get(scene_asset.get("uri", "")) if scene_asset else None
        checks = [
            _check("capture_uploaded", capture_response.status_code == 200),
            _check("session_created_from_capture", session_response.status_code == 200),
            _check("guided_scan_media_count", len(capture_payload.get("media_items", [])) == 2),
            _check("multi_image_provenance", _has_multi_image_provenance(session_payload)),
            _check("game_asset_downloaded", _game_asset_is_downloadable(game_asset, game_response)),
            _check("scene_asset_downloaded", _scene_asset_is_downloadable(scene_asset, scene_response)),
            _check("report_safe", _session_payload_is_safe(session_payload)),
            _check("temporary_patch_restored", False),
        ]
    finally:
        api_main.build_capture_store = original_build_capture_store
        temporary_patch_restored = api_main.build_capture_store is original_build_capture_store

    checks[-1] = _check("temporary_patch_restored", temporary_patch_restored)
    failed = sum(1 for check in checks if check["status"] == "failed")
    report = {
        "kind": "capture_scene_handoff_acceptance_report",
        "status": "succeeded" if failed == 0 else "failed",
        "summary": {"passed": len(checks) - failed, "failed": failed},
        "capture": {
            "capture_mode": capture_payload.get("capture_mode"),
            "media_count": len(capture_payload.get("media_items", [])),
        },
        "session_id": session_payload.get("session_id"),
        "generation_provenance": _generation_provenance(session_payload),
        "game_asset": {
            "format": game_asset.get("format") if game_asset else None,
            "uri": game_asset.get("uri") if game_asset else None,
        },
        "scene_asset": {
            "role": scene_asset.get("role") if scene_asset else None,
            "format": scene_asset.get("format") if scene_asset else None,
            "uri": scene_asset.get("uri") if scene_asset else None,
            "is_scene_loadable": scene_asset.get("is_scene_loadable") if scene_asset else None,
        },
        "checks": checks,
        "safety": {
            "provider_calls": False,
            "temporary_app_patch_restored": temporary_patch_restored,
            "raw_media_in_report": False,
            "local_capture_uris_in_report": False,
            "local_paths_in_report": False,
            "provider_secrets_in_report": False,
        },
    }
    sanitized = _sanitize_report(report, capture_storage_dir)
    return CaptureSceneHandoffAcceptanceResult(
        exit_code=0 if failed == 0 else 1,
        report=sanitized,
    )


def _test_client(app):
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message=r"Using `httpx` with `starlette\.testclient` is deprecated.*",
        )
        from fastapi.testclient import TestClient

    return TestClient(app)


def _json_payload(response) -> dict[str, Any]:
    try:
        data = response.json()
    except ValueError:
        data = {}
    return data if isinstance(data, dict) else {}


def _game_asset(session_payload: dict[str, Any]) -> dict[str, Any] | None:
    generated_asset = session_payload.get("generated_asset")
    return generated_asset if isinstance(generated_asset, dict) else None


def _scene_asset(session_payload: dict[str, Any]) -> dict[str, Any] | None:
    generated_asset = _game_asset(session_payload)
    if generated_asset is None:
        return None
    variants = generated_asset.get("variants")
    if not isinstance(variants, list):
        return None
    for variant in variants:
        if (
            isinstance(variant, dict)
            and variant.get("role") == "ios_scene_asset"
            and variant.get("is_scene_loadable") is True
        ):
            return variant
    return None


def _generation_provenance(session_payload: dict[str, Any]) -> dict[str, Any] | None:
    generated_asset = _game_asset(session_payload)
    if generated_asset is None:
        return None
    provenance = generated_asset.get("generation_provenance")
    return provenance if isinstance(provenance, dict) else None


def _has_multi_image_provenance(session_payload: dict[str, Any]) -> bool:
    provenance = _generation_provenance(session_payload)
    return (
        provenance is not None
        and provenance.get("input_mode") == "multi_image"
        and provenance.get("source_image_count") == 2
        and provenance.get("selected_source_image_count") == 2
        and provenance.get("raw_sources_included") is False
    )


def _game_asset_is_downloadable(asset: dict[str, Any] | None, response) -> bool:
    uri = asset.get("uri") if asset else ""
    return (
        isinstance(uri, str)
        and uri.startswith("http://testserver/v1/generated-assets/")
        and uri.endswith("/game.glb")
        and response is not None
        and response.status_code == 200
        and response.content.startswith(b"glTF")
    )


def _scene_asset_is_downloadable(asset: dict[str, Any] | None, response) -> bool:
    uri = asset.get("uri") if asset else ""
    return (
        isinstance(uri, str)
        and asset.get("format") == "dae"
        and uri.startswith("http://testserver/v1/generated-assets/")
        and uri.endswith("/scene.dae")
        and response is not None
        and response.status_code == 200
        and "COLLADA" in response.text
    )


def _session_payload_is_safe(session_payload: dict[str, Any]) -> bool:
    text = json.dumps(session_payload)
    unsafe_markers = (
        "data:image",
        "local-capture://",
        "Authorization",
        "Bearer ",
        "/tmp",
        "/Users/",
    )
    return not any(marker in text for marker in unsafe_markers)


def _check(check_id: str, passed: bool) -> dict[str, str]:
    return {
        "id": check_id,
        "status": "passed" if passed else "failed",
    }


def _sanitize_report(report: dict[str, Any], capture_storage_dir: Path) -> dict[str, Any]:
    sanitized = json.loads(json.dumps(_sanitize_value(report, capture_storage_dir)))
    text = json.dumps(sanitized)
    sanitized["safety"]["raw_media_in_report"] = "data:image" in text
    sanitized["safety"]["local_capture_uris_in_report"] = "local-capture://" in text
    sanitized["safety"]["local_paths_in_report"] = "/tmp" in text or "/Users/" in text
    sanitized["safety"]["provider_secrets_in_report"] = (
        "Authorization" in text or "Bearer " in text or "sk-" in text
    )
    return sanitized


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
