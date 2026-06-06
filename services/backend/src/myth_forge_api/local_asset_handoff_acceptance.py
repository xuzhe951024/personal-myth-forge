from __future__ import annotations

import json
import re
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from myth_forge_api.main import app


@dataclass(frozen=True)
class LocalAssetHandoffAcceptanceResult:
    exit_code: int
    report: dict[str, Any]


def run_local_asset_handoff_acceptance(
    *,
    repo_root: str | Path | None = None,
) -> LocalAssetHandoffAcceptanceResult:
    _ = repo_root
    client = _test_client()
    response = client.post(
        "/v1/myth-sessions",
        json={
            "object_observation": {
                "label": "old brass key",
                "materials": ["metal", "brass"],
                "source": "acceptance_harness",
            },
            "context_capsule": {
                "current_theme": "deadline pressure",
                "desired_tone": "tender, strange",
            },
        },
    )
    payload = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
    generated_asset = payload.get("generated_asset", {})
    game_uri = generated_asset.get("uri", "") if isinstance(generated_asset, dict) else ""
    game_response = client.get(game_uri) if game_uri else None
    scene_variant = _scene_variant(payload)
    scene_uri = scene_variant.get("uri", "") if scene_variant else ""
    scene_response = client.get(scene_uri) if scene_uri else None
    scene_text = scene_response.text if scene_response is not None else ""
    checks = [
        _check("session_created", response.status_code == 200),
        _check("game_asset_downloadable", _game_asset_is_downloadable(game_uri, game_response)),
        _check("scene_variant_present", scene_variant is not None),
        _check("scene_variant_http_url", _is_backend_scene_url(scene_uri)),
        _check(
            "scene_downloaded",
            scene_response is not None and scene_response.status_code == 200,
        ),
        _check("scene_content_safe", _scene_content_is_safe(scene_text, payload)),
    ]
    failed = sum(1 for check in checks if check["status"] == "failed")
    report = {
        "kind": "local_asset_handoff_acceptance_report",
        "status": "succeeded" if failed == 0 else "failed",
        "summary": {"passed": len(checks) - failed, "failed": failed},
        "session_id": payload.get("session_id"),
        "generated_asset_provider": generated_asset.get("provider")
        if isinstance(generated_asset, dict)
        else None,
        "game_asset": {
            "format": generated_asset.get("format") if isinstance(generated_asset, dict) else None,
            "uri": game_uri,
        },
        "scene_variant": {
            "role": scene_variant.get("role") if scene_variant else None,
            "format": scene_variant.get("format") if scene_variant else None,
            "uri": scene_uri,
            "is_scene_loadable": (
                scene_variant.get("is_scene_loadable") if scene_variant else None
            ),
        },
        "checks": checks,
        "safety": {
            "provider_calls": False,
            "global_mutation": False,
            "provider_secrets_in_report": False,
            "raw_media_in_report": False,
            "local_paths_in_report": False,
        },
    }
    sanitized = _sanitize_report(report)
    return LocalAssetHandoffAcceptanceResult(
        exit_code=0 if failed == 0 else 1,
        report=sanitized,
    )


def _scene_variant(payload: dict[str, Any]) -> dict[str, Any] | None:
    generated_asset = payload.get("generated_asset")
    if not isinstance(generated_asset, dict):
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


def _test_client():
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message=r"Using `httpx` with `starlette\.testclient` is deprecated.*",
        )
        from fastapi.testclient import TestClient

    return TestClient(app)


def _is_backend_scene_url(uri: str) -> bool:
    return (
        uri.startswith("http://testserver/v1/generated-assets/")
        and uri.endswith("/scene.dae")
    )


def _game_asset_is_downloadable(uri: str, response) -> bool:
    return (
        uri.startswith("http://testserver/v1/generated-assets/")
        and uri.endswith("/game.glb")
        and response is not None
        and response.status_code == 200
        and response.content.startswith(b"glTF")
    )


def _scene_content_is_safe(scene_text: str, payload: dict[str, Any]) -> bool:
    if not scene_text or "COLLADA" not in scene_text:
        return False
    if payload.get("session_id") not in scene_text:
        return False
    unsafe_markers = ("local://", "data:image", "Authorization", "Bearer ", "/tmp", "/Users/")
    return not any(marker in scene_text for marker in unsafe_markers)


def _check(check_id: str, passed: bool) -> dict[str, str]:
    return {
        "id": check_id,
        "status": "passed" if passed else "failed",
    }


def _sanitize_report(report: dict[str, Any]) -> dict[str, Any]:
    sanitized = json.loads(json.dumps(_sanitize_value(report)))
    text = json.dumps(sanitized)
    if "data:image" in text or "Authorization" in text or "Bearer " in text:
        sanitized["safety"]["raw_media_in_report"] = "data:image" in text
        sanitized["safety"]["provider_secrets_in_report"] = True
    if "/Users/" in text or "/tmp" in text:
        sanitized["safety"]["local_paths_in_report"] = True
    return sanitized


def _sanitize_value(value: Any) -> Any:
    if isinstance(value, str):
        return _safe_text(value)
    if isinstance(value, list):
        return [_sanitize_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _sanitize_value(item) for key, item in value.items()}
    return value


def _safe_text(message: str) -> str:
    sanitized = re.sub(
        r"Authorization\s*[=:]\s*Bearer\s+[A-Za-z0-9._~+/\-=:-]+",
        "[redacted]",
        message,
    )
    sanitized = re.sub(r"Bearer\s+[A-Za-z0-9._~+/\-=:-]+", "[redacted]", sanitized)
    sanitized = re.sub(
        r"data:[A-Za-z0-9.+-]+/[A-Za-z0-9.+-]+;base64,[A-Za-z0-9+/=_-]+",
        "[redacted-media]",
        sanitized,
    )
    sanitized = re.sub(r"/(?:Users|tmp)/[^\s,;\"']+", "[redacted-local-path]", sanitized)
    return sanitized
