from __future__ import annotations

import json
from pathlib import Path

from myth_forge_api.cli import main
from myth_forge_api.ios_deploy_runbook import build_ios_deploy_runbook_report


def test_ios_deploy_runbook_blocks_missing_inputs_without_secret_or_path_leak(
    tmp_path: Path,
) -> None:
    repo_root = _repo(tmp_path)

    report = build_ios_deploy_runbook_report(mode="local", repo_root=repo_root)
    report_text = json.dumps(report)
    slots = {slot["id"]: slot for slot in report["input_slots"]}

    assert report["kind"] == "ios_deploy_runbook_report"
    assert report["mode"] == "local"
    assert report["status"] == "blocked"
    assert slots["final_resources_env"]["status"] == "missing"
    assert slots["final_resource_apply_preview"]["status"] == "missing"
    assert slots["development_team"]["status"] == "missing"
    assert slots["backend_base_url"]["status"] == "missing"
    assert slots["local_final_acceptance"]["status"] == "missing"
    assert slots["three_d_evaluation"]["status"] == "missing"
    assert slots["npc_agent_evaluation"]["status"] == "missing"
    assert "run make final-resource-init" in " ".join(report["operator_actions"])
    assert "run make final-resource-apply-preview before applying resources" in " ".join(
        report["operator_actions"]
    )
    assert "run make final-acceptance-local" in " ".join(report["operator_actions"])
    assert "run make backend-evaluate-3d" in " ".join(report["operator_actions"])
    assert "run make backend-evaluate-npc" in " ".join(report["operator_actions"])
    commands = [step["command"] for step in report["command_sequence"]]
    assert commands[:3] == [
        "make final-resources-preflight",
        "make final-resource-apply-preview",
        "make final-apply-resources",
    ]
    assert "run local 3D evaluation with evaluate-3d" not in report_text
    assert "run local NPC Agent evaluation with evaluate-npc" not in report_text
    assert report["safety"] == {
        "commands_run": False,
        "provider_calls": False,
        "global_mutation": False,
        "provider_secrets_in_report": False,
        "raw_media_in_report": False,
        "payment_links_in_report": False,
        "local_paths_in_report": False,
    }
    assert "sk-" not in report_text
    assert str(tmp_path) not in report_text


def test_ios_deploy_runbook_resource_actions_include_validation_commands(
    tmp_path: Path,
) -> None:
    repo_root = _repo(tmp_path)

    report = build_ios_deploy_runbook_report(mode="local", repo_root=repo_root)
    actions = report["operator_actions"]

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
        "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig; "
        "rerun make mobile-deploy-preflight"
    ) in actions
    assert (
        "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL; "
        "rerun make mobile-deploy-preflight"
    ) in actions
    assert not any(
        action.endswith("provide MESHY_API_KEY in final-resources.env")
        or action.endswith("provide OPENAI_API_KEY in final-resources.env")
        or action.endswith("provide DEVELOPMENT_TEAM in final-resources.env")
        or action.endswith("provide PRODUCT_BUNDLE_IDENTIFIER in final-resources.env")
        or action.endswith("provide DEVELOPMENT_TEAM in Deployment.local.xcconfig")
        or action.endswith("set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL")
        for action in actions
    )


def test_ios_deploy_runbook_ready_local_inputs_preserve_command_order(
    tmp_path: Path,
) -> None:
    repo_root = _repo(tmp_path)
    _write_deploy_config(repo_root)
    _write_final_resources(repo_root)
    _write_final_acceptance(repo_root, status="passed")
    _write_three_d_evaluation(repo_root, status="passed")
    _write_npc_evaluation(repo_root, status="passed")

    report = build_ios_deploy_runbook_report(mode="local", repo_root=repo_root)
    commands = [step["command"] for step in report["command_sequence"]]
    slots = {slot["id"]: slot for slot in report["input_slots"]}

    assert report["status"] == "partial"
    assert slots["development_team"]["status"] == "ready"
    assert slots["final_resource_apply_preview"]["status"] == "ready"
    assert slots["backend_base_url"]["status"] == "ready"
    assert slots["three_d_evaluation"]["status"] == "ready"
    assert "3D evaluation is ready" not in " ".join(report["operator_actions"])
    assert commands[:5] == [
        "make final-resources-preflight",
        "make final-resource-apply-preview",
        "make final-apply-resources",
        "make backend-device-demo",
        "make mobile-deploy-preflight",
    ]
    assert commands[-1] == "make mobile-xcode-build"
    assert report["command_sequence"][-1]["id"] == "xcode_build_gate"
    assert report["command_sequence"][-1]["status"] == "manual"


