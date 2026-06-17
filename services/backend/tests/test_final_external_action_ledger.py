from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import myth_forge_api.final_external_action_ledger as final_external_action_ledger
from myth_forge_api.config import Settings
from myth_forge_api.final_external_action_ledger import (
    build_final_external_action_ledger_report,
)


VALID_LOCAL_RESOURCES = """# Filled final resources. Do not commit.
MESHY_API_KEY=meshy-secret-test
OPENAI_API_KEY=sk-openai-test
OPENAI_API_BASE_URL=https://api.openai.test/v1
PRINT_PROVIDER=local
TREATSTOCK_API_KEY=
TREATSTOCK_API_BASE_URL=https://treatstock.test
SCULPTEO_API_KEY=
DEVELOPMENT_TEAM=ABCDE12345
PRODUCT_BUNDLE_IDENTIFIER=com.zhexu.personalmythforge.dev
PMF_BACKEND_BASE_URL=http://10.0.0.24:8080
PMF_FINAL_LAUNCH_MODE=configured
CAPTURE_STORAGE_DIR=
MYTH_SESSION_STORAGE_DIR=
"""


def test_external_action_ledger_blocks_missing_resources_without_running_actions(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    result = build_final_external_action_ledger_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    report = result.report
    report_text = json.dumps(report)
    groups = {group["id"]: group for group in report["action_groups"]}
    actions = report["actions_by_id"]

    assert result.exit_code == 2
    assert report["kind"] == "final_external_action_ledger_report"
    assert report["status"] == "blocked"
    assert [group["id"] for group in report["action_groups"]] == [
        "resource_inputs",
        "safe_local_writes",
        "live_provider_costs",
        "global_machine_actions",
        "device_runtime_actions",
    ]
    assert groups["resource_inputs"]["status"] == "blocked"
    assert groups["resource_inputs"]["summary"]["missing"] >= 5
    assert actions["provide_MESHY_API_KEY"]["status"] == "missing"
    assert actions["provide_MESHY_API_KEY"]["secret"] is True
    assert actions["provide_OPENAI_API_KEY"]["secret"] is True
    assert actions["provide_DEVELOPMENT_TEAM"]["requires_user_input"] is True
    assert actions["provide_PMF_BACKEND_BASE_URL"]["command"] == (
        "make mobile-deploy-preflight"
    )
    assert actions["preview_final_resource_apply"]["command"] == (
        "make final-resource-apply-preview"
    )
    assert actions["repair_final_resources"]["status"] == "missing"
    assert actions["repair_final_resources"]["command"] == "make final-resource-init"
    assert actions["apply_final_resources"]["status"] == "blocked"
    assert actions["apply_final_resources"]["writes_repo_local_files"] is True
    assert actions["run_live_provider_evidence"]["status"] == "live"
    assert actions["run_live_provider_evidence"]["requires_cost_consent"] is True
    assert actions["run_configured_3d_evaluation"]["command"] == (
        "make backend-evaluate-3d-configured"
    )
    assert actions["run_configured_3d_evaluation"]["operator_action"] == (
        "PMF_ALLOW_LIVE_PROVIDER_CALLS=1 make backend-evaluate-3d-configured"
    )
    assert actions["run_configured_npc_evaluation"]["command"] == (
        "make backend-evaluate-npc-configured"
    )
    assert actions["run_configured_npc_evaluation"]["operator_action"] == (
        "PMF_ALLOW_LIVE_PROVIDER_CALLS=1 make backend-evaluate-npc-configured"
    )
    assert actions["run_configured_final_acceptance"]["operator_action"] == (
        "PMF_ALLOW_LIVE_PROVIDER_CALLS=1 make final-acceptance-configured"
    )
    assert "PMF_ALLOW_LIVE_PROVIDER_CALLS=1" not in (
        actions["refresh_configured_treatstock_quote"].get("operator_action", "")
    )
    assert actions["run_xcode_build_gate"]["status"] == "manual"
    assert actions["run_xcode_build_gate"]["global"] is True
    assert actions["run_xcode_build_gate"]["requires_user_confirmation"] is True
    assert report["summary"]["groups"] == 5
    assert report["summary"]["secret"] >= 3
    assert report["summary"]["requires_cost_consent"] >= 3
    assert report["summary"]["requires_user_confirmation"] >= 3
    assert report["operator_sequence"][:6] == [
        "make final-resource-requirements",
        "make final-resources-preflight",
        "make final-resource-repair-preview",
        "make final-resource-repair",
        "make final-resource-apply-preview",
        "make final-apply-resources",
    ]
    assert report["source_reports"]["final_resource_requirements"]["status"] == "blocked"
    assert report["source_reports"]["final_resource_apply_preview"]["status"] == "missing"
    assert report["source_reports"]["final_resource_repair"]["status"] == "missing"
    assert report["source_reports"]["live_provider_evidence"]["status"] == "missing"
    first_blocker = report["first_blocker"]
    next_action = report["next_action"]
    expected_device_command = (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto make mobile-write-deploy-config-auto; "
        "rerun make mobile-deploy-preflight"
    )
    assert first_blocker["id"] == "write_development_team"
    assert first_blocker["group_id"] == "device_runtime_actions"
    assert first_blocker["group_label"] == "Device runtime actions"
    assert first_blocker["classification"] == "manual_device_config_required"
    assert first_blocker["command"] == expected_device_command
    assert first_blocker["validation_command"] == "make mobile-deploy-preflight"
    assert next_action["id"] == "write_development_team"
    assert next_action["source"] == "first_blocker"
    assert next_action["command"] == expected_device_command
    assert next_action["validation_command"] == "make mobile-deploy-preflight"
    operator_actions = report["operator_actions"]
    assert "make ios-device-launch-rehearsal" not in operator_actions
    assert "make ios-device-launch-rehearsal" in report["operator_sequence"]
    assert report["operator_actions"][:3] == [
        (
            "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto make mobile-write-deploy-config-auto; "
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
    ]
    assert (
        "provide PRODUCT_BUNDLE_IDENTIFIER in Deployment.local.xcconfig; "
        "rerun make mobile-deploy-preflight"
    ) not in report["operator_actions"]
    assert not any(
        action.startswith(
            (
                "provide MESHY_API_KEY in final-resources.env",
                "provide OPENAI_API_KEY in final-resources.env",
            )
        )
        for action in operator_actions
    )
    assert (
        "make final-resource-fill-guide; rerun make final-resource-apply-preview; "
        "rerun make provider-handoff; rerun make live-provider-evidence"
    ) in operator_actions
    assert "make final-resource-apply-preview" in operator_actions
    assert "make final-apply-resources" not in operator_actions
    assert actions["apply_final_resources"]["command"] == "make final-apply-resources"
    assert "make final-apply-resources" in report["operator_sequence"]
    assert "make mobile-deploy-preflight" not in operator_actions
    assert (
        "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig; "
        "rerun make mobile-deploy-preflight"
    ) not in operator_actions
    assert (
        "provide PRODUCT_BUNDLE_IDENTIFIER in Deployment.local.xcconfig; "
        "rerun make mobile-deploy-preflight"
    ) not in operator_actions
    assert (
        "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL; "
        "rerun make mobile-deploy-preflight"
    ) in operator_actions
    assert (
        "provide PMF_BACKEND_BASE_URL in Deployment.local.xcconfig; "
        "rerun make mobile-deploy-preflight"
    ) not in operator_actions
    assert not any(action.startswith("unblock ") for action in operator_actions)
    assert report["safety"] == {
        "commands_run": False,
        "writes_backend_env": False,
        "writes_ios_deploy_config": False,
        "runs_shell_writers": False,
        "provider_calls": False,
        "live_provider_calls": False,
        "global_mutation": False,
        "xcode_or_signing": False,
        "keychain_writes": False,
        "provider_secrets_in_report": False,
        "local_paths_in_report": False,
        "requires_user_confirmation_for_global_actions": True,
        "requires_cost_consent_for_live_actions": True,
    }
    assert str(tmp_path) not in report_text
    assert "meshy-secret-test" not in report_text
    assert "sk-openai-test" not in report_text


def test_external_action_ledger_preserves_bare_rehearsal_without_specific_device_action() -> None:
    drop_bare_rehearsal = getattr(
        final_external_action_ledger,
        "_drop_bare_ios_rehearsal_when_specific_device_actions_exist",
    )
    actions = drop_bare_rehearsal(["make ios-device-launch-rehearsal"])

    assert actions == ["make ios-device-launch-rehearsal"]


def test_external_action_ledger_routes_live_provider_operator_actions_through_configured_gate() -> None:
    configured_gate_action = (
        "make final-configured-preflight; rerun make configured-live-evidence-bundle"
    )
    actions = final_external_action_ledger._operator_actions(
        [
            {
                "id": "live_provider_costs",
                "label": "Live provider costs",
                "actions": [
                    {
                        "id": "run_configured_3d_evaluation",
                        "label": "Run configured 3D evaluation",
                        "group_id": "live_provider_costs",
                        "status": "live",
                        "command": "make backend-evaluate-3d-configured",
                        "detail": "Calls Meshy and may spend Meshy credits.",
                        "operator_action": (
                            "PMF_ALLOW_LIVE_PROVIDER_CALLS=1 "
                            "make backend-evaluate-3d-configured"
                        ),
                        "requires_cost_consent": True,
                        "requires_user_input": False,
                        "requires_user_confirmation": True,
                    },
                    {
                        "id": "run_configured_npc_evaluation",
                        "label": "Run configured NPC evaluation",
                        "group_id": "live_provider_costs",
                        "status": "live",
                        "command": "make backend-evaluate-npc-configured",
                        "detail": "Calls OpenAI and may spend API credits.",
                        "operator_action": (
                            "PMF_ALLOW_LIVE_PROVIDER_CALLS=1 "
                            "make backend-evaluate-npc-configured"
                        ),
                        "requires_cost_consent": True,
                        "requires_user_input": False,
                        "requires_user_confirmation": True,
                    },
                ],
            }
        ]
    )

    assert actions == [configured_gate_action]
    assert not any("PMF_ALLOW_LIVE_PROVIDER_CALLS" in action for action in actions)


def test_external_action_ledger_ios_deploy_actions_use_mobile_preflight(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    result = build_final_external_action_ledger_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    actions = result.report["actions_by_id"]
    operator_actions = result.report["operator_actions"]

    assert actions["provide_DEVELOPMENT_TEAM"]["command"] == (
        "make mobile-deploy-preflight"
    )
    assert actions["provide_PRODUCT_BUNDLE_IDENTIFIER"]["command"] == (
        "make mobile-deploy-preflight"
    )
    assert actions["provide_PMF_BACKEND_BASE_URL"]["command"] == (
        "make mobile-deploy-preflight"
    )
    assert (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto make mobile-write-deploy-config-auto; "
        "rerun make mobile-deploy-preflight"
    ) in operator_actions
    assert (
        "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig; "
        "rerun make mobile-deploy-preflight"
    ) not in operator_actions
    assert (
        "provide PRODUCT_BUNDLE_IDENTIFIER in Deployment.local.xcconfig; "
        "rerun make mobile-deploy-preflight"
    ) not in operator_actions
    assert (
        "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL; "
        "rerun make mobile-deploy-preflight"
    ) in operator_actions
    assert (
        "provide PMF_BACKEND_BASE_URL in Deployment.local.xcconfig; "
        "rerun make mobile-deploy-preflight"
    ) not in operator_actions
    assert (
        "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig; "
        "rerun make ios-device-launch-rehearsal"
    ) not in operator_actions
    assert (
        "provide PRODUCT_BUNDLE_IDENTIFIER in Deployment.local.xcconfig; "
        "rerun make ios-device-launch-rehearsal"
    ) not in operator_actions
    assert (
        "provide PMF_BACKEND_BASE_URL in Deployment.local.xcconfig; "
        "rerun make final-resources-preflight"
    ) not in operator_actions
    assert actions["provide_MESHY_API_KEY"]["command"] == (
        "make final-resources-preflight"
    )


def test_external_action_ledger_uses_concrete_provider_and_print_handoff_actions(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    result = build_final_external_action_ledger_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    operator_actions = result.report["operator_actions"]
    provider_action = (
        "make final-resource-fill-guide; rerun make final-resource-apply-preview; "
        "rerun make provider-handoff; rerun make live-provider-evidence"
    )
    print_readiness_action = (
        "cd services/backend && uv run pytest tests/test_ios_showcase_acceptance.py; "
        "rerun make print-fulfillment-readiness"
    )

    assert provider_action in operator_actions
    assert print_readiness_action in operator_actions
    assert not any("print-quote-configured" in action for action in operator_actions)
    assert (
        "approve live provider cost before make live-provider-evidence"
        not in operator_actions
    )
    assert (
        "approve live provider cost before make print-fulfillment-readiness"
        not in operator_actions
    )


def test_external_action_ledger_prefers_print_request_before_provider_quote() -> None:
    request_action = (
        "PRINT_SOURCE_ASSET_URI=auto PRINT_CANDIDATE_URI=auto "
        "make print-quote-request-configured; "
        "rerun make print-fulfillment-readiness"
    )
    print_action = (
        "PMF_ALLOW_PRINT_PROVIDER_CALLS=1 make print-quote-configured; "
        "rerun make print-fulfillment-readiness"
    )

    actions = final_external_action_ledger._operator_actions(
        [
            {
                "actions": [
                    {
                        "id": "configured_treatstock_quote",
                        "status": "live",
                        "command": "make print-fulfillment-readiness",
                        "operator_action": print_action,
                        "requires_user_input": False,
                        "requires_user_confirmation": False,
                        "requires_cost_consent": True,
                    },
                    {
                        "id": "configured_treatstock_quote_request",
                        "status": "blocked",
                        "command": request_action,
                        "requires_user_input": False,
                        "requires_user_confirmation": False,
                        "requires_cost_consent": False,
                    },
                ]
            }
        ]
    )

    assert actions == [request_action]


def test_external_action_ledger_prefers_live_provider_child_action(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    local_dir = repo_root / "services/backend/.local"
    local_dir.mkdir(parents=True)
    (local_dir / "provider-handoff.json").write_text(
        json.dumps(
            {
                "kind": "provider_handoff_report",
                "status": "blocked",
                "core_real_ready": False,
                "next_action": {
                    "id": "three_d_provider",
                    "label": "Three D",
                    "status": "blocked",
                    "classification": "local_stub",
                    "command": "make final-resource-apply-preview",
                    "detail": "Core provider is demo-ready but not configured.",
                    "validation_command": "make provider-handoff",
                },
            }
        ),
        encoding="utf-8",
    )

    result = build_final_external_action_ledger_report(
        settings=Settings(),
        repo_root=repo_root,
    )

    operator_actions = result.report["operator_actions"]
    complete_provider_chain = (
        "make final-resource-fill-guide; rerun make final-resource-apply-preview; "
        "rerun make provider-handoff; rerun make live-provider-evidence"
    )
    assert (
        complete_provider_chain
        in operator_actions
    )
    assert (
        "make final-resource-apply-preview; rerun make live-provider-evidence"
        not in operator_actions
    )
    assert (
        "make provider-handoff; rerun make live-provider-evidence"
        not in operator_actions
    )


def test_external_action_ledger_uses_concrete_global_xcode_actions(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    result = build_final_external_action_ledger_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    actions = result.report["actions_by_id"]
    operator_actions = result.report["operator_actions"]

    expected_actions = [
        (
            "accept the Xcode license outside Codex, then rerun "
            "make mobile-xcode-build-evidence"
        ),
        (
            "configure Apple Team ID, bundle id, certificates, and device trust "
            "manually; rerun make mobile-xcode-build-evidence"
        ),
    ]

    for expected in expected_actions:
        assert expected in operator_actions
    assert (
        "run Xcode build gate manually on the Mac: make mobile-xcode-build; "
        "rerun make mobile-xcode-build-evidence"
    ) not in operator_actions

    assert not any(
        action.startswith("confirm global/manual action before")
        for action in operator_actions
    )
    assert actions["accept_apple_sdk_license"]["requires_user_confirmation"] is True
    assert actions["configure_apple_signing"]["global"] is True
    assert actions["run_xcode_build_gate"]["xcode_or_signing"] is True


def test_external_action_ledger_exposes_device_action_bundle(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    result = build_final_external_action_ledger_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    report_text = json.dumps(result.report)
    bundle = result.report["device_action_bundle"]

    assert bundle["id"] == "final_external_action_ledger_device_actions"
    assert bundle["label"] == "Final External Action Ledger Device Actions"
    assert bundle["source_report"] == "ios_deploy_runbook"
    assert bundle["status"] == "blocked"
    assert bundle["summary"]["actions"] >= 4
    assert bundle["summary"]["xcode_or_signing"] == 1
    assert bundle["summary"]["provider_calls"] == 0
    assert bundle["summary"]["global_actions"] == 0
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
    assert "meshy-secret" not in report_text


def test_external_action_ledger_top_level_actions_start_with_device_blocker(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    result = build_final_external_action_ledger_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    report = result.report
    operator_actions = report["operator_actions"]
    device_action = (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto make mobile-write-deploy-config-auto; "
        "rerun make mobile-deploy-preflight"
    )
    provider_action = (
        "make final-resource-fill-guide; rerun make final-resource-apply-preview; "
        "rerun make provider-handoff; rerun make live-provider-evidence"
    )

    assert report["first_blocker"]["id"] == "write_development_team"
    assert report["first_blocker"]["group_id"] == "device_runtime_actions"
    assert report["next_action"]["command"] == device_action
    assert operator_actions[0] == device_action
    assert provider_action in operator_actions
    assert not any(
        action.startswith(
            (
                "provide MESHY_API_KEY in final-resources.env",
                "provide OPENAI_API_KEY in final-resources.env",
            )
        )
        for action in operator_actions
    )
    assert operator_actions.index(device_action) < operator_actions.index(provider_action)
    assert (
        "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig; "
        "rerun make mobile-deploy-preflight"
    ) not in operator_actions


def test_external_action_ledger_top_level_device_blocker_promotes_validation_aware_command(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    result = build_final_external_action_ledger_report(
        settings=Settings(),
        repo_root=repo_root,
    )

    expected_command = (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto make mobile-write-deploy-config-auto; "
        "rerun make mobile-deploy-preflight"
    )

    first_blocker = result.report["first_blocker"]
    next_action = result.report["next_action"]

    assert first_blocker["id"] == "write_development_team"
    assert first_blocker["command"] == expected_command
    assert first_blocker["validation_command"] == "make mobile-deploy-preflight"
    assert next_action["command"] == expected_command
    assert next_action["validation_command"] == "make mobile-deploy-preflight"
    assert result.report["operator_actions"][0] == expected_command


def test_external_action_ledger_operator_actions_include_backend_device_demo_handoff(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    result = build_final_external_action_ledger_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    actions = result.report["actions_by_id"]
    operator_actions = result.report["operator_actions"]
    backend_action = (
        "start backend-device-demo before device checks: "
        "make backend-device-demo; rerun make mobile-deploy-preflight"
    )

    assert actions["start_backend_device_demo"]["operator_action"] == backend_action
    assert backend_action in operator_actions
    assert "make backend-device-demo" not in operator_actions


def test_external_action_ledger_prioritizes_backend_device_demo_before_provider_handoffs(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    result = build_final_external_action_ledger_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    operator_actions = result.report["operator_actions"]
    deploy_writer_action = (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto make mobile-write-deploy-config-auto; "
        "rerun make mobile-deploy-preflight"
    )
    backend_action = (
        "start backend-device-demo before device checks: "
        "make backend-device-demo; rerun make mobile-deploy-preflight"
    )
    provider_action = (
        "make final-resource-fill-guide; rerun make final-resource-apply-preview; "
        "rerun make provider-handoff; rerun make live-provider-evidence"
    )
    print_readiness_action = (
        "cd services/backend && uv run pytest tests/test_ios_showcase_acceptance.py; "
        "rerun make print-fulfillment-readiness"
    )
    xcode_action = (
        "accept the Xcode license outside Codex, then rerun "
        "make mobile-xcode-build-evidence"
    )

    assert operator_actions[:2] == [deploy_writer_action, backend_action]
    assert not any(
        action.startswith(
            (
                "provide MESHY_API_KEY in final-resources.env",
                "provide OPENAI_API_KEY in final-resources.env",
            )
        )
        for action in operator_actions
    )
    assert operator_actions.index(backend_action) < operator_actions.index(
        provider_action
    )
    assert operator_actions.index(backend_action) < operator_actions.index(
        print_readiness_action
    )
    assert operator_actions.index(backend_action) < operator_actions.index(xcode_action)


def test_external_action_ledger_prioritizes_backend_url_after_backend_device_demo(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    result = build_final_external_action_ledger_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    operator_actions = result.report["operator_actions"]
    deploy_writer_action = (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto make mobile-write-deploy-config-auto; "
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
        "make final-resource-fill-guide; rerun make final-resource-apply-preview; "
        "rerun make provider-handoff; rerun make live-provider-evidence"
    )

    assert operator_actions[:3] == [
        deploy_writer_action,
        backend_action,
        backend_url_action,
    ]
    assert not any(
        action.startswith(
            (
                "provide MESHY_API_KEY in final-resources.env",
                "provide OPENAI_API_KEY in final-resources.env",
            )
        )
        for action in operator_actions
    )
    assert operator_actions.index(backend_url_action) < operator_actions.index(
        provider_action
    )


def test_external_action_ledger_prioritizer_moves_backend_url_when_backend_demo_is_already_second() -> None:
    deploy_writer_action = (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto make mobile-write-deploy-config-auto; "
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
    provider_action = "make provider-handoff; rerun make live-provider-evidence"

    actions = final_external_action_ledger._prioritize_backend_device_demo_after_deploy_writer(
        [
            deploy_writer_action,
            backend_action,
            provider_action,
            backend_url_action,
        ]
    )

    assert actions == [
        deploy_writer_action,
        backend_action,
        backend_url_action,
        provider_action,
    ]


def test_external_action_ledger_marks_local_resource_actions_ready_without_leaks(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    write_resources(repo_root, VALID_LOCAL_RESOURCES)

    result = build_final_external_action_ledger_report(
        settings=Settings(
            three_d_provider="meshy",
            meshy_api_key="meshy-secret-test",
            npc_provider="openai",
            openai_api_key="sk-openai-test",
            print_provider="local",
        ),
        repo_root=repo_root,
    )
    report = result.report
    report_text = json.dumps(report)
    groups = {group["id"]: group for group in report["action_groups"]}
    actions = report["actions_by_id"]

    assert result.exit_code == 2
    assert report["status"] == "blocked"
    assert groups["resource_inputs"]["status"] == "ready"
    assert actions["provide_MESHY_API_KEY"]["status"] == "ready"
    assert actions["provide_OPENAI_API_KEY"]["status"] == "ready"
    assert actions["provide_DEVELOPMENT_TEAM"]["status"] == "ready"
    assert actions["provide_PMF_BACKEND_BASE_URL"]["status"] == "ready"
    assert actions["preview_final_resource_apply"]["status"] == "ready"
    assert actions["apply_final_resources"]["status"] == "ready"
    assert groups["safe_local_writes"]["status"] == "ready"
    assert groups["live_provider_costs"]["summary"]["live"] >= 3
    assert groups["global_machine_actions"]["status"] == "manual"
    assert report["summary"]["ready"] >= 7
    assert report["summary"]["live"] >= 3
    assert report["summary"]["manual"] >= 3
    assert "meshy-secret-test" not in report_text
    assert "sk-openai-test" not in report_text
    assert "10.0.0.24" not in report_text
    assert str(tmp_path) not in report_text


def test_external_action_ledger_marks_global_machine_actions_ready_from_ios_runbook(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo_root = tmp_path / "repo"
    write_resources(repo_root, VALID_LOCAL_RESOURCES)
    monkeypatch.setattr(
        final_external_action_ledger,
        "build_ios_deploy_runbook_report",
        lambda **_kwargs: ready_ios_deploy_runbook(),
    )

    result = build_final_external_action_ledger_report(
        settings=Settings(
            three_d_provider="meshy",
            meshy_api_key="meshy-secret-test",
            npc_provider="openai",
            openai_api_key="sk-openai-test",
            print_provider="local",
        ),
        repo_root=repo_root,
    )

    report = result.report
    groups = {group["id"]: group for group in report["action_groups"]}
    actions = report["actions_by_id"]
    operator_actions = report["operator_actions"]

    assert result.exit_code == 2
    assert report["status"] == "partial"
    assert groups["global_machine_actions"]["status"] == "ready"
    assert groups["global_machine_actions"]["summary"]["manual"] == 0
    assert groups["global_machine_actions"]["summary"]["ready"] == 3
    assert actions["accept_apple_sdk_license"]["status"] == "ready"
    assert actions["accept_apple_sdk_license"]["requires_user_confirmation"] is False
    assert actions["configure_apple_signing"]["status"] == "ready"
    assert actions["run_xcode_build_gate"]["status"] == "ready"
    assert report["first_blocker"]["group_id"] != "global_machine_actions"
    assert not any("Xcode license" in action for action in operator_actions)
    assert not any("mobile-xcode-build-evidence" in action for action in operator_actions)


def test_external_action_ledger_live_first_blocker_uses_guarded_operator_action(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo_root = tmp_path / "repo"
    write_resources(repo_root, VALID_LOCAL_RESOURCES)
    monkeypatch.setattr(
        final_external_action_ledger,
        "build_ios_deploy_runbook_report",
        lambda **_kwargs: ready_ios_deploy_runbook(),
    )
    monkeypatch.setattr(
        final_external_action_ledger,
        "build_print_fulfillment_readiness_report",
        lambda **_kwargs: SimpleNamespace(
            report={
                "kind": "print_fulfillment_readiness_report",
                "status": "ready",
                "summary": {"ready": 4, "blocked": 0},
            }
        ),
    )
    legacy_guarded_action = (
        "PMF_ALLOW_LIVE_PROVIDER_CALLS=1 make final-acceptance-configured; "
        "rerun make live-provider-evidence"
    )
    configured_plan_action = (
        "PMF_ALLOW_LIVE_PROVIDER_CALLS=1 make backend-evaluate-3d-configured; "
        "rerun make final-configured-evidence-plan"
    )
    monkeypatch.setattr(
        final_external_action_ledger,
        "build_live_provider_evidence_report",
        lambda **_kwargs: SimpleNamespace(
            report={
                "kind": "live_provider_evidence_report",
                "status": "blocked",
                "summary": {"blocked": 1, "requires_live_provider_consent": 3},
                "operator_actions": [legacy_guarded_action],
            }
        ),
    )
    configured_bundle_path = (
        repo_root / "services/backend/.local/configured-live-evidence-bundle.json"
    )
    configured_bundle_path.parent.mkdir(parents=True, exist_ok=True)
    configured_bundle_path.write_text(
        json.dumps(
            {
                "kind": "configured_live_evidence_bundle_report",
                "status": "blocked",
                "current_blocker": {
                    "id": "three_d_evaluation_configured",
                    "label": "Configured 3D evaluation",
                    "status": "consent_required",
                    "classification": "consent_required",
                    "command": "PMF_ALLOW_LIVE_PROVIDER_CALLS=1 make backend-evaluate-3d-configured",
                    "detail": "Missing configured 3D evaluation evidence.",
                    "validation_command": "make final-configured-evidence-plan",
                },
                "operator_actions": [configured_plan_action],
            }
        ),
        encoding="utf-8",
    )

    result = build_final_external_action_ledger_report(
        settings=Settings(
            three_d_provider="meshy",
            meshy_api_key="meshy-secret-test",
            npc_provider="openai",
            openai_api_key="sk-openai-test",
            print_provider="local",
        ),
        repo_root=repo_root,
    )

    first_blocker = result.report["first_blocker"]
    next_action = result.report["next_action"]
    operator_actions = result.report["operator_actions"]

    assert result.exit_code == 2
    assert result.report["status"] == "partial"
    assert first_blocker["id"] == "run_live_provider_evidence"
    assert first_blocker["group_id"] == "live_provider_costs"
    assert first_blocker["command"] == configured_plan_action
    assert first_blocker["validation_command"] == "make final-configured-evidence-plan"
    assert first_blocker["requires_cost_consent"] is True
    assert first_blocker["live_provider_call"] is True
    assert next_action["command"] == configured_plan_action
    assert next_action["validation_command"] == "make final-configured-evidence-plan"
    assert next_action["requires_cost_consent"] is True
    assert next_action["live_provider_call"] is True
    assert operator_actions[0] == configured_plan_action
    assert legacy_guarded_action not in operator_actions
    assert operator_actions.index(configured_plan_action) < operator_actions.index(
        "make final-configured-preflight; rerun make configured-live-evidence-bundle"
    )
    assert not any("backend-device-demo" in action for action in operator_actions)


def test_external_action_ledger_routes_repairable_final_resources_before_apply(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    write_resources(
        repo_root,
        VALID_LOCAL_RESOURCES.replace(
            "PRODUCT_BUNDLE_IDENTIFIER=com.zhexu.personalmythforge.dev",
            "PRODUCT_BUNDLE_IDENTIFIER=com.example.personalmythforge",
        ).replace(
            "PMF_BACKEND_BASE_URL=http://10.0.0.24:8080",
            "PMF_BACKEND_BASE_URL=http://192.168.1.10:8080",
        ),
    )

    result = build_final_external_action_ledger_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    report = result.report
    report_text = json.dumps(report)
    actions = report["actions_by_id"]
    repair_action = actions["repair_final_resources"]

    assert result.exit_code == 2
    assert report["status"] == "blocked"
    assert report["source_reports"]["final_resource_repair"]["status"] == "repairable"
    assert repair_action["status"] == "blocked"
    assert repair_action["command"] == "make final-resource-repair"
    assert repair_action["safe_local_write"] is True
    assert repair_action["writes_repo_local_files"] is True
    assert repair_action["classification"] == "placeholder_value"
    assert report["operator_sequence"][:5] == [
        "make final-resource-requirements",
        "make final-resources-preflight",
        "make final-resource-repair-preview",
        "make final-resource-repair",
        "make final-resource-apply-preview",
    ]
    assert "make final-resource-repair" in report["operator_actions"]
    assert "unblock repair_final_resources: make final-resource-repair" not in report[
        "operator_actions"
    ]
    assert "meshy-secret-test" not in report_text
    assert "sk-openai-test" not in report_text
    assert "192.168.1.10" not in report_text
    assert str(tmp_path) not in report_text


def write_resources(root: Path, text: str) -> Path:
    path = root / "services/backend/.local/final-resources.env"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def ready_ios_deploy_runbook() -> dict[str, object]:
    return {
        "kind": "ios_deploy_runbook_report",
        "status": "ready",
        "device_action_bundle": {
            "status": "ready",
            "actions": [
                {
                    "id": "resolve_xcode_build_gate",
                    "label": "Resolve Xcode build gate",
                    "status": "ready",
                    "command": "make mobile-xcode-build",
                    "detail": "Xcode build gate passed with code signing disabled.",
                    "global_action": True,
                    "xcode_or_signing": True,
                }
            ],
            "first_action": None,
            "summary": {
                "actions": 1,
                "ready": 1,
                "blocked": 0,
                "manual": 0,
                "global_actions": 1,
                "xcode_or_signing": 1,
            },
        },
    }
