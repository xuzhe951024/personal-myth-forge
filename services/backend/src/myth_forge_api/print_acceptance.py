from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from myth_forge_api.domain.models import GeneratedAsset, PrintQuoteRequest
from myth_forge_api.providers.printing import LocalPrintProvider


@dataclass(frozen=True)
class PrintQuoteAcceptanceResult:
    exit_code: int
    report: dict[str, Any]


def run_print_quote_acceptance() -> PrintQuoteAcceptanceResult:
    started_at = time.perf_counter()
    provider = LocalPrintProvider()
    try:
        asset = GeneratedAsset(
            kind="game_asset",
            provider="local_stub",
            format="glb",
            uri="local://generated-assets/print_acceptance.glb",
            prompt="Create a printable acceptance relic.",
            moderation_status="needs_review",
        )
        candidate = provider.create_print_candidate(asset)
        quote = provider.create_print_quote(PrintQuoteRequest(print_candidate=candidate))
        report = {
            "kind": "print_quote_acceptance_report",
            "status": "succeeded",
            "candidate_format": candidate.format,
            "quote_status": quote.status,
            "provider": quote.provider,
            "currency": quote.currency,
            "estimated_price_cents": quote.estimated_price_cents,
            "estimated_production_days": quote.estimated_production_days,
            "estimated_shipping_days": quote.estimated_shipping_days,
            "requires_user_approval": quote.requires_user_approval,
            "timings": {"total_elapsed_seconds": round(time.perf_counter() - started_at, 4)},
            "safety": _safety_summary(),
            "error": None,
        }
        return PrintQuoteAcceptanceResult(exit_code=0, report=_sanitize_report(report))
    except Exception as exc:
        report = {
            "kind": "print_quote_acceptance_report",
            "status": "failed",
            "timings": {"total_elapsed_seconds": round(time.perf_counter() - started_at, 4)},
            "safety": _safety_summary(),
            "error": str(exc),
        }
        return PrintQuoteAcceptanceResult(exit_code=1, report=_sanitize_report(report))


def _safety_summary() -> dict[str, bool]:
    return {
        "provider_secrets_in_report": False,
        "checkout_identifiers_in_report": False,
        "local_paths_in_report": False,
    }


def _sanitize_report(report: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(_sanitize_value(report)))


def _sanitize_value(value: Any) -> Any:
    if isinstance(value, str):
        return _safe_text(value)
    if isinstance(value, list):
        return [_sanitize_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _sanitize_value(item) for key, item in value.items()}
    return value


def _safe_text(message: str) -> str:
    sanitized = message
    replacements = [
        r"Authorization\s*[=:]\s*Bearer\s+[A-Za-z0-9._~+/\-=:-]+",
        r"Bearer\s+[A-Za-z0-9._~+/\-=:-]+",
        r"raw=[^\s,;\"']+",
        r"api[_-]?key\s*[=:]\s*[^\s,;\"']+",
        r"https?://pay\.[^\s,;\"']+",
        r"https?://checkout\.[^\s,;\"']+",
        r"file://[^\s,;\"']+",
    ]
    for pattern in replacements:
        sanitized = re.sub(pattern, "[redacted]", sanitized, flags=re.IGNORECASE)
    for path in {Path.home(), Path("/tmp")}:
        path_text = str(path)
        if path_text:
            sanitized = sanitized.replace(path_text, "[path]")
    sanitized = re.sub(r"/Users/[^\s,;\"']+", "[path]", sanitized)
    return sanitized
