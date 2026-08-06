# agent-travel

> App de chat com IA para ajudar no planejamento de viagens.

---

## Contexto do Projeto

**Problema:** Planejar uma viagem envolve juntar informação espalhada (destinos, roteiros, orçamento, logística) e tomar várias decisões — um processo manual e demorado.

**Solução:** Um assistente de chat baseado em LLM que conversa com o usuário para entender preferências e ajudar a montar o planejamento da viagem (roteiro, sugestões, decisões).

**Stack:** Python + LLM (provider e framework de orquestração a definir — ver Knowledge Base). Interface (API web e/ou CLI) ainda em aberto.

**Equipe:** Projeto solo — Guilherme Ramos.

---

## Visão Geral da Arquitetura

[Execute /sync-context após adicionar arquivos-fonte para gerar esta seção automaticamente]

---

## Estrutura do Projeto

```text
[project-root]/
├── src/           # Código-fonte
├── tests/         # Suítes de teste
└── ...
```

---

## Workflows de Desenvolvimento

### AgentSpec 4.2 (Spec-Driven Development)

```text
/brainstorm → /define → /design → /build → /ship
  (Opus)      (Opus)    (Opus)   (Sonnet)  (Haiku)
```

| Comando | Fase | Propósito |
|---------|------|-----------|
| `/brainstorm` | 0 | Explorar ideias (opcional) |
| `/define` | 1 | Capturar e validar requisitos |
| `/design` | 2 | Criar arquitetura e especificação |
| `/build` | 3 | Executar implementação |
| `/ship` | 4 | Arquivar com lições aprendidas |
| `/iterate` | Qualquer | Atualizar documentos mid-stream |

**Artefatos:** `.claude/sdd/features/` e `.claude/sdd/archive/`

### Dev Loop (Nível 2 Agentico)

```bash
/dev "Quero construir X"              # O crafter te guia
/dev tasks/PROMPT_FEATURE.md          # Executa PROMPT existente
/dev tasks/PROMPT_FEATURE.md --resume # Retoma sessão interrompida
```

**Quando usar:** KBs, protótipos, features isoladas, utilitários

---

## Diretrizes de Uso de Agentes

| Categoria | Agentes | Quando usar |
|-----------|---------|-------------|
| **Workflow** | brainstorm, define, design, build, ship, iterate | Construir features com SDD |
| **Qualidade** | code-reviewer, code-documenter, code-cleaner, python-developer, test-generator | Revisar e melhorar código |
| **AI/ML** | llm-specialist, genai-architect, ai-prompt-specialist, ai-data-engineer | Prompts, RAG, arquitetura do agente de chat |
| **Exploração** | codebase-explorer, kb-architect | Explorar repositório, criar KBs |
| **Comunicação** | adaptive-explainer, meeting-analyst, the-planner | Explicações, planejamento |
| **Domínio** | ai-developer, api-developer, agent-travel-expert | Tarefas específicas do projeto |

---

## Padrões de Código

### Linguagem: Python 3.11+

- **Style:** Ruff
- **Testes:** pytest
- **Validação:** Pydantic v2
- **Type Hints:** Obrigatórios em todas as assinaturas de função

> **Projetos Python — obrigatório:** usar **uv** (não pip/venv). Comandos: `uv init`,
> `uv add <pkg>`, `uv run <cmd>`, `uv sync`; ferramentas one-off com `uvx <ferramenta>`.
> **Nunca instalar pacotes globalmente na máquina** — tudo isolado no ambiente do projeto.

---

## Knowledge Base

| Domínio | Propósito | Ponto de entrada |
|---------|-----------|-----------------|
| agentes-llm | Agente com function calling sem framework — loop explícito, tools tipadas, grounding determinístico | `.claude/kb/agentes-llm/index.md` |
| engenharia-de-prompts | Estrutura de system prompts, few-shot/CoT/structured output, gerenciamento de contexto e histórico | `.claude/kb/engenharia-de-prompts/index.md` |
| padroes-rag | Retrieval-Augmented Generation — chunking, busca híbrida, re-ranking, avaliação de qualidade | `.claude/kb/padroes-rag/index.md` |
| rest-api-design | Design de API REST — recursos/verbos HTTP, erros (RFC 9457), versionamento, paginação | `.claude/kb/rest-api-design/index.md` |
| autenticacao | Autenticação/autorização — JWT, OAuth2/OIDC, RBAC vs. ABAC, hashing de senha | `.claude/kb/autenticacao/index.md` |

Adicione domínios a qualquer momento com `/create-kb "<dominio>"`.

---

## Features Ativas (Em Progresso)

| Feature | Status | Descrição |
|---------|--------|-----------|
| — | — | — |

---

## Features Entregues (Arquivo SDD)

| Feature | Entregue em | Descrição |
|---------|-------------|-----------|
| — | — | — |

---

## Ajuda

- **Workflow SDD:** [.claude/sdd/_index.md](.claude/sdd/_index.md)
- **Exemplos SDD:** [.claude/sdd/examples/](.claude/sdd/examples/)
- **Dev Loop:** [.claude/dev/_index.md](.claude/dev/_index.md)
- **Agentes:** [.claude/agents/](.claude/agents/)
- **KB Index:** [.claude/kb/_index.yaml](.claude/kb/_index.yaml)
