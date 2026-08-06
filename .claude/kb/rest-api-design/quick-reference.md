# REST API Design Quick Reference

> Fast lookup tables. For code examples, see linked files.

## Verbos HTTP e idempotência

| Verbo | Idempotente? | Uso |
|-------|---------------|-----|
| `GET` | Sim | Leitura, sem side effects |
| `POST` | Não | Criar recurso, ou ação sem verbo CRUD equivalente |
| `PUT` | Sim | Substituição completa do recurso |
| `PATCH` | Depende | Update parcial — idempotente só com merge determinístico |
| `DELETE` | Sim | Remoção — repetir não deve gerar erro novo |

## Status codes mais usados

| Situação | Status |
|----------|--------|
| Leitura/update bem-sucedida com corpo | `200 OK` |
| Criação bem-sucedida | `201 Created` |
| Sucesso sem corpo (ex.: `DELETE`) | `204 No Content` |
| JSON malformado / tipo errado | `400 Bad Request` |
| Sem autenticação válida | `401 Unauthorized` |
| Autenticado, sem permissão | `403 Forbidden` |
| Recurso não existe | `404 Not Found` |
| Conflito de estado (ex.: versão desatualizada) | `409 Conflict` |
| Sintaxe OK, validação semântica falhou | `422 Unprocessable Entity` |
| Rate limit excedido | `429 Too Many Requests` |
| Exceção não tratada | `500 Internal Server Error` |

## Decision Matrix — versionamento

| Use Case | Choose |
|----------|--------|
| API pública, quer cache HTTP nativo | URL path (`/v1/...`) |
| API interna service-to-service, URL limpa | Header (`X-API-Version`) |
| Mudanças frequentes e pequenas, sem "big bang" de major | Versionamento por data (estilo Stripe) |

## Decision Matrix — paginação

| Use Case | Choose |
|----------|--------|
| Dataset grande, escrita concorrente, precisa de performance estável | Cursor-based |
| Dataset pequeno/estático, UI precisa pular para página N | Offset-based |
| Qualquer coleção pública em escala | Cursor-based por padrão |

## Common Pitfalls

| Don't | Do |
|-------|-----|
| Verbo na URL (`/getUsers`, `POST /users/{id}/update`) | Substantivo + verbo HTTP correto (`GET /users`, `PATCH /users/{id}`) |
| Sempre `200 OK` com `{"success": false}` no corpo | Status code correto + corpo Problem Details (RFC 9457) |
| `500` para erro de validação de campo | `422` com detalhe do campo inválido |
| Misturar `camelCase` e `snake_case` no mesmo payload | Uma convenção só, documentada, sem exceção |
| Coleção sem paginação ("retorna tudo") | `limit` com teto obrigatório + cursor/offset desde o início |
| `OFFSET` alto em dataset grande sem medir performance | Cursor-based com tiebreaker único no `ORDER BY` |
| Misturar estratégia de versionamento entre endpoints | Uma estratégia única para toda a API pública |
| Remover rota/campo sem aviso prévio | Headers `Deprecation` + `Sunset` (RFC 8594), janela mínima de 90 dias |

## Related Documentation

| Topic | Path |
|-------|------|
| Getting Started | `concepts/modelagem-de-recursos-e-verbos-http.md` |
| Full Index | `index.md` |
