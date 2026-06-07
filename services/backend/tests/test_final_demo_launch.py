import json
from pathlib import Path

from myth_forge_api.config import Settings
from myth_forge_api.final_demo_launch import build_final_demo_launch_report


def test_configured_final_demo_launch_blocks_missing_resources(tmp_path: Path) -> None:
    repo_root = _write_deploy_config(tmp_path)

    result = build_final_demo_launch_report(
        settings=Settings(),
        repo_root=repo_root,
        mode="configured",
    )

    assert result.exit_code == 2
    assert result.report["kind"] == "final_demo_launch_report"
    assert result.report["mode"] == "configured"
    assert result.report["overall_status"] == "blocked"
    assert result.report["summary"]["missing"] >= 3
    assert result.report["summary"]["manual"] >= 2
    assert "provide MESHY_API_KEY" in " ".join(result.report["operator_checklist"])
    assert "provide OPENAI_API_KEY" in " ".join(result.report["operator_checklist"])
    assert result.report["live_call_policy"] == {
        "live_calls_by_default": False,
        "configured_acceptance_requires_consent": True,
        "consent_flag": "--allow-live-provider-calls",
    }
    assert result.report["final_resources_preflight"]["status"] == "missing"
    assert any("--allow-live-provider-calls" in command for command in result.report["commands"])
    phases = {phase["id"]: phase for phase in result.report["launch_phases"]}
    assert phases["apply_final_resources"]["status"] == "missing"
    assert phases["apply_final_resources"]["command"] == "make final-apply-resources"
    assert "write_backend_env" not in phases
    assert "write_ios_deploy_config" not in phases
    assert phases["configured_final_acceptance"]["status"] == "blocked"
    assert result.report["commands"].index("make final-resources-preflight") < (
        result.report["commands"].index("make final-apply-resources")
    )
    assert "make final-apply-resources" in result.report["commands"]
    assert all("backend-write-provider-env" not in command for command in result.report["commands"])
    assert all("mobile-write-deploy-config" not in command for command in result.report["commands"])
    assert result.report["safety"]["global_mutation"] is False
    assert result.report["safety"]["live_provider_calls_by_default"] is False


