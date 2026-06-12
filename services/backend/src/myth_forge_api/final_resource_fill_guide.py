from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from myth_forge_api.final_resource_requirements import (
    build_final_resource_requirements_report,
)

COMMANDS = [
    "make final-resource-requirements",
    "make final-resource-apply-preview",
    "make final-apply-resources",
    "make final-local-report-refresh",
]


@dataclass(frozen=True)
class FinalResourceFillGuideResult:
    exit_code: int
    report: dict[str, Any]


def build_final_resource_fill_guide_report(
    *,
    repo_root: Path | str | None = None,
    resources_file: Path | str | None = None,
) -> FinalResourceFillGuideResult:
    selected_repo_root = Path(repo_root) if repo_root is not None else _default_repo_root()
    selected_resources_file = Path(resources_file) if resources_file is not None else None
    requirements_result = build_final_resource_requirements_report(
        repo_root=selected_repo_root,
        resources_file=selected_resources_file,
    )
    requirements_report = requirements_result.report
    requirements = [
        item
        for item in requirements_report.get("requirements", [])
        if isinstance(item, dict)
    ]
    required_inputs = _required_inputs(requirements)
    optional_inputs = _optional_inputs(requirements)
    configured_inputs = _configured_inputs(requirements)
    first_blocker = _first_blocker(required_inputs)
    status = "blocked" if required_inputs else "ready"
    report = {
        "kind": "final_resource_fill_guide_report",
        "status": status,
        "summary": {
            "required_inputs": len(required_inputs),
            "optional_inputs": len(optional_inputs),
            "configured_inputs": len(configured_inputs),
            "secret_inputs": sum(1 for item in requirements if item.get("secret")),
        },
        "required_inputs": required_inputs,
        "optional_inputs": optional_inputs,
        "configured_inputs": configured_inputs,
        "first_blocker": first_blocker,
        "next_action": _next_action(first_blocker),
        "commands": COMMANDS,
        "markdown": _markdown(
            status=status,
            required_inputs=required_inputs,
            optional_inputs=optional_inputs,
            configured_inputs=configured_inputs,
        ),
        "source_reports": {
            "final_resource_requirements": _source_summary(requirements_report),
        },
        "safety": _safety(),
    }
    sanitized = _sanitize_report(report, selected_repo_root)
    return FinalResourceFillGuideResult(
        exit_code=0 if sanitized["status"] == "ready" else 2,
        report=sanitized,
    )


def _required_inputs(requirements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        _guide_item(item)
        for item in requirements
        if item.get("required") and item.get("status") in {"missing", "blocked"}
    ]


def _optional_inputs(requirements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        _guide_item(item)
        for item in requirements
        if not item.get("required") and item.get("status") in {"missing", "optional", "blocked"}
    ]


def _configured_inputs(requirements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        _guide_item(item)
        for item in requirements
        if item.get("status") == "ready"
    ]


def _guide_item(item: dict[str, Any]) -> dict[str, Any]:
    secret = bool(item.get("secret"))
    return {
        "id": str(item.get("id", "")),
        "label": str(item.get("label", "")),
        "domain": str(item.get("domain", "")),
        "status": str(item.get("status", "")),
        "classification": str(item.get("classification", "")),
        "required": bool(item.get("required")),
        "secret": secret,
        "display_value": "<secret: fill locally>" if secret else "<fill locally>",
        "input_source": str(item.get("input_source", item.get("destination", ""))),
        "write_destination": str(item.get("write_destination", item.get("destination", ""))),
        "apply_command": str(item.get("apply_command", "make final-apply-resources")),
        "validation_command": str(item.get("validation_command", "")),
        "fill_action": str(item.get("fill_action", "")),
        "notes": str(item.get("notes", "")),
        "unblocks": list(item.get("unblocks", [])),
    }


