import pytest

from myth_forge_api.domain.models import ContextCapsule, GeneratedAsset, MythSeed, ObjectCard
from myth_forge_api.providers.npc import (
    LocalNPCDirector,
    OpenAINPCConfigurationError,
    OpenAINPCDirector,
    OpenAINPCProviderError,
)


def _object_card() -> ObjectCard:
    return ObjectCard(
        label="old brass key",
        materials=["metal"],
        source="manual_upload",
        affordances=["can become a ritual focus"],
        symbolic_reading="A key has crossed into the village.",
    )


def _myth_seed() -> MythSeed:
    return MythSeed(
        title="The Old Brass Key That Fell Through the Sky",
        personal_resonance="It reflects a watchful reset.",
        generation_prompt="Create a mythic key.",
    )


def _capsule() -> ContextCapsule:
    return ContextCapsule(current_theme="reset", desired_tone="watchful")


def _asset() -> GeneratedAsset:
    return GeneratedAsset(
        kind="game_asset",
        provider="local_stub",
        format="glb",
        uri="local://generated-assets/myth_test.glb",
        prompt="Create a mythic key.",
        moderation_status="needs_review",
    )


def test_local_npc_director_returns_stable_three_npc_reactions() -> None:
    result = LocalNPCDirector().generate_reactions(
        session_id="myth_test",
        object_card=_object_card(),
        myth_seed=_myth_seed(),
        context_capsule=_capsule(),
        generated_asset=_asset(),
    )

    assert result.provider == "local_stub"
    assert result.agent_runtime == "local_agent_runtime"
    assert {reaction.npc_id for reaction in result.reactions} == {"mara", "ior", "senn"}
    assert {trace.npc_id for trace in result.agent_traces} == {"mara", "ior", "senn"}
    assert all(reaction.plan for reaction in result.reactions)
    assert all(trace.belief for trace in result.agent_traces)
    assert all(trace.intention for trace in result.agent_traces)
    assert all(trace.proposed_action for trace in result.agent_traces)
    assert all(trace.rationale for trace in result.agent_traces)
    assert all(0 <= trace.confidence <= 1 for trace in result.agent_traces)
    proposed_actions = {trace.proposed_action for trace in result.agent_traces}
    reaction_actions = {reaction.plan[0] for reaction in result.reactions}
    assert proposed_actions <= reaction_actions


def test_openai_npc_director_requires_api_key_before_network_call() -> None:
    director = OpenAINPCDirector(api_key="", model="gpt-4.1-mini")

    with pytest.raises(OpenAINPCConfigurationError):
        director.generate_reactions(
            session_id="myth_test",
            object_card=_object_card(),
            myth_seed=_myth_seed(),
            context_capsule=_capsule(),
            generated_asset=_asset(),
        )


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


