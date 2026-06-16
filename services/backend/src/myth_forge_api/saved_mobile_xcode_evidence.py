from __future__ import annotations

import json
from pathlib import Path
from typing import Any

MOBILE_XCODE_BUILD_EVIDENCE_PATH = Path(
    "services/backend/.local/mobile-xcode-build-evidence.json"
)


def has_ready_mobile_xcode_build_evidence(repo_root: Path) -> bool:
    evidence = _load_mobile_xcode_build_evidence(repo_root)
    return (
        evidence.get("kind") == "mobile_xcode_build_evidence_report"
        and evidence.get("status") == "ready"
        and evidence.get("classification") == "ready"
        and evidence.get("exit_code") == 0
        and _safe_ready_evidence(evidence)
    )


def _load_mobile_xcode_build_evidence(repo_root: Path) -> dict[str, Any]:
    path = repo_root / MOBILE_XCODE_BUILD_EVIDENCE_PATH
    if not path.exists():
        return {}
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _safe_ready_evidence(evidence: dict[str, Any]) -> bool:
    safety = evidence.get("safety")
    if not isinstance(safety, dict):
        return False
    return (
        bool(safety.get("commands_run"))
        and not bool(safety.get("global_mutation"))
        and not bool(safety.get("live_provider_calls"))
        and not bool(safety.get("keychain_writes"))
        and not bool(safety.get("code_signing_allowed"))
    )
