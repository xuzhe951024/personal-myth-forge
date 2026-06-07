import json
from pathlib import Path

from myth_forge_api.config import Settings
from myth_forge_api.ios_device_launch_certificate import (
    build_ios_device_launch_certificate_report,
)


def test_ios_device_launch_certificate_blocks_missing_inputs_without_leaks(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)

    result = build_ios_device_launch_certificate_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    report_text = json.dumps(result.report)
    gates = {gate["id"]: gate for gate in result.report["device_gates"]}

    assert result.exit_code == 2
    assert result.report["kind"] == "ios_device_launch_certificate_report"
    assert result.report["status"] == "blocked"
    assert result.report["mode"] == "local"
    assert gates["final_handoff_index"]["status"] == "blocked"
    assert gates["ios_deploy_config"]["status"] == "blocked"
    assert gates["configured_final_acceptance"]["status"] == "live"
    assert gates["configured_final_acceptance"]["requires_consent"] is True
    assert "make ios-device-launch-certificate" in result.report["commands"]
    assert "make backend-device-demo" in result.report["commands"]
    assert "make mobile-deploy-preflight" in result.report["commands"]
    assert result.report["operator_actions"][:3] == [
        "run make final-handoff-index",
        "provide iOS deploy config and rerun mobile deploy preflight",
        "run make ios-deploy-runbook-local",
    ]
    assert result.report["safety"]["provider_calls"] is False
    assert result.report["safety"]["commands_run"] is False
    assert result.report["safety"]["xcode_or_signing"] is False
    assert result.report["safety"]["writes_ios_deploy_config"] is False
    assert str(tmp_path) not in report_text
    assert "sk-" not in report_text


