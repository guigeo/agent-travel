<!-- Prosa em português; código, nomes de API e keywords técnicas em inglês. Convenção: .claude/kb/_index.yaml -->
# Paginação, filtragem e ordenação de coleções

> **Propósito**: Paginar toda coleção potencialmente grande, com cursor-based pagination por padrão e offset como exceção documentada — nunca devolver a coleção inteira sem limite.
> **Validado**: 2026-08-06 (Zalando RESTful API Guidelines — pagination; Speakeasy API Design pagination guide; padrão observado em Stripe/GitHub/Twitter API)

## Quando usar

- Qualquer endpoint de coleção que pode crescer além de algumas centenas de itens
  — aplica mesmo que hoje a tabela tenha poucos registros.
- Dataset grande, com escrita concorrente (inserts/deletes durante a paginação) ou
  necessidade de performance estável em profundidade: **cursor-based**.
- Dataset pequeno/estático, ou UI que precisa de "pular para a página 37": **offset**
  é aceitável — documentar a degradação de performance em offsets altos.

## Implementação

```python
import base64
import json
from dataclasses import dataclass


@dataclass
class Page:
    items: list
    next_cursor: str | None


def encode_cursor(created_at: str, id_: int) -> str:
    # cursor opaco: cliente nunca deve inspecionar ou construir o valor
    payload = json.dumps({"created_at": created_at, "id": id_}).encode()
    return base64.urlsafe_b64encode(payload).decode()


def decode_cursor(cursor: str) -> dict:
    return json.loads(base64.urlsafe_b64decode(cursor))


def list_orders(db, cursor: str | None = None, limit: int = 20) -> Page:
    limit = min(limit, 100)  # teto obrigatório — nunca confiar só no limit do client

    # ORDER BY sempre com tiebreaker único (id) — evita duplicata/gap sob escrita concorrente
    query = "SELECT * FROM orders ORDER BY created_at DESC, id DESC"
    params = []
    if cursor:
        pos = decode_cursor(cursor)
        query = (
            "SELECT * FROM orders "
            "WHERE (created_at, id) < (%s, %s) "
            "ORDER BY created_at DESC, id DESC"
        )
        params = [pos["created_at"], pos["id"]]

    # busca limit+1 para saber se há próxima página sem um COUNT(*) separado
    rows = db.execute(f"{query} LIMIT %s", [*params, limit + 1]).fetchall()
    has_more = len(rows) > limit
    items = rows[:limit]

    next_cursor = (
        encode_cursor(items[-1]["created_at"], items[-1]["id"])
        if has_more else None
    )
    return Page(items=items, next_cursor=next_cursor)
```

## Configuração

| Decisão | Padrão recomendado | Descrição |
|---------|--------------------|-----------|
| Estratégia default | Cursor-based | Offset custa `O(offset + limit)`; cursor custa `O(limit)` com índice adequado |
| `limit` (page size) | Default 20-50, teto 100 | Nunca aceitar `limit` ilimitado vindo do client |
| Tiebreaker no `ORDER BY` | Chave única e imutável (`id`) além do campo de ordenação | Sem tiebreaker único, escritas concorrentes geram duplicata/gap entre páginas |
| Cursor | Opaco (base64 de JSON/hash), nunca inspecionável pelo client | Permite trocar a implementação sem quebrar contrato |
| Total count | Omitir, ou endpoint separado/aproximado | `COUNT(*)` exato é caro em tabela grande e raramente necessário |
| Filtragem/ordenação | Query params (`?status=active&sort=-created_at`) | `-` prefixo = ordem descendente; documentar campos filtráveis/ordenáveis permitidos |

## Exemplo de uso

```http
GET /orders?status=active&sort=-created_at&limit=20
GET /orders?status=active&sort=-created_at&limit=20&cursor=eyJjcmVhdGVkX2F0IjoiMjAyNi0wOC0wNiJ9

HTTP/1.1 200 OK
{"data": [...], "meta": {"nextCursor": "eyJjcmVhdGVkX2F0Ijo...", "hasMore": true}}
```

## Ver também

- [design-de-payloads-e-convencoes](../concepts/design-de-payloads-e-convencoes.md)
- [modelagem-de-recursos-e-verbos-http](../concepts/modelagem-de-recursos-e-verbos-http.md)
