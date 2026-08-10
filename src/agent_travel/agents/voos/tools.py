from pydantic import BaseModel, Field

from agent_travel.agents.voos.backend import VoosBackend
from agent_travel.core.tool_registry import ToolResult


class BuscarVoosArgs(BaseModel):
    """Busca voos entre origem e destino em datas específicas (ida e volta opcional)."""

    origem: str = Field(description="Cidade ou aeroporto de origem")
    destino: str = Field(description="Cidade ou aeroporto de destino")
    data_ida: str = Field(description="Data de ida no formato YYYY-MM-DD")
    data_volta: str | None = Field(None, description="Data de volta, se a viagem for ida e volta")


def buscar_voos(backend: VoosBackend, args: BuscarVoosArgs) -> ToolResult:
    rows = backend.buscar(args.origem, args.destino, args.data_ida, args.data_volta)
    return ToolResult(payload=rows, ids=[r["id"] for r in rows], rows=rows)
