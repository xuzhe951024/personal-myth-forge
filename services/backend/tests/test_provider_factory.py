from myth_forge_api.config import Settings
from myth_forge_api.providers.factory import build_three_d_provider
from myth_forge_api.providers.three_d import LocalThreeDProvider, MeshyThreeDProvider


def test_provider_factory_defaults_to_local_provider() -> None:
    provider = build_three_d_provider(Settings())

    assert isinstance(provider, LocalThreeDProvider)


def test_provider_factory_selects_meshy_provider() -> None:
    provider = build_three_d_provider(Settings(three_d_provider="meshy", meshy_api_key="test-key"))

    assert isinstance(provider, MeshyThreeDProvider)
