from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from fastapi.testclient import TestClient

from myth_forge_api.main import app


@dataclass(frozen=True)
class SourceRequirement:
    id: str
    label: str
    file: str
    contains: str


@dataclass(frozen=True)
class EndpointProbeResponse:
    status_code: int
    payload: dict[str, Any]
    text: str


@dataclass(frozen=True)
class MobileFinalLaunchReadinessAcceptanceResult:
    exit_code: int
    report: dict[str, Any]


EndpointGetter = Callable[[str], EndpointProbeResponse]

PMF_MODELS_PATH = "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift"
APP_CONFIGURATION_PATH = "apps/mobile/ios/App/AppConfiguration.swift"
API_CLIENT_PATH = (
    "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PersonalMythForgeAPIClient.swift"
)
FORGE_ROOT_VIEW_PATH = "apps/mobile/ios/App/ForgeRootView.swift"
DEVICE_PREFLIGHT_PATH = (
    "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/DevicePreflight.swift"
)
FINAL_LAUNCH_MOBILE_SUMMARY_PATH = (
    "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift"
)
FINAL_LAUNCH_STATUS_VIEW_PATH = "apps/mobile/ios/App/FinalLaunchStatusView.swift"
CORE_CONTRACT_TESTS_PATH = (
    "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift"
)

