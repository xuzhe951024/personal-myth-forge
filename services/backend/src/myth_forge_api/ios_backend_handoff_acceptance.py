from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SourceRequirement:
    id: str
    label: str
    file: str
    contains: str


@dataclass(frozen=True)
class IOSBackendHandoffAcceptanceResult:
    exit_code: int
    report: dict[str, Any]


REQUIREMENTS = (
    SourceRequirement(
        "backend_device_make_target",
        "Backend device Make target",
        "Makefile",
        "backend-device-demo",
    ),
    SourceRequirement(
        "backend_device_host",
        "Backend LAN host binding",
        "Makefile",
        "--host 0.0.0.0",
    ),
    SourceRequirement(
        "backend_device_port",
        "Backend demo port",
        "Makefile",
        "--port 8080",
    ),
    SourceRequirement(
        "local_config_example",
        "Local iPhone backend URL example",
        "apps/mobile/ios/Config/Deployment.local.xcconfig.example",
        "http://192.168.1.10:8080",
    ),
    SourceRequirement(
        "deploy_preflight_loopback_guard",
        "Deploy preflight loopback guard",
        "apps/mobile/ios/scripts/deploy_preflight.sh",
        "http://127.0.0.1:*|http://localhost:*",
    ),
    SourceRequirement(
        "ios_plist_backend_url",
        "Info.plist backend URL",
        "apps/mobile/ios/App/Info.plist",
        "$(PMF_BACKEND_BASE_URL)",
    ),
    SourceRequirement(
        "ios_runtime_backend_url",
        "Runtime backend URL lookup",
        "apps/mobile/ios/App/AppConfiguration.swift",
        "PMFBackendBaseURL",
    ),
)


def run_ios_backend_handoff_acceptance(
    repo_root: str | Path | None = None,
) -> IOSBackendHandoffAcceptanceResult:
    root = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[4]
    requirements = [_evaluate_requirement(root, requirement) for requirement in REQUIREMENTS]
    failed = sum(1 for item in requirements if item["status"] == "failed")
    passed = len(requirements) - failed
    report = {
        "kind": "ios_backend_handoff_acceptance_report",
        "status": "succeeded" if failed == 0 else "failed",
        "requirements": requirements,
        "summary": {"passed": passed, "failed": failed},
        "safety": {
            "global_mutation": False,
            "starts_server": False,
            "runs_xcode": False,
            "runs_swiftpm": False,
            "provider_calls": False,
            "absolute_paths_in_report": False,
        },
    }
    return IOSBackendHandoffAcceptanceResult(
        exit_code=0 if failed == 0 else 1,
        report=_sanitize_report(report),
    )


def _evaluate_requirement(root: Path, requirement: SourceRequirement) -> dict[str, Any]:
    if _contains(root / requirement.file, requirement.contains):
        return {
            "id": requirement.id,
            "label": requirement.label,
            "status": "passed",
            "evidence": f"{requirement.file}::{requirement.contains}",
            "missing": None,
        }
    return {
        "id": requirement.id,
        "label": requirement.label,
        "status": "failed",
        "evidence": None,
        "missing": {"file": requirement.file, "contains": requirement.contains},
    }


def _contains(path: Path, expected: str) -> bool:
    try:
        return expected in path.read_text(encoding="utf-8")
    except OSError:
        return False


def _sanitize_report(report: dict[str, Any]) -> dict[str, Any]:
    text = json.dumps(report)
    if "/Users/" in text or "data:image" in text or "sk-" in text:
        raise ValueError("iOS backend handoff acceptance report contains unsafe text.")
    return report
