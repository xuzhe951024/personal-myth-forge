from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from myth_forge_api.config import Settings, load_settings
from myth_forge_api.final_acceptance_readiness import (
    build_final_acceptance_readiness_report,
)
from myth_forge_api.final_resources_preflight import (
    build_final_resources_preflight_report,
)
from myth_forge_api.ios_deploy_runbook import build_ios_deploy_runbook_report
from myth_forge_api.ios_device_launch_rehearsal_readiness import (
    build_ios_device_launch_rehearsal_readiness_report,
)
from myth_forge_api.ios_showcase_acceptance import run_ios_showcase_acceptance
from myth_forge_api.live_provider_evidence import build_live_provider_evidence_report
from myth_forge_api.npc_agent_evaluation_readiness import (
    build_npc_agent_evaluation_readiness_report,
)
from myth_forge_api.print_fulfillment_readiness import (
    build_print_fulfillment_readiness_report,
)
from myth_forge_api.resource_handoff import build_resource_handoff_report
from myth_forge_api.three_d_evaluation_readiness import (
    build_three_d_evaluation_readiness_report,
)
from myth_forge_api.visual_regression_readiness import (
    build_visual_regression_readiness_report,
)

CAPABILITY_ORDER = [
    "ios_deployable",
    "capture_scanning",
    "game_asset_3d_generation",
    "ai_agent_npc",
    "print_fulfillment",
    "provider_key_handoff",
    "functional_regression",
    "visual_regression",
    "privacy_safety",
]
SOURCE_CAPTURE_FEATURES = {
    "camera_capture",
    "guided_scan",
    "arkit_scan_package",
    "capture_generation_readiness",
    "mobile_3d_generation_input_review",
    "capture_generation_receipt",
}


@dataclass(frozen=True)
class FinalShowcaseReadinessResult:
    exit_code: int
    report: dict[str, Any]