SOURCE_REQUIREMENTS = (
    SourceRequirement(
        "model_final_demo_launch_report",
        "Final launch report model",
        PMF_MODELS_PATH,
        "FinalDemoLaunchReport",
    ),
    SourceRequirement(
        "model_final_demo_launch_phase",
        "Final launch phase model",
        PMF_MODELS_PATH,
        "FinalDemoLaunchPhase",
    ),
    SourceRequirement(
        "model_live_call_policy",
        "Final launch live call policy model",
        PMF_MODELS_PATH,
        "FinalDemoLaunchLiveCallPolicy",
    ),
    SourceRequirement(
        "model_safety",
        "Final launch safety model",
        PMF_MODELS_PATH,
        "FinalDemoLaunchSafety",
    ),
    SourceRequirement(
        "model_final_resources_preflight",
        "Final resources preflight model",
        PMF_MODELS_PATH,
        "FinalResourcesPreflightReport",
    ),
    SourceRequirement(
        "model_final_resources_file",
        "Final resources file status model",
        PMF_MODELS_PATH,
        "FinalResourcesFileStatus",
    ),
    SourceRequirement(
        "model_final_resources_summary",
        "Final resources preflight summary model",
        PMF_MODELS_PATH,
        "FinalResourcesPreflightSummary",
    ),
    SourceRequirement(
        "model_final_launch_mode",
        "Final launch mode model",
        PMF_MODELS_PATH,
        "FinalLaunchMode",
    ),
    SourceRequirement(
        "model_final_launch_mode_display",
        "Final launch mode display label",
        PMF_MODELS_PATH,
        "displayLabel",
    ),
    SourceRequirement(
        "model_ios_deploy_runbook",
        "iOS deploy runbook report model",
        PMF_MODELS_PATH,
        "IOSDeployRunbookReport",
    ),
    SourceRequirement(
        "model_ios_deploy_runbook_field",
        "Final launch iOS deploy runbook field",
        PMF_MODELS_PATH,
        "iosDeployRunbook",
    ),
    SourceRequirement(
        "model_ios_device_launch_rehearsal",
        "iOS device launch rehearsal readiness model",
        PMF_MODELS_PATH,
        "IOSDeviceLaunchRehearsalReadinessReport",
    ),
    SourceRequirement(
        "model_ios_device_launch_rehearsal_field",
        "Final launch iOS device launch rehearsal field",
        PMF_MODELS_PATH,
        "iosDeviceLaunchRehearsalReadiness",
    ),
    SourceRequirement(
        "model_visual_regression_readiness",
        "Visual regression readiness model",
        PMF_MODELS_PATH,
        "VisualRegressionReadinessReport",
    ),
    SourceRequirement(
        "model_visual_regression_readiness_field",
        "Final launch visual regression readiness field",
        PMF_MODELS_PATH,
        "visualRegressionReadiness",
    ),
    SourceRequirement(
        "model_live_provider_evidence",
        "Live provider evidence model",
        PMF_MODELS_PATH,
        "LiveProviderEvidenceReport",
    ),
    SourceRequirement(
        "model_live_provider_evidence_field",
        "Final launch live provider evidence field",
        PMF_MODELS_PATH,
        "liveProviderEvidence",
    ),
    SourceRequirement(
        "model_resource_handoff",
        "Resource handoff report model",
        PMF_MODELS_PATH,
        "ResourceHandoffReport",
    ),
    SourceRequirement(
        "model_resource_handoff_field",
        "Final launch resource handoff field",
        PMF_MODELS_PATH,
        "resourceReport",
    ),
    SourceRequirement(
        "app_configuration_final_launch_mode",
        "App configuration final launch mode",
        APP_CONFIGURATION_PATH,
        "PMFFinalLaunchMode",
    ),
    SourceRequirement(
        "app_configuration_final_launch_mode_safe",
        "Safe app configuration final launch mode",
        APP_CONFIGURATION_PATH,
        "FinalLaunchMode.safe",
    ),
    SourceRequirement(
        "api_client_method",
        "Final launch API client method",
        API_CLIENT_PATH,
        "getFinalDemoLaunch",
    ),
    SourceRequirement(
        "api_client_endpoint",
        "Final launch API endpoint",
        API_CLIENT_PATH,
        "/v1/final-demo-launch",
    ),
    SourceRequirement(
        "api_client_modes",
        "Final launch mode allowlist",
        API_CLIENT_PATH,
        '"local", "configured"',
    ),
    SourceRequirement(
        "api_client_invalid_mode",
        "Final launch invalid mode guard",
        API_CLIENT_PATH,
        "Unsupported final demo launch mode.",
    ),
    SourceRequirement(
        "root_view_state",
        "Root view final launch state",
        FORGE_ROOT_VIEW_PATH,
        "finalDemoLaunch",
    ),
    SourceRequirement(
        "root_view_load_path",
        "Root view final launch load path",
        FORGE_ROOT_VIEW_PATH,
        "loadFinalDemoLaunch",
    ),
    SourceRequirement(
        "root_view_mode_state",
        "Root view final launch mode state",
        FORGE_ROOT_VIEW_PATH,
        "finalLaunchMode",
    ),
    SourceRequirement(
        "root_view_mode_picker",
        "Root view final launch mode picker",
        FORGE_ROOT_VIEW_PATH,
        'Picker("Final launch mode"',
    ),
    SourceRequirement(
        "root_view_mode_options",
        "Root view final launch mode options",
        FORGE_ROOT_VIEW_PATH,
        "FinalLaunchMode.allCases",
    ),
    SourceRequirement(
        "root_view_configured_mode",
        "Root view configured final launch call",
        FORGE_ROOT_VIEW_PATH,
        "getFinalDemoLaunch(mode: mode.rawValue)",
    ),
    SourceRequirement(
        "root_view_configured_initial_load",
        "Root view configured initial final launch load",
        FORGE_ROOT_VIEW_PATH,
        "loadFinalDemoLaunch(mode: finalLaunchMode)",
    ),
    SourceRequirement(
        "root_view_mode_reload",
        "Root view final launch mode reload",
        FORGE_ROOT_VIEW_PATH,
        ".onChange(of: finalLaunchMode)",
    ),
    SourceRequirement(
        "root_view_preflight_handoff",
        "Root view preflight handoff",
        FORGE_ROOT_VIEW_PATH,
        "DevicePreflightSummaryBuilder.build",
    ),
    SourceRequirement(
        "root_view_final_launch_status_panel",
        "Root view final launch status panel",
        FORGE_ROOT_VIEW_PATH,
        "FinalLaunchStatusView(",
    ),
    SourceRequirement(
        "root_view_final_launch_summary_builder",
        "Root view final launch summary builder",
        FORGE_ROOT_VIEW_PATH,
        "FinalLaunchMobileSummaryBuilder.build",
    ),
    SourceRequirement(
        "mobile_summary_builder",
        "Mobile final launch summary builder",
        FINAL_LAUNCH_MOBILE_SUMMARY_PATH,
        "FinalLaunchMobileSummaryBuilder",
    ),
    SourceRequirement(
        "mobile_summary_status",
        "Mobile final launch summary status",
        FINAL_LAUNCH_MOBILE_SUMMARY_PATH,
        "FinalLaunchMobileStatus",
    ),
    SourceRequirement(
        "mobile_summary_mode_policy_rows",
        "Mobile final launch mode policy rows",
        FINAL_LAUNCH_MOBILE_SUMMARY_PATH,
        "modePolicyRows",
    ),
    SourceRequirement(
        "mobile_summary_live_policy",
        "Mobile final launch live policy mapping",
        FINAL_LAUNCH_MOBILE_SUMMARY_PATH,
        "liveCallPolicy",
    ),
    SourceRequirement(
        "mobile_summary_ios_deploy_runbook_rows",
        "Mobile final launch iOS deploy runbook rows",
        FINAL_LAUNCH_MOBILE_SUMMARY_PATH,
        "deployRunbookRows",
    ),
    SourceRequirement(
        "mobile_summary_ios_deploy_command_rows",
        "Mobile final launch iOS deploy command rows",
        FINAL_LAUNCH_MOBILE_SUMMARY_PATH,
        "deployRunbookCommandRows",
    ),
    SourceRequirement(
        "mobile_summary_ios_deploy_safety_rows",
        "Mobile final launch iOS deploy safety rows",
        FINAL_LAUNCH_MOBILE_SUMMARY_PATH,
        "deployRunbookSafetyRows",
    ),
    SourceRequirement(
        "mobile_summary_launch_rehearsal_rows",
        "Mobile final launch rehearsal rows",
        FINAL_LAUNCH_MOBILE_SUMMARY_PATH,
        "launchRehearsalRows",
    ),
    SourceRequirement(
        "mobile_summary_visual_regression_rows",
        "Mobile final launch visual regression rows",
        FINAL_LAUNCH_MOBILE_SUMMARY_PATH,
        "visualRegressionRows",
    ),
    SourceRequirement(
        "mobile_summary_live_provider_evidence_rows",
        "Mobile final launch live provider evidence rows",
        FINAL_LAUNCH_MOBILE_SUMMARY_PATH,
        "liveProviderEvidenceRows",
    ),
    SourceRequirement(
        "mobile_summary_resource_handoff_rows",
        "Mobile final launch resource handoff rows",
        FINAL_LAUNCH_MOBILE_SUMMARY_PATH,
        "resourceHandoffRows",
    ),
    SourceRequirement(
        "mobile_summary_backend_resource_rows",
        "Mobile final launch backend resource rows",
        FINAL_LAUNCH_MOBILE_SUMMARY_PATH,
        "resourceHandoffBackendRows",
    ),
    SourceRequirement(
        "mobile_summary_ios_resource_rows",
        "Mobile final launch iOS resource rows",
        FINAL_LAUNCH_MOBILE_SUMMARY_PATH,
        "resourceHandoffIOSRows",
    ),
    SourceRequirement(
        "mobile_summary_redaction",
        "Mobile final launch summary redaction",
        FINAL_LAUNCH_MOBILE_SUMMARY_PATH,
        "sanitize",
    ),
    SourceRequirement(
        "mobile_status_view_title",
        "Mobile final launch status view title",
        FINAL_LAUNCH_STATUS_VIEW_PATH,
        "Final Launch Status",
    ),
    SourceRequirement(
        "mobile_status_view_resources",
        "Mobile final launch status resource actions",
        FINAL_LAUNCH_STATUS_VIEW_PATH,
        "resourceActions",
    ),
    SourceRequirement(
        "mobile_status_view_mode_section",
        "Mobile final launch mode section",
        FINAL_LAUNCH_STATUS_VIEW_PATH,
        "Mode",
    ),
    SourceRequirement(
        "mobile_status_view_ios_deploy_runbook",
        "Mobile final launch iOS deploy runbook section",
        FINAL_LAUNCH_STATUS_VIEW_PATH,
        "iOS Deploy Runbook",
    ),
    SourceRequirement(
        "mobile_status_view_ios_deploy_commands",
        "Mobile final launch iOS deploy commands section",
        FINAL_LAUNCH_STATUS_VIEW_PATH,
        "Deploy Commands",
    ),
    SourceRequirement(
        "mobile_status_view_ios_deploy_safety",
        "Mobile final launch iOS deploy safety section",
        FINAL_LAUNCH_STATUS_VIEW_PATH,
        "Deploy Safety",
    ),
    SourceRequirement(
        "mobile_status_view_launch_rehearsal",
        "Mobile final launch rehearsal section",
        FINAL_LAUNCH_STATUS_VIEW_PATH,
        "Launch Rehearsal",
    ),
    SourceRequirement(
        "mobile_status_view_visual_regression",
        "Mobile final launch visual regression section",
        FINAL_LAUNCH_STATUS_VIEW_PATH,
        "Visual Regression",
    ),
    SourceRequirement(
        "mobile_status_view_live_evidence",
        "Mobile final launch live evidence section",
        FINAL_LAUNCH_STATUS_VIEW_PATH,
        "Live Evidence",
    ),
    SourceRequirement(
        "mobile_status_view_resource_handoff",
        "Mobile final launch resource handoff section",
        FINAL_LAUNCH_STATUS_VIEW_PATH,
        "Resource Handoff",
    ),
    SourceRequirement(
        "mobile_status_view_backend_resources",
        "Mobile final launch backend resources section",
        FINAL_LAUNCH_STATUS_VIEW_PATH,
        "Backend Resources",
    ),
    SourceRequirement(
        "mobile_status_view_ios_resources",
        "Mobile final launch iOS resources section",
        FINAL_LAUNCH_STATUS_VIEW_PATH,
        "iOS Resources",
    ),
    SourceRequirement(
        "mobile_status_view_commands",
        "Mobile final launch status commands",
        FINAL_LAUNCH_STATUS_VIEW_PATH,
        "commandRows",
    ),
    SourceRequirement(
        "preflight_item",
        "Device preflight final launch item",
        DEVICE_PREFLIGHT_PATH,
        "final_launch",
    ),
    SourceRequirement(
        "preflight_model",
        "Device preflight final launch model",
        DEVICE_PREFLIGHT_PATH,
        "FinalDemoLaunchReport",
    ),
    SourceRequirement(
        "preflight_final_resources_item",
        "Device preflight final resources item",
        DEVICE_PREFLIGHT_PATH,
        "final_resources",
    ),
    SourceRequirement(
        "preflight_final_resources_label",
        "Device preflight final resources label",
        DEVICE_PREFLIGHT_PATH,
        "Final Resources",
    ),
    SourceRequirement(
        "preflight_read_only_note",
        "Device preflight read-only note",
        DEVICE_PREFLIGHT_PATH,
        "Final launch readiness is read-only.",
    ),
    SourceRequirement(
        "preflight_ready_mapping",
        "Device preflight ready mapping",
        DEVICE_PREFLIGHT_PATH,
        'case "ready"',
    ),
    SourceRequirement(
        "preflight_required_item",
        "Device preflight required item",
        DEVICE_PREFLIGHT_PATH,
        'Set(["backend_url", "providers", "final_launch", "final_resources", "local_demo"])',
    ),
    SourceRequirement(
        "contract_decode",
        "Contract test decodes launch payload",
        CORE_CONTRACT_TESTS_PATH,
        "testDecodesFinalDemoLaunchPayload",
    ),
    SourceRequirement(
        "contract_api_get",
        "Contract test checks launch API request",
        CORE_CONTRACT_TESTS_PATH,
        "testGetFinalDemoLaunchBuildsGETRequest",
    ),
    SourceRequirement(
        "contract_api_invalid_mode",
        "Contract test rejects invalid mode",
        CORE_CONTRACT_TESTS_PATH,
        "testGetFinalDemoLaunchRejectsInvalidModeBeforeNetwork",
    ),
    SourceRequirement(
        "contract_preflight_partial",
        "Contract test maps partial launch report",
        CORE_CONTRACT_TESTS_PATH,
        "testDevicePreflightMapsFinalLaunchPartialToWaiting",
    ),
    SourceRequirement(
        "contract_final_resources_missing",
        "Contract test maps missing final resources",
        CORE_CONTRACT_TESTS_PATH,
        "testDevicePreflightMapsMissingFinalResourcesPreflightToWaiting",
    ),
    SourceRequirement(
        "contract_final_resources_ready",
        "Contract test maps ready final resources",
        CORE_CONTRACT_TESTS_PATH,
        "testDevicePreflightMarksReadyFinalResourcesPreflight",
    ),
    SourceRequirement(
        "contract_final_resources_blocked",
        "Contract test redacts blocked final resources",
        CORE_CONTRACT_TESTS_PATH,
        "testDevicePreflightBlocksAndRedactsFinalResourcesPreflight",
    ),
    SourceRequirement(
        "contract_preflight_error",
        "Contract test redacts launch errors",
        CORE_CONTRACT_TESTS_PATH,
        "testDevicePreflightBlocksAndRedactsFinalLaunchError",
    ),
    SourceRequirement(
        "contract_mobile_summary_partial",
        "Contract test builds mobile final launch summary",
        CORE_CONTRACT_TESTS_PATH,
        "testFinalLaunchMobileSummaryBuildsPartialOperatorStatus",
    ),
    SourceRequirement(
        "contract_mobile_summary_mode_policy",
        "Contract test renders final launch mode policy",
        CORE_CONTRACT_TESTS_PATH,
        "testFinalLaunchMobileSummaryShowsConfiguredModePolicy",
    ),
    SourceRequirement(
        "contract_mobile_summary_redaction",
        "Contract test redacts mobile final launch summary",
        CORE_CONTRACT_TESTS_PATH,
        "testFinalLaunchMobileSummaryRedactsUnsafeReportText",
    ),
    SourceRequirement(
        "contract_ios_deploy_runbook_decode",
        "Contract test decodes iOS deploy runbook",
        CORE_CONTRACT_TESTS_PATH,
        "testDecodesIOSDeployRunbookFromFinalLaunchPayload",
    ),
    SourceRequirement(
        "contract_ios_deploy_runbook_partial_summary",
        "Contract test renders partial iOS deploy runbook",
        CORE_CONTRACT_TESTS_PATH,
        "testFinalLaunchMobileSummaryShowsPartialIOSDeployRunbook",
    ),
    SourceRequirement(
        "contract_ios_deploy_runbook_blocked_summary",
        "Contract test renders blocked iOS deploy runbook",
        CORE_CONTRACT_TESTS_PATH,
        "testFinalLaunchMobileSummaryShowsBlockedIOSDeployRunbook",
    ),
    SourceRequirement(
        "contract_ios_deploy_runbook_redaction",
        "Contract test redacts iOS deploy runbook",
        CORE_CONTRACT_TESTS_PATH,
        "testFinalLaunchMobileSummaryRedactsUnsafeIOSDeployRunbook",
    ),
    SourceRequirement(
        "contract_ios_device_launch_rehearsal_decode",
        "Contract test decodes iOS launch rehearsal readiness",
        CORE_CONTRACT_TESTS_PATH,
        "testDecodesIOSDeviceLaunchRehearsalReadinessFromFinalLaunchPayload",
    ),
    SourceRequirement(
        "contract_ios_device_launch_rehearsal_blocked_summary",
        "Contract test renders blocked iOS launch rehearsal",
        CORE_CONTRACT_TESTS_PATH,
        "testFinalLaunchMobileSummaryShowsBlockedIOSDeviceLaunchRehearsal",
    ),
    SourceRequirement(
        "contract_ios_device_launch_rehearsal_ready_summary",
        "Contract test renders ready iOS launch rehearsal",
        CORE_CONTRACT_TESTS_PATH,
        "testFinalLaunchMobileSummaryShowsReadyIOSDeviceLaunchRehearsal",
    ),
    SourceRequirement(
        "contract_ios_device_launch_rehearsal_redaction",
        "Contract test redacts iOS launch rehearsal",
        CORE_CONTRACT_TESTS_PATH,
        "testFinalLaunchMobileSummaryRedactsUnsafeIOSDeviceLaunchRehearsal",
    ),
    SourceRequirement(
        "contract_visual_regression_decode",
        "Contract test decodes visual regression readiness",
        CORE_CONTRACT_TESTS_PATH,
        "testDecodesVisualRegressionReadinessFromFinalLaunchPayload",
    ),
    SourceRequirement(
        "contract_visual_regression_ready_summary",
        "Contract test renders ready visual regression",
        CORE_CONTRACT_TESTS_PATH,
        "testFinalLaunchMobileSummaryShowsReadyVisualRegression",
    ),
    SourceRequirement(
        "contract_visual_regression_blocked_summary",
        "Contract test renders blocked visual regression",
        CORE_CONTRACT_TESTS_PATH,
        "testFinalLaunchMobileSummaryShowsBlockedVisualRegression",
    ),
    SourceRequirement(
        "contract_visual_regression_redaction",
        "Contract test redacts visual regression",
        CORE_CONTRACT_TESTS_PATH,
        "testFinalLaunchMobileSummaryRedactsUnsafeVisualRegression",
    ),
    SourceRequirement(
        "contract_live_provider_evidence_decode",
        "Contract test decodes live provider evidence",
        CORE_CONTRACT_TESTS_PATH,
        "testDecodesLiveProviderEvidenceFromFinalLaunchPayload",
    ),
    SourceRequirement(
        "contract_resource_handoff_decode",
        "Contract test decodes resource handoff",
        CORE_CONTRACT_TESTS_PATH,
        "testDecodesResourceHandoffFromFinalLaunchPayload",
    ),
    SourceRequirement(
        "contract_resource_handoff_missing_summary",
        "Contract test renders missing resource handoff",
        CORE_CONTRACT_TESTS_PATH,
        "testFinalLaunchMobileSummaryShowsMissingResourceHandoff",
    ),
    SourceRequirement(
        "contract_resource_handoff_ready_summary",
        "Contract test renders ready resource handoff",
        CORE_CONTRACT_TESTS_PATH,
        "testFinalLaunchMobileSummaryShowsReadyResourceHandoff",
    ),
    SourceRequirement(
        "contract_resource_handoff_redaction",
        "Contract test redacts resource handoff",
        CORE_CONTRACT_TESTS_PATH,
        "testFinalLaunchMobileSummaryRedactsUnsafeResourceHandoff",
    ),
)

