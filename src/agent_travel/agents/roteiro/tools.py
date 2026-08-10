from typing import Any

from pydantic import BaseModel, Field

from agent_travel.core.config import settings
from agent_travel.core.tool_registry import ToolResult

ROTEIRO_SYSTEM_PROMPT = (
    "Você monta roteiros de viagem dia a dia, objetivos e realistas. "
    "Responda em português, como uma lista numerada por dia, com 2 a 4 atividades por dia."
)


class MontarRoteiroArgs(BaseModel):
    """Monta um roteiro dia a dia para o destino, considerando duração e interesses do viajante."""

    destino: str = Field(description="Cidade ou região do roteiro")
    dias: int = Field(ge=1, le=60, description="Número de dias da viagem")
    interesses: list[str] = Field(
        default_factory=list,
        description="Interesses do viajante, ex: gastronomia, natureza, história",
    )


def montar_roteiro(client: Any, args: MontarRoteiroArgs) -> ToolResult:
    interesses_txt = ", ".join(args.interesses) if args.interesses else "variados"
    pergunta = (
        f"Monte um roteiro de {args.dias} dia(s) em {args.destino}, "
        f"para alguém interessado em: {interesses_txt}."
    )
    resp = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": ROTEIRO_SYSTEM_PROMPT},
            {"role": "user", "content": pergunta},
        ],
    )
    texto = resp.choices[0].message.content or ""
    return ToolResult(payload={"roteiro": texto})
