from __future__ import annotations

import json
import struct
from pathlib import Path

from myth_forge_api.cli import main
from myth_forge_api.visual_regression import (
    DEFAULT_VISUAL_ARTIFACTS,
    VisualArtifactSpec,
    check_visual_artifacts,
    png_dimensions,
)


def test_png_dimensions_reads_png_header(tmp_path: Path) -> None:
    png = tmp_path / "image.png"
    png.write_bytes(_png_header(390, 844))

    assert png_dimensions(png) == (390, 844)


def test_default_visual_artifacts_cover_full_showcase_flow() -> None:
    assert [spec.id for spec in DEFAULT_VISUAL_ARTIFACTS] == [
        "p0.12_ios_device_media_input",
        "p0.19_guided_scan_entry",
        "p0.98_capture_generation_receipt",
        "p0.103_generation_result_receipt",
        "p0.118_scene_load_proof",
        "p0.82_npc_agent_tick_summary",
        "p0.101_print_fulfillment_receipt",
        "p0.214_showcase_evidence_visual",
        "p0.100_live_provider_consent",
        "p0.112_ios_device_launch_rehearsal",
        "p0.119_visual_regression_handoff",
        "p0.153_configured_evidence_visual",
        "p0.186_configured_acceptance_command_visual",
        "p0.154_resource_fill_guide_visual",
        "p0.155_device_fill_guide_preflight",
        "p0.156_ios_device_evidence_bundle",
        "p0.157_final_launch_closure_packet",
        "p0.158_local_showcase_smoke",
        "p0.159_final_showcase_local_smoke",
        "p0.215_final_demo_launch_local_alias",
        "p0.216_final_showcase_next_action",
        "p0.217_final_resource_next_action",
        "p0.218_final_demo_launch_next_action",
        "p0.221_mobile_auto_backend_url_handoff",
        "p0.222_final_showcase_device_action_bundle",
        "p0.223_preflight_evidence_device_actions",
        "p0.160_final_showcase_ios_deploy_digest",
        "p0.189_device_blocker_handoff",
        "p0.161_final_showcase_provider_handoff_digest",
    ]
    assert all((spec.width, spec.height) == (390, 844) for spec in DEFAULT_VISUAL_ARTIFACTS)
    required_text = " ".join(
        token for spec in DEFAULT_VISUAL_ARTIFACTS for token in spec.required_text
    )
    assert "PhotosPicker" in required_text
    assert "Start Guided Scan" in required_text
    assert "Capture-to-3D" in required_text
    assert "3D Generation Result" in required_text
    assert "SceneKit load proof: Loaded" in required_text
    assert "NPC Agent tick resolved" in required_text
    assert "Print Fulfillment" in required_text
    assert "Showcase Evidence" in required_text
    assert "Showcase evidence ready" in required_text
    assert "Generation Result" in required_text
    assert "SceneKit Load" in required_text
    assert "3 saved ticks" in required_text
    assert "Local file paths and payment links are withheld." in required_text
    assert "Live Provider Consent" in required_text
    assert "iOS Device Launch Rehearsal" in required_text
    assert "Visual Regression" in required_text
    assert "Configured Evidence" in required_text
    assert "consent now 0, planned 3" in required_text
    assert "--allow-live-provider-calls" in required_text
    assert "make final-acceptance-configured" in required_text
    assert "Live providers: consent required for configured acceptance." in required_text
    assert "commands_run=false live_calls=false global=false" in required_text
    assert "Resource Fill Guide" in required_text
    assert "Fill guide blocked" in required_text
    assert "required 5, optional 5, configured 3, secret 4" in required_text
    assert "MESHY_API_KEY" in required_text
    assert "Safety: writes=false live_calls=false global_mutation=false" in required_text
    assert "Device Preflight" in required_text
    assert "Fill Guide" in required_text
    assert "Provider keys stay backend-only" in required_text
    assert "Device Evidence" in required_text
    assert "iOS device evidence blocked" in required_text
    assert "mobile_deploy_preflight" in required_text
    assert "make mobile-deploy-preflight" in required_text
    assert "Preflight Evidence" in required_text
    assert "make mobile-deploy-preflight-evidence" in required_text
    assert "evidence ready" in required_text
    assert "Safety: commands_run=false xcode=false global=false" in required_text
    assert "Closure Packet" in required_text
    assert "Final closure blocked" in required_text
    assert "first_blocker" in required_text
    assert "resource_inputs" in required_text
    assert "provide MESHY_API_KEY" in required_text
    assert "configured_evidence_bundle" in required_text
    assert "configured_live_evidence_bundle" in required_text
    assert "make configured-live-evidence-bundle" in required_text
    assert "cost consent" in required_text
    assert "commands_run=false global=false live_calls=false" in required_text
    closure_packet_spec = next(
        spec
        for spec in DEFAULT_VISUAL_ARTIFACTS
        if spec.id == "p0.157_final_launch_closure_packet"
    )
    assert "first_blocker" in closure_packet_spec.required_text
    assert "Local Smoke" in required_text
    assert "Local showcase smoke ready" in required_text
    assert "HTTP 6" in required_text
    assert "NPC ticks 2" in required_text
    assert "downloads 3" in required_text
    assert "provider_calls=false global=false temp_storage=true" in required_text
    assert "Final Showcase" in required_text
    assert "Local smoke ready" in required_text
    assert "Final Demo Launch" in required_text
    assert "Local command ready" in required_text
    assert "make final-demo-launch-local" in required_text
    assert "final-demo-launch-local.json" in required_text
    assert "No providers, Xcode, signing, or global mutation." in required_text
    assert "Next action" in required_text
    assert "ios_deployable blocked" in required_text
    assert "first_blocker" in required_text
    assert "Resource Requirements" in required_text
    assert "Next input" in required_text
    assert "MESHY_API_KEY missing" in required_text
    assert "provide MESHY_API_KEY in final-resources.env" in required_text
    assert "services/backend/.local/final-resources.env" in required_text
    assert "make final-resources-preflight" in required_text
    assert "apply_final_resources blocked" in required_text
    assert "make final-apply-resources" in required_text
    assert "one-file backend and iOS final demo handoff" in required_text
    assert "No provider calls, writes, Xcode, signing, or global mutation." in required_text
    assert "Auto Backend URL" in required_text
    assert "PMF_BACKEND_BASE_URL" in required_text
    assert "apply_time_auto" in required_text
    assert "write_deploy_local_config.sh" in required_text
    assert "final-apply-resources" in required_text
    assert "Device Actions" in required_text
    assert "make backend-device-demo" in required_text
    assert "make ios-device-launch-rehearsal" in required_text
    assert "commands_run=false" in required_text
    assert "iOS Deploy" in required_text
    assert "iOS deploy blocked" in required_text
    assert "make ios-device-launch-rehearsal" in required_text
    assert "Device Blocker Handoff" in required_text
    assert "first_blocker" in required_text
    assert "local_rehearsal" in required_text
    assert "make mobile-deploy-preflight-evidence" in required_text
    assert "make mobile-xcode-build-evidence" in required_text
    assert "Provider Handoff" in required_text
    assert "provider handoff blocked" in required_text
    assert "provide MESHY_API_KEY" in required_text


