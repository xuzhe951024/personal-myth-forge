from __future__ import annotations

import json
from pathlib import Path

from myth_forge_api.config import Settings
from myth_forge_api.final_external_action_ledger import (
    build_final_external_action_ledger_report,
)


VALID_LOCAL_RESOURCES = """# Filled final resources. Do not commit.
MESHY_API_KEY=meshy-secret-test
OPENAI_API_KEY=sk-openai-test
OPENAI_API_BASE_URL=https://api.openai.test/v1
PRINT_PROVIDER=local
TREATSTOCK_API_KEY=
TREATSTOCK_API_BASE_URL=https://treatstock.test
SCULPTEO_API_KEY=
DEVELOPMENT_TEAM=ABCDE12345
PRODUCT_BUNDLE_IDENTIFIER=com.zhexu.personalmythforge.dev
PMF_BACKEND_BASE_URL=http://10.0.0.24:8080
PMF_FINAL_LAUNCH_MODE=configured
CAPTURE_STORAGE_DIR=
MYTH_SESSION_STORAGE_DIR=
"""


def test_external_action_ledger_blocks_missing_resources_without_running_actions(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    result = build_final_external_action_ledger_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    report = result.report
    report_text = json.dumps(report)
    groups = {group["id"]: group for group in report["action_groups"]}
    actions = report["actions_by_id"]

    assert result.exit_code == 2
    assert report["kind"] == "final_external_action_ledger_report"
    assert report["status"] == "blocked"
    assert [group["id"] for group in report["action_groups"]] == [
        "resource_inputs",
        "safe_local_writes",
        "live_provider_costs",
        "global_machine_actions",
        "device_runtime_actions",
    ]
    assert groups["resource_inputs"]["status"] == "blocked"
    assert groups["resource_inputs"]["summary"]["missing"] >= 5
    assert actions["provide_MESHY_API_KEY"]["status"] == "missing"
    assert actions["provide_MESHY_API_KEY"]["secret"] is True
    assert actions["provide_OPENAI_API_KEY"]["secret"] is True
    assert actions["provide_DEVELOPMENT_TEAM"]["requires_user_input"] is True
    assert actions["provide_PMF_BACKEND_BASE_URL"]["command"] == (
        "make final-resources-preflight"
    )
    assert actions["preview_final_resource_apply"]["command"] == (
        "make final-resource-apply-preview"
    )
    assert actions["apply_final_resources"]["status"] == "blocked"
    assert actions["apply_final_resources"]["writes_repo_local_files"] is True
    assert actions["run_live_provider_evidence"]["status"] == "live"
    assert actions["run_live_provider_evidence"]["requires_cost_consent"] is True
    assert actions["run_xcode_build_gate"]["status"] == "manual"
    assert actions["run_xcode_build_gate"]["global"] is True
    assert actions["run_xcode_build_gate"]["requires_user_confirmation"] is True
    assert report["summary"]["groups"] == 5
    assert report["summary"]["secret"] >= 3
    assert report["summary"]["requires_cost_consent"] >= 3
    assert report["summary"]["requires_user_confirmation"] >= 3
    assert report["operator_sequence"][:4] == [
        "make final-resource-requirements",
        "make final-resources-preflight",
        "make final-resource-apply-preview",
        "make final-apply-resources",
    ]
    assert report["source_reports"]["final_resource_requirements"]["status"] == "blocked"
    assert report["source_reports"]["final_resource_apply_preview"]["status"] == "missing"
    assert report["source_reports"]["live_provider_evidence"]["status"] == "missing"
    assert report["safety"] == {
        "commands_run": False,
        "writes_backend_env": False,
        "writes_ios_deploy_config": False,
        "runs_shell_writers": False,
        "provider_calls": False,
        "live_provider_calls": False,
        "global_mutation": False,
        "xcode_or_signing": False,
        "keychain_writes": False,
        "provider_secrets_in_report": False,
        "local_paths_in_report": False,
        "requires_user_confirmation_for_global_actions": True,
        "requires_cost_consent_for_live_actions": True,
    }
    assert str(tmp_path) not in report_text
    assert "meshy-secret-test" not in report_text
    assert "sk-openai-test" not in report_text


def test_external_action_ledger_marks_local_resource_actions_ready_without_leaks(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    write_resources(repo_root, VALID_LOCAL_RESOURCES)

    result = build_final_external_action_ledger_report(
        settings=Settings(
            three_d_provider="meshy",
            meshy_api_key="meshy-secret-test",
            npc_provider="openai",
            openai_api_key="sk-openai-test",
            print_provider="local",
        ),
        repo_root=repo_root,
    )
    report = result.report
    report_text = json.dumps(report)
    groups = {group["id"]: group for group in report["action_groups"]}
    actions = report["actions_by_id"]

    assert result.exit_code == 2
    assert report["status"] == "blocked"
    assert groups["resource_inputs"]["status"] == "ready"
    assert actions["provide_MESHY_API_KEY"]["status"] == "ready"
    assert actions["provide_OPENAI_API_KEY"]["status"] == "ready"
    assert actions["provide_DEVELOPMENT_TEAM"]["status"] == "ready"
    assert actions["provide_PMF_BACKEND_BASE_URL"]["status"] == "ready"
    assert actions["preview_final_resource_apply"]["status"] == "ready"
    assert actions["apply_final_resources"]["status"] == "ready"
    assert groups["safe_local_writes"]["status"] == "ready"
    assert groups["live_provider_costs"]["summary"]["live"] >= 3
    assert groups["global_machine_actions"]["status"] == "manual"
    assert report["summary"]["ready"] >= 7
    assert report["summary"]["live"] >= 3
    assert report["summary"]["manual"] >= 3
    assert "meshy-secret-test" not in report_text
    assert "sk-openai-test" not in report_text
    assert "10.0.0.24" not in report_text
    assert str(tmp_path) not in report_text


def write_resources(root: Path, text: str) -> Path:
    path = root / "services/backend/.local/final-resources.env"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path
