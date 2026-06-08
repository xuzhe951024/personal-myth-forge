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
FINAL_RESOURCE_TEMPLATE_PATH = "services/backend/final-resources.env.example"
FINAL_RESOURCE_APPLY_PATH = "services/backend/scripts/apply_final_resources.sh"
FINAL_RESOURCE_APPLY_MAKE_TARGET = "final-apply-resources"
FINAL_RESOURCES_PREFLIGHT_PATH = (
    "services/backend/src/myth_forge_api/final_resources_preflight.py"
)
FINAL_RESOURCES_PREFLIGHT_MAKE_TARGET = "final-resources-preflight"
FINAL_CONFIGURED_PREFLIGHT_PATH = (
    "services/backend/src/myth_forge_api/final_configured_preflight.py"
)
FINAL_CONFIGURED_PREFLIGHT_MAKE_TARGET = "final-configured-preflight"
FINAL_CONFIGURED_PREFLIGHT_OUTPUT = ".local/final-configured-preflight.json"
FINAL_HANDOFF_INDEX_PATH = "services/backend/src/myth_forge_api/final_handoff_index.py"
FINAL_HANDOFF_INDEX_MAKE_TARGET = "final-handoff-index"
FINAL_HANDOFF_INDEX_OUTPUT = ".local/final-handoff-index.json"
IOS_DEVICE_LAUNCH_CERTIFICATE_PATH = (
    "services/backend/src/myth_forge_api/ios_device_launch_certificate.py"
)
IOS_DEVICE_LAUNCH_CERTIFICATE_MAKE_TARGET = "ios-device-launch-certificate"
IOS_DEVICE_LAUNCH_CERTIFICATE_OUTPUT = ".local/ios-device-launch-certificate.json"
IOS_DEVICE_LAUNCH_REHEARSAL_PATH = (
    "services/backend/src/myth_forge_api/ios_device_launch_rehearsal.py"
)
IOS_DEVICE_LAUNCH_REHEARSAL_READINESS_PATH = (
    "services/backend/src/myth_forge_api/ios_device_launch_rehearsal_readiness.py"
)
IOS_DEVICE_LAUNCH_REHEARSAL_SCRIPT_PATH = (
    "services/backend/scripts/write_ios_device_launch_rehearsal.sh"
)
IOS_DEVICE_LAUNCH_REHEARSAL_MAKE_TARGET = "ios-device-launch-rehearsal"
IOS_DEVICE_LAUNCH_REHEARSAL_OUTPUT = ".local/ios-device-launch-rehearsal.json"
CLI_PATH = "services/backend/src/myth_forge_api/cli.py"
FINAL_DEMO_LAUNCH_PATH = "services/backend/src/myth_forge_api/final_demo_launch.py"
FINAL_DEMO_LAUNCH_MAKE_TARGET = "final-demo-launch"
FINAL_DEMO_LAUNCH_LOCAL_OUTPUT = ".local/final-demo-launch-local.json"
FINAL_ACCEPTANCE_LOCAL_SCRIPT_PATH = (
    "services/backend/scripts/write_final_acceptance_local.sh"
)
IOS_DEPLOY_RUNBOOK_LOCAL_SCRIPT_PATH = (
    "services/backend/scripts/write_ios_deploy_runbook_local.sh"
)
FINAL_ACCEPTANCE_LOCAL_MAKE_TARGET = "final-acceptance-local"
IOS_DEPLOY_RUNBOOK_LOCAL_MAKE_TARGET = "ios-deploy-runbook-local"
FINAL_REHEARSAL_LOCAL_MAKE_TARGET = "final-rehearsal-local"
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
    "TREATSTOCK_API_BASE_URL",
    "SCULPTEO_API_KEY",
    "CAPTURE_STORAGE_DIR",
    "MYTH_SESSION_STORAGE_DIR",
]

