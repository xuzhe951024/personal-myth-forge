import json

from myth_forge_api.evaluation.npc import (
    DEFAULT_NPC_AGENT_EVALUATION_SUITE,
    run_npc_agent_evaluation,
)
from myth_forge_api.providers.npc import LocalNPCDirector, OpenAINPCProviderError
from myth_forge_api.providers.npc_ticks import LocalNPCTickRuntime


def test_npc_agent_evaluation_default_suite_builds_rich_safe_report() -> None:
    report = run_npc_agent_evaluation(
        director=LocalNPCDirector(),
        tick_runtime=LocalNPCTickRuntime(),
        selected_provider="local",
        suite_name="default-v0",
        tick_steps=2,
        cases=DEFAULT_NPC_AGENT_EVALUATION_SUITE,
    )
    report_text = json.dumps(report)

    assert report["kind"] == "npc_agent_evaluation_report"
    assert report["status"] == "succeeded"
    assert report["suite"] == "default-v0"
    assert report["provider"] == "local"
    assert report["tick_steps"] == 2
    assert report["total_cases"] == 6
    assert report["succeeded"] == 6
    assert report["failed"] == 0
    assert report["coverage"]["expected_npc_sets"] == 6
    assert report["coverage"]["trace_sets"] == 6
    assert report["coverage"]["proposed_action_plan_matches"] == 6
    assert report["coverage"]["tick_steps_completed"] == 12
    assert report["coverage"]["world_resolution_steps"] == 12
    assert report["safety"] == {
        "raw_private_context_in_report": False,
        "provider_secrets_in_report": False,
        "local_paths_in_report": False,
        "media_payloads_in_report": False,
    }
    assert len(report["review_rubric"]) == 5

    first_case = report["cases"][0]
    assert first_case["case_id"] == "npc_01_brass_key_dispute"
    assert first_case["expected_npc_ids"] == ["mara", "ior", "senn"]
    assert first_case["npc_ids"] == ["mara", "ior", "senn"]
    assert first_case["trace_count"] == 3
    assert first_case["proposed_actions_in_plan"] is True
    assert len(first_case["ticks"]) == 2
    assert first_case["ticks"][0]["tick_index"] == 1
    assert first_case["ticks"][0]["trace_count"] == 3
    assert first_case["ticks"][0]["accepted_action_count"] >= 1
    assert first_case["manual_review"] == {
        "agent_believability": None,
        "autonomy_signal": None,
        "world_impact": None,
        "privacy_boundary": None,
        "notes": None,
    }
    assert "raw_email:" not in report_text
    assert "raw_calendar:" not in report_text
    assert "private_message:" not in report_text
    assert "Authorization" not in report_text
    assert "file://" not in report_text
    assert "data:image" not in report_text


def test_npc_agent_evaluation_sanitizes_provider_errors() -> None:
    report = run_npc_agent_evaluation(
        director=FailingNPCDirector(),
        tick_runtime=LocalNPCTickRuntime(),
        selected_provider="openai",
        suite_name="default-v0",
        tick_steps=1,
        cases=DEFAULT_NPC_AGENT_EVALUATION_SUITE[:1],
    )
    report_text = json.dumps(report)

    assert report["status"] == "failed"
    assert report["failed"] == 1
    assert report["cases"][0]["status"] == "failed"
    assert "[withheld]" in report["cases"][0]["error"]
    assert "test-secret" not in report_text
    assert "private_message:" not in report_text


class FailingNPCDirector:
    provider_name = "openai"

    def validate_configuration(self) -> None:
        return None

    def generate_reactions(self, **kwargs):
        raise OpenAINPCProviderError(
            "failed Authorization=Bearer test-secret private_message: user said keep this"
        )
