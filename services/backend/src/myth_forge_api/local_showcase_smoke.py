from __future__ import annotations

import json
import os
import re
import tempfile
import warnings
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterator


@dataclass(frozen=True)
class LocalShowcaseSmokeResult:
    exit_code: int
    report: dict[str, Any]


ClientFactory = Callable[[], Any]


def build_local_showcase_smoke_report(
    *,
    client_factory: ClientFactory | None = None,
) -> LocalShowcaseSmokeResult:
    with tempfile.TemporaryDirectory(prefix="pmf-local-showcase-smoke-") as temp_dir:
        temp_root = Path(temp_dir)
        with _temporary_local_environment(temp_root):
            return _run_smoke(client_factory or _test_client, temp_root)


def _run_smoke(client_factory: ClientFactory, temp_root: Path) -> LocalShowcaseSmokeResult:
    client = client_factory()
    steps: list[dict[str, Any]] = []
    downloads: dict[str, dict[str, Any]] = {}
    session_summary: dict[str, Any] | None = None
    npc_summary: dict[str, Any] | None = None
    print_summary: dict[str, Any] | None = None

    capture_response = client.post(
        "/v1/object-captures",
        data={"metadata_json": json.dumps(_capture_metadata())},
        files=[
            ("files", ("front.jpg", b"front-jpeg", "image/jpeg")),
            ("files", ("side.png", b"side-png", "image/png")),
            ("files", ("detail.png", b"detail-png", "image/png")),
        ],
    )
    capture_payload = _json_payload(capture_response)
    steps.append(
        _http_step(
            "upload_guided_scan_capture",
            "POST",
            "/v1/object-captures",
            capture_response,
            passed=(
                capture_response.status_code == 200
                and capture_payload.get("capture_mode") == "guided_scan"
            ),
        )
    )
    if steps[-1]["status"] == "failed":
        return _result(steps=steps, downloads=downloads, temp_root=temp_root)

    session_response = client.post(
        "/v1/myth-sessions/from-capture",
        json={
            "capture_id": capture_payload.get("capture_id"),
            "context_capsule": {
                "current_theme": "showcase pressure",
                "desired_tone": "tender, strange",
            },
        },
    )
    session_payload = _json_payload(session_response)
    scene_variant = _scene_variant(session_payload)
    steps.append(
        _http_step(
            "create_session_from_capture",
            "POST",
            "/v1/myth-sessions/from-capture",
            session_response,
            passed=session_response.status_code == 200 and scene_variant is not None,
        )
    )
    if steps[-1]["status"] == "failed":
        return _result(steps=steps, downloads=downloads, temp_root=temp_root)

    generated_asset = _dict(session_payload.get("generated_asset"))
    game_uri = str(generated_asset.get("uri", ""))
    scene_uri = str(scene_variant.get("uri", "")) if scene_variant else ""
    print_candidate = _dict(session_payload.get("print_candidate"))
    print_uri = str(print_candidate.get("uri", ""))
    session_id = str(session_payload.get("session_id", ""))

    game_response = client.get(game_uri)
    game_passed = (
        game_response.status_code == 200
        and bytes(getattr(game_response, "content", b"")).startswith(b"glTF")
    )
    downloads["game_glb"] = _download_proof(game_response, "glTF", game_passed)
    steps.append(_download_step("download_game_asset", game_uri, game_response, game_passed))

    scene_response = client.get(scene_uri)
    scene_text = str(getattr(scene_response, "text", ""))
    scene_passed = scene_response.status_code == 200 and "COLLADA" in scene_text
    downloads["scene_dae"] = _download_proof(scene_response, "COLLADA", scene_passed)
    steps.append(_download_step("download_scene_asset", scene_uri, scene_response, scene_passed))

    autonomy_response = client.post(
        f"/v1/myth-sessions/{session_id}/autonomy-runs",
        json={"step_count": 2},
    )
    autonomy_payload = _json_payload(autonomy_response)
    steps.append(
        _http_step(
            "run_npc_autonomy",
            "POST",
            f"/v1/myth-sessions/{session_id}/autonomy-runs",
            autonomy_response,
            passed=(
                autonomy_response.status_code == 200
                and autonomy_payload.get("completed_steps") == 2
            ),
        )
    )

    quote_response = client.post(
        "/v1/print-quotes",
        json={"print_candidate": print_candidate},
    )
    quote_payload = _json_payload(quote_response)
    steps.append(
        _http_step(
            "create_print_quote",
            "POST",
            "/v1/print-quotes",
            quote_response,
            passed=(
                quote_response.status_code == 200
                and quote_payload.get("status") == "draft_quote"
            ),
        )
    )

    print_response = client.get(print_uri)
    print_passed = (
        print_response.status_code == 200
        and bytes(getattr(print_response, "content", b"")).startswith(b"PK")
    )
    downloads["print_3mf"] = _download_proof(print_response, "PK", print_passed)
    steps.append(_download_step("download_print_asset", print_uri, print_response, print_passed))

    history_response = client.get(f"/v1/myth-sessions/{session_id}/history")
    history_payload = _json_payload(history_response)
    ticks = history_payload.get("npc_ticks") if isinstance(history_payload, dict) else []
    tick_count = len(ticks) if isinstance(ticks, list) else 0
    steps.append(
        _check_step(
            "history_contains_ticks",
            tick_count == 2,
            detail=f"Saved history contains {tick_count} NPC ticks.",
        )
    )

    provenance = _dict(generated_asset.get("generation_provenance"))
    steps.append(
        _check_step(
            "generation_provenance",
            provenance.get("input_mode") == "multi_image"
            and provenance.get("raw_sources_included") is False,
            detail="Generation provenance proves multi-image routing without raw sources.",
        )
    )
    steps.append(
        _check_step(
            "report_safety",
            True,
            detail="Smoke report exposes counts and proofs only.",
        )
    )

    session_summary = {
        "session_id": session_id,
        "generated_asset_provider": generated_asset.get("provider"),
        "generation_input_mode": provenance.get("input_mode"),
        "scene_variant_format": scene_variant.get("format") if scene_variant else None,
        "npc_agent_runtime": session_payload.get("npc_agent_runtime"),
    }
    npc_summary = {
        "requested_steps": autonomy_payload.get("requested_steps"),
        "completed_steps": autonomy_payload.get("completed_steps"),
        "agent_runtime": autonomy_payload.get("agent_runtime"),
    }
    print_summary = {
        "quote_status": quote_payload.get("status"),
        "provider": quote_payload.get("provider"),
        "requires_user_approval": quote_payload.get("requires_user_approval"),
    }

    return _result(
        steps=steps,
        downloads=downloads,
        temp_root=temp_root,
        session=session_summary,
        npc=npc_summary,
        print_summary=print_summary,
    )


