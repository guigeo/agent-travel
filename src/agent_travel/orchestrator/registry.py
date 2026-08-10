from functools import partial

from agent_travel.agents.hospedagem.backend import HospedagemBackend
from agent_travel.agents.hospedagem.tools import BuscarHospedagemArgs, buscar_hospedagem
from agent_travel.agents.orcamento.tools import CalcularOrcamentoArgs, calcular_orcamento
from agent_travel.agents.roteiro.tools import MontarRoteiroArgs, montar_roteiro
from agent_travel.agents.voos.backend import VoosBackend
from agent_travel.agents.voos.tools import BuscarVoosArgs, buscar_voos
from agent_travel.core.llm_client import get_client
from agent_travel.core.tool_registry import ToolRegistry
from agent_travel.web_search.client import WebSearchClient

_search_client = WebSearchClient()
_voos_backend = VoosBackend(_search_client)
_hospedagem_backend = HospedagemBackend(_search_client)


def _montar_roteiro(args: MontarRoteiroArgs):
    return montar_roteiro(get_client(), args)


PLANNER_TOOL_REGISTRY = ToolRegistry(
    {
        "buscar_voos": (BuscarVoosArgs, partial(buscar_voos, _voos_backend)),
        "buscar_hospedagem": (
            BuscarHospedagemArgs,
            partial(buscar_hospedagem, _hospedagem_backend),
        ),
        "montar_roteiro": (MontarRoteiroArgs, _montar_roteiro),
        "calcular_orcamento": (CalcularOrcamentoArgs, calcular_orcamento),
    }
)