def test_openai_npc_director_parses_structured_response() -> None:
    parsed = {
        "reactions": [
            {
                "npc_id": "mara",
                "name": "Mara",
                "emotion": "awe",
                "interpretation": "The key is a promise.",
                "plan": ["approach_artifact"],
                "world_change": "faith_in_player_increases",
            },
            {
                "npc_id": "ior",
                "name": "Ior",
                "emotion": "suspicion",
                "interpretation": "The key is a test.",
                "plan": ["keep_distance"],
                "world_change": "village_debate_starts",
            },
            {
                "npc_id": "senn",
                "name": "Senn",
                "emotion": "curiosity",
                "interpretation": "The key needs a name.",
                "plan": ["suggest_ritual_name"],
                "world_change": "artifact_gets_a_local_name",
            },
        ],
        "agent_traces": [
            {
                "npc_id": "mara",
                "name": "Mara",
                "belief": "The key is a promise.",
                "intention": "welcome the artifact",
                "proposed_action": "approach_artifact",
                "rationale": "Mara treats awe as an invitation to witness.",
                "confidence": 0.82,
            },
            {
                "npc_id": "ior",
                "name": "Ior",
                "belief": "The key is a test.",
                "intention": "protect the village",
                "proposed_action": "keep_distance",
                "rationale": "Ior distrusts gifts that arrive without provenance.",
                "confidence": 0.69,
            },
            {
                "npc_id": "senn",
                "name": "Senn",
                "belief": "The key needs a name.",
                "intention": "turn curiosity into ritual language",
                "proposed_action": "suggest_ritual_name",
                "rationale": "Senn believes naming makes strange objects safer.",
                "confidence": 0.74,
            },
        ],
    }
    client = FakeOpenAIClient(parsed)
    director = OpenAINPCDirector(api_key="test-key", model="gpt-4.1-mini", client=client)

    result = director.generate_reactions(
        session_id="myth_test",
        object_card=_object_card(),
        myth_seed=_myth_seed(),
        context_capsule=_capsule(),
        generated_asset=_asset(),
    )

    assert result.provider == "openai"
    assert result.agent_runtime == "openai_structured_runtime"
    assert [reaction.npc_id for reaction in result.reactions] == ["mara", "ior", "senn"]
    assert [trace.npc_id for trace in result.agent_traces] == ["mara", "ior", "senn"]
    assert result.agent_traces[0].proposed_action == "approach_artifact"
    assert client.responses.calls[0]["model"] == "gpt-4.1-mini"
    assert "raw private data" in client.responses.calls[0]["input"][0]["content"].lower()
    assert "agent trace" in client.responses.calls[0]["input"][1]["content"].lower()


def test_openai_npc_director_synthesizes_agent_traces_when_missing() -> None:
    parsed = {
        "reactions": [
            {
                "npc_id": "mara",
                "name": "Mara",
                "emotion": "awe",
                "interpretation": "The key is a promise.",
                "plan": ["approach_artifact"],
                "world_change": "faith_in_player_increases",
            },
            {
                "npc_id": "ior",
                "name": "Ior",
                "emotion": "suspicion",
                "interpretation": "The key is a test.",
                "plan": ["keep_distance"],
                "world_change": "village_debate_starts",
            },
            {
                "npc_id": "senn",
                "name": "Senn",
                "emotion": "curiosity",
                "interpretation": "The key needs a name.",
                "plan": ["suggest_ritual_name"],
                "world_change": "artifact_gets_a_local_name",
            },
        ]
    }
    director = OpenAINPCDirector(api_key="test-key", model="gpt-4.1-mini", client=FakeOpenAIClient(parsed))

    result = director.generate_reactions(
        session_id="myth_test",
        object_card=_object_card(),
        myth_seed=_myth_seed(),
        context_capsule=_capsule(),
        generated_asset=_asset(),
    )

    assert [trace.npc_id for trace in result.agent_traces] == ["mara", "ior", "senn"]
    assert result.agent_traces[0].belief == "The key is a promise."
    assert result.agent_traces[0].proposed_action == "approach_artifact"
    assert result.agent_traces[0].confidence == 0.5


def test_openai_npc_director_rejects_wrong_npc_ids() -> None:
    parsed = {"reactions": []}
    director = OpenAINPCDirector(
        api_key="test-key",
        model="gpt-4.1-mini",
        client=FakeOpenAIClient(parsed),
    )

    with pytest.raises(OpenAINPCProviderError, match="mara, ior, senn"):
        director.generate_reactions(
            session_id="myth_test",
            object_card=_object_card(),
            myth_seed=_myth_seed(),
            context_capsule=_capsule(),
            generated_asset=_asset(),
        )


class RaisingResponses:
    def parse(self, **kwargs):
        raise RuntimeError("provider failed Authorization=Bearer test-secret")


class RaisingOpenAIClient:
    responses = RaisingResponses()


def test_openai_npc_director_wraps_sdk_errors() -> None:
    director = OpenAINPCDirector(
        api_key="test-key",
        model="gpt-4.1-mini",
        client=RaisingOpenAIClient(),
    )

    with pytest.raises(OpenAINPCProviderError):
        director.generate_reactions(
            session_id="myth_test",
            object_card=_object_card(),
            myth_seed=_myth_seed(),
            context_capsule=_capsule(),
            generated_asset=_asset(),
        )
