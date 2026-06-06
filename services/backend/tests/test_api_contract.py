from fastapi.testclient import TestClient

from myth_forge_api.config import Settings
from myth_forge_api.domain.models import GeneratedAsset, MythSession, NPCAgentTick
from myth_forge_api.domain.pipeline import create_demo_myth_session
from myth_forge_api.main import app
from myth_forge_api.providers.npc import OpenAINPCConfigurationError, OpenAINPCProviderError
from myth_forge_api.providers.session_store import LocalMythSessionStore
from myth_forge_api.providers.three_d import ThreeDGenerationRequest


def test_create_myth_session_endpoint_returns_reviewable_session() -> None:
    client = TestClient(app)

    response = client.post(
        "/v1/myth-sessions",
        json={
            "object_observation": {
                "label": "tiny desk plant",
                "materials": ["leaf", "soil", "ceramic"],
                "source": "phone_capture",
            },
            "context_capsule": {
                "current_theme": "new beginning",
                "desired_tone": "hopeful but mysterious",
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready_for_review"
    assert payload["object_card"]["label"] == "tiny desk plant"
    assert len(payload["npc_reactions"]) == 3
    assert payload["npc_agent_runtime"] == "local_agent_runtime"
    assert len(payload["npc_agent_traces"]) == 3
    assert payload["npc_agent_traces"][0]["proposed_action"]
    assert payload["generated_asset"]["kind"] == "game_asset"
    assert payload["generated_asset"]["variants"][1]["role"] == "ios_scene_asset"
    assert payload["generated_asset"]["variants"][1]["format"] == "usdz"
    assert payload["generated_asset"]["variants"][1]["is_scene_loadable"] is True
    provenance = payload["generated_asset"]["generation_provenance"]
    assert provenance["input_mode"] == "text_prompt"
    assert provenance["provider_route"] == "local_stub"
    assert provenance["source_image_count"] == 0
    assert provenance["selected_source_image_count"] == 0
    assert provenance["raw_sources_included"] is False
    assert "data:image" not in response.text
    assert "/tmp" not in response.text
    assert payload["print_candidate"]["requires_user_approval"] is True


def _print_candidate_payload() -> dict[str, object]:
    return {
        "kind": "print_asset",
        "source_asset_uri": "local://generated-assets/myth_test.glb",
        "provider": "local_stub",
        "format": "3mf",
        "uri": "local://print-candidates/myth_test.3mf",
        "requires_user_approval": True,
        "approval_reason": "review before fulfillment",
        "printability_notes": ["stable base", "repair thin parts"],
    }


def test_create_print_quote_returns_safe_local_quote() -> None:
    client = TestClient(app)

    response = client.post(
        "/v1/print-quotes",
        json={
            "print_candidate": _print_candidate_payload(),
            "quantity": 2,
            "material": "standard_resin",
            "finish": "matte",
            "ship_to_country": "US",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["kind"] == "print_quote"
    assert payload["provider"] == "local_stub"
    assert payload["status"] == "draft_quote"
    assert payload["source_asset_uri"] == "local://generated-assets/myth_test.glb"
    assert payload["print_candidate_uri"] == "local://print-candidates/myth_test.3mf"
    assert payload["currency"] == "USD"
    assert payload["estimated_price_cents"] == 3200
    assert payload["estimated_production_days"] == 5
    assert payload["estimated_shipping_days"] == 6
    assert payload["checkout_url"] is None
    assert payload["requires_user_approval"] is True
    assert "data:image" not in response.text
    assert "api_key" not in response.text.lower()


def test_demo_route_serves_mobile_first_shell() -> None:
    client = TestClient(app)

    response = client.get("/demo")

    assert response.status_code == 200
    assert "Personal Myth Forge" in response.text
    assert "myth-form" in response.text


class ApiFakeThreeDProvider:
    provider_name = "api_fake"

    def generate_game_asset(self, request: ThreeDGenerationRequest) -> GeneratedAsset:
        return GeneratedAsset(
            kind="game_asset",
            provider=self.provider_name,
            format="glb",
            uri=f"api-fake://{request.session_id}.glb",
            prompt=request.prompt,
            moderation_status="needs_review",
        )


def test_create_myth_session_endpoint_uses_three_d_provider_factory(monkeypatch) -> None:
    monkeypatch.setattr(
        "myth_forge_api.main.build_three_d_provider",
        lambda: ApiFakeThreeDProvider(),
    )
    client = TestClient(app)

    response = client.post(
        "/v1/myth-sessions",
        json={
            "object_observation": {
                "label": "pocket mirror",
                "materials": ["glass", "metal"],
                "source": "manual_upload",
            },
            "context_capsule": {
                "current_theme": "changing self image",
                "desired_tone": "bright and eerie",
            },
        },
    )

    assert response.status_code == 200
    assert response.json()["generated_asset"]["provider"] == "api_fake"


def test_create_myth_session_maps_provider_errors_to_502_without_secret_leak(
    monkeypatch,
) -> None:
    def raise_provider_error():
        raise OpenAINPCConfigurationError(
            "OPENAI_API_KEY is required for NPC generation. "
            "raw=test-secret Authorization=Bearer test-secret"
        )

    monkeypatch.setattr("myth_forge_api.main.build_npc_director", raise_provider_error)
    client = TestClient(app)

    response = client.post(
        "/v1/myth-sessions",
        json={
            "object_observation": {
                "label": "mirror",
                "materials": ["glass"],
                "source": "manual_upload",
            },
            "context_capsule": {
                "current_theme": "self recognition",
                "desired_tone": "bright and eerie",
            },
        },
    )

    assert response.status_code == 502
    assert "OPENAI_API_KEY" in response.json()["detail"]
    assert "test-secret" not in response.json()["detail"]
    assert "Authorization" not in response.json()["detail"]


def test_create_myth_session_response_includes_world_resolution() -> None:
    client = TestClient(app)

    response = client.post(
        "/v1/myth-sessions",
        json={
            "object_observation": {
                "label": "tiny bell",
                "materials": ["metal"],
                "source": "manual_upload",
            },
            "context_capsule": {
                "current_theme": "calling attention",
                "desired_tone": "solemn and bright",
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["npc_director"] == "local_stub"
    assert payload["world_resolution"]["visible_changes"]


def test_create_myth_session_endpoint_persists_readable_history(monkeypatch, tmp_path) -> None:
    store = LocalMythSessionStore(tmp_path)
    monkeypatch.setattr("myth_forge_api.main.build_myth_session_store", lambda: store)
    client = TestClient(app)

    response = client.post(
        "/v1/myth-sessions",
        json={
            "object_observation": {
                "label": "tiny bell",
                "materials": ["metal"],
                "source": "manual_upload",
            },
            "context_capsule": {
                "current_theme": "calling attention",
                "desired_tone": "solemn and bright",
            },
        },
    )
    assert response.status_code == 200
    session_id = response.json()["session_id"]

    history_response = client.get(f"/v1/myth-sessions/{session_id}/history")

    assert history_response.status_code == 200
    history = history_response.json()
    assert history["session_id"] == session_id
    assert history["session"]["session_id"] == session_id
    assert history["npc_ticks"] == []
    assert history["updated_at"]


def test_get_myth_session_endpoint_returns_saved_session(monkeypatch, tmp_path) -> None:
    store = LocalMythSessionStore(tmp_path)
    session = MythSession.model_validate(_sample_myth_session())
    store.save_session(session)
    monkeypatch.setattr("myth_forge_api.main.build_myth_session_store", lambda: store)
    client = TestClient(app)

    response = client.get(f"/v1/myth-sessions/{session.session_id}")

    assert response.status_code == 200
    assert response.json()["session_id"] == session.session_id


def test_get_myth_session_history_unknown_session_returns_404(monkeypatch, tmp_path) -> None:
    store = LocalMythSessionStore(tmp_path)
    monkeypatch.setattr("myth_forge_api.main.build_myth_session_store", lambda: store)
    client = TestClient(app)

    response = client.get("/v1/myth-sessions/myth_0000000000000000/history")

    assert response.status_code == 404


def test_create_npc_tick_endpoint_returns_safe_agent_tick() -> None:
    client = TestClient(app)
    session_response = client.post(
        "/v1/myth-sessions",
        json={
            "object_observation": {
                "label": "tiny bell",
                "materials": ["metal"],
                "source": "manual_upload",
            },
            "context_capsule": {
                "current_theme": "calling attention",
                "desired_tone": "solemn and bright",
            },
        },
    )
    session = session_response.json()

    response = client.post(
        "/v1/npc-ticks",
        json={
            "session": session,
            "tick_index": 1,
            "recent_events": [
                "raw=data:image/jpeg;base64,ZmFrZQ== Authorization=Bearer test-secret"
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["session_id"] == session["session_id"]
    assert payload["agent_runtime"] == "local_tick_runtime"
    assert len(payload["npc_agent_traces"]) == 3
    assert payload["world_resolution"]["visible_changes"]
    assert "data:image" not in response.text
    assert "test-secret" not in response.text
    assert "Authorization" not in response.text


class FakeTickRuntime:
    def generate_tick(self, request):
        return NPCAgentTick(
            session_id=request.session.session_id,
            tick_index=request.tick_index,
            agent_runtime="fake_tick_runtime",
            npc_agent_traces=request.session.npc_agent_traces,
            npc_reactions=request.session.npc_reactions,
            world_resolution=request.session.world_resolution,
        )


def test_create_npc_tick_endpoint_routes_through_provider_factory(monkeypatch) -> None:
    monkeypatch.setattr("myth_forge_api.main.build_npc_tick_runtime", lambda: FakeTickRuntime())
    session = _sample_myth_session()
    client = TestClient(app)

    response = client.post(
        "/v1/npc-ticks",
        json={"session": session, "tick_index": 3, "recent_events": []},
    )

    assert response.status_code == 200
    assert response.json()["agent_runtime"] == "fake_tick_runtime"


def test_create_npc_tick_endpoint_sanitizes_openai_errors(monkeypatch) -> None:
    class RaisingTickRuntime:
        def generate_tick(self, request):
            raise OpenAINPCProviderError("failed Authorization=Bearer test-secret raw=private")

    monkeypatch.setattr("myth_forge_api.main.build_npc_tick_runtime", lambda: RaisingTickRuntime())
    client = TestClient(app)

    response = client.post(
        "/v1/npc-ticks",
        json={"session": _sample_myth_session(), "tick_index": 1, "recent_events": []},
    )

    assert response.status_code == 502
    assert "test-secret" not in response.text
    assert "raw=private" not in response.text
    assert "[redacted]" in response.text


def test_demo_route_includes_world_resolution_mount_points() -> None:
    client = TestClient(app)

    response = client.get("/demo")

    assert response.status_code == 200
    assert "world-state-strip" in response.text
    assert "visible-changes" in response.text


def test_demo_route_includes_capture_upload_mount_points() -> None:
    client = TestClient(app)

    response = client.get("/demo")

    assert response.status_code == 200
    assert 'type="file"' in response.text
    assert "capture-status" in response.text


def test_provider_readiness_endpoint_returns_safe_status(monkeypatch) -> None:
    monkeypatch.setattr(
        "myth_forge_api.main.load_settings",
        lambda: Settings(
            three_d_provider="meshy",
            meshy_api_key="sk-meshy-secret",
            npc_provider="openai",
            openai_api_key=None,
        ),
    )
    client = TestClient(app)

    response = client.get("/v1/provider-readiness")

    assert response.status_code == 200
    payload = response.json()
    assert payload["overall_demo_ready"] is False
    assert payload["overall_real_ready"] is False
    providers = {item["kind"]: item for item in payload["providers"]}
    assert providers["three_d"]["status"] == "ready"
    assert providers["three_d"]["is_real_provider_ready"] is True
    assert providers["npc"]["status"] == "missing_configuration"
    assert providers["npc"]["missing_env"] == ["OPENAI_API_KEY"]
    assert "MESHY_API_KEY" not in response.text
    assert "sk-meshy-secret" not in response.text
    assert "OPENAI_API_KEY" in response.text


def _sample_myth_session() -> dict:
    session = create_demo_myth_session(
        object_observation={
            "label": "tiny bell",
            "materials": ["metal"],
            "source": "manual_upload",
        },
        context_capsule={
            "current_theme": "calling attention",
            "desired_tone": "solemn and bright",
        },
    )
    return session.model_dump(mode="json")
