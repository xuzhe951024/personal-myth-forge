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
    assert report["first_blocker"]["id"] == "final_resource_fill_guide"
    assert report["first_blocker"]["status"] == "blocked"
    assert report["first_blocker"]["command"] == "make final-resource-fill-guide"
    assert report["first_blocker"]["would_write_backend_env"] is False
    assert report["first_blocker"]["would_write_ios_deploy_config"] is False
    assert report["first_blocker"]["validation_command"] == (
        "make final-configured-evidence-plan"
    )
    assert report["next_action"] == {
        **report["first_blocker"],
        "source": "first_blocker",
    }
    assert report["summary"]["commands_run"] == 0
    assert report["summary"]["consent_required"] == 0
    assert report["summary"]["planned_consent_steps"] == 3
    assert report["summary"]["live_provider_steps"] == 3
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
    assert "sk-" not in report_text
    assert "meshy-secret" not in report_text
    assert str(tmp_path) not in report_text


def test_configured_evidence_plan_exposes_device_action_bundle(
    tmp_path: Path,
) -> None:
    result = build_final_configured_evidence_plan_report(repo_root=tmp_path)
    report_text = json.dumps(result.report)

    bundle = result.report["device_action_bundle"]

    assert bundle["id"] == "final_configured_evidence_plan_device_actions"
    assert bundle["label"] == "Final Configured Evidence Plan Device Actions"
    assert bundle["source_report"] == "final_configured_preflight"
    assert bundle["status"] == "blocked"
    assert bundle["summary"]["actions"] == 7
    assert bundle["summary"]["provider_calls"] == 0
    assert bundle["summary"]["global_actions"] == 0
    assert bundle["summary"]["xcode_or_signing"] == 1
    assert bundle["first_action"]["id"] == "write_development_team"
    expected_command = (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto make mobile-write-deploy-config-auto; "
        "rerun make mobile-deploy-preflight"
    )
    assert bundle["first_action"]["command"] == expected_command
    assert bundle["first_action"]["validation_command"] == (
        "make mobile-deploy-preflight"
    )
    assert bundle["safety"]["commands_run"] is False
    assert bundle["safety"]["provider_calls"] is False
    assert bundle["safety"]["xcode_or_signing"] is False
    assert str(tmp_path) not in report_text
    assert "sk-" not in report_text


def test_configured_evidence_plan_source_reports_expose_device_action_bundle(
    tmp_path: Path,
) -> None:
    result = build_final_configured_evidence_plan_report(repo_root=tmp_path)
    report_text = json.dumps(result.report)

    bundle = result.report["source_reports"]["final_configured_preflight"][
        "device_action_bundle"
    ]

    assert bundle["id"] == "final_configured_preflight_device_actions"
    assert bundle["source_report"] == "configured_ios_deploy_runbook"
    assert bundle["status"] == "blocked"
    assert bundle["summary"]["actions"] == 7
    assert bundle["first_action"]["id"] == "write_development_team"
    expected_command = (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto make mobile-write-deploy-config-auto; "
        "rerun make mobile-deploy-preflight"
    )
    assert bundle["first_action"]["command"] == expected_command
    assert bundle["first_action"]["validation_command"] == (
        "make mobile-deploy-preflight"
    )
    assert result.report["device_action_bundle"]["source_report"] == (
        "final_configured_preflight"
    )
    assert bundle["safety"]["commands_run"] is False
    assert str(tmp_path) not in report_text
    assert "sk-" not in report_text


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
    assert steps["three_d_evaluation_configured"]["requires_cost_consent"] is True
    assert steps["three_d_evaluation_configured"]["live_provider_call"] is True
    assert steps["three_d_evaluation_configured"]["requires_user_confirmation"] is True
    assert steps["npc_evaluation_configured"]["status"] == "consent_required"
    assert steps["npc_evaluation_configured"]["command"] == (
        "make backend-evaluate-npc-configured"
    )
    assert steps["npc_evaluation_configured"]["requires_cost_consent"] is True
    assert steps["npc_evaluation_configured"]["live_provider_call"] is True
    assert steps["npc_evaluation_configured"]["requires_user_confirmation"] is True
    assert steps["final_acceptance_configured"]["status"] == "consent_required"
    assert steps["final_acceptance_configured"]["requires_cost_consent"] is True
    assert steps["final_acceptance_configured"]["live_provider_call"] is True
    assert steps["final_acceptance_configured"]["requires_user_confirmation"] is True
    assert steps["final_demo_launch_configured"]["command"] == (
        "make final-demo-launch-configured"
    )
    assert steps["live_provider_evidence"]["status"] == "ready_to_run"
    assert report["first_blocker"]["id"] == "three_d_evaluation_configured"
    assert report["first_blocker"]["status"] == "consent_required"
    assert report["first_blocker"]["command"] == (
        "PMF_ALLOW_LIVE_PROVIDER_CALLS=1 make backend-evaluate-3d-configured"
    )
    assert report["first_blocker"]["requires_live_provider_consent"] is True
    assert report["first_blocker"]["requires_cost_consent"] is True
    assert report["first_blocker"]["live_provider_call"] is True
    assert report["first_blocker"]["requires_user_confirmation"] is True
    assert report["first_blocker"]["cost_risk"] is True
    assert report["first_blocker"]["would_write_backend_env"] is False
    assert report["first_blocker"]["would_write_ios_deploy_config"] is False
    assert report["first_blocker"]["validation_command"] == (
        "make final-configured-evidence-plan"
    )
    assert report["next_action"]["id"] == "three_d_evaluation_configured"
    assert report["next_action"]["command"] == (
        "PMF_ALLOW_LIVE_PROVIDER_CALLS=1 make backend-evaluate-3d-configured"
    )
    assert report["next_action"]["source"] == "first_blocker"
    assert report["next_action"]["requires_cost_consent"] is True
    assert report["next_action"]["live_provider_call"] is True
    assert report["next_action"]["requires_user_confirmation"] is True
    assert report["operator_actions"][:2] == [
        (
            "PMF_ALLOW_LIVE_PROVIDER_CALLS=1 make backend-evaluate-3d-configured; "
            "rerun make final-configured-evidence-plan"
        ),
        (
            "PMF_ALLOW_LIVE_PROVIDER_CALLS=1 make backend-evaluate-npc-configured; "
            "rerun make final-configured-evidence-plan"
        ),
    ]
    assert not any(
        "final-acceptance-configured" in action
        for action in report["operator_actions"]
    )
    assert not any(
        "final-demo-launch-configured" in action
        for action in report["operator_actions"]
    )
    assert not any(
        action.startswith("review live provider cost consent")
        for action in report["operator_actions"]
    )
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


