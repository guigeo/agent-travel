import json
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, ValidationError

Handler = Callable[[BaseModel], "ToolResult"]


@dataclass
class ToolResult:
    payload: Any
    error: bool = False
    ids: list[str] = field(default_factory=list)
    rows: list[dict] = field(default_factory=list)

    @property
    def payload_json(self) -> str:
        return json.dumps(self.payload, ensure_ascii=False, default=str)


class ToolRegistry:
    """Registry de tools tipadas: 1 model Pydantic + 1 handler por tool.

    Cada instância é isolada — orquestrador e agente de milhas montam a sua
    própria, sem nenhum estado ou import cruzado entre eles.
    """

    def __init__(self, tools: dict[str, tuple[type[BaseModel], Handler]]):
        self._tools = tools

    def openai_tools(self) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": " ".join((model.__doc__ or "").split()),
                    "parameters": model.model_json_schema(),
                },
            }
            for name, (model, _) in self._tools.items()
        ]

    def execute_tool(self, name: str, raw_args: str) -> ToolResult:
        entry = self._tools.get(name)
        if entry is None:
            return ToolResult(
                payload={"erro": f"tool desconhecida: {name}", "validas": list(self._tools)},
                error=True,
            )
        model, handler = entry
        try:
            args = model.model_validate_json(raw_args or "{}")
        except ValidationError as exc:
            return ToolResult(
                payload={"erro": "argumentos inválidos", "detalhe": str(exc)}, error=True
            )
        try:
            return handler(args)
        except ValueError as exc:
            return ToolResult(payload={"erro": str(exc)}, error=True)
