# Engenharia de Prompts Knowledge Base

> **Purpose**: Conhecimento geral de prompt engineering — estrutura de system prompts, técnicas (few-shot/chain-of-thought/structured output), gerenciamento de contexto e histórico, testes/regressão de prompts, e armadilhas comuns. Agnóstico de provider (OpenAI, Anthropic, etc.) e de framework de orquestração.
> **Validado**: 2026-08-06 (Anthropic prompt engineering docs, OpenAI Structured Outputs guide, OWASP LLM Prompt Injection Cheat Sheet, pesquisa cross-provider 2026)

## Quick Navigation

### Concepts (< 150 lines each)

| File | Purpose |
|------|---------|
| [concepts/anatomia-do-system-prompt.md](concepts/anatomia-do-system-prompt.md) | Papel, contexto, restrições, formato de saída — estrutura que atravessa providers |
| [concepts/tecnicas-fundamentais-de-prompting.md](concepts/tecnicas-fundamentais-de-prompting.md) | Few-shot ancora forma; chain-of-thought ancora raciocínio multi-step |
| [concepts/janela-de-contexto-e-gerenciamento-de-historico.md](concepts/janela-de-contexto-e-gerenciamento-de-historico.md) | Contexto como orçamento de tokens, não buffer ilimitado |
| [concepts/ambiguidade-e-overfitting-em-poucos-exemplos.md](concepts/ambiguidade-e-overfitting-em-poucos-exemplos.md) | Os dois defeitos que dominam prompts artesanais |

### Patterns (< 200 lines each)

| File | Purpose |
|------|---------|
| [patterns/structured-output-json-schema.md](patterns/structured-output-json-schema.md) | JSON Schema nativo do provider — não "peça JSON" no texto |
| [patterns/compactacao-de-historico-de-conversa.md](patterns/compactacao-de-historico-de-conversa.md) | Sliding window + sumarização em fronteira de turno |
| [patterns/suite-de-regressao-de-prompts.md](patterns/suite-de-regressao-de-prompts.md) | Casos versionados, comportamento > valor exato, diff caso a caso |
| [patterns/mitigacao-de-prompt-injection.md](patterns/mitigacao-de-prompt-injection.md) | Hierarquia de instrução + separação dado/instrução |

---

## Quick Reference

- [quick-reference.md](quick-reference.md) — tabelas de decisão e pitfalls

---

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Estrutura > prosa solta** | role/context/constraints/output_format demarcados > parágrafo único |
| **Técnica por sintoma** | few-shot para formato inconsistente; chain-of-thought para erro de lógica multi-step |
| **Contexto é orçamento** | histórico tem teto; ao estourar, compactar — nunca deixar crescer livre |
| **Prompt é código de política** | mudança de prompt roda suite de regressão antes de mergear |
| **Dado ≠ instrução** | conteúdo de terceiros nunca tem autoridade — hierarquia explícita reduz injection |

---

## Learning Path

| Level | Files |
|-------|-------|
| **Beginner** | concepts/anatomia-do-system-prompt.md → concepts/tecnicas-fundamentais-de-prompting.md |
| **Intermediate** | concepts/janela-de-contexto-e-gerenciamento-de-historico.md → patterns/compactacao-de-historico-de-conversa.md |
| **Advanced** | patterns/suite-de-regressao-de-prompts.md + patterns/mitigacao-de-prompt-injection.md |

---

## Agent Usage

| Agent | Primary Files | Use Case |
|-------|---------------|----------|
| ai-prompt-specialist / llm-specialist | concepts/*, patterns/structured-output-*, patterns/mitigacao-* | Desenhar/corrigir system prompts |
| genai-architect | concepts/janela-de-contexto-*, patterns/compactacao-* | Desenhar gerenciamento de contexto/histórico |
| test-generator | patterns/suite-de-regressao-de-prompts.md | Suite de regressão de prompt |
