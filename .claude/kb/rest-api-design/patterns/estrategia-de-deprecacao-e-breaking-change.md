<!-- Prosa em português; código, nomes de API e keywords técnicas em inglês. Convenção: .claude/kb/_index.yaml -->
# Estratégia de deprecação e breaking change

> **Propósito**: Sinalizar deprecação com antecedência e rodar versões em paralelo por um período — para que remover uma versão nunca seja surpresa para o consumidor.
> **Validado**: 2026-08-06 (RFC 8594 Sunset HTTP Header; convenção Stripe API versioning por data; padrão GitHub API deprecation notices)

## Quando usar

- Antes de remover um campo, endpoint ou versão inteira de API pública — mesmo que
  o time interno "saiba" que ninguém mais usa (validar com telemetria, não achismo).
- Ao introduzir mudança que quebra contrato (remover campo, mudar tipo, mudar
  semântica de status code) — isso é breaking change e não cabe num patch.
- Quando múltiplas versões precisam coexistir por um tempo (rollout gradual de
  clientes) — decidir de antemão por quanto tempo e como isso é medido.

## Implementação

```python
from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

DEPRECATED_ROUTES = {
    "/v1/users": {
        "sunset": datetime(2027, 1, 31, 23, 59, 59, tzinfo=timezone.utc),
        "successor": "https://docs.exemplo.com/migracao-v1-para-v2",
    }
}


@app.middleware("http")
async def add_deprecation_headers(request: Request, call_next):
    response = await call_next(request)
    info = DEPRECATED_ROUTES.get(request.url.path)
    if info:
        # RFC 8594 — Sunset informa QUANDO a rota deixa de existir
        response.headers["Deprecation"] = "true"
        response.headers["Sunset"] = info["sunset"].strftime("%a, %d %b %Y %H:%M:%S GMT")
        response.headers["Link"] = f'<{info["successor"]}>; rel="deprecation"'
    return response


# Breaking change real (não é add de campo opcional): nova versão paralela,
# v1 nunca muda de comportamento até o Sunset — só recebe headers de aviso.
@app.get("/v1/users/{user_id}")
async def get_user_v1(user_id: int):
    user = repo.find(user_id)
    return {"id": user.id, "name": user.name}  # formato antigo, mantido intacto


@app.get("/v2/users/{user_id}")
async def get_user_v2(user_id: int):
    user = repo.find(user_id)
    return {"id": user.id, "fullName": user.name, "email": user.email}  # novo shape
```

## Configuração

| Decisão | Padrão recomendado | Descrição |
|---------|--------------------|-----------|
| O que é breaking change | Remover/renomear campo, mudar tipo, mudar status code, mudar semântica de um verbo | Adicionar campo opcional NÃO é breaking — client antigo ignora o que não conhece |
| Janela de aviso | Mínimo 90 dias entre `Deprecation: true` e remoção real | Prazo curto o suficiente para não travar evolução, longo o suficiente para migração |
| Sinalização | Headers `Deprecation` + `Sunset` (RFC 8594) em toda resposta da rota antiga | Client pode monitorar o header e alertar automaticamente, sem ler changelog |
| Coexistência de versões | Versão antiga congelada — nenhuma mudança de comportamento até o Sunset | Mudar a v1 "por baixo" quebra a garantia que versionamento existe para dar |
| Validação de uso real | Métrica de tráfego por versão antes de remover | "Ninguém usa mais" precisa ser dado, não suposição |

## Exemplo de uso

```http
GET /v1/users/42

HTTP/1.1 200 OK
Deprecation: true
Sunset: Sun, 31 Jan 2027 23:59:59 GMT
Link: <https://docs.exemplo.com/migracao-v1-para-v2>; rel="deprecation"

{"id": 42, "name": "Ana"}
```

## Ver também

- [versionamento-de-api](../concepts/versionamento-de-api.md)
- [codigos-de-status-e-formato-de-erro](../concepts/codigos-de-status-e-formato-de-erro.md)
