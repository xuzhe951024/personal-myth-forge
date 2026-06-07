from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from myth_forge_api.config import Settings, load_settings
from myth_forge_api.final_configured_preflight import (
    build_final_configured_preflight_report,
)

LOCAL_REPORT_SOURCES = [
    {
        "id": "three_d_evaluation",
        "path": "services/backend/.local/3d-evaluation-local.json",
        "command": "make backend-evaluate-3d",
    },
    {
        "id": "npc_agent_evaluation",
        "path": "services/backend/.local/npc-evaluation-local.json",
        "command": "make backend-evaluate-npc",
    },
    {
        "id": "final_acceptance_local",
        "path": "services/backend/.local/final-acceptance-local.json",
        "command": "make final-acceptance-local",
    },
    {
        "id": "final_demo_launch_local",
        "path": "services/backend/.local/final-demo-launch-local.json",
        "command": "make final-demo-launch",
    },
    {
        "id": "ios_deploy_runbook_local",
        "path": "services/backend/.local/ios-deploy-runbook-local.json",
        "command": "make ios-deploy-runbook-local",
    },
]
CONFIGURED_PREFLIGHT_SOURCE = {
    "id": "final_configured_preflight",
    "path": "services/backend/.local/final-configured-preflight.json",
    "command": "make final-configured-preflight",
}


@dataclass(frozen=True)
class FinalHandoffIndexResult:
    exit_code: int
    report: dict[str, Any]


def build_final_handoff_index_report(
    *,
    settings: Settings | None = None,
    repo_root: Path | str | None = None,
) -> FinalHandoffIndexResult:
    selected_settings = settings or load_settings()
    selected_repo_root = Path(repo_root) if repo_root is not None else _default_repo_root()
    local_sources = [
        _source_report(source=source, repo_root=selected_repo_root)
        for source in LOCAL_REPORT_SOURCES
    ]
    configured_preflight = build_final_configured_preflight_report(
        settings=selected_settings,
        repo_root=selected_repo_root,
    ).report
    configured_source = _configured_preflight_source(
        repo_root=selected_repo_root,
        computed_report=configured_preflight,
    )
    source_reports = [*local_sources, configured_source]
    lanes = _lanes(
        local_sources=local_sources,
        configured_preflight=configured_preflight,
    )
    status = _overall_status(lanes)
    report = {
        "kind": "final_handoff_index_report",
        "status": status,
        "summary": _summary(lanes),
        "lanes": lanes,
        "lanes_by_id": {lane["id"]: lane for lane in lanes},
        "source_reports": source_reports,
        "freshness_summary": _freshness_summary(source_reports),
        "operator_sequence": _operator_sequence(lanes),
        "commands": _commands(),
        "safety": _safety(),
    }
    sanitized = _sanitize_report(report, selected_repo_root)
    return FinalHandoffIndexResult(
        exit_code=0 if sanitized["status"] == "ready" else 2,
        report=sanitized,
    )


def _source_report(*, source: dict[str, str], repo_root: Path) -> dict[str, Any]:
    relative_path = source["path"]
    path = repo_root / relative_path
    freshness = _freshness_report(
        repo_root=repo_root,
        source_file=path,
        source_exists=path.exists(),
    )
    base = {
        "id": source["id"],
        "path": relative_path,
        "exists": path.exists(),
        "command": source["command"],
        "freshness": freshness,
    }
    if not path.exists():
        return {
            **base,
            "status": "missing",
            "kind": None,
            "classification": "missing_report",
        }
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {
            **base,
            "status": "blocked",
            "kind": None,
            "classification": "unreadable_report",
        }
    if not isinstance(payload, dict):
        return {
            **base,
            "status": "blocked",
            "kind": None,
            "classification": "invalid_report_shape",
        }
    status = _saved_report_status(payload)
    classification = "saved_report"
    if freshness["status"] == "stale":
        status = "blocked"
        classification = "stale_report"
    return {
        **base,
        "status": status,
        "kind": payload.get("kind"),
        "classification": classification,
    }


def _configured_preflight_source(
    *,
    repo_root: Path,
    computed_report: dict[str, Any],
) -> dict[str, Any]:
    source = CONFIGURED_PREFLIGHT_SOURCE
    path = repo_root / source["path"]
    return {
        "id": source["id"],
        "path": source["path"],
        "exists": path.exists(),
        "command": source["command"],
        "status": str(computed_report.get("status", "blocked")),
        "kind": computed_report.get("kind", "final_configured_preflight_report"),
        "classification": "computed_report",
    }


