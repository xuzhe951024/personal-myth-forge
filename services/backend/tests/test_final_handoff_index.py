import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

import myth_forge_api.final_handoff_index as final_handoff_index
from myth_forge_api.config import Settings
from myth_forge_api.final_handoff_index import build_final_handoff_index_report

LEGACY_PRINT_QUOTE_ACTION = (
    "after explicit Treatstock cost consent, save a sanitized "
    "services/backend/.local/print-quote-configured.json from POST "
    "/v1/print-quotes; rerun make print-fulfillment-readiness"
)
GUARDED_PRINT_QUOTE_ACTION = (
    "PMF_ALLOW_PRINT_PROVIDER_CALLS=1 make print-quote-configured; "
    "rerun make print-fulfillment-readiness"
)
GUARDED_LIVE_ACCEPTANCE_ACTION = (
    "PMF_ALLOW_LIVE_PROVIDER_CALLS=1 make final-acceptance-configured; "
    "rerun make live-provider-evidence"
)


def test_final_handoff_index_dedupes_legacy_print_quote_handoff_actions() -> None:
    actions = final_handoff_index._operator_actions(
        [
            {
                "id": "local_rehearsal",
                "status": "blocked",
                "operator_actions": [
                    LEGACY_PRINT_QUOTE_ACTION,
                    GUARDED_PRINT_QUOTE_ACTION,
                    f"final_demo_launch_local: {LEGACY_PRINT_QUOTE_ACTION}",
                    f"final_demo_launch_local: {GUARDED_PRINT_QUOTE_ACTION}",
                ],
            }
        ]
    )

    assert GUARDED_PRINT_QUOTE_ACTION in actions
    assert all("after explicit Treatstock cost consent" not in action for action in actions)
    assert sum("print-quote-configured" in action for action in actions) == 1


def test_final_handoff_index_blocks_missing_reports_without_leaks(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)

    result = build_final_handoff_index_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    report_text = json.dumps(result.report)
    lanes = result.report["lanes_by_id"]

    assert result.exit_code == 2
    assert result.report["kind"] == "final_handoff_index_report"
    assert result.report["status"] == "blocked"
    assert result.report["summary"]["missing"] >= 1
    assert lanes["local_rehearsal"]["status"] == "missing"
    assert lanes["configured_preflight"]["status"] == "blocked"
    assert lanes["live_acceptance"]["status"] == "live"
    assert lanes["live_acceptance"]["requires_consent"] is True
    assert result.report["first_blocker"] == {
        "id": "local_rehearsal",
        "label": "Local rehearsal",
        "status": "missing",
        "classification": "lane_missing",
        "command": "make final-rehearsal-local",
        "detail": "run make final-rehearsal-local",
    }
    assert result.report["next_action"] == {
        "id": "local_rehearsal",
        "label": "Local rehearsal",
        "status": "missing",
        "classification": "lane_missing",
        "command": "make final-rehearsal-local",
        "detail": "run make final-rehearsal-local",
        "source": "first_blocker",
        "validation_command": "make final-rehearsal-local",
    }
    assert "make final-rehearsal-local" in result.report["commands"]
    assert "make final-configured-preflight" in result.report["commands"]
    assert "make final-handoff-index" in result.report["commands"]
    assert "make final-acceptance-configured" in result.report["commands"]
    assert GUARDED_LIVE_ACCEPTANCE_ACTION in result.report["operator_actions"]
    assert not any(
        action.startswith("approve live provider cost review")
        for action in result.report["operator_actions"]
    )
    assert result.report["operator_actions"][:2] == [
        "make final-rehearsal-local",
        "make final-configured-preflight; rerun make configured-live-evidence-bundle",
    ]
    assert result.report["safety"]["provider_calls"] is False
    assert result.report["safety"]["commands_run"] is False
    assert result.report["safety"]["writes_backend_env"] is False
    assert result.report["safety"]["writes_ios_deploy_config"] is False
    assert str(tmp_path) not in report_text
    assert "sk-" not in report_text


