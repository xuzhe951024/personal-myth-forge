import json
from pathlib import Path

from myth_forge_api.resource_template_acceptance import run_resource_template_acceptance


BACKEND_TEMPLATE = """# Backend
THREE_D_PROVIDER=local
MESHY_API_BASE_URL=https://api.meshy.ai
MESHY_POLL_INTERVAL_SECONDS=5
MESHY_MAX_WAIT_SECONDS=600
MESHY_API_KEY=
NPC_PROVIDER=local
OPENAI_NPC_MODEL=gpt-4.1-mini
OPENAI_API_BASE_URL=
OPENAI_API_KEY=
PRINT_PROVIDER=local
TREATSTOCK_API_KEY=
TREATSTOCK_API_BASE_URL=https://www.treatstock.com
SCULPTEO_API_KEY=
CAPTURE_STORAGE_DIR=
MYTH_SESSION_STORAGE_DIR=
"""

IOS_TEMPLATE = """// Copy this file to Deployment.local.xcconfig for local deployment.
DEVELOPMENT_TEAM = YOUR_TEAM_ID
PRODUCT_BUNDLE_IDENTIFIER = com.example.personalmythforge
PMF_BACKEND_BASE_URL = http://192.168.1.10:8080
PMF_FINAL_LAUNCH_MODE = local
"""

GITIGNORE_TEMPLATE = """.env
services/backend/.local/
apps/mobile/ios/Config/Deployment.local.xcconfig
"""

BACKEND_WRITER_TEMPLATE = """#!/usr/bin/env sh
set -eu
MESHY_API_KEY="${MESHY_API_KEY:-}"
OPENAI_API_KEY="${OPENAI_API_KEY:-}"
printf '%s\\n' "THREE_D_PROVIDER=meshy"
printf '%s\\n' "NPC_PROVIDER=openai"
printf '%s\\n' "PRINT_PROVIDER=local"
printf '%s\\n' "TREATSTOCK_API_BASE_URL=https://www.treatstock.com"
printf '%s\\n' "MESHY_API_KEY: configured (redacted)"
printf '%s\\n' "OPENAI_API_KEY: configured (redacted)"
printf '%s\\n' "services/backend/.env must stay untracked."
"""

FINAL_RESOURCE_TEMPLATE = """# Copy to services/backend/.local/final-resources.env.
MESHY_API_KEY=
OPENAI_API_KEY=
PRINT_PROVIDER=local
TREATSTOCK_API_KEY=
TREATSTOCK_API_BASE_URL=https://www.treatstock.com
SCULPTEO_API_KEY=
DEVELOPMENT_TEAM=
PRODUCT_BUNDLE_IDENTIFIER=com.example.personalmythforge
PMF_BACKEND_BASE_URL=http://192.168.1.10:8080
PMF_FINAL_LAUNCH_MODE=local
"""

FINAL_RESOURCE_APPLY_TEMPLATE = """#!/usr/bin/env sh
set -eu
printf '%s\\n' "MESHY_API_KEY: configured (redacted)"
printf '%s\\n' "OPENAI_API_KEY: configured (redacted)"
printf '%s\\n' "TREATSTOCK_API_KEY: configured (redacted)"
sh services/backend/scripts/write_backend_env.sh
sh apps/mobile/ios/scripts/write_deploy_local_config.sh
"""

FINAL_ACCEPTANCE_LOCAL_SCRIPT = """#!/usr/bin/env sh
set -eu
set +e
uv run python -m myth_forge_api.cli final-acceptance --output .local/final-acceptance-local.json
status=$?
set -e
if [ "$status" -eq 0 ] || [ "$status" -eq 2 ]; then
  printf '%s\\n' "accepted final acceptance exit code $status"
  exit 0
fi
exit "$status"
"""

IOS_DEPLOY_RUNBOOK_LOCAL_SCRIPT = """#!/usr/bin/env sh
set -eu
set +e
uv run python -m myth_forge_api.cli ios-deploy-runbook --output .local/ios-deploy-runbook-local.json
status=$?
set -e
if [ "$status" -eq 0 ] || [ "$status" -eq 2 ]; then
  printf '%s\\n' "accepted iOS deploy runbook exit code $status"
  exit 0
fi
exit "$status"
"""

