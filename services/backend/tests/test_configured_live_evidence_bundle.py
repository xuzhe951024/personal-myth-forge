import json
from pathlib import Path

from myth_forge_api.config import Settings
from myth_forge_api.configured_live_evidence_bundle import (
    build_configured_live_evidence_bundle_report,
)


def test_configured_live_evidence_bundle_blocks_missing_resources_without_running_commands(
    tmp_path: Path,
) -> None:
    result = build_configured_live_evidence_bundle_report(repo_root=tmp_path)
    report = result.report

    assert result.exit_code == 2
    assert report["kind"] == "configured_live_evidence_bundle_report"
    assert report["status"] == "blocked"
    assert report["summary"]["commands_run"] == 0
    assert report["summary"]["evidence_files"] == 5
    assert report["summary"]["evidence_missing"] == 5
    assert report["current_blocker"]["id"] == "final_resource_fill_guide"
    assert report["first_blocker"] == report["current_blocker"]
    assert report["next_action"] == {
        **report["first_blocker"],
        "source": "first_blocker",
    }
    assert report["source_reports"]["final_configured_evidence_plan"]["status"] == (
        "blocked"
    )
    assert report["source_reports"]["live_provider_evidence"]["status"] == "missing"
    assert report["safety"]["commands_run"] is False
    assert report["safety"]["live_provider_calls"] is False
    assert report["safety"]["writes_backend_env"] is False
    assert report["safety"]["writes_ios_deploy_config"] is False
    actions = report["operator_actions"]
    assert actions[:6] == [
        (
            "provide MESHY_API_KEY in final-resources.env; rerun "
            "make final-resources-preflight"
        ),
        "make final-resource-apply-preview",
        "make final-configured-preflight",
        "make provider-handoff",
        "make backend-evaluate-3d-configured",
        "make backend-evaluate-npc-configured",
    ]
    assert "make final-apply-resources" not in actions
    assert "make final-apply-resources" in report["commands"]
    assert "make live-provider-evidence" in actions
    assert not any(action.startswith("unblock ") for action in actions)
    assert "make configured-live-evidence-bundle" in report["commands"]


def test_configured_live_evidence_bundle_exposes_device_action_bundle(
    tmp_path: Path,
) -> None:
    result = build_configured_live_evidence_bundle_report(repo_root=tmp_path)
    report_text = json.dumps(result.report)

    bundle = result.report["device_action_bundle"]

    assert bundle["id"] == "configured_live_evidence_bundle_device_actions"
    assert bundle["label"] == "Configured Live Evidence Bundle Device Actions"
    assert bundle["source_report"] == "final_configured_evidence_plan"
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


def test_configured_live_evidence_bundle_source_reports_expose_device_action_bundle(
    tmp_path: Path,
) -> None:
    result = build_configured_live_evidence_bundle_report(repo_root=tmp_path)
    report_text = json.dumps(result.report)

    bundle = result.report["source_reports"]["final_configured_evidence_plan"][
        "device_action_bundle"
    ]

    assert bundle["id"] == "final_configured_evidence_plan_device_actions"
    assert bundle["source_report"] == "final_configured_preflight"
    assert bundle["status"] == "blocked"
    assert bundle["summary"]["actions"] == 7
    assert bundle["first_action"]["id"] == "write_development_team"
    assert bundle["first_action"]["command"] == (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID make mobile-write-deploy-config-auto"
    )
    assert bundle["first_action"]["validation_command"] == (
        "make mobile-deploy-preflight"
    )
    assert result.report["device_action_bundle"]["source_report"] == (
        "final_configured_evidence_plan"
    )
    assert bundle["safety"]["commands_run"] is False
    assert str(tmp_path) not in report_text
    assert "sk-" not in report_text


