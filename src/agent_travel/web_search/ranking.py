from urllib.parse import urlparse

from agent_travel.web_search.client import SearchHit

_EXCLUIDOS = (
    "wikipedia.org",
    "reddit.com",
    "quora.com",
    "youtube.com",
    "youtu.be",
    "facebook.com",
    "instagram.com",
    "tiktok.com",
    "twitter.com",
    "x.com",
    "pinterest.com",
    "linkedin.com",
    "medium.com",
)

_VOOS = (
    "kayak.com",
    "kayak.com.br",
    "skyscanner.com",
    "skyscanner.com.br",
    "decolar.com",
    "latamairlines.com",
    "latam.com",
    "voegol.com.br",
    "voeazul.com.br",
    "azul.com.br",
    "maxmilhas.com.br",
    "123milhas.com",
    "viajanet.com.br",
    "momondo.com",
    "expedia.com",
    "expedia.com.br",
)

_HOSPEDAGEM = (
    "booking.com",
    "booking.com.br",
    "airbnb.com",
    "airbnb.com.br",
    "hotels.com",
    "expedia.com",
    "expedia.com.br",
    "trivago.com",
    "trivago.com.br",
    "decolar.com",
)

_MILHAS = (
    "livelo.com.br",
    "itau.com.br",
    "latamairlines.com",
    "latam.com",
    "smiles.com.br",
    "tudoazul.com.br",
    "voeazul.com.br",
    "voegol.com.br",
)


def selecionar_fontes(hits: list[SearchHit], perfil: str, limite: int = 2) -> list[SearchHit]:
    """Prioriza agregadores e companhias; descarta fóruns e mídia genérica.

    Devolve no máximo `limite` hits, sem repetir o mesmo host. Se não houver
    fonte preferida, cai nos demais resultados não excluídos.
    """
    pontuados = [(hit, _pontuar(hit, perfil)) for hit in hits]
    preferidos = [hit for hit, score in pontuados if score >= 80]
    aceitaveis = [hit for hit, score in pontuados if 0 < score < 80]
    escolhidos = _deduplicar(preferidos) + _deduplicar(aceitaveis)
    if not escolhidos:
        escolhidos = _deduplicar([hit for hit, score in pontuados if score == 0] or hits)
    return escolhidos[:limite]


def com_papel(hits: list[SearchHit]) -> list[tuple[str, SearchHit]]:
    return [("principal" if index == 0 else "alternativa", hit) for index, hit in enumerate(hits)]


def _pontuar(hit: SearchHit, perfil: str) -> int:
    parsed = urlparse(hit.url)
    host = parsed.netloc.lower().removeprefix("www.")
    path = parsed.path.lower()
    if _host_em(host, _EXCLUIDOS):
        return 0
    if perfil == "voo":
        if _eh_google_travel(host, path, ("/flights", "/travel")):
            return 100
        if _host_em(host, _VOOS):
            return 90
    elif perfil == "hospedagem":
        if _eh_google_travel(host, path, ("/hotels", "/travel")):
            return 100
        if _host_em(host, _HOSPEDAGEM):
            return 90
    elif perfil == "milhas" and _host_em(host, _MILHAS):
        return 90
    return 15


def _eh_google_travel(host: str, path: str, trechos: tuple[str, ...]) -> bool:
    eh_google = (
        host in {"google.com", "google.com.br"}
        or host.startswith("google.")
        or host.endswith((".google.com", ".google.com.br"))
    )
    return eh_google and any(trecho in path for trecho in trechos)


def _host_em(host: str, sufixos: tuple[str, ...]) -> bool:
    return any(host == sufixo or host.endswith("." + sufixo) for sufixo in sufixos)


def _deduplicar(hits: list[SearchHit]) -> list[SearchHit]:
    vistos: set[str] = set()
    unicos: list[SearchHit] = []
    for hit in hits:
        host = urlparse(hit.url).netloc.lower().removeprefix("www.")
        chave = host or hit.url
        if chave in vistos:
            continue
        vistos.add(chave)
        unicos.append(hit)
    return unicos
