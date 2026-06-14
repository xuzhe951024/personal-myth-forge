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
from myth_forge_api.final_resource_apply_preview import (
    build_final_resource_apply_preview_report,
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
from myth_forge_api.local_showcase_smoke import build_local_showcase_smoke_report
from myth_forge_api.npc_agent_evaluation_readiness import (
    build_npc_agent_evaluation_readiness_report,
)
from myth_forge_api.operator_actions import (
    FINAL_RESOURCE_VALIDATION_ACTION_ROOTS,
    IOS_DEPLOY_CONFIG_ACTION,
    PROVIDER_LIVE_HANDOFF_ACTION,
    add_final_resource_validation_command,
    add_mobile_deploy_validation_command,
    normalize_operator_action,
    prefer_guarded_print_quote_handoff_actions,
    prefer_project_local_ios_deploy_handoff_actions,
    prefer_provider_fill_guide_handoff_actions,
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
    "local_showcase_smoke",
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
FINAL_SHOWCASE_OPERATOR_ACTION_LIMIT = 32
FINAL_SHOWCASE_REPORT_ACTION_LIMIT = 4
FINAL_SHOWCASE_IOS_REHEARSAL_ACTION_LIMIT = 12
FINAL_SHOWCASE_IOS_REHEARSAL_PRIORITY_PREFIXES = (
    "final_handoff_index:",
    "ios_device_launch_certificate:",
)
FINAL_SHOWCASE_IOS_REHEARSAL_PRIORITY_MAKE_TARGETS = (
    "make final-rehearsal-local",
    "make final-configured-preflight",
    "make final-demo-launch-configured",
    "make final-handoff-index",
    "make ios-deploy-runbook-local",
)
FINAL_RESOURCE_APPLY_PREVIEW_ACTION = "make final-resource-apply-preview"
FINAL_RESOURCE_APPLY_ACTION = "make final-apply-resources"
FINAL_SHOWCASE_PROVIDER_HANDOFF_ACTION_MARKERS = (
    "provider-handoff",
    "live-provider",
    "live_provider",
    "live-provider-evidence",
)
FINAL_SHOWCASE_PROVIDER_CHAIN_ACTION = PROVIDER_LIVE_HANDOFF_ACTION
FINAL_SHOWCASE_WEAK_PROVIDER_ACTION_ROOTS = {
    FINAL_RESOURCE_APPLY_PREVIEW_ACTION,
    (
        "make final-resource-apply-preview; rerun make provider-handoff; "
        "rerun make live-provider-evidence"
    ),
    "make final-resource-apply-preview; rerun make live-provider-evidence",
    "make provider-handoff",
    "make live-provider-evidence",
    "run make live-provider-evidence to refresh live provider evidence after cost consent",
}
FINAL_SHOWCASE_PRINT_HANDOFF_ACTION_MARKERS = (
    "treatstock",
    "print-quote",
    "print_quote",
    "/v1/print-quotes",
)
FINAL_SHOWCASE_BACKEND_DEVICE_DEMO_ACTION_MARKERS = (
    "backend-device-demo",
)
FINAL_SHOWCASE_PRINT_READINESS_VALIDATION = "make print-fulfillment-readiness"
FINAL_SHOWCASE_LOCAL_REHEARSAL_COMMAND = "make final-rehearsal-local"
FINAL_SHOWCASE_SELF_OPERATOR_ACTIONS = {"make final-showcase-readiness"}
IOS_DEPLOY_DESTINATION_LABEL = "Deployment.local.xcconfig"
IOS_DEPLOY_VALIDATION_COMMAND = "make mobile-deploy-preflight"
FINAL_RESOURCES_ENV_LABEL = "final-resources.env"
IOS_DEPLOY_RESOURCE_IDS = {
    "DEVELOPMENT_TEAM",
    "PRODUCT_BUNDLE_IDENTIFIER",
    "PMF_BACKEND_BASE_URL",
}
FINAL_SHOWCASE_SOURCE_ACTION_PREFIXES = (
    "final_rehearsal_local:",
    "mobile_deploy_preflight_evidence:",
    "final_acceptance_local:",
    "ios_deploy_runbook_local:",
    "final_configured_preflight:",
    "final_handoff_index:",
    "ios_device_launch_certificate:",
)
FINAL_SHOWCASE_DUPLICATE_DEVICE_ROOTS = {
    (
        "start backend-device-demo before device checks: "
        "make backend-device-demo; rerun make mobile-deploy-preflight"
    ),
    (
        "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig; "
        "rerun make mobile-deploy-preflight"
    ),
    (
        "accept the Xcode license outside Codex, then rerun "
        "make mobile-xcode-build-evidence"
    ),
}
CONFIGURED_LIVE_EVIDENCE_BUNDLE_PATH = Path(
    "services/backend/.local/configured-live-evidence-bundle.json"
)
MOBILE_DEPLOY_PREFLIGHT_EVIDENCE_PATH = Path(
    "services/backend/.local/mobile-deploy-preflight-evidence.json"
)
MOBILE_DEPLOY_PREFLIGHT_EVIDENCE_COMMAND = "make mobile-deploy-preflight-evidence"
MOBILE_XCODE_BUILD_EVIDENCE_PATH = Path(
    "services/backend/.local/mobile-xcode-build-evidence.json"
)
MOBILE_XCODE_BUILD_EVIDENCE_COMMAND = "make mobile-xcode-build-evidence"


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
    local_showcase_smoke = build_local_showcase_smoke_report().report
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
    configured_live_evidence_bundle = _load_configured_live_evidence_bundle_report(
        selected_repo_root,
    )
    mobile_deploy_preflight_evidence = _load_mobile_deploy_preflight_evidence_report(
        selected_repo_root,
    )
    mobile_xcode_build_evidence = _load_mobile_xcode_build_evidence_report(
        selected_repo_root,
    )
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
    final_resource_apply_preview = build_final_resource_apply_preview_report(
        repo_root=selected_repo_root,
    ).report
    resource_handoff = build_resource_handoff_report(
        settings=selected_settings,
        repo_root=selected_repo_root,
    )
    capabilities = _capabilities(
        source_acceptance=source_acceptance,
        local_showcase_smoke=local_showcase_smoke,
        final_acceptance=final_acceptance,
        three_d_evaluation=three_d_evaluation,
        npc_evaluation=npc_evaluation,
        visual_regression=visual_regression,
        live_provider_evidence=live_provider_evidence,
        configured_live_evidence_bundle=configured_live_evidence_bundle,
        mobile_deploy_preflight_evidence=mobile_deploy_preflight_evidence,
        mobile_xcode_build_evidence=mobile_xcode_build_evidence,
        print_fulfillment_readiness=print_fulfillment_readiness,
        ios_deploy_runbook=ios_deploy_runbook,
        ios_device_launch_rehearsal=ios_device_launch_rehearsal,
        final_resources=final_resources,
        final_resource_apply_preview=final_resource_apply_preview,
        resource_handoff=resource_handoff,
    )
    device_action_bundle = _device_action_bundle(
        capabilities,
        mobile_deploy_preflight_evidence=mobile_deploy_preflight_evidence,
        mobile_xcode_build_evidence=mobile_xcode_build_evidence,
    )
    capabilities = _capabilities_with_device_action_commands(
        capabilities,
        device_action_bundle=device_action_bundle,
    )
    summary = _summary(capabilities)
    status = _overall_status(capabilities)
    first_blocker = _first_blocker(
        capabilities,
        device_action_bundle=device_action_bundle,
    )
    next_action = _next_action(
        capabilities,
        device_action_bundle=device_action_bundle,
    )
    operator_actions = _operator_actions(
        capabilities,
        next_action=next_action,
        action_reports=[
            ios_device_launch_rehearsal,
            mobile_deploy_preflight_evidence,
            mobile_xcode_build_evidence,
            live_provider_evidence,
            configured_live_evidence_bundle,
            print_fulfillment_readiness,
            final_resource_apply_preview,
            final_resources,
            resource_handoff,
            final_acceptance,
            visual_regression,
        ],
    )
    device_action_bundle = _device_action_bundle_with_saved_next_action(
        device_action_bundle,
        operator_actions,
    )
    report = {
        "kind": "final_showcase_readiness_report",
        "status": status,
        "summary": summary,
        "capabilities": capabilities,
        "capabilities_by_id": {row["id"]: row for row in capabilities},
        "first_blocker": first_blocker,
        "next_action": next_action,
        "device_action_bundle": device_action_bundle,
        "operator_actions": operator_actions,
        "commands": _commands(),
        "evidence": {
            "ios_showcase_acceptance": _evidence_summary(source_acceptance),
            "local_showcase_smoke": _evidence_summary(local_showcase_smoke),
            "final_acceptance_readiness": _evidence_summary(final_acceptance),
            "three_d_evaluation_readiness": _evidence_summary(three_d_evaluation),
            "npc_agent_evaluation_readiness": _evidence_summary(npc_evaluation),
            "visual_regression_readiness": _evidence_summary(visual_regression),
            "live_provider_evidence": _evidence_summary(live_provider_evidence),
            "configured_live_evidence_bundle": _evidence_summary(
                configured_live_evidence_bundle,
            ),
            "mobile_deploy_preflight_evidence": _evidence_summary(
                mobile_deploy_preflight_evidence,
            ),
            "mobile_xcode_build_evidence": _evidence_summary(
                mobile_xcode_build_evidence,
            ),
            "print_fulfillment_readiness": _evidence_summary(
                print_fulfillment_readiness,
            ),
            "ios_deploy_runbook": _evidence_summary(ios_deploy_runbook),
            "ios_device_launch_rehearsal_readiness": _evidence_summary(
                ios_device_launch_rehearsal,
            ),
            "final_resources_preflight": _evidence_summary(final_resources),
            "final_resource_apply_preview": _evidence_summary(
                final_resource_apply_preview,
            ),
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
    local_showcase_smoke: dict[str, Any],
    final_acceptance: dict[str, Any],
    three_d_evaluation: dict[str, Any],
    npc_evaluation: dict[str, Any],
    visual_regression: dict[str, Any],
    live_provider_evidence: dict[str, Any],
    configured_live_evidence_bundle: dict[str, Any],
    mobile_deploy_preflight_evidence: dict[str, Any],
    mobile_xcode_build_evidence: dict[str, Any],
    print_fulfillment_readiness: dict[str, Any],
    ios_deploy_runbook: dict[str, Any],
    ios_device_launch_rehearsal: dict[str, Any],
    final_resources: dict[str, Any],
    final_resource_apply_preview: dict[str, Any],
    resource_handoff: dict[str, Any],
) -> list[dict[str, Any]]:
    rows = [
        _ios_deployable_capability(
            ios_deploy_runbook=ios_deploy_runbook,
            ios_device_launch_rehearsal=ios_device_launch_rehearsal,
        ),
        _capture_scanning_capability(source_acceptance),
        _local_showcase_smoke_capability(local_showcase_smoke),
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
            final_resource_apply_preview=final_resource_apply_preview,
            resource_handoff=resource_handoff,
            live_provider_evidence=live_provider_evidence,
            configured_live_evidence_bundle=configured_live_evidence_bundle,
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
            local_showcase_smoke=local_showcase_smoke,
            final_acceptance=final_acceptance,
            three_d_evaluation=three_d_evaluation,
            npc_evaluation=npc_evaluation,
            visual_regression=visual_regression,
            live_provider_evidence=live_provider_evidence,
            configured_live_evidence_bundle=configured_live_evidence_bundle,
            mobile_deploy_preflight_evidence=mobile_deploy_preflight_evidence,
            mobile_xcode_build_evidence=mobile_xcode_build_evidence,
            print_fulfillment_readiness=print_fulfillment_readiness,
            ios_deploy_runbook=ios_deploy_runbook,
            ios_device_launch_rehearsal=ios_device_launch_rehearsal,
            final_resources=final_resources,
            final_resource_apply_preview=final_resource_apply_preview,
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


def _local_showcase_smoke_capability(report: dict[str, Any]) -> dict[str, Any]:
    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    safety = report.get("safety") if isinstance(report.get("safety"), dict) else {}
    raw_status = str(report.get("status", "missing"))
    failed = _non_negative_int(summary.get("failed"))
    http_steps = _non_negative_int(summary.get("http_steps"))
    npc_ticks = _non_negative_int(summary.get("npc_ticks"))
    downloads = _non_negative_int(summary.get("downloads"))
    evidence = [
        f"{report.get('kind', 'local_showcase_smoke_report')}:{raw_status}",
        f"http_steps:{http_steps}",
        f"npc_ticks:{npc_ticks}",
        f"downloads:{downloads}",
    ]
    unsafe_flags = _local_showcase_smoke_unsafe_flags(safety)
    checks_passed = (
        raw_status == "succeeded"
        and failed == 0
        and http_steps >= 6
        and npc_ticks >= 2
        and downloads >= 3
    )
    if checks_passed and not unsafe_flags:
        return _capability(
            capability_id="local_showcase_smoke",
            label="Local showcase smoke",
            status="ready",
            classification="local_showcase_smoke_ready",
            command="make local-showcase-smoke",
            detail="Local capture-to-3D-to-NPC-to-print smoke proof is ready.",
            evidence=evidence,
        )
    classification = (
        "local_showcase_smoke_safety_failed"
        if unsafe_flags
        else "local_showcase_smoke_failed"
    )
    detail = "Local showcase smoke must pass before final showcase readiness."
    if unsafe_flags:
        detail = f"Local showcase smoke safety flags failed: {', '.join(unsafe_flags[:3])}."
    return _capability(
        capability_id="local_showcase_smoke",
        label="Local showcase smoke",
        status="blocked",
        classification=classification,
        command="make local-showcase-smoke",
        detail=detail,
        evidence=evidence + unsafe_flags[:5],
    )


def _local_showcase_smoke_unsafe_flags(safety: dict[str, Any]) -> list[str]:
    unsafe_flags = [
        key
        for key in (
            "provider_calls",
            "live_provider_calls",
            "global_mutation",
            "starts_server",
            "writes_repo_local_media",
            "provider_secrets_in_report",
            "raw_media_in_report",
            "local_paths_in_report",
            "payment_links_in_report",
        )
        if safety.get(key) is True
    ]
    if safety.get("uses_temporary_storage") is not True:
        unsafe_flags.append("uses_temporary_storage:false")
    return unsafe_flags


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
    command = "make live-provider-evidence"
    validation_command = None
    requires_live_provider_consent = None
    if status == "partial":
        child_command, child_validation_command, child_requires_consent = (
            _report_next_action_metadata(live_provider_evidence)
        )
        command = (
            _operator_action_with_validation(child_command, child_validation_command)
            or command
        )
        validation_command = child_validation_command or None
        requires_live_provider_consent = child_requires_consent
    return _capability(
        capability_id="game_asset_3d_generation",
        label="Game asset 3D generation",
        status=status,
        classification="live_3d_provider_unproven" if status == "partial" else "ready",
        command=command,
        detail=(
            "Local 3D proof is ready; live Meshy evidence still needs consent."
            if status == "partial"
            else "Local and live 3D evidence are ready."
        ),
        evidence=[
            f"three_d_evaluation:{three_d_evaluation.get('status', 'unknown')}",
            f"live_provider_evidence:{live_provider_evidence.get('status', 'unknown')}",
        ],
        validation_command=validation_command,
        requires_live_provider_consent=requires_live_provider_consent,
        completion_requires_live_provider_consent=(
            True if status == "partial" else None
        ),
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
    command = "make live-provider-evidence"
    validation_command = None
    requires_live_provider_consent = None
    if status == "partial":
        child_command, child_validation_command, child_requires_consent = (
            _report_next_action_metadata(live_provider_evidence)
        )
        command = (
            _operator_action_with_validation(child_command, child_validation_command)
            or command
        )
        validation_command = child_validation_command or None
        requires_live_provider_consent = child_requires_consent
    return _capability(
        capability_id="ai_agent_npc",
        label="AI Agent NPC",
        status=status,
        classification="live_openai_provider_unproven" if status == "partial" else "ready",
        command=command,
        detail=(
            "Local NPC Agent proof is ready; live OpenAI evidence still needs consent."
            if status == "partial"
            else "Local and live NPC Agent evidence are ready."
        ),
        evidence=[
            f"npc_agent_evaluation:{npc_evaluation.get('status', 'unknown')}",
            f"live_provider_evidence:{live_provider_evidence.get('status', 'unknown')}",
        ],
        validation_command=validation_command,
        requires_live_provider_consent=requires_live_provider_consent,
        completion_requires_live_provider_consent=(
            True if status == "partial" else None
        ),
    )


def _print_fulfillment_capability(report: dict[str, Any]) -> dict[str, Any]:
    raw_status = str(report.get("status", "missing"))
    status = _normalized_status(raw_status)
    first_blocker = report.get("first_blocker")
    command = "make print-fulfillment-readiness"
    validation_command = ""
    requires_cost_consent = False
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
        child_command, child_validation_command = _report_next_action_command(report)
        command = (
            _operator_action_with_validation(child_command, child_validation_command)
            or command
        )
        validation_command = child_validation_command
        next_action = report.get("next_action")
        if isinstance(next_action, dict):
            requires_cost_consent = bool(next_action.get("requires_cost_consent"))
    else:
        classification = "missing_print_fulfillment_readiness"
        detail = "Print fulfillment readiness report is missing or incomplete."
    return _capability(
        capability_id="print_fulfillment",
        label="Print fulfillment",
        status=status,
        classification=classification,
        command=command,
        detail=detail,
        evidence=[f"{report.get('kind', 'print_fulfillment_readiness')}:{raw_status}"],
        validation_command=validation_command or None,
        requires_cost_consent=requires_cost_consent or None,
    )


def _provider_key_handoff_capability(
    *,
    final_resources: dict[str, Any],
    final_resource_apply_preview: dict[str, Any],
    resource_handoff: dict[str, Any],
    live_provider_evidence: dict[str, Any],
    configured_live_evidence_bundle: dict[str, Any],
) -> dict[str, Any]:
    final_resource_status = _normalized_status(str(final_resources.get("status", "missing")))
    apply_preview_status = _normalized_status(
        str(final_resource_apply_preview.get("status", "missing")),
    )
    resource_handoff_status = _normalized_status(
        str(resource_handoff.get("overall_status", "blocked")),
    )
    live_status = _normalized_status(str(live_provider_evidence.get("status", "missing")))
    configured_bundle_status = _normalized_status(
        str(configured_live_evidence_bundle.get("status", "missing")),
    )
    local_resource_statuses = {
        final_resource_status,
        apply_preview_status,
        resource_handoff_status,
    }
    validation_command = ""
    if "blocked" in local_resource_statuses:
        status = "blocked"
        classification = "provider_handoff_incomplete"
        command = PROVIDER_LIVE_HANDOFF_ACTION
        validation_command = "make live-provider-evidence"
    elif live_status != "ready":
        status = "partial"
        classification = "live_provider_evidence_unproven"
        command = "make live-provider-evidence"
    elif configured_bundle_status != "ready":
        status = "partial"
        classification = "configured_evidence_bundle_unproven"
        command = "make configured-live-evidence-bundle"
    else:
        status = "ready"
        classification = "provider_handoff_ready"
        command = "make final-showcase-readiness"
    return _capability(
        capability_id="provider_key_handoff",
        label="Provider and key handoff",
        status=status,
        classification=classification,
        command=command,
        detail=(
            "Final resources, apply preview, resource handoff, live provider evidence, and configured evidence bundle must be ready."
            if status != "ready"
            else "Final resources, apply preview, resource handoff, live provider evidence, and configured evidence bundle are ready."
        ),
        validation_command=validation_command or None,
        evidence=[
            f"final_resources:{final_resources.get('status', 'unknown')}",
            (
                "final_resource_apply_preview:"
                f"{final_resource_apply_preview.get('status', 'unknown')}"
            ),
            f"resource_handoff:{resource_handoff.get('overall_status', 'unknown')}",
            f"live_provider_evidence:{live_provider_evidence.get('status', 'unknown')}",
            (
                "configured_live_evidence_bundle:"
                f"{configured_live_evidence_bundle.get('status', 'unknown')}"
            ),
        ],
    )


def _report_next_action_metadata(
    report: dict[str, Any]
) -> tuple[str, str, bool | None]:
    next_action = report.get("next_action")
    if not isinstance(next_action, dict):
        return "", "", None
    command = str(next_action.get("command", "")).strip()
    source_validation_command = str(
        next_action.get("source_blocker_validation_command", "")
    ).strip()
    if command and source_validation_command:
        command = _operator_action_with_validation(
            command,
            source_validation_command,
        )
    validation_command = str(next_action.get("validation_command", "")).strip()
    consent = next_action.get("requires_live_provider_consent")
    requires_live_provider_consent = consent if isinstance(consent, bool) else None
    return command, validation_command, requires_live_provider_consent


def _report_next_action_command(report: dict[str, Any]) -> tuple[str, str]:
    command, validation_command, _ = _report_next_action_metadata(report)
    return command, validation_command


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
    validation_command = ""
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
            child_command, child_validation_command = _report_next_action_command(
                blocker,
            )
            command = child_command or command
            validation_command = child_validation_command
            detail = (
                f"{blocked_detail} {blocker.get('id', 'unknown_blocker')}: "
                f"{_report_blocker_detail(blocker)}"
            )
    return _capability(
        capability_id=capability_id,
        label=label,
        status=status,
        classification=classification,
        command=command,
        detail=detail,
        evidence=[f"{report.get('kind', capability_id)}:{raw_status}"],
        validation_command=validation_command or None,
    )


def _first_report_blocker(report: dict[str, Any]) -> dict[str, Any] | None:
    blockers = report.get("blockers")
    if not isinstance(blockers, list):
        return None
    for blocker in blockers:
        if isinstance(blocker, dict):
            return blocker
    return None


def _report_blocker_detail(blocker: dict[str, Any]) -> str:
    next_action = blocker.get("next_action")
    if isinstance(next_action, dict):
        command = str(next_action.get("command", "")).strip()
        validation_command = str(next_action.get("validation_command", "")).strip()
        detail = str(next_action.get("detail", "")).strip()
        parts = []
        if command:
            parts.append(f"Next action: {command}")
        if validation_command and f"rerun {validation_command}" not in command:
            parts.append(f"rerun {validation_command}")
        if detail:
            parts.append(detail)
        formatted = " | ".join(parts)
        if formatted:
            return formatted
    return str(blocker.get("detail", blocker.get("status", "blocked")))


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


def _load_mobile_deploy_preflight_evidence_report(repo_root: Path) -> dict[str, Any]:
    relative_path = MOBILE_DEPLOY_PREFLIGHT_EVIDENCE_PATH.as_posix()
    path = repo_root / MOBILE_DEPLOY_PREFLIGHT_EVIDENCE_PATH
    if not path.exists():
        return _mobile_deploy_preflight_evidence_stub(
            status="missing",
            classification="missing_report",
            detail=f"Missing {relative_path}.",
        )
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _mobile_deploy_preflight_evidence_stub(
            status="blocked",
            classification="unreadable_report",
            detail=f"{relative_path} is not valid JSON.",
        )
    if not isinstance(payload, dict):
        return _mobile_deploy_preflight_evidence_stub(
            status="blocked",
            classification="invalid_report_shape",
            detail=f"{relative_path} must contain a JSON object.",
        )
    if payload.get("kind") != "mobile_deploy_preflight_evidence_report":
        return _mobile_deploy_preflight_evidence_stub(
            status="blocked",
            classification="wrong_report_kind",
            detail="Expected mobile_deploy_preflight_evidence_report.",
        )
    return payload


def _load_mobile_xcode_build_evidence_report(repo_root: Path) -> dict[str, Any]:
    relative_path = MOBILE_XCODE_BUILD_EVIDENCE_PATH.as_posix()
    path = repo_root / MOBILE_XCODE_BUILD_EVIDENCE_PATH
    if not path.exists():
        return _mobile_xcode_build_evidence_stub(
            status="missing",
            classification="missing_report",
            detail=f"Missing {relative_path}.",
        )
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _mobile_xcode_build_evidence_stub(
            status="blocked",
            classification="unreadable_report",
            detail=f"{relative_path} is not valid JSON.",
        )
    if not isinstance(payload, dict):
        return _mobile_xcode_build_evidence_stub(
            status="blocked",
            classification="invalid_report_shape",
            detail=f"{relative_path} must contain a JSON object.",
        )
    if payload.get("kind") != "mobile_xcode_build_evidence_report":
        return _mobile_xcode_build_evidence_stub(
            status="blocked",
            classification="wrong_report_kind",
            detail="Expected mobile_xcode_build_evidence_report.",
        )
    return payload


def _mobile_deploy_preflight_evidence_stub(
    *,
    status: str,
    classification: str,
    detail: str,
) -> dict[str, Any]:
    return {
        "kind": "mobile_deploy_preflight_evidence_report",
        "status": status,
        "command": MOBILE_DEPLOY_PREFLIGHT_EVIDENCE_COMMAND,
        "checks": [
            {
                "id": "mobile_deploy_preflight_evidence",
                "label": "Mobile deploy preflight evidence",
                "status": status,
                "classification": classification,
                "detail": detail,
            }
        ],
        "operator_actions": [
            "run make mobile-deploy-preflight-evidence after backend-device-demo is reachable"
        ],
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


def _mobile_xcode_build_evidence_stub(
    *,
    status: str,
    classification: str,
    detail: str,
) -> dict[str, Any]:
    return {
        "kind": "mobile_xcode_build_evidence_report",
        "status": status,
        "classification": classification,
        "command": "make mobile-xcode-build",
        "checks": [
            {
                "id": "xcode_build_gate",
                "label": "Xcode build gate",
                "status": status,
                "classification": classification,
                "detail": detail,
            }
        ],
        "operator_actions": [
            "run make mobile-xcode-build-evidence after deploy preflight is ready"
        ],
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


def _load_configured_live_evidence_bundle_report(repo_root: Path) -> dict[str, Any]:
    relative_path = CONFIGURED_LIVE_EVIDENCE_BUNDLE_PATH.as_posix()
    path = repo_root / CONFIGURED_LIVE_EVIDENCE_BUNDLE_PATH
    if not path.exists():
        return _configured_live_evidence_bundle_stub(
            status="missing",
            classification="missing_report",
            detail=f"Missing {relative_path}.",
        )
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _configured_live_evidence_bundle_stub(
            status="blocked",
            classification="unreadable_report",
            detail=f"{relative_path} is not valid JSON.",
        )
    if not isinstance(payload, dict):
        return _configured_live_evidence_bundle_stub(
            status="blocked",
            classification="invalid_report_shape",
            detail=f"{relative_path} must contain a JSON object.",
        )
    if payload.get("kind") != "configured_live_evidence_bundle_report":
        return _configured_live_evidence_bundle_stub(
            status="blocked",
            classification="wrong_report_kind",
            detail="Expected configured_live_evidence_bundle_report.",
        )
    return payload


def _configured_live_evidence_bundle_stub(
    *,
    status: str,
    classification: str,
    detail: str,
) -> dict[str, Any]:
    return {
        "kind": "configured_live_evidence_bundle_report",
        "status": status,
        "summary": {
            "evidence_files": 0,
            "evidence_ready": 0,
            "evidence_missing": 1 if status == "missing" else 0,
            "evidence_blocked": 1 if status != "missing" else 0,
            "commands_run": 0,
        },
        "current_blocker": {
            "id": "configured_live_evidence_bundle",
            "label": "Configured live evidence bundle",
            "status": status,
            "classification": classification,
            "command": "make configured-live-evidence-bundle",
            "detail": detail,
        },
        "operator_actions": [
            "run make configured-live-evidence-bundle to refresh configured evidence bundle"
        ],
        "commands": ["make configured-live-evidence-bundle"],
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
    validation_command: str | None = None,
    requires_cost_consent: bool | None = None,
    requires_live_provider_consent: bool | None = None,
    completion_requires_live_provider_consent: bool | None = None,
) -> dict[str, Any]:
    row = {
        "id": capability_id,
        "label": label,
        "status": _normalized_status(status),
        "classification": classification,
        "required": required,
        "evidence": evidence,
        "command": command,
        "detail": detail,
    }
    if validation_command:
        row["validation_command"] = validation_command
    if requires_cost_consent is not None:
        row["requires_cost_consent"] = requires_cost_consent
    if requires_live_provider_consent is not None:
        row["requires_live_provider_consent"] = requires_live_provider_consent
    if completion_requires_live_provider_consent is not None:
        row["completion_requires_live_provider_consent"] = (
            completion_requires_live_provider_consent
        )
    return _capability_with_next_action(row)


def _capability_with_next_action(row: dict[str, Any]) -> dict[str, Any]:
    if row["status"] == "ready":
        row.pop("next_action", None)
        return row
    next_action = {
        "id": row["id"],
        "label": row["label"],
        "status": row["status"],
        "classification": row["classification"],
        "command": row["command"],
        "detail": row["detail"],
        "source": "capability",
    }
    for key in (
        "validation_command",
        "requires_cost_consent",
        "requires_live_provider_consent",
        "completion_requires_live_provider_consent",
    ):
        if key in row:
            next_action[key] = row[key]
    row["next_action"] = next_action
    return row


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


def _first_blocker(
    capabilities: list[dict[str, Any]],
    *,
    device_action_bundle: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    for capability in capabilities:
        if capability.get("required", True) and capability.get("status") != "ready":
            return _capability_with_device_action_detail(
                capability,
                device_action_bundle=device_action_bundle,
            )
    return None


def _next_action(
    capabilities: list[dict[str, Any]],
    *,
    device_action_bundle: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    blocker = _first_blocker(
        capabilities,
        device_action_bundle=device_action_bundle,
    )
    if blocker is None:
        return None
    command = str(blocker.get("command", ""))
    validation_command = str(blocker.get("validation_command", "")).strip()
    if blocker.get("id") == "ios_deployable":
        device_action_source = _preferred_device_action_hint_source(
            device_action_bundle or {},
        )
        child_next_action = _device_action_child_next_action(device_action_source)
        command = (
            str(child_next_action.get("command", "")).strip()
            or _preferred_device_action_command(device_action_bundle)
            or command
        )
        validation_command = str(
            child_next_action.get("validation_command", ""),
        ).strip()
        command = _operator_action_with_validation(command, validation_command)
    action = {
        "id": str(blocker.get("id", "")),
        "label": str(blocker.get("label", "")),
        "status": str(blocker.get("status", "")),
        "classification": str(blocker.get("classification", "")),
        "command": command,
        "detail": str(blocker.get("detail", "")),
        "source": "first_blocker",
    }
    if validation_command:
        action["validation_command"] = validation_command
    return action


def _capability_with_device_action_detail(
    capability: dict[str, Any],
    *,
    device_action_bundle: dict[str, Any] | None,
) -> dict[str, Any]:
    if capability.get("id") != "ios_deployable":
        return capability
    hint = _first_device_action_hint(device_action_bundle)
    if not hint:
        return capability
    result = dict(capability)
    detail = str(result.get("detail", ""))
    result["detail"] = " | ".join(part for part in [detail, hint] if part)
    command, validation_command = _preferred_device_action_blocker_command(
        device_action_bundle,
    )
    if command:
        result["command"] = command
    if validation_command:
        result["validation_command"] = validation_command
    return _capability_with_next_action(result)


def _capabilities_with_device_action_commands(
    capabilities: list[dict[str, Any]],
    *,
    device_action_bundle: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    return [
        _capability_with_device_action_command(
            capability,
            device_action_bundle=device_action_bundle,
        )
        for capability in capabilities
    ]


def _capability_with_device_action_command(
    capability: dict[str, Any],
    *,
    device_action_bundle: dict[str, Any] | None,
) -> dict[str, Any]:
    if capability.get("id") != "ios_deployable":
        return capability
    command, validation_command = _preferred_device_action_blocker_command(
        device_action_bundle,
    )
    if not command:
        return capability
    result = dict(capability)
    result["command"] = command
    if validation_command:
        result["validation_command"] = validation_command
    return _capability_with_next_action(result)


def _preferred_device_action_hint_source(
    device_action_bundle: dict[str, Any],
) -> dict[str, Any] | None:
    actions = device_action_bundle.get("actions")
    if isinstance(actions, list):
        for action in actions:
            if not isinstance(action, dict):
                continue
            if action.get("id") != "run_mobile_deploy_preflight":
                continue
            if str(action.get("status", "")) == "ready":
                continue
            if str(action.get("evidence_status", "")) == "missing":
                continue
            if str(action.get("evidence_detail", "")).strip():
                return action
    first_action = device_action_bundle.get("first_action")
    return first_action if isinstance(first_action, dict) else None


def _preferred_device_action_command(
    device_action_bundle: dict[str, Any] | None,
) -> str:
    if not isinstance(device_action_bundle, dict):
        return ""
    action = _preferred_device_action_hint_source(device_action_bundle)
    if not isinstance(action, dict):
        return ""
    command = str(action.get("command", "")).strip()
    detail = str(action.get("evidence_detail", "")).strip()
    if not command or not detail:
        return ""
    if str(action.get("evidence_status", "")) == "missing":
        return ""
    return command


def _preferred_device_action_blocker_command(
    device_action_bundle: dict[str, Any] | None,
) -> tuple[str, str]:
    if not isinstance(device_action_bundle, dict):
        return "", ""
    action = _preferred_device_action_hint_source(device_action_bundle)
    if not isinstance(action, dict):
        return "", ""
    child_next_action = _device_action_child_next_action(action)
    command = (
        str(child_next_action.get("command", "")).strip()
        or _preferred_device_action_command(device_action_bundle)
    )
    validation_command = str(
        child_next_action.get("validation_command", ""),
    ).strip()
    return _operator_action_with_validation(command, validation_command), validation_command


def _device_action_child_next_action(
    device_action_source: dict[str, Any] | None,
) -> dict[str, Any]:
    if not isinstance(device_action_source, dict):
        return {}
    next_action = device_action_source.get("next_action")
    return next_action if isinstance(next_action, dict) else {}


def _first_device_action_hint(
    device_action_bundle: dict[str, Any] | None,
) -> str:
    if not isinstance(device_action_bundle, dict):
        return ""
    action = _preferred_device_action_hint_source(device_action_bundle)
    if not isinstance(action, dict):
        return ""
    if str(action.get("evidence_status", "")) == "missing":
        return ""
    child_next_action = _device_action_child_next_action(action)
    command = (
        str(child_next_action.get("command", "")).strip()
        or str(action.get("command", "")).strip()
    )
    validation_command = str(
        child_next_action.get("validation_command", ""),
    ).strip()
    command = _operator_action_with_validation(command, validation_command)
    detail = str(action.get("evidence_detail", ""))
    if not command or not detail:
        return ""
    return f"Next device action: {command} | {detail}"


def _device_action_bundle(
    capabilities: list[dict[str, Any]],
    *,
    mobile_deploy_preflight_evidence: dict[str, Any],
    mobile_xcode_build_evidence: dict[str, Any],
) -> dict[str, Any]:
    capabilities_by_id = {str(row.get("id", "")): row for row in capabilities}
    ios_status = str(
        capabilities_by_id.get("ios_deployable", {}).get("status", "blocked"),
    )
    normalized_ios_status = _normalized_status(ios_status)
    preflight_status = _normalized_report_status(mobile_deploy_preflight_evidence)
    preflight_raw_status = str(
        mobile_deploy_preflight_evidence.get("status", "missing"),
    )
    backend_detail = _mobile_deploy_preflight_backend_evidence_detail(
        mobile_deploy_preflight_evidence,
    )
    preflight_detail = _mobile_deploy_preflight_evidence_detail(
        mobile_deploy_preflight_evidence,
    )
    preflight_metadata = {
        "evidence_status": preflight_raw_status,
        "evidence_source": MOBILE_DEPLOY_PREFLIGHT_EVIDENCE_PATH.as_posix(),
        "evidence_detail": preflight_detail,
        "validation_command": MOBILE_DEPLOY_PREFLIGHT_EVIDENCE_COMMAND,
    }
    child_next_action = mobile_deploy_preflight_evidence.get("next_action")
    if isinstance(child_next_action, dict):
        preflight_metadata["next_action"] = child_next_action
    xcode_status = _normalized_report_status(mobile_xcode_build_evidence)
    xcode_raw_status = str(mobile_xcode_build_evidence.get("status", "missing"))
    xcode_metadata = {
        "evidence_status": xcode_raw_status,
        "evidence_source": MOBILE_XCODE_BUILD_EVIDENCE_PATH.as_posix(),
        "evidence_detail": _mobile_xcode_build_evidence_detail(
            mobile_xcode_build_evidence
        ),
        "validation_command": MOBILE_XCODE_BUILD_EVIDENCE_COMMAND,
    }
    xcode_actions = _report_operator_actions(mobile_xcode_build_evidence)[
        :FINAL_SHOWCASE_REPORT_ACTION_LIMIT
    ]
    if xcode_actions:
        xcode_metadata["operator_actions"] = xcode_actions
    actions = [
        _device_action(
            action_id="start_backend_device_demo",
            label="Start backend device demo",
            status="ready" if preflight_status == "ready" else "blocked",
            classification="manual_backend_required",
            command="make backend-device-demo",
            detail="Start the LAN-reachable backend before running iPhone preflight.",
            blocks=["ios_deployable", "functional_regression"],
            extra={**preflight_metadata, "evidence_detail": backend_detail},
        ),
        _device_action(
            action_id="run_mobile_deploy_preflight",
            label="Run mobile deploy preflight",
            status=preflight_status,
            classification="manual_preflight_required",
            command="make mobile-deploy-preflight",
            detail="Verify the iPhone can reach the backend and read launch config.",
            blocks=["ios_deployable", "functional_regression"],
            extra=preflight_metadata,
        ),
        _device_action(
            action_id="resolve_xcode_build_gate",
            label="Resolve Xcode build gate",
            status=xcode_status,
            classification="manual_xcode_or_signing_required",
            command="open Xcode and resolve signing/build gate",
            detail="Resolve signing or build issues in Xcode before device launch proof.",
            blocks=["ios_deployable"],
            xcode_or_signing=True,
            extra=xcode_metadata,
        ),
        _device_action(
            action_id="run_ios_device_launch_rehearsal",
            label="Run iOS device launch rehearsal",
            status=normalized_ios_status,
            classification="manual_device_rehearsal_required",
            command="make ios-device-launch-rehearsal",
            detail="Refresh the final iOS device rehearsal evidence after preflight passes.",
            blocks=["ios_deployable"],
        ),
    ]
    return {
        "id": "ios_device_manual_actions",
        "label": "iOS Device Manual Actions",
        "status": normalized_ios_status,
        "summary": _device_action_bundle_summary(actions),
        "first_action": _first_device_action(actions),
        "actions": actions,
        "safety": {
            "commands_run": False,
            "global_mutation": False,
            "provider_calls": False,
            "live_provider_calls": False,
            "writes_backend_env": False,
            "writes_ios_deploy_config": False,
            "xcode_or_signing": False,
            "keychain_writes": False,
        },
    }


def _device_action_bundle_with_saved_next_action(
    bundle: dict[str, Any],
    operator_actions: list[str],
) -> dict[str, Any]:
    first_action = bundle.get("first_action")
    if not isinstance(first_action, dict) or not operator_actions:
        return bundle
    first_operator_action = str(operator_actions[0]).strip()
    if not first_operator_action:
        return bundle
    command = str(first_action.get("command", "")).strip()
    if first_operator_action == command:
        return bundle

    saved_next_action = {
        "id": str(first_action.get("id", "device_action")),
        "label": str(first_action.get("label", "Device action")),
        "status": str(first_action.get("status", "blocked")),
        "command": first_operator_action,
        "detail": str(
            first_action.get("evidence_detail") or first_action.get("detail") or "",
        ).strip(),
        "source": "operator_actions",
    }
    validation_command = str(first_action.get("validation_command", "")).strip()
    child_next_action = _device_action_child_next_action(first_action)
    child_validation_command = str(
        child_next_action.get("validation_command", ""),
    ).strip()
    if child_validation_command:
        validation_command = child_validation_command
    if validation_command:
        saved_next_action["validation_command"] = validation_command

    first_action["saved_next_action"] = saved_next_action
    actions = bundle.get("actions")
    if isinstance(actions, list):
        first_action_id = str(first_action.get("id", ""))
        for action in actions:
            if not isinstance(action, dict):
                continue
            if str(action.get("id", "")) == first_action_id:
                action["saved_next_action"] = saved_next_action
                break
    return bundle


def _device_action(
    *,
    action_id: str,
    label: str,
    status: str,
    classification: str,
    command: str,
    detail: str,
    blocks: list[str],
    xcode_or_signing: bool = False,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    action = {
        "id": action_id,
        "label": label,
        "status": _normalized_status(status),
        "classification": classification,
        "command": command,
        "detail": detail,
        "source": "final_showcase_readiness",
        "blocks": blocks,
        "manual": True,
        "global_action": False,
        "provider_calls": False,
        "xcode_or_signing": xcode_or_signing,
    }
    if extra:
        action.update(extra)
    validation_command = str(action.get("validation_command", "")).strip()
    if command.startswith("make ") and validation_command:
        action["command"] = _operator_action_with_validation(
            command,
            validation_command,
        )
    return action


def _mobile_deploy_preflight_evidence_detail(report: dict[str, Any]) -> str:
    if _normalized_report_status(report) == "ready":
        return _first_check_detail(
            report,
            fallback="Mobile deploy preflight evidence is not ready.",
        )
    return _check_detail_summary(
        report,
        fallback="Mobile deploy preflight evidence is not ready.",
    )


def _mobile_deploy_preflight_backend_evidence_detail(report: dict[str, Any]) -> str:
    return _preferred_check_detail(
        report,
        preferred_ids=("backend_health", "backend_base_url"),
        fallback=_mobile_deploy_preflight_evidence_detail(report),
    )


def _mobile_xcode_build_evidence_detail(report: dict[str, Any]) -> str:
    return _first_check_detail(
        report,
        fallback="Xcode build evidence is not ready.",
    )


def _first_check_detail(report: dict[str, Any], *, fallback: str) -> str:
    details = _check_details(report)
    if details:
        return details[0]
    return fallback


def _preferred_check_detail(
    report: dict[str, Any],
    *,
    preferred_ids: tuple[str, ...],
    fallback: str,
) -> str:
    checks = report.get("checks")
    if isinstance(checks, list):
        preferred = set(preferred_ids)
        for check in checks:
            if not isinstance(check, dict):
                continue
            if str(check.get("id", "")) not in preferred:
                continue
            detail = check.get("detail")
            if isinstance(detail, str) and detail:
                return detail
    return fallback


def _check_detail_summary(report: dict[str, Any], *, fallback: str) -> str:
    details = _check_details(report)
    if not details:
        return fallback
    visible = details[:3]
    if len(details) > len(visible):
        visible.append(f"+{len(details) - len(visible)} more")
    return "; ".join(visible)


def _check_details(report: dict[str, Any]) -> list[str]:
    checks = report.get("checks")
    if not isinstance(checks, list):
        return []
    details: list[str] = []
    seen: set[str] = set()
    for check in checks:
        if not isinstance(check, dict):
            continue
        detail = check.get("detail")
        if not isinstance(detail, str):
            continue
        normalized = detail.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        details.append(normalized)
    return details


def _device_action_bundle_summary(actions: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "actions": len(actions),
        "ready": sum(1 for action in actions if action.get("status") == "ready"),
        "manual": sum(1 for action in actions if action.get("manual") is True),
        "blocked": sum(1 for action in actions if action.get("status") == "blocked"),
        "partial": sum(1 for action in actions if action.get("status") == "partial"),
        "xcode_or_signing": sum(
            1 for action in actions if action.get("xcode_or_signing") is True
        ),
        "global_actions": sum(
            1 for action in actions if action.get("global_action") is True
        ),
        "provider_calls": sum(
            1 for action in actions if action.get("provider_calls") is True
        ),
    }


def _first_device_action(actions: list[dict[str, Any]]) -> dict[str, Any] | None:
    for action in actions:
        if action.get("status") == "ready":
            continue
        if action.get("id") != "run_mobile_deploy_preflight":
            continue
        promoted = _device_action_with_child_next_action(action)
        if promoted is not None:
            return promoted
    for action in actions:
        if action.get("status") != "ready":
            return action
    return actions[0] if actions else None


def _device_action_with_child_next_action(
    action: dict[str, Any],
) -> dict[str, Any] | None:
    child_next_action = _device_action_child_next_action(action)
    command = str(child_next_action.get("command", "")).strip()
    if not command:
        return None
    promoted = dict(action)
    promoted["command"] = command
    validation_command = str(
        child_next_action.get("validation_command", ""),
    ).strip()
    if validation_command:
        promoted["validation_command"] = validation_command
    return promoted


def _operator_actions(
    capabilities: list[dict[str, Any]],
    *,
    next_action: dict[str, Any] | None,
    action_reports: list[dict[str, Any]],
) -> list[str]:
    actions: list[str] = []
    concrete = _next_action_operator_action(next_action)
    if concrete:
        actions.append(concrete)
    for report in action_reports:
        if _normalized_report_status(report) == "ready":
            continue
        actions.extend(_selected_report_operator_actions(report))
        actions.extend(_mobile_deploy_resource_operator_actions(report))
    actions.extend(["make final-rehearsal-local", "make final-showcase-readiness"])
    actions.extend(
        action
        for row in capabilities
        if row.get("required", True) and row.get("status") != "ready"
        for action in (_capability_operator_action(row),)
        if action
    )
    if any("live_provider" in row.get("classification", "") for row in capabilities):
        actions.append(
            "run make live-provider-evidence to refresh live provider evidence after cost consent"
        )
    deduped_actions = _prioritize_showcase_operator_actions(
        _filter_showcase_operator_actions(_dedupe_operator_actions(actions)),
    )
    return [
        add_final_resource_validation_command(action)
        for action in deduped_actions[:FINAL_SHOWCASE_OPERATOR_ACTION_LIMIT]
    ]


def _next_action_operator_action(next_action: dict[str, Any] | None) -> str:
    if not isinstance(next_action, dict):
        return ""
    command = str(next_action.get("command", "")).strip()
    validation_command = str(next_action.get("validation_command", "")).strip()
    return _operator_action_with_validation(command, validation_command)


def _capability_operator_action(row: dict[str, Any]) -> str:
    command = str(row.get("command", "")).strip()
    validation_command = str(row.get("validation_command", "")).strip()
    return _operator_action_with_validation(command, validation_command)


def _operator_action_with_validation(command: str, validation_command: str) -> str:
    if not command:
        return ""
    action = command
    if not validation_command:
        return normalize_operator_action(action)
    validation_suffix = f"; rerun {validation_command}"
    if validation_suffix not in action:
        action = f"{action}{validation_suffix}"
    return normalize_operator_action(action)


def _normalized_report_status(report: dict[str, Any]) -> str:
    return _normalized_status(
        str(report.get("status", report.get("overall_status", "missing"))),
    )


def _report_operator_actions(report: dict[str, Any]) -> list[str]:
    raw_actions = report.get("operator_actions")
    if not isinstance(raw_actions, list):
        return []
    return [
        _showcase_destination_aware_action(
            _final_showcase_operator_action(
                _validation_aware_operator_action(
                    normalize_operator_action(str(action))
                )
            )
        )
        for action in raw_actions
        if isinstance(action, str) and action
    ]


def _filter_showcase_operator_actions(actions: list[str]) -> list[str]:
    filtered = [
        action
        for action in actions
        if action not in FINAL_SHOWCASE_SELF_OPERATOR_ACTIONS
        and not _is_validation_only_print_action(action)
    ]
    return _drop_bare_local_rehearsal_when_specific_actions_exist(filtered)


def _drop_bare_local_rehearsal_when_specific_actions_exist(
    actions: list[str],
) -> list[str]:
    has_specific_action = any(
        _operator_action_bare_root(action) != FINAL_SHOWCASE_LOCAL_REHEARSAL_COMMAND
        and _is_specific_final_showcase_action(action)
        for action in actions
    )
    if not has_specific_action:
        return actions
    return [
        action
        for action in actions
        if _operator_action_bare_root(action) != FINAL_SHOWCASE_LOCAL_REHEARSAL_COMMAND
    ]


def _is_specific_final_showcase_action(action: str) -> bool:
    return _operator_action_bare_root(action) != FINAL_SHOWCASE_LOCAL_REHEARSAL_COMMAND


def _prioritize_showcase_operator_actions(actions: list[str]) -> list[str]:
    if not actions:
        return []
    first = actions[:1]
    rest = actions[1:]
    device_demo_actions = [
        action for action in rest if _is_backend_device_demo_action(action)
    ]
    backend_url_actions = [
        action
        for action in rest
        if action not in device_demo_actions
        and _is_backend_url_handoff_action(action)
    ]
    provider_actions = [
        action for action in rest if _is_provider_handoff_action(action)
    ]
    print_actions = [
        action for action in rest if _is_print_handoff_action(action)
    ]
    priority_actions = set(
        device_demo_actions + backend_url_actions + provider_actions + print_actions
    )
    remaining = [action for action in rest if action not in priority_actions]
    fallback_priority_actions = set(device_demo_actions + provider_actions + print_actions)
    fallback_remaining = [
        action for action in rest if action not in fallback_priority_actions
    ]
    if _is_mobile_deploy_handoff_action(first[0]):
        return (
            first
            + device_demo_actions
            + backend_url_actions
            + provider_actions
            + print_actions
            + remaining
        )
    return first + device_demo_actions + provider_actions + print_actions + fallback_remaining


def _is_provider_handoff_action(action: str) -> bool:
    lowered = action.lower()
    return any(
        marker in lowered
        for marker in FINAL_SHOWCASE_PROVIDER_HANDOFF_ACTION_MARKERS
    )


def _is_print_handoff_action(action: str) -> bool:
    lowered = action.lower()
    return any(
        marker in lowered
        for marker in FINAL_SHOWCASE_PRINT_HANDOFF_ACTION_MARKERS
    )


def _is_backend_device_demo_action(action: str) -> bool:
    lowered = action.lower()
    return any(
        marker in lowered
        for marker in FINAL_SHOWCASE_BACKEND_DEVICE_DEMO_ACTION_MARKERS
    )


def _is_backend_url_handoff_action(action: str) -> bool:
    lowered = action.lower()
    return (
        "pmf_backend_base_url" in lowered
        or "iphone-reachable lan url" in lowered
    )


def _is_mobile_deploy_handoff_action(action: str) -> bool:
    root = _operator_action_bare_root(action)
    return (
        "mobile-write-deploy-config-auto" in root
        and "mobile-deploy-preflight" in root
        and not _is_backend_device_demo_action(action)
    )


def _is_validation_only_print_action(action: str) -> bool:
    lowered = action.lower()
    if any(
        marker in lowered
        for marker in FINAL_SHOWCASE_PRINT_HANDOFF_ACTION_MARKERS
    ):
        return False
    _command, separator, validation = action.partition("; rerun ")
    return bool(separator) and validation.strip() == FINAL_SHOWCASE_PRINT_READINESS_VALIDATION


def _validation_aware_operator_action(action: str) -> str:
    return add_final_resource_validation_command(
        add_mobile_deploy_validation_command(action)
    )


def _showcase_destination_aware_action(action: str) -> str:
    command, separator, validation = action.partition("; rerun ")
    bare_command = _strip_final_showcase_source_prefixes(command.strip())
    replacement = _showcase_ios_destination_command(bare_command)
    if replacement is None:
        return action
    if separator or validation:
        return f"{replacement}; rerun {IOS_DEPLOY_VALIDATION_COMMAND}"
    return replacement


def _showcase_ios_destination_command(command: str) -> str | None:
    for resource_id in IOS_DEPLOY_RESOURCE_IDS:
        provide_action = f"provide {resource_id} in {FINAL_RESOURCES_ENV_LABEL}"
        fix_action = f"fix {resource_id} in {FINAL_RESOURCES_ENV_LABEL}"
        if command == provide_action:
            return f"provide {resource_id} in {IOS_DEPLOY_DESTINATION_LABEL}"
        if command == fix_action:
            return f"fix {resource_id} in {IOS_DEPLOY_DESTINATION_LABEL}"
    if command == "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL":
        return command
    return None


def _final_showcase_operator_action(action: str) -> str:
    command_part, detail_suffix = _split_detail_suffix(action)
    bare_root = _strip_final_showcase_source_prefixes(command_part)
    if bare_root == command_part:
        return action
    if bare_root.startswith("make "):
        return f"{bare_root}{detail_suffix}"
    if bare_root.startswith("run make "):
        return f"{bare_root.removeprefix('run ')}{detail_suffix}"
    if _is_ios_deploy_config_action_root(bare_root):
        return f"{bare_root}{detail_suffix}"
    return action


def _selected_report_operator_actions(report: dict[str, Any]) -> list[str]:
    actions = _report_operator_actions(report)
    if report.get("kind") != "ios_device_launch_rehearsal_readiness_report":
        return actions[:FINAL_SHOWCASE_REPORT_ACTION_LIMIT]
    selected = actions[:FINAL_SHOWCASE_REPORT_ACTION_LIMIT]
    selected.extend(
        action for action in actions if _is_ios_rehearsal_priority_action(action)
    )
    return _dedupe(selected)[:FINAL_SHOWCASE_IOS_REHEARSAL_ACTION_LIMIT]


def _mobile_deploy_resource_operator_actions(report: dict[str, Any]) -> list[str]:
    if report.get("kind") != "mobile_deploy_preflight_evidence_report":
        return []
    resources = _mobile_deploy_resource_rows(report)
    if not resources:
        return []
    actions: list[str] = []
    for resource in resources:
        if _normalized_status(str(resource.get("status", "missing"))) == "ready":
            continue
        resource_id = str(resource.get("id", "")).strip()
        if resource_id == "development_team":
            actions.append(
                "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig; "
                "rerun make mobile-deploy-preflight"
            )
        elif resource_id == "product_bundle_identifier":
            actions.append(
                "provide PRODUCT_BUNDLE_IDENTIFIER in Deployment.local.xcconfig; "
                "rerun make mobile-deploy-preflight"
            )
        elif resource_id == "backend_base_url":
            actions.append(
                "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL; "
                "rerun make mobile-deploy-preflight"
            )
    return actions


def _mobile_deploy_resource_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key in ("resources", "checks"):
        raw_rows = report.get(key)
        if not isinstance(raw_rows, list):
            continue
        rows.extend(row for row in raw_rows if isinstance(row, dict))
    return rows


def _is_ios_rehearsal_priority_action(action: str) -> bool:
    command_root = action.partition("; rerun ")[0].strip()
    return (
        action.startswith(FINAL_SHOWCASE_IOS_REHEARSAL_PRIORITY_PREFIXES)
        or command_root in FINAL_SHOWCASE_IOS_REHEARSAL_PRIORITY_MAKE_TARGETS
        or _is_ios_deploy_config_action_root(command_root)
        or _is_backend_device_demo_action(action)
    )


def _commands() -> list[str]:
    return [
        "make final-rehearsal-local",
        "make local-showcase-smoke",
        "make ios-device-launch-rehearsal",
        "make live-provider-evidence",
        "make configured-live-evidence-bundle",
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
    if normalized in {"ready", "passed", "ok", "succeeded"}:
        return "ready"
    if normalized in {"partial", "manual", "live", "optional", "waiting"}:
        return "partial"
    return "blocked"


def _non_negative_int(value: Any) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, int):
        return max(value, 0)
    return 0


def _dedupe(items: list[str]) -> list[str]:
    seen = set()
    deduped = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return deduped


def _dedupe_operator_actions(items: list[str]) -> list[str]:
    seen_exact: set[str] = set()
    normalized_items = [item.strip() for item in items if item.strip()]
    bare_roots = {
        _operator_action_bare_root(item)
        for item in normalized_items
        if not _is_source_prefixed_action(item)
    }
    deduped: list[str] = []
    for normalized in normalized_items:
        if normalized in seen_exact:
            continue
        bare_root = _operator_action_bare_root(normalized)
        if (
            _is_drop_candidate_source_prefix(normalized, bare_root)
            and bare_root in bare_roots
        ):
            continue
        seen_exact.add(normalized)
        deduped.append(normalized)
    deduped = _prefer_validation_aware_operator_actions(deduped)
    return _prefer_apply_preview_before_apply(
        prefer_project_local_ios_deploy_handoff_actions(
            prefer_provider_fill_guide_handoff_actions(
                prefer_guarded_print_quote_handoff_actions(
                    _prefer_bare_ios_deploy_writer_action(
                        _prefer_complete_provider_handoff_chain(deduped)
                    )
                )
            )
        )
    )


def _prefer_complete_provider_handoff_chain(actions: list[str]) -> list[str]:
    if FINAL_SHOWCASE_PROVIDER_CHAIN_ACTION not in actions:
        return actions
    return [
        action
        for action in actions
        if action == FINAL_SHOWCASE_PROVIDER_CHAIN_ACTION
        or action not in FINAL_SHOWCASE_WEAK_PROVIDER_ACTION_ROOTS
    ]


def _prefer_validation_aware_operator_actions(actions: list[str]) -> list[str]:
    validation_aware_roots: set[str] = set()
    for action in actions:
        roots = _validation_aware_action_roots(action)
        if roots is None:
            continue
        command_root, validation_root = roots
        validation_aware_roots.add(command_root)
        validation_aware_roots.add(validation_root)
    if not validation_aware_roots:
        return actions
    preferred: list[str] = []
    for action in actions:
        if _validation_aware_action_roots(action) is not None:
            preferred.append(action)
            continue
        if _operator_action_bare_root(action) in validation_aware_roots:
            continue
        preferred.append(action)
    return preferred


def _validation_aware_action_roots(action: str) -> tuple[str, str] | None:
    command_part, _detail_suffix = _split_detail_suffix(action)
    command, separator, validation = command_part.partition("; rerun ")
    if not separator:
        return None
    command_root = _operator_action_bare_root(command.strip())
    validation_root = _operator_action_bare_root(validation.strip())
    if not command_root or not validation_root:
        return None
    return command_root, validation_root


def _prefer_bare_ios_deploy_writer_action(actions: list[str]) -> list[str]:
    bare_writer_by_root = {
        _operator_action_bare_root(action): action
        for action in actions
        if _is_mobile_deploy_writer_action_root(_operator_action_bare_root(action))
        and not _split_detail_suffix(action)[1]
    }
    if not bare_writer_by_root:
        return actions

    preferred: list[str] = []
    seen: set[str] = set()
    for action in actions:
        root = _operator_action_bare_root(action)
        selected = bare_writer_by_root.get(root, action)
        if selected in seen:
            continue
        seen.add(selected)
        preferred.append(selected)
    return preferred


def _prefer_apply_preview_before_apply(actions: list[str]) -> list[str]:
    action_roots = {_operator_action_bare_root(action) for action in actions}
    if FINAL_RESOURCE_APPLY_PREVIEW_ACTION not in action_roots:
        return actions
    return [
        action
        for action in actions
        if _operator_action_bare_root(action) != FINAL_RESOURCE_APPLY_ACTION
    ]


def _operator_action_bare_root(action: str) -> str:
    command, _detail_suffix = _split_detail_suffix(action)
    command = _strip_final_showcase_source_prefixes(command)
    if _looks_like_operator_command(command):
        return command
    parts = command.split(": ")
    for index in range(len(parts) - 1, 0, -1):
        suffix = ": ".join(parts[index:]).strip()
        if not _looks_like_operator_command(suffix):
            continue
        return suffix
    return command


def _split_detail_suffix(action: str) -> tuple[str, str]:
    command, separator, detail = action.partition(" | ")
    if not separator:
        return action.strip(), ""
    return command.strip(), f"{separator}{detail}"


def _strip_final_showcase_source_prefixes(command: str) -> str:
    stripped = command
    while True:
        for prefix in FINAL_SHOWCASE_SOURCE_ACTION_PREFIXES:
            marker = f"{prefix} "
            if stripped.startswith(marker):
                stripped = stripped[len(marker) :].strip()
                break
        else:
            return stripped


def _is_source_prefixed_action(action: str) -> bool:
    return _operator_action_bare_root(action) != action.split(" | ", 1)[0].strip()


def _is_drop_candidate_source_prefix(action: str, bare_root: str) -> bool:
    if not _is_source_prefixed_action(action):
        return False
    if action.startswith(
        "final_rehearsal_local: mobile_deploy_preflight_evidence: "
    ):
        return True
    if _is_final_resource_action_root(bare_root):
        return True
    return bare_root in FINAL_SHOWCASE_DUPLICATE_DEVICE_ROOTS


def _is_final_resource_action_root(action_root: str) -> bool:
    return action_root.startswith(FINAL_RESOURCE_VALIDATION_ACTION_ROOTS)


def _is_ios_deploy_config_action_root(action_root: str) -> bool:
    return action_root.startswith(IOS_DEPLOY_CONFIG_ACTION)


def _is_mobile_deploy_writer_action_root(action_root: str) -> bool:
    return action_root.startswith(
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID make mobile-write-deploy-config-auto"
    )


def _looks_like_operator_command(value: str) -> bool:
    return value.startswith(
        (
            "provide ",
            "set ",
            "make ",
            "run ",
            "start ",
            "accept ",
            "after explicit ",
            "fill ",
        )
    )


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
        (r"checkout_url", "[redacted-payment-field]"),
    ]
    for pattern, replacement in replacements:
        sanitized = re.sub(pattern, replacement, sanitized)
    return json.loads(sanitized)


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parents[3]
