<!-- Prosa em português; código, nomes de API e keywords técnicas em inglês. Convenção: .claude/kb/_index.yaml -->
# Versionamento de API

> **Propósito**: Escolher onde a versão vive (URL, header ou query param) e ter uma estratégia explícita para breaking changes — versionar não é opcional a partir do primeiro cliente externo.
> **Confiança**: 0.9
> **Validado**: 2026-08-06 (RFC 8594 Sunset HTTP Header; convenção Stripe de versionamento por data; comparativo cross-industry URL vs header, 2026)

## Visão geral

Existem três lugares onde a versão pode viver: **URL path** (`/v1/users`), **header**
customizado (`X-API-Version: 2026-08-06`) ou **Accept header** com media type
versionado (`Accept: application/vnd.exemplo.v2+json`). URL path é o padrão mais
adotado para APIs públicas — funciona nativamente com cache HTTP, load balancer e
roteamento de gateway, sem exigir que nenhuma camada de infra entenda header
customizado. Header versioning mantém a URL "limpa" e é mais comum em APIs
internas service-to-service onde cliente e servidor evoluem juntos, mas depende de
toda a cadeia (proxies, CDN) propagar o header corretamente. Qualquer estratégia
escolhida deve ser única — misturar URL versioning em alguns endpoints e header
versioning em outros confunde consumidores.

## O padrão

```http
# URL path versioning — mais comum em API pública
GET /v1/users/{id}
GET /v2/users/{id}

# Header versioning — comum em API interna service-to-service
GET /users/{id}
X-API-Version: 2026-08-06

# Media type versioning — variante de header, no Accept
GET /users/{id}
Accept: application/vnd.exemplo.v2+json

# Deprecação de uma versão (RFC 8594) — sinaliza ANTES de remover
HTTP/1.1 200 OK
Deprecation: true
Sunset: Sat, 31 Jan 2027 23:59:59 GMT
Link: <https://docs.exemplo.com/migracao-v2>; rel="deprecation"
```

## Referência rápida

| Estratégia | Vantagem | Custo |
|------------|----------|-------|
| URL path (`/v1/...`) | Cache HTTP nativo; roteamento de gateway sem config extra | Rota "suja" com versão; duplica paths por versão |
| Header (`X-API-Version`) | URL limpa; fácil trocar versão sem mudar rota | Falha silenciosa se algum proxy no caminho não propagar o header |
| Data (`2026-08-06`, estilo Stripe) | Granularidade fina, sem "big bang" de versão major | Exige registro de qual mudança entrou em qual data |

## Erros comuns

### Errado

```http
GET /v1/users        # endpoint A usa URL versioning
GET /orders           # endpoint B, sem versão nenhuma — inconsistente
X-API-Version: 2       # endpoint C usa header — terceira convenção no mesmo produto
```

### Certo

```http
# Uma única estratégia para toda a API pública, documentada e com prazo de sunset
GET /v1/users
GET /v1/orders
GET /v2/users     # nova versão, mesma convenção, v1 ainda ativa até o Sunset
```

## Relacionados

- [codigos-de-status-e-formato-de-erro](codigos-de-status-e-formato-de-erro.md)
- [estrategia-de-deprecacao-e-breaking-change](../patterns/estrategia-de-deprecacao-e-breaking-change.md)
