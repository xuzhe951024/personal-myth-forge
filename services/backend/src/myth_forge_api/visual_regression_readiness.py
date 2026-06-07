from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_VISUAL_REGRESSION_REPORT_PATH = Path(
    "services/backend/.local/visual-regression-local.json"
)
VISUAL_REGRESSION_LOCAL_COMMAND = "make visual-regression-local"
VISUAL_REGRESSION_RERUN_ACTION = (
    "rerun make visual-regression-local to regenerate "
    "services/backend/.local/visual-regression-local.json for the current git revision"
)


@dataclass(frozen=True)
class VisualRegressionReadinessResult:
    exit_code: int
    report: dict[str, Any]


def build_visual_regression_readiness_report(
    *,
    repo_root: Path | str | None = None,
    report_file: Path | str | None = None,
) -> VisualRegressionReadinessResult:
    selected_repo_root = Path(repo_root) if repo_root is not None else _default_repo_root()
    selected_report_file = (
        Path(report_file)
        if report_file is not None
        else selected_repo_root / DEFAULT_VISUAL_REGRESSION_REPORT_PATH
    )
    source_file = {
        "path": _path_label(path=selected_report_file, repo_root=selected_repo_root),
        "exists": selected_report_file.exists(),
    }
    freshness = _freshness_report(
        repo_root=selected_repo_root,
        source_file=selected_report_file,
        source_exists=selected_report_file.exists(),
    )
    if not selected_report_file.exists():
        return VisualRegressionReadinessResult(
            exit_code=2,
            report=_base_report(
                repo_root=selected_repo_root,
                status="missing",
                source_file=source_file,
                freshness=freshness,
                summary=_empty_summary(),
                artifacts=[],
                blockers=[],
                operator_actions=[
                    "run make visual-regression-local to write "
                    "services/backend/.local/visual-regression-local.json"
                ],
            ),
        )

    try:
        saved_report = json.loads(selected_report_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _blocked_result(
            repo_root=selected_repo_root,
            source_file=source_file,
            freshness=freshness,
            classification="unreadable_report",
            detail="Saved visual regression report is not valid JSON.",
        )

    if not isinstance(saved_report, dict):
        return _blocked_result(
            repo_root=selected_repo_root,
            source_file=source_file,
            freshness=freshness,
            classification="invalid_report_shape",
            detail="Saved visual regression report must be a JSON object.",
        )

    if saved_report.get("kind") != "visual_regression_report":
        return _blocked_result(
            repo_root=selected_repo_root,
            source_file=source_file,
            freshness=freshness,
            classification="wrong_report_kind",
            detail="Saved report is not a visual_regression_report.",
        )

    summary = _summary(saved_report.get("summary"))
    artifacts = _artifacts(saved_report.get("artifacts"))
    blocker = _readiness_blocker(
        saved_report=saved_report,
        summary=summary,
        artifacts=artifacts,
    )
    blockers = [] if blocker is None else [blocker]
    status = "ready" if blocker is None else "blocked"
    operator_actions: list[str] = []
    if blocker is not None:
        operator_actions.append("rerun make visual-regression-local and review failed artifacts")
    if freshness["status"] == "stale":
        status = "blocked"
        blockers.insert(0, _freshness_blocker(freshness))
        operator_actions = [VISUAL_REGRESSION_RERUN_ACTION, *operator_actions]

    return VisualRegressionReadinessResult(
        exit_code=0 if status == "ready" else 2,
        report=_base_report(
            repo_root=selected_repo_root,
            status=status,
            source_file=source_file,
            freshness=freshness,
            summary=summary,
            artifacts=artifacts,
            blockers=blockers,
            operator_actions=_dedupe(operator_actions),
        ),
    )


def _blocked_result(
    *,
    repo_root: Path,
    source_file: dict[str, Any],
    freshness: dict[str, Any],
    classification: str,
    detail: str,
) -> VisualRegressionReadinessResult:
    return VisualRegressionReadinessResult(
        exit_code=2,
        report=_base_report(
            repo_root=repo_root,
            status="blocked",
            source_file=source_file,
            freshness=freshness,
            summary=_empty_summary(),
            artifacts=[],
            blockers=[
                {
                    "id": "visual_regression_file",
                    "label": "Visual regression file",
                    "status": "failed",
                    "classification": classification,
                    "command": VISUAL_REGRESSION_LOCAL_COMMAND,
                    "detail": detail,
                }
            ],
            operator_actions=[VISUAL_REGRESSION_RERUN_ACTION],
        ),
    )


def _base_report(
    *,
    repo_root: Path,
    status: str,
    source_file: dict[str, Any],
    freshness: dict[str, Any],
    summary: dict[str, int],
    artifacts: list[dict[str, Any]],
    blockers: list[dict[str, Any]],
    operator_actions: list[str],
) -> dict[str, Any]:
    report = {
        "kind": "visual_regression_readiness_report",
        "status": status,
        "source_file": source_file,
        "freshness": freshness,
        "summary": summary,
        "artifacts": artifacts,
        "blockers": blockers,
        "operator_actions": operator_actions,
        "commands": [
            VISUAL_REGRESSION_LOCAL_COMMAND,
            (
                "cd services/backend && uv run python -m myth_forge_api.cli "
                "visual-regression --repo-root ../.. "
                "--output .local/visual-regression-local.json"
            ),
        ],
        "safety": {
            "commands_run": False,
            "provider_calls": False,
            "live_provider_calls": False,
            "global_mutation": False,
            "xcode_or_signing": False,
            "keychain_writes": False,
            "provider_secrets_in_report": False,
            "raw_private_context_in_report": False,
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
        "failed": _non_negative_int(raw_summary.get("failed")),
    }


def _empty_summary() -> dict[str, int]:
    return {"passed": 0, "failed": 0}


def _artifacts(raw_artifacts: Any) -> list[dict[str, Any]]:
    if not isinstance(raw_artifacts, list):
        return []
    artifacts: list[dict[str, Any]] = []
    for raw_artifact in raw_artifacts:
        if not isinstance(raw_artifact, dict):
            continue
        artifact = {
            "id": str(raw_artifact.get("id", "unknown_artifact")),
            "status": _normalized_visual_status(str(raw_artifact.get("status", "failed"))),
        }
        html_path = raw_artifact.get("html_path")
        png_path = raw_artifact.get("png_path")
        notes_path = raw_artifact.get("notes_path")
        if isinstance(html_path, str):
            artifact["html_path"] = html_path
        if isinstance(png_path, str):
            artifact["png_path"] = png_path
        if isinstance(notes_path, str):
            artifact["notes_path"] = notes_path
        artifacts.append(artifact)
    return artifacts[:10]


def _readiness_blocker(
    *,
    saved_report: dict[str, Any],
    summary: dict[str, int],
    artifacts: list[dict[str, Any]],
) -> dict[str, Any] | None:
    if str(saved_report.get("status")) != "passed" or summary["failed"] > 0:
        return _blocker(
            classification="visual_regression_failed",
            detail=_failed_detail(saved_report),
        )
    if summary["passed"] <= 0:
        return _blocker(
            classification="empty_pass_count",
            detail="Visual regression report has no passed artifacts.",
        )
    failed_artifacts = [
        artifact for artifact in artifacts if artifact.get("status") != "passed"
    ]
    if failed_artifacts:
        return _blocker(
            classification="visual_regression_failed",
            detail=f"{failed_artifacts[0]['id']}: artifact status {failed_artifacts[0]['status']}",
        )
    return None


def _blocker(*, classification: str, detail: str) -> dict[str, Any]:
    return {
        "id": "visual_regression",
        "label": "Visual regression",
        "status": "failed",
        "classification": classification,
        "command": VISUAL_REGRESSION_LOCAL_COMMAND,
        "detail": detail,
    }


def _failed_detail(saved_report: dict[str, Any]) -> str:
    artifacts = saved_report.get("artifacts")
    if isinstance(artifacts, list):
        for artifact in artifacts:
            if not isinstance(artifact, dict):
                continue
            if artifact.get("status") != "failed":
                continue
            artifact_id = str(artifact.get("id", "unknown_artifact"))
            checks = artifact.get("checks")
            if isinstance(checks, dict):
                for check_id, check in checks.items():
                    if not isinstance(check, dict) or check.get("status") != "failed":
                        continue
                    return f"{artifact_id}: {check_id} {json.dumps(check)}"
            return f"{artifact_id}: artifact failed."
    return "Visual regression report contains failed artifacts."


def _freshness_report(
    *,
    repo_root: Path,
    source_file: Path,
    source_exists: bool,
) -> dict[str, Any]:
    if not source_exists:
        return _freshness_payload(
            status="unknown",
            classification="source_missing",
            source_modified_at=None,
            git_metadata=None,
        )
    source_modified_at = source_file.stat().st_mtime
    git_metadata = _git_head_metadata(repo_root)
    if git_metadata is None:
        return _freshness_payload(
            status="unknown",
            classification="git_unavailable",
            source_modified_at=source_modified_at,
            git_metadata=None,
        )
    freshness_status = (
        "stale"
        if source_modified_at < git_metadata["committed_at_epoch"]
        else "fresh"
    )
    return _freshness_payload(
        status=freshness_status,
        classification="stale_report" if freshness_status == "stale" else "fresh_report",
        source_modified_at=source_modified_at,
        git_metadata=git_metadata,
    )


def _git_head_metadata(repo_root: Path) -> dict[str, Any] | None:
    try:
        revision = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "--short", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            timeout=2,
        ).stdout.strip()
        committed_at = subprocess.run(
            ["git", "-C", str(repo_root), "log", "-1", "--format=%ct", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            timeout=2,
        ).stdout.strip()
    except (subprocess.SubprocessError, OSError):
        return None
    try:
        committed_at_epoch = float(committed_at)
    except ValueError:
        return None
    return {
        "revision": revision or None,
        "committed_at_epoch": committed_at_epoch,
    }


def _freshness_payload(
    *,
    status: str,
    classification: str,
    source_modified_at: float | None,
    git_metadata: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "status": status,
        "classification": classification,
        "checked_against": "git_head",
        "source_modified_at": _iso_timestamp(source_modified_at),
        "current_revision": None if git_metadata is None else git_metadata["revision"],
        "current_revision_committed_at": None
        if git_metadata is None
        else _iso_timestamp(git_metadata["committed_at_epoch"]),
    }


def _freshness_blocker(freshness: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": "visual_regression_freshness",
        "label": "Visual regression freshness",
        "status": "failed",
        "classification": "stale_report",
        "command": VISUAL_REGRESSION_LOCAL_COMMAND,
        "detail": (
            "Visual regression report is older than current git revision "
            f"{freshness.get('current_revision') or 'unknown'}."
        ),
    }


def _iso_timestamp(epoch: float | None) -> str | None:
    if epoch is None:
        return None
    return (
        datetime.fromtimestamp(epoch, tz=timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _normalized_visual_status(status: str) -> str:
    if status in {"passed", "failed"}:
        return status
    if status in {"ready", "succeeded"}:
        return "passed"
    return "failed"


def _non_negative_int(value: Any) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, int) and value > 0:
        return value
    return 0


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


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
        r"Authorization\s*[=:]\s*Bearer\s+[A-Za-z0-9._~+/\-=:-]+",
        r"Bearer\s+[A-Za-z0-9._~+/\-=:-]+",
        r"api[_-]?key\s*[=:]\s*[^\s,;\"']+",
        r"data:[A-Za-z0-9.+-]+/[A-Za-z0-9.+-]+;base64,[A-Za-z0-9+/=_-]+",
        r"local-capture://[^\s,;\"']+",
        r"file://[^\s,;\"']+",
        r"https?://pay\.[^\s,;\"']+",
        r"https?://checkout\.[^\s,;\"']+",
        r"checkout_url",
        r"raw_context:[^\n\r]+",
        r"raw_private_context:[^\n\r]+",
        r"private_message:[^\n\r]+",
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
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return "[external-path]"


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parents[3]
