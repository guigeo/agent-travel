<!-- Prosa em português; código, nomes de API e keywords técnicas em inglês. Convenção: .claude/kb/_index.yaml -->
# Armazenamento seguro de senha com Argon2id

> **Propósito**: Nunca guardar senha em texto puro nem com hash rápido (`MD5`/`SHA-256` puro) — usar um algoritmo lento e memory-hard com salt único por senha.
> **Validado**: 2026-08-06 (OWASP Password Storage Cheat Sheet; RFC 9106 Argon2)

## Quando usar

- Sempre que a aplicação é responsável por armazenar a própria credencial
  (login/senha local) — não se aplica quando a autenticação é 100% delegada a
  um IdP externo via OAuth2/OIDC.
- Ao criar um novo cadastro/registro de usuário.
- Ao migrar um sistema legado que usa hash rápido (`MD5`, `SHA-1`,
  `SHA-256` sem salt) — trocar no próximo login bem-sucedido (rehash lazy).

## Implementação

```python
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError

# Parâmetros recomendados pelo OWASP Password Storage Cheat Sheet:
# m=19456 (19 MiB), t=2 iterações, p=1 grau de paralelismo — Argon2id
hasher = PasswordHasher(
    time_cost=2,
    memory_cost=19456,
    parallelism=1,
    hash_len=32,
    salt_len=16,          # salt único gerado automaticamente por chamada
)

def hash_password(plain_password: str) -> str:
    # o hash retornado já inclui algoritmo, parâmetros e salt — self-describing
    return hasher.hash(plain_password)

def verify_password(stored_hash: str, plain_password: str) -> bool:
    try:
        hasher.verify(stored_hash, plain_password)
    except VerifyMismatchError:
        return False
    except InvalidHashError:
        return False  # hash de formato antigo/inválido — tratar como legado
    return True

def login(user_repo, email: str, plain_password: str) -> "User | None":
    user = user_repo.find_by_email(email)
    if user is None or not verify_password(user.password_hash, plain_password):
        return None  # mesma resposta para "usuário não existe" e "senha errada"

    # rehash lazy: se os parâmetros do hasher mudaram desde que o hash foi
    # criado, gera um novo hash com os parâmetros atuais e persiste
    if hasher.check_needs_rehash(user.password_hash):
        user.password_hash = hash_password(plain_password)
        user_repo.save(user)

    return user
```

## Configuração

| Decisão | Padrão recomendado | Descrição |
|---------|--------------------|-----------|
| Algoritmo | Argon2id | Resiste a ataques de side-channel e GPU/ASIC — vencedor da Password Hashing Competition |
| `memory_cost` (m) | Mínimo 19456 KiB (19 MiB) | Quanto maior, mais caro paralelizar o ataque em GPU |
| `time_cost` (t) | Mínimo 2 | Ajustar para o hash levar ~250-500ms no hardware de produção |
| `parallelism` (p) | 1 em servidor com fila de requisições | `p` alto ajuda o atacante mais do que a defesa em servidor multi-tenant |
| Salt | Único por senha, gerado automaticamente | Nunca reusar salt — impede ataque de rainbow table |
| Fallback sem Argon2 | `bcrypt` (work factor ≥ 10) apenas em sistema legado | Nunca `SHA-256`/`MD5` puro — são rápidos demais, feitos para hashing de dados, não senha |
| Resposta de erro de login | Mensagem idêntica para "não existe" e "senha errada" | Evita enumeração de usuários válidos |

## Exemplo de uso

```http
POST /auth/signup
{"email": "user@exemplo.com", "password": "S3nhaForte!"}

HTTP/1.1 201 Created

POST /auth/login
{"email": "user@exemplo.com", "password": "S3nhaForte!"}

HTTP/1.1 200 OK
{"accessToken": "eyJ...", "refreshToken": "..."}
```

## Ver também

- [metodos-de-autenticacao-trade-offs](../concepts/metodos-de-autenticacao-trade-offs.md)
- [jwt-estrutura-e-ciclo-de-vida](../concepts/jwt-estrutura-e-ciclo-de-vida.md)
