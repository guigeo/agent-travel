from fastapi import APIRouter, Depends, Request
from openai import OpenAI

from agent_travel.api.schemas import ChatRequest, ChatResponse
from agent_travel.api.streaming import respond_turn
from agent_travel.core.llm_client import get_client
from agent_travel.core.session import SessionStore, SqliteSessionStore, planner_session_store
from agent_travel.orchestrator.prompt import PLANNER_SYSTEM_PROMPT
from agent_travel.orchestrator.registry import PLANNER_TOOL_REGISTRY

router = APIRouter(prefix="/chat", tags=["chat"])
_session_store: SessionStore | SqliteSessionStore | None = None


def _store() -> SessionStore | SqliteSessionStore:
    global _session_store
    if _session_store is None:
        _session_store = planner_session_store()
    return _session_store


@router.post("/{session_id}", response_model=None)
def send_message(
    session_id: str,
    body: ChatRequest,
    request: Request,
    client: OpenAI = Depends(get_client),
):
    return respond_turn(
        request=request,
        store=_store(),
        session_id=session_id,
        mensagem=body.mensagem,
        client=client,
        registry=PLANNER_TOOL_REGISTRY,
        system_prompt=PLANNER_SYSTEM_PROMPT,
        response_cls=ChatResponse,
    )
