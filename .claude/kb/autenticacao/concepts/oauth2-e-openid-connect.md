<!-- Prosa em português; código, nomes de API e keywords técnicas em inglês. Convenção: .claude/kb/_index.yaml -->
# OAuth2 e OpenID Connect — fluxos e quando usar cada um

> **Propósito**: Escolher o fluxo OAuth2 correto (authorization code + PKCE vs client credentials) e entender o que o OpenID Connect adiciona sobre o OAuth2 puro.
> **Confiança**: 0.95
> **Validado**: 2026-08-06 (RFC 6749 OAuth 2.0; RFC 9700 OAuth 2.0 Security Best Current Practice, jan/2025; RFC 7636 PKCE; OpenID Connect Core 1.0)

## Visão geral

OAuth2 é um protocolo de **autorização**: delega acesso a um recurso sem
compartilhar a credencial original. OpenID Connect (OIDC) é uma camada de
**identidade** construída sobre o OAuth2 — adiciona o `ID Token` (um JWT com
claims do usuário autenticado, ex.: `email`, `name`) e o endpoint `/userinfo`.
Se a aplicação só precisa saber "quem é o usuário", é OIDC; se precisa "acessar
um recurso em nome do usuário", é OAuth2. A RFC 9700 (2025) formalizou o que a
comunidade já recomendava: o fluxo *implicit* e o *resource owner password
credentials* estão deprecados — **authorization code + PKCE é obrigatório**
para clients públicos (SPA, mobile) e recomendado até para clients
confidenciais, porque o PKCE previne CSRF e authorization code injection como
efeito colateral. *Client credentials* é o fluxo para comunicação
machine-to-machine, sem usuário envolvido.

## O padrão

```text
Authorization Code + PKCE (usuário interativo — web app, SPA, mobile)
  1. Client gera code_verifier (random) e code_challenge = SHA256(code_verifier)
  2. Client redireciona usuário para o Authorization Server com code_challenge
  3. Usuário autentica e consente; Authorization Server redireciona de volta
     com um authorization code (short-lived, single-use)
  4. Client troca o code + code_verifier pelo access token (e ID token, se OIDC)
     no Token Endpoint — servidor valida que code_verifier bate com o challenge

Client Credentials (machine-to-machine, sem usuário)
  1. Client autentica direto no Token Endpoint com client_id + client_secret
  2. Recebe access token com o escopo do PRÓPRIO client (não de um usuário)
```

## Referência rápida

| Fluxo | Quando usar | Status |
|-------|-------------|--------|
| Authorization Code + PKCE | Usuário interativo, qualquer client (público ou confidencial) | Recomendado — obrigatório para clients públicos |
| Client Credentials | Serviço-a-serviço, sem usuário | Recomendado |
| Implicit | — | Deprecado (RFC 9700) — token exposto na URL, sem proteção contra interceptação |
| Resource Owner Password Credentials | — | Deprecado (RFC 9700) — expõe a senha do usuário ao client |
| OIDC (`ID Token` + `/userinfo`) | Aplicação precisa saber "quem é" o usuário | Camada sobre OAuth2, não substitui |

## Erros comuns

### Errado

```text
GET /authorize?response_type=token&client_id=...   # implicit flow — token na URL,
                                                     # sem code_verifier, deprecado
```

### Certo

```text
GET /authorize?response_type=code&client_id=...&code_challenge=...&code_challenge_method=S256
POST /token  { grant_type: authorization_code, code: ..., code_verifier: ... }
```

## Relacionados

- [jwt-estrutura-e-ciclo-de-vida](jwt-estrutura-e-ciclo-de-vida.md)
- [authorization-code-flow-com-pkce](../patterns/authorization-code-flow-com-pkce.md)
- [metodos-de-autenticacao-trade-offs](metodos-de-autenticacao-trade-offs.md)
