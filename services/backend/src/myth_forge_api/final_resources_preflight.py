from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_RESOURCES_PATH = Path("services/backend/.local/final-resources.env")

ACCEPTED_KEYS = [
    "MESHY_API_KEY",
    "OPENAI_API_KEY",
    "OPENAI_API_BASE_URL",
    "PRINT_PROVIDER",
    "TREATSTOCK_API_KEY",
    "TREATSTOCK_API_BASE_URL",
    "SCULPTEO_API_KEY",
    "DEVELOPMENT_TEAM",
    "PRODUCT_BUNDLE_IDENTIFIER",
    "PMF_BACKEND_BASE_URL",
    "PMF_FINAL_LAUNCH_MODE",
    "CAPTURE_STORAGE_DIR",
    "MYTH_SESSION_STORAGE_DIR",
]

ALWAYS_REQUIRED_KEYS = {
    "MESHY_API_KEY",
    "OPENAI_API_KEY",
    "DEVELOPMENT_TEAM",
    "PRODUCT_BUNDLE_IDENTIFIER",
    "PMF_BACKEND_BASE_URL",
}

SECRET_KEYS = {
    "MESHY_API_KEY",
    "OPENAI_API_KEY",
    "TREATSTOCK_API_KEY",
    "SCULPTEO_API_KEY",
}

SUPPORTED_PRINT_PROVIDERS = {"local", "treatstock"}
SUPPORTED_FINAL_LAUNCH_MODES = {"local", "configured"}
EXAMPLE_BACKEND_BASE_URLS = {"http://192.168.1.10:8080"}
AUTO_BACKEND_URL_APPLY_NOTE = (
    "Resolved by write_deploy_local_config.sh during final-apply-resources."
)


@dataclass(frozen=True)
class FinalResourcesPreflightResult:
    exit_code: int
    report: dict[str, Any]


def build_final_resources_preflight_report(
    *,
    repo_root: Path | str | None = None,
    resources_file: Path | str | None = None,
) -> FinalResourcesPreflightResult:
    selected_repo_root = Path(repo_root) if repo_root is not None else _default_repo_root()
    selected_resources_file = (
        Path(resources_file)
        if resources_file is not None
        else selected_repo_root / DEFAULT_RESOURCES_PATH
    )
    resources_label = _path_label(
        path=selected_resources_file,
        repo_root=selected_repo_root,
    )

    if not selected_resources_file.exists():
        report = {
            "kind": "final_resources_preflight_report",
            "status": "missing",
            "resources_file": {"path": resources_label, "exists": False},
            "summary": {
                "ready": 0,
                "missing": 1,
                "blocked": 0,
                "optional": 0,
            },
            "items": [],
            "unknown_keys": [],
            "malformed_lines": [],
            "operator_actions": ["run make final-resource-init"],
            "safety": _safety(),
        }
        return FinalResourcesPreflightResult(exit_code=2, report=report)

    parsed = _parse_resources(selected_resources_file)
    values = parsed["values"]
    unknown_keys = sorted(key for key in values if key not in ACCEPTED_KEYS)
    malformed_lines = parsed["malformed_lines"]
    print_provider = (values.get("PRINT_PROVIDER") or "local").strip().lower()
    final_launch_mode = (values.get("PMF_FINAL_LAUNCH_MODE") or "local").strip().lower()
    treatstock_required = print_provider == "treatstock"
    items = _items(
        values=values,
        print_provider=print_provider,
        final_launch_mode=final_launch_mode,
    )
    item_statuses = [item["status"] for item in items]
    blocked_count = item_statuses.count("blocked") + len(unknown_keys) + len(malformed_lines)
    missing_count = sum(
        1 for item in items if item["status"] == "missing" and item["required"]
    )
    status = "ready"
    if blocked_count or missing_count:
        status = "blocked"

    report = {
        "kind": "final_resources_preflight_report",
        "status": status,
        "resources_file": {"path": resources_label, "exists": True},
        "summary": {
            "ready": item_statuses.count("ready"),
            "missing": missing_count,
            "blocked": blocked_count,
            "optional": item_statuses.count("optional"),
        },
        "items": items,
        "unknown_keys": unknown_keys,
        "malformed_lines": malformed_lines,
        "operator_actions": _operator_actions(
            items=items,
            unknown_keys=unknown_keys,
            malformed_lines=malformed_lines,
            treatstock_required=treatstock_required,
        ),
        "safety": _safety(),
    }
    return FinalResourcesPreflightResult(
        exit_code=0 if status == "ready" else 2,
        report=report,
    )


