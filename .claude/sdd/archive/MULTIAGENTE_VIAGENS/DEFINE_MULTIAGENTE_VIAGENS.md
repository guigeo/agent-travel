# DEFINE: Sistema Multiagente de Planejamento de Viagens

> Assistente multiagente que ajuda a planejar viagens (voos, hospedagem, roteiro, orçamento) e, de forma independente, avalia quando vale a pena trocar pontos Itaú por milhas.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | MULTIAGENTE_VIAGENS |
| **Date** | 2026-08-06 |
| **Author** | define-agent |
| **Status** | ✅ Shipped |
| **Clarity Score** | 14/15 |

---

## Problem Statement

Guilherme tem dificuldade em organizar o planejamento de uma viagem (pesquisar e comparar voos, hospedagem, montar roteiro e controlar orçamento) porque a informação está espalhada em várias fontes e exige várias decisões manuais. Separadamente, ele acumula pontos no cartão Itaú e não tem visibilidade clara de quando um bônus de transferência para um programa de milhas (Livelo/Iupp → Latam Pass, Smiles, TudoAzul etc.) é vantajoso o suficiente para trocar.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Guilherme | Usuário único, projeto solo (uso pessoal) | Perde tempo pesquisando/comparando voos, hotéis e roteiro manualmente; não tem uma forma rápida de saber se vale trocar pontos Itaú por milhas em um dado momento |

---

## Goals

What success looks like (prioritized):

| Priority | Goal |
|----------|------|
| **MUST** | Orquestrador conduz uma conversa de planejamento (destino, datas, orçamento, preferências) e produz recomendação de voos, hospedagem e roteiro dia-a-dia |
| **MUST** | Agente de Orçamento consolida o custo total estimado e sinaliza claramente quando estoura o budget informado |
| **MUST** | Agente de Milhas funciona como módulo totalmente independente — o planejador de viagem nunca depende dele para operar |
| **MUST** | Backend em Python (FastAPI) expõe o chat via API REST |
| **SHOULD** | Agente de Milhas calcula, sob demanda, o valor efetivo de um bônus de transferência de pontos (ex: centavos por ponto) considerando o saldo informado pelo usuário |
| **SHOULD** | Frontend web simples para consumir a API de chat (sem precisar de terminal) |
| **COULD** | Agente de Orçamento considerar milhas no cálculo de custo, mas somente se o usuário pedir explicitamente |

**Priority Guide:**
- **MUST** = MVP fails without this
- **SHOULD** = Important, but workaround exists
- **COULD** = Nice-to-have, cut first if needed

---

## Success Criteria

Measurable outcomes:

- [ ] Orquestrador completa o fluxo de planejamento (voo + hospedagem + roteiro + orçamento) em uma única sessão de conversa, sem exigir reinício ou dados fora do chat
- [ ] 100% das funcionalidades do planejador de viagem operam corretamente com zero chamadas ao Agente de Milhas (valida o desacoplamento)
- [ ] Agente de Milhas responde a uma consulta isolada (sem viagem em andamento) com cálculo de valor efetivo por ponto, baseado em bônus buscado via web
- [ ] Zero armazenamento de credenciais de pagamento ou de contas financeiras (Itaú/Livelo) no sistema
- [ ] Toda recomendação de voo/hotel apresentada ao usuário é rastreável à busca/fonte usada (grounding via web search)

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | Planejamento completo (happy path) | Usuário informa destino, datas e orçamento máximo | Usuário pede um plano de viagem | Orquestrador retorna recomendação de voos, hospedagem, roteiro dia-a-dia e resumo de orçamento, sem qualquer menção a milhas |
| AT-002 | Consulta de milhas isolada | Usuário não tem nenhuma viagem em planejamento ativa | Usuário pergunta "vale a pena trocar meus pontos Itaú agora?" | Agente de Milhas responde normalmente, buscando bônus vigentes, sem exigir contexto de viagem associada |
| AT-003 | Orçamento estourado | Usuário definiu orçamento máximo X | Recomendações de voo + hotel somadas excedem X | Agente de Orçamento sinaliza claramente o estouro e sugere ajustes, sem bloquear a recomendação |
| AT-004 | Limite de escopo (compra) | Usuário recebeu uma recomendação de voo | Usuário pede para o sistema "comprar a passagem agora" | Sistema explica que apenas recomenda e que a compra deve ser finalizada manualmente pelo usuário no site/app oficial |

---

## Out of Scope

