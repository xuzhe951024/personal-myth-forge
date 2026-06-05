from myth_forge_api.domain.models import GeneratedAsset
from myth_forge_api.providers.printing import LocalPrintProvider
from myth_forge_api.providers.three_d import LocalThreeDProvider


def test_local_three_d_provider_returns_reviewable_game_asset() -> None:
    provider = LocalThreeDProvider()

    asset = provider.generate_game_asset(
        session_id="myth_test",
        prompt="Create a strange key-shaped relic for a mobile game scene.",
    )

    assert asset.kind == "game_asset"
    assert asset.provider == "local_stub"
    assert asset.format == "glb"
    assert asset.uri == "local://generated-assets/myth_test.glb"
    assert asset.moderation_status == "needs_review"


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

