import json
from pathlib import Path

from myth_forge_api.final_operator_handoff import build_final_operator_handoff_report


STEP_ORDER = [
    "final_resources_preflight",
    "apply_final_resources",
    "backend_device_server",
    "local_final_acceptance",
    "three_d_evaluation",
    "npc_agent_evaluation",
    "ios_deploy_runbook",
    "mobile_deploy_preflight",
    "xcode_build_gate",
    "configured_final_acceptance",
]


def test_operator_handoff_blocks_missing_resources_and_acceptance_without_running_commands(
    tmp_path: Path,
) -> None:
    report = build_final_operator_handoff_report(
        mode="local",
        final_resources_preflight=_missing_resources_report(),
        final_acceptance_readiness=_missing_acceptance_report(),
        three_d_evaluation_readiness=_missing_three_d_evaluation_readiness(),
        npc_agent_evaluation_readiness=_missing_npc_evaluation_readiness(),
        ios_deploy_runbook=_missing_ios_deploy_runbook(),
        launch_phases=_local_launch_phases(),
        repo_root=tmp_path,
    )
    steps = {step["id"]: step for step in report["steps"]}

    assert report["kind"] == "final_operator_handoff_report"
    assert report["mode"] == "local"
    assert report["status"] == "blocked"
    assert [step["id"] for step in report["steps"]] == STEP_ORDER
    assert steps["final_resources_preflight"]["status"] == "missing"
    assert steps["local_final_acceptance"]["status"] == "missing"
    assert steps["configured_final_acceptance"]["status"] == "optional"
    assert report["summary"]["missing"] == 6
    assert report["summary"]["blocked"] == 0
    assert report["summary"]["optional"] == 1
    assert report["next_actions"][:2] == [
        (
            "copy services/backend/final-resources.env.example to "
            "services/backend/.local/final-resources.env"
        ),
        (
            "run make final-acceptance-local to write "
            "services/backend/.local/final-acceptance-local.json"
        ),
    ]
    assert report["safety"] == {
        "commands_run": False,
        "provider_calls": False,
        "global_mutation": False,
        "provider_secrets_in_report": False,
        "raw_media_in_report": False,
        "payment_links_in_report": False,
        "local_paths_in_report": False,
        "command_execution_from_app": False,
    }


def test_operator_handoff_promotes_saved_acceptance_blockers_and_redacts_text(
    tmp_path: Path,
) -> None:
    report = build_final_operator_handoff_report(
        mode="local",
        final_resources_preflight=_ready_resources_report(),
        final_acceptance_readiness=_blocked_acceptance_report(tmp_path),
        three_d_evaluation_readiness=_ready_three_d_evaluation_readiness(),
        npc_agent_evaluation_readiness=_ready_npc_evaluation_readiness(),
        ios_deploy_runbook=_ready_ios_deploy_runbook(),
        launch_phases=_local_launch_phases(
            apply_status="ready",
            mobile_preflight_status="ready",
        ),
        repo_root=tmp_path,
    )
    report_text = json.dumps(report)
    steps = {step["id"]: step for step in report["steps"]}

    assert report["status"] == "blocked"
    assert steps["local_final_acceptance"]["status"] == "blocked"
    assert steps["mobile_deploy_preflight"]["status"] == "blocked"
    assert steps["mobile_deploy_preflight"]["source"] == "final_acceptance_readiness"
    assert steps["xcode_build_gate"]["status"] == "blocked"
    assert report["next_actions"] == [
        "provide iOS deploy config and rerun mobile deploy preflight",
        "resolve Xcode build gate outside the app",
    ]
    assert str(tmp_path) not in report_text
    assert "/Users/" not in report_text
    assert "sk-secret" not in report_text
    assert "checkout_url" not in report_text
    assert "file:///tmp" not in report_text