IOS_DEVICE_LAUNCH_REHEARSAL_SCRIPT = """#!/usr/bin/env sh
set -eu
run_report_command() { :; }
if [ "$status" -eq 0 ] || [ "$status" -eq 2 ]; then
  printf '%s\\n' "accepted $label exit code $status"
fi
make final-rehearsal-local
uv run python -m myth_forge_api.cli final-configured-preflight --output .local/final-configured-preflight.json
uv run python -m myth_forge_api.cli final-handoff-index --output .local/final-handoff-index.json
uv run python -m myth_forge_api.cli ios-device-launch-certificate --output .local/ios-device-launch-certificate.json
uv run python -m myth_forge_api.cli ios-device-launch-rehearsal --output .local/ios-device-launch-rehearsal.json
run_report_command "final launch rehearsal sync" sh -c '
  uv run python -m myth_forge_api.cli final-demo-launch --mode local --output .local/final-demo-launch-local.json
'
printf '%s\\n' "services/backend/.local/ios-device-launch-rehearsal.json"
printf '%s\\n' "services/backend/.local/final-demo-launch-local.json"
"""

MAKEFILE_TEMPLATE = """.PHONY: backend-write-provider-env
backend-write-provider-env:
\t@services/backend/scripts/write_backend_env.sh
.PHONY: final-acceptance-local final-demo-launch final-rehearsal-local
final-acceptance-local:
\t@services/backend/scripts/write_final_acceptance_local.sh
final-demo-launch:
\tcd services/backend && uv run python -m myth_forge_api.cli final-demo-launch --mode local --repo-root ../.. --output .local/final-demo-launch-local.json
.PHONY: final-apply-resources
final-apply-resources:
\t@services/backend/scripts/apply_final_resources.sh
.PHONY: final-resources-preflight
final-resources-preflight:
\tcd services/backend && uv run python -m myth_forge_api.cli final-resources-preflight --repo-root ../..
.PHONY: final-configured-preflight
final-configured-preflight:
\tcd services/backend && uv run python -m myth_forge_api.cli final-configured-preflight --repo-root ../.. --output .local/final-configured-preflight.json
.PHONY: final-handoff-index
final-handoff-index:
\tcd services/backend && uv run python -m myth_forge_api.cli final-handoff-index --repo-root ../.. --output .local/final-handoff-index.json
.PHONY: ios-device-launch-certificate
ios-device-launch-certificate:
\tcd services/backend && uv run python -m myth_forge_api.cli ios-device-launch-certificate --repo-root ../.. --output .local/ios-device-launch-certificate.json
.PHONY: ios-device-launch-rehearsal
ios-device-launch-rehearsal:
\t@services/backend/scripts/write_ios_device_launch_rehearsal.sh
.PHONY: ios-deploy-runbook ios-deploy-runbook-local
ios-deploy-runbook:
\tcd services/backend && uv run python -m myth_forge_api.cli ios-deploy-runbook --mode local --repo-root ../.. --output .local/ios-deploy-runbook-local.json
ios-deploy-runbook-local:
\t@services/backend/scripts/write_ios_deploy_runbook_local.sh
final-rehearsal-local: backend-evaluate-local final-acceptance-local final-demo-launch ios-deploy-runbook-local
"""

CLI_TEMPLATE = """from myth_forge_api.final_demo_launch import build_final_demo_launch_report
from myth_forge_api.final_configured_preflight import build_final_configured_preflight_report
from myth_forge_api.final_handoff_index import build_final_handoff_index_report
from myth_forge_api.final_resources_preflight import build_final_resources_preflight_report
from myth_forge_api.ios_device_launch_certificate import build_ios_device_launch_certificate_report
from myth_forge_api.ios_device_launch_rehearsal import build_ios_device_launch_rehearsal_report
subcommands.add_parser("final-configured-preflight")
subcommands.add_parser("final-handoff-index")
subcommands.add_parser("ios-device-launch-certificate")
subcommands.add_parser("ios-device-launch-rehearsal")
subcommands.add_parser("final-demo-launch")
subcommands.add_parser("final-resources-preflight")
"""

