from __future__ import annotations

import json
import sqlite3
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

from agent_travel.core.config import settings


@dataclass
class Session:
    messages: list[dict] = field(default_factory=list)
    last_used_at: float = field(default_factory=time.monotonic)


class SessionStore:
    """Sessões em memória com TTL — uma instância por agente (Orquestrador e
    Agente de Milhas usam stores separados, reforçando o desacoplamento)."""

    def __init__(self, ttl_seconds: int | None = None):
        self._ttl = ttl_seconds if ttl_seconds is not None else settings.session_ttl_seconds
        self._sessions: dict[str, Session] = {}

    def get(self, session_id: str) -> Session:
        self._evict_expired()
        session = self._sessions.get(session_id)
        if session is None:
            session = Session()
            self._sessions[session_id] = session
        session.last_used_at = time.monotonic()
        return session

    def save(self, session_id: str, session: Session) -> None:
        session.last_used_at = time.monotonic()
        self._sessions[session_id] = session

    def _evict_expired(self) -> None:
        now = time.monotonic()
        expired = [sid for sid, s in self._sessions.items() if now - s.last_used_at > self._ttl]
        for sid in expired:
            del self._sessions[sid]


class SqliteSessionStore:
    """Histórico de conversa em SQLite, com o mesmo contrato get/save do store em memória."""

    def __init__(self, db_path: str | Path, ttl_seconds: int | None = None):
        self._ttl = ttl_seconds if ttl_seconds is not None else settings.session_ttl_seconds
        self._path = Path(db_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    messages TEXT NOT NULL,
                    last_used_at REAL NOT NULL
                )
                """
            )

    def get(self, session_id: str) -> Session:
        now = time.time()
        with self._lock, self._connect() as conn:
            self._evict_expired(conn, now)
            row = conn.execute(
                "SELECT messages FROM sessions WHERE session_id = ?",
                (session_id,),
            ).fetchone()
            if row is None:
                return Session()
            return Session(messages=json.loads(row[0]), last_used_at=time.monotonic())

    def save(self, session_id: str, session: Session) -> None:
        payload = json.dumps(session.messages, ensure_ascii=False)
        now = time.time()
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                INSERT INTO sessions (session_id, messages, last_used_at)
                VALUES (?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    messages = excluded.messages,
                    last_used_at = excluded.last_used_at
                """,
                (session_id, payload, now),
            )

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._path)
        conn.isolation_level = None
        return conn

    def _evict_expired(self, conn: sqlite3.Connection, now: float) -> None:
        conn.execute(
            "DELETE FROM sessions WHERE last_used_at < ?",
            (now - self._ttl,),
        )


def create_session_store(db_path: str | Path | None) -> SessionStore | SqliteSessionStore:
    if not db_path:
        return SessionStore()
    return SqliteSessionStore(db_path)


def planner_session_store() -> SessionStore | SqliteSessionStore:
    return create_session_store(_db_file("planner-sessions.sqlite"))


def miles_session_store() -> SessionStore | SqliteSessionStore:
    return create_session_store(_db_file("miles-sessions.sqlite"))


def _db_file(name: str) -> str | None:
    directory = settings.session_db_dir.strip()
    if not directory:
        return None
    return str(Path(directory) / name)
