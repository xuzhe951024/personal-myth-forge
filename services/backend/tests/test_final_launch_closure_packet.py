from __future__ import annotations

import json
from pathlib import Path

from myth_forge_api import final_launch_closure_packet
from myth_forge_api.config import Settings
from myth_forge_api.final_launch_closure_packet import (
    build_final_launch_closure_packet_report,
)


VALID_FINAL_RESOURCES = """# Filled final resources. Do not commit.
MESHY_API_KEY=meshy-secret-test
OPENAI_API_KEY=sk-openai-test
PRINT_PROVIDER=local
DEVELOPMENT_TEAM=TEAM12345
PRODUCT_BUNDLE_IDENTIFIER=com.zhexu.personalmythforge.dev
PMF_BACKEND_BASE_URL=http://10.0.0.24:8080
PMF_FINAL_LAUNCH_MODE=configured
"""

PRINT_READINESS_BACKEND_AUTO_ACTION = (
    "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto "
    "make mobile-write-deploy-config-auto; rerun make print-fulfillment-readiness"
)


def test_final_launch_closure_packet_blocks_missing_final_actions(
    tmp_path: Path,
) -> None:
    repo_root = _repo_fixture(tmp_path)

    result = build_final_launch_closure_packet_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    report = result.report
    sections = report["sections_by_id"]

    assert result.exit_code == 2
    assert report["kind"] == "final_launch_closure_packet_report"
    assert report["status"] == "blocked"
    assert report["summary"]["sections"] == 6
    assert report["summary"]["secret_actions"] >= 2
    assert report["summary"]["requires_cost_consent"] >= 1
    assert report["first_blocker"] == {
        "id": "final_showcase_readiness",
        "label": "Final showcase readiness",
        "status": "blocked",
        "classification": "ios_rehearsal_missing",
        "command": "make ios-device-launch-rehearsal",
        "detail": "iOS deploy runbook and device launch rehearsal must both be ready.",
        "section_id": "final_acceptance",
        "action_id": "final_showcase_readiness",
    }
    assert [section["id"] for section in report["sections"]] == [
        "resource_inputs",
        "safe_local_writes",
        "device_evidence",
        "live_provider_consent",
        "configured_evidence_bundle",
        "final_acceptance",
    ]
    assert sections["resource_inputs"]["status"] == "blocked"
    assert sections["resource_inputs"]["first_action"]["id"] == "provide_MESHY_API_KEY"
    assert sections["safe_local_writes"]["command"] == "make final-resource-apply-preview"
    assert sections["device_evidence"]["command"] == "make ios-device-launch-rehearsal"
    assert sections["live_provider_consent"]["requires_cost_consent"] is True
    live_actions = {
        action["id"]: action
        for action in sections["live_provider_consent"]["actions"]
    }
    assert live_actions["run_configured_3d_evaluation"]["operator_action"] == (
        "PMF_ALLOW_LIVE_PROVIDER_CALLS=1 make backend-evaluate-3d-configured; "
        "rerun make final-configured-evidence-plan"
    )
    assert live_actions["run_configured_npc_evaluation"]["operator_action"] == (
        "PMF_ALLOW_LIVE_PROVIDER_CALLS=1 make backend-evaluate-npc-configured; "
        "rerun make final-configured-evidence-plan"
    )
    assert live_actions["run_configured_final_acceptance"]["operator_action"] == (
        "PMF_ALLOW_LIVE_PROVIDER_CALLS=1 make final-acceptance-configured"
    )
    assert sections["configured_evidence_bundle"]["status"] == "blocked"
    assert sections["configured_evidence_bundle"]["command"] == (
        "make configured-live-evidence-bundle"
    )
    assert sections["configured_evidence_bundle"]["first_action"]["id"] == (
        "configured_live_evidence_bundle"
    )
    assert sections["final_acceptance"]["required"] is True
    assert sections["resource_inputs"]["first_action"]["destination"] == (
        "services/backend/.local/final-resources.env"
    )
    resource_actions = {
        action["id"]: action for action in sections["resource_inputs"]["actions"]
    }
    assert resource_actions["provide_DEVELOPMENT_TEAM"]["destination"] == (
        "apps/mobile/ios/Config/Deployment.local.xcconfig"
    )
    operator_actions = report["operator_actions"]
    actions = " ".join(operator_actions)
    configured_3d_action = (
        "PMF_ALLOW_LIVE_PROVIDER_CALLS=1 make backend-evaluate-3d-configured; "
        "rerun make final-configured-evidence-plan"
    )
    configured_npc_action = (
        "PMF_ALLOW_LIVE_PROVIDER_CALLS=1 make backend-evaluate-npc-configured; "
        "rerun make final-configured-evidence-plan"
    )
    assert "make final-resources-preflight" not in operator_actions
    assert "make print-fulfillment-readiness" not in operator_actions
    assert PRINT_READINESS_BACKEND_AUTO_ACTION not in operator_actions
    assert not any("print-quote-configured" in action for action in operator_actions)
    assert "make ios-device-launch-rehearsal" not in operator_actions
    assert "make final-resource-apply-preview" in operator_actions
    assert "make final-apply-resources" not in operator_actions
    assert not any(action.startswith("run make ") for action in operator_actions)
    assert (
        "make final-resource-fill-guide; rerun make final-resource-apply-preview; "
        "rerun make provider-handoff; rerun make live-provider-evidence"
    ) in operator_actions
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
        "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig; rerun "
        "make mobile-deploy-preflight"
    ) in operator_actions
    assert (
        "provide PRODUCT_BUNDLE_IDENTIFIER in Deployment.local.xcconfig; rerun "
        "make mobile-deploy-preflight"
    ) in operator_actions
    assert (
        "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL; rerun "
        "make mobile-deploy-preflight"
    ) in operator_actions
    assert (
        "provide PMF_BACKEND_BASE_URL in Deployment.local.xcconfig; rerun "
        "make mobile-deploy-preflight"
    ) not in operator_actions
    assert not any(
        action.startswith(
            "run DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto make mobile-write-deploy-config-auto"
        )
        for action in operator_actions
    )
    assert "provide MESHY_API_KEY" not in operator_actions
    assert "provide DEVELOPMENT_TEAM" not in operator_actions
    assert "make ios-device-launch-rehearsal" not in actions
    assert "make configured-live-evidence-bundle" not in actions
    assert configured_3d_action in operator_actions
    assert configured_npc_action in operator_actions
    assert not any("make final-acceptance-configured" in action for action in operator_actions)
    assert report["commands"][:6] == [
        "make final-resource-requirements",
        "make final-resource-fill-guide",
        "make final-external-action-ledger",
        "make ios-device-launch-rehearsal",
        "make live-provider-evidence",
        "make configured-live-evidence-bundle",
    ]
    assert report["source_reports"]["configured_live_evidence_bundle"]["status"] == (
        "missing"
    )
    assert report["safety"]["commands_run"] is False
    assert report["safety"]["global_mutation"] is False
    assert report["safety"]["live_provider_calls"] is False
    assert report["safety"]["describes_global_actions"] is True


