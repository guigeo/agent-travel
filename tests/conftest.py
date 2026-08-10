import json
from types import SimpleNamespace

import pytest

from agent_travel.core.session import Session


def texto(content: str) -> SimpleNamespace:
    return SimpleNamespace(content=content, tool_calls=None)


def tool_call(name: str, args: dict, call_id: str = "call_1") -> SimpleNamespace:
    return SimpleNamespace(
        content=None,
        tool_calls=[
            SimpleNamespace(
                id=call_id, function=SimpleNamespace(name=name, arguments=json.dumps(args))
            )
        ],
    )


class FakeClient:
    """Devolve mensagens roteirizadas em sequência e grava cada request recebido.

    Ver KB agentes-llm/patterns/avaliacao-offline-fake-client.md
    """

    def __init__(self, script: list[SimpleNamespace]) -> None:
        self.script = list(script)
        self.requests: list[dict] = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.requests.append(kwargs)
        return SimpleNamespace(choices=[SimpleNamespace(message=self.script.pop(0))], usage=None)


@pytest.fixture
def nova_sessao() -> Session:
    return Session()
