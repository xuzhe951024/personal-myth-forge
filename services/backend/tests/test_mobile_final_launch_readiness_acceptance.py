import json
from pathlib import Path

from myth_forge_api.mobile_final_launch_readiness_acceptance import (
    EndpointProbeResponse,
    run_mobile_final_launch_readiness_acceptance,
)


REPO_ROOT = Path(__file__).resolve().parents[3]


def test_mobile_final_launch_readiness_acceptance_checks_endpoint_source_and_safety() -> None:
    result = run_mobile_final_launch_readiness_acceptance(repo_root=REPO_ROOT)

    assert result.exit_code == 0
    assert result.report["kind"] == "mobile_final_launch_readiness_acceptance_report"
    assert result.report["status"] == "succeeded"
    assert result.report["summary"] == {"passed": 4, "failed": 0}

    checks = {check["id"]: check for check in result.report["checks"]}
    assert list(checks) == [
        "endpoint_local_report",
        "endpoint_invalid_mode",
        "mobile_source",
        "safety",
    ]
    assert checks["endpoint_local_report"]["status"] == "passed"
    assert result.report["endpoint"]["local_status_code"] == 200
    assert result.report["endpoint"]["kind"] == "final_demo_launch_report"
    assert result.report["endpoint"]["mode"] == "local"
    assert result.report["endpoint"]["live_calls_by_default"] is False
    assert result.report["endpoint"]["invalid_mode_status_code"] == 422
    assert result.report["mobile_source"]["failed_requirements"] == []
    requirement_ids = {
        requirement["id"]
        for requirement in result.report["mobile_source"]["requirements"]
    }
    assert "model_final_launch_mode" in requirement_ids
    assert "model_final_demo_launch_first_blocker" in requirement_ids
    assert "model_final_demo_launch_first_blocker_field" in requirement_ids
    assert "app_configuration_final_launch_mode" in requirement_ids
    assert "root_view_mode_picker" in requirement_ids
    assert "root_view_configured_mode" in requirement_ids
    assert "root_view_mode_reload" in requirement_ids
    assert "mobile_summary_mode_policy_rows" in requirement_ids
    assert "mobile_summary_final_demo_launch_first_blocker_row" in requirement_ids
    assert "mobile_status_view_mode_section" in requirement_ids
    assert "model_ios_device_launch_rehearsal" in requirement_ids
    assert "mobile_summary_launch_rehearsal_rows" in requirement_ids
    assert "mobile_status_view_launch_rehearsal" in requirement_ids
    assert "contract_ios_device_launch_rehearsal_decode" in requirement_ids
    assert "model_ios_device_launch_certificate" in requirement_ids
    assert "model_ios_device_launch_certificate_field" in requirement_ids
    assert "model_ios_device_evidence_bundle" in requirement_ids
    assert "model_ios_device_evidence_bundle_field" in requirement_ids
    assert "mobile_summary_ios_device_evidence_rows" in requirement_ids
    assert "mobile_status_view_ios_device_evidence" in requirement_ids
    assert "contract_ios_device_evidence_bundle_decode" in requirement_ids
    assert "contract_ios_device_evidence_bundle_summary" in requirement_ids
    assert "contract_ios_device_evidence_bundle_redaction" in requirement_ids
    assert "model_final_launch_closure_packet" in requirement_ids
    assert "model_final_launch_closure_packet_field" in requirement_ids
    assert "model_final_launch_closure_packet_blocker" in requirement_ids
    assert "model_final_launch_closure_packet_first_blocker_field" in requirement_ids
    assert "mobile_summary_final_launch_closure_packet_rows" in requirement_ids
    assert "mobile_summary_final_launch_closure_packet_first_blocker_row" in requirement_ids
    assert "mobile_status_view_final_launch_closure_packet" in requirement_ids
    assert "contract_final_launch_closure_packet_decode" in requirement_ids
    assert "contract_final_launch_closure_packet_configured_bundle_decode" in requirement_ids
    assert "contract_final_launch_closure_packet_summary" in requirement_ids
    assert "contract_final_launch_closure_packet_configured_bundle_summary" in requirement_ids
    assert "contract_final_launch_closure_packet_redaction" in requirement_ids
    assert "contract_final_launch_closure_packet_configured_bundle_redaction" in requirement_ids
    assert "model_visual_regression_readiness" in requirement_ids
    assert "mobile_summary_visual_regression_rows" in requirement_ids
    assert "mobile_status_view_visual_regression" in requirement_ids
    assert "contract_visual_regression_decode" in requirement_ids
    assert "model_local_showcase_smoke" in requirement_ids
    assert "model_local_showcase_smoke_field" in requirement_ids
    assert "mobile_summary_local_showcase_smoke_rows" in requirement_ids
    assert "mobile_summary_local_showcase_smoke_safety" in requirement_ids
    assert "mobile_status_view_local_smoke" in requirement_ids
    assert "contract_local_showcase_smoke_decode" in requirement_ids
    assert "contract_local_showcase_smoke_summary" in requirement_ids
    assert "contract_local_showcase_smoke_redaction" in requirement_ids
    assert "model_live_provider_evidence" in requirement_ids
    assert "model_live_provider_evidence_field" in requirement_ids
    assert "model_configured_evidence_plan" in requirement_ids
    assert "model_configured_evidence_plan_field" in requirement_ids
    assert "model_configured_evidence_plan_planned_consent" in requirement_ids
    assert "model_configured_evidence_bundle" in requirement_ids
    assert "model_configured_evidence_bundle_field" in requirement_ids
    assert "mobile_summary_live_provider_evidence_rows" in requirement_ids
    assert "mobile_summary_configured_evidence_plan_rows" in requirement_ids
    assert "mobile_summary_configured_evidence_plan_planned_consent" in requirement_ids
    assert "mobile_summary_configured_evidence_bundle_rows" in requirement_ids
    assert "mobile_status_view_live_evidence" in requirement_ids
    assert "mobile_status_view_configured_evidence" in requirement_ids
    assert "mobile_status_view_configured_evidence_bundle" in requirement_ids
    assert "contract_live_provider_evidence_decode" in requirement_ids
    assert "contract_configured_evidence_plan_decode" in requirement_ids
    assert "contract_configured_evidence_plan_planned_consent" in requirement_ids
    assert "contract_configured_evidence_plan_summary" in requirement_ids
    assert "contract_configured_evidence_plan_redaction" in requirement_ids
    assert "contract_configured_evidence_bundle_decode" in requirement_ids
    assert "contract_configured_evidence_bundle_summary" in requirement_ids
    assert "contract_configured_evidence_bundle_redaction" in requirement_ids
    assert "preflight_final_resource_requirements_item" in requirement_ids
    assert "preflight_final_resource_requirements_label" in requirement_ids
    assert "preflight_final_resource_requirements_source" in requirement_ids
    assert "preflight_final_resource_requirements_required_item" in requirement_ids
    assert "preflight_final_resource_fill_guide_item" in requirement_ids
    assert "preflight_final_resource_fill_guide_label" in requirement_ids
    assert "preflight_final_resource_fill_guide_first_blocker_source" in requirement_ids
    assert "preflight_final_resource_apply_preview_item" in requirement_ids
    assert "preflight_final_resource_apply_preview_label" in requirement_ids
    assert "preflight_final_resource_apply_preview_source" in requirement_ids
    assert "preflight_final_resource_apply_preview_required_item" in requirement_ids
    assert "preflight_ios_deploy_runbook_item" in requirement_ids
    assert "preflight_ios_deploy_runbook_label" in requirement_ids
    assert "preflight_ios_deploy_runbook_source" in requirement_ids
    assert "preflight_ios_deploy_runbook_required_item" in requirement_ids
    assert "preflight_ios_device_evidence_bundle_item" in requirement_ids
    assert "preflight_ios_device_evidence_bundle_label" in requirement_ids
    assert "preflight_ios_device_evidence_bundle_source" in requirement_ids
    assert "preflight_ios_device_evidence_bundle_required_item" in requirement_ids
    assert "preflight_ios_launch_rehearsal_readiness_item" in requirement_ids
    assert "preflight_ios_launch_rehearsal_readiness_label" in requirement_ids
    assert "preflight_ios_launch_rehearsal_readiness_source" in requirement_ids
    assert "preflight_ios_launch_rehearsal_readiness_required_item" in requirement_ids
    assert "final_demo_launch_ios_device_launch_certificate" in requirement_ids
    assert "final_demo_launch_ios_device_launch_certificate_injected" in requirement_ids
    assert "preflight_ios_device_launch_certificate_item" in requirement_ids
    assert "preflight_ios_device_launch_certificate_label" in requirement_ids
    assert "preflight_ios_device_launch_certificate_source" in requirement_ids
    assert "preflight_ios_device_launch_certificate_required_item" in requirement_ids
    assert "preflight_final_closure_packet_item" in requirement_ids
    assert "preflight_final_closure_packet_label" in requirement_ids
    assert "preflight_final_closure_packet_source" in requirement_ids
    assert "preflight_final_closure_packet_required_item" in requirement_ids
    assert "preflight_final_operator_handoff_item" in requirement_ids
    assert "preflight_final_operator_handoff_label" in requirement_ids
    assert "preflight_final_operator_handoff_source" in requirement_ids
    assert "preflight_final_operator_handoff_required_item" in requirement_ids
    assert "contract_final_resource_fill_guide_blocked" in requirement_ids
    assert "contract_final_resource_fill_guide_ready" in requirement_ids
    assert "contract_final_resource_fill_guide_redaction" in requirement_ids
    assert "contract_final_resource_fill_guide_first_blocker_redaction" in requirement_ids
    assert "contract_final_resource_requirements_missing" in requirement_ids
    assert "contract_final_resource_requirements_blocked" in requirement_ids
    assert "contract_final_resource_requirements_ready" in requirement_ids
    assert "contract_final_resource_requirements_redaction" in requirement_ids
    assert "contract_final_resource_apply_preview_missing" in requirement_ids
    assert "contract_final_resource_apply_preview_blocked" in requirement_ids
    assert "contract_final_resource_apply_preview_ready" in requirement_ids
    assert "contract_final_resource_apply_preview_redaction" in requirement_ids
    assert "contract_ios_deploy_runbook_missing" in requirement_ids
    assert "contract_ios_deploy_runbook_blocked" in requirement_ids
    assert "contract_ios_deploy_runbook_ready" in requirement_ids
    assert "contract_ios_deploy_runbook_redaction" in requirement_ids
    assert "contract_ios_device_evidence_bundle_missing_preflight" in requirement_ids
    assert "contract_ios_device_evidence_bundle_blocked_preflight" in requirement_ids
    assert "contract_ios_device_evidence_bundle_ready_preflight" in requirement_ids
    assert "contract_ios_device_evidence_bundle_redaction_preflight" in requirement_ids
    assert "contract_ios_launch_rehearsal_readiness_missing_preflight" in requirement_ids
    assert "contract_ios_launch_rehearsal_readiness_blocked_preflight" in requirement_ids
    assert "contract_ios_launch_rehearsal_readiness_ready_preflight" in requirement_ids
    assert "contract_ios_launch_rehearsal_readiness_stale_preflight" in requirement_ids
    assert "contract_ios_launch_rehearsal_readiness_redaction_preflight" in requirement_ids
    assert "contract_ios_device_launch_certificate_decode" in requirement_ids
    assert "contract_ios_device_launch_certificate_missing_preflight" in requirement_ids
    assert "contract_ios_device_launch_certificate_blocked_preflight" in requirement_ids
    assert "contract_ios_device_launch_certificate_ready_preflight" in requirement_ids
    assert "contract_ios_device_launch_certificate_consent_preflight" in requirement_ids
    assert "contract_ios_device_launch_certificate_redaction_preflight" in requirement_ids
    assert "contract_final_closure_packet_missing_preflight" in requirement_ids
    assert "contract_final_closure_packet_blocked_preflight" in requirement_ids
    assert "contract_final_closure_packet_ready_preflight" in requirement_ids
    assert "contract_final_closure_packet_configured_section_preflight" in requirement_ids
    assert "contract_final_closure_packet_redaction_preflight" in requirement_ids
    assert "contract_final_operator_handoff_missing_preflight" in requirement_ids
    assert "contract_final_operator_handoff_blocked_preflight" in requirement_ids
    assert "contract_final_operator_handoff_ready_preflight" in requirement_ids
    assert "contract_final_operator_handoff_live_preflight" in requirement_ids
    assert "contract_final_operator_handoff_redaction_preflight" in requirement_ids
    assert "model_final_resource_fill_guide_first_blocker" in requirement_ids
    assert "model_final_resource_fill_guide_first_blocker_field" in requirement_ids
    assert "mobile_summary_final_resource_fill_guide_first_blocker_row" in requirement_ids
    assert "model_final_resource_apply_preview_first_blocker" in requirement_ids
    assert "model_final_resource_apply_preview_first_blocker_field" in requirement_ids
    assert "mobile_summary_final_resource_apply_preview_first_blocker_row" in requirement_ids
    assert "model_final_resources_preflight_apply_time_handoff" in requirement_ids
    assert "model_final_resource_requirements_apply_time_handoff" in requirement_ids
    assert "model_final_resource_apply_preview_apply_time_handoff" in requirement_ids
    assert "mobile_summary_auto_backend_url_handoff" in requirement_ids
    assert "contract_final_resource_auto_backend_url_handoff_decode" in requirement_ids
    assert "contract_final_resource_auto_backend_url_handoff_summary" in requirement_ids
    assert "model_final_showcase_device_action_bundle" in requirement_ids
    assert "model_final_showcase_device_action_bundle_field" in requirement_ids
    assert "model_final_showcase_device_action_evidence_status" in requirement_ids
    assert "model_final_showcase_device_action_validation_command" in requirement_ids
    assert "mobile_summary_final_showcase_device_action_bundle" in requirement_ids
    assert "mobile_summary_final_showcase_device_action_evidence" in requirement_ids
    assert "mobile_summary_final_showcase_device_action_xcode_evidence" in requirement_ids
    assert "contract_final_showcase_device_action_bundle_decode" in requirement_ids
    assert "contract_final_showcase_device_action_evidence_decode" in requirement_ids
    assert "contract_final_showcase_device_action_xcode_evidence_decode" in requirement_ids
    assert "contract_final_showcase_device_action_bundle_summary" in requirement_ids
    assert "contract_final_showcase_device_action_evidence_summary" in requirement_ids
    assert "contract_final_showcase_device_action_xcode_evidence_summary" in requirement_ids
    assert "model_final_resource_requirements_first_blocker" in requirement_ids
    assert "model_final_resource_requirements_first_blocker_field" in requirement_ids
    assert "mobile_summary_final_resource_requirements_source" in requirement_ids
    assert "mobile_summary_final_resource_requirements_first_blocker_row" in requirement_ids
    assert "contract_final_resource_requirements_first_blocker_fixture" in requirement_ids
    assert "contract_final_demo_launch_first_blocker_receipt" in requirement_ids
    assert "demo_script_external_actions_step" in requirement_ids
    assert "demo_script_external_actions_builder" in requirement_ids
    assert "demo_script_external_actions_blocked_contract" in requirement_ids
    assert "demo_script_external_actions_ready_contract" in requirement_ids
    assert "showcase_autopilot_external_actions_step" in requirement_ids
    assert "showcase_autopilot_check_actions_title" in requirement_ids
    assert "showcase_autopilot_external_actions_contract" in requirement_ids
    assert result.report["safety"] == {
        "global_mutation": False,
        "live_provider_calls_by_default": False,
        "provider_secrets_in_report": False,
        "raw_media_in_report": False,
        "payment_links_in_report": False,
        "absolute_paths_in_report": False,
    }
    report_text = json.dumps(result.report)
    assert "sk-" not in report_text
    assert "Authorization" not in report_text
    assert "data:image" not in report_text
    assert "checkout_url" not in report_text
    assert "/Users/" not in report_text


