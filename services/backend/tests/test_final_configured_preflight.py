import json
from pathlib import Path

from myth_forge_api.config import Settings
from myth_forge_api.final_configured_preflight import (
    build_final_configured_preflight_report,
)


def test_configured_preflight_blocks_missing_resources_without_leaks(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)

    result = build_final_configured_preflight_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    report_text = json.dumps(result.report)

    assert result.exit_code == 2
    assert result.report["kind"] == "final_configured_preflight_report"
    assert result.report["status"] == "blocked"
    assert result.report["final_resources_preflight"]["status"] == "missing"
    assert result.report["provider_handoff"]["core_real_ready"] is False
    assert result.report["resource_handoff"]["summary"]["missing"] >= 3
    assert result.report["configured_final_launch"]["overall_status"] == "blocked"
    assert result.report["configured_ios_deploy_runbook"]["status"] == "blocked"
    assert "make final-apply-resources" in result.report["commands"]
    assert "make final-configured-preflight" in result.report["commands"]
    assert "--allow-live-provider-calls" in " ".join(result.report["commands"])
    assert result.report["safety"]["provider_calls"] is False
    assert result.report["safety"]["writes_backend_env"] is False
    assert result.report["safety"]["writes_ios_deploy_config"] is False
    assert result.report["safety"]["provider_secrets_in_report"] is False
    assert any("MESHY_API_KEY" in action for action in result.report["operator_actions"])
    assert str(tmp_path) not in report_text
    assert "sk-" not in report_text


def test_configured_preflight_is_ready_with_configured_handoff_inputs(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(
        tmp_path,
        local_config=(
            "DEVELOPMENT_TEAM = TEAM12345\n"
            "PRODUCT_BUNDLE_IDENTIFIER = com.zhexu.personalmythforge.dev\n"
            "PMF_BACKEND_BASE_URL = http://10.0.0.24:8080\n"
            "PMF_FINAL_LAUNCH_MODE = configured\n"
        ),
    )
    _write_final_resources(repo_root)
    _write_three_d_evaluation(repo_root)
    _write_npc_evaluation(repo_root)
    _write_final_acceptance(repo_root)
    settings = Settings(
        three_d_provider="meshy",
        meshy_api_key="sk-meshy-secret",
        npc_provider="openai",
        openai_api_key="sk-openai-secret",
        print_provider="treatstock",
        treatstock_api_key="treatstock-secret",
    )

    result = build_final_configured_preflight_report(
        settings=settings,
        repo_root=repo_root,
    )
    report_text = json.dumps(result.report)

    assert result.exit_code == 0
    assert result.report["status"] == "ready"
    assert result.report["summary"]["blocked"] == 0
    assert result.report["summary"]["missing"] == 0
    assert result.report["final_resources_preflight"]["status"] == "ready"
    assert result.report["provider_handoff"]["core_real_ready"] is True
    assert result.report["resource_handoff"]["summary"]["missing"] == 0
    assert result.report["resource_handoff"]["summary"]["blocked"] == 0
    assert result.report["configured_final_launch"]["mode"] == "configured"
    assert result.report["configured_final_launch"]["overall_status"] == "partial"
    assert result.report["configured_ios_deploy_runbook"]["mode"] == "configured"
    assert result.report["configured_ios_deploy_runbook"]["status"] == "partial"
    assert "make final-configured-preflight" in result.report["commands"]
    assert "make backend-device-demo" in result.report["commands"]
    assert "make mobile-deploy-preflight" in result.report["commands"]
    assert any(
        "live provider cost review" in action
        for action in result.report["operator_actions"]
    )
    assert result.report["safety"]["commands_run"] is False
    assert result.report["safety"]["provider_calls"] is False
    assert "sk-meshy-secret" not in report_text
    assert "sk-openai-secret" not in report_text
    assert "treatstock-secret" not in report_text
    assert str(tmp_path) not in report_text


def test_configured_preflight_cli_writes_report_and_makefile_exposes_target(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    output_path = tmp_path / "configured-preflight.json"

    from myth_forge_api.cli import main

    exit_code = main(
        [
            "final-configured-preflight",
            "--repo-root",
            str(repo_root),
            "--output",
            str(output_path),
        ]
    )

    assert exit_code == 2
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["kind"] == "final_configured_preflight_report"
    assert payload["status"] == "blocked"

    makefile = (Path(__file__).resolve().parents[3] / "Makefile").read_text(
        encoding="utf-8"
    )
    assert "final-configured-preflight:" in makefile
    assert "myth_forge_api.cli final-configured-preflight" in makefile


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
                "PRODUCT_BUNDLE_IDENTIFIER=com.zhexu.personalmythforge.dev",
                "PMF_BACKEND_BASE_URL=http://10.0.0.24:8080",
                "PMF_FINAL_LAUNCH_MODE=configured",
            ]
        ),
        encoding="utf-8",
    )


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
    acceptance = repo_root / "services/backend/.local/final-acceptance-local.json"
    acceptance.parent.mkdir(parents=True, exist_ok=True)
    acceptance.write_text(json.dumps(report), encoding="utf-8")


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
    evaluation = repo_root / "services/backend/.local/npc-evaluation-local.json"
    evaluation.parent.mkdir(parents=True, exist_ok=True)
    evaluation.write_text(json.dumps(report), encoding="utf-8")


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
    evaluation = repo_root / "services/backend/.local/3d-evaluation-local.json"
    evaluation.parent.mkdir(parents=True, exist_ok=True)
    evaluation.write_text(json.dumps(report), encoding="utf-8")
