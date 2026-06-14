import json
from pathlib import Path

from myth_forge_api.live_provider_evidence import (
    build_live_provider_evidence_report,
)


def test_live_provider_evidence_missing_reports_without_running_commands(
    tmp_path: Path,
) -> None:
    result = build_live_provider_evidence_report(repo_root=tmp_path)

    assert result.exit_code == 2
    assert result.report["kind"] == "live_provider_evidence_report"
    assert result.report["status"] == "missing"
    assert result.report["summary"] == {
        "ready": 0,
        "missing": 5,
        "blocked": 0,
        "partial": 0,
        "requires_live_provider_consent": 3,
    }
    assert result.report["first_blocker"]["id"] == "provider_handoff"
    assert result.report["first_blocker"]["status"] == "missing"
    assert result.report["next_action"] == {
        **result.report["first_blocker"],
        "requires_live_provider_consent": False,
        "validation_command": "make live-provider-evidence",
        "source": "first_blocker",
    }
    evidence = {slot["id"]: slot for slot in result.report["evidence"]}
    assert evidence["provider_handoff"]["status"] == "missing"
    assert evidence["provider_handoff"]["command"] == "make provider-handoff"
    assert evidence["three_d_evaluation_configured"]["status"] == "missing"
    assert evidence["three_d_evaluation_configured"]["command"] == (
        "make backend-evaluate-3d-configured"
    )
    assert evidence["three_d_evaluation_configured"]["requires_live_provider_consent"] is True
    assert evidence["npc_evaluation_configured"]["command"] == (
        "make backend-evaluate-npc-configured"
    )
    assert evidence["final_demo_launch_configured"]["command"] == (
        "make final-demo-launch-configured"
    )
    assert "make provider-handoff" in result.report["commands"]
    assert "make final-demo-launch-configured" in result.report["commands"]
    assert not any(
        "myth_forge_api.cli provider-handoff" in command
        or "final-demo-launch --mode configured" in command
        for command in result.report["commands"]
    )
    assert result.report["operator_actions"] == [
        "make provider-handoff; rerun make live-provider-evidence",
    ]
    assert not any(
        action.startswith("run make ")
        or action.startswith("rerun provider handoff readiness")
        for action in result.report["operator_actions"]
    )
    assert result.report["safety"]["commands_run"] is False
    assert result.report["safety"]["provider_calls"] is False
    assert result.report["safety"]["provider_secrets_in_report"] is False
    assert result.report["safety"]["raw_media_in_report"] is False


def test_live_provider_evidence_ready_from_configured_fixtures(
    tmp_path: Path,
) -> None:
    _write_ready_evidence(tmp_path)

    result = build_live_provider_evidence_report(repo_root=tmp_path)

    assert result.exit_code == 0
    assert result.report["status"] == "ready"
    assert result.report["summary"] == {
        "ready": 5,
        "missing": 0,
        "blocked": 0,
        "partial": 0,
        "requires_live_provider_consent": 3,
    }
    assert result.report["first_blocker"] is None
    assert result.report["next_action"] is None
    assert result.report["operator_actions"] == []
    evidence = {slot["id"]: slot for slot in result.report["evidence"]}
    assert evidence["provider_handoff"]["status"] == "ready"
    assert evidence["three_d_evaluation_configured"]["status"] == "ready"
    assert evidence["npc_evaluation_configured"]["status"] == "ready"
    assert evidence["final_acceptance_configured"]["status"] == "ready"
    assert evidence["final_demo_launch_configured"]["status"] == "ready"


def test_live_provider_evidence_blocks_saved_non_real_provider_handoff(
    tmp_path: Path,
) -> None:
    _write_json(
        tmp_path / "services/backend/.local/provider-handoff.json",
        {
            "kind": "provider_handoff_report",
            "status": "blocked",
            "classification": "core_real_providers_not_ready",
            "core_real_ready": False,
            "missing_env": [],
        },
    )

    result = build_live_provider_evidence_report(repo_root=tmp_path)

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert result.report["first_blocker"]["id"] == "provider_handoff"
    assert result.report["first_blocker"]["detail"] == (
        "Core real providers are not ready for live evidence."
    )


