from __future__ import annotations

import re
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
FORBIDDEN_PATTERNS = (
    r"sk-[A-Za-z0-9._-]+",
    r"Bearer\s+[A-Za-z0-9._~+/\-=:-]+",
    r"Authorization",
    r"api[_-]?key\s*[=:]\s*[^\s,;\"']+",
    r"local-capture://[^\s,;\"']+",
    r"file://[^\s,;\"']+",
    r"/Users/[^\s,;\"']+",
    r"/tmp/[^\s,;\"']+",
    r"data:image",
    r"checkout_url",
    r"https?://checkout\.[^\s,;\"']+",
    r"https?://pay\.[^\s,;\"']+",
)


@dataclass(frozen=True)
class VisualArtifactSpec:
    id: str
    html_path: str
    png_path: str
    width: int
    height: int
    required_text: tuple[str, ...]
    notes_path: str | None = None


@dataclass(frozen=True)
class VisualRegressionResult:
    exit_code: int
    report: dict[str, Any]


DEFAULT_VISUAL_ARTIFACTS = (
    VisualArtifactSpec(
        id="p0.12_ios_device_media_input",
        html_path="docs/superpowers/verification/p0.12-ios-device-media-input.html",
        png_path="docs/superpowers/verification/assets/p0.12-ios-device-media-input-390x844.png",
        notes_path="docs/superpowers/verification/2026-06-05-p0.12-ios-device-media-input-regression.md",
        width=390,
        height=844,
        required_text=("PhotosPicker", "fileImporter", "CaptureMediaSelection"),
    ),
    VisualArtifactSpec(
        id="p0.19_guided_scan_entry",
        html_path="docs/superpowers/verification/p0.19-guided-scan-entry.html",
        png_path="docs/superpowers/verification/assets/p0.19-guided-scan-entry-390x844.png",
        notes_path="docs/superpowers/verification/2026-06-06-p0.19-guided-scan-entry-regression.md",
        width=390,
        height=844,
        required_text=("Start Guided Scan", "Guided Scan", "Object Capture"),
    ),
    VisualArtifactSpec(
        id="p0.98_capture_generation_receipt",
        html_path="docs/superpowers/verification/p0.98-mobile-capture-generation-receipt.html",
        png_path="docs/superpowers/verification/assets/p0.98-mobile-capture-generation-receipt-390x844.png",
        notes_path="docs/superpowers/verification/2026-06-07-p0.98-mobile-capture-generation-receipt-regression.md",
        width=390,
        height=844,
        required_text=("Capture-to-3D", "Capture-to-3D ready"),
    ),
    VisualArtifactSpec(
        id="p0.103_generation_result_receipt",
        html_path="docs/superpowers/verification/p0.103-generation-result-receipt.html",
        png_path="docs/superpowers/verification/assets/p0.103-generation-result-receipt-390x844.png",
        notes_path="docs/superpowers/verification/2026-06-07-p0.103-generation-result-receipt-regression.md",
        width=390,
        height=844,
        required_text=("3D Generation Result", "NPC Agent", "scene-loadable"),
    ),
    VisualArtifactSpec(
        id="p0.118_scene_load_proof",
        html_path="docs/superpowers/verification/p0.118-scene-load-proof.html",
        png_path="docs/superpowers/verification/assets/p0.118-scene-load-proof-390x844.png",
        notes_path="docs/superpowers/verification/2026-06-07-p0.118-scene-load-proof-regression.md",
        width=390,
        height=844,
        required_text=(
            "SceneKit load proof: Loaded",
            "SceneKit load proof: Conversion needed",
            "SceneKit load proof: Failed",
            "Retry Scene Load",
        ),
    ),
    VisualArtifactSpec(
        id="p0.82_npc_agent_tick_summary",
        html_path="docs/superpowers/verification/p0.82-npc-agent-tick-summary.html",
        png_path="docs/superpowers/verification/assets/p0.82-npc-agent-tick-summary-390x844.png",
        notes_path="docs/superpowers/verification/2026-06-06-p0.82-npc-agent-tick-summary-regression.md",
        width=390,
        height=844,
        required_text=("NPC Agent tick resolved", "Run Autonomy", "Advance Village"),
    ),
    VisualArtifactSpec(
        id="p0.101_print_fulfillment_receipt",
        html_path="docs/superpowers/verification/p0.101-print-fulfillment-receipt.html",
        png_path="docs/superpowers/verification/assets/p0.101-print-fulfillment-receipt-390x844.png",
        notes_path="docs/superpowers/verification/2026-06-07-p0.101-print-fulfillment-receipt-regression.md",
        width=390,
        height=844,
        required_text=("Print Fulfillment", "Approve Print Handoff"),
    ),
    VisualArtifactSpec(
        id="p0.100_live_provider_consent",
        html_path="docs/superpowers/verification/p0.100-live-provider-consent.html",
        png_path="docs/superpowers/verification/assets/p0.100-live-provider-consent-390x844.png",
        notes_path="docs/superpowers/verification/2026-06-07-p0.100-live-provider-consent-regression.md",
        width=390,
        height=844,
        required_text=("Live Provider Consent", "Provider keys remain backend-only"),
    ),
    VisualArtifactSpec(
        id="p0.112_ios_device_launch_rehearsal",
        html_path="docs/superpowers/verification/p0.112-ios-device-launch-rehearsal.html",
        png_path="docs/superpowers/verification/assets/p0.112-ios-device-launch-rehearsal-390x844.png",
        notes_path="docs/superpowers/verification/2026-06-07-p0.112-ios-device-launch-rehearsal-regression.md",
        width=390,
        height=844,
        required_text=("iOS Device Launch Rehearsal", "Launch Rehearsal"),
    ),
    VisualArtifactSpec(
        id="p0.119_visual_regression_handoff",
        html_path="docs/superpowers/verification/p0.119-visual-regression-handoff.html",
        png_path="docs/superpowers/verification/assets/p0.119-visual-regression-handoff-390x844.png",
        notes_path="docs/superpowers/verification/2026-06-07-p0.119-visual-regression-handoff-regression.md",
        width=390,
        height=844,
        required_text=("Final Launch Status", "Visual Regression", "make visual-regression-local"),
    ),
)


