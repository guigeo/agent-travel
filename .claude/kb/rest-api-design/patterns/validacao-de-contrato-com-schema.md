<!-- Prosa em português; código, nomes de API e keywords técnicas em inglês. Convenção: .claude/kb/_index.yaml -->
# Validação de entrada e contrato com schema

> **Propósito**: Validar request (e opcionalmente response) contra um schema declarado — em vez de validação ad-hoc espalhada nos handlers, que diverge silenciosamente da documentação.
> **Validado**: 2026-08-06 (OpenAPI 3.1 spec — schema via JSON Schema; Pydantic v2 docs; padrão de contract testing cross-stack)

## Quando usar

- Toda API pública deveria validar 100% do request body/query params na borda —
  nunca confiar que o client mandou o shape certo, mesmo com TypeScript/tipos no
  client (o wire format não tem tipo, só bytes).
- Contrato precisa ser a mesma fonte de verdade da documentação (OpenAPI/schema) —
  evita o schema documentado divergir do código real ao longo do tempo.
- Quando o consumidor é outro serviço (não humano) — erro de contrato deve falhar
  cedo e alto, não virar `null` silencioso propagado adiante.

## Implementação

```python
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator

# Schema de REQUEST — o que o client pode enviar
class CreateUserRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    age: int = Field(ge=0, le=150)

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        return v.strip()


# Schema de RESPONSE — separado do request; nunca reusar o mesmo model
# (response pode ter campos que o client não deveria poder setar, ex.: id, createdAt)
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime


# FastAPI valida request automaticamente contra o schema; 422 se falhar
# (ver problem-details-rfc9457.md para formatar esse 422 corretamente)
@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(body: CreateUserRequest) -> UserResponse:
    user = repo.create(name=body.name, email=body.email, age=body.age)
    return UserResponse.model_validate(user)


# Fora de um framework com validação automática: validar explicitamente na borda
def handle_create_user(raw_body: dict) -> UserResponse:
    request = CreateUserRequest.model_validate(raw_body)  # levanta ValidationError
    user = repo.create(name=request.name, email=request.email, age=request.age)
    return UserResponse.model_validate(user)
```

## Configuração

| Decisão | Padrão recomendado | Descrição |
|---------|--------------------|-----------|
| Schema de request vs response | Modelos separados, nunca o mesmo | Response pode expor campos (`id`, `createdAt`) que request não aceita como input |
| Onde validar | Na borda (antes de qualquer lógica de negócio) | Nunca deixar dado não validado alcançar a camada de persistência |
| Campo desconhecido no body | Rejeitar (`extra="forbid"` no Pydantic / `additionalProperties: false` no JSON Schema) | Silenciosamente ignorar campo extra esconde erro de integração do client |
| Fonte de verdade do contrato | Schema gera a doc (OpenAPI), não o contrário | Documentação escrita à mão diverge do código em poucas semanas |
| Erro de validação | 422 formatado como Problem Details, um item por campo | Ver [problem-details-rfc9457](problem-details-rfc9457.md) |

## Exemplo de uso

```http
POST /users
Content-Type: application/json

{"name": "", "email": "nao-e-email", "age": -5}

HTTP/1.1 422 Unprocessable Entity
Content-Type: application/problem+json

{"type": "https://api.exemplo.com/errors/validation-error",
 "title": "Validation failed", "status": 422,
 "errors": [
   {"field": "name", "detail": "min_length: 1"},
   {"field": "email", "detail": "not a valid email address"},
   {"field": "age", "detail": "must be >= 0"}
 ]}
```

## Ver também

- [problem-details-rfc9457](problem-details-rfc9457.md)
- [design-de-payloads-e-convencoes](../concepts/design-de-payloads-e-convencoes.md)
