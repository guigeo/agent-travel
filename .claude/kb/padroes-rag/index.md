# Padrões RAG Knowledge Base

> **Purpose**: Conhecimento geral de Retrieval-Augmented Generation — chunking, embeddings e busca (densa/esparsa/híbrida), re-ranking, injeção de contexto no prompt, avaliação de qualidade e armadilhas comuns. Agnóstico de provider de embedding, LLM e vector DB.
> **Validado**: 2026-08-06 (Firecrawl/Extend/DigitalApplied chunking playbooks 2026; AppScale/Denser.ai hybrid search & reranking 2026; RAGAS core metrics; Liu et al. "Lost in the Middle")

## Quick Navigation

### Concepts (< 150 lines each)

| File | Purpose |
|------|---------|
| [concepts/estrategias-de-chunking.md](concepts/estrategias-de-chunking.md) | Tamanho, overlap e chunking semântico vs. fixo — o maior determinante de recall |
| [concepts/retrieval-denso-esparso-e-hibrido.md](concepts/retrieval-denso-esparso-e-hibrido.md) | Embeddings (semântico) vs. BM25 (termo exato) e quando combinar via híbrido |
| [concepts/avaliacao-de-qualidade-de-rag.md](concepts/avaliacao-de-qualidade-de-rag.md) | Retrieval e geração falham de formas independentes — métrica por estágio |
| [concepts/armadilhas-comuns-em-rag.md](concepts/armadilhas-comuns-em-rag.md) | Lost-in-the-middle, poluição de contexto, chunking que quebra semântica |

### Patterns (< 200 lines each)

| File | Purpose |
|------|---------|
| [patterns/busca-hibrida-com-fusao-rrf.md](patterns/busca-hibrida-com-fusao-rrf.md) | Dense + BM25 em paralelo, fundidos por Reciprocal Rank Fusion |
| [patterns/re-ranking-com-cross-encoder.md](patterns/re-ranking-com-cross-encoder.md) | Retrieve amplo (recall) → rerank estreito (precisão) antes do prompt |
| [patterns/injecao-de-contexto-no-prompt.md](patterns/injecao-de-contexto-no-prompt.md) | Ordenação anti-lost-in-the-middle, citação de fonte, budget de tokens |
| [patterns/avaliacao-automatizada-com-ragas.md](patterns/avaliacao-automatizada-com-ragas.md) | Golden set + métricas por estágio como gate de regressão |

---

## Quick Reference

- [quick-reference.md](quick-reference.md) — tabelas de decisão e pitfalls

---

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Chunking é o gargalo silencioso** | fato cortado no meio nunca é recuperado, não importa a qualidade do retrieval |
| **Denso + esparso > qualquer um sozinho** | embeddings pegam paráfrase, BM25 pega termo exato; híbrido combina as duas forças |
| **Mais chunks ≠ melhor resposta** | top-k alto aumenta poluição e risco de lost-in-the-middle — precisão do retrieval > volume |
| **Retrieval e geração falham separado** | avaliar as duas etapas isoladas, não só a resposta final |
| **"Não sei" > resposta inventada** | quando o contexto não cobre a pergunta, o modelo deve declarar isso |

---

## Learning Path

| Level | Files |
|-------|-------|
| **Beginner** | concepts/estrategias-de-chunking.md → concepts/retrieval-denso-esparso-e-hibrido.md |
| **Intermediate** | patterns/busca-hibrida-com-fusao-rrf.md → patterns/re-ranking-com-cross-encoder.md → patterns/injecao-de-contexto-no-prompt.md |
| **Advanced** | concepts/avaliacao-de-qualidade-de-rag.md + patterns/avaliacao-automatizada-com-ragas.md |

---

## Agent Usage

| Agent | Primary Files | Use Case |
|-------|---------------|----------|
| genai-architect / llm-specialist | concepts/*, patterns/busca-hibrida-*, patterns/re-ranking-* | Desenhar pipeline de retrieval de um RAG |
| ai-prompt-specialist | patterns/injecao-de-contexto-no-prompt.md | Formatar contexto recuperado dentro do prompt |
| test-generator | patterns/avaliacao-automatizada-com-ragas.md | Suite de regressão de qualidade de RAG |
