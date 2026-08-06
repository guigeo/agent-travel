<!-- Prosa em português; código, nomes de API e keywords técnicas em inglês. Convenção: .claude/kb/_index.yaml -->
# Injeção de contexto recuperado no prompt: ordenação, citação e budget

> **Propósito**: Formatar os chunks recuperados dentro do prompt de forma que o modelo consiga distinguir fonte de instrução, citar origem, e não sofra degradação por lost-in-the-middle ou estouro de budget de tokens.
> **Validado**: 2026-08-06 (Liu et al. "Lost in the Middle"; getmaxim.ai "Solving the Lost in the Middle Problem"; práticas de spotlighting/delimitação de dados não confiáveis)

## Quando usar

- Sempre que chunks recuperados (RAG) entram no prompt — este é o passo final do
  pipeline de retrieval, imediatamente antes de chamar o LLM.
- Especialmente crítico quando o número de chunks é maior que 3-4 (risco de
  lost-in-the-middle cresce) ou quando a resposta precisa ser rastreável à fonte
  (compliance, auditoria, resposta ao usuário com citação).
- NÃO ignorar mesmo com poucos chunks — delimitação clara entre dado recuperado e
  instrução do sistema também reduz risco de prompt injection via conteúdo indexado.

## Implementação

```python
from dataclasses import dataclass

@dataclass
class ChunkRecuperado:
    doc_id: str
    fonte: str          # ex.: "manual_produto_v3.pdf, p.12"
    texto: str
    score_relevancia: float


def ordenar_para_contexto(chunks: list[ChunkRecuperado]) -> list[ChunkRecuperado]:
    """Mitiga lost-in-the-middle: mais relevante no INÍCIO e no FIM,
    menos relevante escondido no meio da lista."""
    ordenados = sorted(chunks, key=lambda c: c.score_relevancia, reverse=True)
    meio, bordas = [], []
    for i, c in enumerate(ordenados):
        (bordas if i % 2 == 0 else meio).append(c)
    # intercala: mais relevantes vão para as bordas (início/fim), resto para o meio
    return bordas[:len(bordas) // 2] + meio + bordas[len(bordas) // 2:]


def montar_bloco_de_contexto(chunks: list[ChunkRecuperado], budget_tokens: int,
                               contar_tokens) -> str:
    """Respeita budget: para de adicionar chunks quando o orçamento estoura,
    nunca trunca um chunk no meio (perderia coerência)."""
    chunks_ordenados = ordenar_para_contexto(chunks)
    partes, tokens_usados = [], 0
    for c in chunks_ordenados:
        bloco = f'<source id="{c.doc_id}" origem="{c.fonte}">\n{c.texto}\n</source>'
        custo = contar_tokens(bloco)
        if tokens_usados + custo > budget_tokens:
            break
        partes.append(bloco)
        tokens_usados += custo
    return "\n\n".join(partes)


def montar_prompt(pergunta: str, chunks: list[ChunkRecuperado], budget_tokens: int,
                   contar_tokens) -> str:
    bloco_contexto = montar_bloco_de_contexto(chunks, budget_tokens, contar_tokens)
    return f"""Responda à pergunta usando APENAS as informações dentro de <source>.
Cite o id da fonte usada entre colchetes, ex.: [doc_42].
Se as fontes não contiverem informação suficiente para responder, diga isso
explicitamente — NUNCA complete com conhecimento próprio.

{bloco_contexto}

Pergunta: {pergunta}"""
```

## Configuração

| Decisão | Padrão recomendado | Descrição |
|---|---|---|
| Ordenação dos chunks | Mais relevante nas bordas (início/fim), fraco no meio | Mitiga lost-in-the-middle — U-shape de atenção do modelo |
| Número de chunks no prompt | 5-10, vindos de re-ranking | Mais chunks = mais poluição e mais risco de lost-in-the-middle |
| Budget de tokens do contexto recuperado | Fatia fixa do orçamento total (ver janela-de-contexto em engenharia-de-prompts) | Nunca deixar o contexto recuperado crescer livre |
| Citação de fonte | ID + origem em toda entrada, instrução de citar no output | Rastreabilidade — essencial para compliance/auditoria |
| Instrução sobre ausência de cobertura | Explícita: "diga que não sabe, não complete" | Reduz alucinação quando o retrieval não cobre a pergunta |

## Exemplo de uso

```python
prompt = montar_prompt(
    pergunta="Qual o prazo de pagamento do contrato PED-88213?",
    chunks=top_chunks,          # saída de re-ranking-com-cross-encoder.md
    budget_tokens=3000,
    contar_tokens=contador_de_tokens_do_provider,
)
resposta = llm.create(system=SYSTEM_PROMPT, user=prompt)
```

## Ver também

- [armadilhas-comuns-em-rag](../concepts/armadilhas-comuns-em-rag.md)
- [re-ranking-com-cross-encoder](re-ranking-com-cross-encoder.md)
- [avaliacao-automatizada-com-ragas](avaliacao-automatizada-com-ragas.md)
