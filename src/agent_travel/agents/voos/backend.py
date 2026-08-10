from agent_travel.web_search.client import WebSearchClient


class VoosBackend:
    """Busca e normaliza opções de voos via WebSearchClient (sem API paga no MVP)."""

    def __init__(self, search_client: WebSearchClient):
        self._search = search_client

    def buscar(
        self, origem: str, destino: str, data_ida: str, data_volta: str | None = None
    ) -> list[dict]:
        query = f"passagem aérea {origem} para {destino} {data_ida} preço"
        if data_volta:
            query += f" volta {data_volta}"
        hits = self._search.search(query, max_results=5)
        if not hits:
            raise ValueError(
                f"Nenhum resultado encontrado para voos de {origem} a {destino} em {data_ida}."
            )
        return [
            {
                "id": f"voo-{i}",
                "origem": origem,
                "destino": destino,
                "data_ida": data_ida,
                "data_volta": data_volta,
                "resumo": hit.title,
                "trecho": hit.snippet,
                "fonte_url": hit.url,
            }
            for i, hit in enumerate(hits, start=1)
        ]
