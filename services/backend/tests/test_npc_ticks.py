import pytest
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
from myth_forge_api.providers.npc import OpenAINPCConfigurationError, OpenAINPCProviderError
from myth_forge_api.providers.npc_ticks import (
    LocalNPCTickRuntime,
    OpenAINPCTickOutput,
    OpenAINPCTickRuntime,
)
from myth_forge_api.providers.session_store import LocalMythSessionStore


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


def test_openai_npc_tick_runtime_requires_api_key_before_network_call() -> None:
    runtime = OpenAINPCTickRuntime(api_key="", model="gpt-4.1-mini")

    with pytest.raises(OpenAINPCConfigurationError):
        runtime.generate_tick(NPCAgentTickRequest(session=_session(), tick_index=1))


def test_openai_npc_tick_runtime_parses_structured_response_without_raw_recent_events() -> None:
    parsed = _openai_tick_payload()
    client = FakeOpenAIClient(parsed)
    runtime = OpenAINPCTickRuntime(api_key="test-key", model="gpt-4.1-mini", client=client)
    request = NPCAgentTickRequest(
        session=_session_with_data_uri_asset(),
        tick_index=2,
        recent_events=["raw=data:image/jpeg;base64,ZmFrZQ== Authorization=Bearer test-secret"],
    )

    tick = runtime.generate_tick(request)

    assert tick.session_id == request.session.session_id
    assert tick.tick_index == 2
    assert tick.agent_runtime == "openai_tick_structured_runtime"
    assert [reaction.npc_id for reaction in tick.npc_reactions] == ["mara", "ior", "senn"]
    assert tick.world_resolution.accepted_actions
    call = client.responses.calls[0]
    prompt = call["input"][1]["content"]
    assert call["model"] == "gpt-4.1-mini"
    assert call["text_format"] is OpenAINPCTickOutput
    assert "1 recent village event" in prompt
    assert "data:image" not in prompt
    assert "test-secret" not in prompt
    assert "Authorization" not in prompt


def test_openai_npc_tick_runtime_synthesizes_missing_traces() -> None:
    runtime = OpenAINPCTickRuntime(
        api_key="test-key",
        model="gpt-4.1-mini",
        client=FakeOpenAIClient({"reactions": _openai_tick_payload()["reactions"]}),
    )

    tick = runtime.generate_tick(NPCAgentTickRequest(session=_session(), tick_index=1))

    assert [trace.npc_id for trace in tick.npc_agent_traces] == ["mara", "ior", "senn"]
    assert tick.npc_agent_traces[0].confidence == 0.5


def test_openai_npc_tick_runtime_replaces_trace_action_outside_reaction_plan() -> None:
    parsed = _openai_tick_payload()
    parsed["agent_traces"][0]["proposed_action"] = "order_print_without_approval"
    runtime = OpenAINPCTickRuntime(
        api_key="test-key",
        model="gpt-4.1-mini",
        client=FakeOpenAIClient(parsed),
    )

    tick = runtime.generate_tick(NPCAgentTickRequest(session=_session(), tick_index=1))

    assert tick.npc_agent_traces[0].proposed_action == "invite_neighbors_to_witness"
    assert tick.npc_agent_traces[0].rationale.startswith("Synthesized from")


def test_openai_npc_tick_runtime_rejects_wrong_npc_ids() -> None:
    runtime = OpenAINPCTickRuntime(
        api_key="test-key",
        model="gpt-4.1-mini",
        client=FakeOpenAIClient({"reactions": []}),
    )

    with pytest.raises(OpenAINPCProviderError, match="mara, ior, senn"):
        runtime.generate_tick(NPCAgentTickRequest(session=_session(), tick_index=1))


def test_openai_npc_tick_runtime_wraps_provider_errors_without_secret() -> None:
    runtime = OpenAINPCTickRuntime(
        api_key="test-key",
        model="gpt-4.1-mini",
        client=RaisingOpenAIClient(),
    )

    with pytest.raises(OpenAINPCProviderError) as exc:
        runtime.generate_tick(NPCAgentTickRequest(session=_session(), tick_index=1))

    message = str(exc.value)
    assert "test-secret" not in message
    assert "raw=private" not in message


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


def test_create_npc_tick_endpoint_appends_backend_session_history(monkeypatch, tmp_path) -> None:
    store = LocalMythSessionStore(tmp_path)
    monkeypatch.setattr("myth_forge_api.main.build_myth_session_store", lambda: store)
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
    history = store.get_history(session.session_id)
    assert history is not None
    assert history.session == session
    assert [tick.tick_index for tick in history.npc_ticks] == [1]


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


class FakeParsedResponse:
    def __init__(self, parsed) -> None:
        self.output_parsed = parsed


class FakeResponses:
    def __init__(self, parsed) -> None:
        self.parsed = parsed
        self.calls = []

    def parse(self, **kwargs):
        self.calls.append(kwargs)
        return FakeParsedResponse(self.parsed)


class FakeOpenAIClient:
    def __init__(self, parsed) -> None:
        self.responses = FakeResponses(parsed)


class RaisingResponses:
    def parse(self, **kwargs):
        raise RuntimeError("provider failed Authorization=Bearer test-secret raw=private")


class RaisingOpenAIClient:
    responses = RaisingResponses()


def _openai_tick_payload():
    return {
        "reactions": [
            {
                "npc_id": "mara",
                "name": "Mara",
                "emotion": "awe",
                "interpretation": "The village sees the key as a promise.",
                "plan": ["invite_neighbors_to_witness"],
                "world_change": "faith_in_player_increases",
            },
            {
                "npc_id": "ior",
                "name": "Ior",
                "emotion": "suspicion",
                "interpretation": "The key needs rules.",
                "plan": ["guard_artifact"],
                "world_change": "village_debate_starts",
            },
            {
                "npc_id": "senn",
                "name": "Senn",
                "emotion": "curiosity",
                "interpretation": "The key needs a public name.",
                "plan": ["suggest_ritual_name"],
                "world_change": "artifact_gets_a_local_name",
            },
        ],
        "agent_traces": [
            {
                "npc_id": "mara",
                "name": "Mara",
                "belief": "The village sees the key as a promise.",
                "intention": "turn awe into public witness",
                "proposed_action": "invite_neighbors_to_witness",
                "rationale": "Mara wants the reaction to stay communal.",
                "confidence": 0.82,
            },
            {
                "npc_id": "ior",
                "name": "Ior",
                "belief": "The key needs rules.",
                "intention": "guard the artifact without ending debate",
                "proposed_action": "guard_artifact",
                "rationale": "Ior distrusts unreviewed gifts.",
                "confidence": 0.71,
            },
            {
                "npc_id": "senn",
                "name": "Senn",
                "belief": "The key needs a public name.",
                "intention": "make the relic legible",
                "proposed_action": "suggest_ritual_name",
                "rationale": "Senn uses naming to make uncertainty safer.",
                "confidence": 0.78,
            },
        ],
    }
