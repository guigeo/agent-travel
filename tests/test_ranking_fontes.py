from agent_travel.web_search.client import SearchHit
from agent_travel.web_search.ranking import selecionar_fontes


def test_prioriza_agregador_e_descarta_forum():
    hits = [
        SearchHit("Fórum", "https://www.reddit.com/r/viagem", "passagem barata"),
        SearchHit("Kayak", "https://www.kayak.com.br/flights/GRU-GIG", "R$ 800"),
        SearchHit("YouTube", "https://www.youtube.com/watch?v=abc", "vídeo de passagens"),
    ]

    escolhidos = selecionar_fontes(hits, "voo", limite=2)

    assert [hit.url for hit in escolhidos] == ["https://www.kayak.com.br/flights/GRU-GIG"]


def test_limita_a_duas_fontes_sem_repetir_host():
    hits = [
        SearchHit("Kayak 1", "https://www.kayak.com.br/a", "800"),
        SearchHit("Kayak 2", "https://www.kayak.com.br/b", "900"),
        SearchHit("Decolar", "https://www.decolar.com/passagens", "850"),
        SearchHit("Blog", "https://blog.exemplo.com/voo", "dicas"),
    ]

    escolhidos = selecionar_fontes(hits, "voo", limite=2)

    assert len(escolhidos) == 2
    assert "kayak.com.br" in escolhidos[0].url
    assert "decolar.com" in escolhidos[1].url


def test_google_flights_conta_como_fonte_preferida():
    hits = [
        SearchHit("Blog", "https://blog.exemplo.com/voo", "dicas"),
        SearchHit("Google Flights", "https://www.google.com/travel/flights", "GRU GIG"),
    ]

    escolhidos = selecionar_fontes(hits, "voo", limite=1)

    assert "google.com/travel/flights" in escolhidos[0].url
