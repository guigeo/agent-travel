<!-- Prosa em português; código, nomes de API e keywords técnicas em inglês. Convenção: .claude/kb/_index.yaml -->
# Refresh token com rotação e detecção de reuso

> **Propósito**: Manter access tokens de vida curta (baixo dano se vazarem) sem forçar login constante, usando um refresh token de vida longa que é rotacionado a cada uso e revogado por completo se reusado (indício de roubo).
> **Validado**: 2026-08-06 (OAuth 2.0 Security Best Current Practice — RFC 9700; OWASP JSON Web Token Cheat Sheet)

## Quando usar

- Sempre que o access token for um JWT stateless (ver
  [jwt-estrutura-e-ciclo-de-vida](../concepts/jwt-estrutura-e-ciclo-de-vida.md)) — a
  rotação é o que permite revogar acesso de fato antes do `exp` do refresh.
- SPA, app mobile ou qualquer client que precisa manter sessão ativa por
  período longo (horas/dias) sem reautenticar o usuário a cada poucos minutos.
- Cenários que exigem **detecção de roubo de token**: se um refresh token já
  usado (e portanto invalidado) aparecer numa nova requisição, é sinal de que
  um atacante também o possui — a resposta correta é revogar toda a família
  de tokens daquela sessão, não só o token isolado.

## Implementação

```python
import hashlib
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

@dataclass
class RefreshTokenRecord:
    token_hash: str       # nunca armazenar o refresh token em texto puro
    family_id: str        # agrupa todos os tokens derivados de um mesmo login
    user_id: str
    expires_at: datetime
    revoked: bool = False

def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def issue_refresh_token(store, user_id: str, family_id: str | None = None) -> str:
    family_id = family_id or secrets.token_urlsafe(16)
    raw_token = secrets.token_urlsafe(32)
    store.save(RefreshTokenRecord(
        token_hash=_hash(raw_token),
        family_id=family_id,
        user_id=user_id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=14),
    ))
    return raw_token

def refresh_session(store, presented_token: str) -> tuple[str, str] | None:
    record = store.find_by_hash(_hash(presented_token))

    if record is None or record.expires_at < datetime.now(timezone.utc):
        return None  # não existe ou expirou — força novo login

    if record.revoked:
        # REUSO DETECTADO: token já havia sido trocado por um novo antes.
        # Alguém mais possui uma cópia — revoga toda a família imediatamente.
        store.revoke_family(record.family_id)
        return None

    # rotação: o token apresentado é consumido (revogado) e um novo é emitido
    store.revoke(record)
    new_refresh = issue_refresh_token(store, record.user_id, record.family_id)
    new_access = issue_access_token(record.user_id, scopes=[])  # ver jwt-estrutura
    return new_access, new_refresh
```

## Configuração

| Decisão | Padrão recomendado | Descrição |
|---------|--------------------|-----------|
| Vida do access token | 5–15 minutos | Curta o bastante para limitar o dano de um vazamento |
| Vida do refresh token | 7–30 dias | Renovado a cada rotação — sessão "desliza" enquanto o usuário está ativo |
| Rotação | A cada uso, sem exceção | Refresh token é single-use; reusar é sinal de comprometimento |
| Armazenamento server-side | Hash do token (nunca o valor puro) | Mesmo princípio de senha — vazamento do DB não expõe tokens válidos |
| Reuso detectado | Revogar toda a `family_id` | Um único token comprometido não deve exigir rastrear todos os descendentes manualmente |
| Transporte do refresh token | Cookie `HttpOnly` + `Secure` + `SameSite` | Ver [armazenamento-seguro-de-token-no-cliente](armazenamento-seguro-de-token-no-cliente.md) |

## Exemplo de uso

```http
POST /auth/refresh
Cookie: refresh_token=<opaco, HttpOnly>

HTTP/1.1 200 OK
Set-Cookie: refresh_token=<novo-token>; HttpOnly; Secure; SameSite=Strict
{"accessToken": "eyJ..."}

# reuso do token antigo (já rotacionado) — família inteira revogada
POST /auth/refresh
Cookie: refresh_token=<token-ja-consumido>

HTTP/1.1 401 Unauthorized
```

## Ver também

- [armazenamento-seguro-de-token-no-cliente](armazenamento-seguro-de-token-no-cliente.md)
- [jwt-estrutura-e-ciclo-de-vida](../concepts/jwt-estrutura-e-ciclo-de-vida.md)