Explicitly NOT included in this feature:

- Compra ou reserva automática de passagens/hotéis (nem assistida com confirmação) — sistema é assistente/decisor apenas
- Transferência automática de pontos Itaú → programa de milhas
- Monitoramento em background com notificação proativa (email/push) de bônus de milhas
- Integração com WhatsApp/Telegram
- APIs pagas de voos/hotéis (Amadeus, Skyscanner, Booking) — busca via web search no MVP
- Suporte a múltiplos usuários/contas de terceiros

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | Toda instalação/gestão de dependências Python deve usar **uv** (`uv init`, `uv add`, `uv run`, `uv sync`), nunca pip/venv global | Design e Build devem especificar comandos `uv`; nenhum pacote instalado globalmente na máquina |
| Technical | Sem integração de pagamento/checkout | Nenhuma etapa de compra automatizada aparece no design |
| Technical | Sem armazenamento de credenciais de contas financeiras (Itaú/Livelo) | Agente de Milhas opera só com saldo informado manualmente pelo usuário + busca pública de bônus |
| Resource | Sem orçamento para APIs pagas de voos/hotéis no MVP | Cotações via web search (menor precisão aceita em troca de custo zero) |
| Resource | Projeto solo, sem equipe/timeline formal | Prioriza escopo mínimo funcional sobre robustez de produto |

---

## Technical Context

> Essential context for Design phase - prevents misplaced files and missed infrastructure needs.

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `src/` (a criar) — ex: `src/orchestrator/`, `src/agents/{voos,hospedagem,roteiro,orcamento,milhas}/`, `src/api/` | Estrutura ainda não existe; Design deve propor layout definitivo |
| **KB Domains** | `agentes-llm`, `engenharia-de-prompts`, `rest-api-design`, `autenticacao` | `agentes-llm` para o loop de function calling dos subagentes; `engenharia-de-prompts` para os system prompts; `rest-api-design` para a API FastAPI; `autenticacao` avaliar se é necessária (uso solo, mas API exposta) |
| **IaC Impact** | None / TBD | Projeto solo, sem infraestrutura de deploy definida ainda |

**Why This Matters:**

- **Location** → Design phase uses correct project structure, prevents misplaced files
- **KB Domains** → Design phase pulls correct patterns from `.claude/kb/`
- **IaC Impact** → Triggers infrastructure planning, avoids "works locally" failures

---

## Assumptions

Assumptions that if wrong could invalidate the design:

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | Web search via LLM retorna preços/dados de voos e hotéis com precisão suficiente para recomendação, sem API estruturada | Precisão baixa exigiria adotar API paga (Amadeus/Skyscanner) mais cedo do que planejado | [ ] |
| A-002 | Usuário consegue informar e manter atualizado seu saldo de pontos Itaú manualmente no chat | Recomendações do Agente de Milhas ficam desatualizadas; exigiria alguma forma de consulta de saldo | [ ] |
| A-003 | Bônus de transferência de pontos (Itaú/Livelo/companhias) podem ser encontrados via busca na web no momento da consulta | Exigiria fonte estruturada dedicada (scraping/RSS) para dados confiáveis de bônus | [ ] |

**Note:** Validate critical assumptions before DESIGN phase. Unvalidated assumptions become risks.

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Problema específico, com quem sofre e impacto claros (herdado do brainstorm validado) |
| Users | 3 | Usuário único bem identificado, com pain points claros e distintos (planejamento vs. milhas) |
| Goals | 3 | Priorizados em MUST/SHOULD/COULD, cobrindo todos os subagentes e o desacoplamento do Agente de Milhas |
| Success | 2 | Critérios testáveis e claros, mas nem todos quantificados numericamente (natureza qualitativa do domínio) |
| Scope | 3 | Out of Scope explícito e extenso, herdado diretamente das decisões de YAGNI do brainstorm |
| **Total** | **14/15** | |

**Scoring Guide:**
- 0 = Missing entirely
- 1 = Vague or incomplete
- 2 = Clear but missing details
- 3 = Crystal clear, actionable

**Minimum to proceed: 12/15**

---

## Open Questions

None - ready for Design.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-08-06 | define-agent | Versão inicial, extraída de BRAINSTORM_MULTIAGENTE_VIAGENS.md |
| 1.1 | 2026-08-10 | ship-agent | Shipped e arquivado |

---

## Next Step

**Ready for:** `/design .claude/sdd/features/DEFINE_MULTIAGENTE_VIAGENS.md`