def test_operator_handoff_marks_configured_acceptance_as_live_consent_gate(
    tmp_path: Path,
) -> None:
    report = build_final_operator_handoff_report(
        mode="configured",
        final_resources_preflight=_ready_resources_report(),
        final_acceptance_readiness=_ready_acceptance_report(),
        three_d_evaluation_readiness=_ready_three_d_evaluation_readiness(),
        npc_agent_evaluation_readiness=_ready_npc_evaluation_readiness(),
        ios_deploy_runbook=_ready_ios_deploy_runbook(),
        launch_phases=_configured_launch_phases(),
        repo_root=tmp_path,
    )
    steps = {step["id"]: step for step in report["steps"]}

    assert report["status"] == "partial"
    assert report["summary"]["live"] == 1
    assert steps["configured_final_acceptance"]["status"] == "live"
    assert steps["configured_final_acceptance"]["requires_consent"] is True
    assert "--allow-live-provider-calls" in steps["configured_final_acceptance"]["command"]
    assert report["next_actions"] == [
        (
            "run configured final acceptance only after live provider cost review "
            "and --allow-live-provider-calls consent"
        ),
        "run Xcode build gate manually on the Mac: make mobile-xcode-build",
    ]
    assert report["safety"]["provider_calls"] is False
    assert report["safety"]["commands_run"] is False


def test_operator_handoff_includes_ready_three_d_evaluation_step(tmp_path: Path) -> None:
    report = build_final_operator_handoff_report(
        mode="local",
        final_resources_preflight=_ready_resources_report(),
        final_acceptance_readiness=_ready_acceptance_report(),
        three_d_evaluation_readiness=_ready_three_d_evaluation_readiness(),
        npc_agent_evaluation_readiness=_ready_npc_evaluation_readiness(),
        ios_deploy_runbook=_ready_ios_deploy_runbook(),
        launch_phases=_local_launch_phases(
            apply_status="ready",
            mobile_preflight_status="ready",
        ),
        repo_root=tmp_path,
    )
    steps = {step["id"]: step for step in report["steps"]}
    step_ids = [step["id"] for step in report["steps"]]

    assert steps["three_d_evaluation"]["status"] == "ready"
    assert "evaluate-3d" in steps["three_d_evaluation"]["command"]
    assert step_ids.index("local_final_acceptance") < step_ids.index(
        "three_d_evaluation"
    )
    assert step_ids.index("three_d_evaluation") < step_ids.index(
        "npc_agent_evaluation"
    )
    assert all("evaluate-3d" not in action for action in report["next_actions"])


def test_operator_handoff_includes_ready_npc_evaluation_step(tmp_path: Path) -> None:
    report = build_final_operator_handoff_report(
        mode="local",
        final_resources_preflight=_ready_resources_report(),
        final_acceptance_readiness=_ready_acceptance_report(),
        three_d_evaluation_readiness=_ready_three_d_evaluation_readiness(),
        npc_agent_evaluation_readiness=_ready_npc_evaluation_readiness(),
        ios_deploy_runbook=_ready_ios_deploy_runbook(),
        launch_phases=_local_launch_phases(
            apply_status="ready",
            mobile_preflight_status="ready",
        ),
        repo_root=tmp_path,
    )
    steps = {step["id"]: step for step in report["steps"]}
    step_ids = [step["id"] for step in report["steps"]]

    assert steps["npc_agent_evaluation"]["status"] == "ready"
    assert "evaluate-npc" in steps["npc_agent_evaluation"]["command"]
    assert step_ids.index("local_final_acceptance") < step_ids.index(
        "npc_agent_evaluation"
    )
    assert step_ids.index("npc_agent_evaluation") < step_ids.index(
        "mobile_deploy_preflight"
    )
    assert all("evaluate-npc" not in action for action in report["next_actions"])


def test_operator_handoff_surfaces_missing_npc_evaluation_action(
    tmp_path: Path,
) -> None:
    report = build_final_operator_handoff_report(
        mode="local",
        final_resources_preflight=_ready_resources_report(),
        final_acceptance_readiness=_ready_acceptance_report(),
        three_d_evaluation_readiness=_ready_three_d_evaluation_readiness(),
        npc_agent_evaluation_readiness=_missing_npc_evaluation_readiness(),
        ios_deploy_runbook=_ready_ios_deploy_runbook(),
        launch_phases=_local_launch_phases(
            apply_status="ready",
            mobile_preflight_status="ready",
        ),
        repo_root=tmp_path,
    )
    steps = {step["id"]: step for step in report["steps"]}

    assert steps["npc_agent_evaluation"]["status"] == "missing"
    assert "evaluate-npc" in " ".join(report["next_actions"])


