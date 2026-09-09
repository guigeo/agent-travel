import json
import re
from typing import Any

from pydantic import BaseModel, Field

from agent_travel.core.config import settings
from agent_travel.core.tool_registry import ToolResult

ROTEIRO_SYSTEM_PROMPT = (
    "Você monta roteiros de viagem dia a dia, objetivos e realistas. "
    "Responda somente JSON válido, sem markdown, no formato "
    '{"dias": [{"dia": 1, "atividades": ["atividade 1", "atividade 2"]}]}. '
    "Inclua exatamente um objeto por dia, com 2 a 4 atividades por dia."
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
        response_format={"type": "json_object"},
    )
    texto = resp.choices[0].message.content or ""
    dias = _parse_dias(texto, args.dias)
    row = {"id": "roteiro", "destino": args.destino, "dias": dias}
    return ToolResult(payload=row, ids=["roteiro"], rows=[row])


def _parse_dias(texto: str, dias_esperados: int) -> list[dict]:
    cleaned = texto.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        return [{"dia": 1, "atividades": [cleaned or "Roteiro indisponível."]}]

    raw_dias = data.get("dias") if isinstance(data, dict) else data
    parsed: list[dict] = []
    if isinstance(raw_dias, list):
        for index, item in enumerate(raw_dias, start=1):
            if not isinstance(item, dict):
                continue
            atividades = item.get("atividades") or []
            if isinstance(atividades, str):
                atividades = [atividades]
            atividades = [str(a).strip() for a in atividades if str(a).strip()]
            dia = item.get("dia", index)
            try:
                dia_num = int(dia)
            except (TypeError, ValueError):
                dia_num = index
            parsed.append({"dia": dia_num, "atividades": atividades or ["Atividades a confirmar."]})

    if parsed:
        return parsed[:dias_esperados]
    return [{"dia": 1, "atividades": [cleaned or "Roteiro indisponível."]}]
