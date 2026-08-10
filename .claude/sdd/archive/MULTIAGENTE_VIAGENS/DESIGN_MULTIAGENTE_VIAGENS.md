# DESIGN: Sistema Multiagente de Planejamento de Viagens

> Design técnico de um assistente multiagente (orquestrador + tools especializadas) para planejamento de viagens, com um Agente de Milhas totalmente desacoplado para avaliar trocas de pontos Itaú.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | MULTIAGENTE_VIAGENS |
| **Date** | 2026-08-06 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_MULTIAGENTE_VIAGENS.md](./DEFINE_MULTIAGENTE_VIAGENS.md) |
| **Status** | ✅ Shipped |

---

## Architecture Overview

```text
┌────────────────────────────────────────────────────────────────────────┐
│                          API (FastAPI) — src/agent_travel/api/          │
│                                                                          │
│   POST /chat/{session_id}                POST /miles/query             │
└──────────────┬────────────────────────────────────┬─────────────────────┘
               │                                    │
               ▼                                    ▼
   ┌────────────────────────────┐       ┌────────────────────────────┐
   │  Orchestrator (Planner)    │       │  Miles Agent (standalone)  │
   │  run_turn(                 │       │  run_turn(                 │
   │    prompt=PLANNER_PROMPT,  │       │    prompt=MILES_PROMPT,     │
   │    registry=PLANNER_TOOLS, │       │    registry=MILES_TOOLS,    │
   │    session=SessionStore)   │       │    session=SessionStore)    │
   └──────────────┬──────────────┘       └──────────────┬───────────────┘
                  │ tool calls                          │ tool calls
   ┌──────────────┴──────────────────┐    ┌──────────────┴───────────────┐
   │ Tools (subagentes de viagem)    │    │ Tools (Milhas)                │
   │ - buscar_voos                   │    │ - buscar_bonus_vigente        │
   │ - buscar_hospedagem             │    │ - calcular_valor_ponto        │
   │ - montar_roteiro                │    └──────────────┬───────────────┘
   │ - calcular_orcamento            │                   │
   └──────────────┬───────────────────┘                  │
                  │                                       │
                  ▼                                       ▼
          ┌──────────────────────────────────────────────────┐
          │        Web Search Client (infra compartilhada,    │
          │        stateless — sem dados de negócio em comum) │
          └──────────────────────────────────────────────────┘

   Motor comum (sem estado de negócio): core/loop.py → run_turn genérico
   usado pelos dois agentes, cada um com seu próprio prompt/registry/sessão.
```

**Ponto-chave da arquitetura:** Orquestrador e Agente de Milhas rodam sobre o **mesmo motor de loop** (evita duplicar o mecanismo), mas com **prompt, tool registry e sessão totalmente independentes** — o planejador de viagem nunca importa nem depende do módulo `milhas/`, e vice-versa. Isso implementa diretamente o requisito MUST de desacoplamento do DEFINE.

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| API (FastAPI) | Expõe `/chat` e `/miles/query`, valida payloads, formata erros | FastAPI + Pydantic v2 |
| Motor de loop genérico (`core/loop.py`) | `run_turn` reutilizável: teto de iterações, autocorreção de erro, poda de histórico | Python puro, SDK do provider LLM |
| Orquestrador (Planner) | Conduz a conversa de planejamento de viagem, aciona tools de Voos/Hospedagem/Roteiro/Orçamento | Tools tipadas (Pydantic) + registry |
| Agente de Milhas | Módulo standalone; calcula valor efetivo de bônus de transferência de pontos sob demanda | Tools tipadas (Pydantic) + registry, prompt e sessão próprios |
| Web Search Client | Wrapper fino sobre um provider de busca web, usado pelos backends de voos/hospedagem/milhas | HTTP client (provider a definir no Build) |
| SessionStore | Histórico de conversa em memória com TTL, uma instância por agente | dict Python + TTL |
| Frontend simples | Chat web mínimo consumindo `/chat` e `/miles/query` | HTML + JS puro (sem build step) |

---

## Key Decisions

### Decision 1: Motor de loop genérico e reutilizável, parametrizado por prompt/registry/sessão

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-06 |

**Context:** O DEFINE exige que o Agente de Milhas seja totalmente independente do planejador de viagem, mas ambos precisam do mesmo mecanismo de tool-calling (documentado na KB `agentes-llm/patterns/loop-tool-calling-explicito.md`).

