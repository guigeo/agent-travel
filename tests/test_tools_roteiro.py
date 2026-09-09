from types import SimpleNamespace

from agent_travel.agents.roteiro.tools import MontarRoteiroArgs, montar_roteiro


class FakeRoteiroClient:
    def __init__(self, content: str) -> None:
        self.chat = SimpleNamespace(
            completions=SimpleNamespace(create=self._create),
        )
        self.content = content

    def _create(self, **_kwargs):
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=self.content))]
        )


def test_montar_roteiro_estrutura_dias_a_partir_de_json():
    client = FakeRoteiroClient(
        '{"dias": [{"dia": 1, "atividades": ["Miradouro", "Alfama"]}, '
        '{"dia": 2, "atividades": ["Belém"]}]}'
    )
    args = MontarRoteiroArgs(destino="Lisboa", dias=2, interesses=["história"])

    result = montar_roteiro(client, args)

    assert result.ids == ["roteiro"]
    assert result.rows[0]["destino"] == "Lisboa"
    assert result.rows[0]["dias"] == [
        {"dia": 1, "atividades": ["Miradouro", "Alfama"]},
        {"dia": 2, "atividades": ["Belém"]},
    ]


def test_montar_roteiro_texto_livre_vira_um_dia():
    client = FakeRoteiroClient("Dia 1: caminhar pelo centro.")
    args = MontarRoteiroArgs(destino="Porto", dias=1)

    result = montar_roteiro(client, args)

    assert result.rows[0]["dias"] == [{"dia": 1, "atividades": ["Dia 1: caminhar pelo centro."]}]