def test_final_launch_closure_packet_prefers_promoted_deploy_writer() -> None:
    writer_action = (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto make mobile-write-deploy-config-auto; "
        "rerun make mobile-deploy-preflight"
    )
    manual_team_action = (
        "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig; "
        "rerun make mobile-deploy-preflight"
    )
    product_bundle_action = (
        "provide PRODUCT_BUNDLE_IDENTIFIER in Deployment.local.xcconfig; "
        "rerun make mobile-deploy-preflight"
    )
    backend_url_action = (
        "provide PMF_BACKEND_BASE_URL in Deployment.local.xcconfig; "
        "rerun make mobile-deploy-preflight"
    )

    actions = final_launch_closure_packet._promote_first_blocker_device_action(
        [
            manual_team_action,
            product_bundle_action,
            backend_url_action,
            f"run {writer_action}",
        ],
        first_blocker={
            "command": "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto make mobile-write-deploy-config-auto"
        },
    )

    assert actions[0] == writer_action
    assert manual_team_action not in actions
    assert not any(
        action.startswith(
            "run DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto make mobile-write-deploy-config-auto"
        )
        for action in actions
    )
    assert product_bundle_action not in actions
    assert backend_url_action in actions


def test_final_launch_closure_packet_prefers_validated_device_child_actions() -> None:
    backend_validated_action = (
        "start backend-device-demo before device checks: make backend-device-demo; "
        "rerun make mobile-deploy-preflight"
    )
    xcode_validated_action = (
        "accept the Xcode license outside Codex, then rerun "
        "make mobile-xcode-build-evidence"
    )

    actions = final_launch_closure_packet._operator_actions(
        [
            {
                "actions": [
                    {
                        "id": "backend_device_server",
                        "status": "blocked",
                        "command": "make backend-device-demo",
                        "requires_user_input": False,
                        "requires_cost_consent": False,
                        "requires_user_confirmation": False,
                    },
                    {
                        "id": "xcode_build_gate",
                        "status": "blocked",
                        "command": "make mobile-xcode-build",
                        "requires_user_input": False,
                        "requires_cost_consent": False,
                        "requires_user_confirmation": False,
                    },
                    {
                        "id": "mobile_deploy_preflight",
                        "status": "blocked",
                        "command": "make mobile-deploy-preflight",
                        "requires_user_input": False,
                        "requires_cost_consent": False,
                        "requires_user_confirmation": False,
                    },
                ]
            },
            {
                "actions": [
                    {
                        "id": "saved_backend_device_server",
                        "status": "blocked",
                        "command": backend_validated_action,
                        "requires_user_input": False,
                        "requires_cost_consent": False,
                        "requires_user_confirmation": False,
                    },
                    {
                        "id": "saved_xcode_license",
                        "status": "blocked",
                        "command": xcode_validated_action,
                        "requires_user_input": False,
                        "requires_cost_consent": False,
                        "requires_user_confirmation": False,
                    },
                ]
            },
        ],
        first_blocker=None,
    )

    assert backend_validated_action in actions
    assert xcode_validated_action in actions
    assert "make backend-device-demo" not in actions
    assert "make mobile-xcode-build" not in actions
    assert "make mobile-deploy-preflight" not in actions


