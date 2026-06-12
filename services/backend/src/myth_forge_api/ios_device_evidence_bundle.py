from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from myth_forge_api.final_acceptance_readiness import (
    build_final_acceptance_readiness_report,
)
from myth_forge_api.ios_deploy_runbook import build_ios_deploy_runbook_report
from myth_forge_api.ios_device_launch_rehearsal_readiness import (
    build_ios_device_launch_rehearsal_readiness_report,
)
from myth_forge_api.operator_actions import (
    BACKEND_DEVICE_DEMO_VALIDATED_ACTION,
    normalize_operator_action,
)

MOBILE_DEPLOY_PREFLIGHT_EVIDENCE_PATH = Path(
    "services/backend/.local/mobile-deploy-preflight-evidence.json"
)
MOBILE_XCODE_BUILD_EVIDENCE_PATH = Path(
    "services/backend/.local/mobile-xcode-build-evidence.json"
)
IOS_DEVICE_EVIDENCE_SOURCE_ACTION_PREFIXES = (
    "final_rehearsal_local: ",
    "final_acceptance_local: ",
    "final_configured_preflight: ",
    "final_handoff_index: ",
    "ios_device_launch_certificate: ",
    "ios_deploy_runbook_local: ",
    "mobile_deploy_preflight_evidence: ",
    "mobile_xcode_build_evidence: ",
)


@dataclass(frozen=True)
class IOSDeviceEvidenceBundleResult:
    exit_code: int
    report: dict[str, Any]


def build_ios_device_evidence_bundle_report(
    *,
    repo_root: Path | str | None = None,
) -> IOSDeviceEvidenceBundleResult:
    selected_repo_root = Path(repo_root) if repo_root is not None else _default_repo_root()
    final_acceptance = build_final_acceptance_readiness_report(
        repo_root=selected_repo_root,
    ).report
    ios_deploy_runbook = build_ios_deploy_runbook_report(
        mode="local",
        repo_root=selected_repo_root,
    )
    launch_rehearsal = build_ios_device_launch_rehearsal_readiness_report(
        repo_root=selected_repo_root,
    ).report
    mobile_deploy_preflight_evidence = _load_optional_report(
        selected_repo_root / MOBILE_DEPLOY_PREFLIGHT_EVIDENCE_PATH
    )
    xcode_build_evidence = _load_optional_report(
        selected_repo_root / MOBILE_XCODE_BUILD_EVIDENCE_PATH
    )
    evidence_slots = _evidence_slots(
        final_acceptance=final_acceptance,
        ios_deploy_runbook=ios_deploy_runbook,
        launch_rehearsal=launch_rehearsal,
        mobile_deploy_preflight_evidence=mobile_deploy_preflight_evidence,
        xcode_build_evidence=xcode_build_evidence,
    )
    status = _overall_status(evidence_slots)
    source_reports = {
        "final_acceptance_readiness": _source_summary(final_acceptance),
        "ios_deploy_runbook": _source_summary(ios_deploy_runbook),
        "ios_device_launch_rehearsal_readiness": _source_summary(
            launch_rehearsal,
        ),
    }
    if mobile_deploy_preflight_evidence is not None:
        source_reports["mobile_deploy_preflight_evidence"] = _source_summary(
            mobile_deploy_preflight_evidence
        )
    if xcode_build_evidence is not None:
        source_reports["mobile_xcode_build_evidence"] = _source_summary(
            xcode_build_evidence
        )
    report = {
        "kind": "ios_device_evidence_bundle_report",
        "status": status,
        "summary": _summary(evidence_slots),
        "evidence_slots": evidence_slots,
        "source_reports": source_reports,
        "operator_actions": _operator_actions(status, evidence_slots),
        "commands": [
            "make backend-device-demo",
            "make mobile-deploy-preflight",
            "make mobile-xcode-build",
            "make ios-device-launch-rehearsal",
        ],
        "safety": _safety(),
    }
    sanitized = _sanitize_report(report, selected_repo_root)
    return IOSDeviceEvidenceBundleResult(
        exit_code=0 if sanitized["status"] == "ready" else 2,
        report=sanitized,
    )