def test_mobile_final_launch_readiness_acceptance_fails_missing_mobile_source(
    tmp_path: Path,
) -> None:
    result = run_mobile_final_launch_readiness_acceptance(repo_root=tmp_path)

    assert result.exit_code == 1
    assert result.report["status"] == "failed"
    checks = {check["id"]: check for check in result.report["checks"]}
    assert checks["endpoint_local_report"]["status"] == "passed"
    assert checks["endpoint_invalid_mode"]["status"] == "passed"
    assert checks["mobile_source"]["status"] == "failed"
    assert result.report["mobile_source"]["failed_requirements"]
    assert any(
        requirement["file"] == "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift"
        for requirement in result.report["mobile_source"]["failed_requirements"]
    )


def test_mobile_final_launch_readiness_acceptance_fails_unsafe_endpoint_payload(
    tmp_path: Path,
) -> None:
    _write_minimal_mobile_source(tmp_path)

    def fake_endpoint_getter(path: str) -> EndpointProbeResponse:
        if path.endswith("mode=live"):
            return EndpointProbeResponse(status_code=422, payload={"detail": "invalid"}, text="invalid")
        return EndpointProbeResponse(
            status_code=200,
            payload={
                "kind": "final_demo_launch_report",
                "mode": "local",
                "live_call_policy": {"live_calls_by_default": False},
                "safety": {"global_mutation": False},
                "error": "Authorization=Bearer sk-mobile-secret data:image/png;base64,AAAA",
            },
            text="Authorization=Bearer sk-mobile-secret data:image/png;base64,AAAA",
        )

    result = run_mobile_final_launch_readiness_acceptance(
        repo_root=tmp_path,
        endpoint_getter=fake_endpoint_getter,
    )

    assert result.exit_code == 1
    checks = {check["id"]: check for check in result.report["checks"]}
    assert checks["mobile_source"]["status"] == "passed"
    assert checks["safety"]["status"] == "failed"
    assert "sk-mobile-secret" not in json.dumps(result.report)
    assert "Authorization" not in json.dumps(result.report)
    assert "data:image" not in json.dumps(result.report)