FINAL_RESOURCE_REQUIRED_KEYS = [
    "MESHY_API_KEY",
    "OPENAI_API_KEY",
    "PRINT_PROVIDER",
    "TREATSTOCK_API_KEY",
    "TREATSTOCK_API_BASE_URL",
    "SCULPTEO_API_KEY",
    "DEVELOPMENT_TEAM",
    "PRODUCT_BUNDLE_IDENTIFIER",
    "PMF_BACKEND_BASE_URL",
    "PMF_FINAL_LAUNCH_MODE",
]

IOS_REQUIRED_KEYS = [
    "DEVELOPMENT_TEAM",
    "PRODUCT_BUNDLE_IDENTIFIER",
    "PMF_BACKEND_BASE_URL",
    "PMF_FINAL_LAUNCH_MODE",
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
    final_resource_template_text, final_resource_template_exists = _read_optional_text(
        selected_repo_root / FINAL_RESOURCE_TEMPLATE_PATH
    )
    final_resource_apply_text, final_resource_apply_exists = _read_optional_text(
        selected_repo_root / FINAL_RESOURCE_APPLY_PATH
    )
    final_resources_preflight_text, final_resources_preflight_exists = (
        _read_optional_text(selected_repo_root / FINAL_RESOURCES_PREFLIGHT_PATH)
    )
    final_configured_preflight_text, final_configured_preflight_exists = (
        _read_optional_text(selected_repo_root / FINAL_CONFIGURED_PREFLIGHT_PATH)
    )
    final_handoff_index_text, final_handoff_index_exists = _read_optional_text(
        selected_repo_root / FINAL_HANDOFF_INDEX_PATH
    )
    (
        ios_device_launch_certificate_text,
        ios_device_launch_certificate_exists,
    ) = _read_optional_text(selected_repo_root / IOS_DEVICE_LAUNCH_CERTIFICATE_PATH)
    (
        ios_device_launch_rehearsal_text,
        ios_device_launch_rehearsal_exists,
    ) = _read_optional_text(selected_repo_root / IOS_DEVICE_LAUNCH_REHEARSAL_PATH)
    (
        ios_device_launch_rehearsal_readiness_text,
        ios_device_launch_rehearsal_readiness_exists,
    ) = _read_optional_text(
        selected_repo_root / IOS_DEVICE_LAUNCH_REHEARSAL_READINESS_PATH
    )
    (
        ios_device_launch_rehearsal_script_text,
        ios_device_launch_rehearsal_script_exists,
    ) = _read_optional_text(
        selected_repo_root / IOS_DEVICE_LAUNCH_REHEARSAL_SCRIPT_PATH
    )
    cli_text, cli_exists = _read_optional_text(selected_repo_root / CLI_PATH)
    final_demo_launch_text, final_demo_launch_exists = _read_optional_text(
        selected_repo_root / FINAL_DEMO_LAUNCH_PATH
    )
    final_acceptance_local_script_text, final_acceptance_local_script_exists = (
        _read_optional_text(selected_repo_root / FINAL_ACCEPTANCE_LOCAL_SCRIPT_PATH)
    )
    (
        ios_deploy_runbook_local_script_text,
        ios_deploy_runbook_local_script_exists,
    ) = _read_optional_text(selected_repo_root / IOS_DEPLOY_RUNBOOK_LOCAL_SCRIPT_PATH)

    backend_keys = _parse_assignment_keys(backend_text, comment_prefixes=("#",))
    ios_keys = _parse_assignment_keys(ios_text, comment_prefixes=("#", "//"))
    final_resource_keys = _parse_assignment_keys(
        final_resource_template_text,
        comment_prefixes=("#",),
    )
    gitignore_patterns = _parse_gitignore_patterns(gitignore_text)

    backend_missing = _missing_keys(BACKEND_REQUIRED_KEYS, backend_keys)
    ios_missing = _missing_keys(IOS_REQUIRED_KEYS, ios_keys)
    final_resource_missing = _missing_keys(
        FINAL_RESOURCE_REQUIRED_KEYS,
        final_resource_keys,
    )
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
    final_resource_apply_checks = _final_resource_apply_checks(
        template_text=final_resource_template_text,
        template_exists=final_resource_template_exists,
        missing_keys=final_resource_missing,
        script_text=final_resource_apply_text,
        script_exists=final_resource_apply_exists,
        makefile_text=makefile_text,
        makefile_exists=makefile_exists,
    )
    final_resources_preflight_checks = _final_resources_preflight_checks(
        module_text=final_resources_preflight_text,
        module_exists=final_resources_preflight_exists,
        cli_text=cli_text,
        cli_exists=cli_exists,
        final_demo_launch_text=final_demo_launch_text,
        makefile_text=makefile_text,
        makefile_exists=makefile_exists,
    )
    final_demo_launch_checks = _final_demo_launch_checks(
        cli_text=cli_text,
        cli_exists=cli_exists,
        module_text=final_demo_launch_text,
        module_exists=final_demo_launch_exists,
        makefile_text=makefile_text,
        makefile_exists=makefile_exists,
    )
    final_configured_preflight_checks = _final_configured_preflight_checks(
        module_text=final_configured_preflight_text,
        module_exists=final_configured_preflight_exists,
        cli_text=cli_text,
        cli_exists=cli_exists,
        makefile_text=makefile_text,
        makefile_exists=makefile_exists,
    )
    final_handoff_index_checks = _final_handoff_index_checks(
        module_text=final_handoff_index_text,
        module_exists=final_handoff_index_exists,
        cli_text=cli_text,
        cli_exists=cli_exists,
        makefile_text=makefile_text,
        makefile_exists=makefile_exists,
    )
    ios_device_launch_certificate_checks = _ios_device_launch_certificate_checks(
        module_text=ios_device_launch_certificate_text,
        module_exists=ios_device_launch_certificate_exists,
        cli_text=cli_text,
        cli_exists=cli_exists,
        makefile_text=makefile_text,
        makefile_exists=makefile_exists,
    )
    ios_device_launch_rehearsal_checks = _ios_device_launch_rehearsal_checks(
        module_text=ios_device_launch_rehearsal_text,
        module_exists=ios_device_launch_rehearsal_exists,
        readiness_text=ios_device_launch_rehearsal_readiness_text,
        readiness_exists=ios_device_launch_rehearsal_readiness_exists,
        script_text=ios_device_launch_rehearsal_script_text,
        script_exists=ios_device_launch_rehearsal_script_exists,
        cli_text=cli_text,
        cli_exists=cli_exists,
        makefile_text=makefile_text,
        makefile_exists=makefile_exists,
    )
    final_rehearsal_local_checks = _final_rehearsal_local_checks(
        final_acceptance_script_text=final_acceptance_local_script_text,
        final_acceptance_script_exists=final_acceptance_local_script_exists,
        ios_deploy_runbook_script_text=ios_deploy_runbook_local_script_text,
        ios_deploy_runbook_script_exists=ios_deploy_runbook_local_script_exists,
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
        _check("final_resource_apply", all(final_resource_apply_checks.values())),
        _check(
            "final_resources_preflight",
            all(final_resources_preflight_checks.values()),
        ),
        _check("final_demo_launch", all(final_demo_launch_checks.values())),
        _check(
            "final_configured_preflight",
            all(final_configured_preflight_checks.values()),
        ),
        _check("final_handoff_index", all(final_handoff_index_checks.values())),
        _check(
            "ios_device_launch_certificate",
            all(ios_device_launch_certificate_checks.values()),
        ),
        _check(
            "ios_device_launch_rehearsal",
            all(ios_device_launch_rehearsal_checks.values()),
        ),
        _check("final_rehearsal_local", all(final_rehearsal_local_checks.values())),
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
        "final_resource_apply": {
            "path": FINAL_RESOURCE_APPLY_PATH,
            "template_path": FINAL_RESOURCE_TEMPLATE_PATH,
            "make_target": FINAL_RESOURCE_APPLY_MAKE_TARGET,
            "exists": final_resource_apply_exists,
            "template_exists": final_resource_template_exists,
            "required_keys": FINAL_RESOURCE_REQUIRED_KEYS,
            "present_keys": sorted(final_resource_keys),
            "missing_keys": final_resource_missing,
            "checks": final_resource_apply_checks,
        },
        "final_resources_preflight": {
            "path": FINAL_RESOURCES_PREFLIGHT_PATH,
            "make_target": FINAL_RESOURCES_PREFLIGHT_MAKE_TARGET,
            "exists": final_resources_preflight_exists,
            "checks": final_resources_preflight_checks,
        },
        "final_demo_launch": {
            "path": FINAL_DEMO_LAUNCH_PATH,
            "make_target": FINAL_DEMO_LAUNCH_MAKE_TARGET,
            "exists": final_demo_launch_exists,
            "checks": final_demo_launch_checks,
        },
        "final_configured_preflight": {
            "path": FINAL_CONFIGURED_PREFLIGHT_PATH,
            "make_target": FINAL_CONFIGURED_PREFLIGHT_MAKE_TARGET,
            "output_path": FINAL_CONFIGURED_PREFLIGHT_OUTPUT,
            "exists": final_configured_preflight_exists,
            "checks": final_configured_preflight_checks,
        },
        "final_handoff_index": {
            "path": FINAL_HANDOFF_INDEX_PATH,
            "make_target": FINAL_HANDOFF_INDEX_MAKE_TARGET,
            "output_path": FINAL_HANDOFF_INDEX_OUTPUT,
            "exists": final_handoff_index_exists,
            "checks": final_handoff_index_checks,
        },
        "ios_device_launch_certificate": {
            "path": IOS_DEVICE_LAUNCH_CERTIFICATE_PATH,
            "make_target": IOS_DEVICE_LAUNCH_CERTIFICATE_MAKE_TARGET,
            "output_path": IOS_DEVICE_LAUNCH_CERTIFICATE_OUTPUT,
            "exists": ios_device_launch_certificate_exists,
            "checks": ios_device_launch_certificate_checks,
        },
        "ios_device_launch_rehearsal": {
            "path": IOS_DEVICE_LAUNCH_REHEARSAL_PATH,
            "readiness_path": IOS_DEVICE_LAUNCH_REHEARSAL_READINESS_PATH,
            "script_path": IOS_DEVICE_LAUNCH_REHEARSAL_SCRIPT_PATH,
            "make_target": IOS_DEVICE_LAUNCH_REHEARSAL_MAKE_TARGET,
            "output_path": IOS_DEVICE_LAUNCH_REHEARSAL_OUTPUT,
            "exists": ios_device_launch_rehearsal_exists,
            "readiness_exists": ios_device_launch_rehearsal_readiness_exists,
            "script_exists": ios_device_launch_rehearsal_script_exists,
            "checks": ios_device_launch_rehearsal_checks,
        },
        "final_rehearsal_local": {
            "make_target": FINAL_REHEARSAL_LOCAL_MAKE_TARGET,
            "final_acceptance_script_path": FINAL_ACCEPTANCE_LOCAL_SCRIPT_PATH,
            "ios_deploy_runbook_script_path": IOS_DEPLOY_RUNBOOK_LOCAL_SCRIPT_PATH,
            "checks": final_rehearsal_local_checks,
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
                "PRINT_PROVIDER",
                "TREATSTOCK_API_BASE_URL",
            ]
        ),
        "redaction": "configured (redacted)" in writer_text,
        "tracked_env_guard": "services/backend/.env must stay untracked" in writer_text,
        "no_banned_commands": not any(
            banned in writer_text for banned in BANNED_WRITER_TEXT
        ),
    }