def build_final_showcase_readiness_report(
    *,
    settings: Settings | None = None,
    repo_root: Path | str | None = None,
) -> FinalShowcaseReadinessResult:
    selected_settings = settings or load_settings()
    selected_repo_root = Path(repo_root) if repo_root is not None else _default_repo_root()
    source_acceptance = run_ios_showcase_acceptance(repo_root=selected_repo_root).report
    final_acceptance = build_final_acceptance_readiness_report(
        repo_root=selected_repo_root,
    ).report
    three_d_evaluation = build_three_d_evaluation_readiness_report(
        repo_root=selected_repo_root,
    ).report
    npc_evaluation = build_npc_agent_evaluation_readiness_report(
        repo_root=selected_repo_root,
    ).report
    visual_regression = build_visual_regression_readiness_report(
        repo_root=selected_repo_root,
    ).report
    live_provider_evidence = build_live_provider_evidence_report(
        repo_root=selected_repo_root,
    ).report
    print_fulfillment_readiness = build_print_fulfillment_readiness_report(
        settings=selected_settings,
        repo_root=selected_repo_root,
    ).report
    ios_deploy_runbook = build_ios_deploy_runbook_report(
        mode="local",
        repo_root=selected_repo_root,
    )
    ios_device_launch_rehearsal = build_ios_device_launch_rehearsal_readiness_report(
        repo_root=selected_repo_root,
    ).report
    final_resources = build_final_resources_preflight_report(
        repo_root=selected_repo_root,
    ).report
    resource_handoff = build_resource_handoff_report(
        settings=selected_settings,
        repo_root=selected_repo_root,
    )
    capabilities = _capabilities(
        source_acceptance=source_acceptance,
        final_acceptance=final_acceptance,
        three_d_evaluation=three_d_evaluation,
        npc_evaluation=npc_evaluation,
        visual_regression=visual_regression,
        live_provider_evidence=live_provider_evidence,
        print_fulfillment_readiness=print_fulfillment_readiness,
        ios_deploy_runbook=ios_deploy_runbook,
        ios_device_launch_rehearsal=ios_device_launch_rehearsal,
        final_resources=final_resources,
        resource_handoff=resource_handoff,
    )
    summary = _summary(capabilities)
    status = _overall_status(capabilities)
    report = {
        "kind": "final_showcase_readiness_report",
        "status": status,
        "summary": summary,
        "capabilities": capabilities,
        "capabilities_by_id": {row["id"]: row for row in capabilities},
        "first_blocker": _first_blocker(capabilities),
        "operator_actions": _operator_actions(capabilities),
        "commands": _commands(),
        "evidence": {
            "ios_showcase_acceptance": _evidence_summary(source_acceptance),
            "final_acceptance_readiness": _evidence_summary(final_acceptance),
            "three_d_evaluation_readiness": _evidence_summary(three_d_evaluation),
            "npc_agent_evaluation_readiness": _evidence_summary(npc_evaluation),
            "visual_regression_readiness": _evidence_summary(visual_regression),
            "live_provider_evidence": _evidence_summary(live_provider_evidence),
            "print_fulfillment_readiness": _evidence_summary(
                print_fulfillment_readiness,
            ),
            "ios_deploy_runbook": _evidence_summary(ios_deploy_runbook),
            "ios_device_launch_rehearsal_readiness": _evidence_summary(
                ios_device_launch_rehearsal,
            ),
            "final_resources_preflight": _evidence_summary(final_resources),
            "resource_handoff": _evidence_summary(resource_handoff),
        },
        "safety": {
            "commands_run": False,
            "provider_calls": False,
            "live_provider_calls": False,
            "writes_backend_env": False,
            "writes_ios_deploy_config": False,
            "global_mutation": False,
            "xcode_or_signing": False,
            "keychain_writes": False,
            "provider_secrets_in_report": False,
            "raw_private_context_in_report": False,
            "raw_media_in_report": False,
            "payment_links_in_report": False,
            "local_paths_in_report": False,
        },
    }
    sanitized = _sanitize_report(report, selected_repo_root)
    return FinalShowcaseReadinessResult(
        exit_code=0 if sanitized["status"] == "ready" else 2,
        report=sanitized,
    )


def _capabilities(
    *,
    source_acceptance: dict[str, Any],
    final_acceptance: dict[str, Any],
    three_d_evaluation: dict[str, Any],
    npc_evaluation: dict[str, Any],
    visual_regression: dict[str, Any],
    live_provider_evidence: dict[str, Any],
    print_fulfillment_readiness: dict[str, Any],
    ios_deploy_runbook: dict[str, Any],
    ios_device_launch_rehearsal: dict[str, Any],
    final_resources: dict[str, Any],
    resource_handoff: dict[str, Any],
) -> list[dict[str, Any]]:
    rows = [
        _ios_deployable_capability(
            ios_deploy_runbook=ios_deploy_runbook,
            ios_device_launch_rehearsal=ios_device_launch_rehearsal,
        ),
        _capture_scanning_capability(source_acceptance),
        _generated_3d_capability(
            three_d_evaluation=three_d_evaluation,
            live_provider_evidence=live_provider_evidence,
        ),
        _ai_agent_npc_capability(
            npc_evaluation=npc_evaluation,
            live_provider_evidence=live_provider_evidence,
        ),
        _print_fulfillment_capability(print_fulfillment_readiness),
        _provider_key_handoff_capability(
            final_resources=final_resources,
            resource_handoff=resource_handoff,
            live_provider_evidence=live_provider_evidence,
        ),
        _simple_report_capability(
            capability_id="functional_regression",
            label="Functional regression",
            report=final_acceptance,
            command="make final-acceptance-local",
            ready_detail="Local final acceptance evidence is ready.",
            missing_detail="Local final acceptance report is missing.",
            blocked_detail="Local final acceptance has blockers.",
        ),
        _simple_report_capability(
            capability_id="visual_regression",
            label="Visual regression",
            report=visual_regression,
            command="make visual-regression-local",
            ready_detail="Full-showcase visual regression evidence is ready.",
            missing_detail="Visual regression report is missing.",
            blocked_detail="Visual regression has blockers.",
        ),
        _privacy_safety_capability(
            source_acceptance=source_acceptance,
            final_acceptance=final_acceptance,
            three_d_evaluation=three_d_evaluation,
            npc_evaluation=npc_evaluation,
            visual_regression=visual_regression,
            live_provider_evidence=live_provider_evidence,
            print_fulfillment_readiness=print_fulfillment_readiness,
            ios_deploy_runbook=ios_deploy_runbook,
            ios_device_launch_rehearsal=ios_device_launch_rehearsal,
            final_resources=final_resources,
            resource_handoff=resource_handoff,
        ),
    ]
    return sorted(rows, key=lambda row: CAPABILITY_ORDER.index(row["id"]))