def test_operator_handoff_redacts_blocked_npc_evaluation_detail(
    tmp_path: Path,
) -> None:
    readiness = _blocked_npc_evaluation_readiness()

    report = build_final_operator_handoff_report(
        mode="local",
        final_resources_preflight=_ready_resources_report(),
        final_acceptance_readiness=_ready_acceptance_report(),
        three_d_evaluation_readiness=_ready_three_d_evaluation_readiness(),
        npc_agent_evaluation_readiness=readiness,
        ios_deploy_runbook=_ready_ios_deploy_runbook(),
        launch_phases=_local_launch_phases(
            apply_status="ready",
            mobile_preflight_status="ready",
        ),
        repo_root=tmp_path,
    )
    report_text = json.dumps(report)
    steps = {step["id"]: step for step in report["steps"]}

    assert steps["npc_agent_evaluation"]["status"] == "blocked"
    assert "npc_agent_evaluation_failed" in report_text
    assert "test-secret" not in report_text
    assert "private_message:" not in report_text
    assert "/Users/" not in report_text
    assert "file://" not in report_text


def test_operator_handoff_includes_ios_deploy_runbook_before_deploy_preflight(
    tmp_path: Path,
) -> None:
    report = build_final_operator_handoff_report(
        mode="local",
        final_resources_preflight=_ready_resources_report(),
        final_acceptance_readiness=_ready_acceptance_report(),
        three_d_evaluation_readiness=_ready_three_d_evaluation_readiness(),
        npc_agent_evaluation_readiness=_ready_npc_evaluation_readiness(),
        ios_deploy_runbook=_ready_ios_deploy_runbook(),
        launch_phases=_local_launch_phases(
            apply_status="ready",
            mobile_preflight_status="ready",
        ),
        repo_root=tmp_path,
    )
    steps = {step["id"]: step for step in report["steps"]}
    step_ids = [step["id"] for step in report["steps"]]

    assert steps["ios_deploy_runbook"]["status"] == "partial"
    assert steps["ios_deploy_runbook"]["command"] == "make ios-deploy-runbook-local"
    assert step_ids.index("npc_agent_evaluation") < step_ids.index(
        "ios_deploy_runbook"
    )
    assert step_ids.index("ios_deploy_runbook") < step_ids.index(
        "mobile_deploy_preflight"
    )


def _missing_resources_report() -> dict[str, object]:
    return {
        "kind": "final_resources_preflight_report",
        "status": "missing",
        "resources_file": {
            "path": "services/backend/.local/final-resources.env",
            "exists": False,
        },
        "summary": {"ready": 0, "missing": 1, "blocked": 0, "optional": 0},
        "items": [],
        "operator_actions": [
            (
                "copy services/backend/final-resources.env.example to "
                "services/backend/.local/final-resources.env"
            )
        ],
        "safety": {
            "provider_secrets_in_report": False,
            "local_paths_in_report": False,
            "writes_backend_env": False,
            "writes_ios_deploy_config": False,
            "live_provider_calls": False,
            "global_mutation": False,
        },
    }


def _ready_resources_report() -> dict[str, object]:
    return {
        "kind": "final_resources_preflight_report",
        "status": "ready",
        "resources_file": {
            "path": "services/backend/.local/final-resources.env",
            "exists": True,
        },
        "summary": {"ready": 12, "missing": 0, "blocked": 0, "optional": 2},
        "items": [],
        "operator_actions": [],
        "safety": {
            "provider_secrets_in_report": False,
            "local_paths_in_report": False,
            "writes_backend_env": False,
            "writes_ios_deploy_config": False,
            "live_provider_calls": False,
            "global_mutation": False,
        },
    }


def _missing_acceptance_report() -> dict[str, object]:
    return {
        "kind": "final_acceptance_readiness_report",
        "status": "missing",
        "source_file": {
            "path": "services/backend/.local/final-acceptance-local.json",
            "exists": False,
        },
        "summary": {"passed": 0, "blocked": 0, "failed": 0, "skipped": 0},
        "blockers": [],
        "operator_actions": [
            (
                "run make final-acceptance-local to write "
                "services/backend/.local/final-acceptance-local.json"
            )
        ],
        "safety": {
            "commands_run": False,
            "provider_calls": False,
            "global_mutation": False,
            "provider_secrets_in_report": False,
            "raw_media_in_report": False,
            "payment_links_in_report": False,
            "local_paths_in_report": False,
        },
    }