def _items(
    *,
    values: dict[str, str],
    print_provider: str,
    final_launch_mode: str,
) -> list[dict[str, Any]]:
    return [
        _key_item("MESHY_API_KEY", values, required=True),
        _key_item("OPENAI_API_KEY", values, required=True),
        _key_item("OPENAI_API_BASE_URL", values, required=False),
        _print_provider_item(values=values, normalized_value=print_provider),
        _key_item(
            "TREATSTOCK_API_KEY",
            values,
            required=print_provider == "treatstock",
        ),
        _key_item("TREATSTOCK_API_BASE_URL", values, required=False),
        _key_item("SCULPTEO_API_KEY", values, required=False),
        _key_item("DEVELOPMENT_TEAM", values, required=True),
        _bundle_identifier_item(values),
        _backend_url_item(values),
        _final_launch_mode_item(values=values, normalized_value=final_launch_mode),
        _key_item("CAPTURE_STORAGE_DIR", values, required=False),
        _key_item("MYTH_SESSION_STORAGE_DIR", values, required=False),
    ]


def _key_item(
    key: str,
    values: dict[str, str],
    *,
    required: bool,
) -> dict[str, Any]:
    value = values.get(key, "")
    configured = bool(value)
    status = "ready" if configured else "missing"
    if not configured and not required:
        status = "optional"
    item = {
        "id": key,
        "status": status,
        "required": required,
        "configured": configured,
        "redacted": key in SECRET_KEYS and configured,
    }
    if status == "missing":
        item["classification"] = "missing_required_value"
    return item


def _print_provider_item(
    *,
    values: dict[str, str],
    normalized_value: str,
) -> dict[str, Any]:
    configured = bool(values.get("PRINT_PROVIDER"))
    status = "ready" if normalized_value in SUPPORTED_PRINT_PROVIDERS else "blocked"
    item = {
        "id": "PRINT_PROVIDER",
        "status": status,
        "required": False,
        "configured": configured,
        "normalized_value": normalized_value,
        "redacted": False,
    }
    if status == "blocked":
        item["classification"] = "unsupported_value"
    return item


def _final_launch_mode_item(
    *,
    values: dict[str, str],
    normalized_value: str,
) -> dict[str, Any]:
    configured = bool(values.get("PMF_FINAL_LAUNCH_MODE"))
    status = "ready" if normalized_value in SUPPORTED_FINAL_LAUNCH_MODES else "blocked"
    item = {
        "id": "PMF_FINAL_LAUNCH_MODE",
        "status": status,
        "required": False,
        "configured": configured,
        "normalized_value": normalized_value,
        "redacted": False,
    }
    if status == "blocked":
        item["classification"] = "unsupported_value"
    return item