SOURCE_SAFETY_PATTERNS = (
    ("sudo", "sudo"),
    ("xcode_select", "xcode-select"),
    ("xcode_license", "xcodebuild -license"),
    ("security_cli", "security "),
    ("codesign", "codesign"),
    ("meshy_live_domain", "api.meshy.ai"),
    ("openai_live_domain", "api.openai.com"),
    ("treatstock_live_domain", "treatstock.com"),
)
SOURCE_GLOBAL_MUTATION_IDS = {
    "sudo",
    "xcode_select",
    "xcode_license",
    "security_cli",
    "codesign",
}
SOURCE_LIVE_PROVIDER_IDS = {
    "meshy_live_domain",
    "openai_live_domain",
    "treatstock_live_domain",
}

ENDPOINT_SECRET_PATTERNS = (
    ("authorization_header", r"Authorization\s*[=:]\s*Bearer\s+[A-Za-z0-9._~+/\-=:-]+"),
    ("bearer_token", r"Bearer\s+[A-Za-z0-9._~+/\-=:-]+"),
    ("secret_key", r"sk-[A-Za-z0-9._-]+"),
    ("api_key_value", r"api[_-]?key\s*[=:]\s*[^\s,;\"']+"),
)
ENDPOINT_RAW_MEDIA_PATTERNS = (
    ("data_uri", r"data:[A-Za-z0-9.+-]+/[A-Za-z0-9.+-]+;base64,[A-Za-z0-9+/=_-]+"),
    ("local_capture_uri", r"local-capture://[^\s,;\"']+"),
)
ENDPOINT_PAYMENT_PATTERNS = (
    ("checkout_url_key", r"checkout_url"),
    ("payment_url", r"https?://pay\.[^\s,;\"']+"),
    ("checkout_url", r"https?://checkout\.[^\s,;\"']+"),
)
ENDPOINT_PATH_PATTERNS = (
    ("users_path", r"/Users/[^\s,;\"']+"),
    ("tmp_path", r"/tmp/[^\s,;\"']+"),
    ("file_url", r"file://[^\s,;\"']+"),
)