**Choice:** Implementar `run_turn(client, session, registry, system_prompt, pergunta)` uma única vez em `core/loop.py`, genérico o suficiente para ser instanciado duas vezes — uma para o Orquestrador, outra para o Agente de Milhas — cada uma com seu próprio prompt, `ToolRegistry` e `SessionStore`.

**Rationale:** Evita duplicar ~40 linhas de mecanismo (e o risco delas divergirem com o tempo), sem violar o desacoplamento: o que é compartilhado é infraestrutura (o `while` do loop), não dado ou estado de negócio.

**Alternatives Rejected:**
1. Duplicar o loop dentro de `orchestrator/` e `milhas/` — rejeitado: duplicação de mecanismo, risco de bugs divergentes ao corrigir um e esquecer o outro.
2. Framework de multiagentes (LangGraph/CrewAI) — já rejeitado no BRAINSTORM/DEFINE por overhead de dependência para projeto solo.

**Consequences:**
- Qualquer correção no mecanismo do loop (ex: política de retry) beneficia os dois agentes automaticamente.
- Exige que `core/loop.py` não importe nada de `orchestrator/` nem de `milhas/` (dependência é unidirecional: os agentes importam o core, nunca o contrário).

---

### Decision 2: Subagentes de viagem são tools tipadas dentro de UM único loop, não agentes LLM aninhados

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-06 |

**Context:** O BRAINSTORM menciona "subagentes" de Voos, Hospedagem, Roteiro e Orçamento. É preciso decidir se cada um é um agente LLM próprio (chamado como tool, com seu próprio loop) ou uma tool determinística dentro do loop do Orquestrador.

**Choice:** Cada "subagente" de viagem é implementado como **1 Pydantic model de args + 1 handler + 1 backend**, registrado no `PLANNER_TOOL_REGISTRY` do Orquestrador — seguindo a KB `agentes-llm/patterns/tools-pydantic-registry.md`. Não há LLM aninhado dentro de uma tool.

**Rationale:** Para tarefas de busca/cálculo (voos, hotéis, orçamento), uma tool determinística é mais barata, mais rápida e muito mais fácil de testar/depurar do que um agente LLM chamando outro agente LLM. Roteiro é o único subagente com raciocínio mais "criativo", mas ainda cabe como tool cujo handler monta o prompt e faz 1 chamada ao LLM internamente, sem loop próprio.

**Alternatives Rejected:**
1. Cada subagente como agente LLM independente (nested agents) — rejeitado: dobra custo/latência por sub-tarefa, dificulta debugging (dois níveis de tool-calling), sem ganho de qualidade para tarefas majoritariamente determinísticas.

**Consequences:**
- Orquestrador tem 1 único `TOOL_REGISTRY` com 4 tools (`buscar_voos`, `buscar_hospedagem`, `montar_roteiro`, `calcular_orcamento`).
- Simplifica testes: cada tool é testável isoladamente sem precisar de um LLM real (KB `avaliacao-offline-fake-client.md`).

---

### Decision 3: Fonte de dados de voos/hospedagem/bônus via Web Search Client, não API paga

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-06 |

**Context:** DEFINE exclui explicitamente APIs pagas (Amadeus/Skyscanner/Booking) do MVP.

**Choice:** Cada backend (`voos/backend.py`, `hospedagem/backend.py`, `milhas/backend.py`) usa um `WebSearchClient` compartilhado (`web_search/client.py`) para obter dados atuais, com o provider de busca configurável via `core/config.py`.

**Rationale:** Zero custo adicional no MVP; a lógica de parsing/normalização fica isolada no backend, então trocar por uma API estruturada depois (Assumption A-001 do DEFINE) não exige tocar nas tools nem no Orquestrador — só reimplementar o backend.

**Alternatives Rejected:**
1. Amadeus Self-Service / Skyscanner desde o MVP — rejeitado por custo e complexidade de cadastro antes de validar o conceito.

**Consequences:**
- Precisão dos dados depende da qualidade da busca web (risco documentado em Assumptions do DEFINE).
- Backend isolado facilita migração futura sem retrabalho nas camadas superiores.

---

### Decision 4: Sessões em memória (dict + TTL), sem banco de dados

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-06 |

**Context:** Projeto solo, single-user, single-process — DEFINE não exige persistência entre reinicializações.

**Choice:** `SessionStore` como dict Python em memória com TTL, uma instância separada para o Orquestrador e outra para o Agente de Milhas (reforça o desacoplamento).

**Rationale:** Suficiente para 1 usuário e 1 worker; evita a complexidade operacional de um banco de dados para um MVP pessoal.