def _final_resource_apply_checks(
    *,
    template_text: str,
    template_exists: bool,
    missing_keys: list[str],
    script_text: str,
    script_exists: bool,
    makefile_text: str,
    makefile_exists: bool,
) -> dict[str, bool]:
    checked_text = "\n".join([template_text, script_text, makefile_text])
    return {
        "template_exists": template_exists,
        "template_keys": not missing_keys,
        "script_exists": script_exists,
        "make_target": makefile_exists
        and FINAL_RESOURCE_APPLY_MAKE_TARGET in makefile_text
        and FINAL_RESOURCE_APPLY_PATH in makefile_text,
        "uses_existing_writers": BACKEND_WRITER_PATH in script_text
        or "write_backend_env.sh" in script_text,
        "uses_ios_writer": "write_deploy_local_config.sh" in script_text,
        "redaction": "configured (redacted)" in script_text,
        "no_banned_commands": not any(
            banned in checked_text for banned in BANNED_WRITER_TEXT
        ),
    }


def _final_resources_preflight_checks(
    *,
    module_text: str,
    module_exists: bool,
    cli_text: str,
    cli_exists: bool,
    final_demo_launch_text: str,
    makefile_text: str,
    makefile_exists: bool,
) -> dict[str, bool]:
    checked_text = "\n".join([module_text, final_demo_launch_text, makefile_text])
    return {
        "module_exists": module_exists,
        "cli_command": cli_exists
        and "final-resources-preflight" in cli_text
        and "build_final_resources_preflight_report" in cli_text,
        "make_target": makefile_exists
        and FINAL_RESOURCES_PREFLIGHT_MAKE_TARGET in makefile_text
        and "myth_forge_api.cli final-resources-preflight" in makefile_text,
        "launch_integration": "build_final_resources_preflight_report"
        in final_demo_launch_text
        and "final_resources_preflight" in final_demo_launch_text,
        "no_banned_commands": not any(
            banned in checked_text for banned in BANNED_WRITER_TEXT
        ),
    }


