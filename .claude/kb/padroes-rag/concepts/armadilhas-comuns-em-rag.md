<!-- Prosa em português; código, nomes de API e keywords técnicas em inglês. Convenção: .claude/kb/_index.yaml -->
# Armadilhas comuns em RAG: lost-in-the-middle, poluição de contexto, chunking ruim

> **Propósito**: As três falhas que dominam RAGs mal-sucedidos — nenhuma delas é sobre "escolher o vector DB certo".
> **Confiança**: 0.9
> **Validado**: 2026-08-06 (Liu et al. "Lost in the Middle: How Language Models Use Long Contexts"; Arize research reading; QubitTool "Long Context LLMs and the Lost in the Middle Phenomenon 2026")

## Visão geral

A maioria dos problemas de qualidade em RAG não vem do modelo nem do vector DB — vem de
três armadilhas recorrentes e evitáveis. **Lost-in-the-middle**: modelos atendem melhor
ao início e ao fim do contexto; informação relevante posicionada no meio de um contexto
longo sofre degradação de mais de 30% em acurácia, formando uma curva de desempenho em U.
**Poluição de contexto**: injetar chunks irrelevantes (falha de precisão no retrieval)
não é neutro — aumenta o risco do modelo se apoiar no chunk errado, dilui a atenção e
aumenta custo/latência sem ganho. **Chunking ruim**: cortar um chunk no meio de uma frase,
tabela ou bloco de código quebra a unidade semântica — nenhum retrieval ou re-ranking
recupera um fato que nunca foi indexado de forma coerente (ver
[estrategias-de-chunking](estrategias-de-chunking.md)).

## O padrão

```text
Diagnóstico rápido — sintoma → armadilha provável:

"O modelo ignora um fato que EU SEI que está no contexto, mas não no início/fim"
  → lost-in-the-middle: reordenar (mais relevante no início E no fim, menos relevante
    no meio) ou reduzir o total de chunks injetados

"O modelo responde com informação de um chunk claramente fora do tópico da pergunta"
  → poluição de contexto: aumentar precisão do retrieval (re-ranking, hybrid search)
    antes de aumentar top-k

"A resposta cita um fato incompleto ou fora de contexto, mas o documento fonte
  tinha a informação completa"
  → chunking ruim: revisar tamanho/overlap, considerar chunking semântico
```

## Referência rápida

| Armadilha | Causa raiz | Mitigação primária |
|---|---|---|
| Lost-in-the-middle | Viés posicional do modelo em contextos longos | Ordenar chunks por relevância (mais relevante nas bordas); reduzir top-k |
| Poluição de contexto | Baixa precisão no retrieval (chunks irrelevantes entram) | Re-ranking com cross-encoder antes de montar o prompt |
| Chunking ruim | Corte que ignora fronteira semântica (frase/tabela/código) | Splitter recursivo + overlap; escalar para semântico se métrica justificar |
| Contexto sem cobertura da pergunta | Retrieval não encontrou nada relevante (gap real na base) | Instruir o modelo a declarar "não sei" em vez de extrapolar/alucinar |

## Erros comuns

### Errado

```text
Aumentar top-k de 5 para 20 chunks "para garantir que a resposta certa está lá dentro"
→ mais chunks irrelevantes entram (poluição), o chunk certo pode cair no meio do
  contexto (lost-in-the-middle) — a taxa de acerto pode PIORAR, não melhorar
```

### Certo

```text
Investir em precisão do retrieval (re-ranking) para reduzir top-k necessário,
manter o contexto final enxuto (poucos chunks, todos relevantes), e ordenar
por relevância deixando os mais fracos no meio da lista, nunca nas bordas
```

## Relacionados

- [estrategias-de-chunking](estrategias-de-chunking.md)
- [avaliacao-de-qualidade-de-rag](avaliacao-de-qualidade-de-rag.md)
- [injecao-de-contexto-no-prompt](../patterns/injecao-de-contexto-no-prompt.md)
- [re-ranking-com-cross-encoder](../patterns/re-ranking-com-cross-encoder.md)