def test_live_provider_evidence_projects_provider_handoff_child_next_action(
    tmp_path: Path,
) -> None:
    _write_json(
        tmp_path / "services/backend/.local/provider-handoff.json",
        {
            "kind": "provider_handoff_report",
            "status": "blocked",
            "classification": "core_real_providers_not_ready",
            "core_real_ready": False,
            "missing_env": [],
            "next_action": {
                "id": "three_d_provider",
                "label": "3D provider",
                "status": "blocked",
                "classification": "local_stub",
                "command": "make final-resource-apply-preview",
                "detail": "Core 3D provider is demo-ready but not configured.",
                "validation_command": "make provider-handoff",
                "source": "first_blocker",
            },
        },
    )

    result = build_live_provider_evidence_report(repo_root=tmp_path)

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert result.report["first_blocker"]["id"] == "provider_handoff"
    assert result.report["first_blocker"]["command"] == (
        "make final-resource-apply-preview"
    )
    assert result.report["first_blocker"]["source_blocker_id"] == "three_d_provider"
    assert result.report["first_blocker"]["source_blocker_command"] == (
        "make final-resource-apply-preview"
    )
    assert result.report["first_blocker"]["source_blocker_validation_command"] == (
        "make provider-handoff"
    )
    assert result.report["first_blocker"]["detail"] == (
        "Core 3D provider is demo-ready but not configured."
    )
    assert result.report["next_action"]["id"] == "provider_handoff"
    assert result.report["next_action"]["command"] == (
        "make final-resource-apply-preview"
    )
    assert result.report["next_action"]["validation_command"] == (
        "make live-provider-evidence"
    )
    assert result.report["operator_actions"][0] == (
        "make final-resource-apply-preview; "
        "rerun make provider-handoff; "
        "rerun make live-provider-evidence"
    )
    assert "rerun provider handoff readiness" not in " ".join(
        result.report["operator_actions"]
    )
    evidence = {slot["id"]: slot for slot in result.report["evidence"]}
    assert evidence["provider_handoff"]["source_blocker_id"] == "three_d_provider"


def test_live_provider_evidence_blocks_failed_report_and_redacts(
    tmp_path: Path,
) -> None:
    _write_ready_evidence(tmp_path)
    _write_json(
        tmp_path / "services/backend/.local/3d-evaluation-configured.json",
        {
            "kind": "three_d_evaluation_report",
            "provider": "meshy",
            "suite": "default-v0",
            "total_cases": 20,
            "succeeded": 19,
            "failed": 1,
            "errors": [
                (
                    "Authorization Bearer secret-token sk-live-secret "
                    "data:image/png;base64,abc file:///tmp/private.glb "
                    "checkout_url https://pay.example/order"
                )
            ],
        },
    )

    result = build_live_provider_evidence_report(repo_root=tmp_path)
    report_text = json.dumps(result.report)

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert result.report["summary"]["blocked"] == 1
    assert result.report["first_blocker"]["id"] == "three_d_evaluation_configured"
    assert result.report["first_blocker"]["classification"] == "report_not_ready"
    assert result.report["next_action"]["id"] == "three_d_evaluation_configured"
    assert result.report["next_action"]["requires_live_provider_consent"] is True
    assert result.report["next_action"]["validation_command"] == (
        "make live-provider-evidence"
    )
    assert (
        "make backend-evaluate-3d-configured; rerun make live-provider-evidence"
        in " ".join(result.report["operator_actions"])
    )
    assert "secret-token" not in report_text
    assert "sk-live-secret" not in report_text
    assert "data:image" not in report_text
    assert "file://" not in report_text
    assert "pay.example" not in report_text
    assert str(tmp_path) not in report_text


def test_live_provider_evidence_operator_action_prefixes_live_consent(
    tmp_path: Path,
) -> None:
    _write_ready_evidence(tmp_path)
    _write_json(
        tmp_path / "services/backend/.local/3d-evaluation-configured.json",
        {
            "kind": "three_d_evaluation_report",
            "provider": "meshy",
            "suite": "default-v0",
            "total_cases": 20,
            "succeeded": 0,
            "failed": 20,
            "errors": ["Meshy configured evaluation needs an approved live retry."],
        },
    )

    result = build_live_provider_evidence_report(repo_root=tmp_path)

    assert result.exit_code == 2
    assert result.report["first_blocker"]["id"] == "three_d_evaluation_configured"
    assert result.report["next_action"]["command"] == (
        "make backend-evaluate-3d-configured"
    )
    assert result.report["next_action"]["requires_live_provider_consent"] is True
    assert result.report["operator_actions"] == [
        (
            "PMF_ALLOW_LIVE_PROVIDER_CALLS=1 make backend-evaluate-3d-configured; "
            "rerun make live-provider-evidence"
        )
    ]