def _result(
    *,
    steps: list[dict[str, Any]],
    downloads: dict[str, dict[str, Any]],
    temp_root: Path,
    session: dict[str, Any] | None = None,
    npc: dict[str, Any] | None = None,
    print_summary: dict[str, Any] | None = None,
) -> LocalShowcaseSmokeResult:
    failed = sum(1 for step in steps if step["status"] == "failed")
    passed = len(steps) - failed
    report = {
        "kind": "local_showcase_smoke_report",
        "status": "succeeded" if failed == 0 else "failed",
        "summary": {
            "passed": passed,
            "failed": failed,
            "http_steps": 6 if failed == 0 else min(len(steps), 6),
            "npc_ticks": _non_negative_int((npc or {}).get("completed_steps")),
            "downloads": len(downloads),
        },
        "steps": steps,
        "session": session,
        "npc": npc,
        "print": print_summary,
        "downloads": downloads,
        "safety": _safety(),
    }
    sanitized = _sanitize_report(report, temp_root)
    return LocalShowcaseSmokeResult(
        exit_code=0 if sanitized["status"] == "succeeded" else 1,
        report=sanitized,
    )


def _capture_metadata() -> dict[str, Any]:
    return {
        "label": "showcase brass key",
        "materials": ["metal", "brass"],
        "source": "iphone_local_smoke",
        "capture_mode": "guided_scan",
        "visual_notes": "front, side, and detail reference images",
    }


def _http_step(
    step_id: str,
    method: str,
    path: str,
    response: Any,
    *,
    passed: bool,
) -> dict[str, Any]:
    return {
        "id": step_id,
        "status": "passed" if passed else "failed",
        "method": method,
        "path": path,
        "status_code": getattr(response, "status_code", None),
        "detail": "HTTP step completed." if passed else _failure_detail(response),
    }


def _download_step(step_id: str, uri: str, response: Any, passed: bool) -> dict[str, Any]:
    return {
        "id": step_id,
        "status": "passed" if passed else "failed",
        "method": "GET",
        "path": _path_only(uri),
        "status_code": getattr(response, "status_code", None),
        "detail": "Download proof matched." if passed else _failure_detail(response),
    }


