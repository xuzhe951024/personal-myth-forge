from __future__ import annotations

import json
import subprocess
from pathlib import Path

from myth_forge_api.final_resource_repair import build_final_resource_repair_report


def test_repair_reports_missing_resources_without_writes(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    result = build_final_resource_repair_report(repo_root=repo_root)
    report_text = json.dumps(result.report)

    assert result.exit_code == 2
    assert result.report["kind"] == "final_resource_repair_report"
    assert result.report["status"] == "missing"
    assert result.report["resources_file"] == {
        "path": "services/backend/.local/final-resources.env",
        "exists": False,
    }
    assert result.report["repairs"] == []
    assert result.report["operator_actions"] == ["run make final-resource-init"]
    assert result.report["safety"] == {
        "writes_final_resources": False,
        "writes_backend_env": False,
        "writes_ios_deploy_config": False,
        "provider_calls": False,
        "global_mutation": False,
        "provider_secrets_in_report": False,
        "local_paths_in_report": False,
    }
    assert str(tmp_path) not in report_text
    assert not (repo_root / "services/backend/.local/final-resources.env").exists()


def test_repair_preview_detects_stale_placeholders_without_secret_leak(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    resources = write_resources(
        repo_root,
        "\n".join(
            [
                "# Filled final resources. Do not commit.",
                "MESHY_API_KEY=meshy-secret-test",
                "OPENAI_API_KEY=sk-openai-test",
                "DEVELOPMENT_TEAM=TEAM12345",
                "PRODUCT_BUNDLE_IDENTIFIER=com.example.personalmythforge",
                "PMF_BACKEND_BASE_URL=http://192.168.1.10:8080",
                "PMF_FINAL_LAUNCH_MODE=local",
                "",
            ]
        ),
    )
    original_text = resources.read_text(encoding="utf-8")

    result = build_final_resource_repair_report(
        repo_root=repo_root,
        resources_file=resources,
    )
    report_text = json.dumps(result.report)
    repairs = {repair["id"]: repair for repair in result.report["repairs"]}

    assert result.exit_code == 2
    assert result.report["status"] == "repairable"
    assert repairs["PRODUCT_BUNDLE_IDENTIFIER"]["classification"] == "placeholder_value"
    assert repairs["PRODUCT_BUNDLE_IDENTIFIER"]["action"] == "clear_value"
    assert repairs["PMF_BACKEND_BASE_URL"]["classification"] == "placeholder_value"
    assert repairs["PMF_BACKEND_BASE_URL"]["action"] == "clear_value"
    assert "run make final-resource-repair" in result.report["operator_actions"]
    assert result.report["safety"]["writes_final_resources"] is False
    assert resources.read_text(encoding="utf-8") == original_text
    assert "meshy-secret-test" not in report_text
    assert "sk-openai-test" not in report_text
    assert "192.168.1.10" not in report_text
    assert str(tmp_path) not in report_text


def test_repair_apply_clears_only_stale_placeholders_and_preserves_secrets(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    resources = write_resources(
        repo_root,
        "\n".join(
            [
                "# Filled final resources. Do not commit.",
                "MESHY_API_KEY=meshy-secret-test",
                "OPENAI_API_KEY=sk-openai-test",
                "PRODUCT_BUNDLE_IDENTIFIER=com.example.personalmythforge",
                "PMF_BACKEND_BASE_URL=http://192.168.1.10:8080/",
                "PMF_FINAL_LAUNCH_MODE=local",
                "",
            ]
        ),
    )

    result = build_final_resource_repair_report(
        repo_root=repo_root,
        resources_file=resources,
        apply=True,
    )
    repaired_text = resources.read_text(encoding="utf-8")
    report_text = json.dumps(result.report)

    assert result.exit_code == 0
    assert result.report["status"] == "repaired"
    assert result.report["summary"] == {"repaired": 2}
    assert result.report["operator_actions"] == [
        "rerun make final-resource-apply-preview"
    ]
    assert result.report["safety"]["writes_final_resources"] is True
    assert "MESHY_API_KEY=meshy-secret-test" in repaired_text
    assert "OPENAI_API_KEY=sk-openai-test" in repaired_text
    assert "PRODUCT_BUNDLE_IDENTIFIER=\n" in repaired_text
    assert "PMF_BACKEND_BASE_URL=\n" in repaired_text
    assert "192.168.1.10" not in repaired_text
    assert "meshy-secret-test" not in report_text
    assert "sk-openai-test" not in report_text


def test_repair_apply_refuses_tracked_final_resources_without_secret_leak(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    resources = write_resources(
        repo_root,
        "\n".join(
            [
                "MESHY_API_KEY=tracked-secret",
                "PRODUCT_BUNDLE_IDENTIFIER=com.example.personalmythforge",
                "",
            ]
        ),
    )
    subprocess.run(["git", "init"], cwd=repo_root, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "add", "services/backend/.local/final-resources.env"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )

    result = build_final_resource_repair_report(
        repo_root=repo_root,
        resources_file=resources,
        apply=True,
    )
    report_text = json.dumps(result.report)

    assert result.exit_code == 1
    assert result.report["status"] == "blocked"
    assert result.report["classification"] == "tracked_final_resources"
    assert result.report["operator_actions"] == [
        "remove services/backend/.local/final-resources.env from git tracking"
    ]
    assert result.report["safety"]["writes_final_resources"] is False
    assert "tracked-secret" not in report_text
    assert "PRODUCT_BUNDLE_IDENTIFIER=com.example.personalmythforge" in resources.read_text(
        encoding="utf-8"
    )


def write_resources(root: Path, text: str) -> Path:
    path = root / "services/backend/.local/final-resources.env"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path
