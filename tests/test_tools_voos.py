import pytest
from pydantic import ValidationError

from agent_travel.agents.voos.tools import BuscarVoosArgs, buscar_voos


class FakeVoosBackend:
    def __init__(self, rows=None, raise_error=False):
        self._rows = rows or []
        self._raise = raise_error

    def buscar(self, origem, destino, data_ida, data_volta=None):
        if self._raise:
            raise ValueError("Nenhum resultado encontrado")
        return self._rows


def test_buscar_voos_retorna_grounding_com_ids():
    rows = [{"id": "voo-1", "resumo": "GRU-GIG"}]
    backend = FakeVoosBackend(rows=rows)
    args = BuscarVoosArgs(origem="GRU", destino="GIG", data_ida="2026-09-10")

    result = buscar_voos(backend, args)

    assert result.ids == ["voo-1"]
    assert result.rows == rows
    assert not result.error


def test_buscar_voos_sem_resultado_propaga_erro_de_dominio():
    backend = FakeVoosBackend(raise_error=True)
    args = BuscarVoosArgs(origem="GRU", destino="XXX", data_ida="2026-09-10")

    with pytest.raises(ValueError):
        buscar_voos(backend, args)


def test_args_invalidos_sem_origem_levanta_validation_error():
    with pytest.raises(ValidationError):
        BuscarVoosArgs(destino="GIG", data_ida="2026-09-10")