def test_configured_final_demo_launch_marks_ready_resources_without_secret_leak(
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
    _write_final_resources(repo_root)
    _write_npc_evaluation(repo_root)
    _write_final_acceptance(
        repo_root,
        {
            "kind": "final_acceptance_report",
            "overall_status": "passed",
            "summary": {"passed": 14, "blocked": 0, "failed": 0, "skipped": 0},
            "checks": [
                {"id": "provider_handoff", "label": "Provider handoff", "status": "passed"},
                {"id": "demo_acceptance", "label": "Demo acceptance", "status": "passed"},
            ],
        },
    )
    settings = Settings(
        three_d_provider="meshy",
        meshy_api_key="sk-meshy-secret",
        npc_provider="openai",
        openai_api_key="sk-openai-secret",
        print_provider="treatstock",
        treatstock_api_key="treatstock-secret",
    )

    result = build_final_demo_launch_report(
        settings=settings,
        repo_root=repo_root,
        mode="configured",
    )
    report_text = json.dumps(result.report)
    backend = {
        item["id"]: item
        for item in result.report["resource_report"]["backend"]["items"]
    }
    phases = {phase["id"]: phase for phase in result.report["launch_phases"]}

    assert result.exit_code == 0
    assert result.report["overall_status"] == "partial"
    assert result.report["final_resources_preflight"]["status"] == "ready"
    assert backend["MESHY_API_KEY"]["status"] == "ready"
    assert backend["OPENAI_API_KEY"]["status"] == "ready"
    assert backend["PRINT_PROVIDER"]["status"] == "ready"
    assert backend["TREATSTOCK_API_KEY"]["status"] == "ready"
    assert "Treatstock live quote handoff is implemented" in " ".join(
        backend["TREATSTOCK_API_KEY"]["notes"]
    )
    assert phases["apply_final_resources"]["status"] == "ready"
    assert phases["provider_readiness"]["status"] == "ready"
    assert phases["configured_final_acceptance"]["status"] == "ready"
    assert phases["xcode_build_gate"]["status"] == "manual"
    handoff = result.report["final_operator_handoff"]
    handoff_steps = {step["id"]: step for step in handoff["steps"]}
    assert handoff["status"] == "partial"
    assert handoff["summary"]["live"] == 1
    assert handoff_steps["configured_final_acceptance"]["status"] == "live"
    assert handoff_steps["configured_final_acceptance"]["requires_consent"] is True
    assert handoff["next_actions"] == [
        (
            "run configured final acceptance only after live provider cost review "
            "and --allow-live-provider-calls consent"
        ),
        "run Xcode build gate manually on the Mac: make mobile-xcode-build",
    ]
    assert "sk-meshy-secret" not in report_text
    assert "sk-openai-secret" not in report_text
    assert "treatstock-secret" not in report_text
    assert str(tmp_path) not in report_text


def test_local_final_demo_launch_is_no_key_ready_but_surfaces_ios_actions(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)

    result = build_final_demo_launch_report(
        settings=Settings(),
        repo_root=repo_root,
        mode="local",
    )

    assert result.exit_code == 0
    assert result.report["mode"] == "local"
    assert result.report["overall_status"] == "partial"
    assert result.report["final_resources_preflight"]["status"] == "missing"
    phases = {phase["id"]: phase for phase in result.report["launch_phases"]}
    assert phases["apply_final_resources"]["status"] == "missing"
    assert phases["apply_final_resources"]["command"] == "make final-apply-resources"
    assert "write_backend_env" not in phases
    assert "write_ios_deploy_config" not in phases
    assert result.report["commands"].index("make final-resources-preflight") < (
        result.report["commands"].index("make final-apply-resources")
    )
    assert "make final-apply-resources" in result.report["commands"]
    assert "make backend-device-demo" in result.report["commands"]
    assert "make mobile-deploy-preflight" in result.report["commands"]
    assert all("MESHY_API_KEY=..." not in command for command in result.report["commands"])
    assert all("backend-write-provider-env" not in command for command in result.report["commands"])
    assert all("mobile-write-deploy-config" not in command for command in result.report["commands"])
    assert any(
        "set PMF_BACKEND_BASE_URL" in action
        for action in result.report["operator_checklist"]
    )


def test_local_final_demo_launch_marks_unified_apply_missing_with_ios_only(
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

    result = build_final_demo_launch_report(
        settings=Settings(),
        repo_root=repo_root,
        mode="local",
    )
    phases = {phase["id"]: phase for phase in result.report["launch_phases"]}

    assert result.exit_code == 0
    assert result.report["overall_status"] == "partial"
    assert result.report["final_resources_preflight"]["status"] == "missing"
    assert phases["apply_final_resources"]["status"] == "missing"
    assert phases["mobile_deploy_preflight"]["status"] == "ready"


def test_local_final_demo_launch_marks_unified_apply_ready_with_preflight(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_final_resources(repo_root)

    result = build_final_demo_launch_report(
        settings=Settings(),
        repo_root=repo_root,
        mode="local",
    )
    phases = {phase["id"]: phase for phase in result.report["launch_phases"]}

    assert result.exit_code == 0
    assert result.report["overall_status"] == "partial"
    assert result.report["final_resources_preflight"]["status"] == "ready"
    assert phases["apply_final_resources"]["status"] == "ready"
    assert phases["mobile_deploy_preflight"]["status"] == "blocked"


def test_final_demo_launch_embeds_saved_final_acceptance_readiness(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_final_acceptance(
        repo_root,
        {
            "kind": "final_acceptance_report",
            "overall_status": "blocked",
            "summary": {"passed": 12, "blocked": 1, "failed": 0, "skipped": 0},
            "checks": [
                {"id": "provider_handoff", "label": "Provider handoff", "status": "passed"},
                {
                    "id": "mobile_deploy_preflight",
                    "label": "iOS deploy preflight",
                    "status": "blocked",
                    "classification": "blocked_by_local_ios_backend_health",
                    "command": ["make", "mobile-deploy-preflight"],
                    "stderr_tail": "Backend health failed at /Users/zhexu/private sk-secret",
                },
            ],
        },
    )

    result = build_final_demo_launch_report(
        settings=Settings(),
        repo_root=repo_root,
        mode="local",
    )
    report_text = json.dumps(result.report)
    readiness = result.report["final_acceptance_readiness"]

    assert readiness["status"] == "blocked"
    assert readiness["source_file"] == {
        "path": "services/backend/.local/final-acceptance-local.json",
        "exists": True,
    }
    assert readiness["summary"] == {"passed": 12, "blocked": 1, "failed": 0, "skipped": 0}
    assert readiness["blockers"] == [
        {
            "id": "mobile_deploy_preflight",
            "label": "iOS deploy preflight",
            "status": "blocked",
            "classification": "blocked_by_local_ios_backend_health",
            "command": "make mobile-deploy-preflight",
            "detail": "Backend health failed at [home]/private [redacted]",
        }
    ]
    assert readiness["operator_actions"] == [
        "start backend-device-demo and rerun mobile deploy preflight"
    ]
    assert readiness["freshness"]["status"] in {"fresh", "unknown"}
    assert readiness["freshness"]["classification"] in {"fresh_report", "git_unavailable"}
    handoff = result.report["final_operator_handoff"]
    handoff_steps = {step["id"]: step for step in handoff["steps"]}
    assert handoff["status"] == "blocked"
    assert handoff_steps["local_final_acceptance"]["status"] == "blocked"
    assert handoff_steps["mobile_deploy_preflight"]["status"] == "blocked"
    assert handoff_steps["mobile_deploy_preflight"]["source"] == "final_acceptance_readiness"
    assert handoff["next_actions"][:2] == [
        (
            "copy services/backend/final-resources.env.example to "
            "services/backend/.local/final-resources.env"
        ),
        "start backend-device-demo and rerun mobile deploy preflight",
    ]
    assert "run Xcode build gate manually on the Mac: make mobile-xcode-build" in handoff[
        "next_actions"
    ]
    assert "sk-secret" not in report_text
    assert str(tmp_path) not in report_text


def test_final_demo_launch_embeds_npc_agent_evaluation_readiness(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_npc_evaluation(repo_root)

    result = build_final_demo_launch_report(
        settings=Settings(),
        repo_root=repo_root,
        mode="local",
    )

    readiness = result.report["npc_agent_evaluation_readiness"]

    assert readiness["kind"] == "npc_agent_evaluation_readiness_report"
    assert readiness["status"] == "ready"
    assert readiness["summary"]["succeeded"] == 6
    assert readiness["coverage"]["tick_steps_completed"] == 12
    assert readiness["safety"]["commands_run"] is False


def test_final_demo_launch_operator_handoff_includes_npc_evaluation_step(
    tmp_path: Path,
) -> None:
    repo_root = _write_deploy_config(tmp_path)
    _write_npc_evaluation(repo_root)

    result = build_final_demo_launch_report(
        settings=Settings(),
        repo_root=repo_root,
        mode="local",
    )
    handoff_steps = {
        step["id"]: step
        for step in result.report["final_operator_handoff"]["steps"]
    }

    assert handoff_steps["npc_agent_evaluation"]["status"] == "ready"
    assert "evaluate-npc" in handoff_steps["npc_agent_evaluation"]["command"]


def test_final_demo_launch_embeds_ios_deploy_runbook(tmp_path: Path) -> None:
    repo_root = _write_deploy_config(tmp_path)

    result = build_final_demo_launch_report(
        settings=Settings(),
        repo_root=repo_root,
        mode="local",
    )

    runbook = result.report["ios_deploy_runbook"]

    assert runbook["kind"] == "ios_deploy_runbook_report"
    assert any(
        step["id"] == "mobile_deploy_preflight"
        for step in runbook["command_sequence"]
    )
    assert any(
        slot["id"] == "backend_base_url"
        for slot in runbook["input_slots"]
    )


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


def _write_final_acceptance(repo_root: Path, report: dict[str, object]) -> None:
    acceptance = repo_root / "services/backend/.local/final-acceptance-local.json"
    acceptance.parent.mkdir(parents=True, exist_ok=True)
    acceptance.write_text(json.dumps(report), encoding="utf-8")


def _write_npc_evaluation(repo_root: Path) -> None:
    report = {
        "kind": "npc_agent_evaluation_report",
        "suite": "default-v0",
        "provider": "local",
        "tick_steps": 2,
        "total_cases": 6,
        "succeeded": 6,
        "failed": 0,
        "coverage": {
            "expected_npc_sets": 6,
            "trace_sets": 6,
            "proposed_action_plan_matches": 6,
            "tick_steps_completed": 12,
            "world_resolution_steps": 12,
        },
        "cases": [],
    }
    evaluation = repo_root / "services/backend/.local/npc-evaluation-local.json"
    evaluation.parent.mkdir(parents=True, exist_ok=True)
    evaluation.write_text(json.dumps(report), encoding="utf-8")


def _write_final_resources(repo_root: Path) -> None:
    resources = repo_root / "services/backend/.local/final-resources.env"
    resources.parent.mkdir(parents=True)
    resources.write_text(
        "\n".join(
            [
                "MESHY_API_KEY=meshy-secret-test",
                "OPENAI_API_KEY=sk-openai-test",
                "PRINT_PROVIDER=local",
                "DEVELOPMENT_TEAM=TEAM12345",
                "PRODUCT_BUNDLE_IDENTIFIER=com.example.personalmythforge",
                "PMF_BACKEND_BASE_URL=http://192.168.1.10:8080",
            ]
        ),
        encoding="utf-8",
    )