def test_configured_evidence_plan_surfaces_configured_preflight_child_blocker(
    tmp_path: Path,
) -> None:
    repo_root = _write_ready_resource_bundle(tmp_path)
    _write_blocked_final_acceptance(
        repo_root,
        blocker_id="mobile_deploy_preflight",
        command="make mobile-deploy-preflight",
        detail="Backend health failed from the iPhone.",
    )

    result = build_final_configured_evidence_plan_report(
        repo_root=repo_root,
        settings=_configured_settings(),
    )
    report = result.report
    step = report["steps_by_id"]["final_configured_preflight"]

    assert result.exit_code == 2
    assert report["status"] == "blocked"
    assert step["status"] == "blocked"
    assert step["blocked_by"] == ["mobile_deploy_preflight"]
    assert step["source_blocker_id"] == "mobile_deploy_preflight"
    assert step["source_blocker_command"] == "make mobile-deploy-preflight"
    assert step["source_blocker_detail"] == "Backend health failed from the iPhone."
    assert step["source_validation_command"] == "make final-acceptance-local"
    assert report["first_blocker"]["id"] == "final_configured_preflight"
    assert report["first_blocker"]["source_blocker_id"] == "mobile_deploy_preflight"
    assert report["first_blocker"]["command"] == "make mobile-deploy-preflight"
    assert report["first_blocker"]["detail"] == "Backend health failed from the iPhone."
    assert report["first_blocker"]["validation_command"] == (
        "make final-acceptance-local"
    )
    assert report["operator_actions"][0] == (
        "make mobile-deploy-preflight; rerun make final-acceptance-local; "
        "rerun make final-configured-evidence-plan"
    )


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
    assert report["first_blocker"] is None
    assert report["next_action"] is None


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


def _write_blocked_final_acceptance(
    repo_root: Path,
    *,
    blocker_id: str,
    command: str,
    detail: str,
) -> None:
    _write_json(
        repo_root / "services/backend/.local/final-acceptance-local.json",
        {
            "kind": "final_acceptance_report",
            "overall_status": "blocked",
            "summary": {"passed": 13, "blocked": 1, "failed": 0, "skipped": 0},
            "checks": [
                {
                    "id": blocker_id,
                    "label": "Mobile deploy preflight",
                    "status": "blocked",
                    "classification": "blocked_by_local_ios_backend_health",
                    "command": command,
                    "error": detail,
                }
            ],
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
