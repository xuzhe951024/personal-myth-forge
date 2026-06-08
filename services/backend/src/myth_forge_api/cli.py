from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import replace
from pathlib import Path
from typing import Sequence

from myth_forge_api.acceptance import run_demo_acceptance
from myth_forge_api.config import load_settings
from myth_forge_api.evaluation.three_d import (
    DEFAULT_THREE_D_EVALUATION_SUITE,
    GUIDED_SCAN_SMOKE_EVALUATION_SUITE,
    build_custom_prompt_cases,
    run_three_d_evaluation,
)
from myth_forge_api.evaluation.npc import (
    DEFAULT_NPC_AGENT_EVALUATION_SUITE,
    run_npc_agent_evaluation,
)
from myth_forge_api.final_configured_preflight import (
    build_final_configured_preflight_report,
)
from myth_forge_api.final_configured_evidence_plan import (
    build_final_configured_evidence_plan_report,
)
from myth_forge_api.final_external_action_ledger import (
    build_final_external_action_ledger_report,
)
from myth_forge_api.final_handoff_index import build_final_handoff_index_report
from myth_forge_api.final_launch_closure_packet import (
    build_final_launch_closure_packet_report,
)
from myth_forge_api.final_acceptance import run_final_acceptance
from myth_forge_api.final_demo_launch import build_final_demo_launch_report
from myth_forge_api.final_local_report_refresh import run_final_local_report_refresh
from myth_forge_api.final_resource_fill_guide import (
    build_final_resource_fill_guide_report,
)
from myth_forge_api.final_resource_apply_preview import (
    build_final_resource_apply_preview_report,
)
from myth_forge_api.final_resource_repair import (
    build_final_resource_repair_report,
)
from myth_forge_api.final_resources_preflight import (
    build_final_resources_preflight_report,
)
from myth_forge_api.final_resource_requirements import (
    build_final_resource_requirements_report,
)
from myth_forge_api.final_showcase_readiness import (
    build_final_showcase_readiness_report,
)
from myth_forge_api.print_fulfillment_readiness import (
    build_print_fulfillment_readiness_report,
)
from myth_forge_api.live_provider_evidence import (
    build_live_provider_evidence_report,
)
from myth_forge_api.local_showcase_smoke import build_local_showcase_smoke_report
from myth_forge_api.mobile_deploy_preflight_evidence import (
    run_mobile_deploy_preflight_evidence,
)
from myth_forge_api.mobile_xcode_build_evidence import (
    run_mobile_xcode_build_evidence,
)
from myth_forge_api.ios_device_launch_certificate import (
    build_ios_device_launch_certificate_report,
)
from myth_forge_api.ios_device_evidence_bundle import (
    build_ios_device_evidence_bundle_report,
)
from myth_forge_api.ios_device_launch_rehearsal import (
    build_ios_device_launch_rehearsal_report,
)
from myth_forge_api.ios_deploy_runbook import build_ios_deploy_runbook_report
from myth_forge_api.providers.factory import (
    build_npc_director,
    build_npc_tick_runtime,
    build_three_d_provider,
)
from myth_forge_api.providers.npc import OpenAINPCProviderError
from myth_forge_api.providers.readiness import build_provider_readiness
from myth_forge_api.providers.three_d import (
    MeshyConfigurationError,
    MeshyProviderError,
    ThreeDGenerationRequest,
)
from myth_forge_api.resource_handoff import build_resource_handoff_report
from myth_forge_api.resource_template_acceptance import run_resource_template_acceptance
from myth_forge_api.visual_regression_readiness import (
    build_visual_regression_readiness_report,
)

