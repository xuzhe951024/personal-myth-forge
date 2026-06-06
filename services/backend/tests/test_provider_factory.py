from myth_forge_api.config import Settings
from myth_forge_api.providers.factory import (
    build_myth_session_store,
    build_npc_director,
    build_npc_tick_runtime,
    build_print_provider,
    build_three_d_provider,
)
from myth_forge_api.providers.npc import LocalNPCDirector, OpenAINPCDirector
from myth_forge_api.providers.npc_ticks import LocalNPCTickRuntime, OpenAINPCTickRuntime
from myth_forge_api.providers.printing import LocalPrintProvider, TreatstockPrintProvider
from myth_forge_api.providers.session_store import LocalMythSessionStore
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


def test_npc_tick_factory_defaults_to_local_runtime() -> None:
    runtime = build_npc_tick_runtime(Settings())

    assert isinstance(runtime, LocalNPCTickRuntime)


def test_npc_tick_factory_selects_openai_runtime() -> None:
    runtime = build_npc_tick_runtime(
        Settings(
            npc_provider="openai",
            openai_api_key="test-key",
            openai_api_base_url="https://openai.test/v1",
        )
    )

    assert isinstance(runtime, OpenAINPCTickRuntime)
    assert runtime.api_base_url == "https://openai.test/v1"


def test_print_factory_defaults_to_local_provider() -> None:
    provider = build_print_provider(Settings())

    assert isinstance(provider, LocalPrintProvider)


def test_print_factory_selects_treatstock_provider() -> None:
    provider = build_print_provider(
        Settings(
            print_provider="treatstock",
            treatstock_api_key="test-key",
            treatstock_api_base_url="https://treatstock.test",
        )
    )

    assert isinstance(provider, TreatstockPrintProvider)
    assert provider.api_base_url == "https://treatstock.test"


def test_myth_session_store_factory_uses_configured_local_directory(tmp_path) -> None:
    store = build_myth_session_store(Settings(myth_session_storage_dir=str(tmp_path)))

    assert isinstance(store, LocalMythSessionStore)
    assert store.root_dir == tmp_path
