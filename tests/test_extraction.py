from conftest import FakeClient, texto

from agent_travel.web_search.extraction import ExtracaoVoo, ancora_percentual, ancora_preco, extrair


def test_ancora_preco_so_mantem_numero_presente_no_texto():
    assert ancora_preco(800, "a partir de R$ 800 ida") == 800
    assert ancora_preco(9999, "a partir de R$ 800 ida") is None
    assert ancora_preco(None, "R$ 800") is None


def test_ancora_percentual_exige_numero_no_texto():
    assert ancora_percentual(120, "bônus de 120% Livelo") == 120
    assert ancora_percentual(80, "promoção relâmpago sem número") is None


def test_extrair_preenche_campos_do_json():
    client = FakeClient(
        [
            texto(
                '{"companhia": "LATAM", "preco": 800, "moeda": "BRL", '
                '"horario": null, "confianca": "alta"}'
            )
        ]
    )

    extra = extrair(client, ExtracaoVoo, "LATAM GRU-GIG", "a partir de R$ 800", "voo")

    assert extra.companhia == "LATAM"
    assert extra.preco == 800
    assert extra.confianca == "alta"


def test_extrair_json_invalido_vira_objeto_vazio():
    client = FakeClient([texto("não é json")])

    extra = extrair(client, ExtracaoVoo, "título", "trecho", "voo")

    assert extra.preco is None
    assert extra.confianca == "baixa"