def check_visual_artifacts(
    repo_root: Path | str,
    *,
    specs: Sequence[VisualArtifactSpec] = DEFAULT_VISUAL_ARTIFACTS,
) -> VisualRegressionResult:
    root = Path(repo_root)
    artifacts = [_check_artifact(root, spec) for spec in specs]
    failed = sum(1 for artifact in artifacts if artifact["status"] == "failed")
    report = {
        "kind": "visual_regression_report",
        "status": "failed" if failed else "passed",
        "summary": {"passed": len(artifacts) - failed, "failed": failed},
        "artifacts": artifacts,
    }
    return VisualRegressionResult(exit_code=1 if failed else 0, report=_sanitize_json(report))


def png_dimensions(path: Path | str) -> tuple[int, int]:
    data = Path(path).read_bytes()
    if len(data) < 24 or not data.startswith(PNG_SIGNATURE) or data[12:16] != b"IHDR":
        raise ValueError("Expected PNG with IHDR header.")
    return struct.unpack(">II", data[16:24])


def _check_artifact(root: Path, spec: VisualArtifactSpec) -> dict[str, Any]:
    html_file = root / spec.html_path
    png_file = root / spec.png_path
    html_text = html_file.read_text(encoding="utf-8") if html_file.exists() else ""
    notes_text = _optional_text(root / spec.notes_path) if spec.notes_path else ""
    checks: dict[str, dict[str, Any]] = {}
    checks["html_exists"] = {"status": "passed" if html_file.exists() else "failed"}
    checks["png_exists"] = {"status": "passed" if png_file.exists() else "failed"}
    dimensions: dict[str, int] | None = None

    if png_file.exists():
        try:
            width, height = png_dimensions(png_file)
            dimensions = {"width": width, "height": height}
            checks["png_dimensions"] = {
                "status": "passed" if (width, height) == (spec.width, spec.height) else "failed",
                "expected": {"width": spec.width, "height": spec.height},
                "actual": dimensions,
            }
        except ValueError as exc:
            checks["png_dimensions"] = {
                "status": "failed",
                "detail": str(exc),
                "expected": {"width": spec.width, "height": spec.height},
            }
    else:
        checks["png_dimensions"] = {
            "status": "failed",
            "expected": {"width": spec.width, "height": spec.height},
        }

    missing = [token for token in spec.required_text if token not in html_text]
    checks["required_text"] = {"status": "failed" if missing else "passed", "missing": missing}
    unsafe_hits = _unsafe_hits("\n".join([html_text, notes_text]))
    checks["unsafe_text"] = {"status": "failed" if unsafe_hits else "passed", "matches": unsafe_hits}
    status = "failed" if any(check["status"] == "failed" for check in checks.values()) else "passed"
    return {
        "id": spec.id,
        "status": status,
        "html_path": spec.html_path,
        "png_path": spec.png_path,
        "notes_path": spec.notes_path,
        "dimensions": dimensions,
        "checks": checks,
    }


def _optional_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _unsafe_hits(text: str) -> list[str]:
    hits: list[str] = []
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, text):
            hits.append(pattern)
    return hits


def _sanitize_json(value: Any) -> Any:
    if isinstance(value, str):
        return _sanitize_text(value)
    if isinstance(value, list):
        return [_sanitize_json(item) for item in value]
    if isinstance(value, dict):
        return {key: _sanitize_json(item) for key, item in value.items()}
    return value


def _sanitize_text(text: str) -> str:
    sanitized = text
    for pattern in FORBIDDEN_PATTERNS:
        sanitized = re.sub(pattern, "[withheld]", sanitized)
    return sanitized
