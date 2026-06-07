from __future__ import annotations

import json
import struct
from pathlib import Path

from myth_forge_api.cli import main
from myth_forge_api.visual_regression import (
    VisualArtifactSpec,
    check_visual_artifacts,
    png_dimensions,
)


def test_png_dimensions_reads_png_header(tmp_path: Path) -> None:
    png = tmp_path / "image.png"
    png.write_bytes(_png_header(390, 844))

    assert png_dimensions(png) == (390, 844)


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


def test_visual_regression_cli_writes_report(tmp_path: Path, monkeypatch) -> None:
    _write_artifact(
        tmp_path,
        html=(
            "SceneKit load proof: Loaded\n"
            "SceneKit load proof: Conversion needed\n"
            "SceneKit load proof: Failed\n"
            "Retry Scene Load"
        ),
    )
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


def _png_header(width: int, height: int) -> bytes:
    return (
        b"\x89PNG\r\n\x1a\n"
        + struct.pack(">I", 13)
        + b"IHDR"
        + struct.pack(">II", width, height)
        + b"\x08\x02\x00\x00\x00"
    )
