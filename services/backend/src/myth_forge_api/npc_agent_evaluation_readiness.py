from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_NPC_EVALUATION_PATH = Path("services/backend/.local/npc-evaluation-local.json")
LOCAL_NPC_EVALUATION_COMMAND = "make backend-evaluate-npc"


@dataclass(frozen=True)
class NPCAgentEvaluationReadinessResult:
    exit_code: int
    report: dict[str, Any]


def build_npc_agent_evaluation_readiness_report(
    *,
    repo_root: Path | str | None = None,
    evaluation_file: Path | str | None = None,
) -> NPCAgentEvaluationReadinessResult:
    selected_repo_root = Path(repo_root) if repo_root is not None else _default_repo_root()
    selected_evaluation_file = (
        Path(evaluation_file)
        if evaluation_file is not None
        else selected_repo_root / DEFAULT_NPC_EVALUATION_PATH
    )
    source_file = {
        "path": _path_label(path=selected_evaluation_file, repo_root=selected_repo_root),
        "exists": selected_evaluation_file.exists(),
    }
    if not selected_evaluation_file.exists():
        return NPCAgentEvaluationReadinessResult(
            exit_code=2,
            report=_base_report(
                repo_root=selected_repo_root,
                status="missing",
                source_file=source_file,
                summary=_empty_summary(),
                coverage=_empty_coverage(),
                blockers=[],
                operator_actions=[
                    "run make backend-evaluate-npc to write "
                    "services/backend/.local/npc-evaluation-local.json"
                ],
            ),
        )

    try:
        saved_report = json.loads(selected_evaluation_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _blocked_result(
            repo_root=selected_repo_root,
            source_file=source_file,
            classification="unreadable_report",
            detail="Saved NPC Agent evaluation report is not valid JSON.",
        )

    if not isinstance(saved_report, dict):
        return _blocked_result(
            repo_root=selected_repo_root,
            source_file=source_file,
            classification="invalid_report_shape",
            detail="Saved NPC Agent evaluation report must be a JSON object.",
        )

    if saved_report.get("kind") != "npc_agent_evaluation_report":
        return _blocked_result(
            repo_root=selected_repo_root,
            source_file=source_file,
            classification="wrong_report_kind",
            detail="Saved report is not an npc_agent_evaluation_report.",
        )

    summary = _summary(saved_report)
    coverage = _coverage(saved_report.get("coverage"))
    blocker = _readiness_blocker(summary=summary, coverage=coverage, saved_report=saved_report)
    if blocker is not None:
        return NPCAgentEvaluationReadinessResult(
            exit_code=2,
            report=_base_report(
                repo_root=selected_repo_root,
                status="blocked",
                source_file=source_file,
                summary=summary,
                coverage=coverage,
                blockers=[blocker],
                operator_actions=[
                    "rerun make backend-evaluate-npc and review failed cases"
                ],
            ),
        )

    return NPCAgentEvaluationReadinessResult(
        exit_code=0,
        report=_base_report(
            repo_root=selected_repo_root,
            status="ready",
            source_file=source_file,
            summary=summary,
            coverage=coverage,
            blockers=[],
            operator_actions=["NPC Agent evaluation is ready"],
        ),
    )


def _blocked_result(
    *,
    repo_root: Path,
    source_file: dict[str, Any],
    classification: str,
    detail: str,
) -> NPCAgentEvaluationReadinessResult:
    return NPCAgentEvaluationReadinessResult(
        exit_code=2,
        report=_base_report(
            repo_root=repo_root,
            status="blocked",
            source_file=source_file,
            summary=_empty_summary(),
            coverage=_empty_coverage(),
            blockers=[
                {
                    "id": "npc_agent_evaluation_file",
                    "label": "NPC Agent evaluation file",
                    "status": "failed",
                    "classification": classification,
                    "command": LOCAL_NPC_EVALUATION_COMMAND,
                    "detail": detail,
                }
            ],
            operator_actions=[
                "rerun make backend-evaluate-npc to regenerate "
                "services/backend/.local/npc-evaluation-local.json"
            ],
        ),
    )


def _base_report(
    *,
    repo_root: Path,
    status: str,
    source_file: dict[str, Any],
    summary: dict[str, int],
    coverage: dict[str, int],
    blockers: list[dict[str, Any]],
    operator_actions: list[str],
) -> dict[str, Any]:
    report = {
        "kind": "npc_agent_evaluation_readiness_report",
        "status": status,
        "source_file": source_file,
        "summary": summary,
        "coverage": coverage,
        "blockers": blockers,
        "operator_actions": operator_actions,
        "safety": {
            "commands_run": False,
            "provider_calls": False,
            "global_mutation": False,
            "provider_secrets_in_report": False,
            "raw_private_context_in_report": False,
            "raw_media_in_report": False,
            "local_paths_in_report": False,
            "payment_links_in_report": False,
        },
    }
    return _sanitize_report(report, repo_root)


def _summary(saved_report: dict[str, Any]) -> dict[str, int]:
    return {
        "total_cases": _non_negative_int(saved_report.get("total_cases")),
        "succeeded": _non_negative_int(saved_report.get("succeeded")),
        "failed": _non_negative_int(saved_report.get("failed")),
        "tick_steps": _non_negative_int(saved_report.get("tick_steps")),
    }


def _empty_summary() -> dict[str, int]:
    return {"total_cases": 0, "succeeded": 0, "failed": 0, "tick_steps": 0}


def _coverage(raw_coverage: Any) -> dict[str, int]:
    if not isinstance(raw_coverage, dict):
        return _empty_coverage()
    return {
        "expected_npc_sets": _non_negative_int(raw_coverage.get("expected_npc_sets")),
        "trace_sets": _non_negative_int(raw_coverage.get("trace_sets")),
        "proposed_action_plan_matches": _non_negative_int(
            raw_coverage.get("proposed_action_plan_matches")
        ),
        "tick_steps_completed": _non_negative_int(raw_coverage.get("tick_steps_completed")),
        "world_resolution_steps": _non_negative_int(raw_coverage.get("world_resolution_steps")),
    }


def _empty_coverage() -> dict[str, int]:
    return {
        "expected_npc_sets": 0,
        "trace_sets": 0,
        "proposed_action_plan_matches": 0,
        "tick_steps_completed": 0,
        "world_resolution_steps": 0,
    }


def _readiness_blocker(
    *,
    summary: dict[str, int],
    coverage: dict[str, int],
    saved_report: dict[str, Any],
) -> dict[str, Any] | None:
    if summary["failed"] > 0:
        return _blocker(
            classification="npc_agent_evaluation_failed",
            detail=_failed_detail(saved_report),
        )
    if summary["succeeded"] <= 0:
        return _blocker(
            classification="empty_success_count",
            detail="NPC Agent evaluation report has no succeeded cases.",
        )
    if coverage["expected_npc_sets"] <= 0:
        return _blocker(
            classification="missing_expected_npc_coverage",
            detail="NPC Agent evaluation did not record expected NPC id coverage.",
        )
    if coverage["trace_sets"] <= 0:
        return _blocker(
            classification="missing_trace_coverage",
            detail="NPC Agent evaluation did not record agent trace coverage.",
        )
    if coverage["world_resolution_steps"] <= 0:
        return _blocker(
            classification="missing_world_resolution_coverage",
            detail="NPC Agent evaluation did not record world-resolution coverage.",
        )
    return None


def _blocker(*, classification: str, detail: str) -> dict[str, Any]:
    return {
        "id": "npc_agent_evaluation",
        "label": "NPC Agent evaluation",
        "status": "failed",
        "classification": classification,
        "command": LOCAL_NPC_EVALUATION_COMMAND,
        "detail": detail,
    }


def _failed_detail(saved_report: dict[str, Any]) -> str:
    cases = saved_report.get("cases")
    if isinstance(cases, list):
        for case in cases:
            if not isinstance(case, dict):
                continue
            if case.get("status") == "failed":
                case_id = str(case.get("case_id", "unknown_case"))
                error = str(case.get("error", "NPC Agent evaluation case failed."))
                return f"{case_id}: {error}"
    return "NPC Agent evaluation report contains failed cases."


def _non_negative_int(value: Any) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, int) and value > 0:
        return value
    return 0


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
        r"raw_email:[^\n\r]+",
        r"raw_calendar:[^\n\r]+",
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
