<!-- Prosa em português; código, nomes de API e keywords técnicas em inglês. Convenção: .claude/kb/_index.yaml -->
# Retrieval denso, esparso e híbrido

> **Propósito**: Entender quando busca por embeddings (denso) sozinha falha, e por que combinar com busca por termo exato (esparso/BM25) via híbrido é o upgrade de maior impacto num RAG existente.
> **Confiança**: 0.9
> **Validado**: 2026-08-06 (Denser.ai "Hybrid Search for RAG 2026"; AppScale "Hybrid Search and Re-ranking in Production RAG 2026"; benchmark WANDS e-commerce)

## Visão geral

Busca densa (dense retrieval) representa query e chunks como vetores de embedding e
recupera por similaridade de cosseno — captura significado e paráfrase ("carro" ≈
"veículo"), mas é fraca em termos raros e exatos: códigos de produto, IDs, siglas,
números de contrato. Busca esparsa (BM25, TF-IDF) faz o oposto: casa termo exato com
precisão alta, mas não entende sinônimo ou paráfrase. Busca híbrida consulta os dois
índices em paralelo e funde os resultados — tipicamente via Reciprocal Rank Fusion (RRF),
que opera sobre o RANK de cada resultado, não sobre o score bruto (scores de sistemas
diferentes não são comparáveis diretamente). Em benchmark de e-commerce (WANDS), híbrido
bem ajustado atinge NDCG de 0.75 contra 0.70 (BM25 puro) e 0.695 (denso puro) — um ganho
de ~7% sobre qualquer um dos dois isolado.

## O padrão

```text
Query do usuário
      │
      ├──► índice denso (ANN sobre embeddings)  → top-K_denso candidatos
      │
      └──► índice esparso (BM25)                → top-K_esparso candidatos
                    │
                    ▼
         fusão por rank (RRF) — não por score bruto
                    │
                    ▼
         lista fundida → (opcional) re-ranking com cross-encoder
                    │
                    ▼
         top-N final injetado no prompt
```

## Referência rápida

| Abordagem | Força | Fraqueza | Quando é suficiente sozinho |
|---|---|---|---|
| Denso (embeddings) | Paráfrase, sinônimo, significado | Termo raro/exato (código, ID, sigla) | Domínio conceitual, sem vocabulário técnico crítico |
| Esparso (BM25) | Termo exato, sigla, jargão de domínio | Sinônimo, paráfrase, contexto | Busca por identificador/código conhecido |
| Híbrido (denso + esparso, fundido por RRF) | Combina as duas forças | Custo de manter 2 índices + fusão | Produção com vocabulário misto (nomes próprios + linguagem natural) — padrão recomendado |

## Erros comuns

### Errado

```text
Usar só busca densa em domínio com códigos/IDs no vocabulário:
Query: "erro no pedido PED-88213"
→ embedding da query fica dominado pela semântica de "erro" e "pedido";
  o código exato PED-88213 se perde no vetor — retrieval não encontra o chunk certo
```

### Certo

```text
Híbrido: BM25 casa "PED-88213" com precisão exata (match de token),
denso recupera chunks sobre "problemas com pedido" mesmo sem o código citado,
RRF funde as duas listas por rank → o chunk certo aparece no topo mesmo que
só um dos dois retrievers o tenha ranqueado bem
```

## Relacionados

- [estrategias-de-chunking](estrategias-de-chunking.md)
- [busca-hibrida-com-fusao-rrf](../patterns/busca-hibrida-com-fusao-rrf.md)
- [re-ranking-com-cross-encoder](../patterns/re-ranking-com-cross-encoder.md)
