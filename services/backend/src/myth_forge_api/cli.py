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
from myth_forge_api.final_acceptance import run_final_acceptance
from myth_forge_api.final_demo_launch import build_final_demo_launch_report
from myth_forge_api.providers.factory import build_three_d_provider
from myth_forge_api.providers.readiness import build_provider_readiness
from myth_forge_api.providers.three_d import (
    MeshyConfigurationError,
    MeshyProviderError,
    ThreeDGenerationRequest,
)
from myth_forge_api.resource_handoff import build_resource_handoff_report
from myth_forge_api.resource_template_acceptance import run_resource_template_acceptance

CORE_PROVIDER_KINDS = ["three_d", "npc", "capture_storage"]
BACKEND_ONLY_ENV = [
    "MESHY_API_KEY",
    "OPENAI_API_KEY",
    "TREATSTOCK_API_KEY",
    "SCULPTEO_API_KEY",
]
NEXT_HANDOFF_COMMANDS = [
    "make backend-dev",
    "curl http://127.0.0.1:8080/v1/provider-readiness",
    (
        "cd services/backend && uv run python -m myth_forge_api.cli provider-handoff "
        "--require-core-real --output /tmp/personal-myth-forge-provider-handoff.json"
    ),
]


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "evaluate-3d" and bool(args.prompts_file) == bool(args.suite):
        parser.error("evaluate-3d requires exactly one of --suite or --prompts-file.")

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
        if args.command == "final-demo-launch":
            return _final_demo_launch(
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

    handoff_parser = subcommands.add_parser("provider-handoff")
    handoff_parser.add_argument("--output", default=None)
    handoff_parser.add_argument("--require-core-real", action="store_true")

    resource_handoff_parser = subcommands.add_parser("resource-handoff")
    resource_handoff_parser.add_argument("--repo-root", default=None)
    resource_handoff_parser.add_argument("--output", default=None)

    resource_template_parser = subcommands.add_parser("resource-template-acceptance")
    resource_template_parser.add_argument("--repo-root", default=None)
    resource_template_parser.add_argument("--output", default=None)

    final_demo_launch_parser = subcommands.add_parser("final-demo-launch")
    final_demo_launch_parser.add_argument(
        "--mode",
        choices=["local", "configured"],
        default="local",
    )
    final_demo_launch_parser.add_argument("--repo-root", default=None)
    final_demo_launch_parser.add_argument("--output", default=None)

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


def _write_json_payload(report: dict[str, object], output_path: str | None) -> None:
    payload = json.dumps(report, indent=2)
    if output_path:
        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(payload, encoding="utf-8")
    else:
        print(payload)


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
        "overall_demo_ready": readiness.overall_demo_ready,
        "overall_real_ready": readiness.overall_real_ready,
        "core_real_ready": all(provider["is_real_provider_ready"] for provider in core_items),
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
