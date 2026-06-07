from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_THREE_D_EVALUATION_PATH = Path("services/backend/.local/3d-evaluation-local.json")
LOCAL_THREE_D_EVALUATION_COMMAND = "make backend-evaluate-3d"


@dataclass(frozen=True)
class ThreeDEvaluationReadinessResult:
    exit_code: int
    report: dict[str, Any]


def build_three_d_evaluation_readiness_report(
    *,
    repo_root: Path | str | None = None,
    evaluation_file: Path | str | None = None,
) -> ThreeDEvaluationReadinessResult:
    selected_repo_root = Path(repo_root) if repo_root is not None else _default_repo_root()
    selected_evaluation_file = (
        Path(evaluation_file)
        if evaluation_file is not None
        else selected_repo_root / DEFAULT_THREE_D_EVALUATION_PATH
    )
    source_file = {
        "path": _path_label(path=selected_evaluation_file, repo_root=selected_repo_root),
        "exists": selected_evaluation_file.exists(),
    }
    if not selected_evaluation_file.exists():
        return ThreeDEvaluationReadinessResult(
            exit_code=2,
            report=_base_report(
                repo_root=selected_repo_root,
                status="missing",
                source_file=source_file,
                summary=_empty_summary(),
                coverage=_empty_coverage(),
                blockers=[],
                operator_actions=[
                    "run make backend-evaluate-3d to write "
                    "services/backend/.local/3d-evaluation-local.json"
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
            detail="Saved 3D evaluation report is not valid JSON.",
        )

    if not isinstance(saved_report, dict):
        return _blocked_result(
            repo_root=selected_repo_root,
            source_file=source_file,
            classification="invalid_report_shape",
            detail="Saved 3D evaluation report must be a JSON object.",
        )

    if saved_report.get("kind") != "three_d_evaluation_report":
        return _blocked_result(
            repo_root=selected_repo_root,
            source_file=source_file,
            classification="wrong_report_kind",
            detail="Saved report is not a three_d_evaluation_report.",
        )

    summary = _summary(saved_report)
    coverage = _coverage(saved_report.get("coverage"))
    blocker = _readiness_blocker(summary=summary, coverage=coverage, saved_report=saved_report)
    if blocker is not None:
        return ThreeDEvaluationReadinessResult(
            exit_code=2,
            report=_base_report(
                repo_root=selected_repo_root,
                status="blocked",
                source_file=source_file,
                summary=summary,
                coverage=coverage,
                blockers=[blocker],
                operator_actions=["rerun make backend-evaluate-3d and review failed cases"],
            ),
        )

    return ThreeDEvaluationReadinessResult(
        exit_code=0,
        report=_base_report(
            repo_root=selected_repo_root,
            status="ready",
            source_file=source_file,
            summary=summary,
            coverage=coverage,
            blockers=[],
            operator_actions=["3D evaluation is ready"],
        ),
    )


def _blocked_result(
    *,
    repo_root: Path,
    source_file: dict[str, Any],
    classification: str,
    detail: str,
) -> ThreeDEvaluationReadinessResult:
    return ThreeDEvaluationReadinessResult(
        exit_code=2,
        report=_base_report(
            repo_root=repo_root,
            status="blocked",
            source_file=source_file,
            summary=_empty_summary(),
            coverage=_empty_coverage(),
            blockers=[
                {
                    "id": "three_d_evaluation_file",
                    "label": "3D evaluation file",
                    "status": "failed",
                    "classification": classification,
                    "command": LOCAL_THREE_D_EVALUATION_COMMAND,
                    "detail": detail,
                }
            ],
            operator_actions=[
                "rerun make backend-evaluate-3d to regenerate "
                "services/backend/.local/3d-evaluation-local.json"
            ],
        ),
    )


def _base_report(
    *,
    repo_root: Path,
    status: str,
    source_file: dict[str, Any],
    summary: dict[str, int],
    coverage: dict[str, Any],
    blockers: list[dict[str, Any]],
    operator_actions: list[str],
) -> dict[str, Any]:
    report = {
        "kind": "three_d_evaluation_readiness_report",
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
    }


def _empty_summary() -> dict[str, int]:
    return {"total_cases": 0, "succeeded": 0, "failed": 0}


def _coverage(raw_coverage: Any) -> dict[str, Any]:
    if not isinstance(raw_coverage, dict):
        return _empty_coverage()
    return {
        "input_modes": _input_modes(raw_coverage.get("input_modes")),
        "variant_roles": _variant_roles(raw_coverage.get("variant_roles")),
        "scene_loadable_cases": _non_negative_int(raw_coverage.get("scene_loadable_cases")),
    }


def _empty_coverage() -> dict[str, Any]:
    return {
        "input_modes": {
            "text_prompt": 0,
            "single_image": 0,
            "multi_image": 0,
            "unknown": 0,
        },
        "variant_roles": {},
        "scene_loadable_cases": 0,
    }


def _input_modes(raw_input_modes: Any) -> dict[str, int]:
    result = {
        "text_prompt": 0,
        "single_image": 0,
        "multi_image": 0,
        "unknown": 0,
    }
    if not isinstance(raw_input_modes, dict):
        return result
    for key in result:
        result[key] = _non_negative_int(raw_input_modes.get(key))
    return result


def _variant_roles(raw_variant_roles: Any) -> dict[str, int]:
    if not isinstance(raw_variant_roles, dict):
        return {}
    return {
        str(role): _non_negative_int(count)
        for role, count in raw_variant_roles.items()
        if isinstance(role, str) and _non_negative_int(count) > 0
    }


def _readiness_blocker(
    *,
    summary: dict[str, int],
    coverage: dict[str, Any],
    saved_report: dict[str, Any],
) -> dict[str, Any] | None:
    if summary["failed"] > 0:
        return _blocker(
            classification="three_d_evaluation_failed",
            detail=_failed_detail(saved_report),
        )
    if summary["succeeded"] <= 0:
        return _blocker(
            classification="empty_success_count",
            detail="3D evaluation report has no succeeded cases.",
        )
    input_modes = coverage["input_modes"]
    if input_modes["text_prompt"] <= 0:
        return _blocker(
            classification="missing_text_prompt_coverage",
            detail="3D evaluation did not record text prompt input coverage.",
        )
    variant_roles = coverage["variant_roles"]
    if variant_roles.get("game_asset", 0) <= 0:
        return _blocker(
            classification="missing_game_asset_variant_coverage",
            detail="3D evaluation did not record generated game asset variants.",
        )
    if variant_roles.get("ios_scene_asset", 0) <= 0:
        return _blocker(
            classification="missing_ios_scene_variant_coverage",
            detail="3D evaluation did not record iOS scene-loadable variants.",
        )
    if coverage["scene_loadable_cases"] <= 0:
        return _blocker(
            classification="missing_scene_loadable_coverage",
            detail="3D evaluation did not record scene-loadable cases.",
        )
    return None


def _blocker(*, classification: str, detail: str) -> dict[str, Any]:
    return {
        "id": "three_d_evaluation",
        "label": "3D evaluation",
        "status": "failed",
        "classification": classification,
        "command": LOCAL_THREE_D_EVALUATION_COMMAND,
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
                error = str(case.get("error", "3D evaluation case failed."))
                return f"{case_id}: {error}"
    return "3D evaluation report contains failed cases."


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
