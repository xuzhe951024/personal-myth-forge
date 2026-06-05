from fastapi.testclient import TestClient

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

