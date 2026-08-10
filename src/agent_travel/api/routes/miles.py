from fastapi import APIRouter, Depends
from openai import OpenAI

from agent_travel.api.schemas import MilesQueryRequest, MilesQueryResponse
from agent_travel.core.llm_client import get_client
from agent_travel.core.loop import run_turn
from agent_travel.core.session import SessionStore
from agent_travel.milhas.prompt import MILES_SYSTEM_PROMPT
from agent_travel.milhas.registry import MILES_TOOL_REGISTRY

router = APIRouter(prefix="/miles", tags=["miles"])
_session_store = SessionStore()


@router.post("/query/{session_id}", response_model=MilesQueryResponse)
def query(
    session_id: str, body: MilesQueryRequest, client: OpenAI = Depends(get_client)
) -> MilesQueryResponse:
    """Consulta o Agente de Milhas — totalmente independente da sessão de planejamento
    de viagem em `chat.py` (SessionStore próprio, sem session_id de viagem)."""
    session = _session_store.get(session_id)
    response = run_turn(client, session, MILES_TOOL_REGISTRY, MILES_SYSTEM_PROMPT, body.mensagem)
    return MilesQueryResponse(texto=response.texto, acao_ui=response.acao_ui, dados=response.dados)
