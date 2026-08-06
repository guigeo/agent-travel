<!-- Prosa em português; código, nomes de API e keywords técnicas em inglês. Convenção: .claude/kb/_index.yaml -->
# Janela de contexto: orçamento de tokens, não armazenamento ilimitado

> **Propósito**: Tratar a janela de contexto como orçamento finito a ser alocado entre system prompt, histórico e dado recuperado — não como um buffer que cresce livremente.
> **Confiança**: 0.95
> **Validado**: 2026-08-06 (OpenAI Agents SDK "Context Engineering — Session Memory" cookbook; Anthropic "Effective context engineering for AI agents"; Microsoft Agent Framework compaction docs)

## Visão geral

A janela de contexto é o total de tokens (entrada + saída) que o modelo processa numa
chamada. Mesmo janelas grandes (100k+ tokens) degradam com histórico não curado: tool
results verbosos, mensagens redundantes e ruído empurram a instrução do sistema para o
"meio esquecido" do contexto. A disciplina correta não é "caber tudo", é orçar: reservar
uma fatia fixa para system prompt + instrução corrente, e outra fatia — com teto — para
histórico de conversa. Quando o histórico ultrapassa o teto, ele precisa ser reduzido
antes de crescer mais, não depois.

## O padrão

```text
Orçamento típico de uma chamada:
┌──────────────────────────────────────────┐
│ system prompt + tools                (fixo)│  ~500-2000 tokens
│ contexto recuperado (RAG/dados)      (fixo)│  conforme necessidade
│ histórico de conversa             (variável)│  teto configurável
│ mensagem atual do usuário            (fixo)│
└──────────────────────────────────────────┘

Regra de ouro: histórico tem TETO (contagem de turnos ou tokens).
Ao ultrapassar, aplicar UMA estratégia de redução — nunca deixar crescer.
```

## Referência rápida

| Estratégia | Preserva contexto | Custo extra | Quando usar |
|---|---|---|---|
| Truncar (últimas N mensagens) | Baixo — perde fatos antigos | Nenhum | Conversas curtas, sem dependência de fatos antigos |
| Sliding window (últimos N turnos completos) | Baixo-médio — respeita fronteira de turno | Nenhum | Teto rígido de turnos, tool calls presentes |
| Sumarização (resumo do que ficou de fora) | Alto — preserva decisões/fatos | 1 chamada extra ao LLM | Conversas longas onde fatos antigos importam |
| Memória externa (fatos extraídos, fora da janela) | Muito alto — sobrevive à sessão | Escrita/leitura externa | Preferências e fatos que devem persistir entre sessões |

## Erros comuns

### Errado

```python
# Truncar por contagem simples de mensagens, ignorando pares tool_call/tool_result
messages = messages[-10:]   # pode cortar um tool_call sem seu tool_result
# → a API rejeita a sequência (mensagem órfã) ou o modelo alucina o resultado
```

### Certo

```python
# Truncar em fronteira de TURNO (mensagem do usuário = início de turno),
# preservando pares tool_call/tool_result completos dentro do turno mantido
```

## Relacionados

- [compactacao-de-historico-de-conversa](../patterns/compactacao-de-historico-de-conversa.md)
- [anatomia-do-system-prompt](anatomia-do-system-prompt.md)