def _ios_deployable_capability(
    *,
    ios_deploy_runbook: dict[str, Any],
    ios_device_launch_rehearsal: dict[str, Any],
) -> dict[str, Any]:
    runbook_status = _normalized_status(str(ios_deploy_runbook.get("status", "blocked")))
    raw_rehearsal_status = str(ios_device_launch_rehearsal.get("status", "missing"))
    rehearsal_status = _normalized_status(
        raw_rehearsal_status,
    )
    if runbook_status == "ready" and rehearsal_status == "ready":
        status = "ready"
    elif runbook_status == "blocked":
        status = "blocked"
    else:
        status = "partial"
    classification = (
        "ios_rehearsal_missing"
        if rehearsal_status == "blocked"
        and raw_rehearsal_status == "missing"
        else "ios_deploy_evidence"
    )
    detail = (
        "iOS deploy runbook and device launch rehearsal must both be ready."
        if status != "ready"
        else "iOS deploy runbook and launch rehearsal evidence are ready."
    )
    return _capability(
        capability_id="ios_deployable",
        label="iOS deployable",
        status=status,
        classification=classification,
        command="make ios-device-launch-rehearsal",
        detail=detail,
        evidence=[
            f"ios_deploy_runbook:{ios_deploy_runbook.get('status', 'unknown')}",
            (
                "ios_device_launch_rehearsal_readiness:"
                f"{ios_device_launch_rehearsal.get('status', 'unknown')}"
            ),
        ],
    )


def _capture_scanning_capability(source_acceptance: dict[str, Any]) -> dict[str, Any]:
    features = source_acceptance.get("required_features", [])
    passed_feature_ids = {
        str(feature.get("id"))
        for feature in features
        if isinstance(feature, dict) and feature.get("status") == "passed"
    }
    missing_features = sorted(SOURCE_CAPTURE_FEATURES - passed_feature_ids)
    if not missing_features:
        return _capability(
            capability_id="capture_scanning",
            label="Capture and scanning",
            status="ready",
            classification="source_acceptance_passed",
            command="cd services/backend && uv run pytest tests/test_ios_showcase_acceptance.py",
            detail="iOS source acceptance covers camera, guided scan, ARKit scan, and capture-to-3D review.",
            evidence=[f"source_features:{len(SOURCE_CAPTURE_FEATURES)}"],
        )
    return _capability(
        capability_id="capture_scanning",
        label="Capture and scanning",
        status="blocked",
        classification="missing_source_acceptance",
        command="cd services/backend && uv run pytest tests/test_ios_showcase_acceptance.py",
        detail=f"Missing source acceptance features: {', '.join(missing_features[:3])}.",
        evidence=[f"missing_source_features:{len(missing_features)}"],
    )


