<!-- Prosa em português; código, nomes de API e keywords técnicas em inglês. Convenção: .claude/kb/_index.yaml -->
# Formato de erro consistente com Problem Details (RFC 9457)

> **Propósito**: Devolver todo erro no mesmo formato JSON padronizado — em vez de cada endpoint inventar seu próprio schema de erro.
> **Validado**: 2026-08-06 (RFC 9457 Problem Details for HTTP APIs, julho/2023 — obsoleta a RFC 7807 mantendo o formato retrocompatível, com IANA registry e suporte a array de `errors`)

## Quando usar

- API pública ou consumida por times/clientes diferentes — um formato de erro
  único reduz o código de tratamento no client a uma única rotina.
- Middleware/framework tem um exception handler central (a maioria tem) — dá para
  aplicar globalmente sem tocar em cada endpoint individualmente.
- Quando o erro precisa carregar múltiplos problemas de uma vez (ex.: validação
  com vários campos inválidos) — RFC 9457 padroniza isso com um array `errors`.

## Implementação

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

app = FastAPI()

PROBLEM_TYPE_BASE = "https://api.exemplo.com/errors"


class ApiError(Exception):
    def __init__(self, status: int, title: str, detail: str, type_slug: str,
                 errors: list[dict] | None = None):
        self.status, self.title, self.detail = status, title, detail
        self.type_slug, self.errors = type_slug, errors


@app.exception_handler(ApiError)
async def handle_api_error(request: Request, exc: ApiError) -> JSONResponse:
    body = {
        "type": f"{PROBLEM_TYPE_BASE}/{exc.type_slug}",
        "title": exc.title,
        "status": exc.status,
        "detail": exc.detail,
        "instance": str(request.url.path),
    }
    if exc.errors:  # extensão RFC 9457: array de sub-problemas (ex.: validação multi-campo)
        body["errors"] = exc.errors
    return JSONResponse(status_code=exc.status, content=body,
                         media_type="application/problem+json")


# Handler global — captura erro de validação do próprio framework e reformata
@app.exception_handler(RequestValidationError)
async def handle_validation_error(request: Request, exc: RequestValidationError):
    errors = [{"field": ".".join(str(p) for p in e["loc"]), "detail": e["msg"]}
              for e in exc.errors()]
    return JSONResponse(status_code=422, media_type="application/problem+json", content={
        "type": f"{PROBLEM_TYPE_BASE}/validation-error",
        "title": "Validation failed", "status": 422,
        "detail": "Um ou mais campos são inválidos.",
        "instance": str(request.url.path), "errors": errors,
    })


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = repo.find(user_id)
    if user is None:
        raise ApiError(404, "User not found", f"Nenhum usuário com id={user_id}.",
                        type_slug="user-not-found")
    return user
```

## Configuração

| Campo | Obrigatório? | Descrição |
|-------|---------------|-----------|
| `type` | Recomendado | URI que identifica a classe do problema (não precisa resolver — é identificador) |
| `title` | Sim | Resumo curto e estável da classe de erro (não muda por instância) |
| `status` | Sim | Repete o HTTP status code — client não precisa ler o header para saber |
| `detail` | Recomendado | Explicação específica DESSA ocorrência (pode variar por instância) |
| `instance` | Opcional | URI/path da requisição que gerou o erro — ajuda em log/suporte |
| `errors[]` | Opcional (extensão RFC 9457) | Lista de sub-problemas, ex.: um item por campo inválido |
| `Content-Type` | Sim | `application/problem+json` — sinaliza ao client que é um Problem Details, não um payload comum |

## Exemplo de uso

```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/problem+json

{
  "type": "https://api.exemplo.com/errors/validation-error",
  "title": "Validation failed",
  "status": 422,
  "detail": "Um ou mais campos são inválidos.",
  "instance": "/users",
  "errors": [
    {"field": "email", "detail": "formato inválido"},
    {"field": "age", "detail": "deve ser >= 0"}
  ]
}
```

## Ver também

- [codigos-de-status-e-formato-de-erro](../concepts/codigos-de-status-e-formato-de-erro.md)
- [validacao-de-contrato-com-schema](validacao-de-contrato-com-schema.md)
