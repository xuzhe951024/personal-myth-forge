from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import replace
from pathlib import Path
from typing import Sequence

from myth_forge_api.config import load_settings
from myth_forge_api.providers.factory import build_three_d_provider
from myth_forge_api.providers.three_d import MeshyProviderError


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

    return parser


def _generate_asset(prompt: str, provider_name: str | None):
    settings = load_settings()
    if provider_name:
        settings = replace(settings, three_d_provider=provider_name)
    provider = build_three_d_provider(settings)
    return provider.generate_game_asset(session_id=_session_id_for_prompt(prompt), prompt=prompt)


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


if __name__ == "__main__":
    raise SystemExit(main())
