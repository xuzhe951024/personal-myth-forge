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
        "PMF_ALLOW_LIVE_PROVIDER_CALLS=1 make backend-evaluate-3d-configured"
    )
    assert live_actions["run_configured_npc_evaluation"]["operator_action"] == (
        "PMF_ALLOW_LIVE_PROVIDER_CALLS=1 make backend-evaluate-npc-configured"
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
    assert "make final-resources-preflight" in operator_actions
    assert "make print-fulfillment-readiness" in operator_actions
    assert "make ios-device-launch-rehearsal" in operator_actions
    assert "make final-resource-apply-preview" in operator_actions
    assert "make final-apply-resources" not in operator_actions
    assert not any(action.startswith("run make ") for action in operator_actions)
    assert (
        "provide MESHY_API_KEY in final-resources.env; rerun "
        "make final-resources-preflight"
    ) in operator_actions
    assert (
        "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig; rerun "
        "make mobile-deploy-preflight"
    ) in operator_actions
    assert "provide MESHY_API_KEY" not in operator_actions
    assert "provide DEVELOPMENT_TEAM" not in operator_actions
    assert "make ios-device-launch-rehearsal" in actions
    assert "make configured-live-evidence-bundle" in actions
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
    assert bundle["source_report"] == "ios_device_evidence_bundle"
    assert bundle["status"] == "blocked"
    assert bundle["first_action"]["id"] == "backend_device_server"
    assert bundle["first_action"]["command"] == "make backend-device-demo"
    assert bundle["first_action"]["next_action"]["command"] == "make backend-device-demo"
    assert bundle["summary"]["actions"] == 4
    assert bundle["summary"]["missing"] >= 1
    assert bundle["summary"]["provider_calls"] == 0
    assert bundle["summary"]["global_actions"] == 1
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
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID make mobile-write-deploy-config-auto"
    )
    assert configured_bundle["first_action"]["validation_command"] == (
        "make mobile-deploy-preflight"
    )
    assert result.report["device_action_bundle"]["source_report"] == (
        "ios_device_evidence_bundle"
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
                        "DEVELOPMENT_TEAM=YOUR_TEAM_ID "
                        "make mobile-write-deploy-config-auto"
                    ),
                    "validation_command": "make mobile-deploy-preflight",
                },
                "actions": [
                    {
                        "id": "development_team",
                        "status": "blocked",
                        "command": (
                            "DEVELOPMENT_TEAM=YOUR_TEAM_ID "
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
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID make mobile-write-deploy-config-auto"
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

    assert (
        "make final-resource-apply-preview; rerun make live-provider-evidence"
        in operator_actions
    )
    assert (
        "after explicit Treatstock cost consent, save a sanitized "
        "services/backend/.local/print-quote-configured.json from POST "
        "/v1/print-quotes; rerun make print-fulfillment-readiness"
    ) in operator_actions
    assert (
        "approve live provider cost before make live-provider-evidence"
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
    provider_action = (
        "provide MESHY_API_KEY in final-resources.env; "
        "rerun make final-resources-preflight"
    )

    assert result.report["next_action"]["command"] == device_action
    assert actions[0] == device_action
    assert provider_action in actions
    assert actions.index(device_action) < actions.index(provider_action)


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
    assert sections["live_provider_consent"]["status"] in {"ready", "live"}
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
                            "DEVELOPMENT_TEAM=YOUR_TEAM_ID "
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
                        "DEVELOPMENT_TEAM=YOUR_TEAM_ID "
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
