from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from myth_forge_api.resource_handoff import (
    BACKEND_ENV_DESTINATION,
    IOS_DEPLOY_DESTINATION,
)

BACKEND_TEMPLATE_PATH = ".env.example"
IOS_TEMPLATE_PATH = "apps/mobile/ios/Config/Deployment.local.xcconfig.example"
GITIGNORE_PATH = ".gitignore"
MAKEFILE_PATH = "Makefile"
BACKEND_WRITER_PATH = "services/backend/scripts/write_backend_env.sh"
BACKEND_WRITER_MAKE_TARGET = "backend-write-provider-env"
BANNED_WRITER_TEXT = [
    "sudo",
    "xcode-select",
    "xcodebuild -license",
    "security ",
    "codesign",
    "curl ",
    "urllib.request",
]

BACKEND_REQUIRED_KEYS = [
    "THREE_D_PROVIDER",
    "MESHY_API_BASE_URL",
    "MESHY_POLL_INTERVAL_SECONDS",
    "MESHY_MAX_WAIT_SECONDS",
    "MESHY_API_KEY",
    "NPC_PROVIDER",
    "OPENAI_NPC_MODEL",
    "OPENAI_API_BASE_URL",
    "OPENAI_API_KEY",
    "PRINT_PROVIDER",
    "TREATSTOCK_API_KEY",
    "SCULPTEO_API_KEY",
    "CAPTURE_STORAGE_DIR",
    "MYTH_SESSION_STORAGE_DIR",
]

IOS_REQUIRED_KEYS = [
    "DEVELOPMENT_TEAM",
    "PRODUCT_BUNDLE_IDENTIFIER",
    "PMF_BACKEND_BASE_URL",
]

LOCAL_DESTINATIONS = [
    ".env",
    BACKEND_ENV_DESTINATION,
    IOS_DEPLOY_DESTINATION,
    "services/backend/.local/",
]


@dataclass(frozen=True)
class ResourceTemplateAcceptanceResult:
    exit_code: int
    report: dict[str, Any]