def _final_demo_launch_checks(
    *,
    cli_text: str,
    cli_exists: bool,
    module_text: str,
    module_exists: bool,
    makefile_text: str,
    makefile_exists: bool,
) -> dict[str, bool]:
    checked_text = "\n".join([module_text, makefile_text])
    return {
        "module_exists": module_exists,
        "cli_command": cli_exists
        and "final-demo-launch" in cli_text
        and "build_final_demo_launch_report" in cli_text,
        "make_target": makefile_exists
        and FINAL_DEMO_LAUNCH_MAKE_TARGET in makefile_text
        and "myth_forge_api.cli final-demo-launch" in makefile_text,
        "local_output_path": FINAL_DEMO_LAUNCH_LOCAL_OUTPUT in makefile_text,
        "uses_resource_handoff": "build_resource_handoff_report" in module_text,
        "no_banned_commands": not any(
            banned in checked_text for banned in BANNED_WRITER_TEXT
        ),
    }


def _final_configured_preflight_checks(
    *,
    module_text: str,
    module_exists: bool,
    cli_text: str,
    cli_exists: bool,
    makefile_text: str,
    makefile_exists: bool,
) -> dict[str, bool]:
    checked_text = "\n".join([module_text, makefile_text])
    return {
        "module_exists": module_exists,
        "cli_command": cli_exists
        and "final-configured-preflight" in cli_text
        and "build_final_configured_preflight_report" in cli_text,
        "make_target": makefile_exists
        and FINAL_CONFIGURED_PREFLIGHT_MAKE_TARGET in makefile_text
        and "myth_forge_api.cli final-configured-preflight" in makefile_text,
        "output_path": FINAL_CONFIGURED_PREFLIGHT_OUTPUT in makefile_text,
        "composes_handoff_reports": all(
            text in module_text
            for text in [
                "build_final_resources_preflight_report",
                "build_provider_handoff_report",
                "build_resource_handoff_report",
                "build_final_demo_launch_report",
                "build_ios_deploy_runbook_report",
            ]
        ),
        "safety_contract": all(
            text in module_text
            for text in [
                '"provider_calls": False',
                '"writes_backend_env": False',
                '"writes_ios_deploy_config": False',
                '"xcode_or_signing": False',
                '"keychain_writes": False',
            ]
        ),
        "no_banned_commands": not any(
            banned in checked_text for banned in BANNED_WRITER_TEXT
        ),
    }


