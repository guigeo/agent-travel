from agent_travel.agents.orcamento.tools import (
    CalcularOrcamentoArgs,
    ItemCusto,
    calcular_orcamento,
)


def test_orcamento_dentro_do_limite_nao_estoura():
    args = CalcularOrcamentoArgs(
        itens=[ItemCusto(descricao="voo", valor=800), ItemCusto(descricao="hotel", valor=500)],
        orcamento_maximo=1500,
    )

    result = calcular_orcamento(args)

    assert result.payload["total_estimado"] == 1300
    assert result.payload["estourou_orcamento"] is False
    assert not result.error


def test_orcamento_estourado_sinaliza_sem_bloquear():
    args = CalcularOrcamentoArgs(
        itens=[ItemCusto(descricao="voo", valor=1200), ItemCusto(descricao="hotel", valor=700)],
        orcamento_maximo=1500,
    )

    result = calcular_orcamento(args)

    assert result.payload["total_estimado"] == 1900
    assert result.payload["estourou_orcamento"] is True
    assert not result.error


def test_orcamento_sem_limite_maximo_nunca_estoura():
    args = CalcularOrcamentoArgs(itens=[ItemCusto(descricao="voo", valor=1200)])

    result = calcular_orcamento(args)

    assert result.payload["estourou_orcamento"] is False