def test_live_provider_evidence_blocks_unreadable_json(tmp_path: Path) -> None:
    path = tmp_path / "services/backend/.local/provider-handoff.json"
    path.parent.mkdir(parents=True)
    path.write_text("{not-json", encoding="utf-8")

    result = build_live_provider_evidence_report(repo_root=tmp_path)

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert result.report["first_blocker"]["id"] == "provider_handoff"
    assert result.report["first_blocker"]["classification"] == "unreadable_report"


def test_live_provider_evidence_marks_partial_configured_launch_report(
    tmp_path: Path,
) -> None:
    _write_ready_evidence(tmp_path)
    _write_json(
        tmp_path / "services/backend/.local/final-demo-launch-configured.json",
        {
            "kind": "final_demo_launch_report",
            "mode": "configured",
            "overall_status": "partial",
            "summary": {"ready": 8, "missing": 0, "blocked": 0, "manual": 1},
        },
    )

    result = build_live_provider_evidence_report(repo_root=tmp_path)
    evidence = {slot["id"]: slot for slot in result.report["evidence"]}

    assert result.exit_code == 2
    assert result.report["status"] == "partial"
    assert result.report["summary"]["partial"] == 1
    assert result.report["first_blocker"]["id"] == "final_demo_launch_configured"
    assert evidence["final_demo_launch_configured"]["status"] == "partial"


def test_live_provider_evidence_cli_writes_report(tmp_path: Path) -> None:
    output = tmp_path / "live-provider-evidence.json"

    from myth_forge_api.cli import main

    exit_code = main(
        [
            "live-provider-evidence",
            "--repo-root",
            str(tmp_path),
            "--output",
            str(output),
        ]
    )

    assert exit_code == 2
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["kind"] == "live_provider_evidence_report"
    assert payload["status"] == "missing"


def test_live_provider_evidence_makefile_target() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    makefile = (repo_root / "Makefile").read_text(encoding="utf-8")
    wrapper = (
        repo_root / "services/backend/scripts/write_live_provider_evidence.sh"
    ).read_text(encoding="utf-8")

    assert "live-provider-evidence:" in makefile
    assert "services/backend/scripts/write_live_provider_evidence.sh" in makefile
    assert "myth_forge_api.cli live-provider-evidence" in wrapper
    assert ".local/live-provider-evidence.json" in wrapper


def _write_ready_evidence(repo_root: Path) -> None:
    _write_json(
        repo_root / "services/backend/.local/provider-handoff.json",
        {
            "kind": "provider_handoff_report",
            "core_real_ready": True,
            "overall_real_ready": True,
            "missing_env": [],
        },
    )
    _write_json(
        repo_root / "services/backend/.local/3d-evaluation-configured.json",
        {
            "kind": "three_d_evaluation_report",
            "provider": "meshy",
            "suite": "default-v0",
            "total_cases": 20,
            "succeeded": 20,
            "failed": 0,
            "coverage": {"scene_loadable_cases": 20},
        },
    )
    _write_json(
        repo_root / "services/backend/.local/npc-evaluation-configured.json",
        {
            "kind": "npc_agent_evaluation_report",
            "provider": "openai",
            "suite": "default-v0",
            "total_cases": 6,
            "succeeded": 6,
            "failed": 0,
        },
    )
    _write_json(
        repo_root / "services/backend/.local/final-acceptance-configured.json",
        {
            "kind": "final_acceptance_report",
            "profile": "quick",
            "provider_mode": "configured",
            "overall_status": "passed",
            "summary": {"passed": 14, "blocked": 0, "failed": 0, "skipped": 0},
        },
    )
    _write_json(
        repo_root / "services/backend/.local/final-demo-launch-configured.json",
        {
            "kind": "final_demo_launch_report",
            "mode": "configured",
            "overall_status": "ready",
            "summary": {"ready": 9, "missing": 0, "blocked": 0, "manual": 0},
        },
    )


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
