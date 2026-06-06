import pytest

from myth_forge_api.domain.models import GeneratedAsset, PrintCandidate, PrintQuoteRequest
from myth_forge_api.providers.printing import (
    LocalPrintProvider,
    TreatstockConfigurationError,
    TreatstockPrintProvider,
    TreatstockProviderError,
)
from myth_forge_api.providers.three_d import (
    LocalThreeDProvider,
    ThreeDGenerationRequest,
    ThreeDSourceAsset,
    ThreeDSourceImage,
)


def test_local_three_d_provider_returns_reviewable_game_asset() -> None:
    provider = LocalThreeDProvider()

    request = ThreeDGenerationRequest(
        session_id="myth_test",
        prompt="Create a strange key-shaped relic for a mobile game scene.",
        source_images=(
            ThreeDSourceImage(
                uri="local-capture://cap_0123456789abcdef/media_0.jpg",
                content_type="image/jpeg",
                data_uri="data:image/jpeg;base64,ZmFrZQ==",
            ),
        ),
        source_assets=(
            ThreeDSourceAsset(
                uri="local-capture://cap_0123456789abcdef/media_1.glb",
                content_type="model/gltf-binary",
            ),
        ),
    )
    asset = provider.generate_game_asset(request)

    assert asset.kind == "game_asset"
    assert asset.provider == "local_stub"
    assert asset.format == "glb"
    assert asset.uri == "local://generated-assets/myth_test.glb"
    assert asset.variants[1].role == "ios_scene_asset"
    assert asset.variants[1].format == "dae"
    assert asset.variants[1].uri == "local://generated-assets/myth_test.dae"
    assert asset.variants[1].is_scene_loadable is True
    assert "source_images=1" in asset.prompt
    assert "source_assets=1" in asset.prompt
    assert asset.moderation_status == "needs_review"
    assert asset.generation_provenance is not None
    assert asset.generation_provenance.input_mode == "single_image"
    assert asset.generation_provenance.provider_route == "local_stub"
    assert asset.generation_provenance.source_image_count == 1
    assert asset.generation_provenance.selected_source_image_count == 1
    assert asset.generation_provenance.source_asset_count == 1
    assert asset.generation_provenance.raw_sources_included is False


def test_local_three_d_provider_records_text_prompt_provenance() -> None:
    provider = LocalThreeDProvider()

    asset = provider.generate_game_asset(
        ThreeDGenerationRequest(
            session_id="myth_text",
            prompt="Create a text-only relic.",
        )
    )

    assert asset.generation_provenance is not None
    assert asset.generation_provenance.input_mode == "text_prompt"
    assert asset.generation_provenance.source_image_count == 0
    assert asset.generation_provenance.selected_source_image_count == 0
    assert asset.generation_provenance.source_asset_count == 0
    assert asset.generation_provenance.raw_sources_included is False


def test_local_three_d_provider_records_multi_image_provenance() -> None:
    provider = LocalThreeDProvider()

    asset = provider.generate_game_asset(
        ThreeDGenerationRequest(
            session_id="myth_multi",
            prompt="Create a multi-image relic.",
            source_images=(
                ThreeDSourceImage(
                    uri="local-capture://cap_0123456789abcdef/media_0.jpg",
                    content_type="image/jpeg",
                    data_uri="data:image/jpeg;base64,ZmFrZTE=",
                ),
                ThreeDSourceImage(
                    uri="local-capture://cap_0123456789abcdef/media_1.png",
                    content_type="image/png",
                    data_uri="data:image/png;base64,ZmFrZTI=",
                ),
            ),
        )
    )

    assert asset.generation_provenance is not None
    assert asset.generation_provenance.input_mode == "multi_image"
    assert asset.generation_provenance.source_image_count == 2
    assert asset.generation_provenance.selected_source_image_count == 2
    assert asset.generation_provenance.source_asset_count == 0
    assert asset.generation_provenance.raw_sources_included is False


