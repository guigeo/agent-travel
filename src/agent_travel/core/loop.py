from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any

from agent_travel.core.config import settings
from agent_travel.core.session import Session
from agent_travel.core.tool_registry import ToolRegistry

MSG_ERRO_AMIGAVEL = "Tive um problema para concluir essa consulta. Pode tentar reformular o pedido?"
MSG_LIMITE_ITERACOES = (
    "Essa consulta ficou complexa demais para eu resolver em uma única resposta. "
    "Pode dividir o pedido em partes menores?"
)


@dataclass
class ResultadoFerramenta:
    ferramenta: str
    dados: list[dict]


@dataclass
class Response:
    texto: str
    resultados: list[ResultadoFerramenta]


@dataclass
class TurnEvent:
    tipo: str
    ferramenta: str | None = None
    dados: list[dict] = field(default_factory=list)
    erro: bool = False
    texto: str | None = None
    resultados: list[ResultadoFerramenta] = field(default_factory=list)

    def to_dict(self) -> dict:
        payload: dict = {"tipo": self.tipo}
        if self.tipo == "tool_started":
            payload["ferramenta"] = self.ferramenta
        elif self.tipo == "tool_finished":
            payload["ferramenta"] = self.ferramenta
            payload["dados"] = self.dados
            payload["erro"] = self.erro
        elif self.tipo == "texto_final":
            payload["texto"] = self.texto or ""
            payload["resultados"] = [
                {"ferramenta": item.ferramenta, "dados": item.dados} for item in self.resultados
            ]
        return payload


def run_turn(
    client: Any, session: Session, registry: ToolRegistry, system_prompt: str, pergunta: str
) -> Response:
    """Motor de tool-calling genérico e reutilizável.

    Usado tanto pelo Orquestrador (planejador de viagem) quanto pelo Agente de
    Milhas — cada chamador injeta seu próprio system_prompt, ToolRegistry e
    Session, sem nenhum acoplamento entre os dois.
    """
    final: TurnEvent | None = None
    for event in iter_turn(client, session, registry, system_prompt, pergunta):
        if event.tipo == "texto_final":
            final = event
    if final is None:
        return Response(texto="", resultados=[])
    return Response(texto=final.texto or "", resultados=list(final.resultados))


def iter_turn(
    client: Any, session: Session, registry: ToolRegistry, system_prompt: str, pergunta: str
) -> Iterator[TurnEvent]:
    """Mesmo loop de `run_turn`, emitindo progresso de cada tool antes da resposta final."""
    session.messages.append({"role": "user", "content": pergunta})
    resultados: list[ResultadoFerramenta] = []
    erros = 0

    for _ in range(settings.max_tool_iters):
        resp = client.chat.completions.create(
            model=settings.llm_model,
            messages=[{"role": "system", "content": system_prompt}, *session.messages],
            tools=registry.openai_tools(),
        )
        msg = resp.choices[0].message
        session.messages.append(_assistant_dict(msg))

        if not msg.tool_calls:
            _trim(session)
            yield TurnEvent(tipo="texto_final", texto=msg.content or "", resultados=resultados)
            return

        for call in msg.tool_calls:
            yield TurnEvent(tipo="tool_started", ferramenta=call.function.name)
            result = registry.execute_tool(call.function.name, call.function.arguments)
            session.messages.append(
                {"role": "tool", "tool_call_id": call.id, "content": result.payload_json}
            )
            if result.error:
                erros += 1
                yield TurnEvent(
                    tipo="tool_finished",
                    ferramenta=call.function.name,
                    erro=True,
                )
                if erros >= 2:
                    _trim(session)
                    yield TurnEvent(
                        tipo="texto_final", texto=MSG_ERRO_AMIGAVEL, resultados=resultados
                    )
                    return
            else:
                yield TurnEvent(
                    tipo="tool_finished",
                    ferramenta=call.function.name,
                    dados=list(result.rows),
                    erro=False,
                )
                if result.ids:
                    # Acumula por ferramenta (não sobrescreve) — cada tool chamada no turno
                    # vira seu próprio card no frontend, em vez de só a última sobreviver.
                    resultados.append(
                        ResultadoFerramenta(ferramenta=call.function.name, dados=result.rows)
                    )

    _trim(session)
    yield TurnEvent(tipo="texto_final", texto=MSG_LIMITE_ITERACOES, resultados=resultados)


def _assistant_dict(msg: Any) -> dict:
    """Serializa a mensagem do SDK como dict — funciona com o SDK real e com fakes."""
    out: dict = {"role": "assistant", "content": msg.content}
    if msg.tool_calls:
        out["tool_calls"] = [
            {
                "id": c.id,
                "type": "function",
                "function": {"name": c.function.name, "arguments": c.function.arguments},
            }
            for c in msg.tool_calls
        ]
    return out


def _trim(session: Session, max_msgs: int = 20) -> None:
    """Poda SEMPRE em fronteira de turno (mensagem 'user').

    Cortar no meio orfanaria um tool result do seu assistant tool_call, e a API
    rejeitaria o histórico no turno seguinte. Aceita segurar 1 turno acima do teto.
    """
    msgs = session.messages
    while len(msgs) > max_msgs:
        try:
            cut = next(i for i, m in enumerate(msgs[1:], start=1) if m["role"] == "user")
        except StopIteration:
            break
        del msgs[:cut]
