<!-- Prosa em português; código, nomes de API e keywords técnicas em inglês. Convenção: .claude/kb/_index.yaml -->
# Re-ranking com cross-encoder: retrieve amplo, rerank estreito

> **Propósito**: Reduzir a lista de candidatos recuperados (denso, esparso ou híbrido) a um top-N de alta precisão antes de injetar no prompt — o retrieval inicial otimiza recall, o re-ranking otimiza precisão.
> **Validado**: 2026-08-06 (AppScale "Hybrid Search and Re-ranking in Production RAG 2026"; benchmark financeiro texto+tabela — Recall@5 0.816 com pipeline híbrido + rerank neural)

## Quando usar

- O retrieval inicial (denso, esparso ou híbrido) já roda, mas o contexto final injetado
  no prompt ainda tem chunks irrelevantes ou fora de ordem de relevância.
- Latência permite um passo extra: cross-encoder em top-100 candidatos custa
  tipicamente milissegundos, dentro do orçamento de p99 de busca interativa.
- NÃO usar como substituto do retrieval inicial — cross-encoder é caro demais para
  rodar sobre a coleção inteira; ele só faz sentido sobre uma shortlist já filtrada.

## Implementação

```python
from dataclasses import dataclass

@dataclass
class Candidato:
    doc_id: str
    texto: str
    score_retrieval: float   # score do estágio anterior (RRF, cosine, BM25)


def rerank(query: str, candidatos: list[Candidato], modelo_cross_encoder,
           top_n: int = 8) -> list[Candidato]:
    """Cross-encoder processa (query, doc) juntos — mais preciso que embeddings
    separados, mas O(N) mais caro. Por isso roda só sobre a shortlist, não sobre
    o índice inteiro."""
    pares = [(query, c.texto) for c in candidatos]
    scores_precisos = modelo_cross_encoder.predict(pares)   # ex.: sentence-transformers CrossEncoder

    candidatos_pontuados = list(zip(candidatos, scores_precisos))
    candidatos_pontuados.sort(key=lambda par: par[1], reverse=True)

    return [candidato for candidato, _score in candidatos_pontuados[:top_n]]


def pipeline_retrieve_and_rerank(query: str, indice_hibrido, modelo_cross_encoder):
    shortlist = indice_hibrido.search(query, top_k=100)     # estágio 1: recall amplo
    candidatos = [Candidato(doc_id=d.id, texto=d.texto, score_retrieval=d.score)
                  for d in shortlist]
    return rerank(query, candidatos, modelo_cross_encoder, top_n=8)  # estágio 2: precisão
```

## Configuração

| Decisão | Padrão recomendado | Descrição |
|---|---|---|
| Tamanho da shortlist (entrada do rerank) | top-50 a top-100 | Grande o suficiente para não perder recall, pequeno o suficiente para latência aceitável |
| `top_n` final (saída do rerank) | 5-10 chunks | O que de fato entra no prompt — ver injecao-de-contexto-no-prompt.md |
| Modelo de cross-encoder | Modelo dedicado de reranking (não o mesmo LLM da geração) | Mais barato e mais preciso para essa tarefa específica que usar um LLM generalista |
| Quando pular o re-ranking | Retrieval já com alta precisão (ex.: busca por ID exato) | Overhead sem ganho quando a shortlist já é praticamente só relevante |

## Exemplo de uso

```python
top_chunks = pipeline_retrieve_and_rerank(
    "qual o prazo de pagamento do contrato PED-88213?",
    indice_hibrido,
    modelo_cross_encoder,
)
# → top_chunks (8 candidatos, ordenados por relevância real) segue para
#   patterns/injecao-de-contexto-no-prompt.md
```

## Ver também

- [busca-hibrida-com-fusao-rrf](busca-hibrida-com-fusao-rrf.md)
- [armadilhas-comuns-em-rag](../concepts/armadilhas-comuns-em-rag.md)
- [injecao-de-contexto-no-prompt](injecao-de-contexto-no-prompt.md)
