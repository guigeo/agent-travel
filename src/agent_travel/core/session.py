import time
from dataclasses import dataclass, field

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

    def _evict_expired(self) -> None:
        now = time.monotonic()
        expired = [sid for sid, s in self._sessions.items() if now - s.last_used_at > self._ttl]
        for sid in expired:
            del self._sessions[sid]
