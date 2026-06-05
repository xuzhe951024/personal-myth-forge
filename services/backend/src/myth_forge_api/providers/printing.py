from __future__ import annotations

from myth_forge_api.domain.models import GeneratedAsset, PrintCandidate


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

