from functools import partial

from agent_travel.core.tool_registry import ToolRegistry
from agent_travel.milhas.backend import MilhasBackend
from agent_travel.milhas.tools import (
    BuscarBonusArgs,
    CalcularValorPontoArgs,
    buscar_bonus_vigente,
    calcular_valor_ponto,
)
from agent_travel.web_search.client import WebSearchClient

_search_client = WebSearchClient()
_milhas_backend = MilhasBackend(_search_client)

MILES_TOOL_REGISTRY = ToolRegistry(
    {
        "buscar_bonus_vigente": (BuscarBonusArgs, partial(buscar_bonus_vigente, _milhas_backend)),
        "calcular_valor_ponto": (CalcularValorPontoArgs, calcular_valor_ponto),
    }
)
