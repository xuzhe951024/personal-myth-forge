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
PRODUCT_BUNDLE_IDENTIFIER=com.zhexu.personalmythforge.dev
PMF_BACKEND_BASE_URL=http://10.0.0.24:8080
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
    assert result.report["operator_actions"] == ["run make final-resource-init"]
    assert result.report["first_blocker"]["id"] == "final_resources_file"
    assert result.report["first_blocker"]["command"] == "make final-resource-init"
    assert result.report["first_blocker"]["validation_command"] == (
        "make final-resources-preflight"
    )
    assert result.report["next_action"] == {
        **result.report["first_blocker"],
        "source": "first_blocker",
    }
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


def test_preflight_resource_actions_include_validation_commands(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    resources = write_resources(
        repo_root,
        "PRINT_PROVIDER=local\nPMF_FINAL_LAUNCH_MODE=configured\n",
    )

    result = build_final_resources_preflight_report(
        repo_root=repo_root,
        resources_file=resources,
    )
    items = {item["id"]: item for item in result.report["items"]}
    actions = result.report["operator_actions"]

    assert items["MESHY_API_KEY"]["command"] == (
        "provide MESHY_API_KEY in final-resources.env"
    )
    assert items["MESHY_API_KEY"]["detail"] == (
        "Required final resource value is missing: MESHY_API_KEY."
    )
    assert items["MESHY_API_KEY"]["validation_command"] == (
        "make final-resources-preflight"
    )
    assert items["OPENAI_API_KEY"]["command"] == (
        "provide OPENAI_API_KEY in final-resources.env"
    )
    assert (
        "provide MESHY_API_KEY in final-resources.env; "
        "rerun make final-resources-preflight"
    ) in actions
    assert (
        "provide OPENAI_API_KEY in final-resources.env; "
        "rerun make final-resources-preflight"
    ) in actions
    assert (
        "provide DEVELOPMENT_TEAM in final-resources.env; "
        "rerun make final-resources-preflight"
    ) in actions
    assert (
        "provide PRODUCT_BUNDLE_IDENTIFIER in final-resources.env; "
        "rerun make final-resources-preflight"
    ) in actions
    assert (
        "provide PMF_BACKEND_BASE_URL in final-resources.env; "
        "rerun make final-resources-preflight"
    ) in actions
    assert result.report["first_blocker"]["id"] == "MESHY_API_KEY"
    assert result.report["first_blocker"]["classification"] == "missing_required_value"
    assert result.report["first_blocker"]["command"] == (
        "provide MESHY_API_KEY in final-resources.env"
    )
    assert result.report["first_blocker"]["validation_command"] == (
        "make final-resources-preflight"
    )
    assert result.report["next_action"]["source"] == "first_blocker"
    assert not _known_bare_resource_actions(actions)
    assert not _resource_actions_with_wrong_rerun(actions)


def test_preflight_blocks_loopback_backend_url(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    resources = write_resources(
        repo_root,
        VALID_LOCAL_RESOURCES.replace(
            "PMF_BACKEND_BASE_URL=http://10.0.0.24:8080",
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
    assert items["PMF_BACKEND_BASE_URL"]["command"] == (
        "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL"
    )
    assert items["PMF_BACKEND_BASE_URL"]["detail"] == (
        "PMF_BACKEND_BASE_URL must be reachable from iPhone, not loopback."
    )
    assert items["PMF_BACKEND_BASE_URL"]["validation_command"] == (
        "make final-resources-preflight"
    )
    assert result.report["first_blocker"]["id"] == "PMF_BACKEND_BASE_URL"
    assert result.report["first_blocker"]["classification"] == "loopback_url"
    assert result.report["first_blocker"]["command"] == (
        "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL"
    )


def test_preflight_blocks_example_backend_url_placeholder(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    resources = write_resources(
        repo_root,
        VALID_LOCAL_RESOURCES.replace(
            "PMF_BACKEND_BASE_URL=http://10.0.0.24:8080",
            "PMF_BACKEND_BASE_URL=http://192.168.1.10:8080",
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
    assert items["PMF_BACKEND_BASE_URL"]["classification"] == "placeholder_value"
    assert "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL" in result.report[
        "operator_actions"
    ]


def test_preflight_blocks_example_bundle_identifier_placeholder(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    resources = write_resources(
        repo_root,
        VALID_LOCAL_RESOURCES.replace(
            "PRODUCT_BUNDLE_IDENTIFIER=com.zhexu.personalmythforge.dev",
            "PRODUCT_BUNDLE_IDENTIFIER=com.example.personalmythforge",
        ),
    )

    result = build_final_resources_preflight_report(
        repo_root=repo_root,
        resources_file=resources,
    )
    items = {item["id"]: item for item in result.report["items"]}

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert items["PRODUCT_BUNDLE_IDENTIFIER"]["status"] == "blocked"
    assert items["PRODUCT_BUNDLE_IDENTIFIER"]["classification"] == "placeholder_value"
    assert "set PRODUCT_BUNDLE_IDENTIFIER to a unique app bundle id" in result.report[
        "operator_actions"
    ]


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


def test_preflight_accepts_auto_backend_url_as_apply_time_resolution(
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

    result = build_final_resources_preflight_report(
        repo_root=repo_root,
        resources_file=resources,
    )
    report_text = json.dumps(result.report)
    items = {item["id"]: item for item in result.report["items"]}
    backend_url = items["PMF_BACKEND_BASE_URL"]

    assert result.exit_code == 0
    assert result.report["status"] == "ready"
    assert backend_url["status"] == "ready"
    assert backend_url["configured"] is True
    assert backend_url["classification"] == "apply_time_auto_url"
    assert backend_url["resolution_mode"] == "apply_time_auto"
    assert "write_deploy_local_config.sh" in backend_url["apply_note"]
    assert "10.0.0.24" not in report_text
    assert "set PMF_BACKEND_BASE_URL" not in result.report["operator_actions"]


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
    assert items["PRODUCT_BUNDLE_IDENTIFIER"]["status"] == "ready"
    assert items["PMF_BACKEND_BASE_URL"]["status"] == "ready"
    assert "command" not in items["MESHY_API_KEY"]
    assert "validation_command" not in items["MESHY_API_KEY"]
    assert "command" not in items["TREATSTOCK_API_KEY"]
    assert result.report["first_blocker"] is None
    assert result.report["next_action"] is None
    assert "meshy-secret-test" not in report_text
    assert "sk-openai-test" not in report_text
    assert "10.0.0.24" not in report_text
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


def _known_bare_resource_actions(actions: list[str]) -> list[str]:
    roots = (
        "provide MESHY_API_KEY in final-resources.env",
        "provide OPENAI_API_KEY in final-resources.env",
        "provide TREATSTOCK_API_KEY in final-resources.env",
        "provide SCULPTEO_API_KEY in final-resources.env",
        "provide DEVELOPMENT_TEAM in final-resources.env",
        "provide PRODUCT_BUNDLE_IDENTIFIER in final-resources.env",
        "provide PMF_BACKEND_BASE_URL in final-resources.env",
    )
    return [action for action in actions if action.endswith(roots)]


def _resource_actions_with_wrong_rerun(actions: list[str]) -> list[str]:
    return [
        action
        for action in actions
        if " in final-resources.env; rerun " in action
        and not action.endswith("; rerun make final-resources-preflight")
    ]