def run_resource_template_acceptance(
    *,
    repo_root: str | Path | None = None,
) -> ResourceTemplateAcceptanceResult:
    selected_repo_root = Path(repo_root) if repo_root is not None else _default_repo_root()
    backend_text, backend_exists = _read_optional_text(
        selected_repo_root / BACKEND_TEMPLATE_PATH
    )
    ios_text, ios_exists = _read_optional_text(selected_repo_root / IOS_TEMPLATE_PATH)
    gitignore_text, gitignore_exists = _read_optional_text(
        selected_repo_root / GITIGNORE_PATH
    )
    makefile_text, makefile_exists = _read_optional_text(selected_repo_root / MAKEFILE_PATH)
    backend_writer_text, backend_writer_exists = _read_optional_text(
        selected_repo_root / BACKEND_WRITER_PATH
    )

    backend_keys = _parse_assignment_keys(backend_text, comment_prefixes=("#",))
    ios_keys = _parse_assignment_keys(ios_text, comment_prefixes=("#", "//"))
    gitignore_patterns = _parse_gitignore_patterns(gitignore_text)

    backend_missing = _missing_keys(BACKEND_REQUIRED_KEYS, backend_keys)
    ios_missing = _missing_keys(IOS_REQUIRED_KEYS, ios_keys)
    gitignore_items = [
        _gitignore_item(path, gitignore_patterns) for path in LOCAL_DESTINATIONS
    ]
    missing_gitignore = [
        item["path"] for item in gitignore_items if not item["ignored"]
    ]
    safety = _safety_summary("\n".join([backend_text, ios_text]))
    backend_writer_checks = _backend_writer_checks(
        writer_text=backend_writer_text,
        writer_exists=backend_writer_exists,
        makefile_text=makefile_text,
        makefile_exists=makefile_exists,
    )

    checks = [
        _check("backend_template_exists", backend_exists),
        _check("backend_template_keys", not backend_missing),
        _check("ios_template_exists", ios_exists),
        _check("ios_template_keys", not ios_missing),
        _check("gitignore_exists", gitignore_exists),
        _check("gitignore_local_destinations", not missing_gitignore),
        _check("template_safety", _templates_are_safe(safety)),
        _check("backend_writer", all(backend_writer_checks.values())),
    ]
    summary = {
        "passed": sum(1 for check in checks if check["status"] == "passed"),
        "failed": sum(1 for check in checks if check["status"] == "failed"),
    }
    status = "succeeded" if summary["failed"] == 0 else "failed"
    report = {
        "kind": "resource_template_acceptance_report",
        "status": status,
        "summary": summary,
        "checks": checks,
        "backend_template": {
            "path": BACKEND_TEMPLATE_PATH,
            "destination": BACKEND_ENV_DESTINATION,
            "exists": backend_exists,
            "required_keys": BACKEND_REQUIRED_KEYS,
            "present_keys": sorted(backend_keys),
            "missing_keys": backend_missing,
        },
        "ios_template": {
            "path": IOS_TEMPLATE_PATH,
            "destination": IOS_DEPLOY_DESTINATION,
            "exists": ios_exists,
            "required_keys": IOS_REQUIRED_KEYS,
            "present_keys": sorted(ios_keys),
            "missing_keys": ios_missing,
        },
        "gitignore": {
            "path": GITIGNORE_PATH,
            "exists": gitignore_exists,
            "local_destinations": gitignore_items,
            "missing_paths": missing_gitignore,
        },
        "backend_writer": {
            "path": BACKEND_WRITER_PATH,
            "make_target": BACKEND_WRITER_MAKE_TARGET,
            "exists": backend_writer_exists,
            "checks": backend_writer_checks,
        },
        "safety": safety,
    }
    sanitized_report = _sanitize_report(report)
    return ResourceTemplateAcceptanceResult(
        exit_code=0 if status == "succeeded" else 1,
        report=sanitized_report,
    )


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _read_optional_text(path: Path) -> tuple[str, bool]:
    if not path.exists():
        return "", False
    return path.read_text(encoding="utf-8"), True


def _parse_assignment_keys(
    text: str,
    *,
    comment_prefixes: tuple[str, ...],
) -> set[str]:
    keys: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(comment_prefixes):
            continue
        if stripped.startswith("export "):
            stripped = stripped.removeprefix("export ").strip()
        if "=" not in stripped:
            continue
        key, _value = stripped.split("=", 1)
        key = key.strip()
        if key:
            keys.add(key)
    return keys


def _parse_gitignore_patterns(text: str) -> list[str]:
    patterns: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        patterns.append(stripped)
    return patterns


def _missing_keys(required_keys: list[str], present_keys: set[str]) -> list[str]:
    return [key for key in required_keys if key not in present_keys]


def _gitignore_item(path: str, patterns: list[str]) -> dict[str, Any]:
    matched_by = _matching_gitignore_pattern(path, patterns)
    return {
        "path": path,
        "ignored": matched_by is not None,
        "matched_by": matched_by,
    }


def _matching_gitignore_pattern(path: str, patterns: list[str]) -> str | None:
    normalized_path = path.rstrip("/")
    path_name = normalized_path.rsplit("/", 1)[-1]
    for pattern in patterns:
        normalized_pattern = pattern.rstrip("/")
        if normalized_pattern == normalized_path:
            return pattern
        if "/" not in normalized_pattern and normalized_pattern == path_name:
            return pattern
        if pattern.endswith("/") and normalized_path.startswith(normalized_pattern + "/"):
            return pattern
    return None


def _check(check_id: str, passed: bool) -> dict[str, str]:
    return {
        "id": check_id,
        "status": "passed" if passed else "failed",
    }


