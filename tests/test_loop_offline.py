from conftest import FakeClient, texto, tool_call
from pydantic import BaseModel, Field

from agent_travel.core.config import settings
from agent_travel.core.loop import (
    MSG_ERRO_AMIGAVEL,
    MSG_LIMITE_ITERACOES,
    iter_turn,
    run_turn,
)
from agent_travel.core.session import SessionStore
from agent_travel.core.tool_registry import ToolRegistry, ToolResult


class ListarOpcoesArgs(BaseModel):
    """Lista opções disponíveis para uma métrica."""

    metrica: str = Field("total")


def _listar_opcoes(args: ListarOpcoesArgs) -> ToolResult:
    if args.metrica not in {"total", "media"}:
        raise ValueError(f"métrica inválida: {args.metrica}. Válidas: total, media")
    return ToolResult(
        payload=[{"id": "1", "valor": 10}], ids=["1"], rows=[{"id": "1", "valor": 10}]
    )


REGISTRY = ToolRegistry({"listar_opcoes": (ListarOpcoesArgs, _listar_opcoes)})


def test_resposta_direta_sem_tool(nova_sessao):
    client = FakeClient([texto("Olá!")])
    out = run_turn(client, nova_sessao, REGISTRY, "system", "oi")
    assert out.texto == "Olá!"
    assert out.resultados == []


def test_tool_call_gera_grounding(nova_sessao):
    client = FakeClient([tool_call("listar_opcoes", {"metrica": "total"}), texto("A opção é X.")])
    out = run_turn(client, nova_sessao, REGISTRY, "system", "quais opções?")
    assert len(out.resultados) == 1
    assert out.resultados[0].ferramenta == "listar_opcoes"
    assert out.resultados[0].dados == [{"id": "1", "valor": 10}]


def test_autocorrecao_apos_erro_de_tool(nova_sessao):
    client = FakeClient(
        [
            tool_call("listar_opcoes", {"metrica": "inexistente"}),
            tool_call("listar_opcoes", {"metrica": "total"}),
            texto("A opção é X."),
        ]
    )
    out = run_turn(client, nova_sessao, REGISTRY, "system", "quais opções?")
    assert len(out.resultados) == 1
    assert out.resultados[0].ferramenta == "listar_opcoes"
    assert any(
        m.get("role") == "tool" and "erro" in m["content"]
        for r in client.requests
        for m in r["messages"]
    )


def test_2_erros_seguidos_mensagem_amigavel(nova_sessao):
    client = FakeClient(
        [
            tool_call("listar_opcoes", {"metrica": "inexistente"}),
            tool_call("listar_opcoes", {"metrica": "tambem_invalida"}),
            texto("não deveria chegar aqui"),
        ]
    )
    out = run_turn(client, nova_sessao, REGISTRY, "system", "quais opções?")
    assert out.texto == MSG_ERRO_AMIGAVEL


def test_teto_de_iteracoes(nova_sessao):
    client = FakeClient(
        [tool_call("listar_opcoes", {"metrica": "total"})] * settings.max_tool_iters
    )
    out = run_turn(client, nova_sessao, REGISTRY, "system", "loop")
    assert out.texto == MSG_LIMITE_ITERACOES
    assert len(client.requests) == settings.max_tool_iters


def test_multi_turno_preserva_historico():
    store = SessionStore()
    client = FakeClient([texto("Oi!"), texto("Continuando…")])
    run_turn(client, store.get("s1"), REGISTRY, "system", "primeira pergunta")
    run_turn(client, store.get("s1"), REGISTRY, "system", "segunda pergunta")
    ultimas = client.requests[-1]["messages"]
    assert any("primeira pergunta" in (m.get("content") or "") for m in ultimas)


def test_iter_turn_emite_progresso_das_tools(nova_sessao):
    client = FakeClient([tool_call("listar_opcoes", {"metrica": "total"}), texto("A opção é X.")])
    eventos = list(iter_turn(client, nova_sessao, REGISTRY, "system", "quais opções?"))
    tipos = [evento.tipo for evento in eventos]
    assert tipos == ["tool_started", "tool_finished", "texto_final"]
    assert eventos[0].ferramenta == "listar_opcoes"
    assert eventos[1].dados == [{"id": "1", "valor": 10}]
    assert eventos[2].texto == "A opção é X."
    assert eventos[2].resultados[0].ferramenta == "listar_opcoes"
