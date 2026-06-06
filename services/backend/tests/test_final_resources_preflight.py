from __future__ import annotations

import json
from pathlib import Path

from myth_forge_api.final_resources_preflight import (
    build_final_resources_preflight_report,
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
PRODUCT_BUNDLE_IDENTIFIER=com.example.personalmythforge
PMF_BACKEND_BASE_URL=http://192.168.1.10:8080
CAPTURE_STORAGE_DIR=
MYTH_SESSION_STORAGE_DIR=
"""


def test_preflight_reports_missing_default_file_without_local_path_leak(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    result = build_final_resources_preflight_report(repo_root=repo_root)
    report_text = json.dumps(result.report)

    assert result.exit_code == 2
    assert result.report["kind"] == "final_resources_preflight_report"
    assert result.report["status"] == "missing"
    assert result.report["resources_file"] == {
        "path": "services/backend/.local/final-resources.env",
        "exists": False,
    }
    assert result.report["summary"]["missing"] >= 1
    assert str(tmp_path) not in report_text
    assert result.report["safety"] == {
        "provider_secrets_in_report": False,
        "local_paths_in_report": False,
        "writes_backend_env": False,
        "writes_ios_deploy_config": False,
        "live_provider_calls": False,
        "global_mutation": False,
    }
    assert not backend_env_path(repo_root).exists()
    assert not ios_local_config_path(repo_root).exists()


def test_preflight_blocks_unknown_keys_without_secret_value_leak(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    resources = write_resources(
        repo_root,
        VALID_LOCAL_RESOURCES + "UNKNOWN_SECRET_KEY=do-not-print-this\n",
    )

    result = build_final_resources_preflight_report(
        repo_root=repo_root,
        resources_file=resources,
    )
    report_text = json.dumps(result.report)

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert result.report["unknown_keys"] == ["UNKNOWN_SECRET_KEY"]
    assert "do-not-print-this" not in report_text
    assert "meshy-secret-test" not in report_text
    assert "sk-openai-test" not in report_text
    assert not backend_env_path(repo_root).exists()
    assert not ios_local_config_path(repo_root).exists()


def test_preflight_blocks_loopback_backend_url(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    resources = write_resources(
        repo_root,
        VALID_LOCAL_RESOURCES.replace(
            "PMF_BACKEND_BASE_URL=http://192.168.1.10:8080",
            "PMF_BACKEND_BASE_URL=http://127.0.0.1:8080",
        ),
    )

    result = build_final_resources_preflight_report(
        repo_root=repo_root,
        resources_file=resources,
    )
    items = {item["id"]: item for item in result.report["items"]}

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert items["PMF_BACKEND_BASE_URL"]["status"] == "blocked"
    assert items["PMF_BACKEND_BASE_URL"]["classification"] == "loopback_url"


def test_preflight_requires_treatstock_key_when_treatstock_selected(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    resources = write_resources(
        repo_root,
        VALID_LOCAL_RESOURCES.replace("PRINT_PROVIDER=local", "PRINT_PROVIDER=treatstock"),
    )

    result = build_final_resources_preflight_report(
        repo_root=repo_root,
        resources_file=resources,
    )
    items = {item["id"]: item for item in result.report["items"]}

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert items["PRINT_PROVIDER"]["status"] == "ready"
    assert items["TREATSTOCK_API_KEY"]["status"] == "missing"
    assert items["TREATSTOCK_API_KEY"]["required"] is True


def test_preflight_accepts_configured_final_launch_mode(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    resources = write_resources(
        repo_root,
        VALID_LOCAL_RESOURCES + "PMF_FINAL_LAUNCH_MODE=configured\n",
    )

    result = build_final_resources_preflight_report(
        repo_root=repo_root,
        resources_file=resources,
    )
    items = {item["id"]: item for item in result.report["items"]}

    assert result.exit_code == 0
    assert result.report["status"] == "ready"
    assert result.report["unknown_keys"] == []
    assert "PMF_FINAL_LAUNCH_MODE" in items
    assert items["PMF_FINAL_LAUNCH_MODE"]["status"] == "ready"
    assert items["PMF_FINAL_LAUNCH_MODE"]["required"] is False
    assert items["PMF_FINAL_LAUNCH_MODE"]["configured"] is True
    assert items["PMF_FINAL_LAUNCH_MODE"]["normalized_value"] == "configured"


def test_preflight_blocks_unsupported_final_launch_mode(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    resources = write_resources(
        repo_root,
        VALID_LOCAL_RESOURCES + "PMF_FINAL_LAUNCH_MODE=live\n",
    )

    result = build_final_resources_preflight_report(
        repo_root=repo_root,
        resources_file=resources,
    )
    items = {item["id"]: item for item in result.report["items"]}

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert result.report["unknown_keys"] == []
    assert "PMF_FINAL_LAUNCH_MODE" in items
    assert items["PMF_FINAL_LAUNCH_MODE"]["status"] == "blocked"
    assert items["PMF_FINAL_LAUNCH_MODE"]["classification"] == "unsupported_value"
    assert "set PMF_FINAL_LAUNCH_MODE to local or configured" in result.report[
        "operator_actions"
    ]


def test_preflight_marks_valid_local_print_resources_ready_and_redacted(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    resources = write_resources(repo_root, VALID_LOCAL_RESOURCES)

    result = build_final_resources_preflight_report(
        repo_root=repo_root,
        resources_file=resources,
    )
    report_text = json.dumps(result.report)
    items = {item["id"]: item for item in result.report["items"]}

    assert result.exit_code == 0
    assert result.report["status"] == "ready"
    assert result.report["summary"]["blocked"] == 0
    assert result.report["summary"]["missing"] == 0
    assert result.report["unknown_keys"] == []
    assert items["MESHY_API_KEY"]["status"] == "ready"
    assert items["OPENAI_API_KEY"]["status"] == "ready"
    assert items["PRINT_PROVIDER"]["normalized_value"] == "local"
    assert items["TREATSTOCK_API_KEY"]["status"] == "optional"
    assert items["DEVELOPMENT_TEAM"]["status"] == "ready"
    assert items["PMF_BACKEND_BASE_URL"]["status"] == "ready"
    assert "meshy-secret-test" not in report_text
    assert "sk-openai-test" not in report_text
    assert "192.168.1.10" not in report_text
    assert not backend_env_path(repo_root).exists()
    assert not ios_local_config_path(repo_root).exists()


def write_resources(root: Path, text: str) -> Path:
    path = root / "services/backend/.local/final-resources.env"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def backend_env_path(root: Path) -> Path:
    return root / "services/backend/.env"


def ios_local_config_path(root: Path) -> Path:
    return root / "apps/mobile/ios/Config/Deployment.local.xcconfig"
