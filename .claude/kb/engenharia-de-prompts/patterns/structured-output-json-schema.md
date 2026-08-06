<!-- Prosa em português; código, nomes de API e keywords técnicas em inglês. Convenção: .claude/kb/_index.yaml -->
# Structured output com JSON Schema (não "peça JSON" no prompt)

> **Propósito**: Garantir que a saída do modelo bate com um schema, não só que é JSON válido — usar o mecanismo nativo do provider em vez de confiar em instrução textual.
> **Validado**: 2026-08-06 (OpenAI "Structured model outputs" guide; comparativo cross-provider OpenAI/Anthropic/Gemini, 2026)

## Quando usar

- A saída alimenta código downstream que espera campos por nome (parsing, DB insert,
  próxima tool call).
- Extração de dados estruturados (entidades, formulários) a partir de texto livre.
- Schema fixo definido em build-time — para saída genuinamente variável, JSON mode
  simples (sem schema) é suficiente e mais barato.

## Implementação

```python
from pydantic import BaseModel
from openai import OpenAI

class TicketClassification(BaseModel):
    categoria: str          # todo campo é obrigatório em strict mode
    prioridade: str          # sem tipos opcionais — usar union com null se precisar
    resumo: str

client = OpenAI()
response = client.chat.completions.parse(          # helper .parse() deriva o schema do model
    model="gpt-5.4-mini",
    messages=[
        {"role": "system", "content": "Classifique o ticket de suporte."},
        {"role": "user", "content": texto_do_ticket},
    ],
    response_format=TicketClassification,
)
resultado = response.choices[0].message
if resultado.refusal:                    # 1º: sempre checar refusal antes de .parsed
    raise ValueError(resultado.refusal)
ticket: TicketClassification = resultado.parsed
```

```text
# Anthropic (Claude): mesmo princípio, gotcha diferente —
# minimum/maximum/minLength/maxLength são REMOVIDOS do schema e viram texto
# na description; o decoder não os aplica na geração (só valida depois e re-tenta).
# Workaround: expressar limite numérico como enum quando ele precisa ser
# garantido NA geração (ex.: "enum": [1,2,3,4,5] em vez de minimum/maximum).
```

## Configuração

| Decisão | Padrão recomendado | Descrição |
|---|---|---|
| Todo campo obrigatório | `required` = todas as chaves | Strict mode não aceita campo opcional; usar `tipo \| null` |
| `additionalProperties` | `false` | Obrigatório em strict mode — impede o modelo inventar chave |
| Objeto raiz | `type: object` (nunca array/anyOf no topo) | Limitação da API — envolver array em `{"items": [...]}` |
| Validação pós-parse | Pydantic validators / Zod refinements | Schema expressa tipo, não regra semântica ("data_fim > data_início") |
| Refusal | checar antes de acessar `.parsed` | Recusa de segurança não segue o schema — vem em campo separado |

## Exemplo de uso

```python
# Diferença crítica vs JSON mode: JSON mode garante JSON válido, NÃO garante
# que "categoria" existe ou que "prioridade" é uma das strings esperadas.
# Structured output (strict) garante as duas coisas por constrained decoding —
# o modelo fisicamente não consegue emitir um token fora do schema.
```

## Ver também

- [anatomia-do-system-prompt](../concepts/anatomia-do-system-prompt.md)
- [suite-de-regressao-de-prompts](suite-de-regressao-de-prompts.md)
