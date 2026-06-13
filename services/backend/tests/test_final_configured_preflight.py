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
    provider_handoff = result.report["provider_handoff"]
    assert provider_handoff["status"] == "blocked"
    assert provider_handoff["classification"] == "core_real_providers_not_ready"
    assert provider_handoff["summary"]["providers"] >= 4
    assert provider_handoff["summary"]["core_total"] == 3
    assert provider_handoff["summary"]["core_real_ready"] == 1
    assert (
        "curl http://127.0.0.1:8080/v1/provider-readiness"
        in provider_handoff["next_commands"]
    )
    assert result.report["resource_handoff"]["summary"]["missing"] >= 3
    assert result.report["configured_final_launch"]["overall_status"] == "blocked"
    assert result.report["configured_ios_deploy_runbook"]["status"] == "blocked"
    assert "make final-apply-resources" in result.report["commands"]
    assert "make final-configured-preflight" in result.report["commands"]
    assert "make final-acceptance-configured" in result.report["commands"]
    assert (
        "approve live provider cost review before make final-acceptance-configured; "
        "--allow-live-provider-calls consent required"
    ) in result.report["operator_actions"]
    assert result.report["first_blocker"] == {
        "id": "final_resources_preflight",
        "label": "Final resources preflight",
        "status": "missing",
        "classification": "missing_file",
        "command": "make final-resource-init",
        "detail": "Create ignored final-resources.env before configured validation.",
        "source_kind": "final_resources_preflight_report",
        "source_id": "final_resources_file",
        "validation_command": "make final-resources-preflight",
    }
    assert result.report["next_action"] == {
        **result.report["first_blocker"],
        "source": "first_blocker",
    }
    assert result.report["safety"]["provider_calls"] is False
    assert result.report["safety"]["writes_backend_env"] is False
    assert result.report["safety"]["writes_ios_deploy_config"] is False
    assert result.report["safety"]["provider_secrets_in_report"] is False
    assert any("MESHY_API_KEY" in action for action in result.report["operator_actions"])
    assert str(tmp_path) not in report_text
    assert "sk-" not in report_text


