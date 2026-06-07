import json
from pathlib import Path

from myth_forge_api.npc_agent_evaluation_readiness import (
    build_npc_agent_evaluation_readiness_report,
)


def test_npc_agent_evaluation_readiness_missing_file_without_running_commands(
    tmp_path: Path,
) -> None:
    result = build_npc_agent_evaluation_readiness_report(repo_root=tmp_path)

    assert result.exit_code == 2
    assert result.report["kind"] == "npc_agent_evaluation_readiness_report"
    assert result.report["status"] == "missing"
    assert result.report["summary"] == {
        "total_cases": 0,
        "succeeded": 0,
        "failed": 0,
        "tick_steps": 0,
    }
    assert result.report["coverage"]["tick_steps_completed"] == 0
    assert result.report["blockers"] == []
    assert "make backend-evaluate-npc" in result.report["operator_actions"][0]
    assert result.report["safety"]["commands_run"] is False
    assert result.report["safety"]["provider_calls"] is False


def test_npc_agent_evaluation_readiness_ready_report(tmp_path: Path) -> None:
    _write_npc_evaluation_report(tmp_path, _ready_report())

    result = build_npc_agent_evaluation_readiness_report(repo_root=tmp_path)

    assert result.exit_code == 0
    assert result.report["status"] == "ready"
    assert result.report["summary"] == {
        "total_cases": 6,
        "succeeded": 6,
        "failed": 0,
        "tick_steps": 2,
    }
    assert result.report["coverage"]["expected_npc_sets"] == 6
    assert result.report["coverage"]["trace_sets"] == 6
    assert result.report["coverage"]["proposed_action_plan_matches"] == 6
    assert result.report["coverage"]["tick_steps_completed"] == 12
    assert result.report["coverage"]["world_resolution_steps"] == 12
    assert result.report["operator_actions"] == ["NPC Agent evaluation is ready"]


def test_npc_agent_evaluation_readiness_blocks_invalid_json(tmp_path: Path) -> None:
    path = _evaluation_path(tmp_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{not-json", encoding="utf-8")

    result = build_npc_agent_evaluation_readiness_report(repo_root=tmp_path)

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert result.report["blockers"][0]["classification"] == "unreadable_report"
    assert result.report["blockers"][0]["command"] == "make backend-evaluate-npc"


def test_npc_agent_evaluation_readiness_blocks_failed_report_and_redacts(
    tmp_path: Path,
) -> None:
    failed_report = _ready_report()
    failed_report["failed"] = 1
    failed_report["cases"] = [
        {
            "case_id": "npc_secret_case",
            "status": "failed",
            "error": (
                "OpenAI failed Authorization=Bearer test-secret "
                "private_message: raw text file:///Users/example/private.txt"
            ),
        }
    ]
    _write_npc_evaluation_report(tmp_path, failed_report)

    result = build_npc_agent_evaluation_readiness_report(repo_root=tmp_path)
    report_text = json.dumps(result.report)

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert result.report["blockers"][0]["classification"] == "npc_agent_evaluation_failed"
    assert result.report["blockers"][0]["command"] == "make backend-evaluate-npc"
    assert "rerun make backend-evaluate-npc" in result.report["operator_actions"][0]
    assert "[redacted]" in report_text or "[withheld]" in report_text
    assert "test-secret" not in report_text
    assert "private_message:" not in report_text
    assert "/Users/" not in report_text
    assert "file://" not in report_text


def _write_npc_evaluation_report(repo_root: Path, report: dict[str, object]) -> Path:
    path = _evaluation_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report), encoding="utf-8")
    return path


def _evaluation_path(repo_root: Path) -> Path:
    return repo_root / "services/backend/.local/npc-evaluation-local.json"


def _ready_report() -> dict[str, object]:
    return {
        "kind": "npc_agent_evaluation_report",
        "suite": "default-v0",
        "provider": "local",
        "tick_steps": 2,
        "total_cases": 6,
        "succeeded": 6,
        "failed": 0,
        "coverage": {
            "expected_npc_sets": 6,
            "trace_sets": 6,
            "proposed_action_plan_matches": 6,
            "tick_steps_completed": 12,
            "world_resolution_steps": 12,
        },
        "safety": {
            "raw_private_context_in_report": False,
            "provider_secrets_in_report": False,
            "local_paths_in_report": False,
            "media_payloads_in_report": False,
        },
        "cases": [],
    }