def test_local_print_provider_derives_candidate_from_generated_asset() -> None:
    asset = GeneratedAsset(
        kind="game_asset",
        provider="local_stub",
        format="glb",
        uri="local://generated-assets/myth_test.glb",
        prompt="Create a strange key-shaped relic for a mobile game scene.",
        moderation_status="needs_review",
    )
    provider = LocalPrintProvider()

    candidate = provider.create_print_candidate(asset)

    assert candidate.kind == "print_asset"
    assert candidate.provider == "local_stub"
    assert candidate.format == "3mf"
    assert candidate.source_asset_uri == asset.uri
    assert candidate.uri == "local://print-candidates/myth_test.3mf"
    assert candidate.requires_user_approval is True


def test_local_print_provider_creates_draft_quote() -> None:
    asset = GeneratedAsset(
        kind="game_asset",
        provider="local_stub",
        format="glb",
        uri="local://generated-assets/myth_test.glb",
        prompt="Create a strange key-shaped relic for a mobile game scene.",
        moderation_status="needs_review",
    )
    provider = LocalPrintProvider()
    candidate = provider.create_print_candidate(asset)

    quote = provider.create_print_quote(
        PrintQuoteRequest(
            print_candidate=candidate,
            quantity=2,
            material="standard_resin",
            finish="matte",
            ship_to_country="US",
        )
    )

    assert quote.kind == "print_quote"
    assert quote.provider == "local_stub"
    assert quote.status == "draft_quote"
    assert quote.estimated_price_cents == 3200
    assert quote.currency == "USD"
    assert quote.checkout_url is None
    assert quote.requires_user_approval is True


def test_treatstock_print_provider_creates_quote_from_url_upload() -> None:
    client = FakeTreatstockClient(
        responses=[
            FakeTreatstockResponse(
                {
                    "success": True,
                    "id": 223672,
                    "redir": "https://www.treatstock.com/catalog/model3d/preload-printable-pack?packPublicToken=abc",
                    "parts": {"MP:1815136": {"uid": "MP:1815136"}},
                }
            ),
            FakeTreatstockResponse(
                [
                    {
                        "printablePackId": 223672,
                        "materialGroup": "PLA",
                        "color": "White",
                        "price": 8.25,
                        "url": "https://www.treatstock.com/model3d/preload-printable-pack?packPublicToken=def",
                    },
                    {
                        "printablePackId": 223672,
                        "materialGroup": "PLA",
                        "color": "Black",
                        "price": 5.74,
                        "url": "https://www.treatstock.com/model3d/preload-printable-pack?packPublicToken=abc",
                    },
                ]
            ),
        ]
    )
    provider = TreatstockPrintProvider(api_key="treatstock-secret", client=client)

    quote = provider.create_print_quote(
        PrintQuoteRequest(print_candidate=remote_print_candidate())
    )

    assert quote.provider == "treatstock"
    assert quote.status == "draft_quote"
    assert quote.estimated_price_cents == 574
    assert quote.currency == "USD"
    assert quote.checkout_url == (
        "https://www.treatstock.com/model3d/preload-printable-pack?packPublicToken=abc"
    )
    assert quote.requires_user_approval is True
    assert "Treatstock printablePackId=223672" in quote.quote_notes
    assert client.requests[0]["method"] == "POST"
    assert client.requests[0]["url"] == "/api/v2/printable-packs"
    assert client.requests[0]["params"] == {"private-key": "treatstock-secret"}
    assert client.requests[0]["data"]["files-urls[]"] == "https://example.com/relic.3mf"
    assert client.requests[0]["data"]["location[country]"] == "US"
    assert client.requests[1]["method"] == "GET"
    assert client.requests[1]["url"] == "/api/v2/printable-pack-costs/"
    assert client.requests[1]["params"]["printablePackId"] == 223672


def test_treatstock_print_provider_updates_quantity_before_costs() -> None:
    client = FakeTreatstockClient(
        responses=[
            FakeTreatstockResponse(
                {
                    "success": True,
                    "id": 223672,
                    "parts": {"MP:1": {"uid": "MP:1"}},
                }
            ),
            FakeTreatstockResponse({"success": True}),
            FakeTreatstockResponse(
                [
                    {
                        "price": 18.42,
                        "url": "https://www.treatstock.com/model3d/preload-printable-pack?packPublicToken=qty",
                    }
                ]
            ),
        ]
    )
    provider = TreatstockPrintProvider(api_key="treatstock-secret", client=client)

    quote = provider.create_print_quote(
        PrintQuoteRequest(print_candidate=remote_print_candidate(), quantity=3)
    )

    assert quote.estimated_price_cents == 1842
    assert client.requests[1]["method"] == "PUT"
    assert client.requests[1]["url"] == "/api/v2/printable-packs/223672"
    assert client.requests[1]["data"] == {"qty[MP:1]": "3"}
    assert client.requests[2]["method"] == "GET"