def _blocked_acceptance_report(tmp_path: Path) -> dict[str, object]:
    return {
        "kind": "final_acceptance_readiness_report",
        "status": "blocked",
        "source_file": {
            "path": "services/backend/.local/final-acceptance-local.json",
            "exists": True,
        },
        "summary": {"passed": 12, "blocked": 2, "failed": 0, "skipped": 0},
        "blockers": [
            {
                "id": "mobile_deploy_preflight",
                "label": "iOS deploy preflight",
                "status": "blocked",
                "classification": "blocked_by_local_ios_deploy_config",
                "command": "make mobile-deploy-preflight",
                "detail": f"Missing DEVELOPMENT_TEAM at {tmp_path}/repo /Users/zhexu/private",
            },
            {
                "id": "mobile_xcode_build",
                "label": "Xcode build gate",
                "status": "blocked",
                "classification": "blocked_by_apple_sdk_license",
                "command": "make mobile-xcode-build",
                "detail": "license blocked sk-secret checkout_url file:///tmp/private",
            },
        ],
        "operator_actions": [
            "provide iOS deploy config and rerun mobile deploy preflight",
            "resolve Xcode build gate outside the app",
        ],
        "safety": {
            "commands_run": False,
            "provider_calls": False,
            "global_mutation": False,
            "provider_secrets_in_report": False,
            "raw_media_in_report": False,
            "payment_links_in_report": False,
            "local_paths_in_report": False,
        },
    }


def _ready_acceptance_report() -> dict[str, object]:
    return {
        "kind": "final_acceptance_readiness_report",
        "status": "ready",
        "source_file": {
            "path": "services/backend/.local/final-acceptance-local.json",
            "exists": True,
        },
        "summary": {"passed": 14, "blocked": 0, "failed": 0, "skipped": 0},
        "blockers": [],
        "operator_actions": ["final acceptance is ready"],
        "safety": {
            "commands_run": False,
            "provider_calls": False,
            "global_mutation": False,
            "provider_secrets_in_report": False,
            "raw_media_in_report": False,
            "payment_links_in_report": False,
            "local_paths_in_report": False,
        },
    }


def _ready_three_d_evaluation_readiness() -> dict[str, object]:
    return {
        "kind": "three_d_evaluation_readiness_report",
        "status": "ready",
        "summary": {"total_cases": 20, "succeeded": 20, "failed": 0},
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
        "blockers": [],
        "operator_actions": ["3D evaluation is ready"],
        "safety": {
            "commands_run": False,
            "provider_calls": False,
            "global_mutation": False,
        },
    }


def _missing_three_d_evaluation_readiness() -> dict[str, object]:
    return {
        "kind": "three_d_evaluation_readiness_report",
        "status": "missing",
        "summary": {"total_cases": 0, "succeeded": 0, "failed": 0},
        "coverage": {
            "input_modes": {
                "text_prompt": 0,
                "single_image": 0,
                "multi_image": 0,
                "unknown": 0,
            },
            "variant_roles": {},
            "scene_loadable_cases": 0,
        },
        "blockers": [],
        "operator_actions": [
            (
                "run make backend-evaluate-3d to write "
                "services/backend/.local/3d-evaluation-local.json"
            )
        ],
        "safety": {
            "commands_run": False,
            "provider_calls": False,
            "global_mutation": False,
        },
    }


def _ready_npc_evaluation_readiness() -> dict[str, object]:
    return {
        "kind": "npc_agent_evaluation_readiness_report",
        "status": "ready",
        "summary": {"total_cases": 6, "succeeded": 6, "failed": 0, "tick_steps": 2},
        "coverage": {
            "expected_npc_sets": 6,
            "trace_sets": 6,
            "proposed_action_plan_matches": 6,
            "tick_steps_completed": 12,
            "world_resolution_steps": 12,
        },
        "blockers": [],
        "operator_actions": ["NPC Agent evaluation is ready"],
        "safety": {
            "commands_run": False,
            "provider_calls": False,
            "global_mutation": False,
        },
    }


def _missing_npc_evaluation_readiness() -> dict[str, object]:
    return {
        "kind": "npc_agent_evaluation_readiness_report",
        "status": "missing",
        "summary": {"total_cases": 0, "succeeded": 0, "failed": 0, "tick_steps": 0},
        "coverage": {
            "expected_npc_sets": 0,
            "trace_sets": 0,
            "proposed_action_plan_matches": 0,
            "tick_steps_completed": 0,
            "world_resolution_steps": 0,
        },
        "blockers": [],
        "operator_actions": [
            (
                "run make backend-evaluate-npc to write "
                "services/backend/.local/npc-evaluation-local.json"
            )
        ],
        "safety": {
            "commands_run": False,
            "provider_calls": False,
            "global_mutation": False,
        },
    }


