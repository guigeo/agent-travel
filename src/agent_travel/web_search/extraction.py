import json
import re
from typing import Any, Literal, TypeVar

from openai import OpenAIError
from pydantic import BaseModel, Field, ValidationError

from agent_travel.core.config import settings

EXTRACT_SYSTEM_PROMPT = (
    "Você extrai somente fatos explícitos do título e do trecho de uma busca na web. "
    "Se um campo não aparecer com clareza, use null. Nunca invente preço, percentual, "
    "companhia, hotel ou programa. Responda somente JSON válido, sem markdown."
)


class ExtracaoVoo(BaseModel):
    companhia: str | None = None
    preco: float | None = Field(None, ge=0)
    moeda: str | None = None
    horario: str | None = None
    confianca: Literal["alta", "media", "baixa"] = "baixa"


class ExtracaoHospedagem(BaseModel):
    nome: str | None = None
    bairro: str | None = None
    preco: float | None = Field(None, ge=0)
    moeda: str | None = None
    confianca: Literal["alta", "media", "baixa"] = "baixa"


class ExtracaoBonus(BaseModel):
    programa: str | None = None
    percentual: float | None = Field(None, ge=0)
    vigencia: str | None = None
    confianca: Literal["alta", "media", "baixa"] = "baixa"


TModel = TypeVar("TModel", bound=BaseModel)


def extrair(client: Any, model: type[TModel], titulo: str, trecho: str, contexto: str) -> TModel:
    """Extrai campos do título/trecho. Falha de parse vira objeto vazio com confiança baixa."""
    pergunta = (
        f"Contexto: {contexto}\nTítulo: {titulo}\nTrecho: {trecho}\n"
        f"Schema: {json.dumps(model.model_json_schema(), ensure_ascii=False)}"
    )
    try:
        resp = client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": EXTRACT_SYSTEM_PROMPT},
                {"role": "user", "content": pergunta},
            ],
            response_format={"type": "json_object"},
        )
        texto = resp.choices[0].message.content or ""
    except (OpenAIError, AttributeError, IndexError, TypeError, KeyError):
        return model()
    try:
        return model.model_validate(json.loads(_limpar_json(texto)))
    except (json.JSONDecodeError, ValidationError, TypeError, ValueError):
        return model()


def ancora_preco(valor: float | None, texto: str) -> float | None:
    """Só mantém o preço se o número aparecer no texto da fonte."""
    if valor is None or valor <= 0:
        return None
    compacto = re.sub(r"\D", "", texto)
    alvo = str(round(valor))
    if len(alvo) >= 3 and alvo in compacto:
        return valor
    if len(alvo) >= 2 and re.search(r"r\$|reais", texto, flags=re.IGNORECASE) and alvo in compacto:
        return valor
    return None


def ancora_percentual(valor: float | None, texto: str) -> float | None:
    if valor is None or valor < 0:
        return None
    alvo = str(round(valor))
    compacto = texto.replace(" ", "")
    if alvo in compacto or f"{alvo}%" in compacto:
        return valor
    return None


def _limpar_json(texto: str) -> str:
    cleaned = texto.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned
