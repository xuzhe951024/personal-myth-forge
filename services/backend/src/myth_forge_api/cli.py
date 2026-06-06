from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from dataclasses import replace
from pathlib import Path
from typing import Sequence

from myth_forge_api.config import load_settings
from myth_forge_api.providers.factory import build_three_d_provider
from myth_forge_api.providers.three_d import (
    MeshyConfigurationError,
    MeshyProviderError,
    ThreeDGenerationRequest,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

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
                provider_name=args.provider,
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
    evaluate_parser.add_argument("--prompts-file", required=True)
    evaluate_parser.add_argument("--provider", choices=["local", "meshy"], default=None)
    evaluate_parser.add_argument("--output", required=True)

    return parser


def _generate_asset(prompt: str, provider_name: str | None):
    settings = load_settings()
    if provider_name:
        settings = replace(settings, three_d_provider=provider_name)
    provider = build_three_d_provider(settings)
    return provider.generate_game_asset(_generation_request_for_prompt(prompt))


def _evaluate_3d(prompts_file: str, provider_name: str | None, output_path: str) -> int:
    prompts = _read_prompts(prompts_file)
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

    rows = []
    for prompt in prompts:
        started_at = time.perf_counter()
        try:
            asset = provider.generate_game_asset(_generation_request_for_prompt(prompt))
            rows.append(
                {
                    "prompt": prompt,
                    "provider": asset.provider,
                    "status": "succeeded",
                    "asset_uri": asset.uri,
                    "elapsed_seconds": round(time.perf_counter() - started_at, 4),
                    "error": None,
                }
            )
        except Exception as exc:
            rows.append(
                {
                    "prompt": prompt,
                    "provider": selected_provider,
                    "status": "failed",
                    "asset_uri": None,
                    "elapsed_seconds": round(time.perf_counter() - started_at, 4),
                    "error": _safe_provider_error(exc),
                }
            )

    report = {
        "provider": selected_provider,
        "total_prompts": len(prompts),
        "succeeded": sum(1 for row in rows if row["status"] == "succeeded"),
        "failed": sum(1 for row in rows if row["status"] == "failed"),
        "rows": rows,
    }
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return 0


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


def _safe_provider_error(exc: Exception) -> str:
    message = str(exc)
    replacements = [
        r"Authorization\s*[=:]\s*Bearer\s+[A-Za-z0-9._:-]+",
        r"Bearer\s+[A-Za-z0-9._:-]+",
        r"raw=[^\s,;]+",
        r"api[_-]?key\s*[=:]\s*[^\s,;]+",
    ]
    for pattern in replacements:
        message = re.sub(pattern, "[redacted]", message, flags=re.IGNORECASE)
    return message


if __name__ == "__main__":
    raise SystemExit(main())
