import json
from pathlib import Path

import myth_forge_api.final_showcase_readiness as final_showcase_readiness
from myth_forge_api.config import Settings
from myth_forge_api.final_showcase_readiness import (
    build_final_showcase_readiness_report,
)
from myth_forge_api.live_provider_evidence import LiveProviderEvidenceResult
from myth_forge_api.local_showcase_smoke import LocalShowcaseSmokeResult
from myth_forge_api.visual_regression import DEFAULT_VISUAL_ARTIFACTS


def test_final_showcase_readiness_blocks_missing_objective_evidence(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )

    assert result.exit_code == 2
    assert result.report["kind"] == "final_showcase_readiness_report"
    assert result.report["status"] == "blocked"
    assert [row["id"] for row in result.report["capabilities"]] == [
        "ios_deployable",
        "capture_scanning",
        "local_showcase_smoke",
        "game_asset_3d_generation",
        "ai_agent_npc",
        "print_fulfillment",
        "provider_key_handoff",
        "functional_regression",
        "visual_regression",
        "privacy_safety",
    ]
    assert result.report["capabilities_by_id"]["capture_scanning"]["status"] == (
        "blocked"
    )
    local_smoke = result.report["capabilities_by_id"]["local_showcase_smoke"]
    assert local_smoke["status"] == "ready"
    assert local_smoke["command"] == "make local-showcase-smoke"
    assert "local_showcase_smoke_report:succeeded" in local_smoke["evidence"]
    assert "http_steps:6" in local_smoke["evidence"]
    assert "npc_ticks:2" in local_smoke["evidence"]
    assert "downloads:3" in local_smoke["evidence"]
    assert result.report["evidence"]["local_showcase_smoke"]["kind"] == (
        "local_showcase_smoke_report"
    )
    assert result.report["evidence"]["local_showcase_smoke"]["status"] == "succeeded"
    assert result.report["capabilities_by_id"]["game_asset_3d_generation"][
        "status"
    ] == "blocked"
    assert result.report["capabilities_by_id"]["ai_agent_npc"]["status"] == "blocked"
    assert result.report["capabilities_by_id"]["print_fulfillment"][
        "status"
    ] == "blocked"
    provider_handoff = result.report["capabilities_by_id"]["provider_key_handoff"]
    assert result.report["evidence"]["final_resource_apply_preview"]["kind"] == (
        "final_resource_apply_preview_report"
    )
    assert result.report["evidence"]["final_resource_apply_preview"]["status"] == "missing"
    assert provider_handoff["command"] == "make final-resource-init"
    assert provider_handoff["validation_command"] == "make final-resources-preflight"
    assert "final_resource_apply_preview:missing" in provider_handoff["evidence"]
    assert any(
        action == "run make final-resource-init"
        for action in result.report["operator_actions"]
    )
    assert result.report["first_blocker"]["id"] == "ios_deployable"
    assert result.report["next_action"] == {
        "id": "ios_deployable",
        "label": "iOS deployable",
        "status": "blocked",
        "classification": "ios_rehearsal_missing",
        "command": "make ios-device-launch-rehearsal",
        "detail": "iOS deploy runbook and device launch rehearsal must both be ready.",
        "source": "first_blocker",
    }
    assert "make final-showcase-readiness" not in result.report["operator_actions"]
    assert "make final-rehearsal-local" not in result.report["operator_actions"]
    assert "make final-rehearsal-local" in result.report["commands"]
    assert "make final-showcase-readiness" in result.report["commands"]
    assert result.report["safety"]["commands_run"] is False
    assert result.report["safety"]["live_provider_calls"] is False