def test_configured_live_evidence_bundle_requires_consent_with_ready_resources(
    tmp_path: Path,
) -> None:
    repo_root = _write_ready_resource_bundle(tmp_path)

    result = build_configured_live_evidence_bundle_report(
        repo_root=repo_root,
        settings=_configured_settings(),
    )
    report = result.report
    command_sequence = report["command_sequence_by_id"]

    assert result.exit_code == 2
    assert report["status"] == "consent_required"
    assert report["summary"]["blocked_steps"] == 0
    assert report["summary"]["consent_required_steps"] >= 3
    assert report["current_blocker"]["id"] == "three_d_evaluation_configured"
    assert report["first_blocker"]["id"] == "three_d_evaluation_configured"
    assert report["first_blocker"]["status"] == "consent_required"
    assert report["next_action"] == {
        **report["first_blocker"],
        "source": "first_blocker",
    }
    assert command_sequence["three_d_evaluation_configured"]["status"] == (
        "consent_required"
    )
    assert command_sequence["three_d_evaluation_configured"][
        "requires_live_provider_consent"
    ] is True
    assert report["live_call_policy"]["allow_live_provider_calls"] is False
    assert report["safety"]["commands_run"] is False
    assert report["safety"]["live_provider_calls"] is False


def test_configured_live_evidence_bundle_is_ready_to_run_with_consent(
    tmp_path: Path,
) -> None:
    repo_root = _write_ready_resource_bundle(tmp_path)

    result = build_configured_live_evidence_bundle_report(
        repo_root=repo_root,
        settings=_configured_settings(),
        allow_live_provider_calls=True,
    )
    report = result.report
    command_sequence = report["command_sequence_by_id"]

    assert result.exit_code == 2
    assert report["status"] == "ready_to_run"
    assert report["current_blocker"] is None
    assert report["first_blocker"] is None
    assert report["next_action"] is None
    assert command_sequence["three_d_evaluation_configured"]["status"] == (
        "ready_to_run"
    )
    assert command_sequence["npc_evaluation_configured"]["status"] == "ready_to_run"
    assert command_sequence["final_acceptance_configured"]["status"] == "ready_to_run"
    assert report["live_call_policy"]["allow_live_provider_calls"] is True
    assert report["summary"]["commands_run"] == 0


def test_configured_live_evidence_bundle_is_ready_with_saved_evidence(
    tmp_path: Path,
) -> None:
    repo_root = _write_ready_resource_bundle(tmp_path)
    _write_ready_configured_evidence(repo_root)

    result = build_configured_live_evidence_bundle_report(
        repo_root=repo_root,
        settings=_configured_settings(),
    )
    report = result.report

    assert result.exit_code == 0
    assert report["status"] == "ready"
    assert report["current_blocker"] is None
    assert report["first_blocker"] is None
    assert report["next_action"] is None
    assert report["summary"]["evidence_ready"] == 5
    assert report["summary"]["evidence_missing"] == 0
    assert report["summary"]["commands_ready"] == report["summary"]["commands"]
    assert report["operator_actions"] == []
    assert report["evidence_files_by_id"]["provider_handoff"]["status"] == "ready"


def test_configured_live_evidence_bundle_redacts_unsafe_saved_report_text(
    tmp_path: Path,
) -> None:
    repo_root = _write_ready_resource_bundle(tmp_path)
    _write_ready_configured_evidence(repo_root)
    _write_json(
        repo_root / "services/backend/.local/3d-evaluation-configured.json",
        {
            "kind": "three_d_evaluation_report",
            "provider": "meshy",
            "suite": "default-v0",
            "total_cases": 20,
            "succeeded": 19,
            "failed": 1,
            "errors": [
                (
                    "Authorization Bearer secret-token sk-live-secret "
                    "file:///tmp/private.glb https://checkout.example/pay "
                    "http://10.0.0.24:8080"
                )
            ],
        },
    )

    result = build_configured_live_evidence_bundle_report(
        repo_root=repo_root,
        settings=_configured_settings(),
    )
    report_text = json.dumps(result.report)

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert result.report["current_blocker"]["id"] == "three_d_evaluation_configured"
    assert result.report["first_blocker"]["id"] == "three_d_evaluation_configured"
    assert result.report["next_action"] == {
        **result.report["first_blocker"],
        "source": "first_blocker",
    }
    assert "secret-token" not in report_text
    assert "sk-live-secret" not in report_text
    assert "file://" not in report_text
    assert "checkout.example" not in report_text
    assert "10.0.0.24" not in report_text
    assert str(repo_root) not in report_text


