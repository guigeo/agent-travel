<!-- Prosa em português; código, nomes de API e keywords técnicas em inglês. Convenção: .claude/kb/_index.yaml -->
# Ambiguidade e overfitting a poucos exemplos

> **Propósito**: Reconhecer os dois modos de falha mais comuns em prompts artesanais — instrução ambígua (o modelo "decide" a política sozinho) e few-shot que ensina o caso errado (overfitting sintático).
> **Confiança**: 0.85
> **Validado**: 2026-08-06 (Claude Platform Docs — "golden rule" de clareza; observação consolidada em avaliação de prompts comportamentais)

## Visão geral

Dois defeitos dominam prompts que "funcionam no teste manual mas falham em produção".
**Ambiguidade**: a instrução admite mais de uma leitura razoável, e o modelo escolhe
uma consistentemente errada para o caso de uso ("seja útil" não diz o que fazer numa
pergunta fora de escopo). **Overfitting a few-shot**: poucos exemplos, todos muito
parecidos entre si, ensinam o modelo a repetir o *padrão sintático* dos exemplos em vez
da tarefa generalizada — o modelo aprende "responda desse jeito" e não "resolva esse
tipo de problema". Os dois se detectam da mesma forma: rodando o prompt contra uma
variedade de inputs reais (não só os do dia do design) e observando onde a resposta
diverge do esperado.

## Referência rápida

| Sintoma | Causa provável | Fix |
|---|---|---|
| Modelo às vezes ajuda, às vezes recusa, na mesma classe de pedido | Instrução ambígua sobre escopo | Regra explícita e testável ("fora de X: recuse, zero tool call") |
| Resposta copia estrutura de UM exemplo mesmo quando não se aplica | Overfitting — poucos exemplos, baixa diversidade | Trocar por exemplos DIFERENTES entre si, 1 por classe de comportamento |
| Funciona nos casos de teste, falha em produção | Casos de teste = casos de design, sem cobertura real | Regressão com inputs reais/variados, não só os que motivaram o prompt |
| Modelo "corrige" instrução vaga com sua própria política | Instrução deixou decisão de política pro modelo | Ser explícito: dizer O QUE fazer, não confiar em inferência |

## Erros comuns

### Errado

```text
"Responda perguntas sobre o produto da melhor forma possível."
+ 1 único exemplo de pergunta sobre preço, respondido em 1 frase
→ modelo passa a responder TUDO em 1 frase, mesmo quando pedem detalhe
```

### Certo

```text
"Responda perguntas sobre o produto no nível de detalhe que a pergunta pedir."
+ 2 exemplos: um de pergunta objetiva (resposta curta) e um de pergunta
  aberta (resposta com passos) — a diversidade ensina a REGRA, não a forma
```

## Relacionados

- [tecnicas-fundamentais-de-prompting](tecnicas-fundamentais-de-prompting.md)
- [suite-de-regressao-de-prompts](../patterns/suite-de-regressao-de-prompts.md)
