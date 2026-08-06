# Autenticação Quick Reference

> Fast lookup tables. For code examples, see linked files.

## Mecanismo de credencial

| Mecanismo | Estado no servidor | Revogação | Uso típico |
|-----------|---------------------|-----------|------------|
| Token de sessão (cookie opaco) | Sim (store obrigatório) | Trivial | App web server-rendered |
| JWT (stateless) | Não por padrão | Requer blocklist/exp curto | API/SPA/mobile multi-serviço |
| API key | Sim (registro da chave) | Trivial (desativar chave) | Integração server-to-server |

## Fluxos OAuth2/OIDC

| Fluxo | Cliente | Status |
|-------|---------|--------|
| Authorization Code + PKCE | Público (SPA/mobile) ou confidencial | Recomendado — obrigatório p/ público (RFC 9700) |
| Client Credentials | Machine-to-machine, sem usuário | Recomendado |
| Implicit | — | Deprecado — token exposto na URL |
| Resource Owner Password Credentials | — | Deprecado — expõe senha do usuário ao client |

## Decision Matrix — autorização

| Use Case | Choose |
|----------|--------|
| Poucos papéis estáveis, superfície simples | RBAC puro |
| Multi-tenant, regras dependem de contexto/atributo | ABAC / scopes granulares |
| Maioria das APIs em produção | RBAC (superfície) + scopes (ação) + ownership check (instância) |

## Decision Matrix — hashing de senha

| Situação | Choose |
|----------|--------|
| Sistema novo | Argon2id (m≥19 MiB, t≥2, p=1) |
| Argon2 indisponível | scrypt |
| Sistema legado sem Argon2/scrypt | bcrypt (work factor ≥ 10) |
| Nunca | MD5, SHA-1, SHA-256 puro (rápidos demais para senha) |

## Common Pitfalls

| Don't | Do |
|-------|-----|
| Token (JWT/sessão) em `localStorage`/`sessionStorage` | Access token em memória; refresh token em cookie `HttpOnly` |
| `implicit` flow (`response_type=token`) | Authorization Code + PKCE (`response_type=code`) |
| Senha em texto puro ou hash rápido sem salt | Argon2id com salt único por senha |
| Confiar só no papel (RBAC) sem checar ownership do recurso | Papel autoriza a ação; ownership autoriza a instância |
| Refresh token reusável indefinidamente | Rotação a cada uso + revogar família inteira se reuso for detectado |
| Aceitar `alg` do header do JWT sem restringir | Fixar `algorithms=[...]` explicitamente na validação |
| API key autenticando usuário humano em navegador | API key só para serviço/aplicação; usuário usa sessão/JWT com expiração curta |
| Cookie de token sem `SameSite`/`Secure`/`HttpOnly` explícitos | Sempre os três atributos + CSRF token em ações sensíveis |

## Related Documentation

| Topic | Path |
|-------|------|
| Getting Started | `concepts/jwt-estrutura-e-ciclo-de-vida.md` |
| Full Index | `index.md` |