def _generated_3d_capability(
    *,
    three_d_evaluation: dict[str, Any],
    live_provider_evidence: dict[str, Any],
) -> dict[str, Any]:
    local_status = _normalized_status(str(three_d_evaluation.get("status", "missing")))
    if local_status != "ready":
        return _capability(
            capability_id="game_asset_3d_generation",
            label="Game asset 3D generation",
            status="blocked",
            classification="local_3d_evaluation_not_ready",
            command="make backend-evaluate-3d",
            detail="Local 3D generation evaluation must be ready before final showcase.",
            evidence=[f"three_d_evaluation:{three_d_evaluation.get('status', 'unknown')}"],
        )
    live_status = _normalized_status(str(live_provider_evidence.get("status", "missing")))
    status = "ready" if live_status == "ready" else "partial"
    return _capability(
        capability_id="game_asset_3d_generation",
        label="Game asset 3D generation",
        status=status,
        classification="live_3d_provider_unproven" if status == "partial" else "ready",
        command="make live-provider-evidence",
        detail=(
            "Local 3D proof is ready; live Meshy evidence still needs consent."
            if status == "partial"
            else "Local and live 3D evidence are ready."
        ),
        evidence=[
            f"three_d_evaluation:{three_d_evaluation.get('status', 'unknown')}",
            f"live_provider_evidence:{live_provider_evidence.get('status', 'unknown')}",
        ],
    )


def _ai_agent_npc_capability(
    *,
    npc_evaluation: dict[str, Any],
    live_provider_evidence: dict[str, Any],
) -> dict[str, Any]:
    local_status = _normalized_status(str(npc_evaluation.get("status", "missing")))
    if local_status != "ready":
        return _capability(
            capability_id="ai_agent_npc",
            label="AI Agent NPC",
            status="blocked",
            classification="local_npc_evaluation_not_ready",
            command="make backend-evaluate-npc",
            detail="Local NPC Agent evaluation must be ready before final showcase.",
            evidence=[f"npc_agent_evaluation:{npc_evaluation.get('status', 'unknown')}"],
        )
    live_status = _normalized_status(str(live_provider_evidence.get("status", "missing")))
    status = "ready" if live_status == "ready" else "partial"
    return _capability(
        capability_id="ai_agent_npc",
        label="AI Agent NPC",
        status=status,
        classification="live_openai_provider_unproven" if status == "partial" else "ready",
        command="make live-provider-evidence",
        detail=(
            "Local NPC Agent proof is ready; live OpenAI evidence still needs consent."
            if status == "partial"
            else "Local and live NPC Agent evidence are ready."
        ),
        evidence=[
            f"npc_agent_evaluation:{npc_evaluation.get('status', 'unknown')}",
            f"live_provider_evidence:{live_provider_evidence.get('status', 'unknown')}",
        ],
    )


def _print_fulfillment_capability(report: dict[str, Any]) -> dict[str, Any]:
    raw_status = str(report.get("status", "missing"))
    status = _normalized_status(raw_status)
    first_blocker = report.get("first_blocker")
    if status == "ready":
        classification = "print_fulfillment_ready"
        detail = "Local and configured print fulfillment quote handoff evidence are ready."
    elif isinstance(first_blocker, dict):
        classification = str(
            first_blocker.get("classification", "print_fulfillment_not_ready")
        )
        detail = str(
            first_blocker.get("detail", "Print fulfillment readiness is not ready.")
        )
    else:
        classification = "missing_print_fulfillment_readiness"
        detail = "Print fulfillment readiness report is missing or incomplete."
    return _capability(
        capability_id="print_fulfillment",
        label="Print fulfillment",
        status=status,
        classification=classification,
        command="make print-fulfillment-readiness",
        detail=detail,
        evidence=[f"{report.get('kind', 'print_fulfillment_readiness')}:{raw_status}"],
    )


