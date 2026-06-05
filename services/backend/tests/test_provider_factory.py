from myth_forge_api.config import Settings
from myth_forge_api.providers.factory import build_npc_director, build_three_d_provider
from myth_forge_api.providers.npc import LocalNPCDirector, OpenAINPCDirector
from myth_forge_api.providers.three_d import LocalThreeDProvider, MeshyThreeDProvider


def test_provider_factory_defaults_to_local_provider() -> None:
    provider = build_three_d_provider(Settings())

    assert isinstance(provider, LocalThreeDProvider)


def test_provider_factory_selects_meshy_provider() -> None:
    provider = build_three_d_provider(Settings(three_d_provider="meshy", meshy_api_key="test-key"))

    assert isinstance(provider, MeshyThreeDProvider)


def test_npc_factory_defaults_to_local_director() -> None:
    director = build_npc_director(Settings())

    assert isinstance(director, LocalNPCDirector)


def test_npc_factory_selects_openai_director() -> None:
    director = build_npc_director(
        Settings(
            npc_provider="openai",
            openai_api_key="test-key",
            openai_api_base_url="https://openai.test/v1",
        )
    )

    assert isinstance(director, OpenAINPCDirector)
    assert director.api_base_url == "https://openai.test/v1"
