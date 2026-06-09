from __future__ import annotations

import json
from pathlib import Path

from myth_forge_api.config import Settings
from myth_forge_api.final_configured_evidence_plan import (
    build_final_configured_evidence_plan_report,
)


def test_configured_evidence_plan_blocks_missing_resources_without_running_commands(
    tmp_path: Path,
) -> None:
    result = build_final_configured_evidence_plan_report(repo_root=tmp_path)
    report = result.report
    report_text = json.dumps(report)

    assert result.exit_code == 2
    assert report["kind"] == "final_configured_evidence_plan_report"
    assert report["status"] == "blocked"
    assert report["steps_by_id"]["final_resource_fill_guide"]["status"] == "blocked"
    assert report["steps_by_id"]["final_resource_apply_preview"]["status"] == "blocked"
    assert report["steps_by_id"]["final_apply_resources"]["status"] == "blocked"
    assert report["steps_by_id"]["three_d_evaluation_configured"]["status"] == "blocked"
    assert report["steps_by_id"]["three_d_evaluation_configured"][
        "requires_live_provider_consent"
    ] is True
    assert report["summary"]["commands_run"] == 0
    assert report["summary"]["consent_required"] == 0
    assert report["summary"]["planned_consent_steps"] == 3
    assert report["summary"]["live_provider_steps"] == 3
    assert report["safety"]["commands_run"] is False
    assert report["safety"]["live_provider_calls"] is False
    assert report["safety"]["writes_backend_env"] is False
    assert report["safety"]["writes_ios_deploy_config"] is False
    assert "sk-" not in report_text
    assert "meshy-secret" not in report_text
    assert str(tmp_path) not in report_text


def test_configured_evidence_plan_requires_consent_with_ready_resources(
    tmp_path: Path,
) -> None:
    repo_root = _write_ready_resource_bundle(tmp_path)
    settings = _configured_settings()

    result = build_final_configured_evidence_plan_report(
        repo_root=repo_root,
        settings=settings,
    )
    report = result.report
    steps = report["steps_by_id"]
    report_text = json.dumps(report)

    assert result.exit_code == 2
    assert report["status"] == "consent_required"
    assert report["summary"]["blocked"] == 0
    assert report["summary"]["consent_required"] >= 3
    assert report["summary"]["planned_consent_steps"] == 3
    assert steps["final_resource_fill_guide"]["status"] == "ready"
    assert steps["final_resource_apply_preview"]["status"] == "ready"
    assert steps["final_apply_resources"]["status"] == "ready_to_run"
    assert steps["final_configured_preflight"]["status"] == "ready"
    assert steps["provider_handoff"]["status"] == "ready_to_run"
    assert steps["provider_handoff"]["command"] == "make provider-handoff"
    assert steps["three_d_evaluation_configured"]["status"] == "consent_required"
    assert steps["three_d_evaluation_configured"]["command"] == (
        "make backend-evaluate-3d-configured"
    )
    assert steps["npc_evaluation_configured"]["status"] == "consent_required"
    assert steps["npc_evaluation_configured"]["command"] == (
        "make backend-evaluate-npc-configured"
    )
    assert steps["final_acceptance_configured"]["status"] == "consent_required"
    assert steps["final_demo_launch_configured"]["command"] == (
        "make final-demo-launch-configured"
    )
    assert steps["live_provider_evidence"]["status"] == "ready_to_run"
    assert "make provider-handoff" in report["commands"]
    assert "make final-demo-launch-configured" in report["commands"]
    assert not any(
        "myth_forge_api.cli provider-handoff" in command
        or "final-demo-launch --mode configured" in command
        for command in report["commands"]
    )
    assert report["live_call_policy"]["allow_live_provider_calls"] is False
    assert report["safety"]["commands_run"] is False
    assert report["safety"]["live_provider_calls"] is False
    assert "sk-openai-test" not in report_text
    assert "meshy-secret-test" not in report_text
    assert "10.0.0.24" not in report_text
    assert str(tmp_path) not in report_text


def test_configured_evidence_plan_marks_live_steps_ready_to_run_with_consent(
    tmp_path: Path,
) -> None:
    repo_root = _write_ready_resource_bundle(tmp_path)
    settings = _configured_settings()

    result = build_final_configured_evidence_plan_report(
        repo_root=repo_root,
        settings=settings,
        allow_live_provider_calls=True,
    )
    report = result.report
    steps = report["steps_by_id"]

    assert result.exit_code == 2
    assert report["status"] == "ready_to_run"
    assert report["summary"]["blocked"] == 0
    assert report["summary"]["consent_required"] == 0
    assert report["summary"]["planned_consent_steps"] == 3
    assert steps["three_d_evaluation_configured"]["status"] == "ready_to_run"
    assert steps["npc_evaluation_configured"]["status"] == "ready_to_run"
    assert steps["final_acceptance_configured"]["status"] == "ready_to_run"
    assert steps["final_demo_launch_configured"]["status"] == "ready_to_run"
    assert report["live_call_policy"]["allow_live_provider_calls"] is True
    assert report["safety"]["commands_run"] is False
    assert report["safety"]["live_provider_calls"] is False


def test_configured_evidence_plan_is_ready_with_configured_evidence(
    tmp_path: Path,
) -> None:
    repo_root = _write_ready_resource_bundle(tmp_path)
    _write_ready_configured_evidence(repo_root)
    settings = _configured_settings()

    result = build_final_configured_evidence_plan_report(
        repo_root=repo_root,
        settings=settings,
    )
    report = result.report
    steps = report["steps_by_id"]

    assert result.exit_code == 0
    assert report["status"] == "ready"
    assert report["summary"]["ready"] == report["summary"]["steps"]
    assert report["summary"]["blocked"] == 0
    assert report["summary"]["consent_required"] == 0
    assert report["summary"]["planned_consent_steps"] == 0
    assert steps["provider_handoff"]["status"] == "ready"
    assert steps["three_d_evaluation_configured"]["status"] == "ready"
    assert steps["npc_evaluation_configured"]["status"] == "ready"
    assert steps["final_acceptance_configured"]["status"] == "ready"
    assert steps["final_demo_launch_configured"]["status"] == "ready"
    assert steps["live_provider_evidence"]["status"] == "ready"


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
