import json
from pathlib import Path

from myth_forge_api.config import Settings
from myth_forge_api.resource_handoff import build_resource_handoff_report


def test_resource_handoff_reports_missing_final_core_resources(tmp_path: Path) -> None:
    repo_root = _write_deploy_config(tmp_path)

    report = build_resource_handoff_report(settings=Settings(), repo_root=repo_root)

    backend = {item["id"]: item for item in report["backend"]["items"]}
    ios = {item["id"]: item for item in report["ios"]["items"]}
    assert report["kind"] == "resource_handoff_report"
    assert report["overall_status"] == "blocked"
    assert backend["THREE_D_PROVIDER"]["status"] == "manual"
    assert backend["MESHY_API_KEY"]["status"] == "missing"
    assert backend["NPC_PROVIDER"]["status"] == "manual"
    assert backend["OPENAI_API_KEY"]["status"] == "missing"
    assert backend["PRINT_PROVIDER"]["status"] == "ready"
    assert backend["TREATSTOCK_API_KEY"]["status"] == "optional"
    assert backend["MYTH_SESSION_STORAGE_DIR"]["status"] == "ready"
    assert ios["DEVELOPMENT_TEAM"]["status"] == "missing"
    assert ios["PMF_BACKEND_BASE_URL"]["status"] == "blocked"
    assert "provide MESHY_API_KEY" in " ".join(report["operator_actions"])
    assert "make backend-write-provider-env" in report["commands"]
    assert "make backend-device-demo" in report["commands"]
    assert any("resource-template-acceptance" in command for command in report["commands"])
    assert "make mobile-deploy-preflight" in report["commands"]
    assert any("--allow-live-provider-calls" in command for command in report["commands"])


def test_resource_handoff_marks_core_resources_ready_without_secret_leak(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(
        tmp_path,
        local_config=(
            "DEVELOPMENT_TEAM = TEAM12345\n"
            "PRODUCT_BUNDLE_IDENTIFIER = com.example.personalmythforge\n"
            "PMF_BACKEND_BASE_URL = http://192.168.1.10:8080\n"
        ),
    )
    settings = Settings(
        three_d_provider="meshy",
        meshy_api_key="sk-meshy-secret",
        npc_provider="openai",
        openai_api_key="sk-openai-secret",
        print_provider="treatstock",
        treatstock_api_key="treatstock-secret",
    )

    report = build_resource_handoff_report(settings=settings, repo_root=repo_root)
    report_text = json.dumps(report)
    backend = {item["id"]: item for item in report["backend"]["items"]}
    ios = {item["id"]: item for item in report["ios"]["items"]}

    assert backend["THREE_D_PROVIDER"]["status"] == "ready"
    assert backend["MESHY_API_KEY"]["status"] == "ready"
    assert backend["NPC_PROVIDER"]["status"] == "ready"
    assert backend["OPENAI_API_KEY"]["status"] == "ready"
    assert backend["PRINT_PROVIDER"]["status"] == "ready"
    assert backend["TREATSTOCK_API_KEY"]["configured"] is True
    assert backend["TREATSTOCK_API_KEY"]["status"] == "ready"
    assert "Treatstock live quote handoff is implemented" in " ".join(
        backend["TREATSTOCK_API_KEY"]["notes"]
    )
    assert ios["DEVELOPMENT_TEAM"]["status"] == "ready"
    assert ios["PMF_BACKEND_BASE_URL"]["status"] == "ready"
    assert report["safety"]["provider_secrets_in_report"] is False
    assert "sk-meshy-secret" not in report_text
    assert "sk-openai-secret" not in report_text
    assert "treatstock-secret" not in report_text
    assert str(tmp_path) not in report_text


def test_resource_handoff_blocks_treatstock_when_selected_without_key(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    settings = Settings(print_provider="treatstock")

    report = build_resource_handoff_report(settings=settings, repo_root=repo_root)
    backend = {item["id"]: item for item in report["backend"]["items"]}

    assert backend["PRINT_PROVIDER"]["status"] == "missing"
    assert backend["TREATSTOCK_API_KEY"]["status"] == "missing"
    assert "provide TREATSTOCK_API_KEY" in " ".join(report["operator_actions"])


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
