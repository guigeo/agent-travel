<!-- Prosa em português; código, nomes de API e keywords técnicas em inglês. Convenção: .claude/kb/_index.yaml -->
# Autorização: RBAC vs. ABAC/scopes granulares

> **Propósito**: Decidir entre papéis (RBAC), atributos/scopes granulares (ABAC) — ou a combinação dos dois — para modelar "quem pode fazer o quê" na API.
> **Confiança**: 0.9
> **Validado**: 2026-08-06 (NIST RBAC model — INCITS 359; RFC 6749 §3.3 Access Token Scope; OWASP Authorization Cheat Sheet)

## Visão geral

**RBAC** (Role-Based Access Control) atribui permissões a **papéis** (`admin`,
`editor`, `viewer`) e usuários a papéis — simples de implementar e auditar,
mas sofre de granularidade grosseira: regras que dependem de contexto (dono
do recurso, tenant, horário) forçam a criação de papéis cada vez mais
específicos ("role explosion"). **ABAC** (Attribute-Based Access Control) e
scopes OAuth2 (`orders:read`, `orders:write`) decidem autorização a partir de
**atributos** do usuário, do recurso e do ambiente — mais expressivo, porém
mais difícil de testar e auditar porque a lógica vira código em vez de uma
tabela fixa. Na prática a maioria das APIs combina os dois: RBAC para o
controle grosso de superfície de acesso (que endpoints o papel pode chamar) +
scopes granulares por token (o que aquele token específico pode fazer) +
checagem explícita de **ownership** em runtime — ter o papel `user` nunca
deveria, por si só, dar acesso ao recurso de outro usuário.

## O padrão

```python
from dataclasses import dataclass

@dataclass
class AuthContext:
    user_id: str
    role: str            # RBAC: controle grosso ("admin", "user")
    scopes: set[str]      # ABAC/OAuth2: o que ESTE token pode fazer

def can_update_order(ctx: AuthContext, order: "Order") -> bool:
    if ctx.role == "admin":
        return True                                    # RBAC: admin sempre pode
    if "orders:write" not in ctx.scopes:
        return False                                    # scope: token não autoriza a ação
    return order.owner_id == ctx.user_id                 # ABAC: ownership do recurso
```

## Referência rápida

| Modelo | Granularidade | Custo de manutenção | Quando usar |
|--------|----------------|----------------------|-------------|
| RBAC puro | Grosseira (por papel) | Baixo — fácil auditar | Superfícies simples, poucos papéis estáveis |
| ABAC/scopes puro | Fina (por atributo/ação) | Alto — lógica espalhada, difícil auditar | Multi-tenant, regras dinâmicas por contexto |
| RBAC + scopes + ownership | Papel controla superfície, scope controla ação, ownership controla instância | Médio | Padrão recomendado para a maioria das APIs |

## Erros comuns

### Errado

```python
# confia só no papel — qualquer "user" acessa o pedido de QUALQUER outro usuário
def can_update_order(ctx, order):
    return ctx.role == "user"
```

### Certo

```python
# papel autoriza a AÇÃO; ownership autoriza a INSTÂNCIA específica do recurso
def can_update_order(ctx, order):
    return ctx.role in {"user", "admin"} and (
        ctx.role == "admin" or order.owner_id == ctx.user_id
    )
```

## Relacionados

- [metodos-de-autenticacao-trade-offs](metodos-de-autenticacao-trade-offs.md)
- [jwt-estrutura-e-ciclo-de-vida](jwt-estrutura-e-ciclo-de-vida.md)
- [oauth2-e-openid-connect](oauth2-e-openid-connect.md)
