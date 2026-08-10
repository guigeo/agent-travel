from fastapi import APIRouter, Depends
from openai import OpenAI

from agent_travel.api.schemas import ChatRequest, ChatResponse
from agent_travel.core.llm_client import get_client
from agent_travel.core.loop import run_turn
from agent_travel.core.session import SessionStore
from agent_travel.orchestrator.prompt import PLANNER_SYSTEM_PROMPT
from agent_travel.orchestrator.registry import PLANNER_TOOL_REGISTRY

router = APIRouter(prefix="/chat", tags=["chat"])
_session_store = SessionStore()


@router.post("/{session_id}", response_model=ChatResponse)
def send_message(
    session_id: str, body: ChatRequest, client: OpenAI = Depends(get_client)
) -> ChatResponse:
    session = _session_store.get(session_id)
    response = run_turn(
        client, session, PLANNER_TOOL_REGISTRY, PLANNER_SYSTEM_PROMPT, body.mensagem
    )
    return ChatResponse(texto=response.texto, acao_ui=response.acao_ui, dados=response.dados)
