from conftest import FakeClient, texto, tool_call
from fastapi.testclient import TestClient

from agent_travel.api.main import app
from agent_travel.core.llm_client import get_client


def test_happy_path_planeja_viagem_sem_mencionar_milhas(monkeypatch):
    monkeypatch.setattr(
        "agent_travel.orchestrator.registry._voos_backend.buscar",
        lambda origem, destino, data_ida, data_volta=None: [
            {"id": "voo-1", "resumo": f"{origem}-{destino}"}
        ],
    )
    monkeypatch.setattr(
        "agent_travel.orchestrator.registry._hospedagem_backend.buscar",
        lambda destino, data_checkin, data_checkout, hospedes=1: [
            {"id": "hosp-1", "resumo": f"Hotel em {destino}"}
        ],
    )
    fake_client = FakeClient(
        [
            tool_call(
                "buscar_voos",
                {"origem": "GRU", "destino": "GIG", "data_ida": "2026-09-10"},
            ),
            tool_call(
                "buscar_hospedagem",
                {
                    "destino": "GIG",
                    "data_checkin": "2026-09-10",
                    "data_checkout": "2026-09-12",
                },
            ),
            tool_call(
                "calcular_orcamento",
                {
                    "itens": [{"descricao": "voo", "valor": 800}],
                    "orcamento_maximo": 2000,
                },
            ),
            texto("Aqui está seu plano de viagem, com orçamento dentro do previsto."),
        ]
    )
    monkeypatch.setattr("agent_travel.orchestrator.registry.get_client", lambda: fake_client)
    app.dependency_overrides[get_client] = lambda: fake_client

    try:
        client = TestClient(app)
        response = client.post("/chat/sessao-teste", json={"mensagem": "planeje minha viagem"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert "milhas" not in body["texto"].lower()
    # cada tool chamada no turno vira seu próprio resultado — nenhuma é descartada
    resultados_por_ferramenta = {r["ferramenta"]: r["dados"] for r in body["resultados"]}
    assert resultados_por_ferramenta["buscar_voos"] == [{"id": "voo-1", "resumo": "GRU-GIG"}]
    assert resultados_por_ferramenta["buscar_hospedagem"] == [
        {"id": "hosp-1", "resumo": "Hotel em GIG"}
    ]
    assert resultados_por_ferramenta["calcular_orcamento"][0]["total_estimado"] == 800


def test_limite_de_escopo_nao_finaliza_compra(monkeypatch):
    fake_client = FakeClient(
        [texto("Recomendo essa opção, mas a compra deve ser feita por você no site oficial.")]
    )
    monkeypatch.setattr("agent_travel.orchestrator.registry.get_client", lambda: fake_client)
    app.dependency_overrides[get_client] = lambda: fake_client

    try:
        client = TestClient(app)
        response = client.post("/chat/sessao-teste-2", json={"mensagem": "compre a passagem agora"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert "site oficial" in response.json()["texto"].lower()


def test_payload_invalido_retorna_problem_details():
    app.dependency_overrides[get_client] = lambda: FakeClient([])

    try:
        client = TestClient(app)
        response = client.post("/chat/sessao-teste-3", json={})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422
    assert response.headers["content-type"] == "application/problem+json"
    assert response.json()["type"].endswith("/validation-error")
