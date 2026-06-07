import json
from pathlib import Path

from myth_forge_api.npc_agent_provider_acceptance import (
    run_npc_agent_provider_acceptance,
)


def test_npc_agent_provider_acceptance_passes_complete_fixture(tmp_path: Path) -> None:
    write_complete_npc_agent_provider_fixture(tmp_path)

    result = run_npc_agent_provider_acceptance(repo_root=tmp_path)

    assert result.exit_code == 0
    assert result.report["kind"] == "npc_agent_provider_acceptance_report"
    assert result.report["status"] == "succeeded"
    assert result.report["summary"] == {"passed": 8, "failed": 0}
    assert [item["id"] for item in result.report["required_features"]] == [
        "openai_director_structured_output",
        "openai_tick_structured_output",
        "provider_factory_wiring",
        "provider_readiness_contract",
        "resource_handoff_contract",
        "npc_agent_evaluation_contract",
        "backend_docs_contract",
        "mobile_docs_contract",
    ]
    assert result.report["safety"] == {
        "provider_calls": False,
        "provider_secrets_in_report": False,
        "local_paths_in_report": False,
        "raw_media_in_report": False,
        "payment_links_in_report": False,
    }


def test_npc_agent_provider_acceptance_fails_missing_backend_key_docs_safely(
    tmp_path: Path,
) -> None:
    write_complete_npc_agent_provider_fixture(tmp_path)
    readme_path = tmp_path / "README.md"
    readme_path.write_text(
        readme_path.read_text(encoding="utf-8").replace("OPENAI_API_KEY", "OPENAI KEY"),
        encoding="utf-8",
    )

    result = run_npc_agent_provider_acceptance(repo_root=tmp_path)
    report_text = json.dumps(result.report)
    features = {item["id"]: item for item in result.report["required_features"]}

    assert result.exit_code == 1
    assert result.report["status"] == "failed"
    assert result.report["summary"] == {"passed": 7, "failed": 1}
    assert features["backend_docs_contract"]["status"] == "failed"
    assert {
        "file": "README.md",
        "contains": "OPENAI_API_KEY",
    } in features["backend_docs_contract"]["missing"]
    assert str(tmp_path) not in report_text
    assert "/Users/" not in report_text
    assert "sk-" not in report_text
    assert "Bearer" not in report_text
    assert "data:image" not in report_text


def write_complete_npc_agent_provider_fixture(repo_root: Path) -> None:
    files = {
        "services/backend/src/myth_forge_api/providers/npc.py": (
            "OpenAINPCDirector OpenAINPCOutput "
            "text_format=OpenAINPCOutput "
            'agent_runtime="openai_structured_runtime" '
            "OPENAI_API_KEY is required for NPC generation."
        ),
        "services/backend/src/myth_forge_api/providers/npc_ticks.py": (
            "OpenAINPCTickRuntime OpenAINPCTickOutput "
            'runtime_name = "openai_tick_structured_runtime" '
            "text_format=OpenAINPCTickOutput "
            "OPENAI_API_KEY is required for NPC tick generation."
        ),
        "services/backend/src/myth_forge_api/providers/factory.py": (
            'npc_provider == "openai" '
            "OpenAINPCDirector.from_settings "
            "OpenAINPCTickRuntime.from_settings"
        ),
        "services/backend/src/myth_forge_api/providers/readiness.py": (
            "structured_agent_traces structured_agent_ticks "
            'missing_env=["OPENAI_API_KEY"] '
            "OpenAI NPC provider is configured for AI-driven NPC traces and stateless ticks."
        ),
        "services/backend/src/myth_forge_api/resource_handoff.py": (
            "NPC_PROVIDER OPENAI_API_KEY AI Agent NPC traces and ticks "
            "Backend-only key; mobile sees only generated NPC state."
        ),
        "services/backend/src/myth_forge_api/cli.py": "evaluate-npc",
        "services/backend/src/myth_forge_api/evaluation/npc.py": (
            "run_npc_agent_evaluation DEFAULT_NPC_AGENT_EVALUATION_SUITE "
            "npc_agent_evaluation_report"
        ),
        "README.md": (
            "NPC_PROVIDER=openai OPENAI_API_KEY OpenAINPCDirector "
            "OpenAINPCTickRuntime no OpenAI key is stored in or sent to the iOS app "
            "evaluate-npc"
        ),
        "docs/iteration-roadmap.md": "P0.90 NPC Agent evaluation suite",
        "apps/mobile/README.md": (
            "P0.23 OpenAI NPC Tick Provider NPC_PROVIDER=openai "
            "openai_tick_structured_runtime no provider keys"
        ),
    }
    for file_name, content in files.items():
        path = repo_root / file_name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
