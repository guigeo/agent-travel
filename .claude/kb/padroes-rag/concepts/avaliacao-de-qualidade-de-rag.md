<!-- Prosa em português; código, nomes de API e keywords técnicas em inglês. Convenção: .claude/kb/_index.yaml -->
# Avaliação de qualidade de RAG: dois estágios, duas famílias de métrica

> **Propósito**: Um RAG falha em dois estágios independentes — retrieval e geração. Cada estágio precisa de pelo menos uma métrica própria; medir só a resposta final esconde onde o pipeline realmente quebrou.
> **Confiança**: 0.9
> **Validado**: 2026-08-06 (RAGAS core metrics; FutureAGI "RAG Evaluation Metrics 2026"; DigitalApplied "RAG System Metrics: Recall, Precision, Faithfulness 2026")

## Visão geral

Um pipeline RAG tem duas etapas que falham de formas diferentes: **retrieval** (buscar
os chunks certos) e **geração** (responder fielmente com base neles). Retrieval tem dois
modos de falha — recall baixo (chunk relevante nunca foi recuperado) e precisão baixa
(chunks irrelevantes poluem o contexto). Geração tem seu próprio modo de falha
independente do retrieval: mesmo com o contexto certo recuperado, o modelo pode ignorá-lo
e alucinar, ou extrapolar além do que o contexto sustenta. Avaliar só a resposta final
("a resposta está certa?") não diz qual das duas etapas falhou — e sem essa distinção,
não dá para saber se o fix é em chunking/retrieval ou em prompt/geração.

## O padrão

```text
Estágio 1 — RETRIEVAL (a busca trouxe os chunks certos?)
  Context Precision  → fração dos chunks recuperados que são relevantes
  Context Recall     → fração dos chunks relevantes que existem e foram recuperados
  Precision@k / Recall@k / MRR / NDCG → variantes sensíveis à posição no ranking

Estágio 2 — GERAÇÃO (a resposta é fiel ao que foi recuperado?)
  Faithfulness       → toda alegação da resposta é sustentada pelo contexto recuperado?
  Groundedness       → resposta cita/deriva do contexto, não do conhecimento paramétrico
  Answer Relevancy   → resposta de fato responde a pergunta feita
  Ausência de alucinação → quando o contexto NÃO cobre a pergunta, o modelo deve dizer
                            isso, nunca inventar uma resposta plausível
```

## Referência rápida

| Métrica | Estágio | Pergunta que responde | Sintoma se falhar |
|---|---|---|---|
| Context Recall | Retrieval | Os chunks relevantes existem no índice E foram recuperados? | Resposta genérica, "não encontrei informação" mesmo quando existe |
| Context Precision | Retrieval | Os chunks recuperados são relevantes? | Contexto poluído, resposta divagante ou lenta (mais tokens) |
| Faithfulness | Geração | A resposta é sustentada pelo contexto recuperado? | Alucinação — resposta plausível mas não rastreável ao contexto |
| Answer Relevancy | Geração | A resposta responde à pergunta feita? | Resposta correta sobre outro assunto, ou incompleta |

## Erros comuns

### Errado

```text
Avaliar só "a resposta final está correta? sim/não" com um humano lendo a saída.
→ não diferencia "retrieval não achou o chunk certo" de "achou, mas o modelo
  alucinou por cima" — o time corrige o componente errado, o problema persiste
```

### Certo

```text
Golden set com par (pergunta, chunks_esperados, resposta_esperada):
  1. medir Context Recall/Precision isolando SÓ o retriever (sem chamar o LLM)
  2. medir Faithfulness/Answer Relevancy dando ao LLM o contexto CORRETO manualmente
     (isola o problema de geração do problema de retrieval)
  3. só então medir end-to-end
```

## Relacionados

- [armadilhas-comuns-em-rag](armadilhas-comuns-em-rag.md)
- [avaliacao-automatizada-com-ragas](../patterns/avaliacao-automatizada-com-ragas.md)
- [retrieval-denso-esparso-e-hibrido](retrieval-denso-esparso-e-hibrido.md)