FINAL_DEMO_LAUNCH_TEMPLATE = """from myth_forge_api.resource_handoff import build_resource_handoff_report
from myth_forge_api.final_resources_preflight import build_final_resources_preflight_report
def build_final_demo_launch_report():
    build_final_resources_preflight_report()
    return build_resource_handoff_report()
"""

FINAL_RESOURCES_PREFLIGHT_TEMPLATE = """def build_final_resources_preflight_report():
    return {"safety": {"live_provider_calls": False, "global_mutation": False}}
"""

FINAL_CONFIGURED_PREFLIGHT_TEMPLATE = """from myth_forge_api.final_demo_launch import build_final_demo_launch_report
from myth_forge_api.final_resources_preflight import build_final_resources_preflight_report
from myth_forge_api.ios_deploy_runbook import build_ios_deploy_runbook_report
from myth_forge_api.provider_handoff import build_provider_handoff_report
from myth_forge_api.resource_handoff import build_resource_handoff_report

def build_final_configured_preflight_report():
    build_final_resources_preflight_report()
    build_provider_handoff_report()
    build_resource_handoff_report()
    build_final_demo_launch_report()
    build_ios_deploy_runbook_report()
    return {"safety": {
        "provider_calls": False,
        "writes_backend_env": False,
        "writes_ios_deploy_config": False,
        "xcode_or_signing": False,
        "keychain_writes": False,
    }}
"""

FINAL_HANDOFF_INDEX_TEMPLATE = """from myth_forge_api.final_configured_preflight import build_final_configured_preflight_report

def build_final_handoff_index_report():
    _freshness_report()
    _freshness_summary([])
    build_final_configured_preflight_report()
    return {
        "kind": "final_handoff_index_report",
        "source_reports": [],
        "freshness_summary": {"fresh": 0, "stale": 0, "unknown": 0},
        "operator_sequence": [],
        "lanes_by_id": {},
        "blocker": {"classification": "stale_report", "checked_against": "git_head"},
        "safety": {
            "commands_run": False,
            "provider_calls": False,
            "writes_backend_env": False,
            "writes_ios_deploy_config": False,
            "xcode_or_signing": False,
            "keychain_writes": False,
        },
    }

def _freshness_report():
    return {"classification": "stale_report", "checked_against": "git_head"}

def _freshness_summary(source_reports):
    return {"fresh": 0, "stale": 0, "unknown": 0}
"""

IOS_DEVICE_LAUNCH_CERTIFICATE_TEMPLATE = """from myth_forge_api.final_demo_launch import build_final_demo_launch_report
from myth_forge_api.final_handoff_index import build_final_handoff_index_report
from myth_forge_api.ios_deploy_runbook import build_ios_deploy_runbook_report

def build_ios_device_launch_certificate_report():
    build_final_handoff_index_report()
    build_ios_deploy_runbook_report()
    build_final_demo_launch_report()
    return {
        "kind": "ios_device_launch_certificate_report",
        "device_gates": [],
        "operator_sequence": [],
        "safety": {
            "commands_run": False,
            "provider_calls": False,
            "writes_backend_env": False,
            "writes_ios_deploy_config": False,
            "xcode_or_signing": False,
            "keychain_writes": False,
        },
    }
"""

IOS_DEVICE_LAUNCH_REHEARSAL_TEMPLATE = """LOCAL_REPORT_SOURCES = []
REHEARSAL_REPORT_SOURCES = ["final_configured_preflight", "final_handoff_index", "ios_device_launch_certificate"]

def build_ios_device_launch_rehearsal_report():
    return {
        "kind": "ios_device_launch_rehearsal_report",
        "sequence": [],
        "freshness_summary": {"fresh": 0, "stale": 0, "unknown": 0},
        "freshness_status": "fresh",
        "freshness_classification": "fresh_report",
        "operator_actions": [],
        "commands": ["make ios-device-launch-rehearsal"],
        "safety": {
            "report_builder_commands_run": False,
            "make_wrapper_runs_commands": True,
            "writes_ignored_reports": True,
            "provider_calls": False,
            "writes_backend_env": False,
            "writes_ios_deploy_config": False,
            "xcode_or_signing": False,
            "keychain_writes": False,
        },
    }
"""

