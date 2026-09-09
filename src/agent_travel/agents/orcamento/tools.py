from pydantic import BaseModel, Field

from agent_travel.core.tool_registry import ToolResult


class ItemCusto(BaseModel):
    descricao: str
    valor: float | None = Field(
        None,
        ge=0,
        description="Preço extraído da fonte. Omita quando não houver preço no trecho.",
    )
    a_confirmar: bool = Field(
        False,
        description="True quando o item existe mas o preço não foi extraído da fonte.",
    )


class CalcularOrcamentoArgs(BaseModel):
    """Consolida o custo total estimado de uma viagem e sinaliza se ultrapassa o orçamento
    máximo informado pelo viajante. Some somente itens com preço extraído; itens sem preço
    entram como a confirmar e ficam fora do total."""

    itens: list[ItemCusto] = Field(
        description="Itens da viagem. Use valor só com preço extraído; caso contrário a_confirmar=true."
    )
    orcamento_maximo: float | None = Field(
        None, ge=0, description="Orçamento máximo do viajante, se informado"
    )


def calcular_orcamento(args: CalcularOrcamentoArgs) -> ToolResult:
    confirmados: list[dict] = []
    a_confirmar: list[dict] = []
    for item in args.itens:
        if item.a_confirmar or item.valor is None:
            a_confirmar.append({"descricao": item.descricao})
        else:
            confirmados.append({"descricao": item.descricao, "valor": item.valor})
    total = sum(item["valor"] for item in confirmados)
    estourou = args.orcamento_maximo is not None and total > args.orcamento_maximo
    payload = {
        "itens": confirmados,
        "itens_a_confirmar": a_confirmar,
        "total_estimado": total,
        "orcamento_maximo": args.orcamento_maximo,
        "estourou_orcamento": estourou,
        "parcial": bool(a_confirmar),
    }
    return ToolResult(payload=payload, ids=["orcamento"], rows=[payload])
