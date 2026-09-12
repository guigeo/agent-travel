from collections.abc import Callable
from typing import Any

from agent_travel.agents.links import link_busca_voo
from agent_travel.web_search.client import WebSearchClient
from agent_travel.web_search.extraction import ExtracaoVoo, ancora_preco, extrair
from agent_travel.web_search.ranking import com_papel, selecionar_fontes


class VoosBackend:
    """Busca fontes de voos, prioriza agregadores/companhias e extrai o que o trecho diz."""

    def __init__(
        self,
        search_client: WebSearchClient,
        llm_factory: Callable[[], Any] | None = None,
    ):
        self._search = search_client
        self._llm_factory = llm_factory

    def buscar(
        self, origem: str, destino: str, data_ida: str, data_volta: str | None = None
    ) -> list[dict]:
        query = f"passagem aérea {origem} para {destino} {data_ida} preço"
        if data_volta:
            query += f" volta {data_volta}"
        hits = self._search.search(query, max_results=8)
        if not hits:
            raise ValueError(
                f"Nenhum resultado encontrado para voos de {origem} a {destino} em {data_ida}."
            )
        escolhidos = selecionar_fontes(hits, "voo", limite=2)
        client = self._llm_factory() if self._llm_factory else None
        rows: list[dict] = []
        for index, (papel, hit) in enumerate(com_papel(escolhidos), start=1):
            row = {
                "id": f"voo-{index}",
                "papel": papel,
                "origem": origem,
                "destino": destino,
                "data_ida": data_ida,
                "data_volta": data_volta,
                "resumo": hit.title,
                "trecho": hit.snippet,
                "fonte_url": hit.url,
                "continuar_busca_url": link_busca_voo(origem, destino, data_ida, data_volta),
                "companhia": None,
                "preco": None,
                "moeda": None,
                "horario": None,
                "confianca": "baixa",
            }
            if client is not None:
                extra = extrair(
                    client,
                    ExtracaoVoo,
                    hit.title,
                    hit.snippet,
                    f"voo de {origem} para {destino}",
                )
                texto_fonte = f"{hit.title} {hit.snippet}"
                row.update(
                    {
                        "companhia": extra.companhia,
                        "preco": ancora_preco(extra.preco, texto_fonte),
                        "moeda": extra.moeda or "BRL",
                        "horario": extra.horario,
                        "confianca": extra.confianca,
                    }
                )
                if row["preco"] is None and extra.confianca == "alta":
                    row["confianca"] = "media"
            rows.append(row)
        return rows
