<!-- Prosa em português; código, nomes de API e keywords técnicas em inglês. Convenção: .claude/kb/_index.yaml -->
# Authorization Code Flow com PKCE

> **Propósito**: Autenticar o usuário via um Identity Provider externo (Google, Auth0, Keycloak, etc.) usando o fluxo obrigatório desde a RFC 9700 — sem expor client secret em um client público (SPA/mobile).
> **Validado**: 2026-08-06 (RFC 7636 Proof Key for Code Exchange; RFC 9700 OAuth 2.0 Security Best Current Practice, jan/2025; OpenID Connect Core 1.0)

## Quando usar

- SPA, app mobile ou qualquer client **público** (não consegue guardar um
  client secret com segurança) que precisa de login via OAuth2/OIDC — PKCE é
  obrigatório nesse caso pela RFC 9700.
- Também recomendado para clients **confidenciais** (backend tradicional com
  client secret): o PKCE previne authorization code injection e, como efeito
  colateral, já cobre a proteção CSRF do fluxo — dispensa gerenciar `state`
  manualmente para esse fim.
- Sempre que o fluxo anterior era *implicit* (`response_type=token`) — esse
  fluxo está deprecado e deve ser migrado.

## Implementação

```python
import base64
import hashlib
import secrets
from urllib.parse import urlencode

AUTH_ENDPOINT = "https://idp.exemplo.com/authorize"
TOKEN_ENDPOINT = "https://idp.exemplo.com/token"
CLIENT_ID = "meu-client-publico"
REDIRECT_URI = "https://app.exemplo.com/callback"


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def start_login() -> tuple[str, str, str]:
    # code_verifier: segredo gerado pelo próprio client, nunca sai do dispositivo
    code_verifier = _b64url(secrets.token_bytes(32))
    # code_challenge: derivado do verifier — é isso que trafega na URL de authorize
    code_challenge = _b64url(hashlib.sha256(code_verifier.encode()).digest())
    state = secrets.token_urlsafe(16)  # defesa extra além do PKCE (RFC 9700 §4.7.1)

    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",   # único método que não expõe o verifier
        "state": state,
        "scope": "openid profile email",
    }
    authorize_url = f"{AUTH_ENDPOINT}?{urlencode(params)}"
    # code_verifier e state precisam ser guardados no client (ex.: sessionStorage
    # do navegador) até o callback chegar — NUNCA no code_challenge/URL
    return authorize_url, code_verifier, state


def handle_callback(received_code: str, received_state: str,
                     expected_state: str, code_verifier: str) -> dict:
    if received_state != expected_state:
        raise ValueError("state inválido — possível CSRF no redirect")

    response = http_post(TOKEN_ENDPOINT, data={
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "code": received_code,
        "redirect_uri": REDIRECT_URI,
        "code_verifier": code_verifier,   # servidor recalcula o hash e compara
    })
    return response.json()  # { access_token, id_token, refresh_token, ... }
```

## Configuração

| Decisão | Padrão recomendado | Descrição |
|---------|--------------------|-----------|
| `code_challenge_method` | `S256` | Único método que não expõe o `code_verifier` na URL (RFC 9700) |
| `code_verifier` | Random ≥ 32 bytes, gerado por requisição de login | Nunca reusar entre logins — é o segredo que prova posse do fluxo |
| `state` | Random único, validado no callback | Defesa adicional a CSRF mesmo com PKCE presente |
| `nonce` (se OIDC) | Random único, validado dentro do `id_token` | Protege contra injeção de authorization code em fluxos OIDC |
| `redirect_uri` | Exact match contra o valor pré-registrado no IdP | Comparação por prefixo/wildcard é vetor de ataque conhecido |
| Client secret | Nenhum, para client público | PKCE substitui a necessidade de client secret nesse tipo de client |

## Exemplo de uso

```http
GET /authorize?response_type=code&client_id=meu-client&redirect_uri=https%3A%2F%2Fapp.exemplo.com%2Fcallback
    &code_challenge=E9Melhorix...&code_challenge_method=S256&state=xyz789&scope=openid+profile

# usuário autentica no IdP → redirect de volta:
GET https://app.exemplo.com/callback?code=SplxlOBe...&state=xyz789

POST /token
{"grant_type": "authorization_code", "code": "SplxlOBe...",
 "code_verifier": "dBjftJeZ4CVP...", "redirect_uri": "https://app.exemplo.com/callback"}

HTTP/1.1 200 OK
{"access_token": "eyJ...", "id_token": "eyJ...", "refresh_token": "...", "expires_in": 600}
```

## Ver também

- [oauth2-e-openid-connect](../concepts/oauth2-e-openid-connect.md)
- [jwt-estrutura-e-ciclo-de-vida](../concepts/jwt-estrutura-e-ciclo-de-vida.md)
