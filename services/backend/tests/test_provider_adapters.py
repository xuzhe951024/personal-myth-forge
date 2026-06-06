from myth_forge_api.domain.models import GeneratedAsset
from myth_forge_api.providers.printing import LocalPrintProvider
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
    assert "source_images=1" in asset.prompt
    assert "source_assets=1" in asset.prompt
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
