# BRAINSTORM: Sistema Multiagente de Planejamento de Viagens

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | MULTIAGENTE_VIAGENS |
| **Date** | 2026-08-06 |
| **Author** | brainstorm-agent |
| **Status** | ✅ Shipped |

---

## Initial Idea

**Raw Input:** "Quero criar um sistema multiagente que me ajude a planejar minhas viagens, tenho muita dificuldade de me programar (comprar as passagens, hoteis e etc). Tem um ponto que a aplicação também deve ter: tenho muitos pontos no cartão do Itaú e preciso trocar em um programa de milhas que me dê um percentual legal na troca. Sugira ideias, quero algo robusto e assertivo."

**Context Gathered:**
- Projeto em estágio greenfield — apenas scaffolding do template (`.claude/`), sem código-fonte ainda.
- CLAUDE.md já descreve o projeto como "app de chat com IA para ajudar no planejamento de viagens", stack Python + LLM, projeto solo.
- KB já possui domínio `agentes-llm` documentando especificamente o padrão "agente com function calling sem framework — loop explícito, tools tipadas, grounding determinístico", que se encaixa diretamente na abordagem escolhida.
- Demais KBs relevantes já existentes no projeto: `engenharia-de-prompts`, `padroes-rag`, `rest-api-design`, `autenticacao`.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | `src/` (a criar) | Estrutura ainda não existe; Define/Design deverão propor layout (ex: `src/orchestrator/`, `src/agents/`, `src/api/`) |
| Relevant KB Domains | `agentes-llm`, `engenharia-de-prompts`, `rest-api-design`, `autenticacao` | Consultar para padrões de loop de tools, prompts, design da API e auth de usuário |
| IaC Patterns | N/A (projeto solo, sem infra definida) | Deploy/infra fora de escopo deste brainstorm |

---

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | Até onde o sistema deve ir na "compra" de passagens/hotéis? | Assistente/decisor: pesquisa, compara e recomenda; usuário finaliza a compra manualmente. Sem guardar dados de pagamento. | Elimina necessidade de integração com pagamento e checkout automatizado no MVP — reduz drasticamente escopo e risco. |
| 2 | O que o sistema deve fazer com pontos Itaú → milhas? | Monitorar bônus de transferência e avisar quando surgir boa oportunidade, considerando saldo de pontos do usuário. | Define a necessidade de um "Agente de Milhas" com lógica de cálculo de valor efetivo por ponto. |
| 3 | Como o usuário vai interagir com o assistente? | API web + frontend simples (não CLI, não WhatsApp no MVP). | Define stack de interface: backend Python expõe API REST/chat, consumível via navegador. |
| 4 | Já existe acesso a APIs pagas de voos/hotéis (Amadeus, Skyscanner, Booking)? | Nenhuma API paga ainda — MVP usa web search via LLM para cotações. | Reduz custo e complexidade de integração inicial; aceita menor precisão em troca de velocidade de entrega. |
| 5 | O Agente de Milhas deve ser proativo (monitoramento em background + notificação) ou sob demanda? | Sob demanda, e **desacoplado do planejador de viagem** — o planejamento de viagem deve funcionar de forma completamente independente de milhas; milhas só entra quando o usuário pedir explicitamente. | Decisão arquitetural chave: elimina necessidade de scheduler/job em background e canal de notificação (email/push) no MVP. Define o Agente de Milhas como módulo isolado, não uma dependência do fluxo principal. |

**Minimum Questions:** 3 (atingido — 5 perguntas feitas)

---

## Sample Data Inventory

> Samples improve LLM accuracy through in-context learning and few-shot prompting.

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input files | N/A | 0 | Nenhuma amostra disponível ainda |
| Output examples | N/A | 0 | Nenhuma amostra disponível ainda |
| Ground truth | N/A | 0 | Nenhuma amostra disponível ainda |
| Related code | N/A | 0 | Projeto greenfield, sem código relacionado |

**How samples will be used:**

