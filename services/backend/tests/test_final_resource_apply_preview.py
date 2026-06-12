from __future__ import annotations

import json
from pathlib import Path

from myth_forge_api.final_resource_apply_preview import (
    build_final_resource_apply_preview_report,
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


def test_apply_preview_reports_missing_resources_without_writing_outputs(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    result = build_final_resource_apply_preview_report(repo_root=repo_root)
    report_text = json.dumps(result.report)
    targets = result.report["write_targets_by_id"]
    first_blocker = result.report["first_blocker"]

    assert result.exit_code == 2
    assert result.report["kind"] == "final_resource_apply_preview_report"
    assert result.report["status"] == "missing"
    assert first_blocker == {
        "id": "backend_env",
        "label": "Backend env",
        "status": "missing",
        "classification": "missing_required_value",
        "command": "make final-resource-init",
        "detail": "blocked by MESHY_API_KEY, OPENAI_API_KEY",
        "destination": "services/backend/.env",
        "writer": "services/backend/scripts/write_backend_env.sh",
        "blocked_by": ["MESHY_API_KEY", "OPENAI_API_KEY"],
        "validation_command": "make final-resources-preflight",
    }
    assert result.report["next_action"] == {
        **first_blocker,
        "source": "first_blocker",
    }
    assert result.report["summary"]["missing"] >= 5
    assert result.report["summary"]["write_targets"] == 2
    assert targets["backend_env"]["status"] == "missing"
    assert targets["ios_deploy_config"]["status"] == "missing"
    assert "make final-resource-apply-preview" in result.report["commands"]
    assert "make final-apply-resources" in result.report["commands"]
    assert result.report["operator_actions"][0] == "run make final-resource-init"
    assert result.report["safety"] == {
        "provider_secrets_in_report": False,
        "local_paths_in_report": False,
        "writes_backend_env": False,
        "writes_ios_deploy_config": False,
        "runs_shell_writers": False,
        "live_provider_calls": False,
        "global_mutation": False,
        "xcode_or_signing": False,
    }
    assert str(tmp_path) not in report_text
    assert not backend_env_path(repo_root).exists()
    assert not ios_local_config_path(repo_root).exists()


def test_apply_preview_blocks_loopback_backend_url_without_writes(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    resources = write_resources(
        repo_root,
        VALID_LOCAL_RESOURCES.replace(
            "PMF_BACKEND_BASE_URL=http://10.0.0.24:8080",
            "PMF_BACKEND_BASE_URL=http://127.0.0.1:8080",
        ),
    )

    result = build_final_resource_apply_preview_report(
        repo_root=repo_root,
        resources_file=resources,
    )
    slots = {
        slot["id"]: slot
        for target in result.report["write_targets"]
        for slot in target["slots"]
    }

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert slots["PMF_BACKEND_BASE_URL"]["status"] == "blocked"
    assert slots["PMF_BACKEND_BASE_URL"]["classification"] == "loopback_url"
    assert "PMF_BACKEND_BASE_URL" in result.report["write_targets_by_id"][
        "ios_deploy_config"
    ]["blocked_by"]
    assert result.report["first_blocker"]["command"] == (
        "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL"
    )
    assert result.report["next_action"]["command"] == (
        "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL"
    )
    assert result.report["first_blocker"]["command"] != "make final-apply-resources"
    assert not backend_env_path(repo_root).exists()
    assert not ios_local_config_path(repo_root).exists()


def test_apply_preview_blocker_command_uses_value_fill_before_writer(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    resources = write_resources(
        repo_root,
        VALID_LOCAL_RESOURCES.replace(
            "MESHY_API_KEY=meshy-secret-test",
            "MESHY_API_KEY=",
        ),
    )

    result = build_final_resource_apply_preview_report(
        repo_root=repo_root,
        resources_file=resources,
    )

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert result.report["first_blocker"]["command"] == (
        "provide MESHY_API_KEY in final-resources.env"
    )
    assert result.report["next_action"]["command"] == (
        "provide MESHY_API_KEY in final-resources.env"
    )
    assert result.report["first_blocker"]["validation_command"] == (
        "make final-resources-preflight"
    )
    assert result.report["first_blocker"]["writer"] == (
        "services/backend/scripts/write_backend_env.sh"
    )
    assert result.report["first_blocker"]["blocked_by"] == ["MESHY_API_KEY"]
    assert result.report["first_blocker"]["command"] != "make final-apply-resources"
    assert not backend_env_path(repo_root).exists()
    assert not ios_local_config_path(repo_root).exists()


def test_apply_preview_ios_actions_include_mobile_preflight_validation(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    resources = write_resources(
        repo_root,
        VALID_LOCAL_RESOURCES.replace(
            "PMF_BACKEND_BASE_URL=http://10.0.0.24:8080",
            "PMF_BACKEND_BASE_URL=http://127.0.0.1:8080",
        ),
    )

    result = build_final_resource_apply_preview_report(
        repo_root=repo_root,
        resources_file=resources,
    )
    actions = result.report["operator_actions"]

    assert (
        "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL; "
        "rerun make mobile-deploy-preflight"
    ) in actions
    assert not any(
        action.endswith("set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL")
        for action in actions
    )


def test_apply_preview_blocks_example_backend_url_placeholder_without_writes(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    resources = write_resources(
        repo_root,
        VALID_LOCAL_RESOURCES.replace(
            "PMF_BACKEND_BASE_URL=http://10.0.0.24:8080",
            "PMF_BACKEND_BASE_URL=http://192.168.1.10:8080",
        ),
    )

    result = build_final_resource_apply_preview_report(
        repo_root=repo_root,
        resources_file=resources,
    )
    ios_target = result.report["write_targets_by_id"]["ios_deploy_config"]
    slots = {slot["id"]: slot for slot in ios_target["slots"]}

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert slots["PMF_BACKEND_BASE_URL"]["status"] == "blocked"
    assert slots["PMF_BACKEND_BASE_URL"]["classification"] == "placeholder_value"
    assert "PMF_BACKEND_BASE_URL" in ios_target["blocked_by"]
    assert not backend_env_path(repo_root).exists()
    assert not ios_local_config_path(repo_root).exists()


def test_apply_preview_blocks_example_bundle_identifier_placeholder_without_writes(
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

    result = build_final_resource_apply_preview_report(
        repo_root=repo_root,
        resources_file=resources,
    )
    ios_target = result.report["write_targets_by_id"]["ios_deploy_config"]
    slots = {slot["id"]: slot for slot in ios_target["slots"]}

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert slots["PRODUCT_BUNDLE_IDENTIFIER"]["status"] == "blocked"
    assert slots["PRODUCT_BUNDLE_IDENTIFIER"]["classification"] == "placeholder_value"
    assert "PRODUCT_BUNDLE_IDENTIFIER" in ios_target["blocked_by"]
    assert not backend_env_path(repo_root).exists()
    assert not ios_local_config_path(repo_root).exists()


def test_apply_preview_routes_repairable_placeholders_to_repair_workflow(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    resources = write_resources(
        repo_root,
        VALID_LOCAL_RESOURCES.replace(
            "PRODUCT_BUNDLE_IDENTIFIER=com.zhexu.personalmythforge.dev",
            "PRODUCT_BUNDLE_IDENTIFIER=com.example.personalmythforge",
        ).replace(
            "PMF_BACKEND_BASE_URL=http://10.0.0.24:8080",
            "PMF_BACKEND_BASE_URL=http://192.168.1.10:8080",
        ),
    )

    result = build_final_resource_apply_preview_report(
        repo_root=repo_root,
        resources_file=resources,
    )
    report = result.report
    report_text = json.dumps(report)
    commands = report["commands"]

    assert result.exit_code == 2
    assert report["status"] == "blocked"
    assert report["source_reports"]["final_resource_repair"]["status"] == "repairable"
    assert "make final-resource-repair-preview" in commands
    assert "make final-resource-repair" in commands
    assert commands.index("make final-resource-repair-preview") < commands.index(
        "make final-resource-apply-preview"
    )
    assert commands.index("make final-resource-repair") < commands.index(
        "make final-resource-apply-preview"
    )
    assert report["operator_actions"][0] == "run make final-resource-repair"
    assert "meshy-secret-test" not in report_text
    assert "sk-openai-test" not in report_text
    assert "192.168.1.10" not in report_text
    assert str(tmp_path) not in report_text
    assert not backend_env_path(repo_root).exists()
    assert not ios_local_config_path(repo_root).exists()


def test_apply_preview_does_not_route_missing_values_to_repair_workflow(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    resources = write_resources(
        repo_root,
        VALID_LOCAL_RESOURCES.replace(
            "PRODUCT_BUNDLE_IDENTIFIER=com.zhexu.personalmythforge.dev",
            "PRODUCT_BUNDLE_IDENTIFIER=",
        ).replace(
            "PMF_BACKEND_BASE_URL=http://10.0.0.24:8080",
            "PMF_BACKEND_BASE_URL=",
        ),
    )

    result = build_final_resource_apply_preview_report(
        repo_root=repo_root,
        resources_file=resources,
    )
    report = result.report

    assert result.exit_code == 2
    assert report["status"] == "blocked"
    assert report["source_reports"]["final_resource_repair"]["status"] == "ready"
    assert "make final-resource-repair-preview" not in report["commands"]
    assert "make final-resource-repair" not in report["commands"]
    assert "run make final-resource-repair" not in report["operator_actions"]


def test_apply_preview_requires_treatstock_key_when_provider_selected(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    resources = write_resources(
        repo_root,
        VALID_LOCAL_RESOURCES.replace("PRINT_PROVIDER=local", "PRINT_PROVIDER=treatstock"),
    )

    result = build_final_resource_apply_preview_report(
        repo_root=repo_root,
        resources_file=resources,
    )
    backend = result.report["write_targets_by_id"]["backend_env"]
    slots = {slot["id"]: slot for slot in backend["slots"]}

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert backend["status"] == "blocked"
    assert slots["TREATSTOCK_API_KEY"]["required"] is True
    assert slots["TREATSTOCK_API_KEY"]["status"] == "missing"
    assert "TREATSTOCK_API_KEY" in backend["blocked_by"]


def test_apply_preview_resource_actions_include_validation_commands(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    resources = write_resources(
        repo_root,
        "PRINT_PROVIDER=local\nPMF_FINAL_LAUNCH_MODE=configured\n",
    )

    result = build_final_resource_apply_preview_report(
        repo_root=repo_root,
        resources_file=resources,
    )
    actions = result.report["operator_actions"]

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
    assert not _known_bare_resource_actions(actions)
    assert not _resource_actions_with_wrong_rerun(actions)


def test_apply_preview_is_ready_for_valid_local_resources_without_secret_leak(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    resources = write_resources(repo_root, VALID_LOCAL_RESOURCES)

    result = build_final_resource_apply_preview_report(
        repo_root=repo_root,
        resources_file=resources,
    )
    report = result.report
    report_text = json.dumps(report)
    targets = report["write_targets_by_id"]
    backend_slots = {slot["id"]: slot for slot in targets["backend_env"]["slots"]}
    ios_slots = {slot["id"]: slot for slot in targets["ios_deploy_config"]["slots"]}

    assert result.exit_code == 0
    assert report["status"] == "ready"
    assert report["first_blocker"] is None
    assert report["next_action"] is None
    assert report["summary"]["blocked"] == 0
    assert report["summary"]["missing"] == 0
    assert report["summary"]["ready"] >= 9
    assert targets["backend_env"]["status"] == "ready"
    assert targets["backend_env"]["destination"] == "services/backend/.env"
    assert targets["backend_env"]["writer"] == "services/backend/scripts/write_backend_env.sh"
    assert targets["ios_deploy_config"]["status"] == "ready"
    assert targets["ios_deploy_config"]["destination"] == (
        "apps/mobile/ios/Config/Deployment.local.xcconfig"
    )
    assert backend_slots["MESHY_API_KEY"]["secret"] is True
    assert backend_slots["MESHY_API_KEY"]["redacted"] is True
    assert backend_slots["MESHY_API_KEY"]["writes"] == ["MESHY_API_KEY"]
    assert backend_slots["OPENAI_API_KEY"]["writes"] == ["OPENAI_API_KEY"]
    assert backend_slots["PRINT_PROVIDER"]["writes"] == ["PRINT_PROVIDER"]
    assert backend_slots["TREATSTOCK_API_KEY"]["required"] is False
    assert ios_slots["DEVELOPMENT_TEAM"]["writes"] == ["DEVELOPMENT_TEAM"]
    assert ios_slots["PMF_BACKEND_BASE_URL"]["writes"] == ["PMF_BACKEND_BASE_URL"]
    assert "meshy-secret-test" not in report_text
    assert "sk-openai-test" not in report_text
    assert "treatstock-secret-test" not in report_text
    assert "10.0.0.24" not in report_text
    assert str(tmp_path) not in report_text
    assert not backend_env_path(repo_root).exists()
    assert not ios_local_config_path(repo_root).exists()


def test_apply_preview_marks_auto_backend_url_ready_for_apply_time_resolution(
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

    result = build_final_resource_apply_preview_report(
        repo_root=repo_root,
        resources_file=resources,
    )
    report = result.report
    report_text = json.dumps(report)
    ios_target = report["write_targets_by_id"]["ios_deploy_config"]
    ios_slots = {slot["id"]: slot for slot in ios_target["slots"]}
    backend_url = ios_slots["PMF_BACKEND_BASE_URL"]

    assert result.exit_code == 0
    assert report["status"] == "ready"
    assert ios_target["status"] == "ready"
    assert "PMF_BACKEND_BASE_URL" not in ios_target["blocked_by"]
    assert backend_url["status"] == "ready"
    assert backend_url["classification"] == "apply_time_auto_url"
    assert backend_url["resolution_mode"] == "apply_time_auto"
    assert "write_deploy_local_config.sh" in backend_url["apply_note"]
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