def test_visual_regression_default_passes_checked_in_showcase_artifacts() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    result = check_visual_artifacts(repo_root)

    assert result.exit_code == 0
    assert result.report["summary"] == {"passed": 29, "failed": 0}
    assert [artifact["id"] for artifact in result.report["artifacts"]] == [
        spec.id for spec in DEFAULT_VISUAL_ARTIFACTS
    ]


def test_visual_regression_passes_valid_artifact(tmp_path: Path) -> None:
    _write_artifact(tmp_path, html="SceneKit load proof: Loaded\nRetry Scene Load")
    spec = _spec()

    result = check_visual_artifacts(tmp_path, specs=[spec])

    assert result.exit_code == 0
    assert result.report["status"] == "passed"
    assert result.report["summary"] == {"passed": 1, "failed": 0}
    assert result.report["artifacts"][0]["dimensions"] == {"width": 390, "height": 844}


def test_visual_regression_fails_missing_png(tmp_path: Path) -> None:
    (tmp_path / "docs/superpowers/verification").mkdir(parents=True)
    (tmp_path / "docs/superpowers/verification/p0.118-scene-load-proof.html").write_text(
        "SceneKit load proof: Loaded\nRetry Scene Load",
        encoding="utf-8",
    )

    result = check_visual_artifacts(tmp_path, specs=[_spec()])

    assert result.exit_code == 1
    assert result.report["status"] == "failed"
    assert result.report["artifacts"][0]["checks"]["png_exists"]["status"] == "failed"


def test_visual_regression_fails_wrong_dimensions(tmp_path: Path) -> None:
    _write_artifact(tmp_path, html="SceneKit load proof: Loaded\nRetry Scene Load", width=391)

    result = check_visual_artifacts(tmp_path, specs=[_spec()])

    assert result.exit_code == 1
    checks = result.report["artifacts"][0]["checks"]
    assert checks["png_dimensions"]["status"] == "failed"
    assert result.report["artifacts"][0]["dimensions"] == {"width": 391, "height": 844}