IOS_DEVICE_LAUNCH_REHEARSAL_READINESS_TEMPLATE = """
def build_ios_device_launch_rehearsal_readiness_report():
    return {
        "kind": "ios_device_launch_rehearsal_readiness_report",
        "freshness": _freshness_report(),
        "sequence": [{"freshness_summary": {"fresh": 0, "stale": 0, "unknown": 0}, "freshness_status": "stale", "freshness_classification": "stale_report"}],
        "blockers": [{"id": "ios_device_launch_rehearsal_freshness", "classification": "stale_report"}],
        "operator_actions": ["rerun make ios-device-launch-rehearsal"],
    }

def _freshness_report():
    return {"classification": "stale_report"}
"""


def test_resource_template_acceptance_passes_complete_templates(tmp_path: Path) -> None:
    repo_root = _write_repo(tmp_path)

    result = run_resource_template_acceptance(repo_root=repo_root)

    assert result.exit_code == 0
    assert result.report["kind"] == "resource_template_acceptance_report"
    assert result.report["status"] == "succeeded"
    assert result.report["summary"] == {"passed": 16, "failed": 0}
    assert result.report["backend_template"]["missing_keys"] == []
    assert result.report["ios_template"]["missing_keys"] == []
    assert "OPENAI_API_KEY" in result.report["backend_template"]["required_keys"]
    assert "PMF_BACKEND_BASE_URL" in result.report["ios_template"]["required_keys"]
    assert "PMF_FINAL_LAUNCH_MODE" in result.report["ios_template"]["required_keys"]
    assert "PMF_FINAL_LAUNCH_MODE" in result.report["final_resource_apply"][
        "required_keys"
    ]

    ignored = {
        item["path"]: item
        for item in result.report["gitignore"]["local_destinations"]
    }
    assert ignored[".env"]["ignored"] is True
    assert ignored["services/backend/.env"]["ignored"] is True
    assert ignored["services/backend/.env"]["matched_by"] == ".env"
    assert ignored["services/backend/.local/"]["ignored"] is True
    assert (
        ignored["apps/mobile/ios/Config/Deployment.local.xcconfig"]["ignored"] is True
    )
    assert result.report["safety"] == {
        "provider_secrets_in_templates": False,
        "provider_secrets_in_report": False,
        "raw_media_in_templates": False,
        "raw_media_in_report": False,
        "local_paths_in_templates": False,
        "local_paths_in_report": False,
        "payment_links_in_templates": False,
        "payment_links_in_report": False,
        "provider_calls": False,
        "global_mutation": False,
    }
    assert result.report["backend_writer"]["path"] == (
        "services/backend/scripts/write_backend_env.sh"
    )
    assert result.report["backend_writer"]["make_target"] == "backend-write-provider-env"
    assert result.report["backend_writer"]["checks"]["exists"] is True
    assert result.report["backend_writer"]["checks"]["make_target"] is True
    assert result.report["backend_writer"]["checks"]["required_keys"] is True
    assert result.report["backend_writer"]["checks"]["redaction"] is True
    assert result.report["backend_writer"]["checks"]["tracked_env_guard"] is True
    assert result.report["backend_writer"]["checks"]["no_banned_commands"] is True
    assert result.report["final_demo_launch"]["path"] == (
        "services/backend/src/myth_forge_api/final_demo_launch.py"
    )
    assert result.report["final_demo_launch"]["make_target"] == "final-demo-launch"
    assert result.report["final_demo_launch"]["checks"]["module_exists"] is True
    assert result.report["final_demo_launch"]["checks"]["cli_command"] is True
    assert result.report["final_demo_launch"]["checks"]["make_target"] is True
    assert result.report["final_demo_launch"]["checks"]["local_output_path"] is True
    assert result.report["final_demo_launch"]["checks"]["uses_resource_handoff"] is True
    assert result.report["final_demo_launch"]["checks"]["no_banned_commands"] is True
    assert result.report["final_rehearsal_local"]["make_target"] == (
        "final-rehearsal-local"
    )
    assert result.report["final_rehearsal_local"]["checks"] == {
        "final_acceptance_script_exists": True,
        "ios_deploy_runbook_script_exists": True,
        "final_acceptance_accepts_blocked_report": True,
        "ios_deploy_runbook_accepts_blocked_report": True,
        "make_targets": True,
        "local_output_paths": True,
        "no_banned_commands": True,
    }
    assert result.report["final_resource_apply"]["path"] == (
        "services/backend/scripts/apply_final_resources.sh"
    )
    assert result.report["final_resource_apply"]["template_path"] == (
        "services/backend/final-resources.env.example"
    )
    assert result.report["final_resource_apply"]["make_target"] == "final-apply-resources"
    assert result.report["final_resource_apply"]["checks"]["template_exists"] is True
    assert result.report["final_resource_apply"]["checks"]["template_keys"] is True
    assert result.report["final_resource_apply"]["checks"]["script_exists"] is True
    assert result.report["final_resource_apply"]["checks"]["make_target"] is True
    assert result.report["final_resource_apply"]["checks"]["uses_existing_writers"] is True
    assert result.report["final_resource_apply"]["checks"]["uses_ios_writer"] is True
    assert result.report["final_resource_apply"]["checks"]["redaction"] is True
    assert result.report["final_resource_apply"]["checks"]["no_banned_commands"] is True
    assert result.report["final_resources_preflight"]["path"] == (
        "services/backend/src/myth_forge_api/final_resources_preflight.py"
    )
    assert result.report["final_resources_preflight"]["make_target"] == (
        "final-resources-preflight"
    )
    assert result.report["final_resources_preflight"]["checks"]["module_exists"] is True
    assert result.report["final_resources_preflight"]["checks"]["cli_command"] is True
    assert result.report["final_resources_preflight"]["checks"]["make_target"] is True
    assert (
        result.report["final_resources_preflight"]["checks"]["launch_integration"] is True
    )
    assert result.report["final_resources_preflight"]["checks"]["no_banned_commands"] is True
    assert result.report["final_configured_preflight"]["path"] == (
        "services/backend/src/myth_forge_api/final_configured_preflight.py"
    )
    assert result.report["final_configured_preflight"]["make_target"] == (
        "final-configured-preflight"
    )
    assert result.report["final_configured_preflight"]["output_path"] == (
        ".local/final-configured-preflight.json"
    )
    assert result.report["final_configured_preflight"]["checks"] == {
        "module_exists": True,
        "cli_command": True,
        "make_target": True,
        "output_path": True,
        "composes_handoff_reports": True,
        "safety_contract": True,
        "no_banned_commands": True,
    }
    assert result.report["final_handoff_index"]["path"] == (
        "services/backend/src/myth_forge_api/final_handoff_index.py"
    )
    assert result.report["final_handoff_index"]["make_target"] == (
        "final-handoff-index"
    )
    assert result.report["final_handoff_index"]["output_path"] == (
        ".local/final-handoff-index.json"
    )
    assert result.report["final_handoff_index"]["checks"] == {
        "module_exists": True,
        "cli_command": True,
        "make_target": True,
        "output_path": True,
        "composes_handoff_reports": True,
        "source_freshness": True,
        "safety_contract": True,
        "no_banned_commands": True,
    }
    assert result.report["ios_device_launch_certificate"]["path"] == (
        "services/backend/src/myth_forge_api/ios_device_launch_certificate.py"
    )
    assert result.report["ios_device_launch_certificate"]["make_target"] == (
        "ios-device-launch-certificate"
    )
    assert result.report["ios_device_launch_certificate"]["output_path"] == (
        ".local/ios-device-launch-certificate.json"
    )
    assert result.report["ios_device_launch_certificate"]["checks"] == {
        "module_exists": True,
        "cli_command": True,
        "make_target": True,
        "output_path": True,
        "composes_device_reports": True,
        "safety_contract": True,
        "no_banned_commands": True,
    }
    assert result.report["ios_device_launch_rehearsal"]["path"] == (
        "services/backend/src/myth_forge_api/ios_device_launch_rehearsal.py"
    )
    assert result.report["ios_device_launch_rehearsal"]["readiness_path"] == (
        "services/backend/src/myth_forge_api/ios_device_launch_rehearsal_readiness.py"
    )
    assert result.report["ios_device_launch_rehearsal"]["script_path"] == (
        "services/backend/scripts/write_ios_device_launch_rehearsal.sh"
    )
    assert result.report["ios_device_launch_rehearsal"]["make_target"] == (
        "ios-device-launch-rehearsal"
    )
    assert result.report["ios_device_launch_rehearsal"]["output_path"] == (
        ".local/ios-device-launch-rehearsal.json"
    )
    assert result.report["ios_device_launch_rehearsal"]["checks"] == {
        "module_exists": True,
        "readiness_exists": True,
        "script_exists": True,
        "cli_command": True,
        "make_target": True,
        "output_path": True,
        "composes_rehearsal_reports": True,
        "safety_contract": True,
        "script_accepts_blocked_reports": True,
        "syncs_final_launch_after_rehearsal": True,
        "readiness_freshness": True,
        "source_freshness_propagation": True,
        "no_banned_commands": True,
    }


