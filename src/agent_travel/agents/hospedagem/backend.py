from agent_travel.web_search.client import WebSearchClient


class HospedagemBackend:
    """Busca e normaliza opções de hospedagem via WebSearchClient (sem API paga no MVP)."""

    def __init__(self, search_client: WebSearchClient):
        self._search = search_client

    def buscar(
        self, destino: str, data_checkin: str, data_checkout: str, hospedes: int = 1
    ) -> list[dict]:
        query = (
            f"hotel em {destino} check-in {data_checkin} check-out {data_checkout} "
            f"{hospedes} hóspedes preço"
        )
        hits = self._search.search(query, max_results=5)
        if not hits:
            raise ValueError(f"Nenhum resultado encontrado para hospedagem em {destino}.")
        return [
            {
                "id": f"hospedagem-{i}",
                "destino": destino,
                "data_checkin": data_checkin,
                "data_checkout": data_checkout,
                "hospedes": hospedes,
                "resumo": hit.title,
                "trecho": hit.snippet,
                "fonte_url": hit.url,
            }
            for i, hit in enumerate(hits, start=1)
        ]