def _final_handoff_index_checks(
    *,
    module_text: str,
    module_exists: bool,
    cli_text: str,
    cli_exists: bool,
    makefile_text: str,
    makefile_exists: bool,
) -> dict[str, bool]:
    checked_text = "\n".join([module_text, makefile_text])
    return {
        "module_exists": module_exists,
        "cli_command": cli_exists
        and "final-handoff-index" in cli_text
        and "build_final_handoff_index_report" in cli_text,
        "make_target": makefile_exists
        and FINAL_HANDOFF_INDEX_MAKE_TARGET in makefile_text
        and "myth_forge_api.cli final-handoff-index" in makefile_text,
        "output_path": FINAL_HANDOFF_INDEX_OUTPUT in makefile_text,
        "composes_handoff_reports": all(
            text in module_text
            for text in [
                "build_final_configured_preflight_report",
                "final_handoff_index_report",
                "source_reports",
                "operator_sequence",
                "lanes_by_id",
            ]
        ),
        "source_freshness": all(
            text in module_text
            for text in [
                "_freshness_report",
                "_freshness_summary",
                "stale_report",
                "checked_against",
            ]
        ),
        "safety_contract": all(
            text in module_text
            for text in [
                '"commands_run": False',
                '"provider_calls": False',
                '"writes_backend_env": False',
                '"writes_ios_deploy_config": False',
                '"xcode_or_signing": False',
                '"keychain_writes": False',
            ]
        ),
        "no_banned_commands": not any(
            banned in checked_text for banned in BANNED_WRITER_TEXT
        ),
    }


