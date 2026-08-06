<!-- Prosa em português; código, nomes de API e keywords técnicas em inglês. Convenção: .claude/kb/_index.yaml -->
# Modelagem de recursos e verbos HTTP

> **Propósito**: Mapear o domínio em recursos (substantivos) e usar os verbos HTTP com a semântica correta — sobretudo idempotência — em vez de reinventar convenções a cada rota.
> **Confiança**: 0.95
> **Validado**: 2026-08-06 (RFC 9110 HTTP Semantics; Microsoft REST API Guidelines; Google API Design Guide; Zalando RESTful API Guidelines)

## Visão geral

Uma API REST bem modelada nomeia rotas como **substantivos no plural** (`/users`,
`/orders`), nunca como verbos (`/getUsers`, `/createOrder`) — a ação já está no
verbo HTTP. Recursos aninhados expressam posse/hierarquia (`/users/{id}/orders`).
A parte que mais gera bug em produção não é nomenclatura, é **idempotência**: um
cliente que reenvia a mesma requisição (timeout, retry automático) precisa de uma
garantia clara sobre se isso é seguro. `GET`, `PUT`, `DELETE` são idempotentes por
definição do protocolo; `POST` não é; `PATCH` só é se o servidor implementar como
merge determinístico.

## O padrão

```http
GET    /users              # listar coleção (safe + idempotent)
GET    /users/{id}         # obter um recurso (safe + idempotent)
POST   /users               # criar recurso — NÃO idempotente (repetir cria outro)
PUT    /users/{id}         # substituir o recurso INTEIRO — idempotente
PATCH  /users/{id}         # atualizar parcialmente — idempotente só se o merge
                            # for determinístico (evitar operações tipo "increment")
DELETE /users/{id}         # remover — idempotente (repetir dá 404, não erro novo)

# Recursos aninhados expressam hierarquia/posse
GET  /users/{id}/orders    # pedidos DESSE usuário

# Ação sem mapeamento CRUD direto: sub-recurso "verbo", exceção aceita
POST /orders/{id}/cancel   # preferível a inventar um verbo HTTP novo
```

## Referência rápida

| Verbo | Idempotente? | Uso correto |
|-------|---------------|-------------|
| `GET` | Sim | Leitura, sem side effects (safe) |
| `POST` | Não | Criar recurso novo, ou ação sem verbo CRUD equivalente |
| `PUT` | Sim | Substituição completa — cliente envia o objeto inteiro |
| `PATCH` | Depende da implementação | Atualização parcial — só idempotente com merge determinístico |
| `DELETE` | Sim | Remoção — repetir a chamada não deve gerar erro novo |

## Erros comuns

### Errado

```http
POST /users/{id}/update     # verbo na URL, e usa POST para operação idempotente
GET  /users/{id}/delete     # side effect num verbo "safe" — quebra cache/prefetch
```

### Certo

```http
PATCH  /users/{id}          # verbo HTTP já expressa "update parcial"
DELETE /users/{id}          # verbo HTTP já expressa "remover"
```

## Relacionados

- [codigos-de-status-e-formato-de-erro](codigos-de-status-e-formato-de-erro.md)
- [design-de-payloads-e-convencoes](design-de-payloads-e-convencoes.md)
- [validacao-de-contrato-com-schema](../patterns/validacao-de-contrato-com-schema.md)
