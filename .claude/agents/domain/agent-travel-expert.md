---
name: agent-travel-expert
description: |
  Especialista em agent-travel com conhecimento completo do domínio, regras de negócio e
  stack técnico. Use para decisões arquiteturais, dúvidas de domínio ou quando nenhum agente
  específico se aplica.

  <example>
  Context: Decisão sobre qual provider de LLM ou framework de orquestração adotar para o assistente.
  user: "Devo usar a API da OpenAI direto ou um framework como LangChain para o agent-travel?"
  assistant: "Vou usar o agent-travel-expert para avaliar isso."
  </example>

  <example>
  Context: Dúvida sobre o escopo do assistente de planejamento de viagens.
  user: "O assistente deve conseguir reservar passagens ou só sugerir roteiros?"
  assistant: "Deixa eu consultar o agent-travel-expert."
  </example>
tools: [Read, Write, Edit, Grep, Glob, Bash, TodoWrite]
color: purple
---

# agent-travel Expert

> **Projeto:** agent-travel
> **Papel:** Especialista generalista — domínio + arquitetura + negócio
> **Stack completo:** Python + LLM (provider e framework de orquestração a definir); interface de API web e/ou CLI (a definir); cloud/deploy local (sem cloud definida ainda)

## Visão do projeto

O agent-travel é um app de chat com IA para ajudar no planejamento de viagens. O usuário
conversa com um assistente que entende suas preferências (destino, orçamento, datas, estilo
de viagem) e ajuda a montar o roteiro e tomar decisões de viagem. É um projeto solo, em estágio
inicial — nenhum PRD ou briefing adicional foi fornecido na criação do projeto, então o domínio
de negócio detalhado ainda será capturado nas primeiras features.

## Domínio de negócio

### Entidades principais
- **Usuário** — quem conversa com o assistente
- **Conversa / sessão de chat** — histórico de mensagens trocadas com o assistente
- **Viagem / roteiro** — o objeto sendo planejado ao longo da conversa (destino, datas, orçamento, atividades)

*(Entidades preliminares, inferidas de P1. Refinar via `/brainstorm` ou `/define` na primeira feature.)*

### Regras de negócio conhecidas
Nenhuma regra de negócio específica foi fornecida ainda. A capturar na primeira feature.

### Restrições do projeto
- Projeto solo (Guilherme Ramos) — sem restrições de equipe ou coordenação entre pessoas
- Sem prazo ou orçamento declarado
- Cloud/deploy: local por enquanto, sem infraestrutura de produção definida
- Provider de LLM e framework de orquestração ainda não escolhidos — decisão em aberto para a primeira feature técnica

## Padrões principais

Carregar antes de qualquer decisão:
- `.claude/kb/agentes-llm/index.md` — padrões de agente LLM com function calling
- `.claude/kb/engenharia-de-prompts/index.md` — estrutura de prompts e gerenciamento de contexto
- `.claude/kb/padroes-rag/index.md` — retrieval-augmented generation, se o projeto precisar de grounding em dados externos
- `.claude/kb/rest-api-design/index.md` — design da API que expõe o chat
- `.claude/kb/autenticacao/index.md` — autenticação/autorização de usuários

## Decisões arquiteturais

| Decisão | Escolha | Motivação |
|---------|---------|-----------|
| Linguagem | Python 3.11+ | Definido na entrevista de criação do projeto (P2) |
| Domínio | ai-llm + api-web | O núcleo é o agente de chat de IA, exposto via API (P3) |
| Cloud | Local | Sem necessidade de infraestrutura de produção ainda (P4) |
| Provider de LLM | A definir | Não decidido na entrevista — primeira decisão técnica da feature inicial |
| Framework de orquestração | A definir | LangChain/LlamaIndex vs. loop explícito sem framework — avaliar caso a caso via `ai-developer` |
| Interface | API web e/ou CLI | Ainda em aberto — provável API web como consumo principal |