def test_treatstock_print_provider_retries_costs_not_calculated_yet() -> None:
    client = FakeTreatstockClient(
        responses=[
            FakeTreatstockResponse({"success": True, "id": 223672, "parts": {}}),
            FakeTreatstockResponse({"success": False, "reason": "not_calculated_yet"}),
            FakeTreatstockResponse([{"price": 6.12}]),
        ]
    )
    provider = TreatstockPrintProvider(
        api_key="treatstock-secret",
        client=client,
        max_cost_attempts=2,
    )

    quote = provider.create_print_quote(
        PrintQuoteRequest(print_candidate=remote_print_candidate())
    )

    cost_requests = [
        request
        for request in client.requests
        if request["url"] == "/api/v2/printable-pack-costs/"
    ]
    assert quote.estimated_price_cents == 612
    assert len(cost_requests) == 2


def test_treatstock_print_provider_requires_api_key() -> None:
    provider = TreatstockPrintProvider(api_key="", client=FakeTreatstockClient())

    with pytest.raises(TreatstockConfigurationError):
        provider.create_print_quote(PrintQuoteRequest(print_candidate=remote_print_candidate()))


def test_treatstock_print_provider_requires_http_candidate_url() -> None:
    provider = TreatstockPrintProvider(api_key="treatstock-secret", client=FakeTreatstockClient())
    candidate = remote_print_candidate(uri="local://print-candidates/relic.3mf")

    with pytest.raises(TreatstockProviderError, match="requires an http"):
        provider.create_print_quote(PrintQuoteRequest(print_candidate=candidate))


def test_treatstock_print_provider_requires_supported_candidate_format() -> None:
    provider = TreatstockPrintProvider(api_key="treatstock-secret", client=FakeTreatstockClient())
    candidate = remote_print_candidate(format="glb", uri="https://example.com/relic.glb")

    with pytest.raises(TreatstockProviderError, match="STL, PLY, or 3MF"):
        provider.create_print_quote(PrintQuoteRequest(print_candidate=candidate))


def test_treatstock_print_provider_sanitizes_provider_failures() -> None:
    provider = TreatstockPrintProvider(
        api_key="treatstock-secret",
        client=RaisingTreatstockClient(),
    )

    with pytest.raises(TreatstockProviderError) as exc:
        provider.create_print_quote(PrintQuoteRequest(print_candidate=remote_print_candidate()))

    error_text = str(exc.value)
    assert "treatstock-secret" not in error_text
    assert "Authorization" not in error_text
    assert "raw=private" not in error_text


def remote_print_candidate(
    *,
    format: str = "3mf",
    uri: str = "https://example.com/relic.3mf",
) -> PrintCandidate:
    return PrintCandidate(
        kind="print_asset",
        source_asset_uri="https://example.com/relic-source.3mf",
        provider="local_stub",
        format=format,
        uri=uri,
        requires_user_approval=True,
        approval_reason="Review before provider quote.",
        printability_notes=["test candidate"],
    )


class FakeTreatstockResponse:
    def __init__(self, payload, status_code: int = 200) -> None:
        self.payload = payload
        self.status_code = status_code

    def json(self):
        return self.payload


class FakeTreatstockClient:
    def __init__(self, responses=None) -> None:
        self.responses = list(responses or [])
        self.requests = []

    def post(self, url, *, params=None, data=None):
        self.requests.append(
            {"method": "POST", "url": url, "params": params, "data": data}
        )
        return self.responses.pop(0)

    def put(self, url, *, params=None, data=None):
        self.requests.append(
            {"method": "PUT", "url": url, "params": params, "data": data}
        )
        return self.responses.pop(0)

    def get(self, url, *, params=None):
        self.requests.append(
            {"method": "GET", "url": url, "params": params, "data": None}
        )
        return self.responses.pop(0)


class RaisingTreatstockClient:
    def post(self, url, *, params=None, data=None):
        raise RuntimeError("Authorization=Bearer treatstock-secret raw=private")
