from agent_travel.web_search.client import WebSearchClient


class MilhasBackend:
    """Busca promoções de bônus de transferência de pontos via WebSearchClient
    (sem integração com contas Itaú/Livelo — apenas busca pública)."""

    def __init__(self, search_client: WebSearchClient):
        self._search = search_client

    def buscar_bonus_vigente(self, programa_destino: str | None = None) -> list[dict]:
        query = "bônus de transferência de pontos Itaú Livelo Iupp para milhas promoção vigente"
        if programa_destino:
            query += f" {programa_destino}"
        hits = self._search.search(query, max_results=5)
        if not hits:
            raise ValueError("Nenhuma promoção de bônus de transferência encontrada no momento.")
        return [
            {
                "id": f"bonus-{i}",
                "programa_destino": programa_destino,
                "resumo": hit.title,
                "trecho": hit.snippet,
                "fonte_url": hit.url,
            }
            for i, hit in enumerate(hits, start=1)
        ]
