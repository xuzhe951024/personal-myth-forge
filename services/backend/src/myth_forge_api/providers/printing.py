from __future__ import annotations

from typing import Protocol

from myth_forge_api.domain.models import GeneratedAsset, PrintCandidate, PrintQuote, PrintQuoteRequest


class PrintProvider(Protocol):
    provider_name: str

    def create_print_candidate(self, generated_asset: GeneratedAsset) -> PrintCandidate:
        ...

    def create_print_quote(self, request: PrintQuoteRequest) -> PrintQuote:
        ...


class LocalPrintProvider:
    """Deterministic stand-in for Treatstock, Sculpteo, or a future print service."""

    provider_name = "local_stub"

    def create_print_candidate(self, generated_asset: GeneratedAsset) -> PrintCandidate:
        return PrintCandidate(
            kind="print_asset",
            source_asset_uri=generated_asset.uri,
            provider=self.provider_name,
            format="3mf",
            uri=generated_asset.uri.replace(".glb", ".3mf").replace(
                "generated-assets", "print-candidates"
            ),
            requires_user_approval=True,
            approval_reason=(
                "Free-form generated 3D must be reviewed for safety, privacy, "
                "printability, shipping price, and user intent before fulfillment."
            ),
            printability_notes=[
                "derive from generated game asset rather than fixed template",
                "repair thin parts before quote",
                "scale to a small physical relic unless the user approves a larger print",
            ],
        )

    def create_print_quote(self, request: PrintQuoteRequest) -> PrintQuote:
        quantity = request.quantity
        return PrintQuote(
            kind="print_quote",
            provider=self.provider_name,
            status="draft_quote",
            source_asset_uri=request.print_candidate.source_asset_uri,
            print_candidate_uri=request.print_candidate.uri,
            currency="USD",
            estimated_price_cents=1600 * quantity,
            estimated_production_days=5,
            estimated_shipping_days=6,
            checkout_url=None,
            requires_user_approval=True,
            approval_reason=(
                "Draft quote must be reviewed before payment or third-party fulfillment."
            ),
            quote_notes=[
                f"material={request.material}",
                f"finish={request.finish}",
                f"ship_to_country={request.ship_to_country}",
                "local quote stub; no live provider call was made",
            ],
        )
