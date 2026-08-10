import ast
from pathlib import Path

import pytest

MILHAS_DIR = Path(__file__).resolve().parents[1] / "src" / "agent_travel" / "milhas"


def _imported_modules(py_file: Path) -> set[str]:
    tree = ast.parse(py_file.read_text())
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


@pytest.mark.parametrize("py_file", sorted(MILHAS_DIR.glob("*.py")), ids=lambda p: p.name)
def test_milhas_nao_importa_orchestrator(py_file: Path):
    modules = _imported_modules(py_file)
    acopladas = {m for m in modules if m.startswith("agent_travel.orchestrator")}
    assert not acopladas, f"{py_file.name} importa {acopladas} — quebra o desacoplamento"


def test_calcula_valor_ponto_sem_qualquer_contexto_de_viagem():
    from agent_travel.milhas.tools import CalcularValorPontoArgs, calcular_valor_ponto

    args = CalcularValorPontoArgs(
        pontos_disponiveis=10_000, bonus_percentual=100, valor_milheiro_estimado=25.0
    )

    result = calcular_valor_ponto(args)

    assert result.payload["milhas_resultantes"] == 20_000.0
    assert result.payload["valor_estimado_reais"] == 500.0
    assert not result.error


def test_busca_bonus_vigente_sem_programa_destino_especifico():
    from agent_travel.milhas.backend import MilhasBackend
    from agent_travel.web_search.client import SearchHit

    class FakeSearch:
        def search(self, query: str, max_results: int = 5) -> list[SearchHit]:
            return [SearchHit(title="Bônus 120%", url="https://exemplo.com", snippet="...")]

    backend = MilhasBackend(FakeSearch())

    rows = backend.buscar_bonus_vigente()

    assert rows[0]["id"] == "bonus-1"
    assert rows[0]["fonte_url"] == "https://exemplo.com"