def test_ios_deploy_runbook_configured_mode_includes_live_acceptance_consent(
    tmp_path: Path,
) -> None:
    repo_root = _repo(tmp_path)
    _write_deploy_config(repo_root, final_launch_mode="configured")
    _write_final_resources(repo_root)
    _write_final_acceptance(repo_root, status="passed")
    _write_three_d_evaluation(repo_root, status="passed")
    _write_npc_evaluation(repo_root, status="passed")

    report = build_ios_deploy_runbook_report(mode="configured", repo_root=repo_root)
    commands = {step["id"]: step for step in report["command_sequence"]}

    assert report["status"] == "partial"
    assert commands["configured_final_acceptance"]["requires_consent"] is True
    assert commands["configured_final_acceptance"]["command"] == (
        "make final-acceptance-configured"
    )
    assert "live provider cost review" in " ".join(report["operator_actions"])


def test_ios_deploy_runbook_surfaces_final_resource_repair_action(
    tmp_path: Path,
) -> None:
    repo_root = _repo(tmp_path)
    _write_final_resources(
        repo_root,
        bundle_identifier="com.example.personalmythforge",
        backend_base_url="http://192.168.1.10:8080",
    )

    report = build_ios_deploy_runbook_report(mode="local", repo_root=repo_root)

    assert report["status"] == "blocked"
    assert "run make final-resource-repair" in report["operator_actions"]


def test_ios_deploy_runbook_blocks_and_redacts_failed_3d_evaluation(
    tmp_path: Path,
) -> None:
    repo_root = _repo(tmp_path)
    _write_deploy_config(repo_root)
    _write_final_resources(repo_root)
    _write_final_acceptance(repo_root, status="passed")
    _write_three_d_evaluation(
        repo_root,
        status="failed",
        error=(
            "Meshy failed Authorization=Bearer test-secret raw_context: private "
            + f"file://{tmp_path}/private.glb /Users/zhexu/private"
        ),
    )
    _write_npc_evaluation(repo_root, status="passed")

    report = build_ios_deploy_runbook_report(mode="local", repo_root=repo_root)
    report_text = json.dumps(report)
    slots = {slot["id"]: slot for slot in report["input_slots"]}

    assert report["status"] == "blocked"
    assert slots["three_d_evaluation"]["status"] == "blocked"
    assert "rerun make backend-evaluate-3d and review failed cases" in " ".join(
        report["operator_actions"]
    )
    assert "rerun local 3D evaluation" not in report_text
    assert "run local 3D evaluation with evaluate-3d" not in report_text
    assert "test-secret" not in report_text
    assert "raw_context:" not in report_text
    assert "file://" not in report_text
    assert "/Users/" not in report_text
    assert "Bearer" not in report_text


def test_ios_deploy_runbook_cli_writes_output(tmp_path: Path) -> None:
    repo_root = _repo(tmp_path)
    output = tmp_path / "runbook.json"

    exit_code = main(
        [
            "ios-deploy-runbook",
            "--mode",
            "local",
            "--repo-root",
            str(repo_root),
            "--output",
            str(output),
        ]
    )

    assert exit_code == 2
    assert json.loads(output.read_text(encoding="utf-8"))[
        "kind"
    ] == "ios_deploy_runbook_report"


def _repo(tmp_path: Path) -> Path:
    repo_root = tmp_path / "repo"
    config_dir = repo_root / "apps/mobile/ios/Config"
    config_dir.mkdir(parents=True)
    (config_dir / "Deployment.xcconfig").write_text(
        "\n".join(
            [
                "PRODUCT_BUNDLE_IDENTIFIER = com.personalmythforge.app",
                "DEVELOPMENT_TEAM =",
                "CODE_SIGN_STYLE = Automatic",
                "PMF_BACKEND_BASE_URL =",
                "PMF_FINAL_LAUNCH_MODE = local",
                '#include? "Deployment.local.xcconfig"',
            ]
        ),
        encoding="utf-8",
    )
    return repo_root


