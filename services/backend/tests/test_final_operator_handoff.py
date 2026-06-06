import json
from pathlib import Path

from myth_forge_api.final_operator_handoff import build_final_operator_handoff_report


STEP_ORDER = [
    "final_resources_preflight",
    "apply_final_resources",
    "backend_device_server",
    "local_final_acceptance",
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
    assert report["summary"]["missing"] == 3
    assert report["summary"]["blocked"] == 0
    assert report["summary"]["optional"] == 1
    assert report["next_actions"][:2] == [
        (
            "copy services/backend/final-resources.env.example to "
            "services/backend/.local/final-resources.env"
        ),
        "run local final acceptance and write services/backend/.local/final-acceptance-local.json",
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
            "run local final acceptance and write services/backend/.local/final-acceptance-local.json"
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
            (
                "cd services/backend && uv run python -m myth_forge_api.cli "
                "final-acceptance --profile quick --provider-mode local --repo-root ../.."
            ),
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
            (
                "cd services/backend && uv run python -m myth_forge_api.cli "
                "final-acceptance --profile quick --provider-mode local --repo-root ../.."
            ),
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
