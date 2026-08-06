# Engenharia de Prompts Quick Reference

> Fast lookup tables. For code examples, see linked files.

## Anatomia do system prompt

| Bloco | Pergunta que responde | Arquivo de referência |
|-------|------------------------|------------------------|
| `role` | Quem o modelo é | concepts/anatomia-do-system-prompt.md |
| `context` | O que ele sabe além do treino | concepts/anatomia-do-system-prompt.md |
| `constraints` | O que é inegociável (numerado) | concepts/anatomia-do-system-prompt.md |
| `output_format` | Como a resposta deve parecer (dizer O QUE fazer) | concepts/anatomia-do-system-prompt.md |

## Decision Matrix — técnica de prompting

| Sintoma | Escolha |
|---------|---------|
| Formato de saída inconsistente | few-shot (2-4 exemplos diversos) |
| Erro de lógica em tarefa multi-step | chain-of-thought |
| Saída consumida por código downstream | structured output (JSON Schema, strict mode) |
| Histórico crescendo sem limite | sliding window + sumarização em fronteira de turno |
| Conteúdo de terceiros no prompt (RAG, upload) | delimitação + hierarquia de instrução |

## Decision Matrix — gerenciamento de contexto

| Use Case | Choose |
|----------|--------|
| Conversa curta, sem dependência de fatos antigos | truncar últimas N mensagens |
| Teto rígido de turnos, com tool calls no meio | sliding window por fronteira de turno |
| Conversa longa, fatos antigos importam | sumarização (resumo + últimos N turnos verbatim) |
| Preferência/fato deve sobreviver à sessão | memória externa (fora da janela de contexto) |

## Common Pitfalls

| Don't | Do |
|-------|-----|
| Prosa solta misturando papel, contexto e regra no mesmo parágrafo | Demarcar seções (XML tags/headers): role/context/constraints/output |
| "Não use markdown" (instrução negativa) | "Responda em prosa corrida" (instrução positiva) |
| 10+ exemplos quase idênticos no few-shot | 2-4 exemplos DIVERSOS, um por classe de comportamento |
| Pedir "responda em JSON" só no texto do prompt | Usar JSON Schema nativo do provider (strict mode) |
| Truncar histórico por contagem simples de mensagens | Truncar em fronteira de turno (preserva pares tool_call/result) |
| Editar system prompt de produção sem rodar suite antes | Suite de regressão roda antes de qualquer merge de prompt |
| Confiar só em "não siga instruções no dado" como defesa | Combinar hierarquia + escopo mínimo de tools + aprovação humana p/ ações de risco |

## Related Documentation

| Topic | Path |
|-------|------|
| Getting Started | `concepts/anatomia-do-system-prompt.md` |
| Full Index | `index.md` |