def test_visual_regression_fails_missing_required_text(tmp_path: Path) -> None:
    _write_artifact(tmp_path, html="SceneKit load proof: Loaded")

    result = check_visual_artifacts(tmp_path, specs=[_spec()])

    assert result.exit_code == 1
    checks = result.report["artifacts"][0]["checks"]
    assert checks["required_text"]["status"] == "failed"
    assert checks["required_text"]["missing"] == ["Retry Scene Load"]


def test_visual_regression_fails_and_redacts_unsafe_text(tmp_path: Path) -> None:
    _write_artifact(
        tmp_path,
        html="SceneKit load proof: Loaded\nRetry Scene Load\nBearer sk-secret /Users/zhexu/private",
    )

    result = check_visual_artifacts(tmp_path, specs=[_spec()])
    text = json.dumps(result.report)

    assert result.exit_code == 1
    assert "[withheld]" in text
    assert "sk-secret" not in text
    assert "/Users/" not in text
    assert result.report["artifacts"][0]["checks"]["unsafe_text"]["status"] == "failed"


def test_visual_regression_fails_and_redacts_unsafe_notes(tmp_path: Path) -> None:
    _write_artifact(tmp_path, html="SceneKit load proof: Loaded\nRetry Scene Load")
    notes = tmp_path / "docs/superpowers/verification/2026-06-07-p0.118-scene-load-proof-regression.md"
    notes.write_text("Visual note leaked file:///Users/zhexu/private", encoding="utf-8")

    result = check_visual_artifacts(tmp_path, specs=[_spec_with_notes()])
    text = json.dumps(result.report)

    assert result.exit_code == 1
    assert "[withheld]" in text
    assert "file:///" not in text
    assert "/Users/" not in text
    assert result.report["artifacts"][0]["checks"]["unsafe_text"]["status"] == "failed"


def test_visual_regression_cli_writes_showcase_report(tmp_path: Path, monkeypatch) -> None:
    _write_default_artifacts(tmp_path)
    output = tmp_path / "report.json"
    monkeypatch.chdir(tmp_path)

    exit_code = main([
        "visual-regression",
        "--repo-root",
        str(tmp_path),
        "--output",
        str(output),
    ])

    assert exit_code == 0
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["kind"] == "visual_regression_report"
    assert report["status"] == "passed"
    assert report["summary"] == {"passed": 29, "failed": 0}


def _spec() -> VisualArtifactSpec:
    return VisualArtifactSpec(
        id="p0.118_scene_load_proof",
        html_path="docs/superpowers/verification/p0.118-scene-load-proof.html",
        png_path="docs/superpowers/verification/assets/p0.118-scene-load-proof-390x844.png",
        width=390,
        height=844,
        required_text=("SceneKit load proof: Loaded", "Retry Scene Load"),
    )


def _spec_with_notes() -> VisualArtifactSpec:
    return VisualArtifactSpec(
        id="p0.118_scene_load_proof",
        html_path="docs/superpowers/verification/p0.118-scene-load-proof.html",
        png_path="docs/superpowers/verification/assets/p0.118-scene-load-proof-390x844.png",
        notes_path="docs/superpowers/verification/2026-06-07-p0.118-scene-load-proof-regression.md",
        width=390,
        height=844,
        required_text=("SceneKit load proof: Loaded", "Retry Scene Load"),
    )


def _write_artifact(tmp_path: Path, *, html: str, width: int = 390, height: int = 844) -> None:
    verification = tmp_path / "docs/superpowers/verification"
    assets = verification / "assets"
    assets.mkdir(parents=True)
    (verification / "p0.118-scene-load-proof.html").write_text(html, encoding="utf-8")
    (assets / "p0.118-scene-load-proof-390x844.png").write_bytes(_png_header(width, height))


def _write_default_artifacts(tmp_path: Path) -> None:
    for spec in DEFAULT_VISUAL_ARTIFACTS:
        html_file = tmp_path / spec.html_path
        png_file = tmp_path / spec.png_path
        html_file.parent.mkdir(parents=True, exist_ok=True)
        png_file.parent.mkdir(parents=True, exist_ok=True)
        html_file.write_text("\n".join(spec.required_text), encoding="utf-8")
        png_file.write_bytes(_png_header(spec.width, spec.height))
        if spec.notes_path:
            notes_file = tmp_path / spec.notes_path
            notes_file.parent.mkdir(parents=True, exist_ok=True)
            notes_file.write_text(f"{spec.id} visual regression notes", encoding="utf-8")


def _png_header(width: int, height: int) -> bytes:
    return (
        b"\x89PNG\r\n\x1a\n"
        + struct.pack(">I", 13)
        + b"IHDR"
        + struct.pack(">II", width, height)
        + b"\x08\x02\x00\x00\x00"
    )
