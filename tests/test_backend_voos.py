from conftest import FakeClient, texto

from agent_travel.agents.voos.backend import VoosBackend
from agent_travel.web_search.client import SearchHit


class FakeSearch:
    def __init__(self, hits: list[SearchHit]):
        self._hits = hits

    def search(self, query: str, max_results: int = 5) -> list[SearchHit]:
        return list(self._hits)


def test_backend_de_voos_prioriza_fonte_e_marca_papel():
    search = FakeSearch(
        [
            SearchHit("Fórum", "https://www.reddit.com/r/viagem", "passagem"),
            SearchHit("Kayak GRU-GIG", "https://www.kayak.com.br/flights", "R$ 800"),
            SearchHit("Blog", "https://blog.exemplo.com/voo", "dicas de viagem"),
        ]
    )
    backend = VoosBackend(search)

    rows = backend.buscar("GRU", "GIG", "2026-09-10")

    assert len(rows) == 2
    assert rows[0]["papel"] == "principal"
    assert rows[1]["papel"] == "alternativa"
    assert "kayak.com.br" in rows[0]["fonte_url"]
    assert all("reddit" not in row["fonte_url"] for row in rows)


def test_backend_ancora_preco_extraido_no_trecho():
    search = FakeSearch(
        [SearchHit("Kayak GRU-GIG", "https://www.kayak.com.br/flights", "a partir de R$ 800")]
    )
    client = FakeClient(
        [
            texto(
                '{"companhia": "LATAM", "preco": 800, "moeda": "BRL", '
                '"horario": null, "confianca": "alta"}'
            )
        ]
    )
    backend = VoosBackend(search, lambda: client)

    rows = backend.buscar("GRU", "GIG", "2026-09-10")

    assert rows[0]["preco"] == 800
    assert rows[0]["companhia"] == "LATAM"


def test_backend_descarta_preco_que_nao_esta_no_trecho():
    search = FakeSearch(
        [SearchHit("Kayak GRU-GIG", "https://www.kayak.com.br/flights", "consulte valores no site")]
    )
    client = FakeClient(
        [
            texto(
                '{"companhia": null, "preco": 9999, "moeda": "BRL", '
                '"horario": null, "confianca": "alta"}'
            )
        ]
    )
    backend = VoosBackend(search, lambda: client)

    rows = backend.buscar("GRU", "GIG", "2026-09-10")

    assert rows[0]["preco"] is None
    assert rows[0]["confianca"] == "media"