- Nenhuma amostra disponível nesta fase. O assistente se apoiará em conhecimento geral do LLM + web search para grounding. Se o usuário reunir roteiros/planilhas antigas ou regras de conversão de pontos no futuro, podem ser incorporadas via `/iterate`.

---

## Approaches Explored

### Approach A: Orquestrador + subagentes especializados, sem framework ⭐ Recomendada

**Description:** Um agente orquestrador central conversa com o usuário, entende a viagem (destino, datas, orçamento, preferências) e aciona subagentes especializados via function calling explícito:
- **Agente de Voos** — pesquisa e compara rotas/preços (via web search no MVP)
- **Agente de Hospedagem** — idem para hotéis
- **Agente de Roteiro** — monta itinerário dia-a-dia
- **Agente de Orçamento** — consolida custos totais e alerta se estourar o budget
- **Agente de Milhas** — módulo independente, calcula valor efetivo de bônus de transferência Itaú→parceiros (Livelo/Iupp→Latam Pass, Smiles, TudoAzul etc.), acionado sob demanda

**Pros:**
- Alinhado com a KB `agentes-llm` já existente no projeto (loop explícito, tools tipadas, grounding determinístico)
- Controle total do código, sem dependência de framework externo
- Separação de responsabilidades facilita testar e evoluir cada agente isoladamente
- Agente de Milhas desacoplado não vira gargalo/dependência do fluxo principal de planejamento

**Cons:**
- Mais código de "cola" (orquestração, roteamento) escrito manualmente vs. usar um framework pronto

**Why Recommended:** Reaproveita padrão já documentado no projeto, evita lock-in e overhead de aprendizado de ferramenta nova para um projeto solo, e mapeia diretamente para os requisitos de independência entre planejamento e milhas.

---

### Approach B: Framework de multiagentes (LangGraph/CrewAI)

**Description:** Mesma divisão de subagentes, mas orquestrados por um framework pronto com grafo de estados e checkpointing embutido.

**Pros:**
- Menos código de orquestração manual
- Ferramentas de state management e checkpointing prontas

**Cons:**
- Curva de aprendizado extra para um projeto solo
- Dependência pesada e menos controle fino sobre o loop de tool-calling
- Diverge do padrão já documentado na KB `agentes-llm` do projeto

---

### Approach C: Agente único com muitas tools (sem subagentes separados)

**Description:** Um só agente com acesso a todas as ferramentas (buscar_voos, buscar_hoteis, calcular_milhas...), sem camada de orquestração entre "agentes".

**Pros:**
- Menos peças móveis inicialmente

**Cons:**
- Mistura responsabilidades de domínios distintos (viagem vs. milhas) em um único agente, dificultando manter a independência exigida entre planejamento e milhas
- Mais difícil de testar/evoluir cada capacidade isoladamente

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | Approach A |
| **User Confirmation** | 2026-08-06 |
| **Reasoning** | Reaproveita o padrão de agentes já documentado na KB do projeto, mantém controle total do código sem dependências pesadas, e viabiliza naturalmente a independência exigida entre o planejador de viagem e o Agente de Milhas. |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|----------------------|
| 1 | Sistema é assistente/decisor, não executa compras | Reduz risco financeiro/legal e complexidade de integração com pagamento/checkout | Compra assistida com confirmação; compra autônoma |
| 2 | Agente de Milhas é desacoplado do planejador de viagem | Usuário quer que o planejamento funcione 100% independente de milhas; milhas é opt-in | Integrar milhas como etapa obrigatória do orçamento |
| 3 | Agente de Milhas funciona sob demanda, sem background/notificação | Elimina necessidade de scheduler e canal de notificação (email/push) no MVP | Monitoramento proativo em background com alertas |
| 4 | Interface via API web + frontend simples | Acesso de qualquer lugar via navegador, mais flexível que CLI para uso contínuo | CLI/terminal; bot WhatsApp/Telegram |
| 5 | Sem APIs pagas de voos/hotéis no MVP | Evita custo e complexidade de integração antes de validar o conceito | Contratar Amadeus/Skyscanner/Booking desde já |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| Compra/reserva automática de passagens e hotéis | Usuário confirmou papel de assistente/decisor; execução da compra fica manual | Yes |
| Transferência automática de pontos (Itaú→Livelo→cia aérea) | Exigiria login/integração com contas financeiras — risco alto para MVP solo | Yes |
| Integração WhatsApp/Telegram | Usuário optou por API web; outro canal pode reaproveitar a mesma API depois | Yes |
| APIs pagas de voos/hotéis (Amadeus, Skyscanner, Booking) | Usuário optou por começar sem custo, usando web search | Yes, quando precisão virar prioridade |
| Monitoramento em background + notificação proativa de bônus de milhas | Usuário confirmou preferir consulta sob demanda, desacoplada do planejador | Yes |
| Multi-usuário / contas de terceiros | Projeto é uso pessoal solo | Yes, se necessidade mudar |

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| Escolha da Abordagem A vs B vs C | ✅ | Confirmou Abordagem A sem ressalvas | No |
| Modo de operação do Agente de Milhas (notificação) | ✅ | Corrigiu o entendimento inicial: agente de milhas deve ser **independente** do planejador, não apenas "sem notificação" — reformulação necessária | Yes — arquitetura ajustada para desacoplamento explícito |
| Desenho consolidado final (orquestrador independente + milhas sob demanda + stack) | ✅ | Aprovado sem ajustes | No |

