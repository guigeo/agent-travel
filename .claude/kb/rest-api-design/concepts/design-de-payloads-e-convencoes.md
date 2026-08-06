<!-- Prosa em português; código, nomes de API e keywords técnicas em inglês. Convenção: .claude/kb/_index.yaml -->
# Design de payloads e convenções

> **Propósito**: Decidir envelope vs. resposta direta e fixar convenções de payload (casing, datas, null) uma vez — e aplicar em toda a API, não endpoint a endpoint.
> **Confiança**: 0.9
> **Validado**: 2026-08-06 (Google API Design Guide; Microsoft REST API Guidelines; JSON:API spec como referência de envelope)

## Visão geral

**Envelope** significa embrulhar a resposta em um objeto com metadados
(`{"data": ..., "meta": {...}}`); **resposta direta** devolve o recurso puro
(`{"id": 1, "name": "..."}`) ou a coleção como array puro. Envelope ajuda quando a
resposta genuinamente precisa de metadados fora do recurso (paginação, contagem,
links) — sem ele, esses campos teriam que virar headers customizados. Resposta
direta é mais simples para o caso comum (um recurso, sem metadados). A escolha em
si importa menos que a **consistência**: misturar os dois estilos entre endpoints
força o cliente a tratar cada resposta como um caso especial. O mesmo vale para
casing (`camelCase` vs `snake_case`) — ambos são aceitáveis, escolher um e nunca
misturar dentro do mesmo payload é o que evita bug de parsing no cliente.

## O padrão

```json
// Envelope — usado quando há metadados genuínos (ex.: coleção paginada)
{
  "data": [{"id": 1, "name": "Ana"}, {"id": 2, "name": "Bruno"}],
  "meta": {"nextCursor": "eyJpZCI6Mn0", "hasMore": true}
}

// Resposta direta — usada para um recurso único, sem metadados a comunicar
{"id": 1, "name": "Ana", "createdAt": "2026-08-06T14:30:00Z"}
```

## Referência rápida

| Decisão | Escolha recomendada | Nota |
|---------|----------------------|------|
| Coleção com paginação/metadados | Envelope (`data` + `meta`) | Metadados não cabem no corpo do array puro |
| Recurso único, sem metadados | Resposta direta | Envelope aqui é boilerplate sem função |
| Casing | `camelCase` (ecossistema JS/API pública) ou `snake_case` (ecossistema Python) | Um só, documentado, nunca os dois no mesmo payload |
| Datas | ISO-8601 em UTC (`2026-08-06T14:30:00Z`) | Nunca timestamp Unix cru sem documentar a unidade |
| Campo ausente vs. `null` | Documentar a diferença explicitamente | `null` = "sei que não tem valor"; ausente = "não retornado nesta view" |

## Erros comuns

### Errado

```json
// Endpoint A devolve array puro
[{"id": 1}, {"id": 2}]
// Endpoint B da mesma API devolve envelope
{"data": [{"id": 1}], "meta": {}}
// Endpoint C mistura casing dentro do MESMO objeto
{"userId": 1, "created_at": "2026-08-06"}
```

### Certo

```json
// Mesma convenção em toda a API pública: envelope + camelCase
{"data": {"userId": 1, "createdAt": "2026-08-06T14:30:00Z"}, "meta": {}}
```

## Relacionados

- [modelagem-de-recursos-e-verbos-http](modelagem-de-recursos-e-verbos-http.md)
- [validacao-de-contrato-com-schema](../patterns/validacao-de-contrato-com-schema.md)
- [paginacao-cursor-e-offset](../patterns/paginacao-cursor-e-offset.md)
