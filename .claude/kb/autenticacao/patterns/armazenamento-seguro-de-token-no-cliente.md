<!-- Prosa em português; código, nomes de API e keywords técnicas em inglês. Convenção: .claude/kb/_index.yaml -->
# Armazenamento seguro de token no cliente (browser)

> **Propósito**: Evitar que um XSS roube o token de sessão, mantendo o access token só em memória e o refresh token num cookie `HttpOnly` — com defesa CSRF para compensar o envio automático do cookie.
> **Validado**: 2026-08-06 (OWASP HTML5 Security Cheat Sheet; OAuth 2.0 for Browser-Based Apps; OWASP Session Management Cheat Sheet)

## Quando usar

- Qualquer SPA/app browser-based que hoje guarda o token em `localStorage`
  ou `sessionStorage` — ambos são legíveis por **qualquer** JavaScript
  rodando na página, então um único XSS (dependência comprometida, script de
  terceiro, falha própria) exfiltra o token inteiro.
- Aplicação que controla o próprio backend e pode servir front-end e API do
  mesmo domínio (ou domínio irmão) — é o cenário onde cookie `HttpOnly`
  funciona melhor, sem a complexidade extra de `SameSite=None` cross-site.
- Sempre que o refresh token (vida longa, ver
  [refresh-token-rotation](refresh-token-rotation.md)) precisa persistir entre
  recarregamentos de página sem ficar exposto a script.

## Implementação

```javascript
// --- Backend (Express) — só o servidor pode setar cookie HttpOnly ---
app.post('/auth/login', async (req, res) => {
  const user = await authenticate(req.body.email, req.body.password);
  const { accessToken, refreshToken } = issueTokenPair(user);

  res.cookie('refresh_token', refreshToken, {
    httpOnly: true,          // invisível para JavaScript — XSS não consegue ler
    secure: true,             // só trafega em HTTPS
    sameSite: 'strict',       // não enviado em requisição cross-site — mitiga CSRF
    maxAge: 14 * 24 * 60 * 60 * 1000,
    path: '/auth/refresh',    // escopo mínimo: só o endpoint de refresh recebe o cookie
  });

  res.json({ accessToken }); // access token vai no corpo, não em cookie
});

// --- Frontend (SPA) — access token SÓ em memória, nunca em storage persistente ---
let accessTokenInMemory = null;

async function login(email, password) {
  const res = await fetch('/auth/login', {
    method: 'POST',
    credentials: 'include',      // envia/recebe o cookie HttpOnly
    body: JSON.stringify({ email, password }),
  });
  const { accessToken } = await res.json();
  accessTokenInMemory = accessToken;   // variável de módulo — some ao recarregar a página
}

async function callApi(path) {
  let res = await fetch(path, {
    headers: { Authorization: `Bearer ${accessTokenInMemory}` },
  });
  if (res.status === 401) {
    // access token expirado — usa o refresh token (cookie, automático) para renovar
    const refreshRes = await fetch('/auth/refresh', { method: 'POST', credentials: 'include' });
    if (!refreshRes.ok) throw new Error('sessão expirada — refazer login');
    ({ accessToken: accessTokenInMemory } = await refreshRes.json());
    res = await fetch(path, { headers: { Authorization: `Bearer ${accessTokenInMemory}` } });
  }
  return res;
}
```

## Configuração

| Decisão | Padrão recomendado | Descrição |
|---------|--------------------|-----------|
| Access token | Memória (variável JS), nunca `localStorage`/`sessionStorage` | Some ao fechar a aba/recarregar — janela de exposição a XSS é o tempo de vida do token (minutos) |
| Refresh token | Cookie `HttpOnly` + `Secure` + `SameSite=Strict` (ou `Lax`) | Invisível a `document.cookie`/JS — XSS não consegue exfiltrar |
| `SameSite` | `Strict` por padrão; `Lax` se precisar sobreviver a navegação top-level cross-site | Nunca deixar implícito — bloqueia a maior parte do CSRF |
| `path` do cookie | Restrito ao endpoint de refresh (ex.: `/auth/refresh`) | Reduz a superfície de envio automático do cookie |
| Defesa CSRF adicional | Token CSRF (double-submit) em endpoints sensíveis de mudança de estado | `SameSite` cobre a maioria dos casos, mas defesa em profundidade vale para ações críticas |
| API cross-domain (front e API em domínios diferentes) | `SameSite=None; Secure` + CORS com `credentials` explícito | Configuração mais frágil — preferir mesmo domínio/subdomínio quando possível |

## Exemplo de uso

```http
POST /auth/login
{"email": "user@exemplo.com", "password": "..."}

HTTP/1.1 200 OK
Set-Cookie: refresh_token=<opaco>; HttpOnly; Secure; SameSite=Strict; Path=/auth/refresh
{"accessToken": "eyJ..."}

# chamada subsequente à API usa o access token em memória, no header
GET /orders
Authorization: Bearer eyJ...
```

## Ver também

- [refresh-token-rotation](refresh-token-rotation.md)
- [jwt-estrutura-e-ciclo-de-vida](../concepts/jwt-estrutura-e-ciclo-de-vida.md)