def test_resource_template_acceptance_fails_missing_backend_key(tmp_path: Path) -> None:
    repo_root = _write_repo(
        tmp_path,
        backend_template=BACKEND_TEMPLATE.replace("OPENAI_API_KEY=\n", ""),
    )

    result = run_resource_template_acceptance(repo_root=repo_root)

    assert result.exit_code == 1
    assert result.report["status"] == "failed"
    assert result.report["backend_template"]["missing_keys"] == ["OPENAI_API_KEY"]
    assert result.report["ios_template"]["missing_keys"] == []
    assert result.report["summary"]["failed"] == 1


def test_resource_template_acceptance_fails_missing_ios_key(tmp_path: Path) -> None:
    repo_root = _write_repo(
        tmp_path,
        ios_template=IOS_TEMPLATE.replace(
            "PMF_BACKEND_BASE_URL = http://192.168.1.10:8080\n",
            "",
        ),
    )

    result = run_resource_template_acceptance(repo_root=repo_root)

    assert result.exit_code == 1
    assert result.report["status"] == "failed"
    assert result.report["backend_template"]["missing_keys"] == []
    assert result.report["ios_template"]["missing_keys"] == ["PMF_BACKEND_BASE_URL"]


def test_resource_template_acceptance_fails_unsafe_templates_without_leaking_values(
    tmp_path: Path,
) -> None:
    repo_root = _write_repo(
        tmp_path,
        backend_template=BACKEND_TEMPLATE.replace(
            "OPENAI_API_KEY=\n",
            (
                "OPENAI_API_KEY=sk-openai-secret\n"
                "TREATSTOCK_API_KEY=treatstock-secret-value\n"
            ),
        ),
        ios_template=IOS_TEMPLATE.replace(
            "http://192.168.1.10:8080",
            "file:///Users/zhexu/private/backend",
        ),
    )

    result = run_resource_template_acceptance(repo_root=repo_root)
    report_text = json.dumps(result.report)

    assert result.exit_code == 1
    assert result.report["status"] == "failed"
    assert result.report["safety"]["provider_secrets_in_templates"] is True
    assert result.report["safety"]["local_paths_in_templates"] is True
    assert "sk-openai-secret" not in report_text
    assert "treatstock-secret-value" not in report_text
    assert "/Users/zhexu/private" not in report_text


