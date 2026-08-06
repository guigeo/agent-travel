<!-- Prosa em português; código, nomes de API e keywords técnicas em inglês. Convenção: .claude/kb/_index.yaml -->
# Suite de regressão de prompts: casos versionados + verificação de comportamento

> **Propósito**: Tratar mudança de prompt como mudança de código — suite de casos que roda antes de qualquer merge, comparando comportamento (não valores exatos) contra o esperado.
> **Validado**: 2026-08-06 (prática consolidada em avaliação de LLM; ver `agentes-llm/patterns/benchmark-comportamental-yaml.md` para uma implementação completa em agente com tools)

## Quando usar

- Todo prompt que já teve um "funcionava, parou de funcionar depois que editei uma
  frase".
- Antes de qualquer edição em system prompt de produção — rodar a suite primeiro,
  editar, rodar de novo.
- Especialmente crítico quando múltiplas pessoas editam o mesmo prompt ao longo do
  tempo.

## Implementação

```yaml
# casos.yaml — cada caso é comportamento esperado, não string exata
- id: recusa-fora-de-escopo
  input: "Qual o preço do concorrente X?"
  espera:
    tipo: recusa
    nao_deve_conter: ["não sei", "desculpe"]   # frases genéricas = recusa fraca
    deve_oferecer_alternativa: true

- id: extracao-com-schema
  input: "João Silva, joao@ex.com, quer o plano Enterprise"
  espera:
    tipo: structured_output
    schema: ContactExtraction
    campos_obrigatorios: [nome, email, plano]

- id: formato-de-resposta
  input: "Resuma esse contrato em 3 pontos"
  espera:
    tipo: texto
    formato: lista_numerada
    max_itens: 3
```

```python
def rodar_suite(casos: list[dict], prompt_versao: str, llm) -> list[dict]:
    resultados = []
    for caso in casos:
        saida = llm.create(system=prompt_versao, user=caso["input"])
        ok = verificar(caso["espera"], saida)          # 1 verificador por "tipo"
        resultados.append({"id": caso["id"], "passou": ok, "saida": saida})
    return resultados

def diff_entre_versoes(casos, prompt_antigo, prompt_novo, llm):
    """O que importa numa mudança: quais casos MUDARAM de resultado, não a nota geral."""
    antes = {r["id"]: r["passou"] for r in rodar_suite(casos, prompt_antigo, llm)}
    depois = {r["id"]: r["passou"] for r in rodar_suite(casos, prompt_novo, llm)}
    return {cid: (antes[cid], depois[cid]) for cid in antes if antes[cid] != depois[cid]}
```

## Configuração

| Decisão | Padrão recomendado | Descrição |
|---|---|---|
| O que verificar | comportamento (tipo de resposta, presença de campo, formato) | Valor exato quebra com qualquer variação legítima do modelo |
| Cobertura mínima | 1 caso por regra do prompt + casos de borda conhecidos | Toda regra sem caso de teste eventualmente quebra sem ninguém notar |
| Quando rodar | antes de mergear qualquer edição de prompt | Edição de 1 frase pode regredir 3 regras não relacionadas |
| Custo | rodar com LLM real (não mock) — é o que valida POLÍTICA | Testes offline (fake client) validam mecanismo, não qualidade |
| Diff de versão | comparar caso a caso, não score agregado | Score agregado esconde qual regra especificamente regrediu |

## Exemplo de uso

```python
mudancas = diff_entre_versoes(casos, prompt_v1, prompt_v2, llm)
if any(antes and not depois for antes, depois in mudancas.values()):
    raise RegressaoDetectada(mudancas)   # bloqueia merge se algo que passava parou de passar
```

## Ver também

- [ambiguidade-e-overfitting-em-poucos-exemplos](../concepts/ambiguidade-e-overfitting-em-poucos-exemplos.md)
- [structured-output-json-schema](structured-output-json-schema.md)
