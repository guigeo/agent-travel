import json
from collections.abc import Iterator

from fastapi import Request
from fastapi.responses import StreamingResponse
from openai import OpenAI

from agent_travel.core.loop import TurnEvent, iter_turn, run_turn
from agent_travel.core.session import SessionStore, SqliteSessionStore
from agent_travel.core.tool_registry import ToolRegistry

SessionStoreLike = SessionStore | SqliteSessionStore


def wants_sse(request: Request) -> bool:
    return "text/event-stream" in request.headers.get("accept", "")


def format_sse(event: TurnEvent) -> str:
    return f"event: {event.tipo}\ndata: {json.dumps(event.to_dict(), ensure_ascii=False)}\n\n"


def respond_turn(
    *,
    request: Request,
    store: SessionStoreLike,
    session_id: str,
    mensagem: str,
    client: OpenAI,
    registry: ToolRegistry,
    system_prompt: str,
    response_cls: type,
):
    session = store.get(session_id)
    if wants_sse(request):

        def generate() -> Iterator[str]:
            try:
                for event in iter_turn(client, session, registry, system_prompt, mensagem):
                    yield format_sse(event)
            finally:
                store.save(session_id, session)

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    response = run_turn(client, session, registry, system_prompt, mensagem)
    store.save(session_id, session)
    return response_cls(texto=response.texto, resultados=response.resultados)
