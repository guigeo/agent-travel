from fastapi import APIRouter, Depends, Request
from openai import OpenAI

from agent_travel.api.schemas import MilesQueryRequest, MilesQueryResponse
from agent_travel.api.streaming import respond_turn
from agent_travel.core.llm_client import get_client
from agent_travel.core.session import SessionStore, SqliteSessionStore, miles_session_store
from agent_travel.milhas.prompt import MILES_SYSTEM_PROMPT
from agent_travel.milhas.registry import MILES_TOOL_REGISTRY

router = APIRouter(prefix="/miles", tags=["miles"])
_session_store: SessionStore | SqliteSessionStore | None = None


def _store() -> SessionStore | SqliteSessionStore:
    global _session_store
    if _session_store is None:
        _session_store = miles_session_store()
    return _session_store


@router.post("/query/{session_id}", response_model=None)
def query(
    session_id: str,
    body: MilesQueryRequest,
    request: Request,
    client: OpenAI = Depends(get_client),
):
    """Consulta o Agente de Milhas — totalmente independente da sessão de planejamento
    de viagem em `chat.py` (SessionStore próprio, sem session_id de viagem)."""
    return respond_turn(
        request=request,
        store=_store(),
        session_id=session_id,
        mensagem=body.mensagem,
        client=client,
        registry=MILES_TOOL_REGISTRY,
        system_prompt=MILES_SYSTEM_PROMPT,
        response_cls=MilesQueryResponse,
    )
