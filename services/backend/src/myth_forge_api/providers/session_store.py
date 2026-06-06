from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

from myth_forge_api.domain.models import (
    SESSION_ID_PATTERN,
    MythSession,
    MythSessionHistory,
    NPCAgentTick,
)

DEFAULT_MAX_TICKS = 24
SESSION_ID_RE = re.compile(SESSION_ID_PATTERN)
DATA_URI_RE = re.compile(
    r"data:[A-Za-z0-9.+-]+/[A-Za-z0-9.+-]+;base64,[A-Za-z0-9+/=_-]+",
    re.IGNORECASE,
)
AUTH_BEARER_ASSIGN_RE = re.compile(
    r"\bAuthorization\s*[=:]\s*Bearer\s+[^\s,;\"']+",
    re.IGNORECASE,
)
BEARER_TOKEN_RE = re.compile(r"\bBearer\s+[^\s,;\"']+", re.IGNORECASE)
RAW_VALUE_RE = re.compile(r"\braw\s*=\s*[^\s,;\"']+", re.IGNORECASE)
API_KEY_RE = re.compile(r"\bapi[_-]?key\s*[=:]\s*[^\s,;\"']+", re.IGNORECASE)


class MythSessionStore(Protocol):
    def save_session(self, session: MythSession) -> MythSessionHistory:
        ...

    def append_tick(self, session: MythSession, tick: NPCAgentTick) -> MythSessionHistory:
        ...

    def get_history(self, session_id: str) -> MythSessionHistory | None:
        ...

    def get_session(self, session_id: str) -> MythSession | None:
        ...


class MythSessionStoreError(RuntimeError):
    status_code = 400


class MythSessionNotFoundError(MythSessionStoreError):
    status_code = 404


class LocalMythSessionStore:
    def __init__(self, root_dir: str | Path, max_ticks: int = DEFAULT_MAX_TICKS) -> None:
        self.root_dir = Path(root_dir)
        self.max_ticks = max_ticks

    def save_session(self, session: MythSession) -> MythSessionHistory:
        self._validate_session_id(session.session_id)
        existing = self.get_history(session.session_id)
        history = MythSessionHistory(
            session_id=session.session_id,
            session=_sanitized_session(session),
            npc_ticks=existing.npc_ticks if existing is not None else [],
            updated_at=_utc_now(),
        )
        self._write_history(history)
        return history

    def append_tick(self, session: MythSession, tick: NPCAgentTick) -> MythSessionHistory:
        self._validate_session_id(session.session_id)
        if tick.session_id != session.session_id:
            raise MythSessionNotFoundError(
                f"NPC tick does not belong to myth session: {tick.session_id}"
            )

        existing = self.get_history(session.session_id)
        ticks = existing.npc_ticks if existing is not None else []
        bounded_ticks = sorted([*ticks, _sanitized_tick(tick)], key=lambda item: item.tick_index)[
            -self.max_ticks :
        ]
        history = MythSessionHistory(
            session_id=session.session_id,
            session=existing.session if existing is not None else _sanitized_session(session),
            npc_ticks=bounded_ticks,
            updated_at=_utc_now(),
        )
        self._write_history(history)
        return history

    def get_history(self, session_id: str) -> MythSessionHistory | None:
        if SESSION_ID_RE.fullmatch(session_id) is None:
            return None
        history_path = self._history_path(session_id)
        if history_path is None or not history_path.is_file():
            return None
        data = json.loads(history_path.read_text(encoding="utf-8"))
        return MythSessionHistory.model_validate(data)

    def get_session(self, session_id: str) -> MythSession | None:
        history = self.get_history(session_id)
        if history is None:
            return None
        return history.session

    def _validate_session_id(self, session_id: str) -> None:
        if SESSION_ID_RE.fullmatch(session_id) is None:
            raise MythSessionNotFoundError(f"Myth session not found: {session_id}")

    def _history_path(self, session_id: str) -> Path | None:
        root_dir = self.root_dir.resolve()
        history_path = (self.root_dir / session_id / "history.json").resolve()
        try:
            history_path.relative_to(root_dir)
        except ValueError:
            return None
        return history_path

    def _write_history(self, history: MythSessionHistory) -> None:
        history_path = self._history_path(history.session_id)
        if history_path is None:
            raise MythSessionNotFoundError(f"Myth session not found: {history.session_id}")
        history_path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(history.model_dump(mode="json"), indent=2, sort_keys=True)
        tmp_path = history_path.with_suffix(f".{os.getpid()}.tmp")
        tmp_path.write_text(payload, encoding="utf-8")
        os.replace(tmp_path, history_path)


def _sanitized_session(session: MythSession) -> MythSession:
    return MythSession.model_validate(_sanitize_value(session.model_dump(mode="json")))


def _sanitized_tick(tick: NPCAgentTick) -> NPCAgentTick:
    return NPCAgentTick.model_validate(_sanitize_value(tick.model_dump(mode="json")))


def _sanitize_value(value: Any) -> Any:
    if isinstance(value, str):
        return _sanitize_text(value)
    if isinstance(value, list):
        return [_sanitize_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _sanitize_value(item) for key, item in value.items()}
    return value


def _sanitize_text(text: str) -> str:
    sanitized = DATA_URI_RE.sub("[redacted-data-uri]", text)
    sanitized = AUTH_BEARER_ASSIGN_RE.sub("[redacted-secret]", sanitized)
    sanitized = BEARER_TOKEN_RE.sub("Bearer [redacted]", sanitized)
    sanitized = API_KEY_RE.sub("api_key=[redacted]", sanitized)
    return RAW_VALUE_RE.sub("raw=[redacted]", sanitized)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