def _write_minimal_mobile_source(root: Path) -> None:
    files: dict[str, str] = {
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PMFModels.swift": "\n".join(
            [
                "FinalDemoLaunchReport",
                "FinalDemoLaunchPhase",
                "FinalDemoLaunchFirstBlocker",
                "firstBlocker: FinalDemoLaunchFirstBlocker?",
                "FinalDemoLaunchLiveCallPolicy",
                "FinalDemoLaunchSafety",
                "FinalResourcesPreflightReport",
                "FinalResourcesFileStatus",
                "FinalResourcesPreflightSummary",
                "FinalLaunchMode",
                "displayLabel",
                "IOSDeployRunbookReport",
                "iosDeployRunbook",
                "IOSDeviceEvidenceBundleReport",
                "iosDeviceEvidenceBundle",
                "IOSDeviceLaunchRehearsalReadinessReport",
                "iosDeviceLaunchRehearsalReadiness",
                "IOSDeviceLaunchCertificateReport",
                "iosDeviceLaunchCertificate",
                "FinalLaunchClosurePacketReport",
                "FinalLaunchClosurePacketBlocker",
                "firstBlocker: FinalLaunchClosurePacketBlocker?",
                "finalLaunchClosurePacket",
                "FinalShowcaseDeviceActionBundle",
                "deviceActionBundle: FinalShowcaseDeviceActionBundle?",
                "evidenceStatus: String?",
                "validationCommand: String?",
                "VisualRegressionReadinessReport",
                "visualRegressionReadiness",
                "LocalShowcaseSmokeReport",
                "localShowcaseSmoke",
                "LiveProviderEvidenceReport",
                "liveProviderEvidence",
                "FinalConfiguredEvidencePlanReport",
                "finalConfiguredEvidencePlan",
                "plannedConsentSteps",
                "ConfiguredLiveEvidenceBundleReport",
                "configuredLiveEvidenceBundle",
                "FinalResourceFillGuideReport",
                "finalResourceFillGuide",
                "FinalResourceFillGuideFirstBlocker",
                "firstBlocker: FinalResourceFillGuideFirstBlocker?",
                "FinalResourceApplyPreviewFirstBlocker",
                "firstBlocker: FinalResourceApplyPreviewFirstBlocker?",
                "FinalResourceRequirementsFirstBlocker",
                "firstBlocker: FinalResourceRequirementsFirstBlocker?",
                "resolutionMode: String?",
                "applyNote: String?",
                "ResourceHandoffReport",
                "resourceReport",
            ]
        ),
        "apps/mobile/ios/App/AppConfiguration.swift": "\n".join(
            [
                "PMFFinalLaunchMode",
                "FinalLaunchMode.safe",
            ]
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PersonalMythForgeAPIClient.swift": "\n".join(
            [
                "getFinalDemoLaunch",
                "/v1/final-demo-launch",
                "\"local\", \"configured\"",
                "Unsupported final demo launch mode.",
            ]
        ),
        "apps/mobile/ios/App/ForgeRootView.swift": "\n".join(
            [
                "finalDemoLaunch",
                "finalLaunchMode",
                "loadFinalDemoLaunch",
                "getFinalDemoLaunch(mode: \"local\")",
                "loadFinalDemoLaunch(mode: finalLaunchMode)",
                "getFinalDemoLaunch(mode: mode.rawValue)",
                "Picker(\"Final launch mode\"",
                "FinalLaunchMode.allCases",
                ".onChange(of: finalLaunchMode)",
                "DevicePreflightSummaryBuilder.build",
                "FinalLaunchStatusView(",
                "FinalLaunchMobileSummaryBuilder.build",
            ]
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/FinalLaunchMobileSummary.swift": "\n".join(
            [
                "FinalLaunchMobileSummaryBuilder",
                "FinalLaunchMobileStatus",
                "modePolicyRows",
                "liveCallPolicy",
                "deployRunbookRows",
                "deployRunbookCommandRows",
                "deployRunbookSafetyRows",
                "deviceEvidenceRows",
                "launchRehearsalRows",
                "closurePacketRows",
                "closurePacketFirstBlockerRow",
                "report.firstBlocker",
                "showcaseDeviceActionBundleRows",
                "selectedShowcaseDeviceActions",
                "evidenceStatus",
                "validationCommand",
                "visualRegressionRows",
                "localShowcaseSmokeRows",
                "provider_calls=",
                "liveProviderEvidenceRows",
                "configuredEvidencePlanRows",
                "consent now",
                "configuredEvidenceBundleRows",
                "rehearsalFreshnessRow",
                "Freshness:",
                "resourceHandoffRows",
                "resourceHandoffBackendRows",
                "resourceHandoffIOSRows",
                "resourceFillGuideRows",
                "Fill guide",
                "resourceFillGuideFirstBlockerRow",
                "applyPreviewFirstBlockerRow",
                "appendApplyTimeDetail",
                "report.finalResourceRequirements",
                "resourceRequirementFirstBlockerRow",
                "sanitize",
            ]
        ),
        "apps/mobile/ios/App/FinalLaunchStatusView.swift": "\n".join(
            [
                "Final Launch Status",
                "Mode",
                "iOS Deploy Runbook",
                "Deploy Commands",
                "Deploy Safety",
                "Device Evidence",
                "Launch Rehearsal",
                "Closure Packet",
                "Visual Regression",
                "Local Smoke",
                "Live Evidence",
                "Configured Evidence",
                "Configured Evidence Bundle",
                "Resource Fill Guide",
                "Resource Handoff",
                "Backend Resources",
                "iOS Resources",
                "resourceActions",
                "commandRows",
            ]
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/DevicePreflight.swift": "\n".join(
            [
                "final_launch",
                "FinalDemoLaunchReport",
                "final_resources",
                "Final Resources",
                "finalResourceRequirementsItem(report: finalDemoLaunch)",
                "Resource Requirements",
                "report.finalResourceRequirements",
                "\"final_resource_requirements\",",
                "final_resource_fill_guide",
                "Fill Guide",
                "guide.firstBlocker",
                "finalResourceApplyPreviewItem(report: finalDemoLaunch)",
                "Apply Preview",
                "report.finalResourceApplyPreview",
                "\"final_resource_apply_preview\",",
                "iosDeployRunbookItem(report: finalDemoLaunch)",
                "Deploy Runbook",
                "report.iosDeployRunbook",
                "\"ios_deploy_runbook\",",
                "iosDeviceEvidenceBundleItem(report: finalDemoLaunch)",
                "Device Evidence",
                "report.iosDeviceEvidenceBundle",
                "\"ios_device_evidence_bundle\",",
                "iosLaunchRehearsalReadinessItem(report: finalDemoLaunch)",
                "Launch Rehearsal",
                "report.iosDeviceLaunchRehearsalReadiness",
                "\"ios_device_launch_rehearsal_readiness\",",
                "iosDeviceLaunchCertificateItem(report: finalDemoLaunch)",
                "Launch Certificate",
                "report.iosDeviceLaunchCertificate",
                "\"ios_device_launch_certificate\",",
                "finalClosurePacketItem(report: finalDemoLaunch)",
                "Final Closure",
                "report.finalLaunchClosurePacket",
                "\"final_launch_closure_packet\",",
                "finalOperatorHandoffItem(report: finalDemoLaunch)",
                "Operator Handoff",
                "report.finalOperatorHandoff",
                "\"final_operator_handoff\",",
                "Final launch readiness is read-only.",
                "case \"ready\"",
                "\"final_resource_fill_guide\"",
            ]
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/DemoScript.swift": "\n".join(
            [
                '"external_actions"',
                "externalActionsStep",
            ]
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/ShowcaseAutopilot.swift": "\n".join(
            [
                'script.step(id: "external_actions")',
                '"Check Actions"',
            ]
        ),
        "services/backend/src/myth_forge_api/final_demo_launch.py": "\n".join(
            [
                '"ios_device_launch_certificate"',
                "build_ios_device_launch_certificate_report",
                "final_demo_launch_report=report",
            ]
        ),
        "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift": "\n".join(
            [
                "testDecodesFinalDemoLaunchPayload",
                "testGetFinalDemoLaunchBuildsGETRequest",
                "testGetFinalDemoLaunchRejectsInvalidModeBeforeNetwork",
                "testDevicePreflightMapsFinalLaunchPartialToWaiting",
                "testDevicePreflightMapsMissingFinalResourcesPreflightToWaiting",
                "testDevicePreflightMarksReadyFinalResourcesPreflight",
                "testDevicePreflightBlocksAndRedactsFinalResourcesPreflight",
                "testDevicePreflightWaitsForMissingFinalResourceRequirements",
                "testDevicePreflightBlocksOnFinalResourceRequirementsFirstBlocker",
                "testDevicePreflightMarksReadyFinalResourceRequirements",
                "testDevicePreflightRedactsUnsafeFinalResourceRequirementsFirstBlockerDetail",
                "testDevicePreflightBlocksOnRequiredFinalResourceFillGuideInputs",
                "testDevicePreflightMarksReadyFinalResourceFillGuide",
                "testDevicePreflightRedactsUnsafeFinalResourceFillGuideDetail",
                "testDevicePreflightRedactsUnsafeFinalResourceFillGuideFirstBlockerDetail",
                "testDevicePreflightWaitsForMissingFinalResourceApplyPreview",
                "testDevicePreflightBlocksOnFinalResourceApplyPreviewFirstBlocker",
                "testDevicePreflightMarksReadyFinalResourceApplyPreview",
                "testDevicePreflightRedactsUnsafeFinalResourceApplyPreviewFirstBlockerDetail",
                "testDecodesFinalResourceAutoBackendURLHandoffFields",
                "testFinalLaunchMobileSummaryShowsAutoBackendURLHandoff",
                "deviceActionBundle",
                "make mobile-deploy-preflight",
                "evidenceStatus",
                "make mobile-deploy-preflight-evidence",
                "evidence blocked",
                "make mobile-xcode-build-evidence",
                "testFinalLaunchMobileSummaryShowsFinalShowcaseDeviceActionBundle",
                "testDevicePreflightWaitsForMissingIOSDeployRunbook",
                "testDevicePreflightBlocksOnIOSDeployRunbookCommandStep",
                "testDevicePreflightMarksReadyIOSDeployRunbook",
                "testDevicePreflightRedactsUnsafeIOSDeployRunbookDetail",
                "testDevicePreflightWaitsForMissingIOSDeviceEvidenceBundle",
                "testDevicePreflightBlocksOnIOSDeviceEvidenceSlot",
                "testDevicePreflightMarksReadyIOSDeviceEvidenceBundle",
                "testDevicePreflightRedactsUnsafeIOSDeviceEvidenceBundleDetail",
                "testDevicePreflightWaitsForMissingIOSLaunchRehearsalReadiness",
                "testDevicePreflightBlocksOnIOSLaunchRehearsalReadiness",
                "testDevicePreflightMarksReadyIOSLaunchRehearsalReadiness",
                "testDevicePreflightShowsStaleIOSLaunchRehearsalFreshness",
                "testDevicePreflightRedactsUnsafeIOSLaunchRehearsalReadiness",
                "testDecodesIOSDeviceLaunchCertificateFromFinalLaunchPayload",
                "testDevicePreflightWaitsForMissingIOSDeviceLaunchCertificate",
                "testDevicePreflightBlocksOnIOSDeviceLaunchCertificateGate",
                "testDevicePreflightMarksReadyIOSDeviceLaunchCertificate",
                "testDevicePreflightShowsIOSDeviceLaunchCertificateConsentGate",
                "testDevicePreflightRedactsUnsafeIOSDeviceLaunchCertificate",
                "testDevicePreflightWaitsForMissingFinalClosurePacket",
                "testDevicePreflightBlocksOnFinalClosurePacketFirstBlocker",
                "testDevicePreflightMarksReadyFinalClosurePacket",
                "testDevicePreflightShowsConfiguredEvidenceClosureSection",
                "testDevicePreflightRedactsUnsafeFinalClosurePacket",
                "testDevicePreflightWaitsForMissingFinalOperatorHandoff",
                "testDevicePreflightBlocksOnFinalOperatorHandoffNextAction",
                "testDevicePreflightMarksReadyFinalOperatorHandoff",
                "testDevicePreflightShowsLiveFinalOperatorHandoffConsent",
                "testDevicePreflightRedactsUnsafeFinalOperatorHandoff",
                "testDevicePreflightBlocksAndRedactsFinalLaunchError",
                "testFinalLaunchMobileSummaryBuildsPartialOperatorStatus",
                "testFinalLaunchMobileSummaryShowsConfiguredModePolicy",
                "testFinalLaunchMobileSummaryRedactsUnsafeReportText",
                "testDecodesIOSDeployRunbookFromFinalLaunchPayload",
                "testFinalLaunchMobileSummaryShowsPartialIOSDeployRunbook",
                "testFinalLaunchMobileSummaryShowsBlockedIOSDeployRunbook",
                "testFinalLaunchMobileSummaryRedactsUnsafeIOSDeployRunbook",
                "testDecodesIOSDeviceEvidenceBundleFromFinalLaunchPayload",
                "testFinalLaunchMobileSummaryShowsIOSDeviceEvidenceBundle",
                "testFinalLaunchMobileSummaryRedactsUnsafeIOSDeviceEvidenceBundle",
                "testDecodesFinalLaunchClosurePacketFromFinalLaunchPayload",
                "missing closure packet first blocker",
                "configured_evidence_bundle",
                "testFinalLaunchMobileSummaryShowsFinalLaunchClosurePacket",
                "configured_live_evidence_bundle",
                "testFinalLaunchMobileSummaryRedactsUnsafeFinalLaunchClosurePacket",
                "sk-configured",
                "testFinalLaunchMobileSummaryUsesTopLevelFirstBlockerReceipt",
                "testDemoScriptShowsBlockedExternalActionsBeforeFinalLaunch",
                "testDemoScriptCompletesReadyExternalActionsBeforeFinalLaunch",
                "testShowcaseAutopilotBlocksOnExternalActions",
                "testDecodesIOSDeviceLaunchRehearsalReadinessFromFinalLaunchPayload",
                "testDecodesIOSDeviceLaunchRehearsalFreshnessFromFinalLaunchPayload",
                "testFinalLaunchMobileSummaryShowsBlockedIOSDeviceLaunchRehearsal",
                "testFinalLaunchMobileSummaryShowsReadyIOSDeviceLaunchRehearsal",
                "testFinalLaunchMobileSummaryShowsStaleIOSDeviceLaunchRehearsalFreshness",
                "testFinalLaunchMobileSummaryRedactsUnsafeIOSDeviceLaunchRehearsal",
                "testDecodesVisualRegressionReadinessFromFinalLaunchPayload",
                "testFinalLaunchMobileSummaryShowsReadyVisualRegression",
                "testFinalLaunchMobileSummaryShowsBlockedVisualRegression",
                "testFinalLaunchMobileSummaryRedactsUnsafeVisualRegression",
                "testDecodesLocalShowcaseSmokeFromFinalLaunchPayload",
                "testFinalLaunchMobileSummaryShowsLocalShowcaseSmoke",
                "testFinalLaunchMobileSummaryRedactsUnsafeLocalShowcaseSmoke",
                "testDecodesLiveProviderEvidenceFromFinalLaunchPayload",
                "testDecodesConfiguredEvidencePlanFromFinalLaunchPayload",
                "planned_consent_steps",
                "testFinalLaunchMobileSummaryShowsConfiguredEvidencePlan",
                "testFinalLaunchMobileSummaryRedactsUnsafeConfiguredEvidencePlan",
                "testDecodesConfiguredEvidenceBundleFromFinalLaunchPayload",
                "testFinalLaunchMobileSummaryShowsConfiguredEvidenceBundle",
                "testFinalLaunchMobileSummaryRedactsUnsafeConfiguredEvidenceBundle",
                "testDecodesFinalResourceFillGuideFromFinalLaunchPayload",
                "testFinalLaunchMobileSummaryShowsResourceFillGuide",
                "provide MESHY_API_KEY in final-resources.env",
                "testDecodesResourceHandoffFromFinalLaunchPayload",
                "testFinalLaunchMobileSummaryShowsMissingResourceHandoff",
                "testFinalLaunchMobileSummaryShowsReadyResourceHandoff",
                "testFinalLaunchMobileSummaryRedactsUnsafeResourceHandoff",
            ]
        ),
    }
    for relative_path, text in files.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