**Minimum Validations:** 2 (atingido — 3 validações realizadas)

---

## Suggested Requirements for /define

Based on this brainstorm session, the following should be captured in the DEFINE phase:

### Problem Statement (Draft)
Planejar uma viagem envolve juntar informação espalhada (voos, hospedagem, roteiro, orçamento) e tomar várias decisões manualmente, incluindo decidir separadamente se/quando vale a pena trocar pontos do cartão Itaú por milhas — um sistema multiagente pode assumir a pesquisa, comparação e recomendação em ambas as frentes, mantendo-as independentes entre si.

### Target Users (Draft)
| User | Pain Point |
|------|------------|
| Guilherme (usuário único, projeto solo) | Dificuldade de organizar/pesquisar voos, hotéis e roteiro manualmente; falta de visibilidade sobre quando vale trocar pontos Itaú por milhas com bom bônus |

### Success Criteria (Draft)
- [ ] Orquestrador consegue conduzir uma conversa completa de planejamento (destino, datas, orçamento, preferências) e produzir recomendação de voos, hospedagem e roteiro
- [ ] Agente de Orçamento consolida custo total estimado e sinaliza se estourou o budget informado
- [ ] Agente de Milhas responde sob demanda com cálculo de valor efetivo (ex: centavos por ponto) considerando bônus vigente informado/buscado
- [ ] Planejador de viagem funciona de ponta a ponta sem nenhuma dependência do Agente de Milhas
- [ ] API web expõe o chat e é consumível por um frontend simples

### Constraints Identified
- Sem integração de pagamento/checkout automatizado
- Sem credenciais de contas financeiras (Itaú/Livelo) armazenadas ou usadas para ações automáticas
- Sem APIs pagas de voos/hotéis no MVP — depende de web search
- Sem infraestrutura de scheduler/notificação (email/push) no MVP
- Projeto solo — sem necessidade de multi-tenancy/multi-usuário

### Out of Scope (Confirmed)
- Compra ou reserva automática de passagens/hotéis
- Transferência automática de pontos entre programas
- Monitoramento em background com notificação proativa de bônus de milhas
- Canais WhatsApp/Telegram
- Suporte a múltiplos usuários/contas de terceiros

---

## Session Summary

| Metric | Value |
|--------|-------|
| Questions Asked | 5 |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 6 |
| Validations Completed | 3 |
| Duration | ~1 sessão de diálogo |

---

## Next Step

**Ready for:** `/define .claude/sdd/features/BRAINSTORM_MULTIAGENTE_VIAGENS.md`
