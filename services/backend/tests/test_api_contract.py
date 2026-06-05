from fastapi.testclient import TestClient

from myth_forge_api.domain.models import GeneratedAsset
from myth_forge_api.main import app


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
    assert payload["generated_asset"]["kind"] == "game_asset"
    assert payload["print_candidate"]["requires_user_approval"] is True


def test_demo_route_serves_mobile_first_shell() -> None:
    client = TestClient(app)

    response = client.get("/demo")

    assert response.status_code == 200
    assert "Personal Myth Forge" in response.text
    assert "myth-form" in response.text


class ApiFakeThreeDProvider:
    provider_name = "api_fake"

    def generate_game_asset(self, session_id: str, prompt: str) -> GeneratedAsset:
        return GeneratedAsset(
            kind="game_asset",
            provider=self.provider_name,
            format="glb",
            uri=f"api-fake://{session_id}.glb",
            prompt=prompt,
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