def test_final_showcase_readiness_operator_actions_gate_apply_behind_preview(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    actions = result.report["operator_actions"]

    assert "make final-resource-apply-preview" in actions
    assert "make final-apply-resources" not in actions


def test_final_showcase_readiness_includes_ios_device_action_bundle(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )

    bundle = result.report["device_action_bundle"]
    assert bundle["id"] == "ios_device_manual_actions"
    assert bundle["label"] == "iOS Device Manual Actions"
    assert bundle["status"] == "blocked"
    assert bundle["summary"]["actions"] >= 4
    assert bundle["summary"]["manual"] == bundle["summary"]["actions"]
    assert bundle["summary"]["blocked"] >= 1
    assert bundle["summary"]["xcode_or_signing"] == 1
    assert bundle["summary"]["global_actions"] == 0
    assert bundle["summary"]["provider_calls"] == 0
    assert bundle["first_action"]["id"] == "start_backend_device_demo"
    assert bundle["first_action"]["command"] == "make backend-device-demo"
    assert [action["id"] for action in bundle["actions"][:4]] == [
        "start_backend_device_demo",
        "run_mobile_deploy_preflight",
        "resolve_xcode_build_gate",
        "run_ios_device_launch_rehearsal",
    ]
    assert bundle["actions"][0]["blocks"] == [
        "ios_deployable",
        "functional_regression",
    ]
    assert bundle["actions"][2]["xcode_or_signing"] is True
    assert bundle["safety"]["commands_run"] is False
    assert bundle["safety"]["global_mutation"] is False
    assert bundle["safety"]["provider_calls"] is False


def test_final_showcase_readiness_maps_missing_mobile_deploy_preflight_evidence(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )

    evidence = result.report["evidence"]["mobile_deploy_preflight_evidence"]
    bundle = result.report["device_action_bundle"]
    actions = {action["id"]: action for action in bundle["actions"]}
    preflight = actions["run_mobile_deploy_preflight"]

    assert evidence["kind"] == "mobile_deploy_preflight_evidence_report"
    assert evidence["status"] == "missing"
    assert preflight["status"] == "blocked"
    assert preflight["evidence_status"] == "missing"
    assert preflight["evidence_source"] == (
        "services/backend/.local/mobile-deploy-preflight-evidence.json"
    )
    assert preflight["validation_command"] == "make mobile-deploy-preflight-evidence"


def test_final_showcase_readiness_marks_preflight_actions_ready_with_evidence(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_mobile_deploy_preflight_evidence_ready(repo_root)

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )

    bundle = result.report["device_action_bundle"]
    actions = {action["id"]: action for action in bundle["actions"]}

    assert result.exit_code == 2
    assert result.report["evidence"]["mobile_deploy_preflight_evidence"][
        "status"
    ] == "ready"
    assert actions["start_backend_device_demo"]["status"] == "ready"
    assert actions["start_backend_device_demo"]["evidence_status"] == "ready"
    assert actions["run_mobile_deploy_preflight"]["status"] == "ready"
    assert actions["run_mobile_deploy_preflight"]["evidence_status"] == "ready"
    assert actions["run_mobile_deploy_preflight"]["evidence_detail"] == (
        "iOS deploy preflight passed."
    )
    assert actions["resolve_xcode_build_gate"]["status"] == "blocked"
    assert bundle["first_action"]["id"] == "resolve_xcode_build_gate"
    assert bundle["summary"]["ready"] == 2
    assert bundle["summary"]["blocked"] == 2


def test_final_showcase_readiness_backend_action_prefers_backend_evidence_detail(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_mobile_deploy_preflight_evidence_blocked(
        repo_root,
        checks=[
            {
                "id": "development_team",
                "label": "Apple Team ID",
                "status": "blocked",
                "detail": "Missing DEVELOPMENT_TEAM",
            },
            {
                "id": "backend_base_url",
                "label": "Backend base URL",
                "status": "blocked",
                "detail": "PMF_BACKEND_BASE_URL must be iPhone-reachable",
            },
        ],
    )

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )

    actions = {
        action["id"]: action
        for action in result.report["device_action_bundle"]["actions"]
    }

    assert actions["start_backend_device_demo"]["evidence_detail"] == (
        "PMF_BACKEND_BASE_URL must be iPhone-reachable"
    )


def test_final_showcase_readiness_preflight_action_summarizes_blocker_details(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_mobile_deploy_preflight_evidence_blocked(
        repo_root,
        checks=[
            {
                "id": "development_team",
                "label": "Apple Team ID",
                "status": "blocked",
                "detail": "Missing DEVELOPMENT_TEAM",
            },
            {
                "id": "backend_base_url",
                "label": "Backend base URL",
                "status": "blocked",
                "detail": "PMF_BACKEND_BASE_URL must be iPhone-reachable",
            },
        ],
    )

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )

    actions = {
        action["id"]: action
        for action in result.report["device_action_bundle"]["actions"]
    }

    assert actions["run_mobile_deploy_preflight"]["evidence_detail"] == (
        "Missing DEVELOPMENT_TEAM; PMF_BACKEND_BASE_URL must be iPhone-reachable"
    )


def test_final_showcase_readiness_top_level_ios_blocker_includes_device_action_detail(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_mobile_deploy_preflight_evidence_blocked(
        repo_root,
        checks=[
            {
                "id": "development_team",
                "label": "Apple Team ID",
                "status": "blocked",
                "detail": "Missing DEVELOPMENT_TEAM",
            },
            {
                "id": "backend_base_url",
                "label": "Backend base URL",
                "status": "blocked",
                "detail": "PMF_BACKEND_BASE_URL must be iPhone-reachable",
            },
        ],
    )

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )

    blocker = result.report["first_blocker"]
    action = result.report["next_action"]

    assert blocker["id"] == "ios_deployable"
    assert action["id"] == "ios_deployable"
    assert "iOS deploy runbook and device launch rehearsal" in blocker["detail"]
    assert "Next device action: make " in blocker["detail"]
    assert "PMF_BACKEND_BASE_URL must be iPhone-reachable" in blocker["detail"]
    assert action["detail"] == blocker["detail"]
    assert "MESHY_API_KEY" not in blocker["detail"]


def test_final_showcase_readiness_top_level_ios_blocker_prefers_preflight_detail(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_mobile_deploy_preflight_evidence_blocked(
        repo_root,
        checks=[
            {
                "id": "development_team",
                "label": "Apple Team ID",
                "status": "blocked",
                "detail": "Missing DEVELOPMENT_TEAM",
            },
            {
                "id": "backend_base_url",
                "label": "Backend base URL",
                "status": "blocked",
                "detail": "PMF_BACKEND_BASE_URL must be iPhone-reachable",
            },
        ],
    )

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )

    blocker = result.report["first_blocker"]
    action = result.report["next_action"]

    assert blocker["id"] == "ios_deployable"
    assert action["id"] == "ios_deployable"
    assert "Next device action: make mobile-deploy-preflight" in blocker["detail"]
    assert "Missing DEVELOPMENT_TEAM" in blocker["detail"]
    assert "PMF_BACKEND_BASE_URL must be iPhone-reachable" in blocker["detail"]
    assert "Next device action: make backend-device-demo" not in blocker["detail"]
    assert action["detail"] == blocker["detail"]
    assert "MESHY_API_KEY" not in blocker["detail"]


def test_final_showcase_readiness_next_action_command_uses_preferred_device_action(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_mobile_deploy_preflight_evidence_blocked(
        repo_root,
        checks=[
            {
                "id": "development_team",
                "label": "Apple Team ID",
                "status": "blocked",
                "detail": "Missing DEVELOPMENT_TEAM",
            },
            {
                "id": "backend_base_url",
                "label": "Backend base URL",
                "status": "blocked",
                "detail": "PMF_BACKEND_BASE_URL must be iPhone-reachable",
            },
        ],
    )

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )

    blocker = result.report["first_blocker"]
    action = result.report["next_action"]

    assert blocker["id"] == "ios_deployable"
    assert blocker["command"] == "make mobile-deploy-preflight"
    assert action["id"] == "ios_deployable"
    assert action["command"] == "make mobile-deploy-preflight"
    assert "Next device action: make mobile-deploy-preflight" in action["detail"]
    assert "Missing DEVELOPMENT_TEAM" in action["detail"]
    assert "PMF_BACKEND_BASE_URL must be iPhone-reachable" in action["detail"]
    assert "MESHY_API_KEY" not in action["detail"]


def test_final_showcase_readiness_next_action_uses_preflight_child_action(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_mobile_deploy_preflight_evidence_blocked(
        repo_root,
        checks=[
            {
                "id": "development_team",
                "label": "Apple Team ID",
                "status": "blocked",
                "detail": "Missing DEVELOPMENT_TEAM",
            },
            {
                "id": "backend_base_url",
                "label": "Backend base URL",
                "status": "blocked",
                "detail": "PMF_BACKEND_BASE_URL must be iPhone-reachable",
            },
        ],
        next_action={
            "id": "development_team",
            "label": "Apple Team ID",
            "status": "blocked",
            "command": "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig",
            "detail": (
                "Missing DEVELOPMENT_TEAM; "
                "PMF_BACKEND_BASE_URL must be iPhone-reachable"
            ),
            "validation_command": "make mobile-deploy-preflight",
            "source": "first_blocker",
        },
    )

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )

    action = result.report["next_action"]
    blocker = result.report["first_blocker"]
    row = result.report["capabilities_by_id"]["ios_deployable"]
    expected_command = (
        "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig; "
        "rerun make mobile-deploy-preflight"
    )

    assert row["command"] == expected_command
    assert row["validation_command"] == "make mobile-deploy-preflight"
    assert row["next_action"] == {
        "id": "ios_deployable",
        "label": "iOS deployable",
        "status": "blocked",
        "classification": "ios_rehearsal_missing",
        "command": expected_command,
        "detail": row["detail"],
        "source": "capability",
        "validation_command": "make mobile-deploy-preflight",
    }
    assert blocker["command"] == expected_command
    assert blocker["validation_command"] == "make mobile-deploy-preflight"
    assert f"Next device action: {expected_command}" in blocker["detail"]
    assert "Next device action: make mobile-deploy-preflight" not in blocker["detail"]
    assert action["id"] == "ios_deployable"
    assert action["command"] == expected_command
    assert action["validation_command"] == "make mobile-deploy-preflight"
    assert action["detail"] == blocker["detail"]
    assert "Missing DEVELOPMENT_TEAM" in action["detail"]
    assert "PMF_BACKEND_BASE_URL must be iPhone-reachable" in action["detail"]
    assert result.report["operator_actions"][0] == expected_command


def test_final_showcase_readiness_top_level_ios_blocker_promotes_validation_aware_command(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    child_action = {
        "id": "development_team",
        "label": "Apple Team ID",
        "status": "blocked",
        "command": "DEVELOPMENT_TEAM=YOUR_TEAM_ID make mobile-write-deploy-config-auto",
        "detail": (
            "Missing DEVELOPMENT_TEAM; "
            "PMF_BACKEND_BASE_URL must be iPhone-reachable"
        ),
        "validation_command": "make mobile-deploy-preflight",
        "source": "first_blocker",
    }
    _write_mobile_deploy_preflight_evidence_blocked(
        repo_root,
        checks=[
            {
                "id": "development_team",
                "label": "Apple Team ID",
                "status": "blocked",
                "detail": "Missing DEVELOPMENT_TEAM",
            },
            {
                "id": "backend_base_url",
                "label": "Backend base URL",
                "status": "blocked",
                "detail": "PMF_BACKEND_BASE_URL must be iPhone-reachable",
            },
        ],
        next_action=child_action,
    )

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )

    expected_command = (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID make mobile-write-deploy-config-auto; "
        "rerun make mobile-deploy-preflight"
    )

    blocker = result.report["first_blocker"]
    action = result.report["next_action"]
    row = result.report["capabilities_by_id"]["ios_deployable"]

    assert row["command"] == expected_command
    assert blocker["command"] == expected_command
    assert action["command"] == expected_command
    assert row["validation_command"] == "make mobile-deploy-preflight"
    assert blocker["validation_command"] == "make mobile-deploy-preflight"
    assert action["validation_command"] == "make mobile-deploy-preflight"
    assert result.report["operator_actions"][0] == expected_command


def test_final_showcase_readiness_device_bundle_first_action_uses_preflight_child_action(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    child_action = {
        "id": "development_team",
        "label": "Apple Team ID",
        "status": "blocked",
        "command": "DEVELOPMENT_TEAM=YOUR_TEAM_ID make mobile-write-deploy-config-auto",
        "detail": "Missing DEVELOPMENT_TEAM",
        "validation_command": "make mobile-deploy-preflight",
        "source": "first_blocker",
    }
    _write_mobile_deploy_preflight_evidence_blocked(
        repo_root,
        checks=[
            {
                "id": "development_team",
                "label": "Apple Team ID",
                "status": "blocked",
                "detail": "Missing DEVELOPMENT_TEAM",
            },
            {
                "id": "backend_base_url",
                "label": "Backend base URL",
                "status": "blocked",
                "detail": "PMF_BACKEND_BASE_URL must be iPhone-reachable",
            },
        ],
        next_action=child_action,
    )

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )

    bundle = result.report["device_action_bundle"]
    first_action = bundle["first_action"]
    actions = {action["id"]: action for action in bundle["actions"]}

    assert first_action["id"] == "run_mobile_deploy_preflight"
    assert first_action["command"] == child_action["command"]
    assert first_action["validation_command"] == "make mobile-deploy-preflight"
    assert first_action["next_action"] == child_action
    assert first_action["evidence_detail"] == (
        "Missing DEVELOPMENT_TEAM; PMF_BACKEND_BASE_URL must be iPhone-reachable"
    )
    assert actions["run_mobile_deploy_preflight"]["command"] == (
        "make mobile-deploy-preflight"
    )
    expected_command = (
        f"{child_action['command']}; rerun make mobile-deploy-preflight"
    )
    assert result.report["first_blocker"]["command"] == expected_command
    assert result.report["next_action"]["command"] == expected_command


def test_final_showcase_readiness_device_bundle_first_action_exposes_saved_next_action(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    child_action = {
        "id": "development_team",
        "label": "Apple Team ID",
        "status": "blocked",
        "command": "DEVELOPMENT_TEAM=YOUR_TEAM_ID make mobile-write-deploy-config-auto",
        "detail": "Missing DEVELOPMENT_TEAM",
        "validation_command": "make mobile-deploy-preflight",
        "source": "first_blocker",
    }
    _write_mobile_deploy_preflight_evidence_blocked(
        repo_root,
        checks=[
            {
                "id": "development_team",
                "label": "Apple Team ID",
                "status": "blocked",
                "detail": "Missing DEVELOPMENT_TEAM",
            },
            {
                "id": "backend_base_url",
                "label": "Backend base URL",
                "status": "blocked",
                "detail": "PMF_BACKEND_BASE_URL must be iPhone-reachable",
            },
        ],
        next_action=child_action,
    )

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )

    bundle = result.report["device_action_bundle"]
    first_action = bundle["first_action"]
    actions = {action["id"]: action for action in bundle["actions"]}
    preflight_row = actions["run_mobile_deploy_preflight"]
    saved_next_action = first_action["saved_next_action"]

    assert first_action["id"] == "run_mobile_deploy_preflight"
    assert first_action["command"] == child_action["command"]
    assert preflight_row["saved_next_action"] == saved_next_action
    assert saved_next_action == {
        "id": "run_mobile_deploy_preflight",
        "label": "Run mobile deploy preflight",
        "status": "blocked",
        "command": (
            "DEVELOPMENT_TEAM=YOUR_TEAM_ID make mobile-write-deploy-config-auto; "
            "rerun make mobile-deploy-preflight"
        ),
        "detail": "Missing DEVELOPMENT_TEAM; PMF_BACKEND_BASE_URL must be iPhone-reachable",
        "source": "operator_actions",
        "validation_command": "make mobile-deploy-preflight",
    }


def test_final_showcase_readiness_maps_missing_mobile_xcode_build_evidence(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )

    evidence = result.report["evidence"]["mobile_xcode_build_evidence"]
    actions = {
        action["id"]: action
        for action in result.report["device_action_bundle"]["actions"]
    }
    xcode = actions["resolve_xcode_build_gate"]

    assert evidence["kind"] == "mobile_xcode_build_evidence_report"
    assert evidence["status"] == "missing"
    assert xcode["status"] == "blocked"
    assert xcode["evidence_status"] == "missing"
    assert xcode["evidence_source"] == (
        "services/backend/.local/mobile-xcode-build-evidence.json"
    )
    assert xcode["validation_command"] == "make mobile-xcode-build-evidence"


def test_final_showcase_readiness_maps_blocked_mobile_xcode_build_evidence(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_mobile_xcode_build_evidence_blocked(repo_root)

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )

    actions = {
        action["id"]: action
        for action in result.report["device_action_bundle"]["actions"]
    }
    xcode = actions["resolve_xcode_build_gate"]

    assert result.report["evidence"]["mobile_xcode_build_evidence"][
        "status"
    ] == "blocked"
    assert xcode["status"] == "blocked"
    assert xcode["evidence_status"] == "blocked"
    assert xcode["evidence_detail"] == "Apple SDK license agreement is not accepted."
    assert xcode["validation_command"] == "make mobile-xcode-build-evidence"
    assert xcode["operator_actions"] == [
        "accept the Xcode license outside Codex, then rerun make mobile-xcode-build-evidence"
    ]


def test_final_showcase_readiness_marks_xcode_action_ready_with_evidence(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_mobile_deploy_preflight_evidence_ready(repo_root)
    _write_mobile_xcode_build_evidence_ready(repo_root)

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )

    bundle = result.report["device_action_bundle"]
    actions = {action["id"]: action for action in bundle["actions"]}

    assert actions["start_backend_device_demo"]["status"] == "ready"
    assert actions["run_mobile_deploy_preflight"]["status"] == "ready"
    assert actions["resolve_xcode_build_gate"]["status"] == "ready"
    assert actions["resolve_xcode_build_gate"]["evidence_status"] == "ready"
    assert actions["resolve_xcode_build_gate"]["evidence_detail"] == (
        "Xcode build gate passed with code signing disabled."
    )
    assert actions["run_ios_device_launch_rehearsal"]["status"] == "blocked"
    assert bundle["first_action"]["id"] == "run_ios_device_launch_rehearsal"
    assert bundle["summary"]["ready"] == 3
    assert bundle["summary"]["blocked"] == 1


def test_final_showcase_readiness_blocks_failed_local_showcase_smoke(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo_root = _write_deploy_config(tmp_path)

    def fake_local_smoke() -> LocalShowcaseSmokeResult:
        return LocalShowcaseSmokeResult(
            exit_code=1,
            report={
                "kind": "local_showcase_smoke_report",
                "status": "failed",
                "summary": {
                    "passed": 0,
                    "failed": 1,
                    "http_steps": 1,
                    "npc_ticks": 0,
                    "downloads": 0,
                },
                "steps": [
                    {
                        "id": "upload_guided_scan_capture",
                        "status": "failed",
                        "detail": "HTTP 500",
                    }
                ],
                "safety": {
                    "provider_calls": False,
                    "live_provider_calls": False,
                    "global_mutation": False,
                    "starts_server": False,
                    "writes_repo_local_media": False,
                    "uses_temporary_storage": True,
                    "provider_secrets_in_report": False,
                    "raw_media_in_report": False,
                    "local_paths_in_report": False,
                    "payment_links_in_report": False,
                },
            },
        )

    monkeypatch.setattr(
        "myth_forge_api.final_showcase_readiness.build_local_showcase_smoke_report",
        fake_local_smoke,
    )

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    local_smoke = result.report["capabilities_by_id"]["local_showcase_smoke"]

    assert result.exit_code == 2
    assert local_smoke["status"] == "blocked"
    assert local_smoke["classification"] == "local_showcase_smoke_failed"
    assert local_smoke["command"] == "make local-showcase-smoke"
    assert "local_showcase_smoke_report:failed" in local_smoke["evidence"]


def test_final_showcase_readiness_marks_local_proof_partial_until_live_and_device(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(
        tmp_path,
        local_config=(
            "DEVELOPMENT_TEAM = TEAM12345\n"
            "PRODUCT_BUNDLE_IDENTIFIER = com.zhexu.personalmythforge.dev\n"
            "PMF_BACKEND_BASE_URL = http://10.0.0.24:8080\n"
        ),
    )
    _write_capture_source_acceptance(repo_root)
    _write_final_resources(repo_root)
    _write_three_d_evaluation(repo_root)
    _write_npc_evaluation(repo_root)
    _write_visual_regression(repo_root)
    _write_final_acceptance_ready(repo_root)

    result = build_final_showcase_readiness_report(
        settings=Settings(
            three_d_provider="meshy",
            meshy_api_key="sk-meshy-test",
            npc_provider="openai",
            openai_api_key="sk-openai-test",
        ),
        repo_root=repo_root,
    )
    rows = result.report["capabilities_by_id"]

    assert result.exit_code == 2
    assert result.report["status"] == "partial"
    assert rows["ios_deployable"]["status"] == "partial"
    assert rows["capture_scanning"]["status"] == "ready"
    assert rows["game_asset_3d_generation"]["status"] == "partial"
    assert rows["ai_agent_npc"]["status"] == "partial"
    assert rows["print_fulfillment"]["status"] == "partial"
    assert rows["print_fulfillment"]["classification"] == "missing_configured_treatstock_quote"
    assert rows["print_fulfillment"]["command"] == (
        "PMF_ALLOW_PRINT_PROVIDER_CALLS=1 make print-quote-configured"
    )
    assert rows["print_fulfillment"]["validation_command"] == (
        "make print-fulfillment-readiness"
    )
    assert rows["print_fulfillment"]["requires_cost_consent"] is True
    assert rows["provider_key_handoff"]["status"] == "partial"
    assert result.report["evidence"]["final_resource_apply_preview"]["status"] == "ready"
    assert "final_resource_apply_preview:ready" in rows["provider_key_handoff"]["evidence"]
    assert rows["provider_key_handoff"]["command"] == "make live-provider-evidence"
    assert rows["functional_regression"]["status"] == "ready"
    assert rows["visual_regression"]["status"] == "ready"
    assert result.report["first_blocker"]["id"] == "ios_deployable"
    assert any(
        "live provider evidence" in action
        for action in result.report["operator_actions"]
    )


def test_final_showcase_readiness_blocks_stale_visual_regression_inventory(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(
        tmp_path,
        local_config=(
            "DEVELOPMENT_TEAM = TEAM12345\n"
            "PRODUCT_BUNDLE_IDENTIFIER = com.zhexu.personalmythforge.dev\n"
            "PMF_BACKEND_BASE_URL = http://10.0.0.24:8080\n"
        ),
    )
    _write_capture_source_acceptance(repo_root)
    _write_final_resources(repo_root)
    _write_three_d_evaluation(repo_root)
    _write_npc_evaluation(repo_root)
    _write_visual_regression_stale_inventory(repo_root)
    _write_final_acceptance_ready(repo_root)

    result = build_final_showcase_readiness_report(
        settings=Settings(
            three_d_provider="meshy",
            meshy_api_key="sk-meshy-test",
            npc_provider="openai",
            openai_api_key="sk-openai-test",
        ),
        repo_root=repo_root,
    )

    row = result.report["capabilities_by_id"]["visual_regression"]
    evidence = result.report["evidence"]["visual_regression_readiness"]

    assert result.exit_code == 2
    assert row["status"] == "blocked"
    assert row["classification"] == "visual_regression_inventory_stale"
    assert row["command"] == "make visual-regression-local"
    assert "p0.12_ios_device_media_input" in row["detail"]
    assert evidence["status"] == "blocked"
    assert evidence["summary"] == {"passed": 1, "failed": 0}
    assert any(
        "make visual-regression-local" in action
        for action in result.report["operator_actions"]
    )


def test_final_showcase_readiness_live_provider_rows_promote_child_next_action(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo_root = _write_deploy_config(
        tmp_path,
        local_config=(
            "DEVELOPMENT_TEAM = TEAM12345\n"
            "PRODUCT_BUNDLE_IDENTIFIER = com.zhexu.personalmythforge.dev\n"
            "PMF_BACKEND_BASE_URL = http://10.0.0.24:8080\n"
        ),
    )
    _write_capture_source_acceptance(repo_root)
    _write_final_resources(repo_root)
    _write_three_d_evaluation(repo_root)
    _write_npc_evaluation(repo_root)
    _write_visual_regression(repo_root)
    _write_final_acceptance_ready(repo_root)

    def fake_live_provider_evidence_report(
        *, repo_root: Path | str | None = None
    ) -> LiveProviderEvidenceResult:
        return LiveProviderEvidenceResult(
            exit_code=2,
            report={
                "kind": "live_provider_evidence_report",
                "status": "blocked",
                "next_action": {
                    "id": "provider_handoff",
                    "label": "Provider handoff",
                    "status": "blocked",
                    "classification": "report_not_ready",
                    "command": "make final-resource-apply-preview",
                    "detail": "Core 3D provider is demo-ready but not configured.",
                    "requires_live_provider_consent": False,
                    "validation_command": "make live-provider-evidence",
                    "source": "first_blocker",
                    "source_blocker_id": "three_d_provider",
                    "source_blocker_command": "make final-resource-apply-preview",
                    "source_blocker_validation_command": "make provider-handoff",
                },
                "evidence": [],
                "operator_actions": ["make final-resource-apply-preview"],
                "commands": ["make live-provider-evidence", "make provider-handoff"],
                "safety": {"live_provider_calls": False},
            },
        )

    monkeypatch.setattr(
        final_showcase_readiness,
        "build_live_provider_evidence_report",
        fake_live_provider_evidence_report,
    )

    result = build_final_showcase_readiness_report(
        settings=Settings(
            three_d_provider="meshy",
            meshy_api_key="sk-meshy-test",
            npc_provider="openai",
            openai_api_key="sk-openai-test",
        ),
        repo_root=repo_root,
    )
    rows = result.report["capabilities_by_id"]
    provider_handoff_command = (
        "make final-resource-apply-preview; rerun make provider-handoff"
    )

    for row_id in ("game_asset_3d_generation", "ai_agent_npc"):
        row = rows[row_id]
        assert row["status"] == "partial"
        assert row["command"] == provider_handoff_command
        assert row["validation_command"] == "make live-provider-evidence"
        assert row["requires_live_provider_consent"] is False
        assert row["completion_requires_live_provider_consent"] is True
        assert row["next_action"] == {
            "id": row_id,
            "label": row["label"],
            "status": "partial",
            "classification": row["classification"],
            "command": provider_handoff_command,
            "detail": row["detail"],
            "source": "capability",
            "validation_command": "make live-provider-evidence",
            "requires_live_provider_consent": False,
            "completion_requires_live_provider_consent": True,
        }
    actions = result.report["operator_actions"]
    complete_chain = (
        "make final-resource-apply-preview; rerun make provider-handoff; "
        "rerun make live-provider-evidence"
    )
    weak_chain = "make final-resource-apply-preview; rerun make live-provider-evidence"
    assert complete_chain in actions
    assert weak_chain not in actions
    assert "make final-resource-apply-preview" not in actions
    assert "make live-provider-evidence" not in actions


def test_final_showcase_readiness_provider_handoff_uses_final_resource_next_action(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_incomplete_final_resources(repo_root)

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    provider_handoff = result.report["capabilities_by_id"]["provider_key_handoff"]

    assert provider_handoff["status"] == "blocked"
    assert provider_handoff["classification"] == "provider_handoff_incomplete"
    assert provider_handoff["command"] == "provide MESHY_API_KEY in final-resources.env"
    assert provider_handoff["validation_command"] == "make final-resources-preflight"
    assert "final_resources:blocked" in provider_handoff["evidence"]


def test_final_showcase_readiness_gates_provider_handoff_on_configured_bundle(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(
        tmp_path,
        local_config=(
            "DEVELOPMENT_TEAM = TEAM12345\n"
            "PRODUCT_BUNDLE_IDENTIFIER = com.zhexu.personalmythforge.dev\n"
            "PMF_BACKEND_BASE_URL = http://10.0.0.24:8080\n"
        ),
    )
    _write_capture_source_acceptance(repo_root)
    _write_final_resources(repo_root)
    _write_three_d_evaluation(repo_root)
    _write_npc_evaluation(repo_root)
    _write_visual_regression(repo_root)
    _write_final_acceptance_ready(repo_root)
    _write_live_provider_evidence_ready(repo_root)

    result = build_final_showcase_readiness_report(
        settings=Settings(
            three_d_provider="meshy",
            meshy_api_key="sk-meshy-test",
            npc_provider="openai",
            openai_api_key="sk-openai-test",
        ),
        repo_root=repo_root,
    )
    provider_handoff = result.report["capabilities_by_id"]["provider_key_handoff"]

    assert result.exit_code == 2
    assert provider_handoff["status"] == "partial"
    assert provider_handoff["classification"] == "configured_evidence_bundle_unproven"
    assert provider_handoff["command"] == "make configured-live-evidence-bundle"
    assert "configured_live_evidence_bundle:missing" in provider_handoff["evidence"]
    assert result.report["evidence"]["configured_live_evidence_bundle"]["status"] == "missing"
    assert any(
        "configured evidence bundle" in action
        for action in result.report["operator_actions"]
    )


def test_final_showcase_readiness_marks_provider_handoff_ready_with_configured_bundle(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(
        tmp_path,
        local_config=(
            "DEVELOPMENT_TEAM = TEAM12345\n"
            "PRODUCT_BUNDLE_IDENTIFIER = com.zhexu.personalmythforge.dev\n"
            "PMF_BACKEND_BASE_URL = http://10.0.0.24:8080\n"
        ),
    )
    _write_capture_source_acceptance(repo_root)
    _write_final_resources(repo_root)
    _write_three_d_evaluation(repo_root)
    _write_npc_evaluation(repo_root)
    _write_visual_regression(repo_root)
    _write_final_acceptance_ready(repo_root)
    _write_live_provider_evidence_ready(repo_root)
    _write_configured_live_evidence_bundle(repo_root, status="ready")

    result = build_final_showcase_readiness_report(
        settings=Settings(
            three_d_provider="meshy",
            meshy_api_key="sk-meshy-test",
            npc_provider="openai",
            openai_api_key="sk-openai-test",
        ),
        repo_root=repo_root,
    )
    provider_handoff = result.report["capabilities_by_id"]["provider_key_handoff"]

    assert provider_handoff["status"] == "ready"
    assert provider_handoff["classification"] == "provider_handoff_ready"
    assert "next_action" not in provider_handoff
    assert "configured_live_evidence_bundle:ready" in provider_handoff["evidence"]
    assert result.report["evidence"]["configured_live_evidence_bundle"]["status"] == "ready"
    assert "make configured-live-evidence-bundle" in result.report["commands"]


def test_final_showcase_readiness_promotes_nested_operator_actions(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_capture_source_acceptance(repo_root)
    _write_three_d_evaluation(repo_root)
    _write_npc_evaluation(repo_root)
    _write_visual_regression_blocked(repo_root)
    _write_final_acceptance_blocked_with_actions(repo_root)
    _write_ios_device_launch_rehearsal_with_actions(
        repo_root,
        extra_actions=[
            (
                "final_handoff_index: run cd services/backend && uv run python -m "
                "myth_forge_api.cli final-demo-launch --mode configured "
                "--repo-root [repo-root] "
                "--output .local/final-demo-launch-configured.json"
            )
        ],
    )

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    actions = result.report["operator_actions"]

    assert result.exit_code == 2
    assert actions[0] == "make ios-device-launch-rehearsal"
    assert "final_rehearsal_local: final_acceptance_local: action 1" in actions
    assert "make final-configured-preflight" not in actions
    assert any("configured-live-evidence-bundle" in action for action in actions)
    assert "make final-demo-launch-configured" in actions
    assert not any("final-demo-launch --mode configured" in action for action in actions)
    assert "make final-handoff-index" in actions
    assert not any(
        action.startswith(
            (
                "final_handoff_index: make ",
                "final_handoff_index: run make ",
                "ios_device_launch_certificate: make final-handoff-index",
                "ios_device_launch_certificate: run make final-handoff-index",
            )
        )
        for action in actions
    )
    assert "make provider-handoff; rerun make live-provider-evidence" in actions
    assert "make live-provider-evidence" not in actions
    assert "make provider-handoff" not in actions
    assert (
        "run make live-provider-evidence after configured provider evidence files are refreshed"
        not in actions
    )
    assert "make visual-regression-local; rerun make print-fulfillment-readiness" not in actions
    assert any(
        "PMF_ALLOW_PRINT_PROVIDER_CALLS=1 make print-quote-configured" in action
        for action in actions
    )
    provider_action = "make provider-handoff; rerun make live-provider-evidence"
    print_action = next(
        action
        for action in actions
        if "PMF_ALLOW_PRINT_PROVIDER_CALLS=1 make print-quote-configured" in action
    )
    assert actions.index(provider_action) < actions.index(
        "provide MESHY_API_KEY in final-resources.env; rerun make final-resources-preflight"
    )
    assert actions.index(print_action) < actions.index(
        "provide OPENAI_API_KEY in final-resources.env; rerun make final-resources-preflight"
    )
    assert "run make final-resource-init" in actions
    assert (
        "provide iOS deploy config in Deployment.local.xcconfig; "
        "rerun make mobile-deploy-preflight"
        in actions
    )
    assert not any(
        action.startswith("ios_device_launch_certificate: provide iOS deploy config")
        for action in actions
    )
    assert "rerun make visual-regression-local and review failed artifacts" in actions
    assert "make final-showcase-readiness" not in actions
    assert len(actions) <= 32
    assert actions.count("make provider-handoff; rerun make live-provider-evidence") == 1
    assert (
        actions.count("make visual-regression-local; rerun make print-fulfillment-readiness")
        == 0
    )


def test_final_showcase_readiness_dedupes_prefixed_duplicate_actions(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_capture_source_acceptance(repo_root)
    _write_three_d_evaluation(repo_root)
    _write_npc_evaluation(repo_root)
    _write_visual_regression_blocked(repo_root)
    _write_final_acceptance_blocked_with_actions(repo_root)
    _write_ios_device_launch_rehearsal_with_actions(
        repo_root,
        extra_actions=[
            (
                "final_rehearsal_local: mobile_deploy_preflight_evidence: "
                "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig; "
                "rerun make mobile-deploy-preflight | Missing DEVELOPMENT_TEAM; "
                "PMF_BACKEND_BASE_URL must be iPhone-reachable"
            )
        ],
    )

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    actions = result.report["operator_actions"]

    bare_action = (
        "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig; "
        "rerun make mobile-deploy-preflight"
    )

    assert result.exit_code == 2
    assert bare_action in actions
    assert not any(
        action.startswith(
            "final_rehearsal_local: mobile_deploy_preflight_evidence: "
            "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig"
        )
        for action in actions
    )


def test_final_showcase_readiness_dedupes_prefixed_resource_actions(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_capture_source_acceptance(repo_root)
    _write_three_d_evaluation(repo_root)
    _write_npc_evaluation(repo_root)
    _write_visual_regression_blocked(repo_root)
    _write_final_acceptance_blocked_with_actions(repo_root)
    _write_ios_device_launch_rehearsal_with_actions(
        repo_root,
        extra_actions=[
            (
                "final_rehearsal_local: ios_deploy_runbook_local: "
                "provide MESHY_API_KEY in final-resources.env; "
                "rerun make final-resources-preflight"
            ),
            (
                "final_rehearsal_local: ios_deploy_runbook_local: "
                "provide OPENAI_API_KEY in final-resources.env; "
                "rerun make final-resources-preflight"
            ),
        ],
    )

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    actions = result.report["operator_actions"]

    meshy_action = (
        "provide MESHY_API_KEY in final-resources.env; "
        "rerun make final-resources-preflight"
    )
    openai_action = (
        "provide OPENAI_API_KEY in final-resources.env; "
        "rerun make final-resources-preflight"
    )

    assert result.exit_code == 2
    assert actions.count(meshy_action) == 1
    assert actions.count(openai_action) == 1
    assert not any(
        action.startswith(
            "final_rehearsal_local: ios_deploy_runbook_local: "
            "provide MESHY_API_KEY"
        )
        for action in actions
    )
    assert not any(
        action.startswith(
            "final_rehearsal_local: ios_deploy_runbook_local: "
            "provide OPENAI_API_KEY"
        )
        for action in actions
    )


def test_final_showcase_readiness_dedupes_prefixed_device_actions(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_capture_source_acceptance(repo_root)
    _write_three_d_evaluation(repo_root)
    _write_npc_evaluation(repo_root)
    _write_visual_regression_blocked(repo_root)
    _write_final_acceptance_blocked_with_actions(repo_root)
    _write_mobile_deploy_preflight_evidence_blocked(
        repo_root,
        checks=[
            {
                "id": "backend_base_url",
                "label": "Backend base URL",
                "status": "blocked",
                "detail": "PMF_BACKEND_BASE_URL must be iPhone-reachable",
            },
        ],
        next_action={
            "id": "start_backend_device_demo",
            "command": "make backend-device-demo",
            "validation_command": "make mobile-deploy-preflight",
            "source": "first_blocker",
        },
    )
    _write_ios_device_launch_rehearsal_with_actions(
        repo_root,
        extra_actions=[
            "start backend-device-demo",
            "final_handoff_index: start backend-device-demo",
            "ios_device_launch_certificate: start backend-device-demo",
            "ios_device_launch_certificate: provide iOS deploy config",
        ],
    )

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    actions = result.report["operator_actions"]

    backend_action = (
        "start backend-device-demo before device checks: make backend-device-demo; "
        "rerun make mobile-deploy-preflight"
    )
    deploy_config_action = (
        "provide iOS deploy config in Deployment.local.xcconfig; "
        "rerun make mobile-deploy-preflight"
    )

    assert result.exit_code == 2
    assert actions.count(backend_action) == 1
    assert not any(
        action.startswith("final_handoff_index: start backend-device-demo")
        for action in actions
    )
    assert not any(
        action.startswith("ios_device_launch_certificate: start backend-device-demo")
        for action in actions
    )
    assert deploy_config_action in actions
    assert not any(
        action.startswith("ios_device_launch_certificate: provide iOS deploy config")
        for action in actions
    )


def test_final_showcase_readiness_dedupes_prefixed_xcode_actions(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_capture_source_acceptance(repo_root)
    _write_three_d_evaluation(repo_root)
    _write_npc_evaluation(repo_root)
    _write_visual_regression_blocked(repo_root)
    _write_final_acceptance_blocked_with_actions(repo_root)
    _write_mobile_xcode_build_evidence_blocked(repo_root)
    _write_ios_device_launch_rehearsal_with_actions(
        repo_root,
        extra_actions=[
            (
                "final_rehearsal_local: final_acceptance_local: "
                "resolve Xcode build gate outside the app"
            )
        ],
    )

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    actions = result.report["operator_actions"]

    xcode_action = (
        "accept the Xcode license outside Codex, then rerun "
        "make mobile-xcode-build-evidence"
    )

    assert result.exit_code == 2
    assert actions.count(xcode_action) == 1
    assert not any(
        action.startswith("final_rehearsal_local: final_acceptance_local: accept")
        for action in actions
    )


def test_final_showcase_readiness_normalizes_resource_apply_unblock_actions() -> None:
    actions = final_showcase_readiness._report_operator_actions(
        {
            "operator_actions": [
                "unblock final_resource_apply_preview after final_resource_fill_guide",
                (
                    "unblock final_apply_resources after "
                    "final_resource_apply_preview"
                ),
            ]
        }
    )

    assert actions == [
        "make final-resource-apply-preview",
        "make final-apply-resources",
    ]


def test_final_showcase_readiness_normalizes_provider_evidence_actions() -> None:
    actions = final_showcase_readiness._report_operator_actions(
        {
            "operator_actions": [
                "rerun provider handoff readiness: make provider-handoff",
                (
                    "run make live-provider-evidence after configured provider "
                    "evidence files are refreshed"
                ),
            ]
        }
    )

    assert actions == ["make provider-handoff", "make live-provider-evidence"]


def test_final_showcase_readiness_normalizes_prefixed_make_target_actions() -> None:
    actions = final_showcase_readiness._report_operator_actions(
        {
            "operator_actions": [
                "final_handoff_index: run make final-configured-preflight",
                "final_handoff_index: make final-demo-launch-configured",
                "ios_device_launch_certificate: run make final-handoff-index",
                "ios_device_launch_certificate: make ios-deploy-runbook-local",
            ]
        }
    )

    assert actions == [
        (
            "make final-configured-preflight; "
            "rerun make configured-live-evidence-bundle"
        ),
        "make final-demo-launch-configured",
        "make final-handoff-index",
        "make ios-deploy-runbook-local",
    ]


def test_final_showcase_readiness_normalizes_prefixed_ios_config_action() -> None:
    actions = final_showcase_readiness._report_operator_actions(
        {
            "operator_actions": [
                "ios_device_launch_certificate: provide iOS deploy config",
            ]
        }
    )

    assert actions == [
        (
            "provide iOS deploy config in Deployment.local.xcconfig; "
            "rerun make mobile-deploy-preflight"
        )
    ]


def test_final_showcase_readiness_prefers_deploy_writer_over_old_team_action() -> None:
    actions = final_showcase_readiness._dedupe_operator_actions(
        [
            (
                "DEVELOPMENT_TEAM=YOUR_TEAM_ID "
                "make mobile-write-deploy-config-auto; "
                "rerun make mobile-deploy-preflight"
            ),
            (
                "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig; "
                "rerun make mobile-deploy-preflight"
            ),
        ]
    )

    assert actions == [
        (
            "DEVELOPMENT_TEAM=YOUR_TEAM_ID "
            "make mobile-write-deploy-config-auto; "
            "rerun make mobile-deploy-preflight"
        )
    ]


def test_final_showcase_readiness_prefers_writer_over_generic_ios_config_action() -> None:
    actions = final_showcase_readiness._dedupe_operator_actions(
        [
            (
                "DEVELOPMENT_TEAM=YOUR_TEAM_ID "
                "make mobile-write-deploy-config-auto; "
                "rerun make mobile-deploy-preflight"
            ),
            (
                "provide iOS deploy config in Deployment.local.xcconfig; "
                "rerun make mobile-deploy-preflight"
            ),
        ]
    )

    assert actions == [
        (
            "DEVELOPMENT_TEAM=YOUR_TEAM_ID "
            "make mobile-write-deploy-config-auto; "
            "rerun make mobile-deploy-preflight"
        )
    ]


def test_final_showcase_readiness_hides_apply_when_preview_gate_is_present() -> None:
    actions = final_showcase_readiness._dedupe_operator_actions(
        [
            "make final-resource-apply-preview",
            "make final-apply-resources",
            (
                "provide MESHY_API_KEY in final-resources.env; "
                "rerun make final-resources-preflight"
            ),
        ]
    )

    assert actions == [
        "make final-resource-apply-preview",
        (
            "provide MESHY_API_KEY in final-resources.env; "
            "rerun make final-resources-preflight"
        ),
    ]


def test_final_showcase_readiness_prefers_complete_provider_chain() -> None:
    complete_provider_chain = (
        "make final-resource-apply-preview; rerun make provider-handoff; "
        "rerun make live-provider-evidence"
    )
    weak_provider_chain = (
        "make final-resource-apply-preview; rerun make live-provider-evidence"
    )
    print_action = (
        "PMF_ALLOW_PRINT_PROVIDER_CALLS=1 make print-quote-configured; rerun make print-fulfillment-readiness"
    )

    actions = final_showcase_readiness._dedupe_operator_actions(
        [
            weak_provider_chain,
            complete_provider_chain,
            "make provider-handoff",
            print_action,
        ]
    )

    assert actions == [complete_provider_chain, print_action]


def test_final_showcase_readiness_filters_self_referential_operator_action() -> None:
    actions = final_showcase_readiness._filter_showcase_operator_actions(
        [
            "make final-resource-apply-preview",
            "make final-showcase-readiness",
            "make final-rehearsal-local",
        ]
    )

    assert actions == [
        "make final-resource-apply-preview",
    ]


def test_final_showcase_readiness_preserves_bare_rehearsal_when_only_action() -> None:
    actions = final_showcase_readiness._filter_showcase_operator_actions(
        ["make final-rehearsal-local"]
    )

    assert actions == ["make final-rehearsal-local"]


def test_final_showcase_readiness_dedupes_duplicate_deploy_writer_roots() -> None:
    bare_writer = (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID "
        "make mobile-write-deploy-config-auto; "
        "rerun make mobile-deploy-preflight"
    )
    detailed_writer = (
        f"{bare_writer} | Missing DEVELOPMENT_TEAM; "
        "PMF_BACKEND_BASE_URL must be iPhone-reachable"
    )

    actions = final_showcase_readiness._dedupe_operator_actions(
        [bare_writer, detailed_writer]
    )

    assert actions == [bare_writer]


def test_final_showcase_readiness_normalizes_xcode_gate_actions() -> None:
    actions = final_showcase_readiness._report_operator_actions(
        {
            "operator_actions": [
                "resolve Xcode build gate outside the app",
                (
                    "final_rehearsal_local: final_acceptance_local: resolve "
                    "Xcode build gate outside the app"
                ),
            ]
        }
    )

    assert actions == [
        (
            "accept the Xcode license outside Codex, then rerun "
            "make mobile-xcode-build-evidence"
        ),
        (
            "final_rehearsal_local: final_acceptance_local: accept the Xcode "
            "license outside Codex, then rerun make mobile-xcode-build-evidence"
        ),
    ]


def test_final_showcase_readiness_normalizes_prefixed_ios_device_actions(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_capture_source_acceptance(repo_root)
    _write_three_d_evaluation(repo_root)
    _write_npc_evaluation(repo_root)
    _write_visual_regression_blocked(repo_root)
    _write_final_acceptance_blocked_with_actions(repo_root)
    _write_ios_device_launch_rehearsal_with_actions(
        repo_root,
        extra_actions=[
            "ios_device_launch_certificate: provide iOS deploy config",
            "ios_device_launch_certificate: start backend-device-demo",
        ],
    )

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    actions = result.report["operator_actions"]

    deploy_config_action = (
        "provide iOS deploy config in Deployment.local.xcconfig; "
        "rerun make mobile-deploy-preflight"
    )
    backend_action = (
        "ios_device_launch_certificate: start backend-device-demo before device "
        "checks: make backend-device-demo; rerun make mobile-deploy-preflight"
    )

    assert result.exit_code == 2
    assert deploy_config_action in actions
    assert not any(
        action.startswith("ios_device_launch_certificate: provide iOS deploy config")
        for action in actions
    )
    assert backend_action in actions
    assert "ios_device_launch_certificate: start backend-device-demo" not in actions


def test_final_showcase_readiness_preserves_backend_device_demo_handoff_when_device_and_provider_actions_compete(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_capture_source_acceptance(repo_root)
    _write_incomplete_final_resources(repo_root)
    _write_three_d_evaluation(repo_root)
    _write_npc_evaluation(repo_root)
    _write_visual_regression(repo_root)
    _write_final_acceptance_ready(repo_root)
    _write_mobile_deploy_preflight_evidence_blocked(
        repo_root,
        checks=[
            {
                "id": "development_team",
                "label": "Apple Team ID",
                "status": "blocked",
                "detail": "Missing DEVELOPMENT_TEAM",
            },
            {
                "id": "backend_base_url",
                "label": "Backend base URL",
                "status": "blocked",
                "detail": "PMF_BACKEND_BASE_URL must be iPhone-reachable",
            },
        ],
        next_action={
            "id": "development_team",
            "label": "Apple Team ID",
            "status": "blocked",
            "command": (
                "DEVELOPMENT_TEAM=YOUR_TEAM_ID "
                "make mobile-write-deploy-config-auto"
            ),
            "detail": (
                "Missing DEVELOPMENT_TEAM; "
                "PMF_BACKEND_BASE_URL must be iPhone-reachable"
            ),
            "validation_command": "make mobile-deploy-preflight",
            "source": "first_blocker",
        },
    )
    _write_json(
        repo_root / "services/backend/.local/ios-device-launch-rehearsal.json",
        {
            "kind": "ios_device_launch_rehearsal_report",
            "status": "blocked",
            "summary": {
                "ready": 0,
                "missing": 0,
                "blocked": 1,
                "partial": 0,
                "manual": 0,
                "live": 0,
            },
            "sequence": [],
            "operator_actions": [
                (
                    "DEVELOPMENT_TEAM=YOUR_TEAM_ID "
                    "make mobile-write-deploy-config-auto; "
                    "rerun make mobile-deploy-preflight"
                ),
                (
                    "make final-resource-apply-preview; "
                    "rerun make provider-handoff; "
                    "rerun make live-provider-evidence"
                ),
                (
                    "PMF_ALLOW_PRINT_PROVIDER_CALLS=1 "
                    "make print-quote-configured; "
                    "rerun make print-fulfillment-readiness"
                ),
                (
                    "accept the Xcode license outside Codex, then rerun "
                    "make mobile-xcode-build-evidence"
                ),
                (
                    "start backend-device-demo before device checks: "
                    "make backend-device-demo; rerun make mobile-deploy-preflight"
                ),
            ],
            "commands": ["make ios-device-launch-rehearsal"],
            "safety": {
                "provider_calls": False,
                "live_provider_calls": False,
                "writes_backend_env": False,
                "writes_ios_deploy_config": False,
                "global_mutation": False,
                "xcode_or_signing": False,
                "keychain_writes": False,
                "provider_secrets_in_report": False,
                "local_paths_in_report": False,
            },
        },
    )

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    actions = result.report["operator_actions"]
    backend_action = (
        "start backend-device-demo before device checks: "
        "make backend-device-demo; rerun make mobile-deploy-preflight"
    )

    assert result.exit_code == 2
    assert actions[0] == (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID make mobile-write-deploy-config-auto; "
        "rerun make mobile-deploy-preflight"
    )
    assert actions.count(backend_action) == 1
    assert actions.index(backend_action) < actions.index(
        "provide MESHY_API_KEY in final-resources.env; "
        "rerun make final-resources-preflight"
    )


def test_final_showcase_readiness_prioritizes_backend_url_after_backend_demo() -> None:
    deploy_action = (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID make mobile-write-deploy-config-auto; "
        "rerun make mobile-deploy-preflight"
    )
    backend_action = (
        "start backend-device-demo before device checks: "
        "make backend-device-demo; rerun make mobile-deploy-preflight"
    )
    backend_url_action = (
        "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL; "
        "rerun make mobile-deploy-preflight"
    )
    provider_action = (
        "make final-resource-apply-preview; rerun make provider-handoff; "
        "rerun make live-provider-evidence"
    )
    print_action = (
        "PMF_ALLOW_PRINT_PROVIDER_CALLS=1 make print-quote-configured; "
        "rerun make print-fulfillment-readiness"
    )
    xcode_action = (
        "accept the Xcode license outside Codex, then rerun "
        "make mobile-xcode-build-evidence"
    )

    actions = final_showcase_readiness._prioritize_showcase_operator_actions(
        [
            deploy_action,
            provider_action,
            print_action,
            xcode_action,
            backend_action,
            backend_url_action,
        ]
    )

    assert actions[:3] == [deploy_action, backend_action, backend_url_action]
    assert actions.index(backend_url_action) < actions.index(provider_action)
    assert actions.index(backend_url_action) < actions.index(print_action)
    assert actions.index(backend_url_action) < actions.index(xcode_action)


def test_final_showcase_readiness_validates_promoted_ios_deploy_actions(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_capture_source_acceptance(repo_root)
    _write_three_d_evaluation(repo_root)
    _write_npc_evaluation(repo_root)
    _write_visual_regression(repo_root)
    _write_final_acceptance_ready(repo_root)
    _write_ios_device_launch_rehearsal_with_actions(repo_root)
    _write_mobile_deploy_preflight_evidence_blocked(
        repo_root,
        checks=[
            {
                "id": "development_team",
                "label": "Apple Team ID",
                "status": "blocked",
                "detail": "Missing DEVELOPMENT_TEAM",
            },
            {
                "id": "backend_base_url",
                "label": "Backend base URL",
                "status": "blocked",
                "detail": "PMF_BACKEND_BASE_URL must be iPhone-reachable",
            },
        ],
    )

    result = build_final_showcase_readiness_report(
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


def test_final_showcase_readiness_surfaces_saved_mobile_deploy_resource_actions(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_capture_source_acceptance(repo_root)
    _write_three_d_evaluation(repo_root)
    _write_npc_evaluation(repo_root)
    _write_visual_regression(repo_root)
    _write_final_acceptance_ready(repo_root)
    _write_ios_device_launch_rehearsal_with_actions(repo_root)
    writer_action = (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID make mobile-write-deploy-config-auto"
    )
    _write_json(
        repo_root / "services/backend/.local/mobile-deploy-preflight-evidence.json",
        {
            "kind": "mobile_deploy_preflight_evidence_report",
            "status": "blocked",
            "first_blocker": {
                "id": "development_team",
                "label": "Apple Team ID",
                "status": "blocked",
                "detail": "Missing DEVELOPMENT_TEAM",
            },
            "next_action": {
                "id": "development_team",
                "label": "Apple Team ID",
                "status": "blocked",
                "command": writer_action,
                "detail": (
                    "Missing DEVELOPMENT_TEAM; PMF_BACKEND_BASE_URL must be "
                    "iPhone-reachable"
                ),
                "validation_command": "make mobile-deploy-preflight",
                "source": "first_blocker",
            },
            "checks": [
                {
                    "id": "development_team",
                    "label": "Apple Team ID",
                    "status": "blocked",
                    "detail": "Missing DEVELOPMENT_TEAM",
                },
                {
                    "id": "backend_base_url",
                    "label": "Backend base URL",
                    "status": "blocked",
                    "detail": "PMF_BACKEND_BASE_URL must be iPhone-reachable",
                },
            ],
            "operator_actions": [
                f"{writer_action}; rerun make mobile-deploy-preflight",
            ],
        },
    )

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    actions = result.report["operator_actions"]

    assert actions[0] == f"{writer_action}; rerun make mobile-deploy-preflight"
    assert (
        "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL; "
        "rerun make mobile-deploy-preflight"
    ) in actions


def test_final_showcase_readiness_functional_regression_uses_concrete_preflight_action(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_final_acceptance_blocked_with_actions(repo_root)
    _write_mobile_deploy_preflight_evidence_blocked(
        repo_root,
        checks=[
            {
                "id": "development_team",
                "label": "Apple Team ID",
                "status": "blocked",
                "detail": "Missing DEVELOPMENT_TEAM",
            },
            {
                "id": "backend_base_url",
                "label": "Backend base URL",
                "status": "blocked",
                "detail": "PMF_BACKEND_BASE_URL must be iPhone-reachable",
            },
        ],
        next_action={
            "id": "development_team",
            "label": "Apple Team ID",
            "status": "blocked",
            "command": "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig",
            "detail": (
                "Missing DEVELOPMENT_TEAM; "
                "PMF_BACKEND_BASE_URL must be iPhone-reachable"
            ),
            "validation_command": "make mobile-deploy-preflight",
            "source": "first_blocker",
        },
    )

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )

    row = result.report["capabilities_by_id"]["functional_regression"]

    assert row["status"] == "blocked"
    assert row["command"] == "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig"
    assert row["validation_command"] == "make mobile-deploy-preflight"
    assert "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig" in row["detail"]
    assert "rerun make mobile-deploy-preflight" in row["detail"]
    assert (
        "Missing DEVELOPMENT_TEAM; PMF_BACKEND_BASE_URL must be iPhone-reachable"
        in row["detail"]
    )
    assert "make[1]" not in row["detail"]


def test_final_showcase_readiness_surfaces_final_resource_repair_action(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_final_resources(
        repo_root,
        bundle_identifier="com.example.personalmythforge",
        backend_base_url="http://192.168.1.10:8080",
    )

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )

    assert result.exit_code == 2
    assert result.report["evidence"]["final_resource_apply_preview"]["status"] == "blocked"
    assert "run make final-resource-repair" in result.report["operator_actions"]


def test_final_showcase_readiness_normalizes_legacy_final_resource_copy_action(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_capture_source_acceptance(repo_root)
    _write_three_d_evaluation(repo_root)
    _write_npc_evaluation(repo_root)
    _write_visual_regression_blocked(repo_root)
    _write_final_acceptance_blocked_with_actions(repo_root)
    _write_ios_device_launch_rehearsal_with_actions(
        repo_root,
        extra_actions=[
            (
                "final_rehearsal_local: ios_deploy_runbook_local: "
                "copy services/backend/final-resources.env.example to "
                "services/backend/.local/final-resources.env"
            ),
        ],
    )

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    actions = result.report["operator_actions"]
    report_text = json.dumps(result.report)

    assert result.exit_code == 2
    assert "run make final-resource-init" in actions
    assert "services/backend/final-resources.env.example" not in report_text
    assert (
        "make final-configured-preflight; "
        "rerun make configured-live-evidence-bundle"
    ) in actions
    assert "make final-handoff-index" in actions


def test_final_showcase_readiness_adds_validation_to_nested_resource_actions(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_capture_source_acceptance(repo_root)
    _write_three_d_evaluation(repo_root)
    _write_npc_evaluation(repo_root)
    _write_visual_regression_blocked(repo_root)
    _write_final_acceptance_blocked_with_actions(repo_root)
    _write_ios_device_launch_rehearsal_with_actions(
        repo_root,
        extra_actions=[
            (
                "final_rehearsal_local: ios_deploy_runbook_local: "
                "provide MESHY_API_KEY in final-resources.env"
            ),
            (
                "final_rehearsal_local: ios_deploy_runbook_local: "
                "provide OPENAI_API_KEY in final-resources.env"
            ),
        ],
    )

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    actions = result.report["operator_actions"]

    meshy_action = (
        "provide MESHY_API_KEY in final-resources.env; "
        "rerun make final-resources-preflight"
    )
    openai_action = (
        "provide OPENAI_API_KEY in final-resources.env; "
        "rerun make final-resources-preflight"
    )

    assert actions.count(meshy_action) == 1
    assert actions.count(openai_action) == 1
    assert not any(
        action.startswith(
            "final_rehearsal_local: ios_deploy_runbook_local: "
            "provide MESHY_API_KEY"
        )
        for action in actions
    )
    assert not any(
        action.startswith(
            "final_rehearsal_local: ios_deploy_runbook_local: "
            "provide OPENAI_API_KEY"
        )
        for action in actions
    )
    assert (
        "final_rehearsal_local: ios_deploy_runbook_local: "
        "provide MESHY_API_KEY in final-resources.env"
    ) not in actions
    assert (
        "final_rehearsal_local: ios_deploy_runbook_local: "
        "provide OPENAI_API_KEY in final-resources.env"
    ) not in actions


def test_final_showcase_readiness_adds_validation_to_ios_resource_actions(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_capture_source_acceptance(repo_root)
    _write_three_d_evaluation(repo_root)
    _write_npc_evaluation(repo_root)
    _write_visual_regression_blocked(repo_root)
    _write_final_acceptance_blocked_with_actions(repo_root)
    _write_ios_device_launch_rehearsal_with_actions(
        repo_root,
        extra_actions=[
            (
                "final_rehearsal_local: ios_deploy_runbook_local: "
                "provide DEVELOPMENT_TEAM in final-resources.env"
            ),
            (
                "final_rehearsal_local: ios_deploy_runbook_local: "
                "provide PRODUCT_BUNDLE_IDENTIFIER in final-resources.env"
            ),
        ],
    )

    result = build_final_showcase_readiness_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    actions = result.report["operator_actions"]

    development_team_action = (
        "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig; "
        "rerun make mobile-deploy-preflight"
    )
    bundle_identifier_action = (
        "provide PRODUCT_BUNDLE_IDENTIFIER in Deployment.local.xcconfig; "
        "rerun make mobile-deploy-preflight"
    )

    assert actions.count(development_team_action) == 1
    assert actions.count(bundle_identifier_action) == 1
    assert not any(
        action.startswith(
            "final_rehearsal_local: ios_deploy_runbook_local: "
            "provide DEVELOPMENT_TEAM"
        )
        for action in actions
    )
    assert not any(
        action.startswith("provide DEVELOPMENT_TEAM in final-resources.env")
        or action.startswith(
            "provide PRODUCT_BUNDLE_IDENTIFIER in final-resources.env"
        )
        or action.startswith("provide PMF_BACKEND_BASE_URL in final-resources.env")
        or action.endswith("provide DEVELOPMENT_TEAM in final-resources.env")
        or action.endswith("provide PRODUCT_BUNDLE_IDENTIFIER in final-resources.env")
        for action in actions
    )


def test_final_showcase_readiness_sanitizes_secrets_paths_and_private_context(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_final_acceptance_blocked_with_unsafe_detail(repo_root)

    result = build_final_showcase_readiness_report(
        settings=Settings(openai_api_key="sk-openai-secret"),
        repo_root=repo_root,
    )
    report_text = json.dumps(result.report)

    assert "sk-openai-secret" not in report_text
    assert str(tmp_path) not in report_text
    assert "private_message:" not in report_text
    assert "raw_context:" not in report_text
    assert "[redacted]" in report_text or "[home]" in report_text


def test_final_showcase_readiness_sanitizes_configured_bundle_detail(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    unsafe_detail = (
        "Authorization Bearer sk-provider /Users/zhexu/private "
        "file:///tmp/private.glb checkout_url"
    )
    _write_live_provider_evidence_ready(repo_root)
    _write_configured_live_evidence_bundle(
        repo_root,
        status="blocked",
        detail=unsafe_detail,
    )

    result = build_final_showcase_readiness_report(
        settings=Settings(
            three_d_provider="meshy",
            meshy_api_key="sk-meshy-test",
            npc_provider="openai",
            openai_api_key="sk-openai-test",
        ),
        repo_root=repo_root,
    )
    report_text = json.dumps(result.report)

    assert "sk-provider" not in report_text
    assert "sk-meshy-test" not in report_text
    assert "/Users/" not in report_text
    assert "file:///" not in report_text
    assert "checkout_url" not in report_text


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


def _write_capture_source_acceptance(repo_root: Path) -> None:
    _write_text(
        repo_root / "apps/mobile/ios/App/CameraCaptureView.swift",
        "UIImagePickerController\njpegData(compressionQuality:\n",
    )
    _write_text(
        repo_root / "apps/mobile/ios/App/CaptureFormView.swift",
        "\n".join(
            [
                "Take Photo",
                "generationReadinessTitle",
                "generationReadinessRouteLabel",
                "generationReadinessDetail",
                "ThreeDGenerationInputReviewView(review: generationInputReview)",
            ]
        ),
    )
    _write_text(
        repo_root / "apps/mobile/ios/App/ForgeRootView.swift",
        "\n".join(
            [
                "CameraCaptureMediaBuilder.singlePhotoSelection",
                "GuidedScanPhotoSetBuilder.mediaDrafts",
                "arkitScanPackageSelection",
                "ARKitScanPackageBuilder.selection",
                "CaptureGenerationReadinessBuilder.build",
                "captureGenerationReadiness.route.displayLabel",
                "generationInputReview: threeDGenerationInputReview",
                "ThreeDGenerationInputReviewBuilder.build",
                "CaptureGenerationReceiptView(receipt: captureGenerationReceipt)",
                "capture: state.capture",
                "isPrintQuoteApproved",
                "PrintFulfillmentReceiptBuilder.build",
                "fulfillmentReceipt: printFulfillmentReceipt",
            ]
        ),
    )
    _write_text(
        repo_root / "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/CameraCaptureMediaBuilder.swift",
        "camera-capture.jpg",
    )
    _write_text(
        repo_root / "apps/mobile/ios/App/GuidedScanCaptureView.swift",
        "ObjectCaptureSession\nObjectCaptureView(session:",
    )
    _write_text(
        repo_root / "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ARKitScanPackageBuilder.swift",
        "\n".join(
            [
                "ARKitScanPackageBuilder",
                "maximumReferenceImages = 11",
                "CaptureMediaSelection(mode: .arkitScan",
            ]
        ),
    )
    _write_text(
        repo_root / "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/CaptureGenerationReadiness.swift",
        "\n".join(
            [
                "CaptureGenerationReadinessBuilder",
                "maximumProviderSourceImages = 4",
                "CaptureGenerationRoute",
                "displayLabel",
            ]
        ),
    )
    _write_text(
        repo_root / "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ThreeDGenerationInputReview.swift",
        "\n".join(
            [
                "ThreeDGenerationInputReviewBuilder",
                "provider images",
                "Raw capture files withheld.",
            ]
        ),
    )
    _write_text(
        repo_root / "apps/mobile/ios/App/ThreeDGenerationInputReviewView.swift",
        "3D Generation Input",
    )
    _write_text(
        repo_root / "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/CaptureGenerationReceipt.swift",
        "\n".join(
            [
                "CaptureGenerationReceiptBuilder",
                "Capture-to-3D proof missing",
                "raw sources",
                "Raw capture media withheld.",
            ]
        ),
    )
    _write_text(
        repo_root / "apps/mobile/ios/App/CaptureGenerationReceiptView.swift",
        "Capture-to-3D",
    )
    _write_text(
        repo_root / "apps/mobile/ios/PersonalMythForge.xcodeproj/project.pbxproj",
        "\n".join(
            [
                "ThreeDGenerationInputReviewView.swift",
                "CaptureGenerationReceiptView.swift",
                "PrintFulfillmentReceiptView.swift",
            ]
        ),
    )
    _write_text(
        repo_root / "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
        "\n".join(
            [
                "testARKitScanPackageBuilderBuildsReadySelection",
                "testCaptureGenerationReadinessMarksGuidedScanMultiImageRoute",
                "testCaptureGenerationReadinessMarksARKitScanAssetRoute",
                "testThreeDGenerationInputReviewShowsGuidedScanProviderSelection",
                "testThreeDGenerationInputReviewRedactsUnsafeText",
                "testCaptureGenerationReceiptShowsReadyGuidedScanGeneration",
                "testCaptureGenerationReceiptRedactsUnsafeText",
                "testPrintFulfillmentReceiptRequiresApprovalBeforeHandoff",
                "testPrintFulfillmentReceiptBlocksAndRedactsUnsafeText",
            ]
        ),
    )
    _write_text(
        repo_root / "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PrintFulfillmentReceipt.swift",
        "\n".join(
            [
                "PrintFulfillmentReceiptBuilder",
                "Checkout/payment links stay withheld",
                "canHandOffToProvider",
            ]
        ),
    )
    _write_text(
        repo_root / "apps/mobile/ios/App/PrintFulfillmentReceiptView.swift",
        "Print Fulfillment",
    )
    _write_text(
        repo_root / "apps/mobile/ios/App/PrintQuoteReviewView.swift",
        "PrintFulfillmentReceiptView(receipt: fulfillmentReceipt) Approve Print Handoff",
    )


def _write_final_resources(
    repo_root: Path,
    *,
    bundle_identifier: str = "com.zhexu.personalmythforge.dev",
    backend_base_url: str = "http://10.0.0.24:8080",
) -> None:
    _write_text(
        repo_root / "services/backend/.local/final-resources.env",
        "\n".join(
            [
                "MESHY_API_KEY=sk-meshy-test",
                "OPENAI_API_KEY=sk-openai-test",
                "PRINT_PROVIDER=local",
                "DEVELOPMENT_TEAM=TEAM12345",
                f"PRODUCT_BUNDLE_IDENTIFIER={bundle_identifier}",
                f"PMF_BACKEND_BASE_URL={backend_base_url}",
                "PMF_FINAL_LAUNCH_MODE=local",
            ]
        ),
    )


def _write_incomplete_final_resources(repo_root: Path) -> None:
    _write_text(
        repo_root / "services/backend/.local/final-resources.env",
        "\n".join(
            [
                "PRINT_PROVIDER=local",
                "TREATSTOCK_API_BASE_URL=https://api.treatstock.test",
                "PMF_FINAL_LAUNCH_MODE=local",
            ]
        ),
    )


def _write_three_d_evaluation(repo_root: Path) -> None:
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
            "cases": [],
        },
    )


def _write_npc_evaluation(repo_root: Path) -> None:
    _write_json(
        repo_root / "services/backend/.local/npc-evaluation-local.json",
        {
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
        },
    )


def _write_visual_regression(repo_root: Path) -> None:
    artifacts = [
        {
            "id": artifact.id,
            "status": "passed",
        }
        for artifact in DEFAULT_VISUAL_ARTIFACTS
    ]
    _write_json(
        repo_root / "services/backend/.local/visual-regression-local.json",
        {
            "kind": "visual_regression_report",
            "status": "passed",
            "summary": {"passed": len(DEFAULT_VISUAL_ARTIFACTS), "failed": 0},
            "artifacts": artifacts,
        },
    )


def _write_visual_regression_stale_inventory(repo_root: Path) -> None:
    _write_json(
        repo_root / "services/backend/.local/visual-regression-local.json",
        {
            "kind": "visual_regression_report",
            "status": "passed",
            "summary": {"passed": 1, "failed": 0},
            "artifacts": [
                {
                    "id": "p0.118_scene_load_proof",
                    "status": "passed",
                }
            ],
        },
    )


def _write_visual_regression_blocked(repo_root: Path) -> None:
    _write_json(
        repo_root / "services/backend/.local/visual-regression-local.json",
        {
            "kind": "visual_regression_report",
            "status": "failed",
            "summary": {"passed": 9, "failed": 1},
            "artifacts": [
                {
                    "id": "p0.136_final_showcase_action_ledger",
                    "status": "failed",
                    "detail": "Action ledger visual evidence is stale.",
                }
            ],
        },
    )


def _write_final_acceptance_ready(repo_root: Path) -> None:
    _write_json(
        repo_root / "services/backend/.local/final-acceptance-local.json",
        {
            "kind": "final_acceptance_report",
            "overall_status": "passed",
            "summary": {"passed": 14, "blocked": 0, "failed": 0, "skipped": 0},
            "checks": [],
        },
    )


def _write_final_acceptance_blocked_with_actions(repo_root: Path) -> None:
    _write_json(
        repo_root / "services/backend/.local/final-acceptance-local.json",
        {
            "kind": "final_acceptance_report",
            "overall_status": "blocked",
            "summary": {"passed": 12, "blocked": 1, "failed": 0, "skipped": 0},
            "checks": [
                {
                    "id": "mobile_deploy_preflight",
                    "label": "Mobile deploy preflight",
                    "status": "blocked",
                    "classification": "blocked_by_local_ios_deploy_config",
                    "command": ["make", "mobile-deploy-preflight"],
                    "detail": "iOS deploy config is missing.",
                }
            ],
        },
    )


def _write_ios_device_launch_rehearsal_with_actions(
    repo_root: Path,
    *,
    extra_actions: list[str] | None = None,
) -> None:
    operator_actions = [
        "final_rehearsal_local: final_acceptance_local: action 1",
        "final_rehearsal_local: final_acceptance_local: action 2",
        "final_rehearsal_local: ios_deploy_runbook_local: action 1",
        "final_rehearsal_local: ios_deploy_runbook_local: action 2",
        "final_configured_preflight: action 1",
        "final_configured_preflight: action 2",
        "final_handoff_index: run make final-rehearsal-local",
        "final_handoff_index: make final-configured-preflight",
        "ios_device_launch_certificate: make final-handoff-index",
        "ios_device_launch_certificate: provide iOS deploy config",
    ]
    if extra_actions:
        operator_actions[2:2] = extra_actions
    _write_json(
        repo_root / "services/backend/.local/ios-device-launch-rehearsal.json",
        {
            "kind": "ios_device_launch_rehearsal_report",
            "status": "blocked",
            "summary": {
                "ready": 0,
                "missing": 0,
                "blocked": 1,
                "partial": 0,
                "manual": 0,
                "live": 0,
            },
            "sequence": [],
            "operator_actions": operator_actions,
            "commands": ["make ios-device-launch-rehearsal"],
            "safety": {
                "provider_calls": False,
                "live_provider_calls": False,
                "writes_backend_env": False,
                "writes_ios_deploy_config": False,
                "global_mutation": False,
                "xcode_or_signing": False,
                "keychain_writes": False,
                "provider_secrets_in_report": False,
                "raw_media_in_report": False,
                "payment_links_in_report": False,
                "local_paths_in_report": False,
            },
        },
    )


def _write_final_acceptance_blocked_with_unsafe_detail(repo_root: Path) -> None:
    _write_json(
        repo_root / "services/backend/.local/final-acceptance-local.json",
        {
            "kind": "final_acceptance_report",
            "overall_status": "blocked",
            "summary": {"passed": 12, "blocked": 1, "failed": 0, "skipped": 0},
            "checks": [
                {
                    "id": "private_context_guard",
                    "label": "Private context guard",
                    "status": "blocked",
                    "classification": "blocked_by_private_context",
                    "command": ["make", "final-acceptance-local"],
                    "stderr_tail": (
                        f"private_message: hello from {repo_root}/private "
                        "raw_context: bearer sk-openai-secret"
                    ),
                }
            ],
        },
    )


def _write_live_provider_evidence_ready(
    repo_root: Path,
    *,
    configured_launch_status: str = "ready",
    provider_detail: str = "Meshy and OpenAI providers are ready.",
) -> None:
    local_dir = repo_root / "services/backend/.local"
    _write_json(
        local_dir / "provider-handoff.json",
        {
            "kind": "provider_handoff_report",
            "core_real_ready": True,
            "missing_env": [],
            "detail": provider_detail,
        },
    )
    _write_json(
        local_dir / "3d-evaluation-configured.json",
        {
            "kind": "three_d_evaluation_report",
            "provider": "meshy",
            "succeeded": 20,
            "failed": 0,
        },
    )
    _write_json(
        local_dir / "npc-evaluation-configured.json",
        {
            "kind": "npc_agent_evaluation_report",
            "provider": "openai",
            "succeeded": 6,
            "failed": 0,
        },
    )
    _write_json(
        local_dir / "final-acceptance-configured.json",
        {
            "kind": "final_acceptance_report",
            "overall_status": "passed",
            "summary": {"passed": 14, "blocked": 0, "failed": 0, "skipped": 0},
        },
    )
    _write_json(
        local_dir / "final-demo-launch-configured.json",
        {
            "kind": "final_demo_launch_report",
            "mode": "configured",
            "overall_status": configured_launch_status,
        },
    )


def _write_configured_live_evidence_bundle(
    repo_root: Path,
    *,
    status: str,
    detail: str = "Configured evidence bundle is ready.",
) -> None:
    operator_actions = []
    current_blocker = None
    if status != "ready":
        operator_actions = [
            f"run make configured-live-evidence-bundle to refresh configured evidence bundle: {detail}"
        ]
        current_blocker = {
            "id": "configured_live_evidence_bundle",
            "label": "Configured live evidence bundle",
            "status": status,
            "command": "make configured-live-evidence-bundle",
            "detail": detail,
        }
    _write_json(
        repo_root / "services/backend/.local/configured-live-evidence-bundle.json",
        {
            "kind": "configured_live_evidence_bundle_report",
            "status": status,
            "summary": {
                "evidence_files": 5,
                "evidence_ready": 5 if status == "ready" else 4,
                "evidence_missing": 0,
                "evidence_blocked": 0 if status == "ready" else 1,
                "commands": 10,
                "commands_ready": 10 if status == "ready" else 9,
                "commands_run": 0,
            },
            "current_blocker": current_blocker,
            "operator_actions": operator_actions,
            "commands": ["make configured-live-evidence-bundle"],
            "safety": {
                "commands_run": False,
                "provider_calls": False,
                "live_provider_calls": False,
                "writes_backend_env": False,
                "writes_ios_deploy_config": False,
                "global_mutation": False,
                "xcode_or_signing": False,
                "keychain_writes": False,
                "provider_secrets_in_report": False,
                "raw_private_context_in_report": False,
                "raw_media_in_report": False,
                "payment_links_in_report": False,
                "local_paths_in_report": False,
            },
        },
    )


def _write_mobile_deploy_preflight_evidence_ready(repo_root: Path) -> None:
    _write_json(
        repo_root / "services/backend/.local/mobile-deploy-preflight-evidence.json",
        {
            "kind": "mobile_deploy_preflight_evidence_report",
            "status": "ready",
            "command": "make mobile-deploy-preflight",
            "script": "apps/mobile/ios/scripts/deploy_preflight.sh",
            "exit_code": 0,
            "checks": [
                {
                    "id": "deploy_preflight",
                    "label": "iOS deploy preflight",
                    "status": "ready",
                    "detail": "iOS deploy preflight passed.",
                },
                {
                    "id": "backend_health",
                    "label": "Backend health",
                    "status": "ready",
                    "detail": "Backend health: ok",
                },
            ],
            "stdout_lines": [
                "iOS deploy preflight passed.",
                "Backend health: ok",
            ],
            "stderr_lines": [],
            "operator_actions": [],
            "safety": {
                "commands_run": True,
                "provider_calls": False,
                "live_provider_calls": False,
                "writes_backend_env": False,
                "writes_ios_deploy_config": False,
                "global_mutation": False,
                "xcode_or_signing": False,
                "keychain_writes": False,
                "provider_secrets_in_report": False,
                "local_paths_in_report": False,
            },
        },
    )


def _write_mobile_deploy_preflight_evidence_blocked(
    repo_root: Path,
    *,
    checks: list[dict[str, str]],
    next_action: dict[str, object] | None = None,
) -> None:
    _write_json(
        repo_root / "services/backend/.local/mobile-deploy-preflight-evidence.json",
        {
            "kind": "mobile_deploy_preflight_evidence_report",
            "status": "blocked",
            "first_blocker": checks[0] if checks else None,
            "next_action": next_action,
            "command": "make mobile-deploy-preflight",
            "script": "apps/mobile/ios/scripts/deploy_preflight.sh",
            "exit_code": 2,
            "checks": checks,
            "stdout_lines": [],
            "stderr_lines": [str(check["detail"]) for check in checks],
            "operator_actions": [
                "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig",
                "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL",
            ],
            "safety": {
                "commands_run": True,
                "provider_calls": False,
                "live_provider_calls": False,
                "writes_backend_env": False,
                "writes_ios_deploy_config": False,
                "global_mutation": False,
                "xcode_or_signing": False,
                "keychain_writes": False,
                "provider_secrets_in_report": False,
                "local_paths_in_report": False,
            },
        },
    )


def _write_mobile_xcode_build_evidence_blocked(repo_root: Path) -> None:
    _write_json(
        repo_root / "services/backend/.local/mobile-xcode-build-evidence.json",
        {
            "kind": "mobile_xcode_build_evidence_report",
            "status": "blocked",
            "classification": "blocked_by_apple_sdk_license",
            "command": "make mobile-xcode-build",
            "script": "apps/mobile/ios/scripts/xcode_build_gate.sh",
            "exit_code": 69,
            "checks": [
                {
                    "id": "xcode_license",
                    "label": "Xcode license",
                    "status": "blocked",
                    "detail": "Apple SDK license agreement is not accepted.",
                }
            ],
            "stdout_lines": [],
            "stderr_lines": [
                "Apple SDK license agreement is not accepted.",
            ],
            "operator_actions": [
                "accept the Xcode license outside Codex, then rerun make mobile-xcode-build-evidence"
            ],
            "safety": {
                "commands_run": True,
                "provider_calls": False,
                "live_provider_calls": False,
                "writes_backend_env": False,
                "writes_ios_deploy_config": False,
                "global_mutation": False,
                "xcode_or_signing": True,
                "code_signing_allowed": False,
                "keychain_writes": False,
                "provider_secrets_in_report": False,
                "local_paths_in_report": False,
                "writes_derived_data": True,
                "derived_data_path": "apps/mobile/ios/.build/xcode-derived-data",
            },
        },
    )


def _write_mobile_xcode_build_evidence_ready(repo_root: Path) -> None:
    _write_json(
        repo_root / "services/backend/.local/mobile-xcode-build-evidence.json",
        {
            "kind": "mobile_xcode_build_evidence_report",
            "status": "ready",
            "classification": "ready",
            "command": "make mobile-xcode-build",
            "script": "apps/mobile/ios/scripts/xcode_build_gate.sh",
            "exit_code": 0,
            "checks": [
                {
                    "id": "xcode_build_gate",
                    "label": "Xcode build gate",
                    "status": "ready",
                    "detail": "Xcode build gate passed with code signing disabled.",
                }
            ],
            "stdout_lines": [
                "Xcode build gate passed with code signing disabled.",
            ],
            "stderr_lines": [],
            "operator_actions": [],
            "safety": {
                "commands_run": True,
                "provider_calls": False,
                "live_provider_calls": False,
                "writes_backend_env": False,
                "writes_ios_deploy_config": False,
                "global_mutation": False,
                "xcode_or_signing": True,
                "code_signing_allowed": False,
                "keychain_writes": False,
                "provider_secrets_in_report": False,
                "local_paths_in_report": False,
                "writes_derived_data": True,
                "derived_data_path": "apps/mobile/ios/.build/xcode-derived-data",
            },
        },
    )


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_json(path: Path, payload: dict[str, object]) -> None:
    import json

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
