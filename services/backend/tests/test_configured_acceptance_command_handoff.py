from __future__ import annotations

from pathlib import Path

from myth_forge_api.config import Settings
from myth_forge_api.final_configured_preflight import (
    build_final_configured_preflight_report,
)
from myth_forge_api.final_demo_launch import build_final_demo_launch_report
from myth_forge_api.final_handoff_index import build_final_handoff_index_report
from myth_forge_api.final_operator_handoff import build_final_operator_handoff_report
from myth_forge_api.live_provider_evidence import build_live_provider_evidence_report

RAW_CONFIGURED_ACCEPTANCE_FRAGMENT = (
    "final-acceptance --profile quick --provider-mode configured"
)
CONFIGURED_MAKE_TARGET = "make final-acceptance-configured"
CONFIGURED_COST_REVIEW_ACTION = (
    "run make final-acceptance-configured only after live provider cost review "
    "and --allow-live-provider-calls consent"
)


def test_backend_sources_do_not_publish_raw_configured_acceptance_cli() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    offenders = []
    for path in (repo_root / "services/backend/src/myth_forge_api").glob("*.py"):
        text = path.read_text(encoding="utf-8")
        if RAW_CONFIGURED_ACCEPTANCE_FRAGMENT in text:
            offenders.append(path.relative_to(repo_root).as_posix())

    assert offenders == []


def test_configured_preflight_commands_use_make_target(tmp_path: Path) -> None:
    report = build_final_configured_preflight_report(
        settings=Settings(),
        repo_root=tmp_path,
    ).report

    assert CONFIGURED_MAKE_TARGET in report["commands"]
    assert all(
        RAW_CONFIGURED_ACCEPTANCE_FRAGMENT not in command
        for command in report["commands"]
    )
    assert CONFIGURED_COST_REVIEW_ACTION in report["operator_actions"]


def test_configured_demo_launch_uses_make_target(tmp_path: Path) -> None:
    report = build_final_demo_launch_report(
        mode="configured",
        settings=Settings(),
        repo_root=tmp_path,
    ).report
    phases = {phase["id"]: phase for phase in report["launch_phases"]}

    assert phases["configured_final_acceptance"]["command"] == CONFIGURED_MAKE_TARGET
    assert CONFIGURED_MAKE_TARGET in report["commands"]
    assert all(
        RAW_CONFIGURED_ACCEPTANCE_FRAGMENT not in command
        for command in report["commands"]
    )


def test_operator_handoff_uses_make_target_for_configured_acceptance() -> None:
    report = build_final_operator_handoff_report(
        mode="configured",
        final_resources_preflight={"status": "ready", "operator_actions": []},
        final_acceptance_readiness={"status": "ready", "summary": {}},
        three_d_evaluation_readiness={"status": "ready", "summary": {}},
        npc_agent_evaluation_readiness={"status": "ready", "summary": {}},
        ios_deploy_runbook={"status": "ready", "input_slots": [], "command_sequence": []},
        launch_phases=[
            {
                "id": "configured_final_acceptance",
                "label": "Run configured final acceptance",
                "status": "ready",
                "required_for": "real providers",
                "command": CONFIGURED_MAKE_TARGET,
                "notes": ["May call live providers and may spend provider credits."],
            }
        ],
    )
    steps = {step["id"]: step for step in report["steps"]}

    assert steps["configured_final_acceptance"]["command"] == CONFIGURED_MAKE_TARGET
    assert steps["configured_final_acceptance"]["requires_consent"] is True
    assert CONFIGURED_COST_REVIEW_ACTION in report["next_actions"]


def test_final_handoff_index_and_live_evidence_use_make_target(
    tmp_path: Path,
) -> None:
    handoff = build_final_handoff_index_report(
        settings=Settings(),
        repo_root=tmp_path,
    ).report
    live = build_live_provider_evidence_report(repo_root=tmp_path).report
    live_rows = {row["id"]: row for row in live["evidence"]}

    assert CONFIGURED_MAKE_TARGET in handoff["commands"]
    assert all(
        RAW_CONFIGURED_ACCEPTANCE_FRAGMENT not in command
        for command in handoff["commands"]
    )
    assert live_rows["final_acceptance_configured"]["command"] == CONFIGURED_MAKE_TARGET
    assert CONFIGURED_MAKE_TARGET in live["commands"]
