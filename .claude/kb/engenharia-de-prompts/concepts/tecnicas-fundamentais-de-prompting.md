<!-- Prosa em português; código, nomes de API e keywords técnicas em inglês. Convenção: .claude/kb/_index.yaml -->
# Few-shot e chain-of-thought: quando cada técnica ajuda

> **Propósito**: Escolher a técnica certa por classe de tarefa — exemplos ancoram formato/estilo, raciocínio passo a passo ancora lógica multi-step.
> **Confiança**: 0.9
> **Validado**: 2026-08-06 (Anthropic Prompt Engineering Interactive Tutorial, capítulos 6-7 "Precognition" e "Using Examples"; OpenAI cookbook de structured outputs)

## Visão geral

Duas técnicas resolvem problemas diferentes e são compostas, não excludentes.
**Few-shot** (mostrar exemplos de entrada→saída) ancora *forma*: formato de resposta,
tom, nível de detalhe, fronteira entre classes numa tarefa de classificação.
**Chain-of-thought** (pedir para "pensar passo a passo" antes da resposta final)
ancora *lógica*: problemas que exigem decompor, comparar ou encadear inferências.
Usar few-shot para ensinar chain-of-thought é comum: os exemplos mostram o raciocínio
completo, não só a resposta final — o modelo aprende o *processo*, não só o formato.

## O padrão

```text
# Few-shot — ancora formato/estilo
<examples>
<example>
<input>Cliente pergunta sobre reembolso de item quebrado</input>
<output>Classificação: reembolso | Prioridade: alta | Ação: abrir ticket categoria "produto-danificado"</output>
</example>
<example>
<input>Cliente pergunta prazo de entrega</input>
<output>Classificação: informação | Prioridade: baixa | Ação: nenhuma</output>
</example>
</examples>

# Chain-of-thought — ancora raciocínio multi-step
Antes de responder, pense passo a passo dentro de <thinking></thinking>:
1. Quais fatos relevantes o input contém?
2. Qual regra de negócio se aplica?
3. Qual é a conclusão?
Depois, dê a resposta final em <answer></answer>.
```

## Referência rápida

| Sintoma | Técnica | Por quê |
|---|---|---|
| Formato de saída inconsistente | few-shot (2-4 exemplos diversos) | Exemplo vale mais que descrição do formato |
| Erro de lógica em problema multi-step | chain-of-thought | Força decomposição antes da resposta final |
| Classificação com categorias ambíguas | few-shot com 1 exemplo por classe | Exemplo desambigua a fronteira entre categorias |
| Tarefa simples de extração/lookup | nenhuma das duas | Custo extra de tokens sem ganho — CoT pode até piorar |

## Erros comuns

### Errado

```text
15 exemplos de um único caso de borda, todos praticamente idênticos entre si
→ o modelo generaliza para ESSE padrão específico, não para a tarefa completa
```

### Certo

```text
2-4 exemplos DIVERSOS, um por classe de comportamento esperado
(não múltiplas variações sintáticas do mesmo caso)
```

## Relacionados

- [anatomia-do-system-prompt](anatomia-do-system-prompt.md)
- [ambiguidade-e-overfitting-em-poucos-exemplos](ambiguidade-e-overfitting-em-poucos-exemplos.md)
- [suite-de-regressao-de-prompts](../patterns/suite-de-regressao-de-prompts.md)
