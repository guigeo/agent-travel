<!-- Prosa em português; código, nomes de API e keywords técnicas em inglês. Convenção: .claude/kb/_index.yaml -->
# Estratégias de chunking: tamanho, overlap e semântico vs. fixo

> **Propósito**: Dividir documentos em pedaços (`chunks`) que preservem unidade semântica e caibam num budget de embedding/contexto — a decisão que mais impacta recall de um RAG.
> **Confiança**: 0.9
> **Validado**: 2026-08-06 (Firecrawl "Best Chunking Strategies for RAG in 2026"; Extend "Semantic Chunking: 5 Best Practices"; DigitalApplied "RAG Chunking Strategies Playbook 2026")

## Visão geral

Chunking é o primeiro ponto de falha de um pipeline RAG: se o chunk quebra uma unidade
semântica (uma frase no meio, uma tabela cortada, um bloco de código dividido), nenhuma
técnica de retrieval ou re-ranking recupera a informação perdida — ela nunca foi indexada
de forma coerente. A baseline pragmática é `RecursiveCharacterTextSplitter` (ou
equivalente) em 400-512 tokens, com overlap de 10-20% do tamanho do chunk. Chunking
semântico (fronteira definida por queda de similaridade entre sentenças adjacentes)
ganha 2-3 pontos de recall sobre a baseline recursiva, mas custa embedar frase a frase —
só vale o investimento se a métrica de avaliação mostrar que o gap importa para o caso de
uso. Overlap não é gratuito: um estudo sistemático de 2026 encontrou casos onde overlap
não trouxe ganho mensurável, apenas custo extra de indexação — vale medir, não assumir.

## O padrão

```text
Baseline pragmática (ponto de partida para 90% dos casos):
  tamanho do chunk:    400-512 tokens
  overlap:              10-20% do tamanho (ou 1-3 sentenças na fronteira)
  splitter:             recursivo (respeita parágrafo > sentença > palavra, nessa ordem)

Escalar para chunking semântico SE:
  1. métrica de retrieval (recall@k) mostra perda sistemática em documentos longos
     heterogêneos (múltiplos tópicos por documento), E
  2. budget de indexação comporta embedar por sentença antes de agrupar

Chunking semântico: embedar cada sentença → comparar similaridade de cosseno entre
sentenças adjacentes → cortar onde a similaridade cai abruptamente (fronteira de tópico).
```

## Referência rápida

| Estratégia | Recall típico | Custo de indexação | Quando usar |
|---|---|---|---|
| Fixo por caractere/token (sem respeitar estrutura) | Baixo — corta no meio de frases | Mínimo | Nunca como primeira escolha |
| Recursivo (parágrafo → sentença → palavra) | 85-90% @ 400 tokens | Baixo | Baseline — ponto de partida padrão |
| Sentença (chunk = N sentenças) | Equivale ao semântico até ~5k tokens/doc | Baixo-médio | Documentos curtos/médios, homogêneos |
| Semântico (embedding-based, fronteira por queda de similaridade) | 91-92% @ 400 tokens | Alto — embed por sentença | Documentos longos, multi-tópico, quando a métrica justifica |

## Erros comuns

### Errado

```text
Cortar por contagem fixa de caracteres sem respeitar estrutura:
"...o contrato estabelece que o prazo de pagamento é" | "de 30 dias corridos após..."
→ o fato numérico fica partido entre dois chunks; nenhum dos dois, sozinho, responde
  "qual o prazo de pagamento?"
```

### Certo

```text
Splitter recursivo com overlap de 1-3 sentenças na fronteira:
Chunk 1: "...o contrato estabelece que o prazo de pagamento é de 30 dias corridos
          após a emissão da nota fiscal."
Chunk 2: "O prazo de pagamento é de 30 dias corridos após a emissão da nota fiscal.
          Em caso de atraso, incide multa de 2%..."
→ overlap garante que o fato completo apareça inteiro em pelo menos um chunk
```

## Relacionados

- [retrieval-denso-esparso-e-hibrido](retrieval-denso-esparso-e-hibrido.md)
- [armadilhas-comuns-em-rag](armadilhas-comuns-em-rag.md)
- [busca-hibrida-com-fusao-rrf](../patterns/busca-hibrida-com-fusao-rrf.md)
