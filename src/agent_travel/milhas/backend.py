from collections.abc import Callable
from typing import Any

from agent_travel.web_search.client import WebSearchClient
from agent_travel.web_search.extraction import ExtracaoBonus, ancora_percentual, extrair
from agent_travel.web_search.ranking import com_papel, selecionar_fontes


class MilhasBackend:
    """Busca promoções de bônus de transferência de pontos via WebSearchClient
    (sem integração com contas Itaú/Livelo — apenas busca pública)."""

    def __init__(
        self,
        search_client: WebSearchClient,
        llm_factory: Callable[[], Any] | None = None,
    ):
        self._search = search_client
        self._llm_factory = llm_factory

    def buscar_bonus_vigente(self, programa_destino: str | None = None) -> list[dict]:
        query = "bônus de transferência de pontos Itaú Livelo Iupp para milhas promoção vigente"
        if programa_destino:
            query += f" {programa_destino}"
        hits = self._search.search(query, max_results=8)
        if not hits:
            raise ValueError("Nenhuma promoção de bônus de transferência encontrada no momento.")
        escolhidos = selecionar_fontes(hits, "milhas", limite=2)
        client = self._llm_factory() if self._llm_factory else None
        rows: list[dict] = []
        for index, (papel, hit) in enumerate(com_papel(escolhidos), start=1):
            row = {
                "id": f"bonus-{index}",
                "papel": papel,
                "programa_destino": programa_destino,
                "resumo": hit.title,
                "trecho": hit.snippet,
                "fonte_url": hit.url,
                "programa": None,
                "percentual": None,
                "vigencia": None,
                "confianca": "baixa",
            }
            if client is not None:
                extra = extrair(
                    client,
                    ExtracaoBonus,
                    hit.title,
                    hit.snippet,
                    "bônus de transferência de pontos Itaú/Livelo",
                )
                texto_fonte = f"{hit.title} {hit.snippet}"
                row.update(
                    {
                        "programa": extra.programa or programa_destino,
                        "percentual": ancora_percentual(extra.percentual, texto_fonte),
                        "vigencia": extra.vigencia,
                        "confianca": extra.confianca,
                    }
                )
                if row["percentual"] is None and extra.confianca == "alta":
                    row["confianca"] = "media"
            rows.append(row)
        return rows
