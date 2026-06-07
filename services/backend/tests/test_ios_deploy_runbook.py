from __future__ import annotations

import json
from pathlib import Path

from myth_forge_api.cli import main
from myth_forge_api.ios_deploy_runbook import build_ios_deploy_runbook_report


def test_ios_deploy_runbook_blocks_missing_inputs_without_secret_or_path_leak(
    tmp_path: Path,
) -> None:
    repo_root = _repo(tmp_path)

    report = build_ios_deploy_runbook_report(mode="local", repo_root=repo_root)
    report_text = json.dumps(report)
    slots = {slot["id"]: slot for slot in report["input_slots"]}

    assert report["kind"] == "ios_deploy_runbook_report"
    assert report["mode"] == "local"
    assert report["status"] == "blocked"
    assert slots["final_resources_env"]["status"] == "missing"
    assert slots["development_team"]["status"] == "missing"
    assert slots["backend_base_url"]["status"] == "missing"
    assert slots["local_final_acceptance"]["status"] == "missing"
    assert slots["npc_agent_evaluation"]["status"] == "missing"
    assert "copy services/backend/final-resources.env.example" in " ".join(
        report["operator_actions"]
    )
    assert report["safety"] == {
        "commands_run": False,
        "provider_calls": False,
        "global_mutation": False,
        "provider_secrets_in_report": False,
        "raw_media_in_report": False,
        "payment_links_in_report": False,
        "local_paths_in_report": False,
    }
    assert "sk-" not in report_text
    assert str(tmp_path) not in report_text


def test_ios_deploy_runbook_ready_local_inputs_preserve_command_order(
    tmp_path: Path,
) -> None:
    repo_root = _repo(tmp_path)
    _write_deploy_config(repo_root)
    _write_final_resources(repo_root)
    _write_final_acceptance(repo_root, status="passed")
    _write_npc_evaluation(repo_root, status="passed")

    report = build_ios_deploy_runbook_report(mode="local", repo_root=repo_root)
    commands = [step["command"] for step in report["command_sequence"]]
    slots = {slot["id"]: slot for slot in report["input_slots"]}

    assert report["status"] == "partial"
    assert slots["development_team"]["status"] == "ready"
    assert slots["backend_base_url"]["status"] == "ready"
    assert commands[:4] == [
        "make final-resources-preflight",
        "make final-apply-resources",
        "make backend-device-demo",
        "make mobile-deploy-preflight",
    ]
    assert commands[-1] == "make mobile-xcode-build"
    assert report["command_sequence"][-1]["id"] == "xcode_build_gate"
    assert report["command_sequence"][-1]["status"] == "manual"


def test_ios_deploy_runbook_configured_mode_includes_live_acceptance_consent(
    tmp_path: Path,
) -> None:
    repo_root = _repo(tmp_path)
    _write_deploy_config(repo_root, final_launch_mode="configured")
    _write_final_resources(repo_root)
    _write_final_acceptance(repo_root, status="passed")
    _write_npc_evaluation(repo_root, status="passed")

    report = build_ios_deploy_runbook_report(mode="configured", repo_root=repo_root)
    commands = {step["id"]: step for step in report["command_sequence"]}

    assert report["status"] == "partial"
    assert commands["configured_final_acceptance"]["requires_consent"] is True
    assert "--allow-live-provider-calls" in commands["configured_final_acceptance"]["command"]
    assert "live provider cost review" in " ".join(report["operator_actions"])


def test_ios_deploy_runbook_cli_writes_output(tmp_path: Path) -> None:
    repo_root = _repo(tmp_path)
    output = tmp_path / "runbook.json"

    exit_code = main(
        [
            "ios-deploy-runbook",
            "--mode",
            "local",
            "--repo-root",
            str(repo_root),
            "--output",
            str(output),
        ]
    )

    assert exit_code == 2
    assert json.loads(output.read_text(encoding="utf-8"))[
        "kind"
    ] == "ios_deploy_runbook_report"


def _repo(tmp_path: Path) -> Path:
    repo_root = tmp_path / "repo"
    config_dir = repo_root / "apps/mobile/ios/Config"
    config_dir.mkdir(parents=True)
    (config_dir / "Deployment.xcconfig").write_text(
        "\n".join(
            [
                "PRODUCT_BUNDLE_IDENTIFIER = com.personalmythforge.app",
                "DEVELOPMENT_TEAM =",
                "CODE_SIGN_STYLE = Automatic",
                "PMF_BACKEND_BASE_URL =",
                "PMF_FINAL_LAUNCH_MODE = local",
                '#include? "Deployment.local.xcconfig"',
            ]
        ),
        encoding="utf-8",
    )
    return repo_root


def _write_deploy_config(repo_root: Path, *, final_launch_mode: str = "local") -> None:
    config = repo_root / "apps/mobile/ios/Config/Deployment.local.xcconfig"
    config.write_text(
        "\n".join(
            [
                "DEVELOPMENT_TEAM = TEAM12345",
                "PRODUCT_BUNDLE_IDENTIFIER = com.example.personalmythforge",
                "PMF_BACKEND_BASE_URL = http://192.168.1.10:8080",
                f"PMF_FINAL_LAUNCH_MODE = {final_launch_mode}",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _write_final_resources(repo_root: Path) -> None:
    resources = repo_root / "services/backend/.local/final-resources.env"
    resources.parent.mkdir(parents=True)
    resources.write_text(
        "\n".join(
            [
                "MESHY_API_KEY=meshy-secret-test",
                "OPENAI_API_KEY=sk-openai-test",
                "PRINT_PROVIDER=local",
                "DEVELOPMENT_TEAM=TEAM12345",
                "PRODUCT_BUNDLE_IDENTIFIER=com.example.personalmythforge",
                "PMF_BACKEND_BASE_URL=http://192.168.1.10:8080",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _write_final_acceptance(repo_root: Path, *, status: str) -> None:
    acceptance = repo_root / "services/backend/.local/final-acceptance-local.json"
    acceptance.parent.mkdir(parents=True, exist_ok=True)
    acceptance.write_text(
        json.dumps(
            {
                "kind": "final_acceptance_report",
                "overall_status": status,
                "summary": {"passed": 14, "blocked": 0, "failed": 0, "skipped": 0},
                "checks": [
                    {"id": "provider_handoff", "label": "Provider handoff", "status": status}
                ],
            }
        ),
        encoding="utf-8",
    )


def _write_npc_evaluation(repo_root: Path, *, status: str) -> None:
    succeeded = 6 if status == "passed" else 0
    failed = 0 if status == "passed" else 6
    evaluation = repo_root / "services/backend/.local/npc-evaluation-local.json"
    evaluation.parent.mkdir(parents=True, exist_ok=True)
    evaluation.write_text(
        json.dumps(
            {
                "kind": "npc_agent_evaluation_report",
                "suite": "default-v0",
                "provider": "local",
                "tick_steps": 2,
                "total_cases": 6,
                "succeeded": succeeded,
                "failed": failed,
                "coverage": {
                    "expected_npc_sets": succeeded,
                    "trace_sets": succeeded,
                    "proposed_action_plan_matches": succeeded,
                    "tick_steps_completed": succeeded * 2,
                    "world_resolution_steps": succeeded * 2,
                },
                "cases": [],
            }
        ),
        encoding="utf-8",
    )
