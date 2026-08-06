# Padrões RAG Quick Reference

> Fast lookup tables. For code examples, see linked files.

## Chunking — ponto de partida

| Decisão | Padrão recomendado | Arquivo de referência |
|---|---|---|
| Tamanho do chunk | 400-512 tokens | concepts/estrategias-de-chunking.md |
| Overlap | 10-20% do tamanho (ou 1-3 sentenças) — medir, não assumir | concepts/estrategias-de-chunking.md |
| Splitter | Recursivo (parágrafo → sentença → palavra) | concepts/estrategias-de-chunking.md |
| Escalar para semântico | Só se métrica de recall mostrar gap sistemático | concepts/estrategias-de-chunking.md |

## Decision Matrix — retrieval

| Sintoma / cenário | Escolha |
|---|---|
| Vocabulário misto (linguagem natural + código/ID/sigla) | Busca híbrida (denso + BM25) com fusão RRF |
| Domínio puramente conceitual, sem identificadores exatos | Busca densa sozinha é suficiente |
| Retrieval já roda mas contexto final tem ruído | Adicionar re-ranking com cross-encoder antes do prompt |
| Resposta certa está no índice mas não aparece no top-k | Aumentar `top_k_por_retriever` antes de rerank, não o top-k final do prompt |

## Decision Matrix — injeção de contexto

| Sintoma | Escolha |
|---|---|
| Modelo ignora fato que está no meio do contexto | Reordenar: mais relevante nas bordas (início/fim) |
| Resposta usa chunk fora de tópico | Aumentar precisão (rerank) antes de aumentar top-k |
| Resposta sem rastreabilidade de fonte | Citar `doc_id`/origem em cada chunk + instruir citação no output |
| Contexto não cobre a pergunta | Instrução explícita para o modelo declarar "não sei" |

## Common Pitfalls

| Don't | Do |
|-------|-----|
| Aumentar top-k "para garantir" que o chunk certo está lá | Investir em precisão (re-ranking) e manter contexto final enxuto |
| Cortar chunk por contagem fixa de caracteres | Splitter recursivo respeitando parágrafo/sentença + overlap |
| Só busca densa em domínio com códigos/IDs/siglas | Híbrido (denso + BM25) fundido por RRF |
| Comparar score bruto de BM25 com score de cosine diretamente | Fundir por RANK (RRF), não por score |
| Avaliar só "a resposta final está certa?" | Medir retrieval (recall/precision) e geração (faithfulness) separado |
| Deixar o modelo "preencher a lacuna" quando o contexto não cobre | Instrução explícita: declarar ausência de informação, nunca extrapolar |

## Related Documentation

| Topic | Path |
|-------|------|
| Getting Started | `concepts/estrategias-de-chunking.md` |
| Full Index | `index.md` |