def _blocked_npc_evaluation_readiness() -> dict[str, object]:
    readiness = _missing_npc_evaluation_readiness()
    readiness["status"] = "blocked"
    readiness["summary"] = {"total_cases": 6, "succeeded": 5, "failed": 1, "tick_steps": 2}
    readiness["blockers"] = [
        {
            "id": "npc_agent_evaluation",
            "label": "NPC Agent evaluation",
            "status": "failed",
            "classification": "npc_agent_evaluation_failed",
            "command": "make backend-evaluate-npc",
            "detail": (
                "failed Authorization=Bearer test-secret private_message: raw "
                "file:///Users/example/private.txt"
            ),
        }
    ]
    readiness["operator_actions"] = ["rerun make backend-evaluate-npc and review failed cases"]
    return readiness


def _missing_ios_deploy_runbook() -> dict[str, object]:
    return {
        "kind": "ios_deploy_runbook_report",
        "mode": "local",
        "status": "missing",
        "input_slots": [],
        "command_sequence": [],
        "operator_actions": [
            "generate iOS deploy runbook with make ios-deploy-runbook"
        ],
        "safety": {
            "commands_run": False,
            "provider_calls": False,
            "global_mutation": False,
            "provider_secrets_in_report": False,
            "raw_media_in_report": False,
            "payment_links_in_report": False,
            "local_paths_in_report": False,
        },
    }


def _ready_ios_deploy_runbook() -> dict[str, object]:
    return {
        "kind": "ios_deploy_runbook_report",
        "mode": "local",
        "status": "partial",
        "input_slots": [{"id": "backend_base_url", "status": "ready"}],
        "command_sequence": [
            {"id": "mobile_deploy_preflight", "status": "ready"},
            {"id": "xcode_build_gate", "status": "manual"},
        ],
        "operator_actions": [
            "run Xcode build gate manually on the Mac: make mobile-xcode-build"
        ],
        "safety": {
            "commands_run": False,
            "provider_calls": False,
            "global_mutation": False,
            "provider_secrets_in_report": False,
            "raw_media_in_report": False,
            "payment_links_in_report": False,
            "local_paths_in_report": False,
        },
    }


def _local_launch_phases(
    *,
    apply_status: str = "missing",
    mobile_preflight_status: str = "ready",
) -> list[dict[str, object]]:
    return [
        _phase("apply_final_resources", apply_status, "make final-apply-resources"),
        _phase("backend_device_server", "ready", "make backend-device-demo"),
        _phase("provider_readiness", "ready", "provider-handoff --require-core-real"),
        _phase(
            "local_final_acceptance",
            "ready",
            "make final-acceptance-local",
        ),
        _phase(
            "configured_final_acceptance",
            "optional",
            (
                "cd services/backend && uv run python -m myth_forge_api.cli "
                "final-acceptance --profile quick --provider-mode configured "
                "--require-real-core --allow-live-provider-calls --repo-root ../.."
            ),
        ),
        _phase(
            "mobile_deploy_preflight",
            mobile_preflight_status,
            "make mobile-deploy-preflight",
        ),
        _phase("xcode_build_gate", "manual", "make mobile-xcode-build"),
    ]


def _configured_launch_phases() -> list[dict[str, object]]:
    return [
        _phase("apply_final_resources", "ready", "make final-apply-resources"),
        _phase("backend_device_server", "ready", "make backend-device-demo"),
        _phase("provider_readiness", "ready", "provider-handoff --require-core-real"),
        _phase(
            "local_final_acceptance",
            "ready",
            "make final-acceptance-local",
        ),
        _phase(
            "configured_final_acceptance",
            "ready",
            (
                "cd services/backend && uv run python -m myth_forge_api.cli "
                "final-acceptance --profile quick --provider-mode configured "
                "--require-real-core --allow-live-provider-calls --repo-root ../.."
            ),
        ),
        _phase("mobile_deploy_preflight", "ready", "make mobile-deploy-preflight"),
        _phase("xcode_build_gate", "manual", "make mobile-xcode-build"),
    ]


def _phase(phase_id: str, status: str, command: str) -> dict[str, object]:
    return {
        "id": phase_id,
        "label": phase_id.replace("_", " ").title(),
        "status": status,
        "required_for": "final demo",
        "command": command,
        "notes": [f"{phase_id} note"],
    }