**Alternatives Rejected:**
1. Redis/Postgres para sessões — rejeitado: overkill para o volume e escopo atuais.

**Consequences:**
- Reiniciar o processo perde o histórico de conversa em andamento (aceitável para MVP; documentado como trade-off, não como bug).
- Migrar para múltiplos workers exigiria trocar por um store externo — adiado (YAGNI).

---

### Decision 5: Erros de API no formato RFC 9457 Problem Details

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-06 |

**Context:** A API precisa de um formato de erro consistente entre `/chat` e `/miles/query`, incluindo erros de validação e erros de domínio (ex: tool falhou 2x).

**Choice:** Exception handler central em `api/errors.py` seguindo a KB `rest-api-design/patterns/problem-details-rfc9457.md` — toda resposta de erro usa `application/problem+json` com `type`/`title`/`status`/`detail`/`instance`.

**Rationale:** Formato padronizado, reconhecido pela indústria (RFC 9457), evita que cada endpoint invente seu próprio schema de erro.

**Alternatives Rejected:**
1. Formato de erro ad-hoc por endpoint — rejeitado: inconsistência e mais código de tratamento no frontend.

**Consequences:**
- Um único exception handler cobre validação de payload (`RequestValidationError`) e erros de domínio (`ApiError`).

---

### Decision 6: Toda dependência Python gerida via `uv`

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-06 |

**Context:** Constraint explícita do DEFINE e do usuário: nunca usar pip/venv global.

**Choice:** `pyproject.toml` gerido por `uv` (`uv init`, `uv add fastapi pydantic pydantic-settings ...`, `uv run pytest`, `uv sync`). Nenhum pacote instalado fora do ambiente do projeto.

**Rationale:** Padrão já documentado em `.claude/CLAUDE.md` do projeto.