def _provider_key_handoff_capability(
    *,
    final_resources: dict[str, Any],
    resource_handoff: dict[str, Any],
    live_provider_evidence: dict[str, Any],
) -> dict[str, Any]:
    final_resource_status = _normalized_status(str(final_resources.get("status", "missing")))
    resource_handoff_status = _normalized_status(
        str(resource_handoff.get("overall_status", "blocked")),
    )
    live_status = _normalized_status(str(live_provider_evidence.get("status", "missing")))
    if "blocked" in {final_resource_status, resource_handoff_status}:
        status = "blocked"
    elif live_status == "ready":
        status = "ready"
    else:
        status = "partial"
    if status == "partial":
        classification = "live_provider_evidence_unproven"
    elif status == "ready":
        classification = "provider_handoff_ready"
    else:
        classification = "provider_handoff_incomplete"
    return _capability(
        capability_id="provider_key_handoff",
        label="Provider and key handoff",
        status=status,
        classification=classification,
        command="make final-resources-preflight",
        detail=(
            "Final resources, resource handoff, and live provider evidence must be ready."
            if status != "ready"
            else "Final resources, resource handoff, and live provider evidence are ready."
        ),
        evidence=[
            f"final_resources:{final_resources.get('status', 'unknown')}",
            f"resource_handoff:{resource_handoff.get('overall_status', 'unknown')}",
            f"live_provider_evidence:{live_provider_evidence.get('status', 'unknown')}",
        ],
    )


def _simple_report_capability(
    *,
    capability_id: str,
    label: str,
    report: dict[str, Any],
    command: str,
    ready_detail: str,
    missing_detail: str,
    blocked_detail: str,
) -> dict[str, Any]:
    raw_status = str(report.get("status", report.get("overall_status", "missing")))
    status = _normalized_status(raw_status)
    if status == "ready":
        detail = ready_detail
        classification = "report_ready"
    elif raw_status == "missing":
        detail = missing_detail
        classification = "missing_report"
    else:
        detail = blocked_detail
        classification = "report_blocked"
        blocker = _first_report_blocker(report)
        if blocker is not None:
            classification = str(blocker.get("classification", classification))
            detail = (
                f"{blocked_detail} {blocker.get('id', 'unknown_blocker')}: "
                f"{blocker.get('detail', blocker.get('status', 'blocked'))}"
            )
    return _capability(
        capability_id=capability_id,
        label=label,
        status=status,
        classification=classification,
        command=command,
        detail=detail,
        evidence=[f"{report.get('kind', capability_id)}:{raw_status}"],
    )


def _first_report_blocker(report: dict[str, Any]) -> dict[str, Any] | None:
    blockers = report.get("blockers")
    if not isinstance(blockers, list):
        return None
    for blocker in blockers:
        if isinstance(blocker, dict):
            return blocker
    return None


def _privacy_safety_capability(**reports: dict[str, Any]) -> dict[str, Any]:
    unsafe_flags = []
    for report_id, report in reports.items():
        safety = report.get("safety")
        if not isinstance(safety, dict):
            continue
        for key in (
            "provider_secrets_in_report",
            "raw_private_context_in_report",
            "raw_media_in_report",
            "payment_links_in_report",
            "local_paths_in_report",
        ):
            if safety.get(key) is True:
                unsafe_flags.append(f"{report_id}.{key}")
    if unsafe_flags:
        return _capability(
            capability_id="privacy_safety",
            label="Privacy and safety",
            status="blocked",
            classification="unsafe_report_content",
            command="make final-showcase-readiness",
            detail=f"Unsafe report flags: {', '.join(unsafe_flags[:3])}.",
            evidence=unsafe_flags[:5],
        )
    return _capability(
        capability_id="privacy_safety",
        label="Privacy and safety",
        status="ready",
        classification="sanitized_read_only_reports",
        command="make final-showcase-readiness",
        detail="Readiness reports are sanitized and read-only.",
        evidence=["commands_run:false", "live_provider_calls:false"],
    )


def _capability(
    *,
    capability_id: str,
    label: str,
    status: str,
    classification: str,
    command: str,
    detail: str,
    evidence: list[str],
    required: bool = True,
) -> dict[str, Any]:
    return {
        "id": capability_id,
        "label": label,
        "status": _normalized_status(status),
        "classification": classification,
        "required": required,
        "evidence": evidence,
        "command": command,
        "detail": detail,
    }


