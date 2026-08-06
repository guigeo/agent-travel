<!-- Prosa em português; código, nomes de API e keywords técnicas em inglês. Convenção: .claude/kb/_index.yaml -->
# API keys vs. tokens de sessão vs. JWT — trade-offs

> **Propósito**: Escolher o mecanismo de credencial certo para cada tipo de consumidor da API — humano em navegador, aplicação móvel, ou serviço automatizado.
> **Confiança**: 0.9
> **Validado**: 2026-08-06 (OWASP Session Management Cheat Sheet; OWASP Authentication Cheat Sheet)

## Visão geral

Os três mecanismos resolvem "quem está chamando a API" de formas diferentes,
com trade-offs opostos entre **estado no servidor** e **facilidade de
revogação**. **Token de sessão** (cookie com id opaco) exige lookup em um
store server-side (Redis/DB) a cada requisição — mais caro, mas revogar é
trivial (deletar a entrada) e é o padrão mais maduro para app web tradicional.
**JWT** é stateless — nenhum lookup central, o próprio token carrega os
claims assinados — o que escala bem horizontalmente, mas revogar antes do
`exp` exige mecanismo extra (blocklist, `jti` tracking) porque o token
continua "válido" por definição até expirar. **API key** é uma credencial
estática de longa duração associada a uma **aplicação ou serviço**, não a uma
sessão de usuário interativo — usada em chamadas server-to-server ou por
clientes de API pública; não deve autenticar um humano em navegador (não tem
conceito de login/logout, expiração curta ou MFA).

## O padrão

```text
Token de sessão (cookie opaco + store server-side)
  Cliente → Cookie: session_id=<opaco> → Servidor faz lookup em Redis/DB
  Revogar: DELETE session:<id>   — efeito imediato

JWT (stateless, self-contained)
  Cliente → Authorization: Bearer <jwt> → Servidor valida assinatura localmente
  Revogar antes do exp: precisa de blocklist (jti) ou expiração curta + refresh

API key (credencial de aplicação/serviço, não de usuário)
  Cliente → X-API-Key: <chave estática de longa duração>
  Sem conceito de sessão; escopo e rate limit atrelados à própria chave
```

## Referência rápida

| Critério | Token de sessão | JWT | API key |
|----------|------------------|-----|---------|
| Estado no servidor | Sim (store obrigatório) | Não (por padrão) | Sim (registro da chave) |
| Revogação imediata | Trivial | Requer blocklist/exp curto | Trivial (desativar a chave) |
| Escala horizontal | Precisa de store compartilhado | Nativa | Nativa |
| Identifica | Usuário interativo | Usuário ou serviço | Aplicação/serviço |
| Expiração típica | Minutos a horas, renovável | Minutos (access) + dias (refresh) | Longa/sem expiração — rotacionar manualmente |
| Uso típico | App web server-rendered | API/SPA/mobile com múltiplos serviços | Integração server-to-server, API pública |

## Erros comuns

### Errado

```http
# API key usada para autenticar um usuário humano no navegador — sem expiração,
# sem MFA, se vazar (ex.: commitada no repo) o dano é indefinido
GET /me
X-API-Key: sk_live_51...
```

### Certo

```http
# usuário interativo autentica via token de curta duração (sessão ou JWT + refresh);
# API key fica reservada para integração server-to-server, com escopo restrito
GET /me
Authorization: Bearer <jwt-de-curta-duracao>
```

## Relacionados

- [jwt-estrutura-e-ciclo-de-vida](jwt-estrutura-e-ciclo-de-vida.md)
- [autorizacao-rbac-vs-abac](autorizacao-rbac-vs-abac.md)
- [refresh-token-rotation](../patterns/refresh-token-rotation.md)