def _ios_device_launch_certificate_checks(
    *,
    module_text: str,
    module_exists: bool,
    cli_text: str,
    cli_exists: bool,
    makefile_text: str,
    makefile_exists: bool,
) -> dict[str, bool]:
    checked_text = "\n".join([module_text, makefile_text])
    return {
        "module_exists": module_exists,
        "cli_command": cli_exists
        and "ios-device-launch-certificate" in cli_text
        and "build_ios_device_launch_certificate_report" in cli_text,
        "make_target": makefile_exists
        and IOS_DEVICE_LAUNCH_CERTIFICATE_MAKE_TARGET in makefile_text
        and "myth_forge_api.cli ios-device-launch-certificate" in makefile_text,
        "output_path": IOS_DEVICE_LAUNCH_CERTIFICATE_OUTPUT in makefile_text,
        "composes_device_reports": all(
            text in module_text
            for text in [
                "build_final_handoff_index_report",
                "build_ios_deploy_runbook_report",
                "build_final_demo_launch_report",
                "ios_device_launch_certificate_report",
                "device_gates",
                "operator_sequence",
            ]
        ),
        "safety_contract": all(
            text in module_text
            for text in [
                '"commands_run": False',
                '"provider_calls": False',
                '"writes_backend_env": False',
                '"writes_ios_deploy_config": False',
                '"xcode_or_signing": False',
                '"keychain_writes": False',
            ]
        ),
        "no_banned_commands": not any(
            banned in checked_text for banned in BANNED_WRITER_TEXT
        ),
    }