def run_mobile_final_launch_readiness_acceptance(
    *,
    repo_root: str | Path | None = None,
    endpoint_getter: EndpointGetter | None = None,
) -> MobileFinalLaunchReadinessAcceptanceResult:
    root = Path(repo_root) if repo_root is not None else _default_repo_root()
    selected_endpoint_getter = endpoint_getter or _default_endpoint_getter

    local_response = selected_endpoint_getter("/v1/final-demo-launch?mode=local")
    invalid_response = selected_endpoint_getter("/v1/final-demo-launch?mode=live")
    source_requirements = [
        _evaluate_requirement(root, requirement) for requirement in SOURCE_REQUIREMENTS
    ]
    failed_requirements = [
        item["missing"] for item in source_requirements if item["status"] == "failed"
    ]
    source_safety_findings = _source_safety_findings(root)
    endpoint_safety_findings = _endpoint_safety_findings(
        [local_response, invalid_response]
    )

    endpoint_local_ok = _endpoint_local_report_ok(local_response)
    endpoint_invalid_ok = invalid_response.status_code == 422
    mobile_source_ok = not failed_requirements
    safety = _safety_summary(
        local_response=local_response,
        source_safety_findings=source_safety_findings,
        endpoint_safety_findings=endpoint_safety_findings,
    )
    safety_ok = not any(safety.values())

    checks = [
        _check("endpoint_local_report", endpoint_local_ok),
        _check("endpoint_invalid_mode", endpoint_invalid_ok),
        _check("mobile_source", mobile_source_ok),
        _check("safety", safety_ok),
    ]
    summary = {
        "passed": sum(1 for check in checks if check["status"] == "passed"),
        "failed": sum(1 for check in checks if check["status"] == "failed"),
    }
    status = "succeeded" if summary["failed"] == 0 else "failed"
    report = {
        "kind": "mobile_final_launch_readiness_acceptance_report",
        "status": status,
        "summary": summary,
        "checks": checks,
        "endpoint": {
            "local_status_code": local_response.status_code,
            "invalid_mode_status_code": invalid_response.status_code,
            "kind": local_response.payload.get("kind"),
            "mode": local_response.payload.get("mode"),
            "overall_status": local_response.payload.get("overall_status"),
            "live_calls_by_default": _live_calls_by_default(local_response),
            "global_mutation": _endpoint_global_mutation(local_response),
        },
        "mobile_source": {
            "requirements": source_requirements,
            "failed_requirements": failed_requirements,
        },
        "safety": safety,
        "safety_findings": [
            *source_safety_findings,
            *endpoint_safety_findings,
        ],
    }
    return MobileFinalLaunchReadinessAcceptanceResult(
        exit_code=0 if status == "succeeded" else 1,
        report=_sanitize_report(report, root),
    )


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _default_endpoint_getter(path: str) -> EndpointProbeResponse:
    client = TestClient(app)
    response = client.get(path)
    payload = _json_payload(response.text)
    return EndpointProbeResponse(
        status_code=response.status_code,
        payload=payload,
        text=response.text,
    )