def _markdown(
    *,
    status: str,
    required_inputs: list[dict[str, Any]],
    optional_inputs: list[dict[str, Any]],
    configured_inputs: list[dict[str, Any]],
) -> str:
    lines = [
        "# Final Resource Fill Guide",
        "",
        f"Status: {status}",
        "",
        "Fill source: `services/backend/.local/final-resources.env`",
        "",
        "## Required Inputs",
        "",
    ]
    lines.extend(_markdown_rows(required_inputs, empty="No required inputs remain."))
    lines.extend(["", "## Optional Inputs", ""])
    lines.extend(_markdown_rows(optional_inputs, empty="No optional inputs remain."))
    lines.extend(["", "## Configured Inputs", ""])
    lines.extend(_markdown_rows(configured_inputs, empty="No configured inputs yet."))
    lines.extend(["", "## Command Order", ""])
    for index, command in enumerate(COMMANDS, start=1):
        lines.append(f"{index}. `{command}`")
    lines.append("")
    return "\n".join(lines)


def _markdown_rows(items: list[dict[str, Any]], *, empty: str) -> list[str]:
    if not items:
        return [empty]
    rows: list[str] = []
    for item in items:
        rows.extend(
            [
                f"- `{item['id']}`: {item['display_value']}",
                f"  - Input: `{item['input_source']}`",
                f"  - Writes: `{item['write_destination']}`",
                f"  - Validate: `{item['validation_command']}`",
                f"  - Unblocks: {', '.join(str(value) for value in item['unblocks'])}",
            ]
        )
    return rows


def _source_summary(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": report.get("kind", "unknown"),
        "status": report.get("status", "unknown"),
        "summary": report.get("summary", {}),
    }


def _first_blocker(required_inputs: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not required_inputs:
        return None
    item = required_inputs[0]
    return {
        "id": item["id"],
        "label": item["label"],
        "status": item["status"],
        "classification": item["classification"],
        "command": item["fill_action"],
        "detail": item["notes"],
        "domain": item["domain"],
        "input_source": item["input_source"],
        "write_destination": item["write_destination"],
        "validation_command": item["validation_command"],
    }


def _next_action(first_blocker: dict[str, Any] | None) -> dict[str, Any] | None:
    if first_blocker is None:
        return None
    return {**first_blocker, "source": "first_blocker"}


def _safety() -> dict[str, bool]:
    return {
        "provider_secrets_in_report": False,
        "local_paths_in_report": False,
        "writes_backend_env": False,
        "writes_ios_deploy_config": False,
        "writes_final_resources": False,
        "live_provider_calls": False,
        "global_mutation": False,
    }


def _sanitize_report(report: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    return json.loads(json.dumps(_sanitize_value(report, repo_root)))


def _sanitize_value(value: Any, repo_root: Path) -> Any:
    if isinstance(value, str):
        return _safe_text(value, repo_root)
    if isinstance(value, list):
        return [_sanitize_value(item, repo_root) for item in value]
    if isinstance(value, dict):
        return {key: _sanitize_value(item, repo_root) for key, item in value.items()}
    return value


def _safe_text(message: str, repo_root: Path) -> str:
    sanitized = message
    patterns = [
        r"sk-[A-Za-z0-9._-]+",
        r"meshy-secret-[A-Za-z0-9._-]+",
        r"Bearer\s+[A-Za-z0-9._~+/\-=:-]+",
        r"api[_-]?key\s*[=:]\s*[^\s,;\"']+",
        r"file://[^\s,;\"']+",
        r"/private/[^\s,;\"']+",
        r"/tmp/[^\s,;\"']+",
        r"/Users/[^\s,;\"']+",
        r"https?://10\.[^\s,;\"'`]+",
        r"https?://192\.168\.[^\s,;\"'`]+",
        r"https?://172\.(?:1[6-9]|2[0-9]|3[01])\.[^\s,;\"'`]+",
    ]
    for pattern in patterns:
        sanitized = re.sub(pattern, "[redacted]", sanitized, flags=re.IGNORECASE)
    root_text = str(repo_root)
    if root_text:
        sanitized = sanitized.replace(root_text, "[repo-root]")
    home_text = str(Path.home())
    if home_text:
        sanitized = sanitized.replace(home_text, "[home]")
    return sanitized


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parents[4]