def _ios_device_launch_rehearsal_checks(
    *,
    module_text: str,
    module_exists: bool,
    readiness_text: str,
    readiness_exists: bool,
    script_text: str,
    script_exists: bool,
    cli_text: str,
    cli_exists: bool,
    makefile_text: str,
    makefile_exists: bool,
) -> dict[str, bool]:
    checked_text = "\n".join([module_text, readiness_text, script_text, makefile_text])
    rehearsal_command_index = script_text.find(
        "myth_forge_api.cli ios-device-launch-rehearsal"
    )
    final_launch_sync_index = script_text.find("myth_forge_api.cli final-demo-launch")
    return {
        "module_exists": module_exists,
        "readiness_exists": readiness_exists,
        "script_exists": script_exists,
        "cli_command": cli_exists
        and "ios-device-launch-rehearsal" in cli_text
        and "build_ios_device_launch_rehearsal_report" in cli_text,
        "make_target": makefile_exists
        and IOS_DEVICE_LAUNCH_REHEARSAL_MAKE_TARGET in makefile_text
        and IOS_DEVICE_LAUNCH_REHEARSAL_SCRIPT_PATH in makefile_text,
        "output_path": IOS_DEVICE_LAUNCH_REHEARSAL_OUTPUT in script_text,
        "composes_rehearsal_reports": all(
            text in module_text
            for text in [
                "ios_device_launch_rehearsal_report",
                "LOCAL_REPORT_SOURCES",
                "REHEARSAL_REPORT_SOURCES",
                "final_configured_preflight",
                "final_handoff_index",
                "ios_device_launch_certificate",
                "operator_actions",
            ]
        ),
        "safety_contract": all(
            text in module_text
            for text in [
                '"report_builder_commands_run": False',
                '"make_wrapper_runs_commands": True',
                '"writes_ignored_reports": True',
                '"provider_calls": False',
                '"writes_backend_env": False',
                '"writes_ios_deploy_config": False',
                '"xcode_or_signing": False',
                '"keychain_writes": False',
            ]
        ),
        "script_accepts_blocked_reports": all(
            text in script_text
            for text in [
                "run_report_command",
                '"$status" -eq 2',
                "accepted $label exit code",
                "final-configured-preflight",
                "final-handoff-index",
                "ios-device-launch-certificate",
                "ios-device-launch-rehearsal",
            ]
        ),
        "syncs_final_launch_after_rehearsal": all(
            text in script_text
            for text in [
                "final launch rehearsal sync",
                "myth_forge_api.cli final-demo-launch",
                "--mode local",
                FINAL_DEMO_LAUNCH_LOCAL_OUTPUT,
            ]
        )
        and rehearsal_command_index >= 0
        and final_launch_sync_index > rehearsal_command_index,
        "readiness_freshness": all(
            text in readiness_text
            for text in [
                "freshness",
                "_freshness_report",
                "ios_device_launch_rehearsal_freshness",
                "stale_report",
                "rerun make ios-device-launch-rehearsal",
            ]
        ),
        "source_freshness_propagation": all(
            text in checked_text
            for text in [
                "freshness_summary",
                "freshness_status",
                "freshness_classification",
            ]
        ),
        "no_banned_commands": not any(
            banned in checked_text for banned in BANNED_WRITER_TEXT
        ),
    }


def _final_rehearsal_local_checks(
    *,
    final_acceptance_script_text: str,
    final_acceptance_script_exists: bool,
    ios_deploy_runbook_script_text: str,
    ios_deploy_runbook_script_exists: bool,
    makefile_text: str,
    makefile_exists: bool,
) -> dict[str, bool]:
    checked_text = "\n".join(
        [final_acceptance_script_text, ios_deploy_runbook_script_text, makefile_text]
    )
    return {
        "final_acceptance_script_exists": final_acceptance_script_exists,
        "ios_deploy_runbook_script_exists": ios_deploy_runbook_script_exists,
        "final_acceptance_accepts_blocked_report": (
            'accepted final acceptance exit code $status' in final_acceptance_script_text
            and "final-acceptance-local.json" in final_acceptance_script_text
        ),
        "ios_deploy_runbook_accepts_blocked_report": (
            "accepted iOS deploy runbook exit code $status"
            in ios_deploy_runbook_script_text
            and "ios-deploy-runbook-local.json" in ios_deploy_runbook_script_text
        ),
        "make_targets": makefile_exists
        and FINAL_ACCEPTANCE_LOCAL_MAKE_TARGET in makefile_text
        and FINAL_REHEARSAL_LOCAL_MAKE_TARGET in makefile_text
        and IOS_DEPLOY_RUNBOOK_LOCAL_MAKE_TARGET in makefile_text
        and FINAL_ACCEPTANCE_LOCAL_SCRIPT_PATH in makefile_text
        and IOS_DEPLOY_RUNBOOK_LOCAL_SCRIPT_PATH in makefile_text
        and "backend-evaluate-local" in makefile_text
        and FINAL_DEMO_LAUNCH_MAKE_TARGET in makefile_text,
        "local_output_paths": FINAL_DEMO_LAUNCH_LOCAL_OUTPUT in makefile_text
        and "final-acceptance-local.json" in final_acceptance_script_text
        and "ios-deploy-runbook-local.json" in ios_deploy_runbook_script_text,
        "no_banned_commands": not any(
            banned in checked_text for banned in BANNED_WRITER_TEXT
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
