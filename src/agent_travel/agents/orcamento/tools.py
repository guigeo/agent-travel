from pydantic import BaseModel, Field

from agent_travel.core.tool_registry import ToolResult


class ItemCusto(BaseModel):
    descricao: str
    valor: float = Field(ge=0)


class CalcularOrcamentoArgs(BaseModel):
    """Consolida o custo total estimado de uma viagem e sinaliza se ultrapassa o orçamento
    máximo informado pelo viajante."""

    itens: list[ItemCusto] = Field(
        description="Itens de custo da viagem, ex: voo, hospedagem, alimentação"
    )
    orcamento_maximo: float | None = Field(
        None, ge=0, description="Orçamento máximo do viajante, se informado"
    )


def calcular_orcamento(args: CalcularOrcamentoArgs) -> ToolResult:
    total = sum(item.valor for item in args.itens)
    estourou = args.orcamento_maximo is not None and total > args.orcamento_maximo
    payload = {
        "itens": [item.model_dump() for item in args.itens],
        "total_estimado": total,
        "orcamento_maximo": args.orcamento_maximo,
        "estourou_orcamento": estourou,
    }
    return ToolResult(payload=payload, ids=["orcamento"], rows=[payload])
