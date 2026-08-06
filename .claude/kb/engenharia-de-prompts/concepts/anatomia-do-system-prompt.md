<!-- Prosa em português; código, nomes de API e keywords técnicas em inglês. Convenção: .claude/kb/_index.yaml -->
# Anatomia de um system prompt eficaz

> **Propósito**: Estrutura recorrente que funciona atravessando providers — papel, contexto, restrições e formato de saída, nessa ordem de precedência.
> **Confiança**: 0.95
> **Validado**: 2026-08-06 (Claude Platform Docs "Prompting best practices"; Anthropic "Effective context engineering for AI agents"; padrão convergente OpenAI/Anthropic)

## Visão geral

System prompts eficazes convergem para 4 blocos, independente do provider (OpenAI,
Anthropic, etc.): **papel** (quem o modelo é), **contexto** (o que ele precisa saber
para decidir), **restrições** (regras inegociáveis) e **formato de saída** (como a
resposta deve ser estruturada). A ordem importa: papel e contexto vêm primeiro para
ancorar comportamento; restrições e formato vêm depois, próximos de onde o modelo vai
gerar. Demarcar as seções (XML tags ou headers Markdown) reduz ambiguidade de
interpretação — prosa solta misturando tudo num parágrafo degrada aderência,
especialmente em prompts longos.

## O padrão

```text
<role>
You are [papel específico] specializing in [domínio específico].
</role>

<context>
[Fatos que o modelo precisa para decidir corretamente: dados de negócio,
estado do sistema, ferramentas disponíveis — apenas o que é necessário]
</context>

<constraints>
1. [Regra inegociável, numerada — facilita apontar qual regra falhou]
2. [Regra inegociável]
...
</constraints>

<output_format>
Diga o que fazer, não o que não fazer:
- ERRADO: "Não use markdown"
- CERTO: "Responda em parágrafos de prosa corrida, sem listas"
</output_format>
```

## Referência rápida

| Bloco | Pergunta que responde | Erro comum |
|---|---|---|
| `role` | Quem o modelo é / que expertise assume | Papel genérico demais ("Você é um assistente útil") |
| `context` | O que ele sabe além do treino | Contexto solto sem demarcação — mistura com instrução |
| `constraints` | O que é inegociável | Regra vaga ("seja preciso") em vez de regra testável |
| `output_format` | Como a resposta deve parecer | Instrução negativa ("não faça X") em vez de positiva |

## Erros comuns

### Errado

```text
"Seja um assistente útil e responda as perguntas do usuário da melhor forma possível."
```

(papel vago, sem contexto, sem restrição testável, sem formato — o modelo decide a
política sozinho, e essa decisão varia entre execuções)

### Certo

```text
<role>Você é um assistente de suporte técnico para o produto X, especializado em billing.</role>
<constraints>
1. Todo valor monetário citado vem de uma tool. Nunca calcule de memória.
2. Fora do escopo de billing: recuse e ofereça redirecionar, sem executar nenhuma tool.
</constraints>
<output_format>Responda em até 3 frases, tom direto.</output_format>
```

## Relacionados

- [tecnicas-fundamentais-de-prompting](tecnicas-fundamentais-de-prompting.md)
- [janela-de-contexto-e-gerenciamento-de-historico](janela-de-contexto-e-gerenciamento-de-historico.md)
- [suite-de-regressao-de-prompts](../patterns/suite-de-regressao-de-prompts.md)