def _saved_report_status(payload: dict[str, Any]) -> str:
    kind = str(payload.get("kind", ""))
    if kind in {"three_d_evaluation_report", "npc_agent_evaluation_report"}:
        return "blocked" if _positive_int(payload.get("failed")) else "ready"
    if kind == "final_acceptance_report":
        summary = payload.get("summary", {})
        if isinstance(summary, dict) and (
            _positive_int(summary.get("blocked")) or _positive_int(summary.get("failed"))
        ):
            return "blocked"
        return _normalized_status(str(payload.get("overall_status", "ready")))
    if kind == "final_demo_launch_report":
        return _normalized_status(str(payload.get("overall_status", "ready")))
    if kind == "ios_deploy_runbook_report":
        return _normalized_status(str(payload.get("status", "ready")))
    return _normalized_status(str(payload.get("status", "ready")))


def _lanes(
    *,
    local_sources: list[dict[str, Any]],
    configured_preflight: dict[str, Any],
) -> list[dict[str, Any]]:
    local_status = _combined_lane_status([str(source["status"]) for source in local_sources])
    configured_status = str(configured_preflight.get("status", "blocked"))
    configured_launch_status = str(
        configured_preflight.get("configured_final_launch", {}).get(
            "overall_status",
            "blocked",
        )
    )
    device_deploy_status = str(
        configured_preflight.get("configured_ios_deploy_runbook", {}).get(
            "status",
            "blocked",
        )
    )
    return [
        _lane(
            lane_id="local_rehearsal",
            label="Local rehearsal",
            status=local_status,
            command="make final-rehearsal-local",
            required=True,
            notes=["Writes local/no-key saved reports for final launch review."],
        ),
        _lane(
            lane_id="configured_preflight",
            label="Configured preflight",
            status=configured_status,
            command="make final-configured-preflight",
            required=True,
            notes=["Reviews API/key and iOS handoff without live provider calls."],
        ),
        _lane(
            lane_id="configured_launch",
            label="Configured launch report",
            status=configured_launch_status,
            command=(
                "cd services/backend && uv run python -m myth_forge_api.cli "
                "final-demo-launch --mode configured --repo-root ../.. "
                "--output .local/final-demo-launch-configured.json"
            ),
            required=False,
            notes=["Read-only launch profile for the configured lane."],
        ),
        _lane(
            lane_id="device_deploy",
            label="Device deploy path",
            status=device_deploy_status,
            command="make mobile-deploy-preflight",
            required=False,
            notes=["Backend LAN server, deploy preflight, and Xcode remain operator-run."],
        ),
        _lane(
            lane_id="live_acceptance",
            label="Configured live acceptance",
            status="live",
            command=_configured_acceptance_command(),
            required=False,
            requires_consent=True,
            notes=["May call live providers and spend provider credits."],
        ),
    ]


def _lane(
    *,
    lane_id: str,
    label: str,
    status: str,
    command: str,
    required: bool,
    notes: list[str],
    requires_consent: bool = False,
) -> dict[str, Any]:
    return {
        "id": lane_id,
        "label": label,
        "status": _normalized_status(status),
        "command": command,
        "required": required,
        "requires_consent": requires_consent,
        "notes": notes,
    }


