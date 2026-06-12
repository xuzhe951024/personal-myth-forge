from __future__ import annotations

import json
from pathlib import Path

from myth_forge_api.final_resource_fill_guide import (
    build_final_resource_fill_guide_report,
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


def test_fill_guide_lists_required_inputs_without_secret_or_path_leak(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    result = build_final_resource_fill_guide_report(repo_root=repo_root)
    report = result.report
    markdown = report["markdown"]
    report_text = json.dumps(report)
    required_ids = [item["id"] for item in report["required_inputs"]]
    first_blocker = report["first_blocker"]

    assert result.exit_code == 2
    assert report["kind"] == "final_resource_fill_guide_report"
    assert report["status"] == "blocked"
    assert first_blocker == {
        "id": "MESHY_API_KEY",
        "label": "Meshy API key",
        "status": "missing",
        "classification": "missing_required_value",
        "command": "fill MESHY_API_KEY in services/backend/.local/final-resources.env",
        "detail": "Backend-only secret for live Meshy 3D generation.",
        "domain": "backend_provider",
        "input_source": "services/backend/.local/final-resources.env",
        "write_destination": "services/backend/.env",
        "validation_command": "make final-resources-preflight",
    }
    assert report["next_action"] == {
        **first_blocker,
        "source": "first_blocker",
    }
    assert required_ids == [
        "MESHY_API_KEY",
        "OPENAI_API_KEY",
        "DEVELOPMENT_TEAM",
        "PRODUCT_BUNDLE_IDENTIFIER",
        "PMF_BACKEND_BASE_URL",
    ]
    assert "services/backend/.local/final-resources.env" in markdown
    assert "apps/mobile/ios/Config/Deployment.local.xcconfig" in markdown
    assert "<secret: fill locally>" in markdown
    assert "make final-resource-requirements" in report["commands"]
    assert "make final-resource-apply-preview" in report["commands"]
    assert "make final-apply-resources" in report["commands"]
    assert "make final-local-report-refresh" in report["commands"]
    assert str(tmp_path) not in report_text
    assert "/Users/" not in report_text
    assert "sk-" not in report_text
    assert "meshy-secret" not in report_text
    assert report["safety"] == {
        "provider_secrets_in_report": False,
        "local_paths_in_report": False,
        "writes_backend_env": False,
        "writes_ios_deploy_config": False,
        "writes_final_resources": False,
        "live_provider_calls": False,
        "global_mutation": False,
    }


def test_fill_guide_ready_resources_do_not_leak_secret_or_backend_url(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    resources = write_resources(repo_root, VALID_LOCAL_RESOURCES)

    result = build_final_resource_fill_guide_report(
        repo_root=repo_root,
        resources_file=resources,
    )
    report = result.report
    markdown = report["markdown"]
    report_text = json.dumps(report)
    configured_ids = [item["id"] for item in report["configured_inputs"]]

    assert result.exit_code == 0
    assert report["status"] == "ready"
    assert report["first_blocker"] is None
    assert report["next_action"] is None
    assert report["required_inputs"] == []
    assert "MESHY_API_KEY" in configured_ids
    assert "MESHY_API_KEY" in markdown
    assert "services/backend/.env" in markdown
    assert "meshy-secret-test" not in report_text
    assert "sk-openai-test" not in report_text
    assert "10.0.0.24" not in report_text
    assert str(tmp_path) not in report_text


def write_resources(root: Path, text: str) -> Path:
    path = root / "services/backend/.local/final-resources.env"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path
