from myth_forge_api.config import Settings
from myth_forge_api.providers.readiness import build_provider_readiness


def test_provider_readiness_defaults_to_demo_ready_local_stubs() -> None:
    readiness = build_provider_readiness(Settings())

    assert readiness.overall_demo_ready is True
    assert readiness.overall_real_ready is False
    providers = {item.kind: item for item in readiness.providers}
    assert providers["three_d"].selected_provider == "local"
    assert providers["three_d"].status == "local_stub"
    assert providers["three_d"].is_demo_ready is True
    assert providers["three_d"].is_real_provider_ready is False
    assert providers["npc"].selected_provider == "local"
    assert providers["npc"].status == "local_stub"
    assert providers["print"].selected_provider == "local"
    assert providers["print"].status == "local_stub"
    assert providers["capture_storage"].status == "ready"


def test_provider_readiness_reports_print_quote_stub_capability() -> None:
    readiness = build_provider_readiness(Settings())

    providers = {item.kind: item for item in readiness.providers}
    print_provider = providers["print"]
    assert print_provider.selected_provider == "local"
    assert print_provider.status == "local_stub"
    assert print_provider.is_demo_ready is True
    assert print_provider.is_real_provider_ready is False
    assert "quote_stub" in print_provider.capabilities


def test_provider_readiness_reports_missing_treatstock_key() -> None:
    readiness = build_provider_readiness(Settings(print_provider="treatstock"))

    providers = {item.kind: item for item in readiness.providers}
    print_provider = providers["print"]
    assert print_provider.selected_provider == "treatstock"
    assert print_provider.status == "missing_configuration"
    assert print_provider.is_demo_ready is False
    assert print_provider.is_real_provider_ready is False
    assert print_provider.missing_env == ["TREATSTOCK_API_KEY"]


def test_provider_readiness_does_not_mark_unimplemented_treatstock_ready() -> None:
    readiness = build_provider_readiness(
        Settings(print_provider="treatstock", treatstock_api_key="treatstock-secret")
    )

    providers = {item.kind: item for item in readiness.providers}
    print_provider = providers["print"]
    serialized = readiness.model_dump_json()
    assert print_provider.selected_provider == "treatstock"
    assert print_provider.status == "not_implemented"
    assert print_provider.is_demo_ready is False
    assert print_provider.is_real_provider_ready is False
    assert print_provider.missing_env == []
    assert "treatstock-secret" not in serialized


def test_provider_readiness_reports_missing_meshy_key_without_secret_value() -> None:
    readiness = build_provider_readiness(Settings(three_d_provider="meshy"))

    providers = {item.kind: item for item in readiness.providers}
    three_d = providers["three_d"]
    assert readiness.overall_demo_ready is False
    assert readiness.overall_real_ready is False
    assert three_d.selected_provider == "meshy"
    assert three_d.status == "missing_configuration"
    assert three_d.is_demo_ready is False
    assert three_d.is_real_provider_ready is False
    assert three_d.missing_env == ["MESHY_API_KEY"]
    assert "MESHY_API_KEY" in " ".join(three_d.notes)


def test_provider_readiness_marks_meshy_ready_without_leaking_key() -> None:
    readiness = build_provider_readiness(
        Settings(three_d_provider="meshy", meshy_api_key="sk-meshy-secret")
    )

    providers = {item.kind: item for item in readiness.providers}
    three_d = providers["three_d"]
    serialized = readiness.model_dump_json()
    assert three_d.status == "ready"
    assert three_d.is_demo_ready is True
    assert three_d.is_real_provider_ready is True
    assert three_d.missing_env == []
    assert "sk-meshy-secret" not in serialized


def test_provider_readiness_reports_missing_openai_key() -> None:
    readiness = build_provider_readiness(Settings(npc_provider="openai"))

    providers = {item.kind: item for item in readiness.providers}
    npc = providers["npc"]
    assert npc.selected_provider == "openai"
    assert npc.status == "missing_configuration"
    assert npc.is_demo_ready is False
    assert npc.is_real_provider_ready is False
    assert npc.missing_env == ["OPENAI_API_KEY"]
    assert "structured_agent_ticks" in npc.capabilities


def test_provider_readiness_marks_openai_ready_without_leaking_key() -> None:
    readiness = build_provider_readiness(
        Settings(npc_provider="openai", openai_api_key="sk-openai-secret")
    )

    providers = {item.kind: item for item in readiness.providers}
    npc = providers["npc"]
    serialized = readiness.model_dump_json()
    assert npc.status == "ready"
    assert npc.is_demo_ready is True
    assert npc.is_real_provider_ready is True
    assert npc.missing_env == []
    assert "structured_agent_ticks" in npc.capabilities
    assert "tick" in " ".join(npc.notes).lower()
    assert "sk-openai-secret" not in serialized