def test_configured_preflight_resource_actions_include_validation_commands(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_incomplete_final_resources(repo_root)

    result = build_final_configured_preflight_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    actions = result.report["operator_actions"]

    assert (
        "provide MESHY_API_KEY in final-resources.env; "
        "rerun make final-resources-preflight"
    ) in actions
    assert (
        "provide OPENAI_API_KEY in final-resources.env; "
        "rerun make final-resources-preflight"
    ) in actions
    assert (
        "provide DEVELOPMENT_TEAM in final-resources.env; "
        "rerun make final-resources-preflight"
    ) in actions
    assert (
        "provide PRODUCT_BUNDLE_IDENTIFIER in final-resources.env; "
        "rerun make final-resources-preflight"
    ) in actions
    assert (
        "provide PMF_BACKEND_BASE_URL in final-resources.env; "
        "rerun make final-resources-preflight"
    ) in actions
    assert not any(
        action.endswith("provide MESHY_API_KEY in final-resources.env")
        or action.endswith("provide OPENAI_API_KEY in final-resources.env")
        or action.endswith("provide DEVELOPMENT_TEAM in final-resources.env")
        or action.endswith("provide PRODUCT_BUNDLE_IDENTIFIER in final-resources.env")
        or action.endswith("provide PMF_BACKEND_BASE_URL in final-resources.env")
        for action in actions
    )
    assert not any(
        " in final-resources.env; rerun " in action
        and not action.endswith("; rerun make final-resources-preflight")
        for action in actions
    )


def test_configured_preflight_operator_actions_use_make_target_for_provider_handoff(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)

    result = build_final_configured_preflight_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    actions = result.report["operator_actions"]

    assert "make provider-handoff" in actions
    assert not any("myth_forge_api.cli provider-handoff" in action for action in actions)
    assert not any("--output .local/provider-handoff.json" in action for action in actions)


def test_configured_preflight_operator_actions_drop_stale_unblock_fallbacks(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)

    result = build_final_configured_preflight_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    actions = result.report["operator_actions"]
    action_text = " ".join(actions)

    assert not any(action.startswith("unblock ") for action in actions)
    assert "unblock provider_readiness: make provider-handoff" not in actions
    assert (
        "unblock configured_final_acceptance: make final-acceptance-configured"
        not in actions
    )
    assert "make provider-handoff" in actions
    assert "make live-provider-evidence" in actions
    assert "live provider cost review" in action_text


def test_configured_preflight_operator_actions_gate_apply_behind_preview(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_final_resources(repo_root)

    result = build_final_configured_preflight_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    actions = result.report["operator_actions"]

    assert "make final-resource-apply-preview" in actions
    assert "make final-apply-resources" not in actions
    assert "make final-apply-resources" in result.report["commands"]
    assert not any(
        action.startswith("run make final-apply-resources") for action in actions
    )


def test_configured_preflight_ios_deploy_actions_include_validation_commands(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)

    result = build_final_configured_preflight_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    actions = result.report["operator_actions"]

    assert (
        "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig; "
        "rerun make mobile-deploy-preflight"
    ) in actions
    assert (
        "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL; "
        "rerun make mobile-deploy-preflight"
    ) in actions
    assert not any(
        action.endswith("provide DEVELOPMENT_TEAM in Deployment.local.xcconfig")
        or action.endswith("set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL")
        for action in actions
    )


def test_configured_preflight_exposes_device_action_bundle(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)

    result = build_final_configured_preflight_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    report_text = json.dumps(result.report)

    bundle = result.report["device_action_bundle"]

    assert bundle["id"] == "final_configured_preflight_device_actions"
    assert bundle["label"] == "Final Configured Preflight Device Actions"
    assert bundle["source_report"] == "configured_ios_deploy_runbook"
    assert bundle["status"] == "blocked"
    assert bundle["summary"]["actions"] == 7
    assert bundle["summary"]["provider_calls"] == 0
    assert bundle["summary"]["global_actions"] == 0
    assert bundle["summary"]["xcode_or_signing"] == 1
    assert bundle["first_action"]["id"] == "write_development_team"
    assert bundle["first_action"]["command"] == (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID make mobile-write-deploy-config-auto"
    )
    assert bundle["first_action"]["validation_command"] == (
        "make mobile-deploy-preflight"
    )
    assert bundle["safety"]["commands_run"] is False
    assert bundle["safety"]["provider_calls"] is False
    assert bundle["safety"]["xcode_or_signing"] is False
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
    provider_handoff = result.report["provider_handoff"]
    assert provider_handoff["status"] == "ready"
    assert provider_handoff["classification"] == "core_real_providers_ready"
    assert provider_handoff["summary"]["providers"] >= 4
    assert provider_handoff["summary"]["core_total"] == 3
    assert provider_handoff["summary"]["core_real_ready"] == 3
    assert provider_handoff["summary"]["missing_env"] == 0
    assert result.report["resource_handoff"]["summary"]["missing"] == 0
    assert result.report["resource_handoff"]["summary"]["blocked"] == 0
    assert result.report["configured_final_launch"]["mode"] == "configured"
    assert result.report["configured_final_launch"]["overall_status"] == "partial"
    assert result.report["configured_ios_deploy_runbook"]["mode"] == "configured"
    assert result.report["configured_ios_deploy_runbook"]["status"] == "partial"
    assert result.report["first_blocker"] is None
    assert result.report["next_action"] is None
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

    repo_root = Path(__file__).resolve().parents[3]
    makefile = (repo_root / "Makefile").read_text(encoding="utf-8")
    wrapper = (
        repo_root / "services/backend/scripts/write_final_configured_preflight.sh"
    ).read_text(encoding="utf-8")
    assert "final-configured-preflight:" in makefile
    assert "services/backend/scripts/write_final_configured_preflight.sh" in makefile
    assert "myth_forge_api.cli final-configured-preflight" in wrapper
    assert ".local/final-configured-preflight.json" in wrapper


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


def _write_incomplete_final_resources(repo_root: Path) -> None:
    resources = repo_root / "services/backend/.local/final-resources.env"
    resources.parent.mkdir(parents=True)
    resources.write_text(
        "\n".join(
            [
                "PRINT_PROVIDER=local",
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