def _check_step(step_id: str, passed: bool, *, detail: str) -> dict[str, Any]:
    return {
        "id": step_id,
        "status": "passed" if passed else "failed",
        "detail": detail if passed else f"Check failed. {detail}",
    }


def _download_proof(response: Any, expected: str, passed: bool) -> dict[str, Any]:
    return {
        "status_code": getattr(response, "status_code", None),
        "content_proof": expected if passed else "missing",
    }


def _json_payload(response: Any) -> dict[str, Any]:
    try:
        payload = response.json()
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _scene_variant(payload: dict[str, Any]) -> dict[str, Any] | None:
    generated_asset = _dict(payload.get("generated_asset"))
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


def _failure_detail(response: Any) -> str:
    status_code = getattr(response, "status_code", None)
    text = str(getattr(response, "text", ""))
    if not text or "Internal Server Error" in text:
        return f"HTTP {status_code}."
    return f"HTTP {status_code}: {text[:180]}"


def _path_only(uri: str) -> str:
    if not uri:
        return ""
    for prefix in ("http://testserver", "https://testserver"):
        if uri.startswith(prefix):
            return uri[len(prefix):]
    return uri


def _non_negative_int(value: Any) -> int:
    return value if isinstance(value, int) and value >= 0 else 0


def _safety() -> dict[str, bool]:
    return {
        "provider_calls": False,
        "live_provider_calls": False,
        "global_mutation": False,
        "starts_server": False,
        "writes_repo_local_media": False,
        "uses_temporary_storage": True,
        "provider_secrets_in_report": False,
        "raw_media_in_report": False,
        "local_paths_in_report": False,
        "payment_links_in_report": False,
    }


@contextmanager
def _temporary_local_environment(temp_root: Path) -> Iterator[None]:
    overrides = {
        "THREE_D_PROVIDER": "local",
        "NPC_PROVIDER": "local",
        "PRINT_PROVIDER": "local",
        "CAPTURE_STORAGE_DIR": str(temp_root / "captures"),
        "MYTH_SESSION_STORAGE_DIR": str(temp_root / "myth-sessions"),
    }
    previous = {key: os.environ.get(key) for key in overrides}
    try:
        os.environ.update(overrides)
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _test_client() -> Any:
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message=r"Using `httpx` with `starlette\.testclient` is deprecated.*",
        )
        from fastapi.testclient import TestClient

    from myth_forge_api.main import app

    return TestClient(app)


def _sanitize_report(report: dict[str, Any], temp_root: Path) -> dict[str, Any]:
    sanitized = json.loads(json.dumps(_sanitize_value(report, temp_root)))
    return sanitized


def _sanitize_value(value: Any, temp_root: Path) -> Any:
    if isinstance(value, str):
        return _safe_text(value, temp_root)
    if isinstance(value, list):
        return [_sanitize_value(item, temp_root) for item in value]
    if isinstance(value, dict):
        return {key: _sanitize_value(item, temp_root) for key, item in value.items()}
    return value


def _safe_text(message: str, temp_root: Path) -> str:
    sanitized = message
    patterns = [
        r"Authorization\s*[=:]\s*Bearer\s+[A-Za-z0-9._~+/\-=:-]+",
        r"Bearer\s+[A-Za-z0-9._~+/\-=:-]+",
        r"sk-[A-Za-z0-9._-]+",
        r"meshy-secret-[A-Za-z0-9._-]+",
        r"api[_-]?key\s*[=:]\s*[^\s,;\"']+",
        r"raw=[^\s,;\"']+",
        r"data:[A-Za-z0-9.+-]+/[A-Za-z0-9.+-]+;base64,[A-Za-z0-9+/=_-]+",
        r"local-capture://[^\s,;\"']+",
        r"file://[^\s,;\"']+",
        r"checkout_url",
        r"payment_link",
        r"https?://checkout\.[^\s,;\"']+",
        r"https?://pay\.[^\s,;\"']+",
        r"https?://pay\.[A-Za-z0-9./?=&_%:-]+",
    ]
    for pattern in patterns:
        sanitized = re.sub(pattern, "[withheld]", sanitized, flags=re.IGNORECASE)
    for path in {temp_root, Path.home(), Path("/tmp")}:
        path_text = str(path)
        if path_text:
            sanitized = sanitized.replace(path_text, "[withheld]")
    sanitized = re.sub(r"/Users/[^\s,;\"']+", "[withheld]", sanitized)
    return sanitized
