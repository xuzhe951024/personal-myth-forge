import json
from pathlib import Path

from myth_forge_api.ios_backend_handoff_acceptance import (
    run_ios_backend_handoff_acceptance,
)


def test_ios_backend_handoff_acceptance_passes_complete_fixture(tmp_path: Path) -> None:
    write_complete_fixture(tmp_path)

    result = run_ios_backend_handoff_acceptance(repo_root=tmp_path)

    assert result.exit_code == 0
    assert result.report["kind"] == "ios_backend_handoff_acceptance_report"
    assert result.report["status"] == "succeeded"
    assert result.report["summary"] == {"passed": 9, "failed": 0}
    assert [item["id"] for item in result.report["requirements"]] == [
        "backend_device_make_target",
        "backend_device_host",
        "backend_device_port",
        "mobile_auto_config_make_target",
        "mobile_auto_backend_url_env",
        "local_config_example",
        "deploy_preflight_loopback_guard",
        "ios_plist_backend_url",
        "ios_runtime_backend_url",
    ]
    assert all(item["status"] == "passed" for item in result.report["requirements"])
    assert result.report["safety"] == {
        "global_mutation": False,
        "starts_server": False,
        "runs_xcode": False,
        "runs_swiftpm": False,
        "provider_calls": False,
        "absolute_paths_in_report": False,
    }


def test_ios_backend_handoff_acceptance_fails_missing_make_target_without_paths(
    tmp_path: Path,
) -> None:
    write_complete_fixture(tmp_path)
    (tmp_path / "Makefile").write_text("backend-dev:\n\tuvicorn app\n", encoding="utf-8")

    result = run_ios_backend_handoff_acceptance(repo_root=tmp_path)
    report_text = json.dumps(result.report)
    requirements = {item["id"]: item for item in result.report["requirements"]}

    assert result.exit_code == 1
    assert result.report["status"] == "failed"
    assert result.report["summary"] == {"passed": 4, "failed": 5}
    assert requirements["backend_device_make_target"]["status"] == "failed"
    assert requirements["backend_device_host"]["status"] == "failed"
    assert requirements["backend_device_port"]["status"] == "failed"
    assert requirements["mobile_auto_config_make_target"]["status"] == "failed"
    assert requirements["mobile_auto_backend_url_env"]["status"] == "failed"
    assert str(tmp_path) not in report_text
    assert "/Users/" not in report_text
    assert "sk-" not in report_text
    assert "data:image" not in report_text


def write_complete_fixture(root: Path) -> None:
    files = {
        "Makefile": (
            ".PHONY: backend-device-demo\n"
            "backend-device-demo:\n"
            "\tcd services/backend && uv run uvicorn myth_forge_api.main:app "
            "--host 0.0.0.0 --port 8080\n"
            ".PHONY: mobile-write-deploy-config-auto\n"
            "mobile-write-deploy-config-auto:\n"
            "\tPMF_BACKEND_BASE_URL=auto apps/mobile/ios/scripts/"
            "write_deploy_local_config.sh\n"
        ),
        "apps/mobile/ios/Config/Deployment.local.xcconfig.example": (
            "PMF_BACKEND_BASE_URL = http://192.168.1.10:8080\n"
        ),
        "apps/mobile/ios/scripts/deploy_preflight.sh": (
            "http://127.0.0.1:*|http://localhost:*"
        ),
        "apps/mobile/ios/App/Info.plist": "$(PMF_BACKEND_BASE_URL)",
        "apps/mobile/ios/App/AppConfiguration.swift": "PMFBackendBaseURL",
    }
    for relative_path, contents in files.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding="utf-8")