CORE_PROVIDER_KINDS = ["three_d", "npc", "capture_storage"]
BACKEND_ONLY_ENV = [
    "MESHY_API_KEY",
    "OPENAI_API_KEY",
    "TREATSTOCK_API_KEY",
    "SCULPTEO_API_KEY",
]
NEXT_HANDOFF_COMMANDS = [
    "make final-apply-resources",
    "make backend-dev",
    "curl http://127.0.0.1:8080/v1/provider-readiness",
    (
        "cd services/backend && uv run python -m myth_forge_api.cli provider-handoff "
        "--require-core-real --output .local/provider-handoff.json"
    ),
]


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "evaluate-3d" and bool(args.prompts_file) == bool(args.suite):
        parser.error("evaluate-3d requires exactly one of --suite or --prompts-file.")
    if args.command == "evaluate-npc" and not args.suite:
        parser.error("evaluate-npc requires --suite default-v0.")

    try:
        if args.command == "generate-asset":
            asset = _generate_asset(prompt=args.prompt, provider_name=args.provider)
            print(json.dumps(asset.model_dump(mode="json"), indent=2))
            return 0
        if args.command == "generate-batch":
            assets = [
                _generate_asset(prompt=prompt, provider_name=args.provider).model_dump(mode="json")
                for prompt in _read_prompts(args.prompts_file)
            ]
            print(json.dumps(assets, indent=2))
            return 0
        if args.command == "evaluate-3d":
            return _evaluate_3d(
                prompts_file=args.prompts_file,
                suite_name=args.suite,
                provider_name=args.provider,
                output_path=args.output,
            )
        if args.command == "evaluate-npc":
            return _evaluate_npc(
                suite_name=args.suite,
                provider_name=args.provider,
                tick_steps=args.tick_steps,
                output_path=args.output,
            )
        if args.command == "provider-handoff":
            return _provider_handoff(
                output_path=args.output,
                require_core_real=args.require_core_real,
            )
        if args.command == "resource-handoff":
            return _resource_handoff(
                repo_root=args.repo_root,
                output_path=args.output,
            )
        if args.command == "resource-template-acceptance":
            return _resource_template_acceptance(
                repo_root=args.repo_root,
                output_path=args.output,
            )
        if args.command == "final-resources-preflight":
            return _final_resources_preflight(
                repo_root=args.repo_root,
                resources_file=args.resources_file,
                output_path=args.output,
            )
        if args.command == "final-resource-requirements":
            return _final_resource_requirements(
                repo_root=args.repo_root,
                output_path=args.output,
            )
        if args.command == "final-resource-apply-preview":
            return _final_resource_apply_preview(
                repo_root=args.repo_root,
                output_path=args.output,
            )
        if args.command == "final-resource-repair-preview":
            return _final_resource_repair(
                repo_root=args.repo_root,
                output_path=args.output,
                apply=False,
            )
        if args.command == "final-resource-repair":
            return _final_resource_repair(
                repo_root=args.repo_root,
                output_path=args.output,
                apply=True,
            )
        if args.command == "final-resource-fill-guide":
            return _final_resource_fill_guide(
                repo_root=args.repo_root,
                output_path=args.output,
                markdown_output_path=args.markdown_output,
            )
        if args.command == "final-external-action-ledger":
            return _final_external_action_ledger(
                repo_root=args.repo_root,
                output_path=args.output,
            )
        if args.command == "final-launch-closure-packet":
            return _final_launch_closure_packet(
                repo_root=args.repo_root,
                output_path=args.output,
            )
        if args.command == "local-showcase-smoke":
            return _local_showcase_smoke(output_path=args.output)
        if args.command == "final-local-report-refresh":
            return _final_local_report_refresh(
                repo_root=args.repo_root,
                output_path=args.output,
            )
        if args.command == "mobile-deploy-preflight-evidence":
            return _mobile_deploy_preflight_evidence(
                repo_root=args.repo_root,
                output_path=args.output,
            )
        if args.command == "mobile-xcode-build-evidence":
            return _mobile_xcode_build_evidence(
                repo_root=args.repo_root,
                output_path=args.output,
            )
        if args.command == "final-configured-preflight":
            return _final_configured_preflight(
                repo_root=args.repo_root,
                output_path=args.output,
            )
        if args.command == "final-configured-evidence-plan":
            return _final_configured_evidence_plan(
                repo_root=args.repo_root,
                output_path=args.output,
                allow_live_provider_calls=args.allow_live_provider_calls,
            )
        if args.command == "final-handoff-index":
            return _final_handoff_index(
                repo_root=args.repo_root,
                output_path=args.output,
            )
        if args.command == "final-showcase-readiness":
            return _final_showcase_readiness(
                repo_root=args.repo_root,
                output_path=args.output,
            )
        if args.command == "print-fulfillment-readiness":
            return _print_fulfillment_readiness(
                repo_root=args.repo_root,
                output_path=args.output,
            )
        if args.command == "live-provider-evidence":
            return _live_provider_evidence(
                repo_root=args.repo_root,
                output_path=args.output,
            )
        if args.command == "ios-device-launch-certificate":
            return _ios_device_launch_certificate(
                repo_root=args.repo_root,
                output_path=args.output,
            )
        if args.command == "ios-device-evidence-bundle":
            return _ios_device_evidence_bundle(
                repo_root=args.repo_root,
                output_path=args.output,
            )
        if args.command == "ios-device-launch-rehearsal":
            return _ios_device_launch_rehearsal(
                repo_root=args.repo_root,
                output_path=args.output,
            )
        if args.command == "final-demo-launch":
            return _final_demo_launch(
                mode=args.mode,
                repo_root=args.repo_root,
                output_path=args.output,
            )
        if args.command == "ios-deploy-runbook":
            return _ios_deploy_runbook(
                mode=args.mode,
                repo_root=args.repo_root,
                output_path=args.output,
            )
        if args.command == "demo-acceptance":
            return _demo_acceptance(
                provider_mode=args.provider_mode,
                npc_steps=args.npc_steps,
                require_real_core=args.require_real_core,
                allow_live_provider_calls=args.allow_live_provider_calls,
                output_path=args.output,
            )
        if args.command == "final-acceptance":
            return _final_acceptance(
                profile=args.profile,
                provider_mode=args.provider_mode,
                require_real_core=args.require_real_core,
                allow_live_provider_calls=args.allow_live_provider_calls,
                npc_steps=args.npc_steps,
                repo_root=args.repo_root,
                output_path=args.output,
            )
        if args.command == "visual-regression":
            return _visual_regression(
                repo_root=args.repo_root,
                output_path=args.output,
            )
        if args.command == "visual-regression-readiness":
            return _visual_regression_readiness(
                repo_root=args.repo_root,
                output_path=args.output,
            )
    except (MeshyProviderError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    parser.print_help(sys.stderr)
    return 1


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="myth-forge")
    subcommands = parser.add_subparsers(dest="command")

    asset_parser = subcommands.add_parser("generate-asset")
    asset_parser.add_argument("--prompt", required=True)
    asset_parser.add_argument("--provider", choices=["local", "meshy"], default=None)

    batch_parser = subcommands.add_parser("generate-batch")
    batch_parser.add_argument("--prompts-file", required=True)
    batch_parser.add_argument("--provider", choices=["local", "meshy"], default=None)

    evaluate_parser = subcommands.add_parser("evaluate-3d")
    evaluate_parser.add_argument("--prompts-file", default=None)
    evaluate_parser.add_argument("--suite", choices=["default-v0", "guided-scan-smoke-v0"], default=None)
    evaluate_parser.add_argument("--provider", choices=["local", "meshy"], default=None)
    evaluate_parser.add_argument("--output", required=True)

    npc_evaluate_parser = subcommands.add_parser("evaluate-npc")
    npc_evaluate_parser.add_argument("--suite", choices=["default-v0"], default=None)
    npc_evaluate_parser.add_argument("--provider", choices=["local", "openai"], default=None)
    npc_evaluate_parser.add_argument("--tick-steps", type=_npc_steps_arg, default=2)
    npc_evaluate_parser.add_argument("--output", required=True)

    handoff_parser = subcommands.add_parser("provider-handoff")
    handoff_parser.add_argument("--output", default=None)
    handoff_parser.add_argument("--require-core-real", action="store_true")

    resource_handoff_parser = subcommands.add_parser("resource-handoff")
    resource_handoff_parser.add_argument("--repo-root", default=None)
    resource_handoff_parser.add_argument("--output", default=None)

    resource_template_parser = subcommands.add_parser("resource-template-acceptance")
    resource_template_parser.add_argument("--repo-root", default=None)
    resource_template_parser.add_argument("--output", default=None)

    final_resources_parser = subcommands.add_parser("final-resources-preflight")
    final_resources_parser.add_argument("--repo-root", default=None)
    final_resources_parser.add_argument("--resources-file", default=None)
    final_resources_parser.add_argument("--output", default=None)

    final_resource_requirements_parser = subcommands.add_parser(
        "final-resource-requirements"
    )
    final_resource_requirements_parser.add_argument("--repo-root", default=None)
    final_resource_requirements_parser.add_argument("--output", default=None)

    final_resource_apply_preview_parser = subcommands.add_parser(
        "final-resource-apply-preview"
    )
    final_resource_apply_preview_parser.add_argument("--repo-root", default=None)
    final_resource_apply_preview_parser.add_argument("--output", default=None)

    final_resource_repair_preview_parser = subcommands.add_parser(
        "final-resource-repair-preview"
    )
    final_resource_repair_preview_parser.add_argument("--repo-root", default=None)
    final_resource_repair_preview_parser.add_argument("--output", default=None)

    final_resource_repair_parser = subcommands.add_parser("final-resource-repair")
    final_resource_repair_parser.add_argument("--repo-root", default=None)
    final_resource_repair_parser.add_argument("--output", default=None)

    final_resource_fill_guide_parser = subcommands.add_parser(
        "final-resource-fill-guide"
    )
    final_resource_fill_guide_parser.add_argument("--repo-root", default=None)
    final_resource_fill_guide_parser.add_argument("--output", default=None)
    final_resource_fill_guide_parser.add_argument("--markdown-output", default=None)

    final_external_action_ledger_parser = subcommands.add_parser(
        "final-external-action-ledger"
    )
    final_external_action_ledger_parser.add_argument("--repo-root", default=None)
    final_external_action_ledger_parser.add_argument("--output", default=None)

    final_launch_closure_packet_parser = subcommands.add_parser(
        "final-launch-closure-packet"
    )
    final_launch_closure_packet_parser.add_argument("--repo-root", default=None)
    final_launch_closure_packet_parser.add_argument("--output", default=None)

    local_showcase_smoke_parser = subcommands.add_parser("local-showcase-smoke")
    local_showcase_smoke_parser.add_argument("--output", default=None)

    final_local_report_refresh_parser = subcommands.add_parser(
        "final-local-report-refresh"
    )
    final_local_report_refresh_parser.add_argument("--repo-root", default=None)
    final_local_report_refresh_parser.add_argument("--output", default=None)

    mobile_deploy_preflight_evidence_parser = subcommands.add_parser(
        "mobile-deploy-preflight-evidence"
    )
    mobile_deploy_preflight_evidence_parser.add_argument("--repo-root", default=None)
    mobile_deploy_preflight_evidence_parser.add_argument("--output", default=None)

    mobile_xcode_build_evidence_parser = subcommands.add_parser(
        "mobile-xcode-build-evidence"
    )
    mobile_xcode_build_evidence_parser.add_argument("--repo-root", default=None)
    mobile_xcode_build_evidence_parser.add_argument("--output", default=None)

    final_configured_preflight_parser = subcommands.add_parser(
        "final-configured-preflight"
    )
    final_configured_preflight_parser.add_argument("--repo-root", default=None)
    final_configured_preflight_parser.add_argument("--output", default=None)

    final_configured_evidence_plan_parser = subcommands.add_parser(
        "final-configured-evidence-plan"
    )
    final_configured_evidence_plan_parser.add_argument("--repo-root", default=None)
    final_configured_evidence_plan_parser.add_argument("--output", default=None)
    final_configured_evidence_plan_parser.add_argument(
        "--allow-live-provider-calls",
        action="store_true",
    )

    final_handoff_index_parser = subcommands.add_parser("final-handoff-index")
    final_handoff_index_parser.add_argument("--repo-root", default=None)
    final_handoff_index_parser.add_argument("--output", default=None)

    final_showcase_readiness_parser = subcommands.add_parser(
        "final-showcase-readiness"
    )
    final_showcase_readiness_parser.add_argument("--repo-root", default=None)
    final_showcase_readiness_parser.add_argument("--output", default=None)

    print_fulfillment_readiness_parser = subcommands.add_parser(
        "print-fulfillment-readiness"
    )
    print_fulfillment_readiness_parser.add_argument("--repo-root", default=None)
    print_fulfillment_readiness_parser.add_argument("--output", default=None)

    live_provider_evidence_parser = subcommands.add_parser("live-provider-evidence")
    live_provider_evidence_parser.add_argument("--repo-root", default=None)
    live_provider_evidence_parser.add_argument("--output", default=None)

    ios_device_launch_certificate_parser = subcommands.add_parser(
        "ios-device-launch-certificate"
    )
    ios_device_launch_certificate_parser.add_argument("--repo-root", default=None)
    ios_device_launch_certificate_parser.add_argument("--output", default=None)

    ios_device_evidence_bundle_parser = subcommands.add_parser(
        "ios-device-evidence-bundle"
    )
    ios_device_evidence_bundle_parser.add_argument("--repo-root", default=None)
    ios_device_evidence_bundle_parser.add_argument("--output", default=None)

    ios_device_launch_rehearsal_parser = subcommands.add_parser(
        "ios-device-launch-rehearsal"
    )
    ios_device_launch_rehearsal_parser.add_argument("--repo-root", default=None)
    ios_device_launch_rehearsal_parser.add_argument("--output", default=None)

    final_demo_launch_parser = subcommands.add_parser("final-demo-launch")
    final_demo_launch_parser.add_argument(
        "--mode",
        choices=["local", "configured"],
        default="local",
    )
    final_demo_launch_parser.add_argument("--repo-root", default=None)
    final_demo_launch_parser.add_argument("--output", default=None)

    ios_deploy_runbook_parser = subcommands.add_parser("ios-deploy-runbook")
    ios_deploy_runbook_parser.add_argument(
        "--mode",
        choices=["local", "configured"],
        default="local",
    )
    ios_deploy_runbook_parser.add_argument("--repo-root", default=None)
    ios_deploy_runbook_parser.add_argument("--output", default=None)

    acceptance_parser = subcommands.add_parser("demo-acceptance")
    acceptance_parser.add_argument(
        "--provider-mode",
        choices=["local", "configured"],
        default="local",
    )
    acceptance_parser.add_argument("--npc-steps", type=_npc_steps_arg, default=3)
    acceptance_parser.add_argument("--require-real-core", action="store_true")
    acceptance_parser.add_argument("--allow-live-provider-calls", action="store_true")
    acceptance_parser.add_argument("--output", default=None)

    final_acceptance_parser = subcommands.add_parser("final-acceptance")
    final_acceptance_parser.add_argument("--profile", choices=["quick", "full"], default="quick")
    final_acceptance_parser.add_argument(
        "--provider-mode",
        choices=["local", "configured"],
        default="local",
    )
    final_acceptance_parser.add_argument("--require-real-core", action="store_true")
    final_acceptance_parser.add_argument("--allow-live-provider-calls", action="store_true")
    final_acceptance_parser.add_argument("--npc-steps", type=_npc_steps_arg, default=3)
    final_acceptance_parser.add_argument("--repo-root", default=None)
    final_acceptance_parser.add_argument("--output", default=None)

    visual_regression_parser = subcommands.add_parser("visual-regression")
    visual_regression_parser.add_argument("--repo-root", default=None)
    visual_regression_parser.add_argument("--output", default=None)

    visual_regression_readiness_parser = subcommands.add_parser(
        "visual-regression-readiness"
    )
    visual_regression_readiness_parser.add_argument("--repo-root", default=None)
    visual_regression_readiness_parser.add_argument("--output", default=None)

    return parser