**Consequences:**
- Build phase deve usar exclusivamente comandos `uv` — nunca `pip install` direto.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `pyproject.toml` | Create | Config do projeto gerida por `uv` | @python-developer | None |
| 2 | `.env.example` | Create | Variáveis de ambiente (chave LLM, chave web search) | @python-developer | None |
| 3 | `src/agent_travel/__init__.py` | Create | Marcador de pacote | @python-developer | None |
| 4 | `src/agent_travel/core/config.py` | Create | `Settings` (pydantic-settings): modelo LLM, teto de iterações, TTL de sessão | @python-developer | 1, 2 |
| 5 | `src/agent_travel/core/llm_client.py` | Create | Factory do client LLM (provider a definir no Build) | @ai-developer | 4 |
| 6 | `src/agent_travel/core/tool_registry.py` | Create | `ToolRegistry` genérico: `openai_tools()` / `execute_tool()` | @ai-developer | None |
| 7 | `src/agent_travel/core/loop.py` | Create | `run_turn` genérico (Decision 1) | @ai-developer | 5, 6 |
| 8 | `src/agent_travel/core/session.py` | Create | `SessionStore` (dict + TTL) | @python-developer | 4 |
| 9 | `src/agent_travel/web_search/client.py` | Create | `WebSearchClient` — wrapper fino de busca web | @python-developer | 4 |
| 10 | `src/agent_travel/agents/voos/backend.py` | Create | Busca e normalização de voos via `WebSearchClient` | @python-developer | 9 |
| 11 | `src/agent_travel/agents/voos/tools.py` | Create | `BuscarVoosArgs` + handler `buscar_voos` | @ai-developer | 6, 10 |
| 12 | `src/agent_travel/agents/hospedagem/backend.py` | Create | Busca e normalização de hospedagem via `WebSearchClient` | @python-developer | 9 |
| 13 | `src/agent_travel/agents/hospedagem/tools.py` | Create | `BuscarHospedagemArgs` + handler `buscar_hospedagem` | @ai-developer | 6, 12 |
| 14 | `src/agent_travel/agents/roteiro/tools.py` | Create | `MontarRoteiroArgs` + handler `montar_roteiro` | @ai-developer | 5, 6 |
| 15 | `src/agent_travel/agents/orcamento/tools.py` | Create | `CalcularOrcamentoArgs` + handler `calcular_orcamento` (consolidação + alerta de estouro) | @ai-developer | 6 |
| 16 | `src/agent_travel/orchestrator/prompt.py` | Create | `PLANNER_SYSTEM_PROMPT` (regras numeradas, KB `system-prompt-como-politica`) | @ai-developer | None |
| 17 | `src/agent_travel/orchestrator/registry.py` | Create | `PLANNER_TOOL_REGISTRY` combinando tools 11, 13, 14, 15 | @ai-developer | 11, 13, 14, 15 |
| 18 | `src/agent_travel/milhas/backend.py` | Create | Busca de bônus de transferência vigente via `WebSearchClient` | @python-developer | 9 |
| 19 | `src/agent_travel/milhas/tools.py` | Create | `BuscarBonusArgs`/`CalcularValorPontoArgs` + handlers | @ai-developer | 6, 18 |
| 20 | `src/agent_travel/milhas/prompt.py` | Create | `MILES_SYSTEM_PROMPT` — explicita que não depende de contexto de viagem | @ai-developer | None |
| 21 | `src/agent_travel/milhas/registry.py` | Create | `MILES_TOOL_REGISTRY` | @ai-developer | 19 |
| 22 | `src/agent_travel/api/schemas.py` | Create | Pydantic request/response (`ChatRequest`, `ChatResponse`, `MilesQueryRequest`, `MilesQueryResponse`) | @api-developer | None |
| 23 | `src/agent_travel/api/errors.py` | Create | `ApiError` + exception handlers RFC 9457 (Decision 5) | @api-developer | None |
| 24 | `src/agent_travel/api/routes/chat.py` | Create | `POST /chat/{session_id}` — usa Orquestrador | @api-developer | 7, 8, 16, 17, 22, 23 |
| 25 | `src/agent_travel/api/routes/miles.py` | Create | `POST /miles/query` — usa Agente de Milhas, sem `session_id` de viagem | @api-developer | 7, 8, 20, 21, 22, 23 |
| 26 | `src/agent_travel/api/main.py` | Create | App FastAPI, monta routers e exception handlers | @api-developer | 23, 24, 25 |
| 27 | `frontend/index.html` | Create | Chat web mínimo (HTML+JS puro) consumindo `/chat` e `/miles/query` | @python-developer | 26 |
| 28 | `tests/conftest.py` | Create | Fixtures: client LLM fake roteirizado, backends fake | @python-developer | None |
| 29 | `tests/test_loop_offline.py` | Create | Testes offline do motor genérico (teto, autocorreção, poda) | @python-developer | 7, 28 |
| 30 | `tests/test_tools_voos.py` | Create | Testes de validação/handler de `buscar_voos` | @python-developer | 11, 28 |
| 31 | `tests/test_tools_orcamento.py` | Create | Testes de cálculo de orçamento e alerta de estouro (AT-003) | @python-developer | 15, 28 |
| 32 | `tests/test_milhas_independente.py` | Create | Garante que `milhas/` roda sem import/estado do `orchestrator/` (valida AT-002 e desacoplamento) | @python-developer | 19, 20, 21, 28 |
| 33 | `tests/test_api_chat.py` | Create | Integração via `TestClient` — happy path (AT-001) e limite de escopo (AT-004) | @python-developer | 26, 28 |

**Total Files:** 33

---

## Agent Assignment Rationale

> Agents discovered from `.claude/agents/` - Build phase invokes matched specialists.

| Agent | Files Assigned | Why This Agent |
|-------|----------------|-----------------|
| @ai-developer | 5, 6, 7, 11, 13, 14, 15, 16, 17, 19, 20, 21 | Especialista no domínio de prompts/loop/tools do agente de chat do projeto — cobre motor de loop, tools tipadas e system prompts (planner e milhas) |
| @api-developer | 22, 23, 24, 25, 26 | Especialista em endpoints/convenções REST do agent-travel — schemas, formato de erro RFC 9457, rotas |
| @python-developer | 1, 2, 3, 4, 8, 9, 10, 12, 18, 27, 28, 29, 30, 31, 32, 33 | Código Python geral (config, sessão, web search client, backends, frontend estático, testes) — dataclasses/type hints/pytest |
| (general/code-reviewer) | Revisão pós-build de todos os arquivos | Nenhum specialist adicional necessário; @code-reviewer roda revisão de qualidade/segurança no fim do `/build` |

**Agent Discovery:**
- Scanned: `.claude/agents/**/*.md`
- Matched by: domínio (KB `agentes-llm` → @ai-developer; KB `rest-api-design` → @api-developer), tipo de arquivo, palavras-chave de propósito

---

## Code Patterns

### Pattern 1: Motor de loop genérico e reutilizável (`core/loop.py`)

