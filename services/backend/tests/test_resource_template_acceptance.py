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
SCULPTEO_API_KEY=
CAPTURE_STORAGE_DIR=
MYTH_SESSION_STORAGE_DIR=
"""

IOS_TEMPLATE = """// Copy this file to Deployment.local.xcconfig for local deployment.
DEVELOPMENT_TEAM = YOUR_TEAM_ID
PRODUCT_BUNDLE_IDENTIFIER = com.example.personalmythforge
PMF_BACKEND_BASE_URL = http://192.168.1.10:8080
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
printf '%s\\n' "MESHY_API_KEY: configured (redacted)"
printf '%s\\n' "OPENAI_API_KEY: configured (redacted)"
printf '%s\\n' "services/backend/.env must stay untracked."
"""

MAKEFILE_TEMPLATE = """.PHONY: backend-write-provider-env
backend-write-provider-env:
\t@services/backend/scripts/write_backend_env.sh
"""


def test_resource_template_acceptance_passes_complete_templates(tmp_path: Path) -> None:
    repo_root = _write_repo(tmp_path)

    result = run_resource_template_acceptance(repo_root=repo_root)

    assert result.exit_code == 0
    assert result.report["kind"] == "resource_template_acceptance_report"
    assert result.report["status"] == "succeeded"
    assert result.report["summary"] == {"passed": 8, "failed": 0}
    assert result.report["backend_template"]["missing_keys"] == []
    assert result.report["ios_template"]["missing_keys"] == []
    assert "OPENAI_API_KEY" in result.report["backend_template"]["required_keys"]
    assert "PMF_BACKEND_BASE_URL" in result.report["ios_template"]["required_keys"]

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
    (repo_root / "Makefile").write_text(makefile, encoding="utf-8")
    return repo_root
