# Autenticação Knowledge Base

> **Purpose**: Conhecimento geral de autenticação e autorização em APIs web — JWT (estrutura, assinatura, expiração, refresh tokens, armazenamento seguro), OAuth2/OpenID Connect (fluxos principais), API keys vs. tokens de sessão vs. JWT, RBAC vs. ABAC/scopes, hashing de senha e armadilhas comuns (localStorage vs. cookie httpOnly, CSRF, replay attacks). Agnóstico de framework; exemplos ilustrativos em Python/JavaScript.
> **Validado**: 2026-08-06 (RFC 7519 JSON Web Token; RFC 6749 OAuth 2.0; RFC 9700 OAuth 2.0 Security BCP; RFC 7636 PKCE; OpenID Connect Core 1.0; OWASP Password Storage/JWT/HTML5 Security Cheat Sheets)

## Quick Navigation

### Concepts (< 150 lines each)

| File | Purpose |
|------|---------|
| [concepts/jwt-estrutura-e-ciclo-de-vida.md](concepts/jwt-estrutura-e-ciclo-de-vida.md) | Anatomia do JWT, HS256 vs RS256, validação de assinatura e expiração |
| [concepts/oauth2-e-openid-connect.md](concepts/oauth2-e-openid-connect.md) | Authorization code + PKCE vs client credentials; o que o OIDC adiciona ao OAuth2 |
| [concepts/metodos-de-autenticacao-trade-offs.md](concepts/metodos-de-autenticacao-trade-offs.md) | API key vs token de sessão vs JWT — estado, revogação, escala |
| [concepts/autorizacao-rbac-vs-abac.md](concepts/autorizacao-rbac-vs-abac.md) | Papel (RBAC) vs atributo/scope (ABAC) vs ownership em runtime |

### Patterns (< 200 lines each)

| File | Purpose |
|------|---------|
| [patterns/hashing-de-senha-com-argon2.md](patterns/hashing-de-senha-com-argon2.md) | Armazenar senha com Argon2id, salt único e rehash lazy |
| [patterns/refresh-token-rotation.md](patterns/refresh-token-rotation.md) | Access token curto + refresh token rotacionado com detecção de reuso |
| [patterns/armazenamento-seguro-de-token-no-cliente.md](patterns/armazenamento-seguro-de-token-no-cliente.md) | Access token em memória + refresh token em cookie httpOnly |
| [patterns/authorization-code-flow-com-pkce.md](patterns/authorization-code-flow-com-pkce.md) | Login via IdP externo com PKCE, obrigatório desde a RFC 9700 |

---

## Quick Reference

- [quick-reference.md](quick-reference.md) — tabelas de decisão e pitfalls

---

## Key Concepts

| Concept | Description |
|---------|-------------|
| **JWT é assinado, não criptografado** | Payload é apenas codificado — nunca colocar dado sensível nele |
| **Authorization code + PKCE é o fluxo padrão** | RFC 9700 deprecou implicit e password grant; PKCE previne CSRF e code injection |
| **Revogação é o trade-off central** | Sessão/API key revoga fácil (estado no servidor); JWT stateless exige blocklist ou expiração curta |
| **Senha nunca em texto puro** | Sempre Argon2id (ou bcrypt em legado) com salt único por senha |
| **Token no cliente: memória > cookie httpOnly > localStorage** | localStorage é legível por qualquer XSS; cookie httpOnly reintroduz CSRF, mitigado por SameSite |

---

## Learning Path

| Level | Files |
|-------|-------|
| **Beginner** | concepts/jwt-estrutura-e-ciclo-de-vida.md → concepts/metodos-de-autenticacao-trade-offs.md |
| **Intermediate** | patterns/hashing-de-senha-com-argon2.md → patterns/armazenamento-seguro-de-token-no-cliente.md → patterns/refresh-token-rotation.md |
| **Advanced** | concepts/oauth2-e-openid-connect.md + patterns/authorization-code-flow-com-pkce.md + concepts/autorizacao-rbac-vs-abac.md |

---

## Agent Usage

| Agent | Primary Files | Use Case |
|-------|---------------|----------|
| python-developer / code-reviewer | concepts/*, patterns/hashing-de-senha-com-argon2.md | Implementar ou revisar login/signup de uma API |
| genai-architect / the-planner | concepts/oauth2-e-openid-connect.md, patterns/authorization-code-flow-com-pkce.md | Planejar integração de login com IdP externo |
| kb-architect / code-reviewer | patterns/armazenamento-seguro-de-token-no-cliente.md, patterns/refresh-token-rotation.md | Revisar armadilhas de sessão em SPA/mobile |