```python
# Usado tanto pelo Orquestrador quanto pelo Agente de Milhas — cada chamador
# passa seu próprio system_prompt, ToolRegistry e Session.


def run_turn(
    client, session, registry: ToolRegistry, system_prompt: str, pergunta: str
) -> Response:
    session.messages.append({"role": "user", "content": pergunta})
    acao_ui, dados, erros = None, None, 0

    for _ in range(settings.max_tool_iters):
        resp = client.chat.completions.create(
            model=settings.llm_model,
            messages=[{"role": "system", "content": system_prompt}, *session.messages],
            tools=registry.openai_tools(),
        )
        msg = resp.choices[0].message
        session.messages.append(assistant_dict(msg))

        if not msg.tool_calls:
            trim(session)
            return Response(texto=msg.content or "", acao_ui=acao_ui, dados=dados)

        for call in msg.tool_calls:
            result = registry.execute_tool(call.function.name, call.function.arguments)
            session.messages.append(
                {"role": "tool", "tool_call_id": call.id, "content": result.payload_json}
            )
            if result.error:
                erros += 1
                if erros >= 2:
                    trim(session)
                    return Response(texto=MSG_ERRO_AMIGAVEL, acao_ui=acao_ui, dados=dados)
            elif result.ids:
                acao_ui, dados = result.ids, result.rows

    trim(session)
    return Response(texto=MSG_LIMITE_ITERACOES, acao_ui=acao_ui, dados=dados)
```

### Pattern 2: Tool tipada + registry (subagente de viagem)

```python
# agents/voos/tools.py
class BuscarVoosArgs(BaseModel):
    """Busca voos entre origem e destino em datas específicas (ida e volta opcional)."""

    origem: str = Field(description="Cidade ou aeroporto de origem")
    destino: str = Field(description="Cidade ou aeroporto de destino")
    data_ida: str = Field(description="Data de ida no formato YYYY-MM-DD")
    data_volta: str | None = Field(None, description="Data de volta, se ida e volta")


def _buscar_voos(backend: VoosBackend, a: BuscarVoosArgs) -> ToolResult:
    rows = backend.buscar(a.origem, a.destino, a.data_ida, a.data_volta)
    return ToolResult(payload=rows, ids=[r["id"] for r in rows], rows=rows)


# orchestrator/registry.py
PLANNER_TOOL_REGISTRY = ToolRegistry(
    {
        "buscar_voos": (BuscarVoosArgs, _buscar_voos),
        "buscar_hospedagem": (BuscarHospedagemArgs, _buscar_hospedagem),
        "montar_roteiro": (MontarRoteiroArgs, _montar_roteiro),
        "calcular_orcamento": (CalcularOrcamentoArgs, _calcular_orcamento),
    }
)

# milhas/registry.py — registry INDEPENDENTE, sem nenhum import de orchestrator/
MILES_TOOL_REGISTRY = ToolRegistry(
    {
        "buscar_bonus_vigente": (BuscarBonusArgs, _buscar_bonus_vigente),
        "calcular_valor_ponto": (CalcularValorPontoArgs, _calcular_valor_ponto),
    }
)
```

### Pattern 3: Configuração via pydantic-settings

```python
# core/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    llm_provider_api_key: str
    llm_model: str = "TBD"  # provider definido no Build (ver @ai-developer)
    web_search_api_key: str | None = None
    max_tool_iters: int = 6
    session_ttl_seconds: int = 3600

    class Config:
        env_file = ".env"


settings = Settings()
```

```text
# .env.example
LLM_PROVIDER_API_KEY=
LLM_MODEL=
WEB_SEARCH_API_KEY=
MAX_TOOL_ITERS=6
SESSION_TTL_SECONDS=3600
```

---

## Data Flow