def _operator_sequence(lanes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {lane["id"]: lane for lane in lanes}
    sequence = [
        _sequence_step(
            "local_rehearsal",
            "Run local rehearsal",
            by_id["local_rehearsal"]["status"],
            "make final-rehearsal-local",
            "no-key local report generation",
        ),
        _sequence_step(
            "configured_preflight",
            "Run configured preflight",
            by_id["configured_preflight"]["status"],
            "make final-configured-preflight",
            "read-only API/key and iOS deploy review",
        ),
        _sequence_step(
            "final_handoff_index",
            "Refresh final handoff index",
            "ready",
            "make final-handoff-index",
            "writes this ignored JSON index",
        ),
        _sequence_step(
            "backend_device_server",
            "Start backend on LAN",
            "manual",
            "make backend-device-demo",
            "operator-run backend server for the iPhone",
        ),
        _sequence_step(
            "mobile_deploy_preflight",
            "Run mobile deploy preflight",
            by_id["device_deploy"]["status"],
            "make mobile-deploy-preflight",
            "validates iPhone-reachable backend URL and local deploy config",
        ),
        _sequence_step(
            "configured_final_acceptance",
            "Run configured final acceptance",
            "live",
            _configured_acceptance_command(),
            "requires explicit live provider cost consent",
            requires_consent=True,
        ),
    ]
    return sequence


def _sequence_step(
    step_id: str,
    label: str,
    status: str,
    command: str,
    purpose: str,
    *,
    requires_consent: bool = False,
) -> dict[str, Any]:
    return {
        "id": step_id,
        "label": label,
        "status": _normalized_status(status),
        "command": command,
        "purpose": purpose,
        "requires_consent": requires_consent,
    }


def _commands() -> list[str]:
    return [
        "make final-rehearsal-local",
        "make final-configured-preflight",
        "make final-handoff-index",
        "make backend-device-demo",
        "make mobile-deploy-preflight",
        (
            "cd services/backend && uv run python -m myth_forge_api.cli "
            "final-demo-launch --mode configured --repo-root ../.. "
            "--output .local/final-demo-launch-configured.json"
        ),
        _configured_acceptance_command(),
    ]


def _configured_acceptance_command() -> str:
    return (
        "cd services/backend && uv run python -m myth_forge_api.cli "
        "final-acceptance --profile quick --provider-mode configured "
        "--require-real-core --allow-live-provider-calls --repo-root ../.. "
        "--output .local/final-acceptance-configured.json"
    )


def _overall_status(lanes: list[dict[str, Any]]) -> str:
    required_statuses = [str(lane["status"]) for lane in lanes if lane["required"]]
    if any(status in {"missing", "blocked"} for status in required_statuses):
        return "blocked"
    return "ready"


def _summary(lanes: list[dict[str, Any]]) -> dict[str, int]:
    statuses = ["ready", "missing", "blocked", "manual", "optional", "partial", "live"]
    return {
        status: sum(1 for lane in lanes if lane["status"] == status)
        for status in statuses
    }


def _combined_lane_status(statuses: list[str]) -> str:
    normalized = [_normalized_status(status) for status in statuses]
    if "missing" in normalized:
        return "missing"
    if "blocked" in normalized:
        return "blocked"
    return "ready"


def _normalized_status(status: str) -> str:
    if status in {"ready", "missing", "blocked", "manual", "optional", "partial", "live"}:
        return status
    if status in {"passed", "succeeded"}:
        return "ready"
    if status in {"failed", "error"}:
        return "blocked"
    return "blocked"


def _positive_int(value: Any) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, int) and value > 0:
        return value
    return 0


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


def _iso_timestamp(epoch: float | None) -> str | None:
    if epoch is None:
        return None
    return (
        datetime.fromtimestamp(epoch, tz=timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _freshness_summary(source_reports: list[dict[str, Any]]) -> dict[str, int]:
    statuses = ["fresh", "stale", "unknown"]
    return {
        status: sum(
            1
            for source in source_reports
            if source.get("freshness", {}).get("status") == status
        )
        for status in statuses
    }


def _safety() -> dict[str, bool]:
    return {
        "commands_run": False,
        "provider_calls": False,
        "writes_local_config": False,
        "writes_backend_env": False,
        "writes_ios_deploy_config": False,
        "global_mutation": False,
        "xcode_or_signing": False,
        "keychain_writes": False,
        "provider_secrets_in_report": False,
        "raw_media_in_report": False,
        "payment_links_in_report": False,
        "local_paths_in_report": False,
    }


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


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
        r"data:[A-Za-z0-9.+-]+/[A-Za-z0-9+/=_-]+",
        r"local-capture://[^\s,;\"']+",
        r"file://[^\s,;\"']+",
        r"https?://pay\.[^\s,;\"']+",
        r"https?://checkout\.[^\s,;\"']+",
        r"checkout_url",
        r"raw_email:[^\n\r]+",
        r"raw_calendar:[^\n\r]+",
        r"private_message:[^\n\r]+",
        r"raw_context:[^\n\r]+",
        r"message_body:[^\n\r]+",
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
