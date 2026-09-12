from agent_travel.agents.links import link_busca_hospedagem, link_busca_voo


def test_link_de_voo_preserva_rota_e_datas():
    link = link_busca_voo("GRU", "LIS", "2026-10-10", "2026-10-20")

    assert link.startswith("https://www.google.com/travel/flights")
    assert "GRU.LIS.2026-10-10*LIS.GRU.2026-10-20" in link


def test_link_de_hospedagem_preserva_criterios_da_busca():
    link = link_busca_hospedagem("Lisboa", "2026-10-10", "2026-10-15", 2)

    assert link.startswith("https://www.booking.com/searchresults.html?")
    assert "ss=Lisboa" in link
    assert "checkin=2026-10-10" in link
    assert "checkout=2026-10-15" in link
    assert "group_adults=2" in link
