from __future__ import annotations

import re
from typing import Protocol

import httpx

from myth_forge_api.domain.models import GeneratedAsset, PrintCandidate, PrintQuote, PrintQuoteRequest

TREATSTOCK_SUPPORTED_FORMATS = {"stl", "ply", "3mf"}


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


class TreatstockProviderError(ValueError):
    pass


class TreatstockConfigurationError(TreatstockProviderError):
    pass


class TreatstockPrintProvider:
    provider_name = "treatstock"
    _printable_packs_path = "/api/v2/printable-packs"
    _printable_pack_costs_path = "/api/v2/printable-pack-costs/"

    def __init__(
        self,
        api_key: str | None,
        api_base_url: str = "https://www.treatstock.com",
        client=None,
        max_cost_attempts: int = 3,
    ) -> None:
        self.api_key = api_key
        self.api_base_url = api_base_url.rstrip("/")
        self.client = client or httpx.Client(base_url=self.api_base_url, timeout=30)
        self.max_cost_attempts = max_cost_attempts

    @classmethod
    def from_settings(cls, settings: object) -> "TreatstockPrintProvider":
        return cls(
            api_key=getattr(settings, "treatstock_api_key"),
            api_base_url=getattr(settings, "treatstock_api_base_url"),
        )

    def create_print_candidate(self, generated_asset: GeneratedAsset) -> PrintCandidate:
        print_source = _print_source_variant(generated_asset)
        if print_source is not None:
            return PrintCandidate(
                kind="print_asset",
                source_asset_uri=generated_asset.uri,
                provider=self.provider_name,
                format=print_source.format.lower(),
                uri=print_source.uri,
                requires_user_approval=True,
                approval_reason=(
                    "Treatstock quote handoff requires user review before checkout or order placement."
                ),
                printability_notes=[
                    "provider-ready print source selected from generated asset variants",
                    "quote adapter uploads only STL, PLY, or 3MF URLs",
                    "manual review remains required before fulfillment",
                ],
            )

        local_candidate = LocalPrintProvider().create_print_candidate(generated_asset)
        return local_candidate.model_copy(update={"provider": self.provider_name})

    def create_print_quote(self, request: PrintQuoteRequest) -> PrintQuote:
        self._validate_configuration()
        candidate = request.print_candidate
        candidate_format = candidate.format.lower()
        if candidate_format not in TREATSTOCK_SUPPORTED_FORMATS:
            raise TreatstockProviderError(
                "Treatstock quote handoff requires an STL, PLY, or 3MF print candidate."
            )
        upload_url = _candidate_upload_url(candidate)
        if upload_url is None:
            raise TreatstockProviderError(
                "Treatstock quote handoff requires an http or https print candidate URL."
            )

        try:
            upload_payload = self._upload_printable_pack(
                upload_url=upload_url,
                ship_to_country=request.ship_to_country,
            )
            pack_id = _printable_pack_id(upload_payload)
            if request.quantity > 1:
                self._update_quantity(
                    pack_id=pack_id,
                    quantity=request.quantity,
                    parts=upload_payload.get("parts"),
                )
            chosen_cost = self._retrieve_lowest_cost(
                pack_id=pack_id,
                ship_to_country=request.ship_to_country,
            )
        except TreatstockProviderError:
            raise
        except Exception as exc:
            message = _sanitize_provider_error(exc, secret=self.api_key)
            raise TreatstockProviderError(f"Treatstock quote failed: {message}") from exc

        price_cents = int(round(float(chosen_cost["price"]) * 100))
        checkout_url = chosen_cost.get("url") or upload_payload.get("redir")
        return PrintQuote(
            kind="print_quote",
            provider=self.provider_name,
            status="draft_quote",
            source_asset_uri=candidate.source_asset_uri,
            print_candidate_uri=candidate.uri,
            currency="USD",
            estimated_price_cents=price_cents,
            estimated_production_days=0,
            estimated_shipping_days=0,
            checkout_url=checkout_url,
            requires_user_approval=True,
            approval_reason=(
                "Treatstock quote must be reviewed before checkout or third-party order placement."
            ),
            quote_notes=[
                f"Treatstock printablePackId={pack_id}",
                f"material={request.material}",
                f"finish={request.finish}",
                f"ship_to_country={request.ship_to_country}",
                "production and shipping days are not returned by the quote API",
            ],
        )

    def _validate_configuration(self) -> None:
        if not self.api_key:
            raise TreatstockConfigurationError(
                "TREATSTOCK_API_KEY is required for Treatstock print quotes."
            )

    def _upload_printable_pack(self, *, upload_url: str, ship_to_country: str) -> dict:
        response = self.client.post(
            self._printable_packs_path,
            params={"private-key": self.api_key},
            data={
                "files-urls[]": upload_url,
                "location[country]": ship_to_country,
            },
        )
        return self._json_response(response, "upload printable pack")

    def _update_quantity(self, *, pack_id: int, quantity: int, parts) -> None:
        part_uids = _part_uids(parts)
        if not part_uids:
            return
        data = {f"qty[{uid}]": str(quantity) for uid in part_uids}
        response = self.client.put(
            f"{self._printable_packs_path}/{pack_id}",
            params={"private-key": self.api_key},
            data=data,
        )
        self._json_response(response, "update printable pack quantity")

    def _retrieve_lowest_cost(self, *, pack_id: int, ship_to_country: str) -> dict:
        last_payload = None
        for _ in range(max(1, self.max_cost_attempts)):
            response = self.client.get(
                self._printable_pack_costs_path,
                params={
                    "printablePackId": pack_id,
                    "private-key": self.api_key,
                    "location[country]": ship_to_country,
                },
            )
            payload = self._json_response(
                response,
                "retrieve printable pack costs",
                allow_not_calculated=True,
            )
            last_payload = payload
            if (
                isinstance(payload, dict)
                and payload.get("success") is False
                and payload.get("reason") == "not_calculated_yet"
            ):
                continue
            return _lowest_cost(payload)
        raise TreatstockProviderError(
            f"Treatstock costs were not calculated after {self.max_cost_attempts} attempts: "
            f"{_safe_payload(last_payload)}"
        )

    def _json_response(self, response, action: str, *, allow_not_calculated: bool = False):
        status_code = getattr(response, "status_code", 200)
        try:
            payload = response.json()
        except Exception as exc:
            message = _sanitize_provider_error(exc, secret=self.api_key)
            raise TreatstockProviderError(
                f"Treatstock {action} response was not JSON: {message}"
            ) from exc
        if status_code >= 400:
            raise TreatstockProviderError(
                f"Treatstock {action} HTTP {status_code}: {_safe_payload(payload)}"
            )
        if (
            allow_not_calculated
            and isinstance(payload, dict)
            and payload.get("success") is False
            and payload.get("reason") == "not_calculated_yet"
        ):
            return payload
        if isinstance(payload, dict) and payload.get("success") is False:
            raise TreatstockProviderError(
                f"Treatstock {action} failed: {_safe_payload(payload)}"
            )
        return payload


