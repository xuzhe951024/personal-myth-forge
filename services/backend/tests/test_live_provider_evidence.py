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
    evidence = {slot["id"]: slot for slot in result.report["evidence"]}
    assert evidence["provider_handoff"]["status"] == "missing"
    assert evidence["three_d_evaluation_configured"]["status"] == "missing"
    assert evidence["three_d_evaluation_configured"]["command"] == (
        "make backend-evaluate-3d-configured"
    )
    assert evidence["three_d_evaluation_configured"]["requires_live_provider_consent"] is True
    assert evidence["npc_evaluation_configured"]["command"] == (
        "make backend-evaluate-npc-configured"
    )
    assert "make live-provider-evidence" in result.report["operator_actions"][0]
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
    assert "rerun configured 3D evaluation" in " ".join(result.report["operator_actions"])
    assert "secret-token" not in report_text
    assert "sk-live-secret" not in report_text
    assert "data:image" not in report_text
    assert "file://" not in report_text
    assert "pay.example" not in report_text
    assert str(tmp_path) not in report_text


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
    makefile = (Path(__file__).resolve().parents[3] / "Makefile").read_text(
        encoding="utf-8"
    )

    assert "live-provider-evidence:" in makefile
    assert "myth_forge_api.cli live-provider-evidence" in makefile
    assert ".local/live-provider-evidence.json" in makefile


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
