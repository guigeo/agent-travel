from urllib.parse import urlencode


def link_busca_voo(origem: str, destino: str, data_ida: str, data_volta: str | None = None) -> str:
    """Monta um link de pesquisa no Google Flights, sem alegar uma oferta específica."""
    trecho_ida = f"{origem}.{destino}.{data_ida}"
    trechos = [trecho_ida]
    if data_volta:
        trechos.append(f"{destino}.{origem}.{data_volta}")
    return (
        f"https://www.google.com/travel/flights?hl=pt-BR#flt={'*'.join(trechos)};c:BRL;e:1;sd:1;t:f"
    )


def link_busca_hospedagem(
    destino: str, data_checkin: str, data_checkout: str, hospedes: int
) -> str:
    """Monta uma busca no Booking.com com destino, datas e número de hóspedes."""
    params = urlencode(
        {
            "ss": destino,
            "checkin": data_checkin,
            "checkout": data_checkout,
            "group_adults": hospedes,
            "no_rooms": 1,
        }
    )
    return f"https://www.booking.com/searchresults.html?{params}"