def test_resource_template_acceptance_current_repo_passes() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    result = run_resource_template_acceptance(repo_root=repo_root)

    assert result.exit_code == 0
    assert result.report["status"] == "succeeded"


def _write_repo(
    tmp_path: Path,
    *,
    backend_template: str = BACKEND_TEMPLATE,
    ios_template: str = IOS_TEMPLATE,
    gitignore_template: str = GITIGNORE_TEMPLATE,
    backend_writer: str = BACKEND_WRITER_TEMPLATE,
    final_resource_template: str = FINAL_RESOURCE_TEMPLATE,
    final_resource_apply: str = FINAL_RESOURCE_APPLY_TEMPLATE,
    final_acceptance_local_script: str = FINAL_ACCEPTANCE_LOCAL_SCRIPT,
    ios_deploy_runbook_local_script: str = IOS_DEPLOY_RUNBOOK_LOCAL_SCRIPT,
    ios_device_launch_rehearsal_script: str = IOS_DEVICE_LAUNCH_REHEARSAL_SCRIPT,
    final_resources_preflight: str = FINAL_RESOURCES_PREFLIGHT_TEMPLATE,
    final_configured_preflight: str = FINAL_CONFIGURED_PREFLIGHT_TEMPLATE,
    final_handoff_index: str = FINAL_HANDOFF_INDEX_TEMPLATE,
    ios_device_launch_certificate: str = IOS_DEVICE_LAUNCH_CERTIFICATE_TEMPLATE,
    ios_device_launch_rehearsal: str = IOS_DEVICE_LAUNCH_REHEARSAL_TEMPLATE,
    ios_device_launch_rehearsal_readiness: str = (
        IOS_DEVICE_LAUNCH_REHEARSAL_READINESS_TEMPLATE
    ),
    makefile: str = MAKEFILE_TEMPLATE,
) -> Path:
    repo_root = tmp_path / "repo"
    (repo_root / "apps/mobile/ios/Config").mkdir(parents=True)
    (repo_root / "services/backend/scripts").mkdir(parents=True)
    (repo_root / ".env.example").write_text(backend_template, encoding="utf-8")
    (repo_root / "apps/mobile/ios/Config/Deployment.local.xcconfig.example").write_text(
        ios_template,
        encoding="utf-8",
    )
    (repo_root / ".gitignore").write_text(gitignore_template, encoding="utf-8")
    (repo_root / "services/backend/scripts/write_backend_env.sh").write_text(
        backend_writer,
        encoding="utf-8",
    )
    (repo_root / "services/backend/scripts/apply_final_resources.sh").write_text(
        final_resource_apply,
        encoding="utf-8",
    )
    (repo_root / "services/backend/scripts/write_final_acceptance_local.sh").write_text(
        final_acceptance_local_script,
        encoding="utf-8",
    )
    (
        repo_root / "services/backend/scripts/write_ios_deploy_runbook_local.sh"
    ).write_text(
        ios_deploy_runbook_local_script,
        encoding="utf-8",
    )
    (
        repo_root / "services/backend/scripts/write_ios_device_launch_rehearsal.sh"
    ).write_text(
        ios_device_launch_rehearsal_script,
        encoding="utf-8",
    )
    (repo_root / "services/backend/final-resources.env.example").write_text(
        final_resource_template,
        encoding="utf-8",
    )
    (repo_root / "services/backend/src/myth_forge_api").mkdir(parents=True)
    (repo_root / "services/backend/src/myth_forge_api/cli.py").write_text(
        CLI_TEMPLATE,
        encoding="utf-8",
    )
    (
        repo_root / "services/backend/src/myth_forge_api/final_demo_launch.py"
    ).write_text(
        FINAL_DEMO_LAUNCH_TEMPLATE,
        encoding="utf-8",
    )
    (
        repo_root / "services/backend/src/myth_forge_api/final_resources_preflight.py"
    ).write_text(
        final_resources_preflight,
        encoding="utf-8",
    )
    (
        repo_root / "services/backend/src/myth_forge_api/final_configured_preflight.py"
    ).write_text(
        final_configured_preflight,
        encoding="utf-8",
    )
    (repo_root / "services/backend/src/myth_forge_api/final_handoff_index.py").write_text(
        final_handoff_index,
        encoding="utf-8",
    )
    (
        repo_root / "services/backend/src/myth_forge_api/ios_device_launch_certificate.py"
    ).write_text(
        ios_device_launch_certificate,
        encoding="utf-8",
    )
    (
        repo_root / "services/backend/src/myth_forge_api/ios_device_launch_rehearsal.py"
    ).write_text(
        ios_device_launch_rehearsal,
        encoding="utf-8",
    )
    (
        repo_root
        / "services/backend/src/myth_forge_api/ios_device_launch_rehearsal_readiness.py"
    ).write_text(
        ios_device_launch_rehearsal_readiness,
        encoding="utf-8",
    )
    (repo_root / "Makefile").write_text(makefile, encoding="utf-8")
    return repo_root
