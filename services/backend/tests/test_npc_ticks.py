from fastapi.testclient import TestClient

from myth_forge_api.domain.arbitration import LocalWorldArbitrator
from myth_forge_api.domain.models import (
    GeneratedAsset,
    NPCAgentTickRequest,
    NPCReaction,
    WorldResolution,
)
from myth_forge_api.domain.pipeline import create_demo_myth_session
from myth_forge_api.main import app
from myth_forge_api.providers.npc_ticks import LocalNPCTickRuntime


def test_local_npc_tick_runtime_generates_three_agent_actions() -> None:
    session = _session()
    request = NPCAgentTickRequest(
        session=session,
        tick_index=1,
        recent_events=["Mara prepared to approach the artifact."],
    )

    tick = LocalNPCTickRuntime().generate_tick(request)

    assert tick.session_id == session.session_id
    assert tick.tick_index == 1
    assert tick.agent_runtime == "local_tick_runtime"
    assert [trace.npc_id for trace in tick.npc_agent_traces] == ["mara", "ior", "senn"]
    assert [reaction.npc_id for reaction in tick.npc_reactions] == ["mara", "ior", "senn"]
    assert all(trace.proposed_action for trace in tick.npc_agent_traces)
    assert all(reaction.plan for reaction in tick.npc_reactions)
    assert "1 recent village event" in tick.npc_agent_traces[0].rationale
    assert isinstance(tick.world_resolution, WorldResolution)
    assert tick.world_resolution.accepted_actions
    assert tick.world_resolution.visible_changes


def test_local_npc_tick_runtime_does_not_echo_recent_event_payloads() -> None:
    request = NPCAgentTickRequest(
        session=_session_with_data_uri_asset(),
        tick_index=2,
        recent_events=[
            "raw=data:image/jpeg;base64,ZmFrZQ== Authorization=Bearer test-secret",
        ],
    )

    tick = LocalNPCTickRuntime().generate_tick(request)
    payload = tick.model_dump_json()

    assert "data:image" not in payload
    assert "ZmFrZQ" not in payload
    assert "test-secret" not in payload
    assert "Authorization" not in payload


def test_world_arbitrator_rejects_unsafe_tick_action() -> None:
    session = _session()
    reaction = NPCReaction(
        npc_id="ior",
        name="Ior",
        emotion="suspicion",
        interpretation="Ior wants to bypass review.",
        plan=["order_print_without_approval"],
        world_change="village_debate_starts",
    )

    resolution = LocalWorldArbitrator().resolve(
        session_id=session.session_id,
        object_card=session.object_card,
        myth_seed=session.myth_seed,
        context_capsule=_tick_context(),
        generated_asset=session.generated_asset,
        npc_reactions=[reaction],
    )

    assert not resolution.accepted_actions
    assert resolution.rejected_actions[0].status == "rejected"
    assert resolution.rejected_actions[0].reason == "blocked by safety and privacy rules"


def test_create_npc_tick_endpoint_returns_tick_contract() -> None:
    session = _session()
    client = TestClient(app)

    response = client.post(
        "/v1/npc-ticks",
        json={
            "session": session.model_dump(mode="json"),
            "tick_index": 1,
            "recent_events": ["The village debate grows louder."],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["session_id"] == session.session_id
    assert payload["tick_index"] == 1
    assert payload["agent_runtime"] == "local_tick_runtime"
    assert len(payload["npc_agent_traces"]) == 3
    assert len(payload["npc_reactions"]) == 3
    assert payload["world_resolution"]["accepted_actions"]
    assert "data:image" not in response.text
    assert "local://generated-assets" not in response.text


def _session():
    return create_demo_myth_session(
        object_observation={
            "label": "old brass key",
            "materials": ["metal", "brass"],
            "source": "phone_capture",
        },
        context_capsule={
            "current_theme": "deadline pressure",
            "desired_tone": "tender and strange",
        },
    )


def _session_with_data_uri_asset():
    session = _session()
    return session.model_copy(
        update={
            "generated_asset": GeneratedAsset(
                kind="game_asset",
                provider="test",
                format="glb",
                uri="data:image/jpeg;base64,ZmFrZQ==",
                prompt=session.generated_asset.prompt,
                moderation_status="needs_review",
            )
        }
    )


def _tick_context():
    from myth_forge_api.domain.models import ContextCapsule

    return ContextCapsule(current_theme="tick test", desired_tone="watchful")