def _evidence_slots(
    *,
    final_acceptance: dict[str, Any],
    ios_deploy_runbook: dict[str, Any],
    launch_rehearsal: dict[str, Any],
    mobile_deploy_preflight_evidence: dict[str, Any] | None,
    xcode_build_evidence: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    blockers = _blockers_by_id(final_acceptance)
    final_acceptance_status = str(final_acceptance.get("status", "missing"))
    acceptance_ready = final_acceptance_status == "ready"
    mobile_blocker = blockers.get("mobile_deploy_preflight")
    xcode_blocker = blockers.get("mobile_xcode_build")
    launch_status = str(launch_rehearsal.get("status", "missing"))
    xcode_status = _xcode_evidence_status(
        xcode_build_evidence,
        acceptance_ready=acceptance_ready,
        final_acceptance_status=final_acceptance_status,
        xcode_blocker=xcode_blocker,
    )
    xcode_detail = _xcode_evidence_detail(
        xcode_build_evidence,
        xcode_blocker=xcode_blocker,
    )
    xcode_classification = _xcode_evidence_classification(
        xcode_build_evidence,
        xcode_blocker=xcode_blocker,
        final_acceptance_status=final_acceptance_status,
    )
    xcode_evidence_source = (
        MOBILE_XCODE_BUILD_EVIDENCE_PATH.as_posix()
        if xcode_build_evidence is not None
        else "services/backend/.local/final-acceptance-local.json"
    )
    preflight_evidence_source = _mobile_preflight_evidence_source(
        mobile_deploy_preflight_evidence
    )

    return [
        _slot(
            slot_id="backend_device_server",
            label="Backend device server",
            status=_backend_server_status(
                acceptance_ready=acceptance_ready,
                final_acceptance_status=final_acceptance_status,
                mobile_blocker=mobile_blocker,
                mobile_deploy_preflight_evidence=mobile_deploy_preflight_evidence,
            ),
            command="make backend-device-demo",
            detail=_backend_server_detail(
                acceptance_ready=acceptance_ready,
                mobile_blocker=mobile_blocker,
                mobile_deploy_preflight_evidence=mobile_deploy_preflight_evidence,
            ),
            classification=_backend_server_classification(
                mobile_blocker,
                final_acceptance_status=final_acceptance_status,
                mobile_deploy_preflight_evidence=mobile_deploy_preflight_evidence,
            ),
            evidence_source=preflight_evidence_source,
        ),
        _slot(
            slot_id="mobile_deploy_preflight",
            label="Mobile deploy preflight",
            status=_mobile_preflight_slot_status(
                acceptance_ready=acceptance_ready,
                final_acceptance_status=final_acceptance_status,
                mobile_blocker=mobile_blocker,
                mobile_deploy_preflight_evidence=mobile_deploy_preflight_evidence,
            ),
            command="make mobile-deploy-preflight",
            detail=_mobile_preflight_slot_detail(
                blocker=mobile_blocker,
                mobile_deploy_preflight_evidence=mobile_deploy_preflight_evidence,
            ),
            classification=_mobile_preflight_slot_classification(
                mobile_blocker,
                final_acceptance_status=final_acceptance_status,
                mobile_deploy_preflight_evidence=mobile_deploy_preflight_evidence,
            ),
            evidence_source=preflight_evidence_source,
        ),
        _slot(
            slot_id="xcode_build_gate",
            label="Xcode build gate",
            status=xcode_status,
            command="make mobile-xcode-build",
            detail=xcode_detail,
            classification=xcode_classification,
            evidence_source=xcode_evidence_source,
            global_action=True,
            xcode_or_signing=True,
        ),
        _slot(
            slot_id="ios_device_launch_rehearsal",
            label="iOS device launch rehearsal",
            status="ready" if launch_status == "ready" else launch_status,
            command="make ios-device-launch-rehearsal",
            detail=_launch_rehearsal_detail(launch_rehearsal),
            classification=_launch_rehearsal_classification(launch_rehearsal),
            evidence_source="services/backend/.local/ios-device-launch-rehearsal.json",
        ),
    ]


def _slot(
    *,
    slot_id: str,
    label: str,
    status: str,
    command: str,
    detail: str,
    classification: str,
    evidence_source: str,
    global_action: bool = False,
    xcode_or_signing: bool = False,
) -> dict[str, Any]:
    normalized_status = _normalized_status(status)
    return {
        "id": slot_id,
        "label": label,
        "status": normalized_status,
        "command": command,
        "detail": detail,
        "classification": classification,
        "evidence_source": evidence_source,
        "required": True,
        "global_action": global_action,
        "xcode_or_signing": xcode_or_signing,
    }


def _backend_server_status(
    *,
    acceptance_ready: bool,
    final_acceptance_status: str,
    mobile_blocker: dict[str, Any] | None,
    mobile_deploy_preflight_evidence: dict[str, Any] | None,
) -> str:
    evidence_status = _mobile_preflight_evidence_status(
        mobile_deploy_preflight_evidence
    )
    if evidence_status is not None:
        return evidence_status
    if acceptance_ready:
        return "ready"
    if final_acceptance_status == "missing":
        return "missing"
    if (
        mobile_blocker
        and mobile_blocker.get("classification")
        == "blocked_by_local_ios_backend_health"
    ):
        return "blocked"
    return "blocked"


def _backend_server_detail(
    *,
    acceptance_ready: bool,
    mobile_blocker: dict[str, Any] | None,
    mobile_deploy_preflight_evidence: dict[str, Any] | None,
) -> str:
    if acceptance_ready:
        return "Final acceptance recorded iPhone-reachable backend health."
    evidence_detail = _mobile_preflight_check_detail(
        mobile_deploy_preflight_evidence,
        preferred_ids=("backend_health", "backend_base_url"),
    )
    if evidence_detail:
        return evidence_detail
    if mobile_blocker and str(mobile_blocker.get("detail", "")).strip():
        return str(mobile_blocker["detail"])
    return "Start backend-device-demo and prove iPhone-reachable /health before device launch."


def _backend_server_classification(
    mobile_blocker: dict[str, Any] | None,
    *,
    final_acceptance_status: str,
    mobile_deploy_preflight_evidence: dict[str, Any] | None,
) -> str:
    evidence_status = _mobile_preflight_evidence_status(
        mobile_deploy_preflight_evidence
    )
    if evidence_status is not None:
        return f"mobile_deploy_preflight_evidence_{_normalized_status(evidence_status)}"
    return _classification(
        mobile_blocker,
        default="final_acceptance_missing"
        if final_acceptance_status == "missing"
        else "backend_health_not_proven",
    )


def _mobile_preflight_slot_status(
    *,
    acceptance_ready: bool,
    final_acceptance_status: str,
    mobile_blocker: dict[str, Any] | None,
    mobile_deploy_preflight_evidence: dict[str, Any] | None,
) -> str:
    evidence_status = _mobile_preflight_evidence_status(
        mobile_deploy_preflight_evidence
    )
    if evidence_status is not None:
        return evidence_status
    return _gate_status(
        acceptance_ready=acceptance_ready,
        final_acceptance_status=final_acceptance_status,
        blocker=mobile_blocker,
    )


def _mobile_preflight_slot_detail(
    *,
    blocker: dict[str, Any] | None,
    mobile_deploy_preflight_evidence: dict[str, Any] | None,
) -> str:
    evidence_detail = _mobile_preflight_detail_summary(
        mobile_deploy_preflight_evidence
    )
    if evidence_detail:
        return evidence_detail
    return _gate_detail(
        blocker=blocker,
        ready_detail="Final acceptance recorded a passing mobile deploy preflight.",
        missing_detail="Run mobile deploy preflight after backend-device-demo is reachable.",
    )


def _mobile_preflight_slot_classification(
    blocker: dict[str, Any] | None,
    *,
    final_acceptance_status: str,
    mobile_deploy_preflight_evidence: dict[str, Any] | None,
) -> str:
    evidence_status = _mobile_preflight_evidence_status(
        mobile_deploy_preflight_evidence
    )
    if evidence_status is not None:
        return f"mobile_deploy_preflight_evidence_{_normalized_status(evidence_status)}"
    return _classification(
        blocker,
        default="final_acceptance_missing"
        if final_acceptance_status == "missing"
        else "mobile_deploy_preflight_not_proven",
    )


def _mobile_preflight_evidence_source(evidence: dict[str, Any] | None) -> str:
    if _mobile_preflight_evidence_status(evidence) is not None:
        return MOBILE_DEPLOY_PREFLIGHT_EVIDENCE_PATH.as_posix()
    return "services/backend/.local/final-acceptance-local.json"


def _mobile_preflight_evidence_status(evidence: dict[str, Any] | None) -> str | None:
    if (
        evidence is None
        or evidence.get("kind") != "mobile_deploy_preflight_evidence_report"
    ):
        return None
    return str(evidence.get("status", "blocked"))


def _mobile_preflight_detail_summary(evidence: dict[str, Any] | None) -> str:
    return _mobile_preflight_check_detail(evidence) or _first_operator_action(evidence)


def _mobile_preflight_check_detail(
    evidence: dict[str, Any] | None,
    *,
    preferred_ids: tuple[str, ...] = (),
) -> str:
    checks = evidence.get("checks") if isinstance(evidence, dict) else None
    if not isinstance(checks, list):
        return ""
    preferred = set(preferred_ids)
    details: list[str] = []
    for check in checks:
        if not isinstance(check, dict):
            continue
        detail = str(check.get("detail", "")).strip()
        if not detail:
            continue
        if preferred and str(check.get("id", "")) not in preferred:
            continue
        details.append(detail)
    return "; ".join(details)


def _first_operator_action(report: dict[str, Any] | None) -> str:
    actions = report.get("operator_actions") if isinstance(report, dict) else None
    if isinstance(actions, list) and actions:
        return str(actions[0])
    return ""


def _gate_status(
    *,
    acceptance_ready: bool,
    final_acceptance_status: str,
    blocker: dict[str, Any] | None,
) -> str:
    if acceptance_ready:
        return "ready"
    if final_acceptance_status == "missing":
        return "missing"
    return "blocked" if blocker else "blocked"


def _gate_detail(
    *,
    blocker: dict[str, Any] | None,
    ready_detail: str,
    missing_detail: str,
) -> str:
    if blocker and str(blocker.get("detail", "")).strip():
        return str(blocker["detail"])
    if blocker:
        return str(blocker.get("classification") or missing_detail)
    return missing_detail


def _classification(blocker: dict[str, Any] | None, *, default: str) -> str:
    if blocker and blocker.get("classification"):
        return str(blocker["classification"])
    return default


def _xcode_evidence_status(
    evidence: dict[str, Any] | None,
    *,
    acceptance_ready: bool,
    final_acceptance_status: str,
    xcode_blocker: dict[str, Any] | None,
) -> str:
    if evidence is not None:
        return str(evidence.get("status", "blocked"))
    return _gate_status(
        acceptance_ready=acceptance_ready,
        final_acceptance_status=final_acceptance_status,
        blocker=xcode_blocker,
    )


def _xcode_evidence_detail(
    evidence: dict[str, Any] | None,
    *,
    xcode_blocker: dict[str, Any] | None,
) -> str:
    if evidence is not None:
        checks = evidence.get("checks")
        if isinstance(checks, list):
            for check in checks:
                if isinstance(check, dict) and str(check.get("detail", "")).strip():
                    return str(check["detail"])
        actions = evidence.get("operator_actions")
        if isinstance(actions, list) and actions:
            return str(actions[0])
        classification = evidence.get("classification")
        if classification:
            return str(classification)
    return _gate_detail(
        blocker=xcode_blocker,
        ready_detail="Final acceptance recorded a passing Xcode build gate.",
        missing_detail="Run the Xcode build gate on the Mac after deploy preflight passes.",
    )


def _xcode_evidence_classification(
    evidence: dict[str, Any] | None,
    *,
    xcode_blocker: dict[str, Any] | None,
    final_acceptance_status: str,
) -> str:
    if evidence is not None and evidence.get("classification"):
        return str(evidence["classification"])
    return _classification(
        xcode_blocker,
        default="final_acceptance_missing"
        if final_acceptance_status == "missing"
        else "xcode_build_gate_not_proven",
    )


def _launch_rehearsal_detail(report: dict[str, Any]) -> str:
    status = str(report.get("status", "missing"))
    if status == "ready":
        return "Saved iOS device launch rehearsal evidence is ready."
    actions = report.get("operator_actions")
    if isinstance(actions, list) and actions:
        normalized_action = normalize_operator_action(str(actions[0]))
        if normalized_action == "make ios-device-launch-rehearsal":
            return "Run iOS device launch rehearsal to refresh final device evidence."
        return normalized_action
    return "Run iOS device launch rehearsal to refresh final device evidence."


def _launch_rehearsal_classification(report: dict[str, Any]) -> str:
    status = str(report.get("status", "missing"))
    if status == "ready":
        return "ready"
    if status == "missing":
        return "missing_report"
    blockers = report.get("blockers")
    if isinstance(blockers, list) and blockers:
        blocker = blockers[0]
        if isinstance(blocker, dict) and blocker.get("classification"):
            return str(blocker["classification"])
    return f"{status}_rehearsal"


def _blockers_by_id(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw_blockers = report.get("blockers")
    if not isinstance(raw_blockers, list):
        return {}
    blockers: dict[str, dict[str, Any]] = {}
    for blocker in raw_blockers:
        if not isinstance(blocker, dict):
            continue
        blocker_id = str(blocker.get("id", ""))
        if blocker_id:
            blockers[blocker_id] = blocker
    return blockers


def _operator_actions(status: str, slots: list[dict[str, Any]]) -> list[str]:
    if status == "ready":
        return ["iOS device evidence is ready"]
    actions: list[str] = []
    for slot in slots:
        if slot["status"] == "ready":
            continue
        if slot["id"] == "backend_device_server":
            actions.append(
                _action_with_detail(
                    "start backend-device-demo before device checks: make backend-device-demo",
                    slot,
                )
            )
        elif slot["id"] == "mobile_deploy_preflight":
            actions.append(
                _action_with_detail(
                    BACKEND_DEVICE_DEMO_VALIDATED_ACTION,
                    slot,
                )
            )
        elif slot["id"] == "xcode_build_gate":
            actions.append(
                _action_with_detail(
                    "run Xcode build gate manually on the Mac: make mobile-xcode-build",
                    slot,
                )
            )
        elif slot["id"] == "ios_device_launch_rehearsal":
            actions.append(
                _action_with_detail("run make ios-device-launch-rehearsal", slot)
            )
    return _dedupe(actions)


def _action_with_detail(action: str, slot: dict[str, Any]) -> str:
    detail = str(slot.get("detail", "")).strip()
    if not detail:
        return action
    return f"{action} | {detail}"


def _summary(slots: list[dict[str, Any]]) -> dict[str, int]:
    statuses = ["ready", "missing", "blocked", "manual"]
    return {
        **{status: sum(1 for slot in slots if slot["status"] == status) for status in statuses},
        "required": sum(1 for slot in slots if slot["required"]),
        "global_actions": sum(1 for slot in slots if slot["global_action"]),
    }


def _overall_status(slots: list[dict[str, Any]]) -> str:
    return "ready" if all(slot["status"] == "ready" for slot in slots) else "blocked"


def _source_summary(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": report.get("kind"),
        "status": report.get("status") or report.get("overall_status"),
        "summary": report.get("summary", {}),
    }


def _load_optional_report(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return loaded if isinstance(loaded, dict) else None


def _safety() -> dict[str, bool]:
    return {
        "commands_run": False,
        "provider_calls": False,
        "live_provider_calls": False,
        "writes_backend_env": False,
        "writes_ios_deploy_config": False,
        "global_mutation": False,
        "xcode_or_signing": False,
        "keychain_writes": False,
        "provider_secrets_in_report": False,
        "raw_media_in_report": False,
        "payment_links_in_report": False,
        "local_paths_in_report": False,
        "describes_global_actions": True,
    }


def _normalized_status(status: str) -> str:
    normalized = status.strip().lower()
    if normalized in {"ready", "missing", "blocked", "manual"}:
        return normalized
    if normalized in {"passed", "succeeded"}:
        return "ready"
    return "blocked"


def _sanitize_report(report: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    return json.loads(json.dumps(_sanitize_value(report, repo_root)))


def _sanitize_value(value: Any, repo_root: Path) -> Any:
    if isinstance(value, str):
        return _safe_text(value, repo_root)
    if isinstance(value, list):
        return [_sanitize_value(item, repo_root) for item in value]
    if isinstance(value, dict):
        return {key: _sanitize_value(item, repo_root) for key, item in value.items()}
    return value


def _safe_text(message: str, repo_root: Path) -> str:
    sanitized = message
    for pattern in [
        r"sk-[A-Za-z0-9._-]+",
        r"Bearer\s+[A-Za-z0-9._~+/\-=:-]+",
        r"Authorization",
        r"api[_-]?key\s*[=:]\s*[^\s,;\"']+",
        r"data:[A-Za-z0-9.+-]+/[A-Za-z0-9.+-]+;base64,[A-Za-z0-9+/=_-]+",
        r"https?://pay\.[^\s,;\"']+",
        r"https?://checkout\.[^\s,;\"']+",
        r"checkout_url",
        r"file://[^\s,;\"']+",
        r"/Users/[^\s,;\"']+",
        r"/tmp/[^\s,;\"']+",
    ]:
        sanitized = re.sub(pattern, "[redacted]", sanitized, flags=re.IGNORECASE)
    root_text = str(repo_root)
    if root_text:
        sanitized = sanitized.replace(root_text, "[repo-root]")
    home_text = str(Path.home())
    if home_text:
        sanitized = sanitized.replace(home_text, "[home]")
    return sanitized


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        normalized = _top_level_operator_action(value)
        if normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result


def _top_level_operator_action(action: str) -> str:
    normalized = normalize_operator_action(action)
    command_part, detail_suffix = _split_detail_suffix(normalized)
    return f"{command_part}{_strip_source_prefixes_from_detail(detail_suffix)}"


def _split_detail_suffix(action: str) -> tuple[str, str]:
    command, separator, detail = action.partition(" | ")
    if not separator:
        return action.strip(), ""
    return command.strip(), f"{separator}{detail}"


def _strip_source_prefixes_from_detail(detail_suffix: str) -> str:
    if not detail_suffix:
        return ""
    separator = " | "
    detail = detail_suffix.removeprefix(separator).strip()
    detail_root, nested_separator, nested_detail = detail.partition(separator)
    stripped_root = _strip_evidence_source_prefixes(detail_root)
    if nested_separator:
        return f"{separator}{stripped_root}{nested_separator}{nested_detail}"
    return f"{separator}{stripped_root}"


def _strip_evidence_source_prefixes(value: str) -> str:
    stripped = value.strip()
    changed = True
    while changed:
        changed = False
        for prefix in IOS_DEVICE_EVIDENCE_SOURCE_ACTION_PREFIXES:
            if stripped.startswith(prefix):
                stripped = stripped.removeprefix(prefix).strip()
                changed = True
    return stripped


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parents[4]