def _print_source_variant(generated_asset: GeneratedAsset):
    for variant in generated_asset.variants:
        if (
            variant.role == "print_source"
            and variant.format.lower() in TREATSTOCK_SUPPORTED_FORMATS
        ):
            return variant
    return None


def _candidate_upload_url(candidate: PrintCandidate) -> str | None:
    if candidate.uri.startswith("http://") or candidate.uri.startswith("https://"):
        return candidate.uri
    return None


def _printable_pack_id(payload: dict) -> int:
    if not isinstance(payload, dict) or payload.get("id") is None:
        raise TreatstockProviderError("Treatstock upload response did not include a printable pack id.")
    return int(payload["id"])


def _part_uids(parts) -> list[str]:
    if not isinstance(parts, dict):
        return []
    uids: list[str] = []
    for key, value in parts.items():
        if isinstance(value, dict) and value.get("uid"):
            uids.append(str(value["uid"]))
        else:
            uids.append(str(key))
    return uids


def _lowest_cost(payload) -> dict:
    if not isinstance(payload, list) or not payload:
        raise TreatstockProviderError(
            f"Treatstock cost response did not include quotes: {_safe_payload(payload)}"
        )
    quotes = [item for item in payload if isinstance(item, dict) and item.get("price") is not None]
    if not quotes:
        raise TreatstockProviderError(
            f"Treatstock cost response did not include prices: {_safe_payload(payload)}"
        )
    return min(quotes, key=lambda item: float(item["price"]))


def _safe_payload(payload) -> str:
    text = str(payload)
    return _sanitize_provider_error(Exception(text))


def _sanitize_provider_error(exc: Exception, secret: str | None = None) -> str:
    message = str(exc)
    if secret:
        message = message.replace(secret, "[redacted]")
    replacements = [
        r"Authorization\s*[=:]\s*Bearer\s+\[[^\]]+\]",
        r"Authorization\s*[=:]\s*Bearer\s+[A-Za-z0-9._~+/\-=:-]+",
        r"Bearer\s+[A-Za-z0-9._~+/\-=:-]+",
        r"private-key[=:/\s]+[A-Za-z0-9._~+/\-=:-]+",
        r"raw=[^\s,;\"']+",
        r"api[_-]?key\s*[=:]\s*[^\s,;\"']+",
    ]
    for pattern in replacements:
        message = re.sub(pattern, "[redacted]", message, flags=re.IGNORECASE)
    return message