def _summary(capabilities: list[dict[str, Any]]) -> dict[str, int]:
    summary = {"ready": 0, "partial": 0, "blocked": 0}
    for capability in capabilities:
        status = str(capability["status"])
        summary[status if status in summary else "blocked"] += 1
    return summary


def _overall_status(capabilities: list[dict[str, Any]]) -> str:
    required = [row for row in capabilities if row.get("required", True)]
    if any(row["status"] == "blocked" for row in required):
        return "blocked"
    if any(row["status"] == "partial" for row in required):
        return "partial"
    return "ready"


def _first_blocker(capabilities: list[dict[str, Any]]) -> dict[str, Any] | None:
    for capability in capabilities:
        if capability.get("required", True) and capability.get("status") != "ready":
            return capability
    return None


def _operator_actions(capabilities: list[dict[str, Any]]) -> list[str]:
    actions = [
        row["command"]
        for row in capabilities
        if row.get("required", True) and row.get("status") != "ready"
    ]
    if any("live_provider" in row.get("classification", "") for row in capabilities):
        actions.append(
            "run make live-provider-evidence to refresh live provider evidence after cost consent"
        )
    actions.extend(["make final-rehearsal-local", "make final-showcase-readiness"])
    return _dedupe(actions)[:8]


def _commands() -> list[str]:
    return [
        "make final-rehearsal-local",
        "make ios-device-launch-rehearsal",
        "make live-provider-evidence",
        "make print-fulfillment-readiness",
        "make final-showcase-readiness",
        (
            "cd services/backend && uv run python -m myth_forge_api.cli "
            "final-showcase-readiness --repo-root ../.. "
            "--output .local/final-showcase-readiness.json"
        ),
    ]


def _evidence_summary(report: dict[str, Any]) -> dict[str, Any]:
    summary = {
        "kind": report.get("kind"),
        "status": report.get("status", report.get("overall_status")),
    }
    raw_summary = report.get("summary")
    if isinstance(raw_summary, dict):
        summary["summary"] = {
            str(key): value
            for key, value in raw_summary.items()
            if isinstance(value, (int, str, bool)) or value is None
        }
    return summary


def _combined_status(statuses: list[str]) -> str:
    normalized = [_normalized_status(status) for status in statuses]
    if "blocked" in normalized:
        return "blocked"
    if "partial" in normalized:
        return "partial"
    return "ready"


def _normalized_status(status: str) -> str:
    normalized = status.strip().lower()
    if normalized in {"ready", "passed", "ok"}:
        return "ready"
    if normalized in {"partial", "manual", "live", "optional", "waiting"}:
        return "partial"
    return "blocked"


def _dedupe(items: list[str]) -> list[str]:
    seen = set()
    deduped = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return deduped


def _sanitize_report(report: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    text = json.dumps(report, sort_keys=True)
    sanitized = text
    replacements = [
        (re.escape(str(repo_root)), "[repo]"),
        (r"/Users/[^\s,;\"']+", "[home]"),
        (r"/tmp/[^\s,;\"']+", "[tmp]"),
        (r"sk-[A-Za-z0-9._-]+", "[redacted]"),
        (r"Bearer\s+[A-Za-z0-9._~+/=:\-]+", "Bearer [redacted]"),
        (r"api[_-]?key\s*[=:]\s*[^\s,;\"']+", "api_key=[redacted]"),
        (r"(private_message|raw_context|message_body)\s*:\s*[^\n\"]+", "[redacted]"),
        (r"local-capture://[^\s,;\"']+", "local-capture://[redacted]"),
        (r"file://[^\s,;\"']+", "file://[redacted]"),
        (r"https?://checkout\.[^\s,;\"']+", "[redacted-payment-link]"),
        (r"https?://pay\.[^\s,;\"']+", "[redacted-payment-link]"),
    ]
    for pattern, replacement in replacements:
        sanitized = re.sub(pattern, replacement, sanitized)
    return json.loads(sanitized)


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parents[3]