def _generate_asset(prompt: str, provider_name: str | None):
    settings = load_settings()
    if provider_name:
        settings = replace(settings, three_d_provider=provider_name)
    provider = build_three_d_provider(settings)
    return provider.generate_game_asset(_generation_request_for_prompt(prompt))


def _evaluate_3d(
    prompts_file: str | None,
    suite_name: str | None,
    provider_name: str | None,
    output_path: str,
) -> int:
    if bool(prompts_file) == bool(suite_name):
        raise ValueError("Provide exactly one of --suite or --prompts-file.")
    if suite_name == "default-v0":
        cases = DEFAULT_THREE_D_EVALUATION_SUITE
        report_suite_name = suite_name
    elif suite_name == "guided-scan-smoke-v0":
        cases = GUIDED_SCAN_SMOKE_EVALUATION_SUITE
        report_suite_name = suite_name
    else:
        cases = build_custom_prompt_cases(_read_prompts(prompts_file or ""))
        report_suite_name = "custom-prompts"

    settings = load_settings()
    if provider_name:
        settings = replace(settings, three_d_provider=provider_name)
    selected_provider = settings.three_d_provider

    try:
        provider = build_three_d_provider(settings)
        if selected_provider == "meshy" and not settings.meshy_api_key:
            raise MeshyConfigurationError("MESHY_API_KEY is required for Meshy generation.")
    except (MeshyProviderError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    report = run_three_d_evaluation(
        provider=provider,
        selected_provider=selected_provider,
        suite_name=report_suite_name,
        cases=cases,
    )
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return 0


def _evaluate_npc(
    *,
    suite_name: str | None,
    provider_name: str | None,
    tick_steps: int,
    output_path: str,
) -> int:
    if suite_name != "default-v0":
        raise ValueError("evaluate-npc requires --suite default-v0.")

    settings = load_settings()
    if provider_name:
        settings = replace(settings, npc_provider=provider_name)
    selected_provider = settings.npc_provider

    try:
        director = build_npc_director(settings)
        tick_runtime = build_npc_tick_runtime(settings)
        director.validate_configuration()
    except (OpenAINPCProviderError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    report = run_npc_agent_evaluation(
        director=director,
        tick_runtime=tick_runtime,
        selected_provider=selected_provider,
        suite_name=suite_name,
        tick_steps=tick_steps,
        cases=DEFAULT_NPC_AGENT_EVALUATION_SUITE,
    )
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return 0 if report["failed"] == 0 else 1


def _provider_handoff(output_path: str | None, require_core_real: bool) -> int:
    report = _provider_handoff_report()
    _write_json_payload(report, output_path)
    if require_core_real and not report["core_real_ready"]:
        return 2
    return 0


def _resource_handoff(repo_root: str | None, output_path: str | None) -> int:
    report = build_resource_handoff_report(
        repo_root=Path(repo_root) if repo_root else None,
    )
    _write_json_payload(report, output_path)
    return 0 if report["overall_status"] == "ready" else 2


def _resource_template_acceptance(repo_root: str | None, output_path: str | None) -> int:
    result = run_resource_template_acceptance(
        repo_root=Path(repo_root) if repo_root else None,
    )
    _write_json_payload(result.report, output_path)
    return result.exit_code


def _final_resources_preflight(
    repo_root: str | None,
    resources_file: str | None,
    output_path: str | None,
) -> int:
    result = build_final_resources_preflight_report(
        repo_root=Path(repo_root) if repo_root else None,
        resources_file=Path(resources_file) if resources_file else None,
    )
    _write_json_payload(result.report, output_path)
    return result.exit_code


def _final_resource_requirements(
    *,
    repo_root: str | None,
    output_path: str | None,
) -> int:
    result = build_final_resource_requirements_report(
        repo_root=Path(repo_root) if repo_root else None,
    )
    _write_json_payload(result.report, output_path)
    return result.exit_code


def _final_resource_apply_preview(
    *,
    repo_root: str | None,
    output_path: str | None,
) -> int:
    result = build_final_resource_apply_preview_report(
        repo_root=Path(repo_root) if repo_root else None,
    )
    _write_json_payload(result.report, output_path)
    return result.exit_code


def _final_resource_repair(
    *,
    repo_root: str | None,
    output_path: str | None,
    apply: bool,
) -> int:
    result = build_final_resource_repair_report(
        repo_root=Path(repo_root) if repo_root else None,
        apply=apply,
    )
    _write_json_payload(result.report, output_path)
    return result.exit_code


def _final_resource_fill_guide(
    *,
    repo_root: str | None,
    output_path: str | None,
    markdown_output_path: str | None,
) -> int:
    result = build_final_resource_fill_guide_report(
        repo_root=Path(repo_root) if repo_root else None,
    )
    _write_json_payload(result.report, output_path)
    if markdown_output_path:
        _write_text_payload(str(result.report.get("markdown", "")), markdown_output_path)
    return result.exit_code


def _final_external_action_ledger(
    *,
    repo_root: str | None,
    output_path: str | None,
) -> int:
    result = build_final_external_action_ledger_report(
        repo_root=Path(repo_root) if repo_root else None,
    )
    _write_json_payload(result.report, output_path)
    return result.exit_code


def _final_launch_closure_packet(
    *,
    repo_root: str | None,
    output_path: str | None,
) -> int:
    result = build_final_launch_closure_packet_report(
        repo_root=Path(repo_root) if repo_root else None,
    )
    _write_json_payload(result.report, output_path)
    return result.exit_code


def _local_showcase_smoke(*, output_path: str | None) -> int:
    result = build_local_showcase_smoke_report()
    _write_json_payload(result.report, output_path)
    return result.exit_code


def _final_local_report_refresh(
    *,
    repo_root: str | None,
    output_path: str | None,
) -> int:
    result = run_final_local_report_refresh(
        repo_root=Path(repo_root) if repo_root else None,
    )
    _write_json_payload(result.report, output_path)
    return result.exit_code


def _mobile_deploy_preflight_evidence(
    *,
    repo_root: str | None,
    output_path: str | None,
) -> int:
    result = run_mobile_deploy_preflight_evidence(
        repo_root=Path(repo_root) if repo_root else None,
    )
    _write_json_payload(result.report, output_path)
    return result.exit_code


def _mobile_xcode_build_evidence(
    *,
    repo_root: str | None,
    output_path: str | None,
) -> int:
    result = run_mobile_xcode_build_evidence(
        repo_root=Path(repo_root) if repo_root else None,
    )
    _write_json_payload(result.report, output_path)
    return result.exit_code


def _final_configured_preflight(
    *,
    repo_root: str | None,
    output_path: str | None,
) -> int:
    result = build_final_configured_preflight_report(
        repo_root=Path(repo_root) if repo_root else None,
    )
    _write_json_payload(result.report, output_path)
    return result.exit_code


def _final_configured_evidence_plan(
    *,
    repo_root: str | None,
    output_path: str | None,
    allow_live_provider_calls: bool,
) -> int:
    result = build_final_configured_evidence_plan_report(
        repo_root=Path(repo_root) if repo_root else None,
        allow_live_provider_calls=allow_live_provider_calls,
    )
    _write_json_payload(result.report, output_path)
    return result.exit_code


def _final_handoff_index(
    *,
    repo_root: str | None,
    output_path: str | None,
) -> int:
    result = build_final_handoff_index_report(
        repo_root=Path(repo_root) if repo_root else None,
    )
    _write_json_payload(result.report, output_path)
    return result.exit_code


def _final_showcase_readiness(
    *,
    repo_root: str | None,
    output_path: str | None,
) -> int:
    result = build_final_showcase_readiness_report(
        repo_root=Path(repo_root) if repo_root else None,
    )
    _write_json_payload(result.report, output_path)
    return result.exit_code


def _print_fulfillment_readiness(
    *,
    repo_root: str | None,
    output_path: str | None,
) -> int:
    result = build_print_fulfillment_readiness_report(
        repo_root=Path(repo_root) if repo_root else None,
    )
    _write_json_payload(result.report, output_path)
    return result.exit_code


def _live_provider_evidence(
    *,
    repo_root: str | None,
    output_path: str | None,
) -> int:
    result = build_live_provider_evidence_report(
        repo_root=Path(repo_root) if repo_root else None,
    )
    _write_json_payload(result.report, output_path)
    return result.exit_code


def _ios_device_launch_certificate(
    *,
    repo_root: str | None,
    output_path: str | None,
) -> int:
    result = build_ios_device_launch_certificate_report(
        repo_root=Path(repo_root) if repo_root else None,
    )
    _write_json_payload(result.report, output_path)
    return result.exit_code


def _ios_device_evidence_bundle(
    *,
    repo_root: str | None,
    output_path: str | None,
) -> int:
    result = build_ios_device_evidence_bundle_report(
        repo_root=Path(repo_root) if repo_root else None,
    )
    _write_json_payload(result.report, output_path)
    return result.exit_code


def _ios_device_launch_rehearsal(
    *,
    repo_root: str | None,
    output_path: str | None,
) -> int:
    result = build_ios_device_launch_rehearsal_report(
        repo_root=Path(repo_root) if repo_root else None,
    )
    _write_json_payload(result.report, output_path)
    return result.exit_code


def _final_demo_launch(
    *,
    mode: str,
    repo_root: str | None,
    output_path: str | None,
) -> int:
    result = build_final_demo_launch_report(
        mode=mode,
        repo_root=Path(repo_root) if repo_root else None,
    )
    _write_json_payload(result.report, output_path)
    return result.exit_code


def _ios_deploy_runbook(
    *,
    mode: str,
    repo_root: str | None,
    output_path: str | None,
) -> int:
    report = build_ios_deploy_runbook_report(
        mode=mode,
        repo_root=Path(repo_root) if repo_root else None,
    )
    _write_json_payload(report, output_path)
    return 2 if report["status"] == "blocked" else 0


def _demo_acceptance(
    *,
    provider_mode: str,
    npc_steps: int,
    require_real_core: bool,
    allow_live_provider_calls: bool,
    output_path: str | None,
) -> int:
    result = run_demo_acceptance(
        provider_mode=provider_mode,
        npc_steps=npc_steps,
        require_real_core=require_real_core,
        allow_live_provider_calls=allow_live_provider_calls,
    )
    _write_json_payload(result.report, output_path)
    return result.exit_code


def _final_acceptance(
    *,
    profile: str,
    provider_mode: str,
    require_real_core: bool,
    allow_live_provider_calls: bool,
    npc_steps: int,
    repo_root: str | None,
    output_path: str | None,
) -> int:
    result = run_final_acceptance(
        profile=profile,
        provider_mode=provider_mode,
        require_real_core=require_real_core,
        allow_live_provider_calls=allow_live_provider_calls,
        npc_steps=npc_steps,
        repo_root=repo_root,
    )
    _write_json_payload(result.report, output_path)
    return result.exit_code


def _visual_regression(
    *,
    repo_root: str | None,
    output_path: str | None,
) -> int:
    from myth_forge_api.visual_regression import check_visual_artifacts

    result = check_visual_artifacts(Path(repo_root) if repo_root else Path.cwd())
    _write_json_payload(result.report, output_path)
    return result.exit_code


def _visual_regression_readiness(
    *,
    repo_root: str | None,
    output_path: str | None,
) -> int:
    result = build_visual_regression_readiness_report(
        repo_root=Path(repo_root) if repo_root else Path.cwd(),
    )
    _write_json_payload(result.report, output_path)
    return result.exit_code


def _write_json_payload(report: dict[str, object], output_path: str | None) -> None:
    payload = json.dumps(report, indent=2)
    if output_path:
        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(payload, encoding="utf-8")
    else:
        print(payload)


def _write_text_payload(payload: str, output_path: str) -> None:
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(payload, encoding="utf-8")


def _npc_steps_arg(value: str) -> int:
    try:
        steps = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("npc steps must be an integer from 0 to 3.") from exc
    if steps < 0 or steps > 3:
        raise argparse.ArgumentTypeError("npc steps must be an integer from 0 to 3.")
    return steps


def _provider_handoff_report() -> dict[str, object]:
    readiness = build_provider_readiness(load_settings())
    provider_items = [item.model_dump(mode="json") for item in readiness.providers]
    provider_by_kind = {item["kind"]: item for item in provider_items}
    core_items = [
        provider_by_kind[kind]
        for kind in CORE_PROVIDER_KINDS
        if kind in provider_by_kind
    ]
    core_real_count = sum(
        1 for provider in core_items if provider["is_real_provider_ready"]
    )
    core_total = len(core_items)
    core_real_ready = core_real_count == core_total
    missing_env = sorted(
        {
            env_name
            for provider in provider_items
            for env_name in provider.get("missing_env", [])
        }
    )
    return {
        "kind": "provider_handoff_report",
        "mode": "configuration",
        "status": "ready" if core_real_ready else "blocked",
        "classification": (
            "core_real_providers_ready"
            if core_real_ready
            else "core_real_providers_not_ready"
        ),
        "summary": {
            "providers": len(provider_items),
            "core_total": core_total,
            "core_real_ready": core_real_count,
            "missing_env": len(missing_env),
        },
        "overall_demo_ready": readiness.overall_demo_ready,
        "overall_real_ready": readiness.overall_real_ready,
        "core_real_ready": core_real_ready,
        "core_provider_kinds": CORE_PROVIDER_KINDS,
        "missing_env": missing_env,
        "backend_only_env": BACKEND_ONLY_ENV,
        "mobile_secret_policy": (
            "Provider secrets stay on the backend; mobile clients only see readiness metadata."
        ),
        "providers": provider_items,
        "next_commands": NEXT_HANDOFF_COMMANDS,
    }


def _read_prompts(prompts_file: str) -> list[str]:
    prompts = [
        line.strip()
        for line in Path(prompts_file).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not prompts:
        raise ValueError(f"No prompts found in {prompts_file}.")
    return prompts


def _session_id_for_prompt(prompt: str) -> str:
    digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    return f"cli_{digest[:12]}"


def _generation_request_for_prompt(prompt: str) -> ThreeDGenerationRequest:
    return ThreeDGenerationRequest(session_id=_session_id_for_prompt(prompt), prompt=prompt)


if __name__ == "__main__":
    raise SystemExit(main())
