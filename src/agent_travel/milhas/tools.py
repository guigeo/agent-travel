from pydantic import BaseModel, Field

from agent_travel.core.tool_registry import ToolResult
from agent_travel.milhas.backend import MilhasBackend


class BuscarBonusArgs(BaseModel):
    """Busca fontes públicas de bônus de transferência Itaú/Livelo e devolve no máximo
    duas opções (principal e alternativa). O percentual só vem preenchido se aparecer
    no trecho da fonte. Use para recomendar, não para listar links."""

    programa_destino: str | None = Field(
        None,
        description="Programa de milhas de destino, ex: Latam Pass, Smiles, TudoAzul — "
        "deixe vazio para buscar todos",
    )


def buscar_bonus_vigente(backend: MilhasBackend, args: BuscarBonusArgs) -> ToolResult:
    rows = backend.buscar_bonus_vigente(args.programa_destino)
    return ToolResult(payload=rows, ids=[r["id"] for r in rows], rows=rows)


class CalcularValorPontoArgs(BaseModel):
    """Calcula o valor efetivo de uma transferência de pontos Itaú para milhas, dado um
    bônus percentual e o valor estimado do milheiro no programa de destino."""

    pontos_disponiveis: int = Field(ge=0, description="Saldo de pontos Itaú disponível")
    bonus_percentual: float = Field(
        ge=0, description="Bônus de transferência vigente, em percentual (ex: 120 para 120%)"
    )
    valor_milheiro_estimado: float = Field(
        gt=0,
        description="Valor estimado de 1.000 milhas no programa de destino, em reais (ex: 25.0)",
    )


def calcular_valor_ponto(args: CalcularValorPontoArgs) -> ToolResult:
    milhas_resultantes = args.pontos_disponiveis * (1 + args.bonus_percentual / 100)
    valor_estimado_reais = (milhas_resultantes / 1000) * args.valor_milheiro_estimado
    valor_por_ponto_centavos = (
        (valor_estimado_reais / args.pontos_disponiveis) * 100 if args.pontos_disponiveis else 0.0
    )
    payload = {
        "milhas_resultantes": round(milhas_resultantes, 2),
        "valor_estimado_reais": round(valor_estimado_reais, 2),
        "valor_por_ponto_centavos": round(valor_por_ponto_centavos, 4),
    }
    return ToolResult(payload=payload, ids=["valor-ponto"], rows=[payload])