def test_final_handoff_index_ready_when_local_and_configured_inputs_are_ready(
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
    _write_local_rehearsal_reports(repo_root)
    settings = Settings(
        three_d_provider="meshy",
        meshy_api_key="sk-meshy-secret",
        npc_provider="openai",
        openai_api_key="sk-openai-secret",
        print_provider="treatstock",
        treatstock_api_key="treatstock-secret",
    )

    result = build_final_handoff_index_report(
        settings=settings,
        repo_root=repo_root,
    )
    report_text = json.dumps(result.report)
    lanes = result.report["lanes_by_id"]
    source_reports = {
        source["id"]: source
        for source in result.report["source_reports"]
    }

    assert result.exit_code == 0
    assert result.report["status"] == "ready"
    assert result.report["first_blocker"] is None
    assert result.report["next_action"] is None
    assert result.report["summary"]["missing"] == 0
    assert result.report["summary"]["blocked"] == 0
    assert lanes["local_rehearsal"]["status"] == "ready"
    assert lanes["configured_preflight"]["status"] == "ready"
    assert lanes["configured_launch"]["status"] == "partial"
    assert lanes["configured_launch"]["command"] == "make final-demo-launch-configured"
    assert lanes["device_deploy"]["status"] == "partial"
    assert lanes["live_acceptance"]["status"] == "live"
    assert lanes["live_acceptance"]["requires_consent"] is True
    assert source_reports["visual_regression"]["status"] == "ready"
    assert source_reports["visual_regression"]["path"] == (
        "services/backend/.local/visual-regression-local.json"
    )
    assert source_reports["visual_regression"]["command"] == "make visual-regression-local"
    assert source_reports["final_configured_preflight"]["status"] == "ready"
    assert source_reports["final_configured_preflight"]["exists"] is False
    assert result.report["operator_sequence"][0]["command"] == "make final-rehearsal-local"
    assert result.report["operator_sequence"][1]["command"] == "make final-configured-preflight"
    assert result.report["operator_sequence"][2]["command"] == "make final-handoff-index"
    assert "make final-demo-launch-configured" in result.report["commands"]
    assert not any(
        "final-demo-launch --mode configured" in command
        for command in result.report["commands"]
    )
    assert "make backend-device-demo" in result.report["commands"]
    assert "make mobile-deploy-preflight" in result.report["commands"]
    assert "sk-meshy-secret" not in report_text
    assert "sk-openai-secret" not in report_text
    assert "treatstock-secret" not in report_text
    assert str(tmp_path) not in report_text


def test_final_handoff_index_local_lane_uses_saved_blocker_detail(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_three_d_evaluation(repo_root)
    _write_npc_evaluation(repo_root)
    _write_visual_regression(repo_root)
    _write_json(
        repo_root / "services/backend/.local/final-acceptance-local.json",
        {
            "kind": "final_acceptance_report",
            "overall_status": "blocked",
            "summary": {"passed": 12, "blocked": 1, "failed": 0, "skipped": 0},
        },
    )
    _write_ios_deploy_runbook(repo_root)
    _write_final_demo_launch(
        repo_root,
        overall_status="partial",
        first_blocker={
            "id": "mobile_deploy_preflight",
            "label": "Run iOS deploy preflight",
            "status": "blocked",
            "classification": "final_demo_launch_phase",
            "command": "make mobile-deploy-preflight",
            "detail": (
                "physical iPhone backend health gate | Checks local config and "
                "backend /health; does not build or sign. | Missing DEVELOPMENT_TEAM; "
                "PMF_BACKEND_BASE_URL must be iPhone-reachable"
            ),
        },
        next_action={
            "id": "mobile_deploy_preflight",
            "label": "Run iOS deploy preflight",
            "status": "blocked",
            "classification": "final_demo_launch_phase",
            "command": "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig",
            "detail": (
                "physical iPhone backend health gate | Checks local config and "
                "backend /health; does not build or sign. | Missing DEVELOPMENT_TEAM; "
                "PMF_BACKEND_BASE_URL must be iPhone-reachable"
            ),
            "validation_command": "make mobile-deploy-preflight",
        },
        operator_actions=[
            (
                "mobile_deploy_preflight: Missing DEVELOPMENT_TEAM; "
                "PMF_BACKEND_BASE_URL must be iPhone-reachable"
            )
        ],
    )

    result = build_final_handoff_index_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    lanes = result.report["lanes_by_id"]
    report_text = json.dumps(result.report)
    expected_detail = (
        "final_demo_launch_local: physical iPhone backend health gate | "
        "Checks local config and backend /health; does not build or sign. | "
        "Missing DEVELOPMENT_TEAM; PMF_BACKEND_BASE_URL must be iPhone-reachable"
    )

    assert result.exit_code == 2
    assert lanes["local_rehearsal"]["status"] == "blocked"
    assert lanes["local_rehearsal"]["detail"] == expected_detail
    assert result.report["first_blocker"]["detail"] == expected_detail
    next_action = result.report["next_action"]
    expected_command = (
        "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig; "
        "rerun make mobile-deploy-preflight"
    )
    assert result.report["first_blocker"]["command"] == expected_command
    assert next_action["id"] == "local_rehearsal"
    assert next_action["source"] == "first_blocker"
    assert next_action["command"] == expected_command
    assert next_action["validation_command"] == "make mobile-deploy-preflight"
    assert next_action["detail"] == expected_detail
    assert result.report["operator_actions"][0] == (
        "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig; "
        "rerun make mobile-deploy-preflight"
    )
    assert not any(
        action.startswith("final_demo_launch_local:")
        for action in result.report["operator_actions"]
    )
    assert "MESHY_API_KEY" not in report_text


def test_final_handoff_index_does_not_copy_live_provider_actions_into_local_lane(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_three_d_evaluation(repo_root)
    _write_npc_evaluation(repo_root)
    _write_visual_regression(repo_root)
    _write_json(
        repo_root / "services/backend/.local/final-acceptance-local.json",
        {
            "kind": "final_acceptance_report",
            "overall_status": "blocked",
            "summary": {"passed": 12, "blocked": 1, "failed": 0, "skipped": 0},
        },
    )
    _write_ios_deploy_runbook(repo_root)
    live_action = (
        "PMF_ALLOW_LIVE_PROVIDER_CALLS=1 make final-acceptance-configured; "
        "rerun make live-provider-evidence"
    )
    _write_final_demo_launch(
        repo_root,
        overall_status="partial",
        first_blocker={
            "id": "game_asset_3d_generation",
            "label": "Game asset 3D generation",
            "status": "partial",
            "classification": "live_3d_provider_unproven",
            "command": live_action,
            "detail": f"Live Meshy evidence still needs consent. Next: {live_action}",
        },
        next_action={
            "id": "game_asset_3d_generation",
            "label": "Game asset 3D generation",
            "status": "partial",
            "classification": "live_3d_provider_unproven",
            "command": live_action,
            "detail": f"Live Meshy evidence still needs consent. Next: {live_action}",
            "validation_command": "make live-provider-evidence",
        },
        operator_actions=[live_action, "make live-provider-evidence"],
    )

    result = build_final_handoff_index_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    local_lane = result.report["lanes_by_id"]["local_rehearsal"]

    assert result.exit_code == 2
    assert local_lane["status"] == "blocked"
    assert "operator_action" not in local_lane
    assert "PMF_ALLOW_LIVE_PROVIDER_CALLS" not in local_lane.get("detail", "")
    assert "final-acceptance-configured" not in local_lane.get("detail", "")
    assert not any(
        "live-provider-evidence" in action
        for action in local_lane.get("operator_actions", [])
    )
    assert result.report["first_blocker"]["id"] == "local_rehearsal"
    assert result.report["first_blocker"]["command"] == "make final-rehearsal-local"
    assert result.report["first_blocker"]["detail"] == "run make final-rehearsal-local"
    assert result.report["next_action"]["command"] == "make final-rehearsal-local"
    assert "final-acceptance-configured" not in result.report["next_action"]["detail"]
    assert not any(
        action.startswith("final_demo_launch_local:")
        and "live-provider-evidence" in action
        for action in result.report["operator_actions"]
    )
    assert any(
        "make final-acceptance-configured" in action
        for action in result.report["operator_actions"]
    )


def test_final_handoff_index_promotes_local_lane_operator_action_to_next_action(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_three_d_evaluation(repo_root)
    _write_npc_evaluation(repo_root)
    _write_visual_regression(repo_root)
    _write_json(
        repo_root / "services/backend/.local/final-acceptance-local.json",
        {
            "kind": "final_acceptance_report",
            "overall_status": "blocked",
            "summary": {"passed": 12, "blocked": 1, "failed": 0, "skipped": 0},
        },
    )
    _write_ios_deploy_runbook(repo_root)
    _write_final_demo_launch(
        repo_root,
        overall_status="partial",
        first_blocker={
            "id": "mobile_deploy_preflight",
            "label": "Run iOS deploy preflight",
            "status": "blocked",
            "classification": "final_demo_launch_phase",
            "command": "make mobile-deploy-preflight",
            "detail": (
                "physical iPhone backend health gate | Missing DEVELOPMENT_TEAM; "
                "PMF_BACKEND_BASE_URL must be iPhone-reachable"
            ),
        },
        next_action={
            "id": "mobile_deploy_preflight",
            "label": "Run iOS deploy preflight",
            "status": "blocked",
            "classification": "final_demo_launch_phase",
            "command": (
                "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto "
                "make mobile-write-deploy-config-auto"
            ),
            "detail": (
                "Missing DEVELOPMENT_TEAM; PMF_BACKEND_BASE_URL must be "
                "iPhone-reachable"
            ),
            "validation_command": "make mobile-deploy-preflight",
        },
        operator_actions=[
            (
                "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto "
                "make mobile-write-deploy-config-auto; "
                "rerun make mobile-deploy-preflight"
            ),
            (
                "start backend-device-demo before device checks: "
                "make backend-device-demo; rerun make mobile-deploy-preflight"
            ),
            (
                "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL; "
                "rerun make mobile-deploy-preflight"
            ),
        ],
    )

    result = build_final_handoff_index_report(
        settings=Settings(),
        repo_root=repo_root,
    )

    expected_command = (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto make mobile-write-deploy-config-auto; "
        "rerun make mobile-deploy-preflight"
    )

    assert result.exit_code == 2
    assert result.report["first_blocker"]["command"] == expected_command
    assert result.report["next_action"]["command"] == expected_command
    assert result.report["next_action"]["validation_command"] == (
        "make mobile-deploy-preflight"
    )


def test_final_handoff_index_promotes_provider_and_print_handoff_from_final_demo(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_three_d_evaluation(repo_root)
    _write_npc_evaluation(repo_root)
    _write_visual_regression(repo_root)
    _write_json(
        repo_root / "services/backend/.local/final-acceptance-local.json",
        {
            "kind": "final_acceptance_report",
            "overall_status": "blocked",
            "summary": {"passed": 12, "blocked": 1, "failed": 0, "skipped": 0},
        },
    )
    _write_ios_deploy_runbook(repo_root)
    _write_final_demo_launch(
        repo_root,
        overall_status="partial",
        next_action={
            "id": "mobile_deploy_preflight",
            "label": "Run iOS deploy preflight",
            "status": "blocked",
            "classification": "final_demo_launch_phase",
            "command": (
                "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto "
                "make mobile-write-deploy-config-auto"
            ),
            "detail": (
                "Missing DEVELOPMENT_TEAM; PMF_BACKEND_BASE_URL must be "
                "iPhone-reachable"
            ),
            "validation_command": "make mobile-deploy-preflight",
        },
        operator_actions=[
            (
                "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto "
                "make mobile-write-deploy-config-auto; "
                "rerun make mobile-deploy-preflight"
            ),
            "make provider-handoff; rerun make live-provider-evidence",
            (
                "PMF_ALLOW_PRINT_PROVIDER_CALLS=1 make print-quote-configured; rerun make print-fulfillment-readiness"
            ),
            (
                "provide PRODUCT_BUNDLE_IDENTIFIER in Deployment.local.xcconfig; "
                "rerun make mobile-deploy-preflight"
            ),
            (
                "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL; "
                "rerun make mobile-deploy-preflight"
            ),
            (
                "start backend-device-demo before device checks: "
                "make backend-device-demo; rerun make mobile-deploy-preflight"
            ),
            (
                "provide MESHY_API_KEY in final-resources.env; "
                "rerun make final-resources-preflight"
            ),
        ],
    )

    result = build_final_handoff_index_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    actions = result.report["operator_actions"]
    provider_action = "make provider-handoff; rerun make live-provider-evidence"
    print_action = (
        "PMF_ALLOW_PRINT_PROVIDER_CALLS=1 make print-quote-configured; rerun make print-fulfillment-readiness"
    )
    lan_backend_url_action = (
        "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL; "
        "rerun make mobile-deploy-preflight"
    )
    backend_device_demo_action = (
        "start backend-device-demo before device checks: "
        "make backend-device-demo; rerun make mobile-deploy-preflight"
    )

    assert actions[0] == (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto make mobile-write-deploy-config-auto; "
        "rerun make mobile-deploy-preflight"
    )
    assert len(actions) <= 6
    assert lan_backend_url_action in actions
    assert backend_device_demo_action in actions
    assert provider_action in actions
    assert print_action in actions
    assert actions.index(lan_backend_url_action) < actions.index(provider_action)
    assert actions.index(backend_device_demo_action) < actions.index(provider_action)
    assert actions.index(provider_action) < actions.index(print_action)
    assert actions.index(print_action) < actions.index(
        "make final-configured-preflight; rerun make configured-live-evidence-bundle"
    )


def test_final_handoff_index_prioritizes_backend_demo_before_backend_url_and_provider(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_three_d_evaluation(repo_root)
    _write_npc_evaluation(repo_root)
    _write_visual_regression(repo_root)
    _write_json(
        repo_root / "services/backend/.local/final-acceptance-local.json",
        {
            "kind": "final_acceptance_report",
            "overall_status": "blocked",
            "summary": {"passed": 12, "blocked": 1, "failed": 0, "skipped": 0},
        },
    )
    _write_ios_deploy_runbook(repo_root)
    _write_final_demo_launch(
        repo_root,
        overall_status="partial",
        next_action={
            "id": "mobile_deploy_preflight",
            "label": "Run iOS deploy preflight",
            "status": "blocked",
            "classification": "final_demo_launch_phase",
            "command": (
                "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto "
                "make mobile-write-deploy-config-auto"
            ),
            "detail": (
                "Missing DEVELOPMENT_TEAM; PMF_BACKEND_BASE_URL must be "
                "iPhone-reachable"
            ),
            "validation_command": "make mobile-deploy-preflight",
        },
        operator_actions=[
            (
                "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto "
                "make mobile-write-deploy-config-auto; "
                "rerun make mobile-deploy-preflight"
            ),
            (
                "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL; "
                "rerun make mobile-deploy-preflight"
            ),
            (
                "start backend-device-demo before device checks: "
                "make backend-device-demo; rerun make mobile-deploy-preflight"
            ),
            "make provider-handoff; rerun make live-provider-evidence",
            (
                "PMF_ALLOW_PRINT_PROVIDER_CALLS=1 make print-quote-configured; "
                "rerun make print-fulfillment-readiness"
            ),
        ],
    )

    result = build_final_handoff_index_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    actions = result.report["operator_actions"]
    deploy_writer_action = (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto make mobile-write-deploy-config-auto; "
        "rerun make mobile-deploy-preflight"
    )
    backend_demo_action = (
        "start backend-device-demo before device checks: "
        "make backend-device-demo; rerun make mobile-deploy-preflight"
    )
    backend_url_action = (
        "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL; "
        "rerun make mobile-deploy-preflight"
    )
    provider_action = "make provider-handoff; rerun make live-provider-evidence"
    print_action = (
        "PMF_ALLOW_PRINT_PROVIDER_CALLS=1 make print-quote-configured; "
        "rerun make print-fulfillment-readiness"
    )

    assert actions[:2] == [deploy_writer_action, backend_demo_action]
    assert actions.index(backend_demo_action) < actions.index(backend_url_action)
    assert actions.index(backend_demo_action) < actions.index(provider_action)
    assert actions.index(backend_demo_action) < actions.index(print_action)


def test_final_handoff_index_exposes_device_action_bundle(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_three_d_evaluation(repo_root)
    _write_npc_evaluation(repo_root)
    _write_visual_regression(repo_root)
    _write_final_acceptance(repo_root)
    _write_ios_deploy_runbook(repo_root)
    _write_final_demo_launch(
        repo_root,
        overall_status="partial",
        next_action={
            "id": "mobile_deploy_preflight",
            "label": "Run iOS deploy preflight",
            "status": "blocked",
            "classification": "final_demo_launch_phase",
            "command": (
                "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto "
                "make mobile-write-deploy-config-auto"
            ),
            "detail": "Missing DEVELOPMENT_TEAM.",
            "validation_command": "make mobile-deploy-preflight",
        },
        device_action_bundle={
            "id": "final_demo_launch_device_actions",
            "status": "blocked",
            "actions": [
                {
                    "id": "run_mobile_deploy_preflight",
                    "label": "Run mobile deploy preflight",
                    "status": "blocked",
                    "classification": "manual_preflight_required",
                    "command": "make mobile-deploy-preflight",
                    "detail": "Verify iPhone backend access.",
                    "manual": True,
                    "provider_calls": False,
                    "global_action": False,
                    "xcode_or_signing": False,
                    "validation_command": "make mobile-deploy-preflight",
                    "next_action": {
                        "id": "mobile_deploy_preflight",
                        "label": "Mobile deploy preflight",
                        "status": "blocked",
                        "command": (
                            "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto "
                            "make mobile-write-deploy-config-auto"
                        ),
                        "detail": "Missing DEVELOPMENT_TEAM.",
                        "source": "first_blocker",
                        "validation_command": "make mobile-deploy-preflight",
                    },
                },
                {
                    "id": "resolve_xcode_build_gate",
                    "label": "Resolve Xcode build gate",
                    "status": "blocked",
                    "classification": "manual_xcode_or_signing_required",
                    "command": "open Xcode and resolve signing/build gate",
                    "detail": "Resolve signing before launch proof.",
                    "manual": True,
                    "provider_calls": False,
                    "global_action": False,
                    "xcode_or_signing": True,
                },
            ],
            "first_action": {
                "id": "run_mobile_deploy_preflight",
                "label": "Run mobile deploy preflight",
                "status": "blocked",
                "classification": "manual_preflight_required",
                "command": (
                    "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto "
                    "make mobile-write-deploy-config-auto"
                ),
                "detail": "Verify iPhone backend access.",
                "manual": True,
                "provider_calls": False,
                "global_action": False,
                "xcode_or_signing": False,
                "validation_command": "make mobile-deploy-preflight",
            },
        },
    )

    result = build_final_handoff_index_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    report_text = json.dumps(result.report)
    bundle = result.report["device_action_bundle"]

    assert bundle["id"] == "final_handoff_index_device_actions"
    assert bundle["label"] == "Final Handoff Index Device Actions"
    assert bundle["source_report"] == "final_demo_launch_local"
    assert bundle["status"] == "blocked"
    assert bundle["summary"]["actions"] == 2
    assert bundle["summary"]["xcode_or_signing"] == 1
    assert bundle["summary"]["provider_calls"] == 0
    assert bundle["summary"]["global_actions"] == 0
    assert bundle["first_action"]["id"] == "run_mobile_deploy_preflight"
    assert bundle["first_action"]["command"] == (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto make mobile-write-deploy-config-auto"
    )
    assert bundle["first_action"]["validation_command"] == (
        "make mobile-deploy-preflight"
    )
    assert bundle["safety"]["commands_run"] is False
    assert bundle["safety"]["provider_calls"] is False
    assert bundle["safety"]["xcode_or_signing"] is False
    assert str(tmp_path) not in report_text
    assert "sk-" not in report_text
    assert "meshy-secret" not in report_text


def test_final_handoff_index_configured_preflight_source_exposes_device_action_bundle(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_three_d_evaluation(repo_root)
    _write_npc_evaluation(repo_root)
    _write_visual_regression(repo_root)
    _write_final_acceptance(repo_root)
    _write_ios_deploy_runbook(repo_root)
    _write_final_demo_launch(
        repo_root,
        overall_status="partial",
        device_action_bundle={
            "id": "final_demo_launch_device_actions",
            "status": "blocked",
            "actions": [
                {
                    "id": "run_mobile_deploy_preflight",
                    "label": "Run mobile deploy preflight",
                    "status": "blocked",
                    "classification": "manual_preflight_required",
                    "command": (
                        "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto "
                        "make mobile-write-deploy-config-auto"
                    ),
                    "detail": "Missing DEVELOPMENT_TEAM.",
                    "manual": True,
                    "provider_calls": False,
                    "global_action": False,
                    "xcode_or_signing": False,
                    "validation_command": "make mobile-deploy-preflight",
                },
            ],
            "first_action": {
                "id": "run_mobile_deploy_preflight",
                "label": "Run mobile deploy preflight",
                "status": "blocked",
                "classification": "manual_preflight_required",
                "command": (
                    "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto "
                    "make mobile-write-deploy-config-auto"
                ),
                "detail": "Missing DEVELOPMENT_TEAM.",
                "manual": True,
                "provider_calls": False,
                "global_action": False,
                "xcode_or_signing": False,
                "validation_command": "make mobile-deploy-preflight",
            },
        },
    )

    result = build_final_handoff_index_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    sources = {source["id"]: source for source in result.report["source_reports"]}
    report_text = json.dumps(result.report)

    bundle = sources["final_configured_preflight"]["device_action_bundle"]

    assert bundle["id"] == "final_configured_preflight_device_actions"
    assert bundle["source_report"] == "configured_ios_deploy_runbook"
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
    assert result.report["device_action_bundle"]["source_report"] == (
        "final_demo_launch_local"
    )
    assert bundle["safety"]["commands_run"] is False
    assert bundle["safety"]["provider_calls"] is False
    assert bundle["safety"]["xcode_or_signing"] is False
    assert str(tmp_path) not in report_text
    assert "sk-" not in report_text


def test_final_handoff_index_reports_missing_source_freshness(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)

    result = build_final_handoff_index_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    source_reports = {source["id"]: source for source in result.report["source_reports"]}

    assert source_reports["three_d_evaluation"]["freshness"] == {
        "status": "unknown",
        "classification": "source_missing",
        "checked_against": "git_head",
        "source_modified_at": None,
        "current_revision": None,
        "current_revision_committed_at": None,
    }
    assert result.report["freshness_summary"]["unknown"] >= 1


def test_final_handoff_index_marks_local_sources_fresh_against_git_head(
    tmp_path: Path,
) -> None:
    repo_root = _init_git_repo(
        tmp_path,
        committed_at="2026-06-07T12:00:00+00:00",
    )
    _write_deploy_config_at(
        repo_root,
        local_config=(
            "DEVELOPMENT_TEAM = TEAM12345\n"
            "PRODUCT_BUNDLE_IDENTIFIER = com.zhexu.personalmythforge.dev\n"
            "PMF_BACKEND_BASE_URL = http://10.0.0.24:8080\n"
            "PMF_FINAL_LAUNCH_MODE = configured\n"
        ),
    )
    _write_final_resources(repo_root)
    _write_local_rehearsal_reports(repo_root)
    for path in (repo_root / "services/backend/.local").glob("*.json"):
        _set_mtime(path, "2026-06-07T12:05:00+00:00")

    result = build_final_handoff_index_report(
        settings=Settings(
            three_d_provider="meshy",
            meshy_api_key="sk-meshy-secret",
            npc_provider="openai",
            openai_api_key="sk-openai-secret",
            print_provider="local",
        ),
        repo_root=repo_root,
    )
    source_reports = {source["id"]: source for source in result.report["source_reports"]}

    assert source_reports["three_d_evaluation"]["status"] == "ready"
    assert source_reports["three_d_evaluation"]["freshness"]["status"] == "fresh"
    assert source_reports["three_d_evaluation"]["freshness"][
        "classification"
    ] == "fresh_report"
    assert source_reports["visual_regression"]["freshness"]["status"] == "fresh"
    assert result.report["freshness_summary"]["fresh"] >= 6
    assert result.report["freshness_summary"]["stale"] == 0


def test_final_handoff_index_blocks_stale_required_local_source(
    tmp_path: Path,
) -> None:
    repo_root = _init_git_repo(
        tmp_path,
        committed_at="2026-06-07T12:10:00+00:00",
    )
    _write_deploy_config_at(repo_root)
    _write_final_resources(repo_root)
    _write_local_rehearsal_reports(repo_root)
    stale_path = repo_root / "services/backend/.local/3d-evaluation-local.json"
    _set_mtime(stale_path, "2026-06-07T12:00:00+00:00")

    result = build_final_handoff_index_report(
        settings=Settings(
            three_d_provider="meshy",
            meshy_api_key="sk-meshy-secret",
            npc_provider="openai",
            openai_api_key="sk-openai-secret",
            print_provider="local",
        ),
        repo_root=repo_root,
    )
    source_reports = {source["id"]: source for source in result.report["source_reports"]}
    lanes = result.report["lanes_by_id"]

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert lanes["local_rehearsal"]["status"] == "blocked"
    assert source_reports["three_d_evaluation"]["status"] == "blocked"
    assert source_reports["three_d_evaluation"]["classification"] == "stale_report"
    assert source_reports["three_d_evaluation"]["freshness"]["status"] == "stale"
    assert result.report["freshness_summary"]["stale"] >= 1


def test_final_handoff_index_cli_writes_report_and_makefile_exposes_target(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    output_path = tmp_path / "final-handoff-index.json"

    from myth_forge_api.cli import main

    exit_code = main(
        [
            "final-handoff-index",
            "--repo-root",
            str(repo_root),
            "--output",
            str(output_path),
        ]
    )

    assert exit_code == 2
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["kind"] == "final_handoff_index_report"
    assert payload["status"] == "blocked"

    repo_root = Path(__file__).resolve().parents[3]
    makefile = (repo_root / "Makefile").read_text(encoding="utf-8")
    wrapper = (
        repo_root / "services/backend/scripts/write_final_handoff_index.sh"
    ).read_text(encoding="utf-8")
    assert "final-handoff-index:" in makefile
    assert "services/backend/scripts/write_final_handoff_index.sh" in makefile
    assert "myth_forge_api.cli final-handoff-index" in wrapper
    assert ".local/final-handoff-index.json" in wrapper


def _write_deploy_config(tmp_path: Path, local_config: str | None = None) -> Path:
    repo_root = tmp_path / "repo"
    return _write_deploy_config_at(repo_root, local_config=local_config)


def _write_deploy_config_at(repo_root: Path, local_config: str | None = None) -> Path:
    config_dir = repo_root / "apps/mobile/ios/Config"
    config_dir.mkdir(parents=True, exist_ok=True)
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


def _write_final_demo_launch(
    repo_root: Path,
    *,
    overall_status: str = "partial",
    first_blocker: dict[str, object] | None = None,
    next_action: dict[str, object] | None = None,
    operator_actions: list[str] | None = None,
    device_action_bundle: dict[str, object] | None = None,
) -> None:
    report: dict[str, object] = {
        "kind": "final_demo_launch_report",
        "mode": "local",
        "overall_status": overall_status,
        "summary": {"ready": 8, "missing": 0, "blocked": 0, "manual": 1, "optional": 1},
    }
    if first_blocker is not None:
        report["first_blocker"] = first_blocker
    if next_action is not None:
        report["next_action"] = next_action
    if operator_actions is not None:
        report["operator_actions"] = operator_actions
    if device_action_bundle is not None:
        report["device_action_bundle"] = device_action_bundle
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
                "html_path": "docs/superpowers/verification/p0.118-scene-load-proof.html",
                "png_path": (
                    "docs/superpowers/verification/assets/"
                    "p0.118-scene-load-proof-390x844.png"
                ),
            }
        ],
    }
    _write_json(repo_root / "services/backend/.local/visual-regression-local.json", report)


def _write_json(path: Path, report: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report), encoding="utf-8")


def _init_git_repo(tmp_path: Path, *, committed_at: str) -> Path:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    env = os.environ | {
        "GIT_AUTHOR_DATE": committed_at,
        "GIT_COMMITTER_DATE": committed_at,
    }
    subprocess.run(["git", "init"], cwd=repo_root, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_root,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_root,
        check=True,
    )
    (repo_root / "README.md").write_text("test\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=repo_root, check=True)
    subprocess.run(
        ["git", "commit", "-m", "initial"],
        cwd=repo_root,
        check=True,
        env=env,
        capture_output=True,
    )
    return repo_root


def _set_mtime(path: Path, iso_timestamp: str) -> None:
    epoch = datetime.fromisoformat(iso_timestamp).timestamp()
    os.utime(path, (epoch, epoch))
