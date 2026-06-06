from fastapi.testclient import TestClient

from myth_forge_api.config import Settings
from myth_forge_api.domain.models import GeneratedAsset
from myth_forge_api.main import app
from myth_forge_api.providers.npc import OpenAINPCConfigurationError
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
    assert payload["print_candidate"]["requires_user_approval"] is True


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
