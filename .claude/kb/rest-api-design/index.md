# REST API Design Knowledge Base

> **Purpose**: Conhecimento geral de design de APIs REST — modelagem de recursos e verbos HTTP, status codes e formato de erro (RFC 9457 Problem Details), versionamento, paginação/filtragem/ordenação, validação de contrato e design de payloads. Agnóstico de framework (aplica a FastAPI, Express, Spring, etc.); exemplos ilustrativos em Python.
> **Validado**: 2026-08-06 (RFC 9110 HTTP Semantics; RFC 9457 Problem Details for HTTP APIs; RFC 8594 Sunset Header; Google/Microsoft/Zalando API design guidelines; Speakeasy pagination guide)

## Quick Navigation

### Concepts (< 150 lines each)

| File | Purpose |
|------|---------|
| [concepts/modelagem-de-recursos-e-verbos-http.md](concepts/modelagem-de-recursos-e-verbos-http.md) | Nomenclatura de rotas e semântica de idempotência de cada verbo HTTP |
| [concepts/codigos-de-status-e-formato-de-erro.md](concepts/codigos-de-status-e-formato-de-erro.md) | Famílias de status code e por que erro nunca deveria voltar como `200` |
| [concepts/versionamento-de-api.md](concepts/versionamento-de-api.md) | URL path vs header vs media type versioning, e sinalização de deprecação |
| [concepts/design-de-payloads-e-convencoes.md](concepts/design-de-payloads-e-convencoes.md) | Envelope vs resposta direta, casing e consistência de payload |

### Patterns (< 200 lines each)

| File | Purpose |
|------|---------|
| [patterns/paginacao-cursor-e-offset.md](patterns/paginacao-cursor-e-offset.md) | Cursor-based pagination como padrão; offset como exceção documentada |
| [patterns/problem-details-rfc9457.md](patterns/problem-details-rfc9457.md) | Exception handler central que devolve erro no formato RFC 9457 |
| [patterns/validacao-de-contrato-com-schema.md](patterns/validacao-de-contrato-com-schema.md) | Validar request/response na borda com schema (Pydantic/JSON Schema) |
| [patterns/estrategia-de-deprecacao-e-breaking-change.md](patterns/estrategia-de-deprecacao-e-breaking-change.md) | Headers `Deprecation`/`Sunset` e coexistência de versões antes de remover |

---

## Quick Reference

- [quick-reference.md](quick-reference.md) — tabelas de decisão e pitfalls

---

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Recurso é substantivo, verbo é o método** | Rota nunca carrega verbo (`/getUsers`); o verbo HTTP já expressa a ação |
| **Idempotência é contrato, não detalhe** | `PUT`/`DELETE` idempotentes; `POST` não; `PATCH` só se merge for determinístico |
| **Status code é protocolo** | Erro sempre no status code certo — nunca `200` com `success: false` no corpo |
| **Consistência > preferência pessoal** | Envelope vs direto, camelCase vs snake_case: escolher um e nunca misturar |
| **Versionar é prometer estabilidade** | Versão + deprecação com prazo (`Sunset`) é o que permite evoluir sem quebrar cliente |

---

## Learning Path

| Level | Files |
|-------|-------|
| **Beginner** | concepts/modelagem-de-recursos-e-verbos-http.md → concepts/codigos-de-status-e-formato-de-erro.md |
| **Intermediate** | concepts/design-de-payloads-e-convencoes.md → patterns/validacao-de-contrato-com-schema.md → patterns/paginacao-cursor-e-offset.md |
| **Advanced** | concepts/versionamento-de-api.md + patterns/estrategia-de-deprecacao-e-breaking-change.md |

---

## Agent Usage

| Agent | Primary Files | Use Case |
|-------|---------------|----------|
| python-developer / code-reviewer | concepts/*, patterns/validacao-de-contrato-com-schema.md | Desenhar ou revisar rotas de uma API REST |
| genai-architect / ai-data-engineer | patterns/problem-details-rfc9457.md, patterns/paginacao-cursor-e-offset.md | Endpoints que servem dados para agentes/pipelines |
| the-planner | concepts/versionamento-de-api.md, patterns/estrategia-de-deprecacao-e-breaking-change.md | Planejar rollout de breaking change em API pública |
