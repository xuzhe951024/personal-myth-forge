import json
from pathlib import Path

import pytest

from myth_forge_api.acceptance import DemoAcceptanceResult
from myth_forge_api.config import Settings
from myth_forge_api.final_demo_launch import FinalDemoLaunchResult
from myth_forge_api.final_configured_preflight import FinalConfiguredPreflightResult
from myth_forge_api.final_configured_evidence_plan import (
    FinalConfiguredEvidencePlanResult,
)
from myth_forge_api.final_external_action_ledger import FinalExternalActionLedgerResult
from myth_forge_api.final_handoff_index import FinalHandoffIndexResult
from myth_forge_api.final_launch_closure_packet import FinalLaunchClosurePacketResult
from myth_forge_api.final_local_report_refresh import FinalLocalReportRefreshResult
from myth_forge_api.final_resource_fill_guide import FinalResourceFillGuideResult
from myth_forge_api.final_resource_apply_preview import FinalResourceApplyPreviewResult
from myth_forge_api.final_resource_requirements import FinalResourceRequirementsResult
from myth_forge_api.final_showcase_readiness import FinalShowcaseReadinessResult
from myth_forge_api.final_acceptance import FinalAcceptanceResult
from myth_forge_api.local_showcase_smoke import LocalShowcaseSmokeResult
from myth_forge_api.print_fulfillment_readiness import PrintFulfillmentReadinessResult
from myth_forge_api.resource_template_acceptance import ResourceTemplateAcceptanceResult
from myth_forge_api.cli import main
from myth_forge_api.domain.models import PrintCandidate, PrintQuote, PrintQuoteRequest
from myth_forge_api.providers.three_d import (
    LocalThreeDProvider,
    MeshyProviderError,
    ThreeDGenerationRequest,
)


