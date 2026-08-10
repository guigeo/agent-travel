from dataclasses import dataclass

from ddgs import DDGS


@dataclass
class SearchHit:
    title: str
    url: str
    snippet: str


class WebSearchClient:
    """Wrapper fino sobre busca web — sem API key, usado pelos backends de
    voos, hospedagem e milhas para obter dados atuais sem custo no MVP."""

    def search(self, query: str, max_results: int = 5) -> list[SearchHit]:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=max_results)
        return [
            SearchHit(title=r.get("title", ""), url=r.get("href", ""), snippet=r.get("body", ""))
            for r in results
        ]
