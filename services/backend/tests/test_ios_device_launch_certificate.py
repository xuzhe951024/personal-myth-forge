import json
from pathlib import Path

from myth_forge_api.config import Settings
import myth_forge_api.ios_device_launch_certificate as ios_device_launch_certificate
from myth_forge_api.ios_device_launch_certificate import (
    build_ios_device_launch_certificate_report,
)

LEGACY_PRINT_QUOTE_ACTION = (
    "after explicit Treatstock cost consent, save a sanitized "
    "services/backend/.local/print-quote-configured.json from POST "
    "/v1/print-quotes; rerun make print-fulfillment-readiness"
)
GUARDED_PRINT_QUOTE_ACTION = (
    "PMF_ALLOW_PRINT_PROVIDER_CALLS=1 make print-quote-configured; "
    "rerun make print-fulfillment-readiness"
)


def test_ios_device_launch_certificate_dedupes_print_quote_handoff_actions() -> None:
    actions = ios_device_launch_certificate._operator_actions(
        [
            {
                "id": "final_handoff_index",
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


def test_ios_device_launch_certificate_blocks_missing_inputs_without_leaks(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)

    result = build_ios_device_launch_certificate_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    report_text = json.dumps(result.report)
    gates = {gate["id"]: gate for gate in result.report["device_gates"]}

    assert result.exit_code == 2
    assert result.report["kind"] == "ios_device_launch_certificate_report"
    assert result.report["status"] == "blocked"
    assert result.report["mode"] == "local"
    assert gates["final_handoff_index"]["status"] == "blocked"
    assert gates["ios_deploy_config"]["status"] == "blocked"
    assert gates["configured_final_acceptance"]["status"] == "live"
    assert gates["configured_final_acceptance"]["requires_consent"] is True
    assert "make ios-device-launch-certificate" in result.report["commands"]
    assert "make backend-device-demo" in result.report["commands"]
    assert "make mobile-deploy-preflight" in result.report["commands"]
    assert "make final-demo-launch-local" in result.report["commands"]
    assert not any(
        "final-demo-launch --mode local" in command
        for command in result.report["commands"]
    )
    deploy_action = (
        "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig; "
        "rerun make mobile-deploy-preflight"
    )
    assert result.report["operator_actions"][0] == deploy_action
    assert result.report["first_blocker"]["command"] == deploy_action
    assert "run make final-handoff-index" not in result.report["operator_actions"][:3]
    assert not any(
        action.startswith(
            (
                "provide DEVELOPMENT_TEAM in final-resources.env",
                "provide PRODUCT_BUNDLE_IDENTIFIER in final-resources.env",
                "provide PMF_BACKEND_BASE_URL in final-resources.env",
            )
        )
        for action in result.report["operator_actions"]
    )
    assert result.report["first_blocker"] == {
        "id": "final_handoff_index",
        "label": "Final handoff index",
        "status": "blocked",
        "classification": "device_gate_blocked",
        "command": deploy_action,
        "detail": "Refreshes the unified local/configured handoff index.",
        "validation_command": "make final-handoff-index",
    }
    assert result.report["next_action"] == {
        **result.report["first_blocker"],
        "source": "first_blocker",
    }
    assert result.report["safety"]["provider_calls"] is False
    assert result.report["safety"]["commands_run"] is False
    assert result.report["safety"]["xcode_or_signing"] is False
    assert result.report["safety"]["writes_ios_deploy_config"] is False
    assert str(tmp_path) not in report_text
    assert "sk-" not in report_text


def test_ios_device_launch_certificate_exposes_device_action_bundle(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(
        tmp_path,
        local_config=(
            "DEVELOPMENT_TEAM = TEAM12345\n"
            "PRODUCT_BUNDLE_IDENTIFIER = com.zhexu.personalmythforge.dev\n"
            "PMF_BACKEND_BASE_URL = http://10.0.0.24:8080\n"
            "PMF_FINAL_LAUNCH_MODE = local\n"
        ),
    )

    result = build_ios_device_launch_certificate_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    bundle = result.report["device_action_bundle"]
    report_text = json.dumps(bundle)
    deploy_action = (
        "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig; "
        "rerun make mobile-deploy-preflight"
    )

    assert bundle["id"] == "ios_device_launch_certificate_actions"
    assert bundle["label"] == "iOS Device Launch Certificate Actions"
    assert bundle["status"] == "blocked"
    assert bundle["first_action"]["id"] == "final_handoff_index"
    assert bundle["first_action"]["command"] == deploy_action
    assert bundle["first_action"]["validation_command"] == "make final-handoff-index"
    assert bundle["first_action"]["next_action"] == {
        "id": "final_handoff_index",
        "label": "Final handoff index",
        "status": "blocked",
        "command": deploy_action,
        "detail": "Refreshes the unified local/configured handoff index.",
        "source": "device_action_bundle",
        "validation_command": "make final-handoff-index",
    }
    assert bundle["summary"]["actions"] == len(result.report["device_gates"])
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


def test_ios_device_launch_certificate_ready_with_configured_inputs(
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

    result = build_ios_device_launch_certificate_report(
        settings=settings,
        repo_root=repo_root,
    )
    report_text = json.dumps(result.report)
    gates = {gate["id"]: gate for gate in result.report["device_gates"]}

    assert result.exit_code == 0
    assert result.report["status"] == "ready"
    assert result.report["mode"] == "configured"
    assert result.report["first_blocker"] is None
    assert result.report["next_action"] is None
    assert result.report["certificate"]["development_team"]["configured"] is True
    assert result.report["certificate"]["product_bundle_identifier"]["configured"] is True
    assert result.report["certificate"]["backend_base_url"]["configured"] is True
    assert result.report["final_handoff_index"]["status"] == "ready"
    assert result.report["final_handoff_index"]["summary"]["blocked"] == 0
    assert result.report["ios_deploy_runbook"]["status"] == "partial"
    runbook_commands = [
        step["command"]
        for step in result.report["ios_deploy_runbook"]["command_sequence"]
    ]
    assert "make final-resource-apply-preview" in runbook_commands
    assert runbook_commands.index("make final-resource-apply-preview") < (
        runbook_commands.index("make final-apply-resources")
    )
    assert result.report["final_demo_launch"]["overall_status"] == "partial"
    assert result.report["final_demo_launch"]["first_blocker"] == {
        "id": "ios_deployable",
        "label": "iOS deployable",
        "status": "partial",
        "classification": "ios_rehearsal_missing",
        "command": "make ios-device-launch-rehearsal",
        "detail": "iOS deploy runbook and device launch rehearsal must both be ready.",
        "source": "final_showcase_readiness",
        "source_id": "ios_deployable",
    }
    assert gates["ios_deploy_config"]["status"] == "ready"
    assert gates["backend_device_server"]["status"] == "manual"
    assert gates["xcode_build_gate"]["status"] == "manual"
    assert gates["configured_final_acceptance"]["requires_consent"] is True
    bundle = result.report["device_action_bundle"]
    assert bundle["id"] == "ios_device_launch_certificate_actions"
    assert bundle["status"] == "ready"
    assert bundle["first_action"] is None
    assert bundle["summary"]["actions"] == len(result.report["device_gates"])
    assert bundle["summary"]["provider_calls"] == 0
    assert all(action["provider_calls"] is False for action in bundle["actions"])
    assert result.report["operator_sequence"][0]["command"] == (
        "make ios-device-launch-certificate"
    )
    assert "make backend-device-demo" in result.report["commands"]
    assert "make mobile-deploy-preflight" in result.report["commands"]
    assert "make final-demo-launch-configured" in result.report["commands"]
    assert not any(
        "final-demo-launch --mode configured" in command
        for command in result.report["commands"]
    )
    assert "sk-meshy-secret" not in report_text
    assert "sk-openai-secret" not in report_text
    assert "treatstock-secret" not in report_text
    assert "10.0.0.24" not in report_text
    assert str(tmp_path) not in report_text


def test_ios_device_launch_certificate_uses_injected_final_demo_launch_report(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo_root = _write_deploy_config(
        tmp_path,
        local_config=(
            "DEVELOPMENT_TEAM = TEAM12345\n"
            "PRODUCT_BUNDLE_IDENTIFIER = com.zhexu.personalmythforge.dev\n"
            "PMF_BACKEND_BASE_URL = http://10.0.0.24:8080\n"
            "PMF_FINAL_LAUNCH_MODE = local\n"
        ),
    )

    def fail_if_builder_recurses(**kwargs):
        raise AssertionError("final demo launch builder should not be called")

    monkeypatch.setattr(
        "myth_forge_api.ios_device_launch_certificate.build_final_demo_launch_report",
        fail_if_builder_recurses,
    )

    result = build_ios_device_launch_certificate_report(
        settings=Settings(),
        repo_root=repo_root,
        final_demo_launch_report={
            "kind": "final_demo_launch_report",
            "mode": "local",
            "overall_status": "partial",
            "first_blocker": {
                "id": "ios_deployable",
                "label": "iOS deployable",
                "status": "partial",
                "classification": "ios_rehearsal_missing",
                "command": "make ios-device-launch-rehearsal",
                "detail": "Injected final launch report.",
                "source": "final_showcase_readiness",
                "source_id": "ios_deployable",
            },
        },
    )

    assert result.report["final_demo_launch"]["overall_status"] == "partial"
    assert result.report["final_demo_launch"]["first_blocker"]["detail"] == (
        "Injected final launch report."
    )


def test_ios_device_launch_certificate_uses_final_demo_child_action_when_handoff_has_none(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo_root = _write_deploy_config(
        tmp_path,
        local_config=(
            "DEVELOPMENT_TEAM = TEAM12345\n"
            "PRODUCT_BUNDLE_IDENTIFIER = com.zhexu.personalmythforge.dev\n"
            "PMF_BACKEND_BASE_URL = http://10.0.0.24:8080\n"
            "PMF_FINAL_LAUNCH_MODE = local\n"
        ),
    )
    deploy_action = (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto "
        "make mobile-write-deploy-config-auto; "
        "rerun make mobile-deploy-preflight"
    )

    class StubFinalHandoffResult:
        report = {
            "kind": "final_handoff_index_report",
            "status": "blocked",
            "summary": {"blocked": 1},
            "lanes_by_id": {},
            "operator_actions": [
                (
                    "start backend-device-demo before device checks: "
                    "make backend-device-demo; rerun make mobile-deploy-preflight"
                )
            ],
        }

    monkeypatch.setattr(
        "myth_forge_api.ios_device_launch_certificate.build_final_handoff_index_report",
        lambda **kwargs: StubFinalHandoffResult(),
    )

    result = build_ios_device_launch_certificate_report(
        settings=Settings(),
        repo_root=repo_root,
        final_demo_launch_report={
            "kind": "final_demo_launch_report",
            "mode": "local",
            "overall_status": "partial",
            "operator_actions": [deploy_action],
        },
    )

    assert result.report["first_blocker"]["command"] == deploy_action
    assert result.report["operator_actions"][0] == deploy_action


def test_ios_device_launch_certificate_preserves_backend_device_demo_handoff(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo_root = _write_deploy_config(
        tmp_path,
        local_config=(
            "DEVELOPMENT_TEAM = TEAM12345\n"
            "PRODUCT_BUNDLE_IDENTIFIER = com.zhexu.personalmythforge.dev\n"
            "PMF_BACKEND_BASE_URL = http://10.0.0.24:8080\n"
            "PMF_FINAL_LAUNCH_MODE = local\n"
        ),
    )
    deploy_action = (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto "
        "make mobile-write-deploy-config-auto; "
        "rerun make mobile-deploy-preflight"
    )
    backend_action = (
        "start backend-device-demo before device checks: "
        "make backend-device-demo; rerun make mobile-deploy-preflight"
    )

    class StubFinalHandoffResult:
        report = {
            "kind": "final_handoff_index_report",
            "status": "blocked",
            "summary": {"blocked": 1},
            "lanes_by_id": {},
            "operator_actions": [
                deploy_action,
                (
                    "make final-resource-apply-preview; rerun make provider-handoff; "
                    "rerun make live-provider-evidence"
                ),
                (
                    "PMF_ALLOW_PRINT_PROVIDER_CALLS=1 make print-quote-configured; rerun make print-fulfillment-readiness"
                ),
                "make final-configured-preflight; rerun make configured-live-evidence-bundle",
                "make final-demo-launch-configured",
                backend_action,
            ],
        }

    monkeypatch.setattr(
        "myth_forge_api.ios_device_launch_certificate.build_final_handoff_index_report",
        lambda **kwargs: StubFinalHandoffResult(),
    )

    result = build_ios_device_launch_certificate_report(
        settings=Settings(),
        repo_root=repo_root,
    )

    actions = result.report["operator_actions"]
    assert actions[0] == deploy_action
    assert backend_action in actions
    assert "start backend-device-demo" not in actions


def test_ios_device_launch_certificate_prioritizes_backend_demo_after_deploy_handoff(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo_root = _write_deploy_config(
        tmp_path,
        local_config=(
            "DEVELOPMENT_TEAM = TEAM12345\n"
            "PRODUCT_BUNDLE_IDENTIFIER = com.zhexu.personalmythforge.dev\n"
            "PMF_BACKEND_BASE_URL = http://10.0.0.24:8080\n"
            "PMF_FINAL_LAUNCH_MODE = local\n"
        ),
    )
    deploy_action = (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto "
        "make mobile-write-deploy-config-auto; "
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
        "rerun make provider-handoff; "
        "rerun make live-provider-evidence"
    )
    print_action = (
        "PMF_ALLOW_PRINT_PROVIDER_CALLS=1 make print-quote-configured; "
        "rerun make print-fulfillment-readiness"
    )
    request_action = (
        "make final-demo-launch-local; rerun make print-fulfillment-readiness"
    )

    class StubFinalHandoffResult:
        report = {
            "kind": "final_handoff_index_report",
            "status": "blocked",
            "summary": {"blocked": 1},
            "lanes_by_id": {},
            "operator_actions": [
                deploy_action,
                provider_action,
                print_action,
                backend_action,
                backend_url_action,
            ],
        }

    monkeypatch.setattr(
        "myth_forge_api.ios_device_launch_certificate.build_final_handoff_index_report",
        lambda **kwargs: StubFinalHandoffResult(),
    )

    result = build_ios_device_launch_certificate_report(
        settings=Settings(),
        repo_root=repo_root,
    )

    actions = result.report["operator_actions"]
    assert actions[:3] == [deploy_action, backend_action, backend_url_action]
    assert actions.index(backend_action) < actions.index(provider_action)
    assert request_action not in actions
    assert print_action in actions


def test_ios_device_launch_certificate_prefers_device_action_over_provider_action_for_blocker(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo_root = _write_deploy_config(
        tmp_path,
        local_config=(
            "DEVELOPMENT_TEAM = TEAM12345\n"
            "PRODUCT_BUNDLE_IDENTIFIER = com.zhexu.personalmythforge.dev\n"
            "PMF_BACKEND_BASE_URL = http://10.0.0.24:8080\n"
            "PMF_FINAL_LAUNCH_MODE = local\n"
        ),
    )
    provider_action = (
        "PMF_ALLOW_LIVE_PROVIDER_CALLS=1 make final-acceptance-configured; "
        "rerun make live-provider-evidence"
    )
    backend_action = (
        "start backend-device-demo before device checks: "
        "make backend-device-demo; rerun make mobile-deploy-preflight"
    )

    class StubFinalHandoffResult:
        report = {
            "kind": "final_handoff_index_report",
            "status": "blocked",
            "summary": {"blocked": 1},
            "lanes_by_id": {},
            "operator_actions": [provider_action, backend_action],
        }

    monkeypatch.setattr(
        "myth_forge_api.ios_device_launch_certificate.build_final_handoff_index_report",
        lambda **kwargs: StubFinalHandoffResult(),
    )

    result = build_ios_device_launch_certificate_report(
        settings=Settings(),
        repo_root=repo_root,
        final_demo_launch_report={
            "kind": "final_demo_launch_report",
            "mode": "local",
            "overall_status": "partial",
            "operator_actions": [],
        },
    )
    first_action = result.report["device_action_bundle"]["first_action"]

    assert result.report["first_blocker"]["id"] == "final_handoff_index"
    assert result.report["first_blocker"]["command"] == backend_action
    assert result.report["next_action"]["command"] == backend_action
    assert first_action["id"] == "final_handoff_index"
    assert first_action["command"] == backend_action
    assert provider_action in result.report["operator_actions"]


def test_ios_device_launch_certificate_prioritizes_deploy_handoff_before_backend_url_child_action() -> None:
    deploy_action = (
        "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig; "
        "rerun make mobile-deploy-preflight"
    )
    backend_url_action = (
        "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL; "
        "rerun make mobile-deploy-preflight"
    )

    actions = ios_device_launch_certificate._prioritize_final_handoff_child_actions(
        [
            backend_url_action,
            deploy_action,
        ]
    )

    assert actions == [deploy_action, backend_url_action]


def test_ios_device_launch_certificate_promotes_print_request_before_provider_quote(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(
        tmp_path,
        local_config=(
            "DEVELOPMENT_TEAM = TEAM12345\n"
            "PRODUCT_BUNDLE_IDENTIFIER = com.zhexu.personalmythforge.dev\n"
            "PMF_BACKEND_BASE_URL = http://10.0.0.24:8080\n"
            "PMF_FINAL_LAUNCH_MODE = local\n"
        ),
    )
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
    deploy_action = (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto "
        "make mobile-write-deploy-config-auto; "
        "rerun make mobile-deploy-preflight"
    )
    _write_json(
        repo_root / "services/backend/.local/final-demo-launch-local.json",
        {
            "kind": "final_demo_launch_report",
            "mode": "local",
            "overall_status": "partial",
            "next_action": {
                "command": (
                    "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto "
                    "make mobile-write-deploy-config-auto"
                ),
                "validation_command": "make mobile-deploy-preflight",
            },
            "operator_actions": [
                deploy_action,
                "make provider-handoff; rerun make live-provider-evidence",
                "make final-demo-launch-local; rerun make print-fulfillment-readiness",
                (
                    "PMF_ALLOW_PRINT_PROVIDER_CALLS=1 make print-quote-configured; rerun make print-fulfillment-readiness"
                ),
            ],
        },
    )

    result = build_ios_device_launch_certificate_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    actions = result.report["operator_actions"]
    provider_action = (
        "make final-resource-fill-guide; rerun make final-resource-apply-preview; "
        "rerun make provider-handoff; rerun make live-provider-evidence"
    )
    print_action = (
        "PMF_ALLOW_PRINT_PROVIDER_CALLS=1 make print-quote-configured; rerun make print-fulfillment-readiness"
    )
    request_action = (
        "make final-demo-launch-local; rerun make print-fulfillment-readiness"
    )

    assert result.report["first_blocker"]["command"] == deploy_action
    assert actions[0] == deploy_action
    assert "run make final-handoff-index" not in actions[:3]
    assert provider_action in actions
    assert request_action in actions
    assert print_action not in actions
    assert actions.index(provider_action) < actions.index(request_action)


def test_ios_device_launch_certificate_promotes_guarded_print_after_request_ready(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(
        tmp_path,
        local_config=(
            "DEVELOPMENT_TEAM = TEAM12345\n"
            "PRODUCT_BUNDLE_IDENTIFIER = com.zhexu.personalmythforge.dev\n"
            "PMF_BACKEND_BASE_URL = http://10.0.0.24:8080\n"
            "PMF_FINAL_LAUNCH_MODE = local\n"
        ),
    )
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
    _write_configured_print_quote_request(repo_root)
    deploy_action = (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto "
        "make mobile-write-deploy-config-auto; "
        "rerun make mobile-deploy-preflight"
    )
    _write_json(
        repo_root / "services/backend/.local/final-demo-launch-local.json",
        {
            "kind": "final_demo_launch_report",
            "mode": "local",
            "overall_status": "partial",
            "next_action": {
                "command": (
                    "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto "
                    "make mobile-write-deploy-config-auto"
                ),
                "validation_command": "make mobile-deploy-preflight",
            },
            "operator_actions": [
                deploy_action,
                "make provider-handoff; rerun make live-provider-evidence",
                (
                    "PMF_ALLOW_PRINT_PROVIDER_CALLS=1 make print-quote-configured; rerun make print-fulfillment-readiness"
                ),
            ],
        },
    )

    result = build_ios_device_launch_certificate_report(
        settings=Settings(),
        repo_root=repo_root,
    )
    actions = result.report["operator_actions"]
    provider_action = (
        "make final-resource-fill-guide; rerun make final-resource-apply-preview; "
        "rerun make provider-handoff; rerun make live-provider-evidence"
    )
    print_action = (
        "PMF_ALLOW_PRINT_PROVIDER_CALLS=1 make print-quote-configured; rerun make print-fulfillment-readiness"
    )
    request_action = (
        "PRINT_SOURCE_ASSET_URI=auto PRINT_CANDIDATE_URI=auto "
        "make print-quote-request-configured; "
        "rerun make print-fulfillment-readiness"
    )

    assert result.report["first_blocker"]["command"] == deploy_action
    assert actions[0] == deploy_action
    assert provider_action in actions
    assert print_action in actions
    assert request_action not in actions
    assert actions.index(provider_action) < actions.index(print_action)


def test_ios_device_launch_certificate_cli_writes_report_and_makefile_target(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    output_path = tmp_path / "ios-device-launch-certificate.json"

    from myth_forge_api.cli import main

    exit_code = main(
        [
            "ios-device-launch-certificate",
            "--repo-root",
            str(repo_root),
            "--output",
            str(output_path),
        ]
    )

    assert exit_code == 2
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["kind"] == "ios_device_launch_certificate_report"
    assert payload["status"] == "blocked"

    repo_root = Path(__file__).resolve().parents[3]
    makefile = (repo_root / "Makefile").read_text(encoding="utf-8")
    wrapper = (
        repo_root / "services/backend/scripts/write_ios_device_launch_certificate.sh"
    ).read_text(encoding="utf-8")
    assert "ios-device-launch-certificate:" in makefile
    assert "services/backend/scripts/write_ios_device_launch_certificate.sh" in makefile
    assert "myth_forge_api.cli ios-device-launch-certificate" in wrapper
    assert ".local/ios-device-launch-certificate.json" in wrapper


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


def _write_configured_print_quote_request(repo_root: Path) -> None:
    _write_json(
        repo_root / "services/backend/.local/print-quote-request-configured.json",
        {
            "print_candidate": {
                "kind": "print_asset",
                "source_asset_uri": "https://assets.example/relic.glb",
                "provider": "local_stub",
                "format": "3mf",
                "uri": "https://assets.example/relic.3mf",
                "requires_user_approval": True,
                "approval_reason": "Review before configured quote.",
                "printability_notes": ["Watertight local handoff candidate."],
            },
            "quantity": 1,
            "material": "standard_resin",
            "finish": "matte",
            "ship_to_country": "US",
        },
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


def _write_final_demo_launch(repo_root: Path) -> None:
    report = {
        "kind": "final_demo_launch_report",
        "mode": "local",
        "overall_status": "partial",
        "summary": {"ready": 8, "missing": 0, "blocked": 0, "manual": 1, "optional": 1},
    }
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
            }
        ],
    }
    _write_json(repo_root / "services/backend/.local/visual-regression-local.json", report)


def _write_json(path: Path, report: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report), encoding="utf-8")