def _write_deploy_config(repo_root: Path, *, final_launch_mode: str = "local") -> None:
    config = repo_root / "apps/mobile/ios/Config/Deployment.local.xcconfig"
    config.write_text(
        "\n".join(
            [
                "DEVELOPMENT_TEAM = TEAM12345",
                "PRODUCT_BUNDLE_IDENTIFIER = com.zhexu.personalmythforge.dev",
                "PMF_BACKEND_BASE_URL = http://10.0.0.24:8080",
                f"PMF_FINAL_LAUNCH_MODE = {final_launch_mode}",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _write_final_resources(
    repo_root: Path,
    *,
    bundle_identifier: str = "com.zhexu.personalmythforge.dev",
    backend_base_url: str = "http://10.0.0.24:8080",
) -> None:
    resources = repo_root / "services/backend/.local/final-resources.env"
    resources.parent.mkdir(parents=True)
    resources.write_text(
        "\n".join(
            [
                "MESHY_API_KEY=meshy-secret-test",
                "OPENAI_API_KEY=sk-openai-test",
                "PRINT_PROVIDER=local",
                "DEVELOPMENT_TEAM=TEAM12345",
                f"PRODUCT_BUNDLE_IDENTIFIER={bundle_identifier}",
                f"PMF_BACKEND_BASE_URL={backend_base_url}",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _write_final_acceptance(repo_root: Path, *, status: str) -> None:
    acceptance = repo_root / "services/backend/.local/final-acceptance-local.json"
    acceptance.parent.mkdir(parents=True, exist_ok=True)
    acceptance.write_text(
        json.dumps(
            {
                "kind": "final_acceptance_report",
                "overall_status": status,
                "summary": {"passed": 14, "blocked": 0, "failed": 0, "skipped": 0},
                "checks": [
                    {"id": "provider_handoff", "label": "Provider handoff", "status": status}
                ],
            }
        ),
        encoding="utf-8",
    )


def _write_three_d_evaluation(
    repo_root: Path,
    *,
    status: str,
    error: str = "3D evaluation case failed.",
) -> None:
    succeeded = 20 if status == "passed" else 0
    failed = 0 if status == "passed" else 20
    evaluation = repo_root / "services/backend/.local/3d-evaluation-local.json"
    evaluation.parent.mkdir(parents=True, exist_ok=True)
    evaluation.write_text(
        json.dumps(
            {
                "kind": "three_d_evaluation_report",
                "suite": "default-v0",
                "provider": "local",
                "total_cases": 20,
                "succeeded": succeeded,
                "failed": failed,
                "coverage": {
                    "input_modes": {
                        "text_prompt": succeeded,
                        "single_image": 0,
                        "multi_image": 0,
                    },
                    "variant_roles": {
                        "game_asset": succeeded,
                        "ios_scene_asset": succeeded,
                    },
                    "scene_loadable_cases": succeeded,
                },
                "cases": [
                    {
                        "id": "case-1",
                        "status": status,
                        "generated_asset": {
                            "provider": "local",
                            "format": "glb",
                            "uri": "local://generated-assets/case-1.glb",
                            "variants": [
                                {"role": "game_asset", "format": "glb"},
                                {
                                    "role": "ios_scene_asset",
                                    "format": "dae",
                                    "is_scene_loadable": True,
                                },
                            ],
                        },
                        "error": error if status != "passed" else None,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def _write_npc_evaluation(repo_root: Path, *, status: str) -> None:
    succeeded = 6 if status == "passed" else 0
    failed = 0 if status == "passed" else 6
    evaluation = repo_root / "services/backend/.local/npc-evaluation-local.json"
    evaluation.parent.mkdir(parents=True, exist_ok=True)
    evaluation.write_text(
        json.dumps(
            {
                "kind": "npc_agent_evaluation_report",
                "suite": "default-v0",
                "provider": "local",
                "tick_steps": 2,
                "total_cases": 6,
                "succeeded": succeeded,
                "failed": failed,
                "coverage": {
                    "expected_npc_sets": succeeded,
                    "trace_sets": succeeded,
                    "proposed_action_plan_matches": succeeded,
                    "tick_steps_completed": succeeded * 2,
                    "world_resolution_steps": succeeded * 2,
                },
                "cases": [],
            }
        ),
        encoding="utf-8",
    )