def _json_payload(text: str) -> dict[str, Any]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


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
        "missing": {
            "id": requirement.id,
            "file": requirement.file,
            "contains": requirement.contains,
        },
    }


def _contains(path: Path, expected: str) -> bool:
    try:
        return expected in path.read_text(encoding="utf-8")
    except OSError:
        return False


def _source_safety_findings(root: Path) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for relative_path in sorted({requirement.file for requirement in SOURCE_REQUIREMENTS}):
        text, exists = _read_optional_text(root / relative_path)
        if not exists:
            continue
        lowered = text.lower()
        for pattern_id, expected in SOURCE_SAFETY_PATTERNS:
            if expected.lower() in lowered:
                findings.append(
                    {
                        "kind": "source_safety",
                        "id": pattern_id,
                        "file": relative_path,
                    }
                )
    return findings


def _read_optional_text(path: Path) -> tuple[str, bool]:
    try:
        return path.read_text(encoding="utf-8"), True
    except OSError:
        return "", False


def _endpoint_safety_findings(
    responses: list[EndpointProbeResponse],
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    combined_text = "\n".join(
        part
        for response in responses
        for part in (response.text, json.dumps(response.payload, sort_keys=True))
    )
    pattern_groups = (
        ("provider_secret", ENDPOINT_SECRET_PATTERNS),
        ("raw_media", ENDPOINT_RAW_MEDIA_PATTERNS),
        ("payment_link", ENDPOINT_PAYMENT_PATTERNS),
        ("absolute_path", ENDPOINT_PATH_PATTERNS),
    )
    for group, patterns in pattern_groups:
        for pattern_id, pattern in patterns:
            if re.search(pattern, combined_text, flags=re.IGNORECASE):
                findings.append({"kind": group, "id": pattern_id})
    return findings


def _endpoint_local_report_ok(response: EndpointProbeResponse) -> bool:
    return (
        response.status_code == 200
        and response.payload.get("kind") == "final_demo_launch_report"
        and response.payload.get("mode") == "local"
        and _live_calls_by_default(response) is False
        and _endpoint_global_mutation(response) is False
    )


def _live_calls_by_default(response: EndpointProbeResponse) -> bool | None:
    policy = response.payload.get("live_call_policy")
    if not isinstance(policy, dict):
        return None
    value = policy.get("live_calls_by_default")
    return value if isinstance(value, bool) else None


def _endpoint_global_mutation(response: EndpointProbeResponse) -> bool | None:
    safety = response.payload.get("safety")
    if not isinstance(safety, dict):
        return None
    value = safety.get("global_mutation")
    return value if isinstance(value, bool) else None


def _safety_summary(
    *,
    local_response: EndpointProbeResponse,
    source_safety_findings: list[dict[str, str]],
    endpoint_safety_findings: list[dict[str, str]],
) -> dict[str, bool]:
    endpoint_finding_kinds = {finding["kind"] for finding in endpoint_safety_findings}
    source_finding_ids = {finding["id"] for finding in source_safety_findings}
    return {
        "global_mutation": (
            _endpoint_global_mutation(local_response) is not False
            or bool(source_finding_ids & SOURCE_GLOBAL_MUTATION_IDS)
        ),
        "live_provider_calls_by_default": (
            _live_calls_by_default(local_response) is not False
            or bool(source_finding_ids & SOURCE_LIVE_PROVIDER_IDS)
        ),
        "provider_secrets_in_report": "provider_secret" in endpoint_finding_kinds,
        "raw_media_in_report": "raw_media" in endpoint_finding_kinds,
        "payment_links_in_report": "payment_link" in endpoint_finding_kinds,
        "absolute_paths_in_report": "absolute_path" in endpoint_finding_kinds,
    }


def _check(check_id: str, passed: bool) -> dict[str, str]:
    return {
        "id": check_id,
        "status": "passed" if passed else "failed",
    }


def _sanitize_report(report: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    text = json.dumps(report)
    return json.loads(_safe_text(text, repo_root))


def _safe_text(message: str, repo_root: Path) -> str:
    sanitized = message
    replacements = [
        r"Authorization\s*[=:]\s*Bearer\s+[A-Za-z0-9._~+/\-=:-]+",
        r"Bearer\s+[A-Za-z0-9._~+/\-=:-]+",
        r"sk-[A-Za-z0-9._-]+",
        r"api[_-]?key\s*[=:]\s*[^\s,;\"']+",
        r"data:[A-Za-z0-9.+-]+/[A-Za-z0-9.+-]+;base64,[A-Za-z0-9+/=_-]+",
        r"local-capture://[^\s,;\"']+",
        r"https?://pay\.[^\s,;\"']+",
        r"https?://checkout\.[^\s,;\"']+",
        r"file://[^\s,;\"']+",
    ]
    for pattern in replacements:
        sanitized = re.sub(pattern, "[redacted]", sanitized, flags=re.IGNORECASE)
    for path in {repo_root, Path.home(), Path("/tmp")}:
        path_text = str(path)
        if path_text:
            sanitized = sanitized.replace(path_text, "[path]")
    sanitized = re.sub(r"/Users/[^\s,;\"']+", "[path]", sanitized)
    return sanitized