def test_cli_generates_local_asset_json(capsys) -> None:
    exit_code = main(
        ["generate-asset", "--provider", "local", "--prompt", "Create a tiny moon cup."]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["provider"] == "local_stub"
    assert payload["format"] == "glb"


def test_cli_evaluate_3d_writes_report(tmp_path) -> None:
    prompts_file = tmp_path / "prompts.txt"
    output_file = tmp_path / "report.json"
    prompts_file.write_text("Create a moon cup.\nCreate a brass key.\n", encoding="utf-8")

    exit_code = main(
        [
            "evaluate-3d",
            "--provider",
            "local",
            "--prompts-file",
            str(prompts_file),
            "--output",
            str(output_file),
        ]
    )

    assert exit_code == 0
    report = json.loads(output_file.read_text(encoding="utf-8"))
    assert report["kind"] == "three_d_evaluation_report"
    assert report["suite"] == "custom-prompts"
    assert report["provider"] == "local"
    assert report["total_cases"] == 2
    assert [case["case_id"] for case in report["cases"]] == ["custom_001", "custom_002"]
    assert [case["category"] for case in report["cases"]] == [
        "custom_prompt",
        "custom_prompt",
    ]
    assert [case["status"] for case in report["cases"]] == ["succeeded", "succeeded"]
    assert all("elapsed_seconds" in case for case in report["cases"])


def test_cli_evaluate_3d_default_suite_writes_rich_report(tmp_path) -> None:
    output_file = tmp_path / "suite-report.json"

    exit_code = main(
        [
            "evaluate-3d",
            "--provider",
            "local",
            "--suite",
            "default-v0",
            "--output",
            str(output_file),
        ]
    )

    report_text = output_file.read_text(encoding="utf-8")
    report = json.loads(report_text)

    assert exit_code == 0
    assert report["kind"] == "three_d_evaluation_report"
    assert report["status"] == "succeeded"
    assert report["suite"] == "default-v0"
    assert report["provider"] == "local"
    assert report["total_cases"] == 20
    assert report["succeeded"] == 20
    assert report["failed"] == 0
    assert report["coverage"]["input_modes"]["text_prompt"] == 20
    assert report["coverage"]["variant_roles"]["game_asset"] == 20
    assert report["coverage"]["variant_roles"]["ios_scene_asset"] == 20
    assert report["coverage"]["scene_loadable_cases"] == 20
    assert len(report["review_rubric"]) == 5
    assert report["safety"]["raw_media_in_report"] is False
    assert report["safety"]["provider_secrets_in_report"] is False
    assert report["safety"]["local_paths_in_report"] is False
    first_case = report["cases"][0]
    assert first_case["case_id"]
    assert first_case["category"] == "object_description"
    assert first_case["expected_input_mode"] == "text_prompt"
    assert first_case["review_focus"]
    assert first_case["generation_provenance"]["input_mode"] == "text_prompt"
    assert first_case["generation_provenance"]["raw_sources_included"] is False
    assert first_case["variant_roles"] == ["game_asset", "ios_scene_asset"]
    assert first_case["scene_loadable_variant"] is True
    assert first_case["manual_review"] == {
        "artifact_quality": None,
        "prompt_alignment": None,
        "mobile_readiness": None,
        "printability_signal": None,
        "notes": None,
    }
    assert "data:image" not in report_text
    assert "Authorization" not in report_text


def test_cli_evaluate_3d_guided_scan_suite_writes_media_safe_report(tmp_path) -> None:
    output_file = tmp_path / "guided-scan-report.json"

    exit_code = main(
        [
            "evaluate-3d",
            "--provider",
            "local",
            "--suite",
            "guided-scan-smoke-v0",
            "--output",
            str(output_file),
        ]
    )

    report_text = output_file.read_text(encoding="utf-8")
    report = json.loads(report_text)

    assert exit_code == 0
    assert report["kind"] == "three_d_evaluation_report"
    assert report["suite"] == "guided-scan-smoke-v0"
    assert report["total_cases"] == 3
    assert report["succeeded"] == 3
    assert report["failed"] == 0
    assert report["coverage"]["input_modes"]["single_image"] == 1
    assert report["coverage"]["input_modes"]["multi_image"] == 2
    assert report["coverage"]["input_modes"]["text_prompt"] == 0
    assert [case["source_image_count"] for case in report["cases"]] == [1, 2, 4]
    assert [case["source_image_roles"] for case in report["cases"]] == [
        ["front"],
        ["front", "side"],
        ["front", "side", "top", "detail"],
    ]
    assert report["cases"][0]["generation_provenance"]["input_mode"] == "single_image"
    assert report["cases"][1]["generation_provenance"]["input_mode"] == "multi_image"
    assert report["cases"][2]["generation_provenance"]["source_image_count"] == 4
    assert report["cases"][2]["generation_provenance"]["selected_source_image_count"] == 4
    assert "data:image" not in report_text
    assert "file://" not in report_text
    assert "Authorization" not in report_text


def test_cli_evaluate_3d_guided_scan_suite_passes_source_images_to_provider(
    tmp_path,
    monkeypatch,
) -> None:
    output_file = tmp_path / "guided-scan-report.json"
    provider = RecordingThreeDProvider()
    monkeypatch.setattr("myth_forge_api.cli.build_three_d_provider", lambda settings: provider)

    exit_code = main(
        [
            "evaluate-3d",
            "--provider",
            "local",
            "--suite",
            "guided-scan-smoke-v0",
            "--output",
            str(output_file),
        ]
    )

    assert exit_code == 0
    assert [len(request.source_images) for request in provider.requests] == [1, 2, 4]
    assert provider.requests[0].source_images[0].content_type == "image/png"
    assert provider.requests[0].source_images[0].data_uri.startswith("data:image/png;base64,")
    report_text = output_file.read_text(encoding="utf-8")
    assert "data:image" not in report_text


def test_cli_evaluate_3d_requires_suite_or_prompts_file(tmp_path) -> None:
    output_file = tmp_path / "report.json"

    with pytest.raises(SystemExit):
        main(["evaluate-3d", "--provider", "local", "--output", str(output_file)])


def test_cli_evaluate_3d_rejects_suite_and_prompts_file_together(tmp_path) -> None:
    prompts_file = tmp_path / "prompts.txt"
    output_file = tmp_path / "report.json"
    prompts_file.write_text("Create a moon cup.\n", encoding="utf-8")

    with pytest.raises(SystemExit):
        main(
            [
                "evaluate-3d",
                "--provider",
                "local",
                "--suite",
                "default-v0",
                "--prompts-file",
                str(prompts_file),
                "--output",
                str(output_file),
            ]
        )


def test_cli_evaluate_3d_returns_error_without_report_when_provider_config_fails(
    tmp_path,
    monkeypatch,
) -> None:
    prompts_file = tmp_path / "prompts.txt"
    output_file = tmp_path / "report.json"
    prompts_file.write_text("Create a moon cup.\n", encoding="utf-8")

    def raise_provider_error(settings):
        raise MeshyProviderError("MESHY_API_KEY is required.")

    monkeypatch.setattr("myth_forge_api.cli.build_three_d_provider", raise_provider_error)

    exit_code = main(
        [
            "evaluate-3d",
            "--provider",
            "meshy",
            "--prompts-file",
            str(prompts_file),
            "--output",
            str(output_file),
        ]
    )

    assert exit_code == 1
    assert not output_file.exists()


def test_cli_evaluate_npc_default_suite_writes_report(tmp_path) -> None:
    output_file = tmp_path / "npc-report.json"

    exit_code = main(
        [
            "evaluate-npc",
            "--provider",
            "local",
            "--suite",
            "default-v0",
            "--tick-steps",
            "2",
            "--output",
            str(output_file),
        ]
    )

    report_text = output_file.read_text(encoding="utf-8")
    report = json.loads(report_text)
    assert exit_code == 0
    assert report["kind"] == "npc_agent_evaluation_report"
    assert report["status"] == "succeeded"
    assert report["suite"] == "default-v0"
    assert report["provider"] == "local"
    assert report["tick_steps"] == 2
    assert report["total_cases"] == 6
    assert report["succeeded"] == 6
    assert report["failed"] == 0
    assert "Authorization" not in report_text
    assert "raw_email:" not in report_text


def test_cli_evaluate_npc_requires_suite(tmp_path) -> None:
    output_file = tmp_path / "npc-report.json"

    with pytest.raises(SystemExit):
        main(["evaluate-npc", "--provider", "local", "--output", str(output_file)])


def test_cli_evaluate_npc_returns_error_without_openai_key(tmp_path, monkeypatch) -> None:
    output_file = tmp_path / "npc-report.json"
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    exit_code = main(
        [
            "evaluate-npc",
            "--provider",
            "openai",
            "--suite",
            "default-v0",
            "--output",
            str(output_file),
        ]
    )

    assert exit_code == 1
    assert not output_file.exists()


class FailingThreeDProvider:
    provider_name = "failing"

    def generate_game_asset(self, request: ThreeDGenerationRequest):
        raise MeshyProviderError("failed Authorization=Bearer test-secret raw=test-secret")


class RecordingThreeDProvider:
    provider_name = "recording"

    def __init__(self) -> None:
        self.requests: list[ThreeDGenerationRequest] = []
        self.local_provider = LocalThreeDProvider()

    def generate_game_asset(self, request: ThreeDGenerationRequest):
        self.requests.append(request)
        return self.local_provider.generate_game_asset(request)


def test_cli_evaluate_3d_sanitizes_per_prompt_errors(tmp_path, monkeypatch) -> None:
    prompts_file = tmp_path / "prompts.txt"
    output_file = tmp_path / "report.json"
    prompts_file.write_text("Create a moon cup.\n", encoding="utf-8")

    monkeypatch.setattr(
        "myth_forge_api.cli.build_three_d_provider",
        lambda settings: FailingThreeDProvider(),
    )

    exit_code = main(
        [
            "evaluate-3d",
            "--provider",
            "local",
            "--prompts-file",
            str(prompts_file),
            "--output",
            str(output_file),
        ]
    )

    report_text = output_file.read_text(encoding="utf-8")
    report = json.loads(report_text)

    assert exit_code == 0
    assert report["status"] == "failed"
    assert report["cases"][0]["status"] == "failed"
    assert report["cases"][0]["error"] == "failed [redacted] [redacted]"
    assert "test-secret" not in report_text
    assert "Authorization" not in report_text
    assert "raw=" not in report_text
    assert "data:image" not in report_text
    assert "file://" not in report_text


def test_cli_provider_handoff_writes_local_report(tmp_path, monkeypatch) -> None:
    output_file = tmp_path / "handoff.json"
    monkeypatch.setattr("myth_forge_api.cli.load_settings", lambda: Settings())

    exit_code = main(["provider-handoff", "--output", str(output_file)])

    assert exit_code == 0
    report = json.loads(output_file.read_text(encoding="utf-8"))
    assert report["kind"] == "provider_handoff_report"
    assert report["mode"] == "configuration"
    assert report["status"] == "blocked"
    assert report["classification"] == "core_real_providers_not_ready"
    assert report["summary"]["providers"] >= 4
    assert report["summary"]["core_real_ready"] == 1
    assert report["summary"]["core_total"] == 3
    assert report["overall_demo_ready"] is True
    assert report["overall_real_ready"] is False
    assert report["core_real_ready"] is False
    assert report["core_provider_kinds"] == ["three_d", "npc", "capture_storage"]
    assert report["missing_env"] == []
    assert "MESHY_API_KEY" in report["backend_only_env"]
    assert "OPENAI_API_KEY" in report["backend_only_env"]
    assert "Provider secrets stay on the backend" in report["mobile_secret_policy"]
    assert report["next_commands"][0] == "make final-resource-apply-preview"
    assert report["next_commands"].index("make final-resource-apply-preview") < (
        report["next_commands"].index("make final-apply-resources")
    )
    assert "make final-apply-resources" in report["next_commands"]
    assert any("provider-readiness" in command for command in report["next_commands"])
    assert all("/tmp/" not in command for command in report["next_commands"])
    assert report["first_blocker"]["id"] == "three_d_provider"
    assert report["first_blocker"]["command"] == "make final-resource-apply-preview"
    assert report["first_blocker"]["resources_file"] == (
        "services/backend/.local/final-resources.env"
    )
    assert report["first_blocker"]["apply_command"] == "make final-apply-resources"
    assert report["first_blocker"]["handoff_command"] == "make provider-handoff"
    assert report["next_action"]["source"] == "first_blocker"
    assert report["operator_actions"] == [
        "make final-resource-apply-preview",
        (
            "provide MESHY_API_KEY in final-resources.env; "
            "rerun make final-resources-preflight"
        ),
        (
            "provide OPENAI_API_KEY in final-resources.env; "
            "rerun make final-resources-preflight"
        ),
        "make provider-handoff",
    ]
    assert report["safety"]["provider_calls"] is False


def test_cli_provider_handoff_require_core_real_returns_two_when_keys_missing(
    tmp_path,
    monkeypatch,
) -> None:
    output_file = tmp_path / "handoff.json"
    monkeypatch.setattr(
        "myth_forge_api.cli.load_settings",
        lambda: Settings(three_d_provider="meshy", npc_provider="openai"),
    )

    exit_code = main(["provider-handoff", "--require-core-real", "--output", str(output_file)])

    report_text = output_file.read_text(encoding="utf-8")
    report = json.loads(report_text)
    assert exit_code == 2
    assert report["core_real_ready"] is False
    assert report["missing_env"] == ["MESHY_API_KEY", "OPENAI_API_KEY"]
    assert report["first_blocker"]["resources_file"] == (
        "services/backend/.local/final-resources.env"
    )
    assert report["operator_actions"] == [
        "make final-resource-apply-preview",
        (
            "provide MESHY_API_KEY in final-resources.env; "
            "rerun make final-resources-preflight"
        ),
        (
            "provide OPENAI_API_KEY in final-resources.env; "
            "rerun make final-resources-preflight"
        ),
        "make provider-handoff",
    ]
    assert "provide MESHY_API_KEY in final-resources.env" not in report[
        "operator_actions"
    ]
    assert "provide OPENAI_API_KEY in final-resources.env" not in report[
        "operator_actions"
    ]
    assert "sk-" not in report_text


def test_cli_provider_handoff_core_real_ready_with_keys_without_secret_leak(
    tmp_path,
    monkeypatch,
) -> None:
    output_file = tmp_path / "handoff.json"
    monkeypatch.setattr(
        "myth_forge_api.cli.load_settings",
        lambda: Settings(
            three_d_provider="meshy",
            meshy_api_key="sk-meshy-secret",
            npc_provider="openai",
            openai_api_key="sk-openai-secret",
        ),
    )

    exit_code = main(["provider-handoff", "--require-core-real", "--output", str(output_file)])

    report_text = output_file.read_text(encoding="utf-8")
    report = json.loads(report_text)
    assert exit_code == 0
    assert report["status"] == "ready"
    assert report["classification"] == "core_real_providers_ready"
    assert report["summary"]["core_real_ready"] == 3
    assert report["summary"]["core_total"] == 3
    assert report["core_real_ready"] is True
    assert report["overall_real_ready"] is False
    assert report["missing_env"] == []
    assert "sk-meshy-secret" not in report_text
    assert "sk-openai-secret" not in report_text


def test_cli_provider_handoff_prints_json_to_stdout(capsys, monkeypatch) -> None:
    monkeypatch.setattr("myth_forge_api.cli.load_settings", lambda: Settings())

    exit_code = main(["provider-handoff"])

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["kind"] == "provider_handoff_report"


def test_makefile_exposes_provider_handoff_target() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    text = (repo_root / "Makefile").read_text(encoding="utf-8")
    wrapper = (
        repo_root / "services/backend/scripts/write_provider_handoff.sh"
    ).read_text(encoding="utf-8")

    assert "provider-handoff:" in text
    assert "services/backend/scripts/write_provider_handoff.sh" in text
    assert "myth_forge_api.cli provider-handoff" in wrapper
    assert "--require-core-real" in wrapper
    assert ".local/provider-handoff.json" in wrapper


def test_cli_resource_handoff_writes_report(tmp_path, monkeypatch) -> None:
    output_file = tmp_path / "resource-handoff.json"
    calls = []

    def fake_report(*, repo_root=None):
        calls.append(repo_root)
        return {
            "kind": "resource_handoff_report",
            "overall_status": "blocked",
            "summary": {
                "ready": 1,
                "missing": 1,
                "blocked": 0,
                "manual": 0,
                "optional": 0,
            },
            "backend": {"items": []},
            "ios": {"items": []},
            "operator_actions": [],
            "commands": [],
            "safety": {
                "provider_secrets_in_report": False,
                "local_paths_in_report": False,
            },
        }

    monkeypatch.setattr("myth_forge_api.cli.build_resource_handoff_report", fake_report)

    exit_code = main(
        [
            "resource-handoff",
            "--repo-root",
            str(tmp_path),
            "--output",
            str(output_file),
        ]
    )

    report = json.loads(output_file.read_text(encoding="utf-8"))
    assert exit_code == 2
    assert report["kind"] == "resource_handoff_report"
    assert report["overall_status"] == "blocked"
    assert calls == [tmp_path]


def test_cli_resource_handoff_prints_stdout_when_ready(capsys, monkeypatch) -> None:
    monkeypatch.setattr(
        "myth_forge_api.cli.build_resource_handoff_report",
        lambda repo_root=None: {
            "kind": "resource_handoff_report",
            "overall_status": "ready",
            "summary": {
                "ready": 2,
                "missing": 0,
                "blocked": 0,
                "manual": 0,
                "optional": 0,
            },
            "backend": {"items": []},
            "ios": {"items": []},
            "operator_actions": [],
            "commands": [],
            "safety": {
                "provider_secrets_in_report": False,
                "local_paths_in_report": False,
            },
        },
    )

    exit_code = main(["resource-handoff"])

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["kind"] == "resource_handoff_report"
    assert payload["overall_status"] == "ready"


def test_cli_final_resources_preflight_writes_ready_report(tmp_path) -> None:
    repo_root = tmp_path / "repo"
    resources = repo_root / "services/backend/.local/final-resources.env"
    output_file = tmp_path / "final-resources-preflight.json"
    resources.parent.mkdir(parents=True)
    resources.write_text(
        "\n".join(
            [
                "MESHY_API_KEY=meshy-secret-test",
                "OPENAI_API_KEY=sk-openai-test",
                "PRINT_PROVIDER=local",
                "DEVELOPMENT_TEAM=ABCDE12345",
                    "PRODUCT_BUNDLE_IDENTIFIER=com.zhexu.personalmythforge.dev",
                    "PMF_BACKEND_BASE_URL=http://10.0.0.24:8080",
            ]
        ),
        encoding="utf-8",
    )

    exit_code = main(
        [
            "final-resources-preflight",
            "--repo-root",
            str(repo_root),
            "--resources-file",
            str(resources),
            "--output",
            str(output_file),
        ]
    )

    report_text = output_file.read_text(encoding="utf-8")
    report = json.loads(report_text)
    assert exit_code == 0
    assert report["kind"] == "final_resources_preflight_report"
    assert report["status"] == "ready"
    assert report["first_blocker"] is None
    assert report["next_action"] is None
    assert report["resources_file"]["path"] == "services/backend/.local/final-resources.env"
    assert "meshy-secret-test" not in report_text
    assert "sk-openai-test" not in report_text
    assert str(tmp_path) not in report_text


def test_cli_final_resource_repair_preview_writes_report(tmp_path) -> None:
    repo_root = tmp_path / "repo"
    resources = repo_root / "services/backend/.local/final-resources.env"
    output_file = tmp_path / "final-resource-repair-preview.json"
    resources.parent.mkdir(parents=True)
    resources.write_text(
        "\n".join(
            [
                "MESHY_API_KEY=meshy-secret-test",
                "PRODUCT_BUNDLE_IDENTIFIER=com.example.personalmythforge",
                "PMF_BACKEND_BASE_URL=http://192.168.1.10:8080",
                "",
            ]
        ),
        encoding="utf-8",
    )

    exit_code = main(
        [
            "final-resource-repair-preview",
            "--repo-root",
            str(repo_root),
            "--output",
            str(output_file),
        ]
    )

    report_text = output_file.read_text(encoding="utf-8")
    report = json.loads(report_text)
    repairs = {repair["id"]: repair for repair in report["repairs"]}

    assert exit_code == 2
    assert report["kind"] == "final_resource_repair_report"
    assert report["status"] == "repairable"
    assert repairs["PRODUCT_BUNDLE_IDENTIFIER"]["action"] == "clear_value"
    assert repairs["PMF_BACKEND_BASE_URL"]["action"] == "clear_value"
    assert "meshy-secret-test" not in report_text
    assert "192.168.1.10" not in report_text
    assert str(tmp_path) not in report_text


def test_cli_final_resource_repair_applies_safe_placeholder_cleanup(tmp_path) -> None:
    repo_root = tmp_path / "repo"
    resources = repo_root / "services/backend/.local/final-resources.env"
    output_file = tmp_path / "final-resource-repair.json"
    resources.parent.mkdir(parents=True)
    resources.write_text(
        "\n".join(
            [
                "MESHY_API_KEY=meshy-secret-test",
                "PRODUCT_BUNDLE_IDENTIFIER=com.example.personalmythforge",
                "PMF_BACKEND_BASE_URL=http://192.168.1.10:8080",
                "",
            ]
        ),
        encoding="utf-8",
    )

    exit_code = main(
        [
            "final-resource-repair",
            "--repo-root",
            str(repo_root),
            "--output",
            str(output_file),
        ]
    )

    report_text = output_file.read_text(encoding="utf-8")
    report = json.loads(report_text)
    repaired_text = resources.read_text(encoding="utf-8")

    assert exit_code == 0
    assert report["status"] == "repaired"
    assert report["summary"] == {"repaired": 2}
    assert "MESHY_API_KEY=meshy-secret-test" in repaired_text
    assert "PRODUCT_BUNDLE_IDENTIFIER=\n" in repaired_text
    assert "PMF_BACKEND_BASE_URL=\n" in repaired_text
    assert "meshy-secret-test" not in report_text
    assert "192.168.1.10" not in report_text


def test_cli_final_resources_preflight_returns_two_when_missing(
    tmp_path,
    capsys,
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    exit_code = main(["final-resources-preflight", "--repo-root", str(repo_root)])

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 2
    assert payload["kind"] == "final_resources_preflight_report"
    assert payload["status"] == "missing"
    assert payload["first_blocker"]["id"] == "final_resources_file"
    assert payload["next_action"]["source"] == "first_blocker"
    assert str(tmp_path) not in json.dumps(payload)


def test_cli_final_resource_requirements_writes_report_and_returns_result_code(
    tmp_path,
    monkeypatch,
) -> None:
    output_file = tmp_path / "final-resource-requirements.json"
    calls = []

    def fake_build_final_resource_requirements_report(**kwargs):
        calls.append(kwargs)
        return FinalResourceRequirementsResult(
            exit_code=2,
            report={
                "kind": "final_resource_requirements_report",
                "status": "blocked",
                "summary": {"ready": 0, "missing": 5, "blocked": 0},
                "requirements": [],
                "requirements_by_id": {},
                "operator_actions": ["provide MESHY_API_KEY in final-resources.env"],
                "validation_commands": ["make final-resource-requirements"],
                "safety": {"provider_secrets_in_report": False},
            },
        )

    monkeypatch.setattr(
        "myth_forge_api.cli.build_final_resource_requirements_report",
        fake_build_final_resource_requirements_report,
    )

    exit_code = main(
        [
            "final-resource-requirements",
            "--repo-root",
            str(tmp_path),
            "--output",
            str(output_file),
        ]
    )

    report = json.loads(output_file.read_text(encoding="utf-8"))
    assert exit_code == 2
    assert calls == [{"repo_root": tmp_path}]
    assert report["kind"] == "final_resource_requirements_report"
    assert report["status"] == "blocked"


def test_cli_final_resource_apply_preview_writes_report_and_returns_result_code(
    tmp_path,
    monkeypatch,
) -> None:
    output_file = tmp_path / "final-resource-apply-preview.json"
    calls = []

    def fake_build_final_resource_apply_preview_report(**kwargs):
        calls.append(kwargs)
        return FinalResourceApplyPreviewResult(
            exit_code=2,
            report={
                "kind": "final_resource_apply_preview_report",
                "status": "blocked",
                "summary": {"ready": 0, "missing": 5, "blocked": 1},
                "write_targets": [],
                "write_targets_by_id": {},
                "operator_actions": ["set PMF_BACKEND_BASE_URL to a LAN URL"],
                "commands": ["make final-resource-apply-preview"],
                "safety": {"writes_backend_env": False},
            },
        )

    monkeypatch.setattr(
        "myth_forge_api.cli.build_final_resource_apply_preview_report",
        fake_build_final_resource_apply_preview_report,
    )

    exit_code = main(
        [
            "final-resource-apply-preview",
            "--repo-root",
            str(tmp_path),
            "--output",
            str(output_file),
        ]
    )

    report = json.loads(output_file.read_text(encoding="utf-8"))
    assert exit_code == 2
    assert calls == [{"repo_root": tmp_path}]
    assert report["kind"] == "final_resource_apply_preview_report"
    assert report["status"] == "blocked"


def test_cli_final_external_action_ledger_writes_report_and_returns_result_code(
    tmp_path,
    monkeypatch,
) -> None:
    output_file = tmp_path / "final-external-action-ledger.json"
    calls = []

    def fake_build_final_external_action_ledger_report(**kwargs):
        calls.append(kwargs)
        return FinalExternalActionLedgerResult(
            exit_code=2,
            report={
                "kind": "final_external_action_ledger_report",
                "status": "blocked",
                "summary": {"groups": 5, "actions": 16, "blocked": 3},
                "action_groups": [],
                "actions_by_id": {},
                "operator_sequence": ["make final-resource-requirements"],
                "safety": {"commands_run": False, "global_mutation": False},
            },
        )

    monkeypatch.setattr(
        "myth_forge_api.cli.build_final_external_action_ledger_report",
        fake_build_final_external_action_ledger_report,
    )

    exit_code = main(
        [
            "final-external-action-ledger",
            "--repo-root",
            str(tmp_path),
            "--output",
            str(output_file),
        ]
    )

    report = json.loads(output_file.read_text(encoding="utf-8"))
    assert exit_code == 2
    assert calls == [{"repo_root": tmp_path}]
    assert report["kind"] == "final_external_action_ledger_report"
    assert report["status"] == "blocked"


def test_cli_final_launch_closure_packet_writes_report_and_returns_result_code(
    tmp_path,
    monkeypatch,
) -> None:
    output_file = tmp_path / "final-launch-closure-packet.json"
    calls = []

    def fake_build_final_launch_closure_packet_report(**kwargs):
        calls.append(kwargs)
        return FinalLaunchClosurePacketResult(
            exit_code=2,
            report={
                "kind": "final_launch_closure_packet_report",
                "status": "blocked",
                "summary": {"sections": 5, "blocked": 3},
                "sections": [],
                "sections_by_id": {},
                "operator_actions": ["provide MESHY_API_KEY"],
                "safety": {"commands_run": False, "global_mutation": False},
            },
        )

    monkeypatch.setattr(
        "myth_forge_api.cli.build_final_launch_closure_packet_report",
        fake_build_final_launch_closure_packet_report,
    )

    exit_code = main(
        [
            "final-launch-closure-packet",
            "--repo-root",
            str(tmp_path),
            "--output",
            str(output_file),
        ]
    )

    report = json.loads(output_file.read_text(encoding="utf-8"))
    assert exit_code == 2
    assert calls == [{"repo_root": tmp_path}]
    assert report["kind"] == "final_launch_closure_packet_report"
    assert report["status"] == "blocked"


def test_cli_local_showcase_smoke_writes_report(tmp_path, monkeypatch) -> None:
    output_file = tmp_path / "local-showcase-smoke.json"
    calls = []

    def fake_build_local_showcase_smoke_report(**kwargs):
        calls.append(kwargs)
        return LocalShowcaseSmokeResult(
            exit_code=0,
            report={
                "kind": "local_showcase_smoke_report",
                "status": "succeeded",
                "summary": {"passed": 10, "failed": 0, "http_steps": 6},
                "steps": [],
                "safety": {"provider_calls": False},
            },
        )

    monkeypatch.setattr(
        "myth_forge_api.cli.build_local_showcase_smoke_report",
        fake_build_local_showcase_smoke_report,
    )

    exit_code = main(["local-showcase-smoke", "--output", str(output_file)])

    report = json.loads(output_file.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert calls == [{}]
    assert report["kind"] == "local_showcase_smoke_report"
    assert report["summary"]["http_steps"] == 6


def test_cli_final_local_report_refresh_writes_report(
    tmp_path,
    monkeypatch,
) -> None:
    output_file = tmp_path / "final-local-report-refresh.json"
    calls = []

    def fake_run_final_local_report_refresh(**kwargs):
        calls.append(kwargs)
        return FinalLocalReportRefreshResult(
            exit_code=2,
            report={
                "kind": "final_local_report_refresh_report",
                "status": "blocked",
                "summary": {"steps": 17, "ready": 3, "blocked": 14, "failed": 0},
                "steps": [
                    {
                        "id": "final_showcase_readiness",
                        "status": "blocked",
                        "output": "services/backend/.local/final-showcase-readiness.json",
                    }
                ],
                "safety": {
                    "live_provider_calls": False,
                    "global_mutation": False,
                    "xcode_or_signing": False,
                },
            },
        )

    monkeypatch.setattr(
        "myth_forge_api.cli.run_final_local_report_refresh",
        fake_run_final_local_report_refresh,
    )

    exit_code = main(
        [
            "final-local-report-refresh",
            "--repo-root",
            str(tmp_path),
            "--output",
            str(output_file),
        ]
    )

    report = json.loads(output_file.read_text(encoding="utf-8"))
    assert exit_code == 2
    assert calls == [{"repo_root": tmp_path}]
    assert report["kind"] == "final_local_report_refresh_report"
    assert report["status"] == "blocked"
    assert report["safety"]["live_provider_calls"] is False
    assert report["steps"][0]["id"] == "final_showcase_readiness"


def test_cli_final_resource_fill_guide_writes_json_and_markdown(
    tmp_path,
    monkeypatch,
) -> None:
    output_file = tmp_path / "final-resource-fill-guide.json"
    markdown_file = tmp_path / "final-resource-fill-guide.md"
    calls = []

    def fake_build_final_resource_fill_guide_report(**kwargs):
        calls.append(kwargs)
        return FinalResourceFillGuideResult(
            exit_code=2,
            report={
                "kind": "final_resource_fill_guide_report",
                "status": "blocked",
                "summary": {"required_inputs": 1},
                "required_inputs": [{"id": "MESHY_API_KEY"}],
                "markdown": "# Final Resource Fill Guide\n\n- `MESHY_API_KEY`",
                "safety": {"provider_secrets_in_report": False},
            },
        )

    monkeypatch.setattr(
        "myth_forge_api.cli.build_final_resource_fill_guide_report",
        fake_build_final_resource_fill_guide_report,
    )

    exit_code = main(
        [
            "final-resource-fill-guide",
            "--repo-root",
            str(tmp_path),
            "--output",
            str(output_file),
            "--markdown-output",
            str(markdown_file),
        ]
    )

    report = json.loads(output_file.read_text(encoding="utf-8"))
    assert exit_code == 2
    assert calls == [{"repo_root": tmp_path}]
    assert report["kind"] == "final_resource_fill_guide_report"
    assert report["status"] == "blocked"
    assert markdown_file.read_text(encoding="utf-8").startswith(
        "# Final Resource Fill Guide"
    )


def test_cli_final_configured_evidence_plan_writes_report(
    tmp_path,
    monkeypatch,
) -> None:
    output_file = tmp_path / "final-configured-evidence-plan.json"
    calls = []

    def fake_build_final_configured_evidence_plan_report(**kwargs):
        calls.append(kwargs)
        return FinalConfiguredEvidencePlanResult(
            exit_code=2,
            report={
                "kind": "final_configured_evidence_plan_report",
                "status": "consent_required",
                "summary": {"steps": 10, "consent_required": 3},
                "safety": {
                    "commands_run": False,
                    "live_provider_calls": False,
                },
            },
        )

    monkeypatch.setattr(
        "myth_forge_api.cli.build_final_configured_evidence_plan_report",
        fake_build_final_configured_evidence_plan_report,
    )

    exit_code = main(
        [
            "final-configured-evidence-plan",
            "--repo-root",
            str(tmp_path),
            "--output",
            str(output_file),
            "--allow-live-provider-calls",
        ]
    )

    report = json.loads(output_file.read_text(encoding="utf-8"))
    assert exit_code == 2
    assert calls == [
        {
            "repo_root": tmp_path,
            "allow_live_provider_calls": True,
        }
    ]
    assert report["kind"] == "final_configured_evidence_plan_report"
    assert report["status"] == "consent_required"
    assert report["safety"]["commands_run"] is False


def test_cli_resource_template_acceptance_writes_report(tmp_path, monkeypatch) -> None:
    output_file = tmp_path / "resource-template-acceptance.json"
    calls = []

    def fake_run_resource_template_acceptance(*, repo_root=None):
        calls.append(repo_root)
        return ResourceTemplateAcceptanceResult(
            exit_code=1,
            report={
                "kind": "resource_template_acceptance_report",
                "status": "failed",
                "summary": {"passed": 6, "failed": 1},
            },
        )

    monkeypatch.setattr(
        "myth_forge_api.cli.run_resource_template_acceptance",
        fake_run_resource_template_acceptance,
    )

    exit_code = main(
        [
            "resource-template-acceptance",
            "--repo-root",
            str(tmp_path),
            "--output",
            str(output_file),
        ]
    )

    report = json.loads(output_file.read_text(encoding="utf-8"))
    assert exit_code == 1
    assert calls == [tmp_path]
    assert report["kind"] == "resource_template_acceptance_report"
    assert report["status"] == "failed"


def test_cli_resource_template_acceptance_prints_stdout_when_ready(
    capsys,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "myth_forge_api.cli.run_resource_template_acceptance",
        lambda repo_root=None: ResourceTemplateAcceptanceResult(
            exit_code=0,
            report={
                "kind": "resource_template_acceptance_report",
                "status": "succeeded",
                "summary": {"passed": 7, "failed": 0},
            },
        ),
    )

    exit_code = main(["resource-template-acceptance"])

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["kind"] == "resource_template_acceptance_report"
    assert payload["status"] == "succeeded"


def test_cli_final_demo_launch_writes_report_and_returns_result_code(
    tmp_path,
    monkeypatch,
) -> None:
    output_file = tmp_path / "final-demo-launch.json"
    calls = []

    def fake_build_final_demo_launch_report(**kwargs):
        calls.append(kwargs)
        return FinalDemoLaunchResult(
            exit_code=0,
            report={
                "kind": "final_demo_launch_report",
                "mode": kwargs["mode"],
                "overall_status": "partial",
            },
        )

    monkeypatch.setattr(
        "myth_forge_api.cli.build_final_demo_launch_report",
        fake_build_final_demo_launch_report,
    )

    exit_code = main(
        [
            "final-demo-launch",
            "--mode",
            "local",
            "--repo-root",
            str(tmp_path),
            "--output",
            str(output_file),
        ]
    )

    report = json.loads(output_file.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert calls == [
        {
            "mode": "local",
            "repo_root": tmp_path,
        }
    ]
    assert report["kind"] == "final_demo_launch_report"
    assert report["mode"] == "local"


def test_cli_final_configured_preflight_writes_report_and_returns_result_code(
    tmp_path,
    monkeypatch,
) -> None:
    output_file = tmp_path / "final-configured-preflight.json"
    calls = []

    def fake_build_final_configured_preflight_report(**kwargs):
        calls.append(kwargs)
        return FinalConfiguredPreflightResult(
            exit_code=2,
            report={
                "kind": "final_configured_preflight_report",
                "status": "blocked",
            },
        )

    monkeypatch.setattr(
        "myth_forge_api.cli.build_final_configured_preflight_report",
        fake_build_final_configured_preflight_report,
    )

    exit_code = main(
        [
            "final-configured-preflight",
            "--repo-root",
            str(tmp_path),
            "--output",
            str(output_file),
        ]
    )

    report = json.loads(output_file.read_text(encoding="utf-8"))
    assert exit_code == 2
    assert calls == [{"repo_root": tmp_path}]
    assert report["kind"] == "final_configured_preflight_report"
    assert report["status"] == "blocked"


def test_cli_final_handoff_index_writes_report_and_returns_result_code(
    tmp_path,
    monkeypatch,
) -> None:
    output_file = tmp_path / "final-handoff-index.json"
    calls = []

    def fake_build_final_handoff_index_report(**kwargs):
        calls.append(kwargs)
        return FinalHandoffIndexResult(
            exit_code=2,
            report={
                "kind": "final_handoff_index_report",
                "status": "blocked",
            },
        )

    monkeypatch.setattr(
        "myth_forge_api.cli.build_final_handoff_index_report",
        fake_build_final_handoff_index_report,
    )

    exit_code = main(
        [
            "final-handoff-index",
            "--repo-root",
            str(tmp_path),
            "--output",
            str(output_file),
        ]
    )

    report = json.loads(output_file.read_text(encoding="utf-8"))
    assert exit_code == 2
    assert calls == [{"repo_root": tmp_path}]
    assert report["kind"] == "final_handoff_index_report"
    assert report["status"] == "blocked"


def test_cli_final_showcase_readiness_writes_report_and_returns_result_code(
    tmp_path,
    monkeypatch,
) -> None:
    output_file = tmp_path / "final-showcase-readiness.json"
    calls = []

    def fake_build_final_showcase_readiness_report(**kwargs):
        calls.append(kwargs)
        return FinalShowcaseReadinessResult(
            exit_code=2,
            report={
                "kind": "final_showcase_readiness_report",
                "status": "blocked",
                "summary": {"ready": 0, "partial": 0, "blocked": 1},
                "capabilities": [],
                "operator_actions": ["run make final-rehearsal-local"],
                "commands": ["make final-showcase-readiness"],
                "safety": {"commands_run": False},
            },
        )

    monkeypatch.setattr(
        "myth_forge_api.cli.build_final_showcase_readiness_report",
        fake_build_final_showcase_readiness_report,
    )

    exit_code = main(
        [
            "final-showcase-readiness",
            "--repo-root",
            str(tmp_path),
            "--output",
            str(output_file),
        ]
    )

    report = json.loads(output_file.read_text(encoding="utf-8"))
    assert exit_code == 2
    assert calls == [{"repo_root": tmp_path}]
    assert report["kind"] == "final_showcase_readiness_report"
    assert report["status"] == "blocked"


def test_cli_print_fulfillment_readiness_writes_report_and_returns_result_code(
    tmp_path,
    monkeypatch,
) -> None:
    output_file = tmp_path / "print-fulfillment-readiness.json"
    calls = []

    def fake_build_print_fulfillment_readiness_report(**kwargs):
        calls.append(kwargs)
        return PrintFulfillmentReadinessResult(
            exit_code=2,
            report={
                "kind": "print_fulfillment_readiness_report",
                "status": "partial",
                "summary": {"ready": 4, "partial": 1, "blocked": 0},
                "checks": [],
                "operator_actions": ["save configured Treatstock quote evidence"],
                "commands": ["make print-fulfillment-readiness"],
                "safety": {"commands_run": False},
            },
        )

    monkeypatch.setattr(
        "myth_forge_api.cli.build_print_fulfillment_readiness_report",
        fake_build_print_fulfillment_readiness_report,
    )

    exit_code = main(
        [
            "print-fulfillment-readiness",
            "--repo-root",
            str(tmp_path),
            "--output",
            str(output_file),
        ]
    )

    report = json.loads(output_file.read_text(encoding="utf-8"))
    assert exit_code == 2
    assert calls == [{"repo_root": tmp_path}]
    assert report["kind"] == "print_fulfillment_readiness_report"
    assert report["status"] == "partial"


def test_cli_print_quote_request_configured_writes_valid_request(
    tmp_path,
    monkeypatch,
) -> None:
    output_file = tmp_path / "print-quote-request-configured.json"

    def fail_provider_call(settings):
        raise AssertionError("request writer must not build a print provider")

    monkeypatch.setattr("myth_forge_api.cli.build_print_provider", fail_provider_call)

    exit_code = main(
        [
            "print-quote-request-configured",
            "--source-asset-uri",
            "https://assets.example/relic.glb",
            "--print-candidate-uri",
            "https://assets.example/relic.3mf",
            "--output",
            str(output_file),
        ]
    )

    payload = json.loads(output_file.read_text(encoding="utf-8"))
    request = PrintQuoteRequest.model_validate(payload)
    assert exit_code == 0
    assert request.print_candidate.provider == "treatstock"
    assert request.print_candidate.source_asset_uri == "https://assets.example/relic.glb"
    assert request.print_candidate.uri == "https://assets.example/relic.3mf"
    assert request.print_candidate.format == "3mf"
    assert request.print_candidate.requires_user_approval is True
    assert request.quantity == 1
    assert request.material == "standard_resin"
    assert request.finish == "matte"
    assert request.ship_to_country == "US"


def test_cli_print_quote_request_configured_rejects_non_http_candidate(
    tmp_path,
    capsys,
) -> None:
    output_file = tmp_path / "print-quote-request-configured.json"

    exit_code = main(
        [
            "print-quote-request-configured",
            "--source-asset-uri",
            "https://assets.example/relic.glb",
            "--print-candidate-uri",
            "local://print-candidates/relic.3mf",
            "--output",
            str(output_file),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "requires an http or https print candidate URI" in captured.err
    assert not output_file.exists()


def test_cli_print_quote_configured_requires_explicit_allow(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    request_file = tmp_path / "request.json"
    output_file = tmp_path / "print-quote-configured.json"
    _write_print_quote_request(request_file)

    def fail_provider_call(settings):
        raise AssertionError("print provider must not be built without explicit allow")

    monkeypatch.setattr("myth_forge_api.cli.build_print_provider", fail_provider_call)

    exit_code = main(
        [
            "print-quote-configured",
            "--request",
            str(request_file),
            "--output",
            str(output_file),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "requires --allow-print-provider-calls" in captured.err
    assert not output_file.exists()


def test_cli_print_quote_configured_writes_sanitized_treatstock_evidence(
    tmp_path,
    monkeypatch,
) -> None:
    request_file = tmp_path / "request.json"
    output_file = tmp_path / "print-quote-configured.json"
    request = _write_print_quote_request(request_file)
    calls = []

    class FakePrintProvider:
        provider_name = "treatstock"

        def create_print_quote(self, received_request: PrintQuoteRequest) -> PrintQuote:
            calls.append(received_request)
            return PrintQuote(
                kind="print_quote",
                provider="treatstock",
                status="draft_quote",
                source_asset_uri=received_request.print_candidate.source_asset_uri,
                print_candidate_uri=received_request.print_candidate.uri,
                currency="USD",
                estimated_price_cents=2400,
                estimated_production_days=0,
                estimated_shipping_days=0,
                checkout_url="https://checkout.example/order?token=secret-token",
                requires_user_approval=True,
                approval_reason=(
                    "Treatstock quote must be reviewed before checkout or order placement."
                ),
                quote_notes=[
                    "Treatstock printablePackId=12345",
                    "Bearer secret-token should be removed",
                    "checkout_url=https://checkout.example/order?token=secret-token",
                    "material=standard_resin",
                ],
            )

    monkeypatch.setattr(
        "myth_forge_api.cli.build_print_provider",
        lambda settings: FakePrintProvider(),
    )

    exit_code = main(
        [
            "print-quote-configured",
            "--allow-print-provider-calls",
            "--request",
            str(request_file),
            "--output",
            str(output_file),
        ]
    )

    payload_text = output_file.read_text(encoding="utf-8")
    payload = json.loads(payload_text)
    assert exit_code == 0
    assert calls == [request]
    assert payload["kind"] == "print_quote"
    assert payload["provider"] == "treatstock"
    assert payload["status"] == "draft_quote"
    assert payload["estimated_price_cents"] == 2400
    assert payload["requires_user_approval"] is True
    assert payload["checkout_url"] is None
    assert "checkout.example" not in payload_text
    assert "secret-token" not in payload_text
    assert "Bearer" not in payload_text
    assert "material=standard_resin" in payload["quote_notes"]


def test_cli_demo_acceptance_writes_report(tmp_path, monkeypatch) -> None:
    output_file = tmp_path / "acceptance.json"
    calls = []

    def fake_run_demo_acceptance(**kwargs):
        calls.append(kwargs)
        return DemoAcceptanceResult(
            exit_code=0,
            report={
                "kind": "demo_acceptance_report",
                "mode": kwargs["provider_mode"],
                "status": "succeeded",
            },
        )

    monkeypatch.setattr("myth_forge_api.cli.run_demo_acceptance", fake_run_demo_acceptance)

    exit_code = main(
        [
            "demo-acceptance",
            "--provider-mode",
            "local",
            "--npc-steps",
            "3",
            "--output",
            str(output_file),
        ]
    )

    assert exit_code == 0
    assert calls == [
        {
            "provider_mode": "local",
            "npc_steps": 3,
            "require_real_core": False,
            "allow_live_provider_calls": False,
        }
    ]
    assert json.loads(output_file.read_text(encoding="utf-8"))["kind"] == (
        "demo_acceptance_report"
    )


def test_cli_demo_acceptance_passes_live_provider_consent_flag(
    tmp_path,
    monkeypatch,
) -> None:
    output_file = tmp_path / "acceptance.json"
    calls = []

    def fake_run_demo_acceptance(**kwargs):
        calls.append(kwargs)
        return DemoAcceptanceResult(
            exit_code=0,
            report={
                "kind": "demo_acceptance_report",
                "mode": kwargs["provider_mode"],
                "status": "succeeded",
            },
        )

    monkeypatch.setattr("myth_forge_api.cli.run_demo_acceptance", fake_run_demo_acceptance)

    exit_code = main(
        [
            "demo-acceptance",
            "--provider-mode",
            "configured",
            "--require-real-core",
            "--allow-live-provider-calls",
            "--output",
            str(output_file),
        ]
    )

    assert exit_code == 0
    assert calls == [
        {
            "provider_mode": "configured",
            "npc_steps": 3,
            "require_real_core": True,
            "allow_live_provider_calls": True,
        }
    ]


def test_cli_demo_acceptance_prints_stdout_and_returns_result_code(capsys, monkeypatch) -> None:
    monkeypatch.setattr(
        "myth_forge_api.cli.run_demo_acceptance",
        lambda **kwargs: DemoAcceptanceResult(
            exit_code=2,
            report={
                "kind": "demo_acceptance_report",
                "mode": kwargs["provider_mode"],
                "status": "not_ready",
            },
        ),
    )

    exit_code = main(["demo-acceptance", "--provider-mode", "configured", "--require-real-core"])

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 2
    assert payload["kind"] == "demo_acceptance_report"
    assert payload["mode"] == "configured"
    assert payload["status"] == "not_ready"


@pytest.mark.parametrize("npc_steps", ["-1", "4"])
def test_cli_demo_acceptance_rejects_invalid_npc_steps(npc_steps: str) -> None:
    with pytest.raises(SystemExit):
        main(["demo-acceptance", "--npc-steps", npc_steps])


def test_cli_final_acceptance_writes_report_and_returns_result_code(
    tmp_path,
    monkeypatch,
) -> None:
    output_file = tmp_path / "final-acceptance.json"
    calls = []

    def fake_run_final_acceptance(**kwargs):
        calls.append(kwargs)
        return FinalAcceptanceResult(
            exit_code=2,
            report={
                "kind": "final_acceptance_report",
                "profile": kwargs["profile"],
                "overall_status": "blocked",
            },
        )

    monkeypatch.setattr("myth_forge_api.cli.run_final_acceptance", fake_run_final_acceptance)

    exit_code = main(
        [
            "final-acceptance",
            "--profile",
            "full",
            "--provider-mode",
            "configured",
            "--require-real-core",
            "--npc-steps",
            "2",
            "--repo-root",
            str(tmp_path),
            "--output",
            str(output_file),
        ]
    )

    assert exit_code == 2
    assert calls == [
        {
            "profile": "full",
            "provider_mode": "configured",
            "require_real_core": True,
            "npc_steps": 2,
            "repo_root": str(tmp_path),
            "allow_live_provider_calls": False,
        }
    ]
    report = json.loads(output_file.read_text(encoding="utf-8"))
    assert report["kind"] == "final_acceptance_report"
    assert report["overall_status"] == "blocked"


def test_cli_final_acceptance_prints_stdout_with_defaults(capsys, monkeypatch) -> None:
    calls = []

    def fake_run_final_acceptance(**kwargs):
        calls.append(kwargs)
        return FinalAcceptanceResult(
            exit_code=0,
            report={
                "kind": "final_acceptance_report",
                "profile": kwargs["profile"],
                "overall_status": "passed",
            },
        )

    monkeypatch.setattr("myth_forge_api.cli.run_final_acceptance", fake_run_final_acceptance)

    exit_code = main(["final-acceptance"])

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert calls == [
        {
            "profile": "quick",
            "provider_mode": "local",
            "require_real_core": False,
            "npc_steps": 3,
            "repo_root": None,
            "allow_live_provider_calls": False,
        }
    ]
    assert payload["kind"] == "final_acceptance_report"
    assert payload["overall_status"] == "passed"


def test_cli_final_acceptance_passes_live_provider_consent_flag(
    tmp_path,
    monkeypatch,
) -> None:
    calls = []

    def fake_run_final_acceptance(**kwargs):
        calls.append(kwargs)
        return FinalAcceptanceResult(
            exit_code=0,
            report={
                "kind": "final_acceptance_report",
                "profile": kwargs["profile"],
                "overall_status": "passed",
            },
        )

    monkeypatch.setattr("myth_forge_api.cli.run_final_acceptance", fake_run_final_acceptance)

    exit_code = main(
        [
            "final-acceptance",
            "--provider-mode",
            "configured",
            "--require-real-core",
            "--allow-live-provider-calls",
            "--repo-root",
            str(tmp_path),
        ]
    )

    assert exit_code == 0
    assert calls == [
        {
            "profile": "quick",
            "provider_mode": "configured",
            "require_real_core": True,
            "npc_steps": 3,
            "repo_root": str(tmp_path),
            "allow_live_provider_calls": True,
        }
    ]


def _write_print_quote_request(path: Path) -> PrintQuoteRequest:
    request = PrintQuoteRequest(
        print_candidate=PrintCandidate(
            kind="print_asset",
            source_asset_uri="https://assets.example/game.glb",
            provider="treatstock",
            format="3mf",
            uri="https://assets.example/print.3mf",
            requires_user_approval=True,
            approval_reason="Review before quote handoff.",
            printability_notes=["configured request fixture"],
        ),
        quantity=1,
        material="standard_resin",
        finish="matte",
        ship_to_country="US",
    )
    path.write_text(
        json.dumps(request.model_dump(mode="json"), indent=2),
        encoding="utf-8",
    )
    return request
