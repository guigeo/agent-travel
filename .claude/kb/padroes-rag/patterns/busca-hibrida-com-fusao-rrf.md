<!-- Prosa em português; código, nomes de API e keywords técnicas em inglês. Convenção: .claude/kb/_index.yaml -->
# Busca híbrida com fusão RRF (Reciprocal Rank Fusion)

> **Propósito**: Combinar busca densa (embeddings) e esparsa (BM25) num único ranking, sem sofrer o problema de scores incompatíveis entre sistemas diferentes.
> **Validado**: 2026-08-06 (AppScale "Hybrid Search and Re-ranking in Production RAG 2026"; Elasticsearch BM25+HNSW+RRF reference; benchmark WANDS e-commerce)

## Quando usar

- Vocabulário misto: linguagem natural (paráfrase, sinônimo) E termos exatos (código de
  produto, ID, sigla, jargão de domínio) coexistem nas queries dos usuários.
- Já existe um RAG só com busca densa e a qualidade estagnou — hybrid search é o upgrade
  de maior impacto isolado disponível.
- NÃO é necessário se o domínio é puramente conceitual, sem identificadores exatos
  relevantes na busca (overhead de manter dois índices sem ganho proporcional).

## Implementação

```python
from collections import defaultdict

def reciprocal_rank_fusion(
    ranked_lists: list[list[str]],   # cada lista: IDs de doc em ordem de rank (0 = melhor)
    k: int = 60,                      # constante de suavização — padrão da literatura
) -> list[tuple[str, float]]:
    """RRF: soma 1/(k + rank) por lista em que o doc aparece. Opera sobre RANK,
    não sobre score bruto — scores de sistemas diferentes (BM25 vs cosine) não
    são comparáveis diretamente, ranks são."""
    scores: dict[str, float] = defaultdict(float)
    for ranked_list in ranked_lists:
        for rank, doc_id in enumerate(ranked_list):
            scores[doc_id] += 1.0 / (k + rank + 1)
    return sorted(scores.items(), key=lambda item: item[1], reverse=True)


def busca_hibrida(query: str, indice_denso, indice_bm25, top_k_por_retriever: int = 50):
    resultados_densos = indice_denso.search(query, top_k=top_k_por_retriever)
    resultados_bm25 = indice_bm25.search(query, top_k=top_k_por_retriever)

    lista_densa_ids = [doc_id for doc_id, _score in resultados_densos]
    lista_bm25_ids = [doc_id for doc_id, _score in resultados_bm25]

    fundido = reciprocal_rank_fusion([lista_densa_ids, lista_bm25_ids])
    return fundido  # [(doc_id, score_rrf), ...] ordenado, pronto para re-ranking
```

## Configuração

| Decisão | Padrão recomendado | Descrição |
|---|---|---|
| `k` (constante RRF) | 60 | Valor padrão da literatura — suaviza a diferença entre rank 1 e rank 2 |
| `top_k_por_retriever` | 50-500 | Candidatos por sistema antes da fusão; maior = mais recall, mais custo de re-ranking depois |
| Execução dos dois retrievers | Em paralelo, sempre | Latência = max(denso, esparso), não soma |
| Pesos por sistema | Nenhum por padrão (RRF é não-ponderado) | Só ponderar se um teste A/B mostrar que um sistema é sistematicamente melhor no domínio |

## Exemplo de uso

```python
candidatos = busca_hibrida("erro no pedido PED-88213", indice_denso, indice_bm25)
top_50_ids = [doc_id for doc_id, _score in candidatos[:50]]
# → passar para re-ranking (ver patterns/re-ranking-com-cross-encoder.md) antes
#   de injetar no prompt
```

## Ver também

- [retrieval-denso-esparso-e-hibrido](../concepts/retrieval-denso-esparso-e-hibrido.md)
- [re-ranking-com-cross-encoder](re-ranking-com-cross-encoder.md)
