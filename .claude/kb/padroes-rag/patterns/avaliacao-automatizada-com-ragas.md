<!-- Prosa em português; código, nomes de API e keywords técnicas em inglês. Convenção: .claude/kb/_index.yaml -->
# Avaliação automatizada de RAG estilo RAGAS

> **Propósito**: Suite de regressão para pipelines RAG — golden set versionado, métricas de retrieval e geração calculadas separadamente, gate antes de mudar chunking/retrieval/prompt em produção.
> **Validado**: 2026-08-06 (RAGAS core metrics; Braintrust "Best RAG Evaluation Tools 2026"; DataVLab "RAG Evaluation 2026: Methods, Metrics, Frameworks")

## Quando usar

- Antes de qualquer mudança em chunking, retrieval (denso/esparso/híbrido), re-ranking
  ou no template de injeção de contexto — mudanças "óbvias" regridem silenciosamente.
- Pipeline em produção onde qualidade da resposta é crítica (suporte, jurídico,
  financeiro) — regressão manual não escala e não é reproduzível.
- NÃO substitui avaliação humana amostral periódica — métricas automatizadas
  (especialmente as baseadas em LLM-as-judge) têm seu próprio ruído.

## Implementação

```python
from dataclasses import dataclass

@dataclass
class CasoDeTeste:
    pergunta: str
    chunks_esperados: set[str]     # doc_ids que DEVERIAM ser recuperados
    resposta_esperada: str         # referência para comparação de faithfulness/relevância


def context_recall(chunks_recuperados: list[str], chunks_esperados: set[str]) -> float:
    if not chunks_esperados:
        return 1.0
    acertos = len(set(chunks_recuperados) & chunks_esperados)
    return acertos / len(chunks_esperados)


def context_precision(chunks_recuperados: list[str], chunks_esperados: set[str]) -> float:
    if not chunks_recuperados:
        return 0.0
    acertos = len(set(chunks_recuperados) & chunks_esperados)
    return acertos / len(chunks_recuperados)


def faithfulness_llm_judge(resposta: str, contexto_usado: str, chamar_llm_juiz) -> float:
    """LLM-as-judge: pergunta se toda alegação da resposta é sustentada pelo contexto.
    Roda com modelo diferente (ou mesmo modelo, temperatura 0) do que gerou a resposta."""
    prompt_juiz = f"""Contexto: {contexto_usado}
Resposta a avaliar: {resposta}

Toda alegação factual na resposta está sustentada pelo contexto acima?
Responda apenas um número de 0.0 (nada sustentado) a 1.0 (tudo sustentado)."""
    return float(chamar_llm_juiz(prompt_juiz))


def rodar_suite(casos: list[CasoDeTeste], pipeline_rag, chamar_llm_juiz) -> dict:
    resultados = {"context_recall": [], "context_precision": [], "faithfulness": []}
    for caso in casos:
        chunks_recuperados, resposta, contexto_usado = pipeline_rag(caso.pergunta)
        resultados["context_recall"].append(
            context_recall(chunks_recuperados, caso.chunks_esperados))
        resultados["context_precision"].append(
            context_precision(chunks_recuperados, caso.chunks_esperados))
        resultados["faithfulness"].append(
            faithfulness_llm_judge(resposta, contexto_usado, chamar_llm_juiz))
    return {metrica: sum(vs) / len(vs) for metrica, vs in resultados.items()}
```

## Configuração

| Decisão | Padrão recomendado | Descrição |
|---|---|---|
| Tamanho do golden set | 30-100 casos, cobrindo classes de pergunta distintas | Poucos casos não detectam regressão; muitos casos custam manutenção |
| Casos "sem resposta no contexto" | Incluir explicitamente no golden set | Testa se o modelo declara "não sei" em vez de alucinar |
| Modelo do LLM-juiz | Separado do LLM de geração, temperatura 0 | Reduz viés de auto-avaliação e não-determinismo |
| Gate de merge | Nenhuma métrica pode regredir > X% vs. baseline | Threshold específico do domínio — definir com o time |
| Frequência de execução | A cada mudança em chunking/retrieval/prompt | Igual à suite de regressão de prompts — nunca opcional |

## Exemplo de uso

```python
golden_set = carregar_casos("golden_set_rag.jsonl")
metricas = rodar_suite(golden_set, pipeline_rag=meu_pipeline_rag,
                        chamar_llm_juiz=llm_juiz.avaliar)
assert metricas["context_recall"] >= 0.85, "Regressão em context recall — investigar chunking/retrieval"
assert metricas["faithfulness"] >= 0.90, "Regressão em faithfulness — investigar prompt/injeção de contexto"
```

## Ver também

- [avaliacao-de-qualidade-de-rag](../concepts/avaliacao-de-qualidade-de-rag.md)
- [injecao-de-contexto-no-prompt](injecao-de-contexto-no-prompt.md)