def test_configured_live_evidence_bundle_cli_writes_report(tmp_path: Path) -> None:
    output = tmp_path / "configured-live-evidence-bundle.json"

    from myth_forge_api.cli import main

    exit_code = main(
        [
            "configured-live-evidence-bundle",
            "--repo-root",
            str(tmp_path),
            "--output",
            str(output),
        ]
    )

    assert exit_code == 2
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["kind"] == "configured_live_evidence_bundle_report"
    assert payload["status"] == "blocked"


def _configured_settings() -> Settings:
    return Settings(
        three_d_provider="meshy",
        meshy_api_key="meshy-secret-test",
        npc_provider="openai",
        openai_api_key="sk-openai-test",
        print_provider="local",
    )


def _write_ready_resource_bundle(tmp_path: Path) -> Path:
    repo_root = tmp_path / "repo"
    _write_deploy_config(repo_root)
    _write_local_rehearsal_reports(repo_root)
    resources = repo_root / "services/backend/.local/final-resources.env"
    resources.parent.mkdir(parents=True, exist_ok=True)
    resources.write_text(
        "\n".join(
            [
                "MESHY_API_KEY=meshy-secret-test",
                "OPENAI_API_KEY=sk-openai-test",
                "PRINT_PROVIDER=local",
                "DEVELOPMENT_TEAM=TEAM12345",
                "PRODUCT_BUNDLE_IDENTIFIER=com.zhexu.personalmythforge.dev",
                "PMF_BACKEND_BASE_URL=http://10.0.0.24:8080",
                "PMF_FINAL_LAUNCH_MODE=configured",
            ]
        ),
        encoding="utf-8",
    )
    return repo_root


def _write_deploy_config(repo_root: Path) -> None:
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
    (config_dir / "Deployment.local.xcconfig").write_text(
        "\n".join(
            [
                "DEVELOPMENT_TEAM = TEAM12345",
                "PRODUCT_BUNDLE_IDENTIFIER = com.zhexu.personalmythforge.dev",
                "PMF_BACKEND_BASE_URL = http://10.0.0.24:8080",
                "PMF_FINAL_LAUNCH_MODE = configured",
            ]
        ),
        encoding="utf-8",
    )


def _write_ready_configured_evidence(repo_root: Path) -> None:
    _write_json(
        repo_root / "services/backend/.local/provider-handoff.json",
        {
            "kind": "provider_handoff_report",
            "core_real_ready": True,
            "overall_real_ready": True,
            "missing_env": [],
        },
    )
    _write_json(
        repo_root / "services/backend/.local/3d-evaluation-configured.json",
        {
            "kind": "three_d_evaluation_report",
            "provider": "meshy",
            "suite": "default-v0",
            "total_cases": 20,
            "succeeded": 20,
            "failed": 0,
        },
    )
    _write_json(
        repo_root / "services/backend/.local/npc-evaluation-configured.json",
        {
            "kind": "npc_agent_evaluation_report",
            "provider": "openai",
            "suite": "default-v0",
            "total_cases": 6,
            "succeeded": 6,
            "failed": 0,
        },
    )
    _write_json(
        repo_root / "services/backend/.local/final-acceptance-configured.json",
        {
            "kind": "final_acceptance_report",
            "profile": "quick",
            "provider_mode": "configured",
            "overall_status": "passed",
            "summary": {"passed": 14, "blocked": 0, "failed": 0, "skipped": 0},
        },
    )
    _write_json(
        repo_root / "services/backend/.local/final-demo-launch-configured.json",
        {
            "kind": "final_demo_launch_report",
            "mode": "configured",
            "overall_status": "ready",
            "summary": {"ready": 9, "missing": 0, "blocked": 0, "manual": 0},
        },
    )


def _write_local_rehearsal_reports(repo_root: Path) -> None:
    _write_json(
        repo_root / "services/backend/.local/3d-evaluation-local.json",
        {
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
        },
    )
    _write_json(
        repo_root / "services/backend/.local/npc-evaluation-local.json",
        {
            "kind": "npc_agent_evaluation_report",
            "suite": "default-v0",
            "provider": "local",
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
        },
    )
    _write_json(
        repo_root / "services/backend/.local/final-acceptance-local.json",
        {
            "kind": "final_acceptance_report",
            "overall_status": "passed",
            "summary": {"passed": 14, "blocked": 0, "failed": 0, "skipped": 0},
        },
    )


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