def _backend_url_item(values: dict[str, str]) -> dict[str, Any]:
    key = "PMF_BACKEND_BASE_URL"
    value = values.get(key, "")
    configured = bool(value)
    resolution_mode = None
    apply_note = None
    if not configured:
        status = "missing"
        classification = "missing_required_value"
    elif _is_auto_backend_url(value):
        status = "ready"
        classification = "apply_time_auto_url"
        resolution_mode = "apply_time_auto"
        apply_note = AUTO_BACKEND_URL_APPLY_NOTE
    elif _is_example_backend_url(value):
        status = "blocked"
        classification = "placeholder_value"
    elif _is_loopback_url(value):
        status = "blocked"
        classification = "loopback_url"
    else:
        status = "ready"
        classification = None
    item = {
        "id": key,
        "status": status,
        "required": True,
        "configured": configured and status == "ready",
        "redacted": configured,
    }
    if classification:
        item["classification"] = classification
    if resolution_mode:
        item["resolution_mode"] = resolution_mode
    if apply_note:
        item["apply_note"] = apply_note
    return item


def _bundle_identifier_item(values: dict[str, str]) -> dict[str, Any]:
    key = "PRODUCT_BUNDLE_IDENTIFIER"
    value = values.get(key, "")
    configured = bool(value)
    if not configured:
        status = "missing"
        classification = "missing_required_value"
    elif _is_example_bundle_identifier(value):
        status = "blocked"
        classification = "placeholder_value"
    else:
        status = "ready"
        classification = None
    item = {
        "id": key,
        "status": status,
        "required": True,
        "configured": configured and status == "ready",
        "redacted": False,
    }
    if classification:
        item["classification"] = classification
    return item


def _parse_resources(path: Path) -> dict[str, Any]:
    values: dict[str, str] = {}
    malformed_lines: list[dict[str, int]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("export "):
            stripped = stripped.removeprefix("export ").strip()
        if "=" not in stripped:
            malformed_lines.append({"line_number": line_number})
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip()
    return {"values": values, "malformed_lines": malformed_lines}


def _operator_actions(
    *,
    items: list[dict[str, Any]],
    unknown_keys: list[str],
    malformed_lines: list[dict[str, int]],
    treatstock_required: bool,
) -> list[str]:
    actions: list[str] = []
    if unknown_keys:
        actions.append("remove unknown keys from final-resources.env")
    if malformed_lines:
        actions.append("fix malformed final resource lines")
    for item in items:
        if item["status"] == "missing" and item["required"]:
            actions.append(f"provide {item['id']} in final-resources.env")
        if item["status"] == "blocked" and item["id"] == "PMF_BACKEND_BASE_URL":
            actions.append("set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL")
        if item["status"] == "blocked" and item["id"] == "PRODUCT_BUNDLE_IDENTIFIER":
            actions.append("set PRODUCT_BUNDLE_IDENTIFIER to a unique app bundle id")
        if item["status"] == "blocked" and item["id"] == "PRINT_PROVIDER":
            actions.append("set PRINT_PROVIDER to local or treatstock")
        if item["status"] == "blocked" and item["id"] == "PMF_FINAL_LAUNCH_MODE":
            actions.append("set PMF_FINAL_LAUNCH_MODE to local or configured")
    if treatstock_required:
        actions.append("provide TREATSTOCK_API_KEY or set PRINT_PROVIDER=local")
    return _dedupe(actions)


def _is_loopback_url(value: str) -> bool:
    lowered = value.lower()
    return "://127.0.0.1" in lowered or "://localhost" in lowered


def _is_auto_backend_url(value: str) -> bool:
    return value.strip().lower() == "auto"


def _is_example_backend_url(value: str) -> bool:
    normalized = value.strip().rstrip("/").lower()
    return normalized in EXAMPLE_BACKEND_BASE_URLS


def _is_example_bundle_identifier(value: str) -> bool:
    normalized = value.strip().lower()
    return normalized == "com.example" or normalized.startswith("com.example.")


def _path_label(*, path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return "[external-final-resources-file]"


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def _safety() -> dict[str, bool]:
    return {
        "provider_secrets_in_report": False,
        "local_paths_in_report": False,
        "writes_backend_env": False,
        "writes_ios_deploy_config": False,
        "live_provider_calls": False,
        "global_mutation": False,
    }


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parents[4]
