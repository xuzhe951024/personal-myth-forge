import json
from pathlib import Path

from myth_forge_api.final_acceptance_readiness import (
    build_final_acceptance_readiness_report,
)


def test_final_acceptance_readiness_missing_file_without_running_commands(
    tmp_path: Path,
) -> None:
    result = build_final_acceptance_readiness_report(repo_root=tmp_path)

    assert result.exit_code == 2
    assert result.report["kind"] == "final_acceptance_readiness_report"
    assert result.report["status"] == "missing"
    assert result.report["source_file"] == {
        "path": "services/backend/.local/final-acceptance-local.json",
        "exists": False,
    }
    assert result.report["summary"] == {
        "passed": 0,
        "blocked": 0,
        "failed": 0,
        "skipped": 0,
    }
    assert result.report["blockers"] == []
    assert result.report["operator_actions"] == [
        "run local final acceptance and write services/backend/.local/final-acceptance-local.json"
    ]
    assert result.report["safety"] == {
        "commands_run": False,
        "provider_calls": False,
        "global_mutation": False,
        "provider_secrets_in_report": False,
        "raw_media_in_report": False,
        "payment_links_in_report": False,
        "local_paths_in_report": False,
    }


def test_final_acceptance_readiness_blocks_from_saved_report_without_unsafe_text(
    tmp_path: Path,
) -> None:
    _write_final_acceptance_report(
        tmp_path,
        {
            "kind": "final_acceptance_report",
            "overall_status": "blocked",
            "summary": {"passed": 12, "blocked": 2, "failed": 0, "skipped": 0},
            "checks": [
                {"id": "provider_handoff", "label": "Provider handoff", "status": "passed"},
                {
                    "id": "mobile_deploy_preflight",
                    "label": "iOS deploy preflight",
                    "status": "blocked",
                    "classification": "blocked_by_local_ios_deploy_config",
                    "command": ["make", "mobile-deploy-preflight"],
                    "stderr_tail": f"Missing DEVELOPMENT_TEAM in {tmp_path}/repo/private /Users/zhexu/private.",
                },
                {
                    "id": "mobile_xcode_build",
                    "label": "Xcode build gate",
                    "status": "blocked",
                    "classification": "blocked_by_apple_sdk_license",
                    "command": ["make", "mobile-xcode-build"],
                    "stderr_tail": "xcodebuild license blocked sk-secret checkout_url file:///tmp/private",
                },
            ],
        },
    )

    result = build_final_acceptance_readiness_report(repo_root=tmp_path)
    report_text = json.dumps(result.report)

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert result.report["summary"] == {
        "passed": 12,
        "blocked": 2,
        "failed": 0,
        "skipped": 0,
    }
    assert result.report["blockers"] == [
        {
            "id": "mobile_deploy_preflight",
            "label": "iOS deploy preflight",
            "status": "blocked",
            "classification": "blocked_by_local_ios_deploy_config",
            "command": "make mobile-deploy-preflight",
            "detail": "Missing DEVELOPMENT_TEAM in [repo-root]/repo/private [home]/private.",
        },
        {
            "id": "mobile_xcode_build",
            "label": "Xcode build gate",
            "status": "blocked",
            "classification": "blocked_by_apple_sdk_license",
            "command": "make mobile-xcode-build",
            "detail": "xcodebuild license blocked [redacted] [redacted] [redacted]",
        },
    ]
    assert result.report["operator_actions"] == [
        "provide iOS deploy config and rerun mobile deploy preflight",
        "resolve Xcode build gate outside the app",
    ]
    assert str(tmp_path) not in report_text
    assert "/Users/" not in report_text
    assert "sk-secret" not in report_text
    assert "checkout_url" not in report_text
    assert "file:///tmp" not in report_text


def test_final_acceptance_readiness_ready_from_saved_report(tmp_path: Path) -> None:
    _write_final_acceptance_report(
        tmp_path,
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

    result = build_final_acceptance_readiness_report(repo_root=tmp_path)

    assert result.exit_code == 0
    assert result.report["status"] == "ready"
    assert result.report["summary"] == {
        "passed": 14,
        "blocked": 0,
        "failed": 0,
        "skipped": 0,
    }
    assert result.report["blockers"] == []
    assert result.report["operator_actions"] == ["final acceptance is ready"]


def test_final_acceptance_readiness_blocks_malformed_file_safely(tmp_path: Path) -> None:
    report_path = tmp_path / "services/backend/.local/final-acceptance-local.json"
    report_path.parent.mkdir(parents=True)
    report_path.write_text("{not-json sk-secret /Users/zhexu/private", encoding="utf-8")

    result = build_final_acceptance_readiness_report(repo_root=tmp_path)
    report_text = json.dumps(result.report)

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert result.report["blockers"] == [
        {
            "id": "final_acceptance_file",
            "label": "Final acceptance file",
            "status": "failed",
            "classification": "unreadable_report",
            "command": (
                "cd services/backend && uv run python -m myth_forge_api.cli "
                "final-acceptance --profile quick --provider-mode local --repo-root ../.. "
                "--output .local/final-acceptance-local.json"
            ),
            "detail": "Saved final acceptance report is not valid JSON.",
        }
    ]
    assert result.report["operator_actions"] == [
        "regenerate services/backend/.local/final-acceptance-local.json"
    ]
    assert "sk-secret" not in report_text
    assert "/Users/" not in report_text


def _write_final_acceptance_report(repo_root: Path, report: dict[str, object]) -> None:
    report_path = repo_root / "services/backend/.local/final-acceptance-local.json"
    report_path.parent.mkdir(parents=True)
    report_path.write_text(json.dumps(report), encoding="utf-8")
