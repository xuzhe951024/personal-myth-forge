from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_ACCEPTANCE_PATH = Path("services/backend/.local/final-acceptance-local.json")
LOCAL_FINAL_ACCEPTANCE_COMMAND = (
    "cd services/backend && uv run python -m myth_forge_api.cli "
    "final-acceptance --profile quick --provider-mode local --repo-root ../.. "
    "--output .local/final-acceptance-local.json"
)


@dataclass(frozen=True)
class FinalAcceptanceReadinessResult:
    exit_code: int
    report: dict[str, Any]


def build_final_acceptance_readiness_report(
    *,
    repo_root: Path | str | None = None,
    acceptance_file: Path | str | None = None,
) -> FinalAcceptanceReadinessResult:
    selected_repo_root = Path(repo_root) if repo_root is not None else _default_repo_root()
    selected_acceptance_file = (
        Path(acceptance_file)
        if acceptance_file is not None
        else selected_repo_root / DEFAULT_ACCEPTANCE_PATH
    )
    source_file = {
        "path": _path_label(path=selected_acceptance_file, repo_root=selected_repo_root),
        "exists": selected_acceptance_file.exists(),
    }
    if not selected_acceptance_file.exists():
        report = _base_report(
            repo_root=selected_repo_root,
            status="missing",
            source_file=source_file,
            summary=_empty_summary(),
            blockers=[],
            operator_actions=[
                "run local final acceptance and write services/backend/.local/final-acceptance-local.json"
            ],
        )
        return FinalAcceptanceReadinessResult(exit_code=2, report=report)

    try:
        saved_report = json.loads(selected_acceptance_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        report = _invalid_report(
            repo_root=selected_repo_root,
            source_file=source_file,
            classification="unreadable_report",
            detail="Saved final acceptance report is not valid JSON.",
        )
        return FinalAcceptanceReadinessResult(exit_code=2, report=report)

    if not isinstance(saved_report, dict):
        report = _invalid_report(
            repo_root=selected_repo_root,
            source_file=source_file,
            classification="invalid_report_shape",
            detail="Saved final acceptance report must be a JSON object.",
        )
        return FinalAcceptanceReadinessResult(exit_code=2, report=report)

    summary = _summary(saved_report.get("summary"))
    checks = saved_report.get("checks", [])
    if not isinstance(checks, list):
        checks = []
    blockers = [
        _blocker(check)
        for check in checks
        if isinstance(check, dict) and check.get("status") in {"blocked", "failed"}
    ]
    status = "ready" if summary["blocked"] == 0 and summary["failed"] == 0 and not blockers else "blocked"
    report = _base_report(
        repo_root=selected_repo_root,
        status=status,
        source_file=source_file,
        summary=summary,
        blockers=blockers,
        operator_actions=_operator_actions(status=status, blockers=blockers),
    )
    return FinalAcceptanceReadinessResult(
        exit_code=0 if status == "ready" else 2,
        report=report,
    )


def _invalid_report(
    *,
    repo_root: Path,
    source_file: dict[str, Any],
    classification: str,
    detail: str,
) -> dict[str, Any]:
    return _base_report(
        repo_root=repo_root,
        status="blocked",
        source_file=source_file,
        summary=_empty_summary(),
        blockers=[
            {
                "id": "final_acceptance_file",
                "label": "Final acceptance file",
                "status": "failed",
                "classification": classification,
                "command": LOCAL_FINAL_ACCEPTANCE_COMMAND,
                "detail": detail,
            }
        ],
        operator_actions=[
            "regenerate services/backend/.local/final-acceptance-local.json"
        ],
    )


def _base_report(
    *,
    repo_root: Path,
    status: str,
    source_file: dict[str, Any],
    summary: dict[str, int],
    blockers: list[dict[str, Any]],
    operator_actions: list[str],
) -> dict[str, Any]:
    report = {
        "kind": "final_acceptance_readiness_report",
        "status": status,
        "source_file": source_file,
        "summary": summary,
        "blockers": blockers,
        "operator_actions": operator_actions,
        "safety": {
            "commands_run": False,
            "provider_calls": False,
            "global_mutation": False,
            "provider_secrets_in_report": False,
            "raw_media_in_report": False,
            "payment_links_in_report": False,
            "local_paths_in_report": False,
        },
    }
    return _sanitize_report(report, repo_root)


def _summary(raw_summary: Any) -> dict[str, int]:
    if not isinstance(raw_summary, dict):
        return _empty_summary()
    return {
        "passed": _non_negative_int(raw_summary.get("passed")),
        "blocked": _non_negative_int(raw_summary.get("blocked")),
        "failed": _non_negative_int(raw_summary.get("failed")),
        "skipped": _non_negative_int(raw_summary.get("skipped")),
    }


def _empty_summary() -> dict[str, int]:
    return {"passed": 0, "blocked": 0, "failed": 0, "skipped": 0}


def _non_negative_int(value: Any) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, int) and value > 0:
        return value
    return 0


def _blocker(check: dict[str, Any]) -> dict[str, Any]:
    command = check.get("command", "")
    if isinstance(command, list):
        command_text = " ".join(str(item) for item in command)
    else:
        command_text = str(command)
    return {
        "id": str(check.get("id", "unknown_check")),
        "label": str(check.get("label", "Unknown check")),
        "status": str(check.get("status", "blocked")),
        "classification": str(check.get("classification", "blocked")),
        "command": command_text,
        "detail": _detail(check),
    }


def _detail(check: dict[str, Any]) -> str:
    for key in ("stderr_tail", "stdout_tail", "error"):
        value = check.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    classification = check.get("classification")
    if isinstance(classification, str) and classification:
        return classification
    return "Final acceptance check needs attention."


def _operator_actions(*, status: str, blockers: list[dict[str, Any]]) -> list[str]:
    if status == "ready":
        return ["final acceptance is ready"]
    actions: list[str] = []
    for blocker in blockers:
        blocker_id = blocker["id"]
        classification = blocker["classification"]
        if (
            blocker_id == "mobile_deploy_preflight"
            and classification == "blocked_by_local_ios_backend_health"
        ):
            actions.append("start backend-device-demo and rerun mobile deploy preflight")
        elif blocker_id == "mobile_deploy_preflight":
            actions.append("provide iOS deploy config and rerun mobile deploy preflight")
        elif blocker_id == "mobile_xcode_build":
            actions.append("resolve Xcode build gate outside the app")
        elif blocker["status"] == "failed":
            actions.append(f"fix {blocker_id}: {blocker['label']}")
        elif blocker["command"]:
            actions.append(f"unblock {blocker_id}: {blocker['command']}")
        else:
            actions.append(f"unblock {blocker_id}: {blocker['label']}")
    return _dedupe(actions)


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
        r"Bearer\s+[A-Za-z0-9._~+/\-=:-]+",
        r"api[_-]?key\s*[=:]\s*[^\s,;\"']+",
        r"data:[A-Za-z0-9.+-]+/[A-Za-z0-9.+-]+;base64,[A-Za-z0-9+/=_-]+",
        r"https?://pay\.[^\s,;\"']+",
        r"https?://checkout\.[^\s,;\"']+",
        r"checkout_url",
        r"file://[^\s,;\"']+",
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


def _path_label(*, path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return "[external-final-acceptance-file]"


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parents[4]
