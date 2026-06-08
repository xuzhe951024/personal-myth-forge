from __future__ import annotations

import json
from pathlib import Path

from myth_forge_api.final_resource_requirements import (
    build_final_resource_requirements_report,
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


def test_requirements_report_lists_missing_required_resources_without_leaks(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    result = build_final_resource_requirements_report(repo_root=repo_root)
    report = result.report
    report_text = json.dumps(report)

    assert result.exit_code == 2
    assert report["kind"] == "final_resource_requirements_report"
    assert report["status"] == "blocked"
    assert report["source_reports"]["final_resources_preflight"]["status"] == "missing"
    assert report["summary"]["required"] == 5
    assert report["summary"]["missing"] >= 5
    assert report["summary"]["secret"] >= 4
    assert report["summary"]["backend"] >= 4
    assert report["summary"]["ios"] >= 3
    assert report["summary"]["print"] >= 2
    assert "make final-resources-preflight" in report["validation_commands"]
    assert "make final-resource-requirements" in report["validation_commands"]
    assert report["operator_actions"][0] == "run make final-resource-init"
    assert report["first_blocker"] == {
        "id": "MESHY_API_KEY",
        "label": "Meshy API key",
        "status": "missing",
        "classification": "missing_required_value",
        "command": "provide MESHY_API_KEY in final-resources.env",
        "detail": "Backend-only secret for live Meshy 3D generation.",
        "domain": "backend_provider",
        "destination": "services/backend/.local/final-resources.env",
        "validation_command": "make final-resources-preflight",
    }
    assert report["next_action"] == {
        "id": "MESHY_API_KEY",
        "label": "Meshy API key",
        "status": "missing",
        "classification": "missing_required_value",
        "command": "provide MESHY_API_KEY in final-resources.env",
        "detail": "Backend-only secret for live Meshy 3D generation.",
        "domain": "backend_provider",
        "destination": "services/backend/.local/final-resources.env",
        "validation_command": "make final-resources-preflight",
        "source": "first_blocker",
    }
    assert str(tmp_path) not in report_text
    assert "meshy-secret-test" not in report_text
    assert "sk-openai-test" not in report_text
    assert report["safety"] == {
        "provider_secrets_in_report": False,
        "local_paths_in_report": False,
        "writes_backend_env": False,
        "writes_ios_deploy_config": False,
        "live_provider_calls": False,
        "global_mutation": False,
    }

    rows = report["requirements_by_id"]
    for key in [
        "MESHY_API_KEY",
        "OPENAI_API_KEY",
        "DEVELOPMENT_TEAM",
        "PRODUCT_BUNDLE_IDENTIFIER",
        "PMF_BACKEND_BASE_URL",
    ]:
        assert rows[key]["required"] is True
        assert rows[key]["status"] == "missing"
        assert rows[key]["classification"] == "missing_required_value"

    assert rows["MESHY_API_KEY"]["secret"] is True
    assert rows["MESHY_API_KEY"]["destination"] == (
        "services/backend/.local/final-resources.env"
    )
    assert rows["MESHY_API_KEY"]["input_source"] == (
        "services/backend/.local/final-resources.env"
    )
    assert rows["MESHY_API_KEY"]["write_destination"] == "services/backend/.env"
    assert rows["DEVELOPMENT_TEAM"]["destination"] == (
        "apps/mobile/ios/Config/Deployment.local.xcconfig"
    )
    assert rows["DEVELOPMENT_TEAM"]["input_source"] == (
        "services/backend/.local/final-resources.env"
    )
    assert rows["DEVELOPMENT_TEAM"]["write_destination"] == (
        "apps/mobile/ios/Config/Deployment.local.xcconfig"
    )
    assert rows["DEVELOPMENT_TEAM"]["apply_command"] == "make final-apply-resources"
    assert rows["DEVELOPMENT_TEAM"]["fill_action"] == (
        "fill DEVELOPMENT_TEAM in services/backend/.local/final-resources.env"
    )
    assert rows["PMF_BACKEND_BASE_URL"]["validation_command"] == (
        "make final-resources-preflight"
    )


def test_requirements_report_is_ready_for_valid_local_resources(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    resources = write_resources(repo_root, VALID_LOCAL_RESOURCES)

    result = build_final_resource_requirements_report(
        repo_root=repo_root,
        resources_file=resources,
    )
    report = result.report
    report_text = json.dumps(report)
    rows = report["requirements_by_id"]

    assert result.exit_code == 0
    assert report["status"] == "ready"
    assert report["first_blocker"] is None
    assert report["next_action"] is None
    assert report["summary"]["blocked"] == 0
    assert report["summary"]["missing"] == 0
    assert report["summary"]["ready"] >= 8
    assert rows["MESHY_API_KEY"]["status"] == "ready"
    assert rows["OPENAI_API_KEY"]["status"] == "ready"
    assert rows["PRINT_PROVIDER"]["configured"] is True
    assert rows["PRINT_PROVIDER"]["status"] == "ready"
    assert rows["TREATSTOCK_API_KEY"]["required"] is False
    assert rows["TREATSTOCK_API_KEY"]["status"] == "optional"
    assert rows["PMF_BACKEND_BASE_URL"]["status"] == "ready"
    assert rows["PMF_FINAL_LAUNCH_MODE"]["status"] == "ready"
    assert "meshy-secret-test" not in report_text
    assert "sk-openai-test" not in report_text
    assert "10.0.0.24" not in report_text
    assert str(tmp_path) not in report_text


def test_requirements_report_marks_auto_backend_url_as_apply_time_resolution(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    resources = write_resources(
        repo_root,
        VALID_LOCAL_RESOURCES.replace(
            "PMF_BACKEND_BASE_URL=http://10.0.0.24:8080",
            "PMF_BACKEND_BASE_URL=auto",
        ),
    )

    result = build_final_resource_requirements_report(
        repo_root=repo_root,
        resources_file=resources,
    )
    report = result.report
    report_text = json.dumps(report)
    row = report["requirements_by_id"]["PMF_BACKEND_BASE_URL"]

    assert result.exit_code == 0
    assert report["status"] == "ready"
    assert row["status"] == "ready"
    assert row["classification"] == "apply_time_auto_url"
    assert row["resolution_mode"] == "apply_time_auto"
    assert "write_deploy_local_config.sh" in row["apply_note"]
    assert "10.0.0.24" not in report_text


def test_requirements_report_requires_treatstock_key_when_provider_selected(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    resources = write_resources(
        repo_root,
        VALID_LOCAL_RESOURCES.replace("PRINT_PROVIDER=local", "PRINT_PROVIDER=treatstock"),
    )

    result = build_final_resource_requirements_report(
        repo_root=repo_root,
        resources_file=resources,
    )
    rows = result.report["requirements_by_id"]

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert rows["PRINT_PROVIDER"]["status"] == "ready"
    assert rows["TREATSTOCK_API_KEY"]["required"] is True
    assert rows["TREATSTOCK_API_KEY"]["status"] == "missing"
    assert rows["TREATSTOCK_API_KEY"]["classification"] == "missing_required_value"
    assert result.report["first_blocker"]["id"] == "TREATSTOCK_API_KEY"
    assert result.report["first_blocker"]["domain"] == "print_provider"
    assert result.report["first_blocker"]["command"] == (
        "provide TREATSTOCK_API_KEY in final-resources.env"
    )
    assert "provide TREATSTOCK_API_KEY in final-resources.env" in result.report[
        "operator_actions"
    ]


def test_requirements_report_marks_loopback_backend_url_blocked(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    resources = write_resources(
        repo_root,
        VALID_LOCAL_RESOURCES.replace(
            "PMF_BACKEND_BASE_URL=http://10.0.0.24:8080",
            "PMF_BACKEND_BASE_URL=http://localhost:8080",
        ),
    )

    result = build_final_resource_requirements_report(
        repo_root=repo_root,
        resources_file=resources,
    )
    rows = result.report["requirements_by_id"]

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert rows["PMF_BACKEND_BASE_URL"]["status"] == "blocked"
    assert rows["PMF_BACKEND_BASE_URL"]["classification"] == "loopback_url"
    assert "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL" in result.report[
        "operator_actions"
    ]


def write_resources(root: Path, text: str) -> Path:
    path = root / "services/backend/.local/final-resources.env"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path
