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
    VisualArtifactSpec(
        id="p0.153_configured_evidence_visual",
        html_path="docs/superpowers/verification/p0.153-configured-evidence-visual.html",
        png_path="docs/superpowers/verification/assets/p0.153-configured-evidence-visual-390x844.png",
        notes_path="docs/superpowers/verification/2026-06-07-p0.153-configured-evidence-visual-regression.md",
        width=390,
        height=844,
        required_text=(
            "Configured Evidence",
            "Configured evidence blocked",
            "consent now 0, planned 3",
            "Live steps 3, cost steps 3",
            "--allow-live-provider-calls",
            "commands_run=false live_calls=false",
        ),
    ),
    VisualArtifactSpec(
        id="p0.186_configured_acceptance_command_visual",
        html_path=(
            "docs/superpowers/verification/"
            "p0.186-configured-acceptance-command-visual.html"
        ),
        png_path=(
            "docs/superpowers/verification/assets/"
            "p0.186-configured-acceptance-command-visual-390x844.png"
        ),
        notes_path=(
            "docs/superpowers/verification/"
            "2026-06-08-p0.186-configured-acceptance-command-visual-regression.md"
        ),
        width=390,
        height=844,
        required_text=(
            "Final Launch Status",
            "Commands",
            "make final-acceptance-configured",
            "Live providers: consent required for configured acceptance.",
            "--allow-live-provider-calls",
            "commands_run=false live_calls=false global=false",
        ),
    ),
    VisualArtifactSpec(
        id="p0.154_resource_fill_guide_visual",
        html_path="docs/superpowers/verification/p0.154-resource-fill-guide-visual.html",
        png_path="docs/superpowers/verification/assets/p0.154-resource-fill-guide-visual-390x844.png",
        notes_path="docs/superpowers/verification/2026-06-08-p0.154-resource-fill-guide-visual-regression.md",
        width=390,
        height=844,
        required_text=(
            "Resource Fill Guide",
            "Fill guide blocked",
            "required 5, optional 5, configured 3, secret 4",
            "MESHY_API_KEY",
            "make final-resource-requirements",
            "Safety: writes=false live_calls=false global_mutation=false",
        ),
    ),
    VisualArtifactSpec(
        id="p0.155_device_fill_guide_preflight",
        html_path="docs/superpowers/verification/p0.155-device-fill-guide-preflight.html",
        png_path="docs/superpowers/verification/assets/p0.155-device-fill-guide-preflight-390x844.png",
        notes_path="docs/superpowers/verification/2026-06-08-p0.155-device-fill-guide-preflight-regression.md",
        width=390,
        height=844,
        required_text=(
            "Device Preflight",
            "Fill Guide",
            "blocked: required 5, optional 5, configured 3, secret 4",
            "MESHY_API_KEY",
            "make final-resource-requirements",
            "Provider keys stay backend-only",
        ),
    ),
    VisualArtifactSpec(
        id="p0.156_ios_device_evidence_bundle",
        html_path="docs/superpowers/verification/p0.156-ios-device-evidence-bundle.html",
        png_path="docs/superpowers/verification/assets/p0.156-ios-device-evidence-bundle-390x844.png",
        notes_path="docs/superpowers/verification/2026-06-08-p0.156-ios-device-evidence-bundle-regression.md",
        width=390,
        height=844,
        required_text=(
            "Final Launch Status",
            "Device Evidence",
            "iOS device evidence blocked",
            "mobile_deploy_preflight",
            "make mobile-deploy-preflight",
            "Safety: commands_run=false xcode=false global=false",
        ),
    ),
    VisualArtifactSpec(
        id="p0.157_final_launch_closure_packet",
        html_path="docs/superpowers/verification/p0.157-final-launch-closure-packet.html",
        png_path="docs/superpowers/verification/assets/p0.157-final-launch-closure-packet-390x844.png",
        notes_path=(
            "docs/superpowers/verification/"
            "2026-06-08-p0.157-final-launch-closure-packet-regression.md"
        ),
        width=390,
        height=844,
        required_text=(
            "Closure Packet",
            "Final closure blocked",
            "first_blocker",
            "resource_inputs",
            "provide MESHY_API_KEY",
            "configured_evidence_bundle",
            "configured_live_evidence_bundle",
            "make configured-live-evidence-bundle",
            "cost consent",
            "commands_run=false global=false live_calls=false",
        ),
    ),
    VisualArtifactSpec(
        id="p0.158_local_showcase_smoke",
        html_path="docs/superpowers/verification/p0.158-local-showcase-smoke.html",
        png_path="docs/superpowers/verification/assets/p0.158-local-showcase-smoke-390x844.png",
        notes_path=(
            "docs/superpowers/verification/"
            "2026-06-08-p0.158-local-showcase-smoke-regression.md"
        ),
        width=390,
        height=844,
        required_text=(
            "Local Smoke",
            "Local showcase smoke ready",
            "HTTP 6",
            "NPC ticks 2",
            "downloads 3",
            "provider_calls=false global=false temp_storage=true",
        ),
    ),
    VisualArtifactSpec(
        id="p0.159_final_showcase_local_smoke",
        html_path="docs/superpowers/verification/p0.159-final-showcase-local-smoke.html",
        png_path=(
            "docs/superpowers/verification/assets/"
            "p0.159-final-showcase-local-smoke-390x844.png"
        ),
        notes_path=(
            "docs/superpowers/verification/"
            "2026-06-08-p0.159-final-showcase-local-smoke-regression.md"
        ),
        width=390,
        height=844,
        required_text=(
            "Final Showcase",
            "Local Smoke",
            "Local smoke ready",
            "HTTP 6",
            "NPC ticks 2",
            "downloads 3",
        ),
    ),
    VisualArtifactSpec(
        id="p0.160_final_showcase_ios_deploy_digest",
        html_path="docs/superpowers/verification/p0.160-final-showcase-ios-deploy-digest.html",
        png_path=(
            "docs/superpowers/verification/assets/"
            "p0.160-final-showcase-ios-deploy-digest-390x844.png"
        ),
        notes_path=(
            "docs/superpowers/verification/"
            "2026-06-08-p0.160-final-showcase-ios-deploy-digest-regression.md"
        ),
        width=390,
        height=844,
        required_text=(
            "Final Showcase",
            "iOS Deploy",
            "iOS deploy blocked",
            "make ios-device-launch-rehearsal",
        ),
    ),
    VisualArtifactSpec(
        id="p0.189_device_blocker_handoff",
        html_path="docs/superpowers/verification/p0.189-device-blocker-handoff.html",
        png_path=(
            "docs/superpowers/verification/assets/"
            "p0.189-device-blocker-handoff-390x844.png"
        ),
        notes_path=(
            "docs/superpowers/verification/"
            "2026-06-08-p0.189-device-blocker-handoff-regression.md"
        ),
        width=390,
        height=844,
        required_text=(
            "Device Blocker Handoff",
            "first_blocker",
            "local_rehearsal",
            "make final-rehearsal-local",
            "make mobile-deploy-preflight-evidence",
            "make mobile-xcode-build-evidence",
            "commands_run=false xcode=false global=false",
        ),
    ),
    VisualArtifactSpec(
        id="p0.161_final_showcase_provider_handoff_digest",
        html_path="docs/superpowers/verification/p0.161-final-showcase-provider-handoff-digest.html",
        png_path=(
            "docs/superpowers/verification/assets/"
            "p0.161-final-showcase-provider-handoff-digest-390x844.png"
        ),
        notes_path=(
            "docs/superpowers/verification/"
            "2026-06-08-p0.161-final-showcase-provider-handoff-digest-regression.md"
        ),
        width=390,
        height=844,
        required_text=(
            "Final Showcase",
            "Provider Handoff",
            "provider handoff blocked",
            "provide MESHY_API_KEY",
        ),
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
