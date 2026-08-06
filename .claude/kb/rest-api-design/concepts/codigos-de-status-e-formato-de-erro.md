<!-- Prosa em português; código, nomes de API e keywords técnicas em inglês. Convenção: .claude/kb/_index.yaml -->
# Códigos de status HTTP e formato de erro consistente

> **Propósito**: Usar a família de status code correta para cada situação e devolver erros num formato previsível — em vez de sempre `200 OK` com `{"success": false}` no corpo.
> **Confiança**: 0.95
> **Validado**: 2026-08-06 (RFC 9110 HTTP Semantics; RFC 9457 Problem Details for HTTP APIs — obsoleta a RFC 7807 desde 2023, mantendo o formato compatível)

## Visão geral

Status code é protocolo, não decoração: proxies, CDNs, retry logic de HTTP client e
monitoring dependem dele para decidir o que fazer (cachear, re-tentar, alertar).
Retornar sempre `200` e empurrar o erro para dentro do JSON quebra tudo isso. As
quatro famílias relevantes para API são `2xx` (sucesso), `4xx` (erro do cliente —
não re-tentar sem mudar a requisição) e `5xx` (erro do servidor — pode re-tentar).
Para o **corpo** do erro, a convenção madura é RFC 9457 *Problem Details*: um
formato JSON padronizado (`type`, `title`, `status`, `detail`, `instance`) que
qualquer client HTTP genérico sabe interpretar, em vez de um schema de erro
inventado por cada API. Implementação completa em
[problem-details-rfc9457](../patterns/problem-details-rfc9457.md).

## O padrão

```text
2xx — sucesso
  200 OK              resposta com corpo (GET, PUT, PATCH bem-sucedidos)
  201 Created         POST que criou recurso — inclua header Location
  202 Accepted        aceito para processamento assíncrono (ainda não concluído)
  204 No Content       sucesso sem corpo (DELETE, PUT sem retorno)

4xx — erro do cliente (requisição precisa mudar para funcionar)
  400 Bad Request      sintaxe/formato inválido (JSON malformado, tipo errado)
  401 Unauthorized     sem autenticação válida (não confundir com 403)
  403 Forbidden        autenticado, mas sem permissão para o recurso
  404 Not Found        recurso não existe (ou o cliente não pode saber que existe)
  409 Conflict         estado atual do recurso conflita com a operação (ex.: versão desatualizada)
  422 Unprocessable    sintaxe válida, mas falha de validação semântica (campo obrigatório ausente)
  429 Too Many Requests rate limit excedido — inclua header Retry-After

5xx — erro do servidor (cliente pode re-tentar, idealmente com backoff)
  500 Internal Server Error  falha não tratada — nunca vaze stack trace no corpo
  503 Service Unavailable    indisponibilidade temporária — inclua Retry-After
```

## Referência rápida

| Entrada | Saída | Notas |
|---------|-------|-------|
| Campo obrigatório ausente no body | `422` | Não `400` — sintaxe do JSON está OK, é a semântica que falha |
| Token ausente/expirado | `401` | Cliente pode corrigir reautenticando |
| Token válido, sem permissão no recurso | `403` | Reautenticar não resolve — não confundir com `401` |
| `PUT` numa versão desatualizada do recurso (optimistic lock) | `409` | Cliente precisa buscar o estado atual antes de re-tentar |
| Exceção não tratada no handler | `500` | Nunca exponha stack trace/SQL no corpo da resposta |

## Erros comuns

### Errado

```json
HTTP/1.1 200 OK
{"success": false, "error": "user not found"}
```

### Certo

```json
HTTP/1.1 404 Not Found
Content-Type: application/problem+json

{"type": "https://api.exemplo.com/errors/user-not-found",
 "title": "User not found", "status": 404,
 "detail": "Nenhum usuário com id=42."}
```

## Relacionados

- [modelagem-de-recursos-e-verbos-http](modelagem-de-recursos-e-verbos-http.md)
- [problem-details-rfc9457](../patterns/problem-details-rfc9457.md)
- [versionamento-de-api](versionamento-de-api.md)