def _backend_writer_checks(
    *,
    writer_text: str,
    writer_exists: bool,
    makefile_text: str,
    makefile_exists: bool,
) -> dict[str, bool]:
    return {
        "exists": writer_exists,
        "make_target": makefile_exists
        and BACKEND_WRITER_MAKE_TARGET in makefile_text
        and BACKEND_WRITER_PATH in makefile_text,
        "required_keys": all(
            key in writer_text
            for key in [
                "MESHY_API_KEY",
                "OPENAI_API_KEY",
                "THREE_D_PROVIDER=meshy",
                "NPC_PROVIDER=openai",
                "PRINT_PROVIDER=local",
            ]
        ),
        "redaction": "configured (redacted)" in writer_text,
        "tracked_env_guard": "services/backend/.env must stay untracked" in writer_text,
        "no_banned_commands": not any(
            banned in writer_text for banned in BANNED_WRITER_TEXT
        ),
    }


def _safety_summary(template_text: str) -> dict[str, bool]:
    provider_secrets = _has_provider_secret(template_text)
    raw_media = bool(re.search(r"data:[^;\s]+;base64,|local-capture://", template_text))
    local_paths = _has_local_path(template_text)
    payment_links = bool(
        re.search(r"https?://(?:pay|checkout)\.|/checkout(?:/|$)", template_text)
    )
    return {
        "provider_secrets_in_templates": provider_secrets,
        "provider_secrets_in_report": False,
        "raw_media_in_templates": raw_media,
        "raw_media_in_report": False,
        "local_paths_in_templates": local_paths,
        "local_paths_in_report": False,
        "payment_links_in_templates": payment_links,
        "payment_links_in_report": False,
        "provider_calls": False,
        "global_mutation": False,
    }


def _has_provider_secret(text: str) -> bool:
    return bool(
        re.search(r"\bsk-[A-Za-z0-9_-]{6,}", text)
        or re.search(r"Bearer\s+[A-Za-z0-9._~+/\-=:-]{6,}", text)
        or re.search(
            r"(?i)\b(?:api[_-]?key|secret|token)\s*=\s*[^\s#\"']{6,}",
            text,
        )
    )


def _has_local_path(text: str) -> bool:
    home = str(Path.home())
    return bool(
        "file://" in text
        or home in text
        or re.search(r"(?m)(?:^|[\s=])/(?:Users|tmp|var/folders)/[^\s]+", text)
    )


def _templates_are_safe(safety: dict[str, bool]) -> bool:
    return not (
        safety["provider_secrets_in_templates"]
        or safety["raw_media_in_templates"]
        or safety["local_paths_in_templates"]
        or safety["payment_links_in_templates"]
    )


def _sanitize_report(report: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(_sanitize_value(report)))


def _sanitize_value(value: Any) -> Any:
    if isinstance(value, str):
        return _safe_text(value)
    if isinstance(value, list):
        return [_sanitize_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _sanitize_value(item) for key, item in value.items()}
    return value


def _safe_text(message: str) -> str:
    sanitized = re.sub(r"\bsk-[A-Za-z0-9_-]+", "[redacted]", message)
    sanitized = re.sub(
        r"Bearer\s+[A-Za-z0-9._~+/\-=:-]+",
        "[redacted]",
        sanitized,
    )
    sanitized = re.sub(
        r"(?i)(api[_-]?key|secret|token)\s*=\s*[^\s#\"']+",
        r"\1=[redacted]",
        sanitized,
    )
    sanitized = re.sub(
        r"data:[^;\s]+;base64,[A-Za-z0-9+/=_-]+",
        "[redacted-media]",
        sanitized,
    )
    sanitized = re.sub(
        r"file://[^\s,;\"']+",
        "[redacted-local-path]",
        sanitized,
    )
    sanitized = re.sub(
        r"/(?:Users|tmp|var/folders)/[^\s,;\"']+",
        "[redacted-local-path]",
        sanitized,
    )
    return sanitized
