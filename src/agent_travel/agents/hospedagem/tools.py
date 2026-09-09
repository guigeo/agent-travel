from pydantic import BaseModel, Field

from agent_travel.agents.hospedagem.backend import HospedagemBackend
from agent_travel.core.tool_registry import ToolResult


class BuscarHospedagemArgs(BaseModel):
    """Busca fontes confiáveis de hospedagem e devolve no máximo duas opções (principal e
    alternativa), com preço somente se ele aparecer no trecho da fonte. Use para montar
    UMA recomendação — não é inventário de hotéis."""

    destino: str = Field(description="Cidade ou região onde buscar hospedagem")
    data_checkin: str = Field(description="Data de check-in no formato YYYY-MM-DD")
    data_checkout: str = Field(description="Data de check-out no formato YYYY-MM-DD")
    hospedes: int = Field(1, ge=1, le=20, description="Número de hóspedes")


def buscar_hospedagem(backend: HospedagemBackend, args: BuscarHospedagemArgs) -> ToolResult:
    rows = backend.buscar(args.destino, args.data_checkin, args.data_checkout, args.hospedes)
    return ToolResult(payload=rows, ids=[r["id"] for r in rows], rows=rows)