def test_final_launch_closure_packet_prefers_print_request_before_provider_quote() -> None:
    request_action = (
        "PRINT_SOURCE_ASSET_URI=auto PRINT_CANDIDATE_URI=auto "
        "make print-quote-request-configured; "
        "rerun make print-fulfillment-readiness"
    )
    print_action = (
        "PMF_ALLOW_PRINT_PROVIDER_CALLS=1 make print-quote-configured; "
        "rerun make print-fulfillment-readiness"
    )

    actions = final_launch_closure_packet._operator_actions(
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


def test_final_launch_closure_packet_drops_bare_print_readiness_for_auto_request() -> None:
    request_action = (
        "PRINT_SOURCE_ASSET_URI=auto PRINT_CANDIDATE_URI=auto "
        "make print-quote-request-configured; "
        "rerun make print-fulfillment-readiness"
    )

    actions = final_launch_closure_packet._operator_actions(
        [
            {
                "actions": [
                    {
                        "id": "print_fulfillment_readiness",
                        "status": "blocked",
                        "command": "make print-fulfillment-readiness",
                        "requires_user_input": False,
                        "requires_user_confirmation": False,
                        "requires_cost_consent": False,
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


def test_final_launch_closure_packet_exposes_device_action_bundle(
    tmp_path: Path,
) -> None:
    repo_root = _repo_fixture(tmp_path)

    result = build_final_launch_closure_packet_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    bundle = result.report["device_action_bundle"]
    report_text = json.dumps(bundle)

    assert bundle["id"] == "final_launch_closure_device_actions"
    assert bundle["label"] == "Final Launch Closure Device Actions"
    assert bundle["source_report"] == "final_showcase_readiness"
    assert bundle["status"] == "blocked"
    assert bundle["first_action"]["id"] == "start_backend_device_demo"
    assert bundle["first_action"]["command"] == (
        "make backend-device-demo; rerun make mobile-deploy-preflight-evidence"
    )
    assert bundle["summary"]["actions"] == 4
    assert bundle["summary"]["blocked"] >= 1
    assert bundle["summary"]["provider_calls"] == 0
    assert bundle["summary"]["global_actions"] == 0
    assert bundle["summary"]["xcode_or_signing"] == 1
    assert bundle["safety"] == {
        "commands_run": False,
        "global_mutation": False,
        "keychain_writes": False,
        "live_provider_calls": False,
        "provider_calls": False,
        "writes_backend_env": False,
        "writes_ios_deploy_config": False,
        "xcode_or_signing": False,
    }
    assert str(tmp_path) not in report_text
    assert "sk-" not in report_text


def test_final_launch_closure_packet_device_bundle_prefers_showcase_bundle(
    tmp_path: Path,
) -> None:
    repo_root = _repo_fixture(tmp_path)
    writer_action = (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto make mobile-write-deploy-config-auto; "
        "rerun make mobile-deploy-preflight"
    )
    _write_mobile_deploy_preflight_evidence(
        repo_root,
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
                    "Missing DEVELOPMENT_TEAM; "
                    "PMF_BACKEND_BASE_URL must be iPhone-reachable"
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
        },
    )

    result = build_final_launch_closure_packet_report(
        settings=Settings(),
        repo_root=repo_root,
    )

    bundle = result.report["device_action_bundle"]
    showcase_source_bundle = result.report["source_reports"][
        "final_showcase_readiness"
    ]["device_action_bundle"]
    ios_source_bundle = result.report["source_reports"]["ios_device_evidence_bundle"][
        "device_action_bundle"
    ]

    assert bundle["source_report"] == "final_showcase_readiness"
    assert bundle["first_action"]["command"] == writer_action
    assert bundle["first_action"]["command"] == showcase_source_bundle["first_action"][
        "command"
    ]
    assert ios_source_bundle["id"] == "ios_device_evidence_actions"


def test_final_launch_closure_packet_source_reports_expose_device_action_bundles(
    tmp_path: Path,
) -> None:
    repo_root = _repo_fixture(tmp_path)
    _write_configured_live_evidence_bundle_blocked(
        repo_root,
        detail="configured live provider evidence missing",
    )

    result = build_final_launch_closure_packet_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    sources = result.report["source_reports"]
    report_text = json.dumps(result.report)

    ios_bundle = sources["ios_device_evidence_bundle"]["device_action_bundle"]
    configured_bundle = sources["configured_live_evidence_bundle"][
        "device_action_bundle"
    ]

    assert ios_bundle["id"] == "ios_device_evidence_actions"
    assert ios_bundle["status"] == "blocked"
    assert ios_bundle["first_action"]["id"] == "backend_device_server"
    assert ios_bundle["first_action"]["command"] == "make backend-device-demo"
    assert configured_bundle["id"] == "configured_live_evidence_bundle_device_actions"
    assert configured_bundle["source_report"] == "final_configured_evidence_plan"
    assert configured_bundle["status"] == "blocked"
    assert configured_bundle["first_action"]["id"] == "write_development_team"
    assert configured_bundle["first_action"]["command"] == (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto make mobile-write-deploy-config-auto"
    )
    assert configured_bundle["first_action"]["validation_command"] == (
        "make mobile-deploy-preflight"
    )
    assert result.report["device_action_bundle"]["source_report"] == (
        "final_showcase_readiness"
    )
    assert ios_bundle["safety"]["commands_run"] is False
    assert configured_bundle["safety"]["commands_run"] is False
    assert str(tmp_path) not in report_text
    assert "sk-" not in report_text


def test_final_launch_closure_packet_sources_resource_requirements_bundle(
    tmp_path: Path,
) -> None:
    repo_root = _repo_fixture(tmp_path)

    result = build_final_launch_closure_packet_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    report = result.report
    report_text = json.dumps(report)
    resource_source = report["source_reports"]["final_resource_requirements"]
    bundle = resource_source["device_action_bundle"]

    assert resource_source["kind"] == "final_resource_requirements_report"
    assert resource_source["status"] == "blocked"
    assert bundle["id"] == "final_resource_requirements_actions"
    assert bundle["source_report"] == "final_resource_requirements"
    assert bundle["first_action"]["id"] == "MESHY_API_KEY"
    assert bundle["first_action"]["validation_command"] == (
        "make final-resources-preflight"
    )
    assert bundle["safety"]["live_provider_calls"] is False
    assert "make final-resource-requirements" in report["commands"]
    assert str(tmp_path) not in report_text
    assert "meshy-secret-test" not in report_text
    assert "sk-openai-test" not in report_text


def test_final_launch_closure_packet_preserves_ios_device_nested_source_reports(
    tmp_path: Path,
) -> None:
    repo_root = _repo_fixture(tmp_path)
    _write_mobile_deploy_preflight_evidence(
        repo_root,
        {
            "kind": "mobile_deploy_preflight_evidence_report",
            "status": "blocked",
            "summary": {"blocked": 2},
            "device_action_bundle": {
                "id": "mobile_deploy_preflight_evidence_actions",
                "status": "blocked",
                "first_action": {
                    "id": "development_team",
                    "command": (
                        "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto "
                        "make mobile-write-deploy-config-auto"
                    ),
                    "validation_command": "make mobile-deploy-preflight",
                },
                "actions": [
                    {
                        "id": "development_team",
                        "status": "blocked",
                        "command": (
                            "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto "
                            "make mobile-write-deploy-config-auto"
                        ),
                        "detail": "Missing DEVELOPMENT_TEAM sk-test",
                        "manual": True,
                        "provider_calls": False,
                        "global_action": False,
                        "xcode_or_signing": False,
                    }
                ],
                "summary": {"actions": 1, "blocked": 1},
                "safety": {"commands_run": True, "xcode_or_signing": False},
            },
        },
    )
    _write_mobile_xcode_build_evidence(
        repo_root,
        {
            "kind": "mobile_xcode_build_evidence_report",
            "status": "blocked",
            "classification": "blocked_by_apple_sdk_license",
            "summary": {"blocked": 1},
            "device_action_bundle": {
                "id": "mobile_xcode_build_evidence_actions",
                "status": "blocked",
                "first_action": {
                    "id": "xcode_license",
                    "command": (
                        "accept the Xcode license outside Codex, then rerun "
                        "make mobile-xcode-build-evidence"
                    ),
                    "validation_command": "make mobile-xcode-build-evidence",
                },
                "actions": [
                    {
                        "id": "xcode_license",
                        "status": "blocked",
                        "command": (
                            "accept the Xcode license outside Codex, then rerun "
                            "make mobile-xcode-build-evidence"
                        ),
                        "detail": f"Apple SDK license at {repo_root}",
                        "manual": True,
                        "provider_calls": False,
                        "global_action": True,
                        "xcode_or_signing": True,
                    }
                ],
                "summary": {"actions": 1, "blocked": 1},
                "safety": {
                    "commands_run": True,
                    "xcode_or_signing": True,
                    "code_signing_allowed": False,
                },
            },
        },
    )

    result = build_final_launch_closure_packet_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    report_text = json.dumps(result.report)
    nested_sources = result.report["source_reports"]["ios_device_evidence_bundle"][
        "source_reports"
    ]
    deploy_bundle = nested_sources["mobile_deploy_preflight_evidence"][
        "device_action_bundle"
    ]
    xcode_bundle = nested_sources["mobile_xcode_build_evidence"][
        "device_action_bundle"
    ]

    assert deploy_bundle["id"] == "mobile_deploy_preflight_evidence_actions"
    assert deploy_bundle["first_action"]["id"] == "development_team"
    assert deploy_bundle["first_action"]["command"] == (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto make mobile-write-deploy-config-auto"
    )
    assert deploy_bundle["safety"]["commands_run"] is True
    assert xcode_bundle["id"] == "mobile_xcode_build_evidence_actions"
    assert xcode_bundle["first_action"]["id"] == "xcode_license"
    assert xcode_bundle["safety"]["xcode_or_signing"] is True
    assert xcode_bundle["safety"]["code_signing_allowed"] is False
    assert "sk-test" not in report_text
    assert str(repo_root) not in report_text


def test_final_launch_closure_packet_exposes_next_action_from_first_blocker(
    tmp_path: Path,
) -> None:
    repo_root = _repo_fixture(tmp_path)

    result = build_final_launch_closure_packet_report(
        settings=Settings(),
        repo_root=repo_root,
    )

    blocker = result.report["first_blocker"]
    action = result.report["next_action"]

    assert blocker["id"] == "final_showcase_readiness"
    assert action == {
        "id": "final_showcase_readiness",
        "label": "Final showcase readiness",
        "status": "blocked",
        "classification": "ios_rehearsal_missing",
        "command": "make ios-device-launch-rehearsal",
        "detail": "iOS deploy runbook and device launch rehearsal must both be ready.",
        "source": "first_blocker",
        "section_id": "final_acceptance",
        "action_id": "final_showcase_readiness",
    }
    assert "meshy-secret" not in json.dumps(action)


def test_final_launch_closure_packet_routes_configured_evidence_through_live_consent() -> None:
    expected_command = (
        "PMF_ALLOW_LIVE_PROVIDER_CALLS=1 make backend-evaluate-3d-configured; "
        "rerun make final-configured-evidence-plan"
    )
    configured_section = final_launch_closure_packet._configured_evidence_bundle_section(
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
            "operator_actions": [expected_command],
            "summary": {
                "evidence_ready": 0,
                "evidence_missing": 1,
                "evidence_blocked": 0,
            },
        }
    )
    configured_action = configured_section["first_action"]
    blocker = final_launch_closure_packet._first_blocker(
        [configured_section],
        showcase_readiness={
            "kind": "final_showcase_readiness_report",
            "status": "partial",
            "first_blocker": {
                "id": "game_asset_3d_generation",
                "classification": "live_3d_provider_unproven",
                "command": expected_command,
            },
        },
    )
    action = final_launch_closure_packet._next_action(blocker)
    operator_actions = final_launch_closure_packet._operator_actions(
        [configured_section],
        first_blocker=blocker,
    )

    assert configured_section["status"] == "blocked"
    assert blocker["id"] == "configured_evidence_bundle"
    assert blocker["command"] == expected_command
    assert blocker["validation_command"] == "make final-configured-evidence-plan"
    assert blocker["requires_cost_consent"] is True
    assert blocker["live_provider_call"] is True
    assert blocker["requires_user_confirmation"] is True
    assert action["command"] == expected_command
    assert action["validation_command"] == "make final-configured-evidence-plan"
    assert action["requires_cost_consent"] is True
    assert action["live_provider_call"] is True
    assert action["requires_user_confirmation"] is True
    assert configured_action["command"] == expected_command
    assert configured_action["requires_cost_consent"] is True
    assert configured_action["live_provider_call"] is True
    assert configured_action["requires_user_confirmation"] is True
    assert expected_command in operator_actions
    assert "make final-acceptance-configured" not in operator_actions


def test_final_launch_closure_packet_does_not_mix_local_stub_metadata_with_live_consent() -> None:
    local_stub_action = (
        "make final-resource-fill-guide; rerun make final-resource-apply-preview; "
        "rerun make provider-handoff; rerun make final-configured-evidence-plan"
    )
    expected_command = (
        "PMF_ALLOW_LIVE_PROVIDER_CALLS=1 make final-acceptance-configured; "
        "rerun make live-provider-evidence"
    )
    configured_section = final_launch_closure_packet._configured_evidence_bundle_section(
        {
            "kind": "configured_live_evidence_bundle_report",
            "status": "blocked",
            "current_blocker": {
                "id": "final_configured_preflight",
                "label": "Final configured preflight",
                "status": "blocked",
                "classification": "local_stub",
                "command": (
                    "make final-resource-fill-guide; rerun "
                    "make final-resource-apply-preview; rerun make provider-handoff"
                ),
                "detail": (
                    "Core provider is demo-ready but not configured as a real provider."
                ),
                "validation_command": "make provider-handoff",
            },
            "operator_actions": [local_stub_action, expected_command],
            "summary": {
                "evidence_ready": 0,
                "evidence_missing": 1,
                "evidence_blocked": 1,
            },
        }
    )
    configured_action = configured_section["first_action"]
    blocker = final_launch_closure_packet._first_blocker([configured_section])
    action = final_launch_closure_packet._next_action(blocker)

    assert configured_action["command"] == expected_command
    assert configured_action["classification"] == "consent_required"
    assert configured_action["detail"] == (
        "Live provider cost consent is required before configured evidence can be refreshed."
    )
    assert configured_action["requires_cost_consent"] is True
    assert configured_action["live_provider_call"] is True
    assert configured_action["requires_user_confirmation"] is True
    assert blocker is not None
    assert blocker["command"] == expected_command
    assert blocker["classification"] == "consent_required"
    assert blocker["detail"] == (
        "Live provider cost consent is required before configured evidence can be refreshed."
    )
    assert blocker["validation_command"] == "make live-provider-evidence"
    assert action is not None
    assert action["classification"] == "consent_required"
    assert action["validation_command"] == "make live-provider-evidence"
    assert "Core provider is demo-ready" not in configured_action["detail"]


def test_final_launch_closure_packet_keeps_section_order_for_non_device_showcase_blocker() -> None:
    blocker = final_launch_closure_packet._first_blocker(
        [
            {
                "id": "resource_inputs",
                "label": "Resource inputs",
                "status": "blocked",
                "required": True,
                "first_action": {
                    "id": "provide_MESHY_API_KEY",
                    "status": "missing",
                    "classification": "missing_required_value",
                    "command": "provide MESHY_API_KEY in final-resources.env",
                    "detail": "Backend-only secret for live Meshy 3D generation.",
                    "validation_command": "make final-resources-preflight",
                },
            },
            {
                "id": "final_acceptance",
                "label": "Final acceptance",
                "status": "blocked",
                "required": True,
                "first_action": {
                    "id": "final_showcase_readiness",
                    "status": "blocked",
                    "classification": "provider_handoff_incomplete",
                    "command": "make final-resource-apply-preview",
                    "detail": "Provider handoff incomplete.",
                    "validation_command": "make live-provider-evidence",
                },
            },
        ],
        showcase_readiness={
            "kind": "final_showcase_readiness_report",
            "status": "blocked",
            "first_blocker": {
                "id": "provider_key_handoff",
                "label": "Provider and key handoff",
                "status": "blocked",
                "classification": "provider_handoff_incomplete",
                "command": "make final-resource-apply-preview",
                "detail": "Provider handoff incomplete.",
                "validation_command": "make live-provider-evidence",
            },
        },
    )

    assert blocker == {
        "id": "resource_inputs",
        "label": "Resource inputs",
        "status": "blocked",
        "classification": "missing_required_value",
        "command": "provide MESHY_API_KEY in final-resources.env",
        "detail": "Backend-only secret for live Meshy 3D generation.",
        "section_id": "resource_inputs",
        "action_id": "provide_MESHY_API_KEY",
    }


def test_final_launch_closure_packet_prefers_ledger_child_operator_actions(
    tmp_path: Path,
) -> None:
    repo_root = _repo_fixture(tmp_path)
    _write_json(
        repo_root / "services/backend/.local/provider-handoff.json",
        {
            "kind": "provider_handoff_report",
            "status": "blocked",
            "classification": "core_real_providers_not_ready",
            "core_real_ready": False,
            "missing_env": [],
            "next_action": {
                "id": "three_d_provider",
                "label": "3D provider",
                "status": "blocked",
                "classification": "local_stub",
                "command": "make final-resource-apply-preview",
                "detail": "Core 3D provider is demo-ready but not configured.",
                "validation_command": "make provider-handoff",
                "source": "first_blocker",
            },
        },
    )

    result = build_final_launch_closure_packet_report(
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
    assert "make print-fulfillment-readiness" not in operator_actions
    assert PRINT_READINESS_BACKEND_AUTO_ACTION not in operator_actions
    assert not any("print-quote-configured" in action for action in operator_actions)
    assert (
        "approve live provider cost before make live-provider-evidence"
        not in operator_actions
    )
    assert (
        "make final-resource-apply-preview; rerun make live-provider-evidence"
        not in operator_actions
    )
    assert (
        "make provider-handoff; rerun make live-provider-evidence"
        not in operator_actions
    )
    assert (
        "approve live provider cost before make print-fulfillment-readiness"
        not in operator_actions
    )


def test_final_launch_closure_packet_replaces_blocked_bare_print_readiness_action() -> None:
    actions = final_launch_closure_packet._operator_actions(
        [
            {
                "actions": [
                    {
                        "id": "refresh_print_readiness",
                        "status": "blocked",
                        "command": "make print-fulfillment-readiness",
                        "requires_user_input": False,
                        "requires_cost_consent": False,
                        "requires_user_confirmation": False,
                    }
                ]
            }
        ],
        first_blocker=None,
    )
    assert "make print-fulfillment-readiness" not in actions
    assert PRINT_READINESS_BACKEND_AUTO_ACTION in actions


def test_final_launch_closure_packet_dedupes_backend_auto_print_handoff() -> None:
    actions = final_launch_closure_packet._operator_actions(
        [
            {
                "actions": [
                    {
                        "id": "print_fulfillment_backend_auto",
                        "status": "blocked",
                        "command": PRINT_READINESS_BACKEND_AUTO_ACTION,
                        "requires_user_input": False,
                        "requires_user_confirmation": False,
                        "requires_cost_consent": False,
                    },
                    {
                        "id": "print_fulfillment_readiness",
                        "status": "blocked",
                        "command": "make print-fulfillment-readiness",
                        "requires_user_input": False,
                        "requires_user_confirmation": False,
                        "requires_cost_consent": False,
                    },
                ]
            }
        ]
    )

    assert actions.count(PRINT_READINESS_BACKEND_AUTO_ACTION) == 1
    assert "make print-fulfillment-readiness" not in actions


def test_final_launch_closure_packet_routes_live_provider_actions_through_configured_gate() -> None:
    configured_gate_action = (
        "make final-configured-preflight; rerun make configured-live-evidence-bundle"
    )
    actions = final_launch_closure_packet._operator_actions(
        [
            {
                "actions": [
                    {
                        "id": "run_configured_3d_evaluation",
                        "status": "blocked",
                        "command": (
                            "PMF_ALLOW_LIVE_PROVIDER_CALLS=1 "
                            "make backend-evaluate-3d-configured"
                        ),
                        "requires_user_input": False,
                        "requires_user_confirmation": True,
                        "requires_cost_consent": True,
                    },
                    {
                        "id": "run_configured_npc_evaluation",
                        "status": "blocked",
                        "command": (
                            "PMF_ALLOW_LIVE_PROVIDER_CALLS=1 "
                            "make backend-evaluate-npc-configured"
                        ),
                        "requires_user_input": False,
                        "requires_user_confirmation": True,
                        "requires_cost_consent": True,
                    },
                ]
            }
        ]
    )

    assert actions == [configured_gate_action]
    assert not any("PMF_ALLOW_LIVE_PROVIDER_CALLS" in action for action in actions)


def test_final_launch_closure_packet_preserves_validated_3d_and_npc_live_actions() -> None:
    three_d_action = (
        "PMF_ALLOW_LIVE_PROVIDER_CALLS=1 make backend-evaluate-3d-configured; "
        "rerun make final-configured-evidence-plan"
    )
    npc_action = (
        "PMF_ALLOW_LIVE_PROVIDER_CALLS=1 make backend-evaluate-npc-configured; "
        "rerun make final-configured-evidence-plan"
    )

    actions = final_launch_closure_packet._operator_actions(
        [
            {
                "actions": [
                    {
                        "id": "run_configured_3d_evaluation",
                        "status": "blocked",
                        "command": "make backend-evaluate-3d-configured",
                        "operator_action": three_d_action,
                        "requires_user_input": False,
                        "requires_user_confirmation": True,
                        "requires_cost_consent": True,
                    },
                    {
                        "id": "run_configured_npc_evaluation",
                        "status": "blocked",
                        "command": "make backend-evaluate-npc-configured",
                        "operator_action": npc_action,
                        "requires_user_input": False,
                        "requires_user_confirmation": True,
                        "requires_cost_consent": True,
                    },
                    {
                        "id": "run_configured_final_acceptance",
                        "status": "blocked",
                        "command": (
                            "PMF_ALLOW_LIVE_PROVIDER_CALLS=1 "
                            "make final-acceptance-configured"
                        ),
                        "requires_user_input": False,
                        "requires_user_confirmation": True,
                        "requires_cost_consent": True,
                    },
                ]
            }
        ],
    )

    assert actions[:2] == [three_d_action, npc_action]
    assert "make final-acceptance-configured" not in actions
    assert (
        "make final-configured-preflight; rerun make configured-live-evidence-bundle"
        not in actions
    )


def test_final_launch_closure_packet_drops_short_provider_handoff_chain() -> None:
    complete_provider_chain = (
        "make final-resource-fill-guide; rerun make final-resource-apply-preview; "
        "rerun make provider-handoff; rerun make live-provider-evidence"
    )
    short_provider_chain = (
        "make final-resource-fill-guide; rerun make final-resource-apply-preview; "
        "rerun make provider-handoff"
    )

    actions = final_launch_closure_packet._operator_actions(
        [
            {
                "actions": [
                    {
                        "id": "live_provider_evidence",
                        "status": "blocked",
                        "command": complete_provider_chain,
                        "requires_user_input": False,
                        "requires_user_confirmation": False,
                        "requires_cost_consent": False,
                    },
                    {
                        "id": "provider_handoff",
                        "status": "blocked",
                        "command": short_provider_chain,
                        "requires_user_input": False,
                        "requires_user_confirmation": False,
                        "requires_cost_consent": False,
                    },
                ]
            }
        ]
    )

    assert complete_provider_chain in actions
    assert short_provider_chain not in actions


def test_final_launch_closure_packet_operator_actions_start_with_promoted_device_action(
    tmp_path: Path,
) -> None:
    repo_root = _repo_fixture(tmp_path)

    result = build_final_launch_closure_packet_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    actions = result.report["operator_actions"]
    device_action = "make ios-device-launch-rehearsal"
    specific_device_action = (
        "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig; "
        "rerun make mobile-deploy-preflight"
    )
    provider_action = (
        "make final-resource-fill-guide; rerun make final-resource-apply-preview; "
        "rerun make provider-handoff; rerun make live-provider-evidence"
    )

    assert result.report["next_action"]["command"] == device_action
    assert device_action not in actions
    assert actions[0] == specific_device_action
    assert provider_action in actions
    assert not any(
        action.startswith(
            (
                "provide MESHY_API_KEY in final-resources.env",
                "provide OPENAI_API_KEY in final-resources.env",
            )
        )
        for action in actions
    )
    assert actions.index(specific_device_action) < actions.index(provider_action)


def test_final_launch_closure_packet_prioritizes_backend_demo_after_device_handoff(
    tmp_path: Path,
) -> None:
    repo_root = _repo_fixture(tmp_path)

    result = build_final_launch_closure_packet_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    actions = result.report["operator_actions"]
    device_action = (
        "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig; "
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
    xcode_action = (
        "accept the Xcode license outside Codex, then rerun "
        "make mobile-xcode-build-evidence"
    )

    assert actions[:2] == [device_action, backend_action]
    assert not any(
        action.startswith(
            (
                "provide MESHY_API_KEY in final-resources.env",
                "provide OPENAI_API_KEY in final-resources.env",
            )
        )
        for action in actions
    )
    assert actions.index(backend_action) < actions.index(provider_action)
    assert PRINT_READINESS_BACKEND_AUTO_ACTION not in actions
    assert actions.index(backend_action) < actions.index(xcode_action)


def test_final_launch_closure_packet_prioritizes_backend_url_after_backend_demo(
    tmp_path: Path,
) -> None:
    repo_root = _repo_fixture(tmp_path)

    result = build_final_launch_closure_packet_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    actions = result.report["operator_actions"]
    deploy_action = (
        "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig; "
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

    assert actions[:3] == [deploy_action, backend_action, backend_url_action]
    assert not any(
        action.startswith(
            (
                "provide MESHY_API_KEY in final-resources.env",
                "provide OPENAI_API_KEY in final-resources.env",
            )
        )
        for action in actions
    )
    assert actions.index(backend_url_action) < actions.index(provider_action)


def test_final_launch_closure_packet_marks_resource_and_device_sections_ready(
    tmp_path: Path,
) -> None:
    repo_root = _repo_fixture(tmp_path)
    _write_final_resources(repo_root, VALID_FINAL_RESOURCES)
    _write_final_acceptance_ready(repo_root)
    _write_ios_device_launch_rehearsal_ready(repo_root)
    _write_configured_live_evidence_ready(repo_root)
    _write_configured_live_evidence_bundle_ready(repo_root)

    result = build_final_launch_closure_packet_report(
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
    sections = report["sections_by_id"]
    text = json.dumps(report)

    assert sections["resource_inputs"]["status"] == "ready"
    assert report["first_blocker"] is None or report["first_blocker"]["status"] == (
        "blocked"
    )
    assert sections["safe_local_writes"]["status"] == "ready"
    assert sections["device_evidence"]["status"] == "ready"
    assert sections["live_provider_consent"]["status"] == "blocked"
    assert sections["configured_evidence_bundle"]["status"] == "ready"
    assert sections["configured_evidence_bundle"]["first_action"]["id"] == (
        "configured_live_evidence_bundle"
    )
    assert sections["final_acceptance"]["status"] in {"ready", "blocked", "partial"}
    assert report["source_reports"]["configured_live_evidence_bundle"]["status"] == (
        "ready"
    )
    assert sections["resource_inputs"]["first_action"]["status"] == "ready"
    assert sections["device_evidence"]["first_action"]["id"] == "backend_device_server"
    bundle = report["device_action_bundle"]
    assert bundle["status"] == "ready"
    assert bundle["first_action"] is None
    assert bundle["summary"]["actions"] == 4
    assert bundle["summary"]["ready"] == 4
    assert bundle["summary"]["provider_calls"] == 0
    assert all(action["status"] == "ready" for action in bundle["actions"])
    assert report["summary"]["ready"] >= 3
    assert "meshy-secret-test" not in text
    assert "sk-openai-test" not in text
    assert "10.0.0.24" not in text
    assert str(tmp_path) not in text


def test_final_launch_closure_packet_prunes_optional_actions_before_live_consent() -> None:
    expected_live_action = (
        "PMF_ALLOW_LIVE_PROVIDER_CALLS=1 make final-acceptance-configured; "
        "rerun make live-provider-evidence"
    )

    operator_actions = final_launch_closure_packet._operator_actions(
        [
            {
                "actions": [
                    {
                        "id": "provide_OPENAI_API_BASE_URL",
                        "status": "optional",
                        "command": "make final-resources-preflight",
                        "requires_user_input": False,
                        "requires_cost_consent": False,
                        "requires_user_confirmation": False,
                    },
                    {
                        "id": "provide_TREATSTOCK_API_KEY",
                        "status": "optional",
                        "command": "make print-fulfillment-readiness",
                        "requires_user_input": False,
                        "requires_cost_consent": False,
                        "requires_user_confirmation": False,
                    },
                    {
                        "id": "configured_live_evidence_bundle",
                        "status": "blocked",
                        "command": expected_live_action,
                        "operator_action": expected_live_action,
                        "requires_user_input": False,
                        "requires_cost_consent": True,
                        "requires_user_confirmation": False,
                    },
                ]
            }
        ],
        first_blocker={"command": expected_live_action},
    )

    assert operator_actions[0] == expected_live_action
    assert "make final-resources-preflight" not in operator_actions
    assert PRINT_READINESS_BACKEND_AUTO_ACTION not in operator_actions
    assert not any("backend-device-demo" in action for action in operator_actions)


def test_final_launch_closure_packet_prunes_configured_bundle_gate_after_granular_consent() -> None:
    expected_live_action = (
        "PMF_ALLOW_LIVE_PROVIDER_CALLS=1 make backend-evaluate-3d-configured; "
        "rerun make final-configured-evidence-plan"
    )
    configured_gate_action = (
        "make final-configured-preflight; rerun make configured-live-evidence-bundle"
    )

    operator_actions = final_launch_closure_packet._operator_actions(
        [
            {
                "actions": [
                    {
                        "id": "configured_live_evidence_bundle",
                        "status": "blocked",
                        "command": expected_live_action,
                        "operator_action": expected_live_action,
                        "requires_user_input": False,
                        "requires_cost_consent": True,
                        "requires_user_confirmation": True,
                    },
                    {
                        "id": "configured_live_evidence_prerequisite",
                        "status": "blocked",
                        "command": configured_gate_action,
                        "operator_action": configured_gate_action,
                        "requires_user_input": False,
                        "requires_cost_consent": False,
                        "requires_user_confirmation": False,
                    },
                ]
            }
        ],
        first_blocker={"command": expected_live_action},
    )

    assert operator_actions == [expected_live_action]


def test_final_launch_closure_packet_redacts_unsafe_source_details(
    tmp_path: Path,
) -> None:
    repo_root = _repo_fixture(tmp_path)
    _write_final_resources(repo_root, VALID_FINAL_RESOURCES)
    _write_final_acceptance_ready(repo_root)
    _write_ios_device_launch_rehearsal_ready(repo_root)
    _write_configured_live_evidence_ready(repo_root)
    _write_final_acceptance(
        repo_root,
        {
            "kind": "final_acceptance_report",
            "overall_status": "blocked",
            "summary": {"passed": 12, "blocked": 1, "failed": 0, "skipped": 0},
            "checks": [
                {
                    "id": "mobile_deploy_preflight",
                    "label": "iOS deploy preflight",
                    "status": "blocked",
                    "classification": "blocked_by_local_ios_backend_health",
                    "command": ["make", "mobile-deploy-preflight"],
                    "stderr_tail": (
                        "Authorization=Bearer sk-secret /Users/zhexu/private "
                        "file:///tmp/private checkout_url=https://pay.example"
                    ),
                }
            ],
        },
    )
    _write_ios_device_launch_rehearsal(
        repo_root,
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
            "sequence": [
                {
                    "id": "final_handoff_index",
                    "label": "Final handoff index",
                    "status": "blocked",
                    "command": (
                        "make final-handoff-index sk-secret "
                        "/Users/zhexu/private file:///tmp/private"
                    ),
                    "classification": "stale_report",
                }
            ],
            "operator_actions": [
                "rerun with api_key=secret Bearer token https://checkout.example/pay"
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
                "raw_media_in_report": False,
                "payment_links_in_report": False,
                "local_paths_in_report": False,
            },
        },
    )
    _write_configured_live_evidence_bundle_blocked(
        repo_root,
        detail=(
            "Configured bundle blocked sk-configured /Users/zhexu/private "
            "file:///tmp/private checkout_url Bearer token"
        ),
    )

    result = build_final_launch_closure_packet_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    text = json.dumps(result.report)

    assert result.exit_code == 2
    assert result.report["first_blocker"] is not None
    assert result.report["first_blocker"]["id"] == "final_showcase_readiness"
    assert "[redacted]" in text
    assert "sk-secret" not in text
    assert "sk-configured" not in text
    assert "/Users/" not in text
    assert "file:///" not in text
    assert "checkout_url" not in text
    assert "pay.example" not in text
    assert "api_key=secret" not in text
    assert "Bearer" not in text


def _repo_fixture(tmp_path: Path) -> Path:
    repo_root = tmp_path / "repo"
    (repo_root / "apps/mobile/ios/Config").mkdir(parents=True)
    (repo_root / "services/backend/.local").mkdir(parents=True)
    (repo_root / "apps/mobile/ios/Config/Deployment.xcconfig").write_text(
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
    return repo_root


def _write_final_resources(repo_root: Path, payload: str) -> None:
    path = repo_root / "services/backend/.local/final-resources.env"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


def _write_final_acceptance_ready(repo_root: Path) -> None:
    _write_final_acceptance(
        repo_root,
        {
            "kind": "final_acceptance_report",
            "overall_status": "passed",
            "summary": {"passed": 14, "blocked": 0, "failed": 0, "skipped": 0},
            "checks": [
                {
                    "id": "mobile_deploy_preflight",
                    "label": "iOS deploy preflight",
                    "status": "passed",
                    "classification": "passed",
                    "command": ["make", "mobile-deploy-preflight"],
                },
                {
                    "id": "mobile_xcode_build",
                    "label": "Xcode build gate",
                    "status": "passed",
                    "classification": "passed",
                    "command": ["make", "mobile-xcode-build"],
                },
            ],
        },
    )


def _write_final_acceptance(repo_root: Path, payload: dict[str, object]) -> None:
    path = repo_root / "services/backend/.local/final-acceptance-local.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_ios_device_launch_rehearsal_ready(repo_root: Path) -> None:
    _write_ios_device_launch_rehearsal(
        repo_root,
        {
            "kind": "ios_device_launch_rehearsal_report",
            "status": "ready",
            "summary": {
                "ready": 4,
                "missing": 0,
                "blocked": 0,
                "partial": 0,
                "manual": 0,
                "live": 0,
            },
            "sequence": [
                {
                    "id": "final_rehearsal_local",
                    "label": "Local final rehearsal",
                    "status": "ready",
                    "command": "make final-rehearsal-local",
                    "classification": "saved_report_set",
                }
            ],
            "operator_actions": ["iOS device launch rehearsal is ready"],
            "commands": ["make ios-device-launch-rehearsal"],
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
                "raw_media_in_report": False,
                "payment_links_in_report": False,
                "local_paths_in_report": False,
            },
        },
    )


def _write_ios_device_launch_rehearsal(
    repo_root: Path,
    payload: dict[str, object],
) -> None:
    path = repo_root / "services/backend/.local/ios-device-launch-rehearsal.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_mobile_deploy_preflight_evidence(
    repo_root: Path,
    payload: dict[str, object],
) -> None:
    path = repo_root / "services/backend/.local/mobile-deploy-preflight-evidence.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_mobile_xcode_build_evidence(
    repo_root: Path,
    payload: dict[str, object],
) -> None:
    path = repo_root / "services/backend/.local/mobile-xcode-build-evidence.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_configured_live_evidence_ready(repo_root: Path) -> None:
    local_dir = repo_root / "services/backend/.local"
    _write_json(
        local_dir / "provider-handoff.json",
        {
            "kind": "provider_handoff_report",
            "core_real_ready": True,
            "overall_real_ready": True,
            "missing_env": [],
        },
    )
    _write_json(
        local_dir / "3d-evaluation-configured.json",
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
        local_dir / "npc-evaluation-configured.json",
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
        local_dir / "final-acceptance-configured.json",
        {
            "kind": "final_acceptance_report",
            "profile": "quick",
            "provider_mode": "configured",
            "overall_status": "passed",
            "summary": {"passed": 14, "blocked": 0, "failed": 0, "skipped": 0},
        },
    )
    _write_json(
        local_dir / "final-demo-launch-configured.json",
        {
            "kind": "final_demo_launch_report",
            "mode": "configured",
            "overall_status": "ready",
            "summary": {"ready": 9, "missing": 0, "blocked": 0, "manual": 0},
        },
    )


def _write_configured_live_evidence_bundle_ready(repo_root: Path) -> None:
    _write_json(
        repo_root / "services/backend/.local/configured-live-evidence-bundle.json",
        {
            "kind": "configured_live_evidence_bundle_report",
            "status": "ready",
            "summary": {
                "evidence_files": 5,
                "evidence_ready": 5,
                "evidence_missing": 0,
                "evidence_blocked": 0,
                "commands": 10,
                "commands_ready": 10,
                "commands_run": 0,
            },
            "current_blocker": None,
            "operator_actions": [],
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


def _write_configured_live_evidence_bundle_blocked(
    repo_root: Path,
    *,
    detail: str,
) -> None:
    _write_json(
        repo_root / "services/backend/.local/configured-live-evidence-bundle.json",
        {
            "kind": "configured_live_evidence_bundle_report",
            "status": "blocked",
            "summary": {
                "evidence_files": 5,
                "evidence_ready": 4,
                "evidence_missing": 0,
                "evidence_blocked": 1,
                "commands": 10,
                "commands_ready": 9,
                "commands_run": 0,
            },
            "device_action_bundle": {
                "id": "configured_live_evidence_bundle_device_actions",
                "label": "Configured Live Evidence Bundle Device Actions",
                "source_report": "final_configured_evidence_plan",
                "status": "blocked",
                "actions": [
                    {
                        "id": "write_development_team",
                        "label": "Write development team",
                        "status": "blocked",
                        "classification": "ios_deploy_config_missing",
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
                    }
                ],
                "first_action": {
                    "id": "write_development_team",
                    "label": "Write development team",
                    "status": "blocked",
                    "classification": "ios_deploy_config_missing",
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
                "summary": {
                    "actions": 1,
                    "ready": 0,
                    "missing": 0,
                    "blocked": 1,
                    "manual": 1,
                    "partial": 0,
                    "live": 0,
                    "provider_calls": 0,
                    "global_actions": 0,
                    "xcode_or_signing": 0,
                },
                "safety": {
                    "commands_run": False,
                    "provider_calls": False,
                    "live_provider_calls": False,
                    "global_mutation": False,
                    "keychain_writes": False,
                    "writes_backend_env": False,
                    "writes_ios_deploy_config": False,
                    "xcode_or_signing": False,
                },
            },
            "current_blocker": {
                "id": "final_resource_fill_guide",
                "label": "Final resource fill guide",
                "status": "blocked",
                "classification": "configured_bundle_blocked",
                "command": "make configured-live-evidence-bundle",
                "detail": detail,
            },
            "operator_actions": [detail],
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


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
