from collections.abc import Callable
from typing import Any

from agent_travel.agents.links import link_busca_hospedagem
from agent_travel.web_search.client import WebSearchClient
from agent_travel.web_search.extraction import ExtracaoHospedagem, ancora_preco, extrair
from agent_travel.web_search.ranking import com_papel, selecionar_fontes


class HospedagemBackend:
    """Busca fontes de hospedagem, prioriza reservas conhecidas e extrai o que o trecho diz."""

    def __init__(
        self,
        search_client: WebSearchClient,
        llm_factory: Callable[[], Any] | None = None,
    ):
        self._search = search_client
        self._llm_factory = llm_factory

    def buscar(
        self, destino: str, data_checkin: str, data_checkout: str, hospedes: int = 1
    ) -> list[dict]:
        query = (
            f"hotel em {destino} check-in {data_checkin} check-out {data_checkout} "
            f"{hospedes} hóspedes preço"
        )
        hits = self._search.search(query, max_results=8)
        if not hits:
            raise ValueError(f"Nenhum resultado encontrado para hospedagem em {destino}.")
        escolhidos = selecionar_fontes(hits, "hospedagem", limite=2)
        client = self._llm_factory() if self._llm_factory else None
        rows: list[dict] = []
        for index, (papel, hit) in enumerate(com_papel(escolhidos), start=1):
            row = {
                "id": f"hospedagem-{index}",
                "papel": papel,
                "destino": destino,
                "data_checkin": data_checkin,
                "data_checkout": data_checkout,
                "hospedes": hospedes,
                "resumo": hit.title,
                "trecho": hit.snippet,
                "fonte_url": hit.url,
                "continuar_busca_url": link_busca_hospedagem(
                    destino, data_checkin, data_checkout, hospedes
                ),
                "nome": None,
                "bairro": None,
                "preco": None,
                "moeda": None,
                "confianca": "baixa",
            }
            if client is not None:
                extra = extrair(
                    client,
                    ExtracaoHospedagem,
                    hit.title,
                    hit.snippet,
                    f"hospedagem em {destino}",
                )
                texto_fonte = f"{hit.title} {hit.snippet}"
                row.update(
                    {
                        "nome": extra.nome,
                        "bairro": extra.bairro,
                        "preco": ancora_preco(extra.preco, texto_fonte),
                        "moeda": extra.moeda or "BRL",
                        "confianca": extra.confianca,
                    }
                )
                if row["preco"] is None and extra.confianca == "alta":
                    row["confianca"] = "media"
            rows.append(row)
        return rows
