<!-- Prosa em português; código, nomes de API e keywords técnicas em inglês. Convenção: .claude/kb/_index.yaml -->
# Estrutura e ciclo de vida do JWT

> **Propósito**: Entender a anatomia de um JWT (`header.payload.signature`), validar assinatura e expiração corretamente, e projetar o par access token + refresh token sem reinventar riscos de segurança conhecidos.
> **Confiança**: 0.95
> **Validado**: 2026-08-06 (RFC 7519 JSON Web Token; RFC 7518 JSON Web Algorithms; OWASP JSON Web Token Cheat Sheet)

## Visão geral

Um JWT é um token **auto-contido**: três partes em Base64URL separadas por ponto —
`header` (algoritmo de assinatura e tipo), `payload` (claims) e `signature`. A
assinatura garante **integridade** (o token não foi alterado), não
**confidencialidade** — o payload é apenas codificado, não criptografado, e
qualquer um pode decodificá-lo. Nunca colocar dado sensível (senha, PII
desnecessária, segredo) no payload. A assinatura pode ser simétrica (`HS256` —
mesma chave assina e valida, só faz sentido quando um único serviço controla
ambos os lados) ou assimétrica (`RS256`/`ES256` — chave privada assina, chave
pública valida, permite múltiplos serviços validarem o token sem conhecer o
segredo que o emitiu). Validar um JWT sempre significa: checar assinatura
primeiro, depois `exp` (expiração) e, se presentes, `nbf`/`iss`/`aud` — nunca
usar os claims antes de validar a assinatura.

## O padrão

```python
import jwt  # PyJWT
from datetime import datetime, timedelta, timezone

SECRET = "chave-de-ao-menos-256-bits"  # em produção: vault/secret manager
ALGORITHM = "HS256"

def issue_access_token(user_id: str, scopes: list[str]) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,                          # subject — quem é o token
        "scope": " ".join(scopes),
        "iat": now,                              # issued at
        "exp": now + timedelta(minutes=10),      # access token: vida curta
        "jti": generate_unique_id(),             # id único — suporta blocklist
    }
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)

def verify_access_token(token: str) -> dict:
    # algorithms= é EXPLÍCITO — nunca aceitar o alg vindo do header do token
    return jwt.decode(token, SECRET, algorithms=[ALGORITHM])
```

## Referência rápida

| Claim | Significado | Notas |
|-------|-------------|-------|
| `sub` | Subject — identifica o usuário/entidade | Nunca use PII legível como e-mail; prefira id opaco |
| `iss` | Issuer — quem emitiu o token | Validar contra o emissor esperado em ambientes multi-tenant |
| `aud` | Audience — para qual serviço o token vale | Rejeitar token emitido para outra API (evita replay entre serviços) |
| `exp` | Expiration — timestamp de expiração | Access token: 5–15 min; nunca "sem expiração" |
| `jti` | JWT ID — identificador único do token | Necessário para blocklist/revogação individual |
| `HS256` vs `RS256` | Simétrico vs assimétrico | `RS256` quando múltiplos serviços validam sem confiar uns nos outros |

## Erros comuns

### Errado

```python
# decodifica sem especificar algoritmo permitido — vulnerável a "alg confusion"
# (atacante troca header para alg="none" ou HS256 usando a chave pública como segredo)
payload = jwt.decode(token, options={"verify_signature": False})
```

### Certo

```python
# algoritmo fixado explicitamente; assinatura sempre validada
payload = jwt.decode(token, SECRET, algorithms=["HS256"])
```

## Relacionados

- [oauth2-e-openid-connect](oauth2-e-openid-connect.md)
- [refresh-token-rotation](../patterns/refresh-token-rotation.md)
- [armazenamento-seguro-de-token-no-cliente](../patterns/armazenamento-seguro-de-token-no-cliente.md)