```text
1. Usuário envia mensagem via POST /chat/{session_id}
   │
   ▼
2. API valida payload (ChatRequest) e busca/cria sessão em SessionStore do Orquestrador
   │
   ▼
3. Orquestrador roda run_turn(PLANNER_SYSTEM_PROMPT, PLANNER_TOOL_REGISTRY, sessão)
   │
   ▼
4. LLM decide chamar tools (buscar_voos / buscar_hospedagem / montar_roteiro / calcular_orcamento)
   │
   ▼
5. Cada tool valida args via Pydantic, aciona seu backend (Web Search Client) e retorna ToolResult
   │
   ▼
6. Resultado volta ao LLM como tool result; ids/rows das tools alimentam o grounding determinístico
   │
   ▼
7. LLM produz resposta final em texto; API retorna ChatResponse (texto + dados estruturados)

── fluxo paralelo e independente ──────────────────────────────────────────
8. Usuário consulta POST /miles/query (sem session_id de viagem)
   │
   ▼
9. Agente de Milhas roda seu próprio run_turn(MILES_SYSTEM_PROMPT, MILES_TOOL_REGISTRY,
   sessão própria) — nenhum dado do fluxo 1-7 é lido ou necessário
```

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|-------------------|-----------------|
| Provider de busca web (a definir no Build) | REST/SDK, via `WebSearchClient` | API key em variável de ambiente |
| Provider de LLM (a definir no Build — ver @ai-developer) | SDK oficial (chat completions + tool calling) | API key em variável de ambiente |

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|-----------------|
| Unit (offline, fake client) | Motor de loop genérico (teto, autocorreção, poda de histórico) | `test_loop_offline.py` | pytest + fake LLM client roteirizado (KB `avaliacao-offline-fake-client`) | Todos os ramos do `run_turn` |
| Unit | Tools individuais (validação Pydantic + handler) | `test_tools_voos.py`, `test_tools_orcamento.py` | pytest, backends fake injetados | 80% |
| Unit (desacoplamento) | `milhas/` não importa nada de `orchestrator/` | `test_milhas_independente.py` | pytest (import-check) + testes funcionais | Garantir AT-002 |
| Integration | Endpoints da API | `test_api_chat.py` | pytest + FastAPI `TestClient` | AT-001, AT-004 |
| E2E | Fluxo completo via frontend simples | Manual | Navegador | Happy path (AT-001) |

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|---------------------|--------|
| Args de tool inválidos (Pydantic `ValidationError`) | Retorna payload de erro ao LLM (`{"erro": ..., "detalhe": ...}`) para autocorreção | Yes (1x, via LLM) |
| Tool falha 2x no mesmo turno | Mensagem amigável ao usuário, sem propagar exceção | No |
| Timeout/erro do Web Search Client | Backend captura e retorna `ToolResult(error=True)` com mensagem de fonte indisponível | No (LLM decide se tenta reformular) |
| Payload malformado na API (`RequestValidationError`) | RFC 9457 Problem Details, HTTP 422 | No |
| `MAX_TOOL_ITERS` excedido | Mensagem de limite de iterações ao usuário, sem erro fatal | No |

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|--------------|
| `llm_provider_api_key` | string | — (obrigatório) | Chave do provider LLM, nunca hardcoded |
| `llm_model` | string | `TBD` | Modelo usado pelos dois agentes (definir no Build) |
| `web_search_api_key` | string \| None | `None` | Chave do provider de busca web, se exigida |
| `max_tool_iters` | int | `6` | Teto de chamadas ao LLM por turno |
| `session_ttl_seconds` | int | `3600` | Tempo de vida de uma sessão em memória |

---

## Security Considerations

- Nenhuma credencial de conta financeira (Itaú/Livelo) é solicitada, armazenada ou usada — Agente de Milhas trabalha apenas com o saldo informado em texto pelo usuário e com bônus públicos buscados na web.
- Nenhuma etapa de checkout/pagamento existe no sistema — elimina superfície de dados sensíveis de pagamento (fora de escopo, ver DEFINE).
- API keys (LLM, web search) apenas via variáveis de ambiente (`.env`, nunca commitado — já coberto por `.gitignore`).
- Sessões em memória: dados de conversa não persistem além do processo — aceitável para MVP de uso pessoal solo, sem exposição pública planejada.
- Se a API vier a ser exposta fora de `localhost`, adicionar autenticação simples (ex: API key estática via header) antes — não incluído no MVP por ser uso local (KB `autenticacao` disponível para quando for necessário).

---

## Observability

| Aspect | Implementation |
|--------|------------------|
| Logging | Log estruturado (JSON) por turno — `session_id`, tools chamadas, latência, erros — sem logar payload bruto de dados potencialmente sensíveis (ex: saldo de pontos) |
| Metrics | Fora de escopo do MVP — projeto solo, sem infraestrutura de monitoramento ainda |
| Tracing | Fora de escopo do MVP — reavaliar se o uso crescer além de pessoal |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|-----------|
| 1.0 | 2026-08-06 | design-agent | Versão inicial, a partir de DEFINE_MULTIAGENTE_VIAGENS.md |
| 1.1 | 2026-08-10 | ship-agent | Shipped e arquivado |

---

## Next Step

**Ready for:** `/build .claude/sdd/features/DESIGN_MULTIAGENTE_VIAGENS.md`
