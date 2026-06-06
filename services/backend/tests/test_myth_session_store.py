import json

import pytest

from myth_forge_api.domain.models import GeneratedAsset, MythSessionHistory, NPCAgentTick
from myth_forge_api.domain.pipeline import create_demo_myth_session
from myth_forge_api.providers.session_store import (
    LocalMythSessionStore,
    MythSessionNotFoundError,
)


def test_local_myth_session_store_saves_and_loads_session_history(tmp_path) -> None:
    store = LocalMythSessionStore(root_dir=tmp_path)
    session = _session()

    history = store.save_session(session)

    assert history.session_id == session.session_id
    assert history.session == session
    assert history.npc_ticks == []
    assert history.updated_at
    assert store.get_history(session.session_id) == history
    assert store.get_session(session.session_id) == session
    assert (tmp_path / session.session_id / "history.json").exists()


def test_local_myth_session_store_appends_matching_ticks_sorted_and_bounded(tmp_path) -> None:
    store = LocalMythSessionStore(root_dir=tmp_path, max_ticks=3)
    session = _session()
    store.save_session(session)

    for index in [2, 1, 4, 3]:
        store.append_tick(session, _tick(session.session_id, index))

    history = store.get_history(session.session_id)

    assert history is not None
    assert [tick.tick_index for tick in history.npc_ticks] == [2, 3, 4]
    assert all(tick.session_id == session.session_id for tick in history.npc_ticks)


def test_local_myth_session_store_saves_session_when_appending_first_tick(tmp_path) -> None:
    store = LocalMythSessionStore(root_dir=tmp_path)
    session = _session()

    history = store.append_tick(session, _tick(session.session_id, 1))

    assert history.session == session
    assert [tick.tick_index for tick in history.npc_ticks] == [1]


def test_local_myth_session_store_rejects_invalid_session_ids(tmp_path) -> None:
    store = LocalMythSessionStore(root_dir=tmp_path)

    assert store.get_history("../myth_0000000000000000") is None
    with pytest.raises(MythSessionNotFoundError):
        store.append_tick(_session(), _tick("other_session", 1))


def test_local_myth_session_store_history_json_excludes_raw_payloads_and_secrets(tmp_path) -> None:
    store = LocalMythSessionStore(root_dir=tmp_path)
    session = _session_with_data_uri_asset()

    history = store.append_tick(
        session,
        _tick(session.session_id, 1, visible_change="Authorization=Bearer test-secret raw=private"),
    )
    body = (tmp_path / session.session_id / "history.json").read_text(encoding="utf-8")
    parsed = json.loads(body)

    assert MythSessionHistory.model_validate(parsed) == history
    assert "data:image" not in body
    assert "test-secret" not in body
    assert "Authorization=Bearer" not in body
    assert "raw=private" not in body


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


def _tick(session_id: str, tick_index: int, visible_change: str = "Mara circles the relic.") -> NPCAgentTick:
    session = _session()
    return NPCAgentTick(
        session_id=session_id,
        tick_index=tick_index,
        agent_runtime="local_tick_runtime",
        npc_agent_traces=session.npc_agent_traces,
        npc_reactions=session.npc_reactions,
        world_resolution=session.world_resolution.model_copy(update={"visible_changes": [visible_change]}),
    )