def test_ios_device_launch_certificate_ready_with_configured_inputs(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(
        tmp_path,
        local_config=(
            "DEVELOPMENT_TEAM = TEAM12345\n"
            "PRODUCT_BUNDLE_IDENTIFIER = com.example.personalmythforge\n"
            "PMF_BACKEND_BASE_URL = http://192.168.1.10:8080\n"
            "PMF_FINAL_LAUNCH_MODE = configured\n"
        ),
    )
    _write_final_resources(repo_root)
    _write_local_rehearsal_reports(repo_root)
    settings = Settings(
        three_d_provider="meshy",
        meshy_api_key="sk-meshy-secret",
        npc_provider="openai",
        openai_api_key="sk-openai-secret",
        print_provider="treatstock",
        treatstock_api_key="treatstock-secret",
    )

    result = build_ios_device_launch_certificate_report(
        settings=settings,
        repo_root=repo_root,
    )
    report_text = json.dumps(result.report)
    gates = {gate["id"]: gate for gate in result.report["device_gates"]}

    assert result.exit_code == 0
    assert result.report["status"] == "ready"
    assert result.report["mode"] == "configured"
    assert result.report["certificate"]["development_team"]["configured"] is True
    assert result.report["certificate"]["product_bundle_identifier"]["configured"] is True
    assert result.report["certificate"]["backend_base_url"]["configured"] is True
    assert result.report["final_handoff_index"]["status"] == "ready"
    assert result.report["final_handoff_index"]["summary"]["blocked"] == 0
    assert result.report["ios_deploy_runbook"]["status"] == "partial"
    runbook_commands = [
        step["command"]
        for step in result.report["ios_deploy_runbook"]["command_sequence"]
    ]
    assert "make final-resource-apply-preview" in runbook_commands
    assert runbook_commands.index("make final-resource-apply-preview") < (
        runbook_commands.index("make final-apply-resources")
    )
    assert result.report["final_demo_launch"]["overall_status"] == "partial"
    assert gates["ios_deploy_config"]["status"] == "ready"
    assert gates["backend_device_server"]["status"] == "manual"
    assert gates["xcode_build_gate"]["status"] == "manual"
    assert gates["configured_final_acceptance"]["requires_consent"] is True
    assert result.report["operator_sequence"][0]["command"] == (
        "make ios-device-launch-certificate"
    )
    assert "make backend-device-demo" in result.report["commands"]
    assert "make mobile-deploy-preflight" in result.report["commands"]
    assert "sk-meshy-secret" not in report_text
    assert "sk-openai-secret" not in report_text
    assert "treatstock-secret" not in report_text
    assert "192.168.1.10" not in report_text
    assert str(tmp_path) not in report_text


def test_ios_device_launch_certificate_cli_writes_report_and_makefile_target(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    output_path = tmp_path / "ios-device-launch-certificate.json"

    from myth_forge_api.cli import main

    exit_code = main(
        [
            "ios-device-launch-certificate",
            "--repo-root",
            str(repo_root),
            "--output",
            str(output_path),
        ]
    )

    assert exit_code == 2
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["kind"] == "ios_device_launch_certificate_report"
    assert payload["status"] == "blocked"

    makefile = (Path(__file__).resolve().parents[3] / "Makefile").read_text(
        encoding="utf-8"
    )
    assert "ios-device-launch-certificate:" in makefile
    assert "myth_forge_api.cli ios-device-launch-certificate" in makefile
    assert ".local/ios-device-launch-certificate.json" in makefile


def _write_deploy_config(tmp_path: Path, local_config: str | None = None) -> Path:
    repo_root = tmp_path / "repo"
    config_dir = repo_root / "apps/mobile/ios/Config"
    config_dir.mkdir(parents=True)
    (config_dir / "Deployment.xcconfig").write_text(
        "\n".join(
            [
                "PRODUCT_BUNDLE_IDENTIFIER = com.personalmythforge.app",
                "DEVELOPMENT_TEAM =",
                "CODE_SIGN_STYLE = Automatic",
                "PMF_BACKEND_BASE_URL = http://127.0.0.1:8080",
                '#include? "Deployment.local.xcconfig"',
            ]
        ),
        encoding="utf-8",
    )
    if local_config is not None:
        (config_dir / "Deployment.local.xcconfig").write_text(
            local_config,
            encoding="utf-8",
        )
    return repo_root


def _write_final_resources(repo_root: Path) -> None:
    resources = repo_root / "services/backend/.local/final-resources.env"
    resources.parent.mkdir(parents=True)
    resources.write_text(
        "\n".join(
            [
                "MESHY_API_KEY=meshy-secret-test",
                "OPENAI_API_KEY=sk-openai-test",
                "PRINT_PROVIDER=treatstock",
                "TREATSTOCK_API_KEY=treatstock-secret-test",
                "DEVELOPMENT_TEAM=TEAM12345",
                "PRODUCT_BUNDLE_IDENTIFIER=com.example.personalmythforge",
                "PMF_BACKEND_BASE_URL=http://192.168.1.10:8080",
                "PMF_FINAL_LAUNCH_MODE=configured",
            ]
        ),
        encoding="utf-8",
    )


def _write_local_rehearsal_reports(repo_root: Path) -> None:
    _write_three_d_evaluation(repo_root)
    _write_npc_evaluation(repo_root)
    _write_visual_regression(repo_root)
    _write_final_acceptance(repo_root)
    _write_final_demo_launch(repo_root)
    _write_ios_deploy_runbook(repo_root)


def _write_final_acceptance(repo_root: Path) -> None:
    report = {
        "kind": "final_acceptance_report",
        "overall_status": "passed",
        "summary": {"passed": 14, "blocked": 0, "failed": 0, "skipped": 0},
        "checks": [
            {"id": "provider_handoff", "label": "Provider handoff", "status": "passed"},
            {"id": "demo_acceptance", "label": "Demo acceptance", "status": "passed"},
        ],
    }
    _write_json(repo_root / "services/backend/.local/final-acceptance-local.json", report)


def _write_final_demo_launch(repo_root: Path) -> None:
    report = {
        "kind": "final_demo_launch_report",
        "mode": "local",
        "overall_status": "partial",
        "summary": {"ready": 8, "missing": 0, "blocked": 0, "manual": 1, "optional": 1},
    }
    _write_json(repo_root / "services/backend/.local/final-demo-launch-local.json", report)


def _write_ios_deploy_runbook(repo_root: Path) -> None:
    report = {
        "kind": "ios_deploy_runbook_report",
        "mode": "local",
        "status": "partial",
        "input_slots": [],
        "command_sequence": [],
    }
    _write_json(repo_root / "services/backend/.local/ios-deploy-runbook-local.json", report)


def _write_npc_evaluation(repo_root: Path) -> None:
    report = {
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
        "cases": [],
    }
    _write_json(repo_root / "services/backend/.local/npc-evaluation-local.json", report)


def _write_three_d_evaluation(repo_root: Path) -> None:
    report = {
        "kind": "three_d_evaluation_report",
        "suite": "default-v0",
        "provider": "local",
        "total_cases": 20,
        "succeeded": 20,
        "failed": 0,
        "coverage": {
            "input_modes": {
                "text_prompt": 20,
                "single_image": 0,
                "multi_image": 0,
                "unknown": 0,
            },
            "variant_roles": {
                "game_asset": 20,
                "ios_scene_asset": 20,
            },
            "scene_loadable_cases": 20,
        },
        "cases": [],
    }
    _write_json(repo_root / "services/backend/.local/3d-evaluation-local.json", report)


def _write_visual_regression(repo_root: Path) -> None:
    report = {
        "kind": "visual_regression_report",
        "status": "passed",
        "summary": {"passed": 1, "failed": 0},
        "artifacts": [
            {
                "id": "p0.118_scene_load_proof",
                "status": "passed",
            }
        ],
    }
    _write_json(repo_root / "services/backend/.local/visual-regression-local.json", report)


def _write_json(path: Path, report: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report), encoding="utf-8")
