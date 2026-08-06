<!-- Prosa em português; código, nomes de API e keywords técnicas em inglês. Convenção: .claude/kb/_index.yaml -->
# Compactação de histórico: sliding window + sumarização em fronteira de turno

> **Propósito**: Manter a janela de contexto dentro do orçamento sem perder fatos que a conversa estabeleceu — janela deslizante para o recente, resumo para o antigo.
> **Validado**: 2026-08-06 (OpenAI Agents SDK "Context Engineering — Session Memory" cookbook; Microsoft Agent Framework compaction strategies)

## Quando usar

- Conversas multi-turno que podem crescer sem limite (chat de suporte, agente de
  sessão longa).
- Sintoma de que já é tarde: erro de limite de tokens, ou resposta degradando conforme
  a conversa cresce.
- NÃO usar para agentes de turno único (sem histórico a gerenciar) — overhead
  desnecessário.

## Implementação

```python
def eh_inicio_de_turno(msg: dict) -> bool:
    return msg["role"] == "user"

def indice_dos_ultimos_turnos(mensagens: list[dict], n_turnos: int) -> int:
    """Índice onde começam os últimos N turnos completos (user + tudo que segue)."""
    inicios = [i for i, m in enumerate(mensagens) if eh_inicio_de_turno(m)]
    if len(inicios) <= n_turnos:
        return 0
    return inicios[-n_turnos]

def compactar(mensagens: list[dict], manter_ultimos_n: int, resumir) -> list[dict]:
    corte = indice_dos_ultimos_turnos(mensagens, manter_ultimos_n)
    if corte == 0:
        return mensagens                          # ainda dentro do teto, nada a fazer
    antigas, recentes = mensagens[:corte], mensagens[corte:]
    resumo = resumir(antigas)                      # 1 chamada de LLM (modelo pequeno/rápido)
    bloco_resumo = [
        {"role": "user", "content": "Resuma a conversa até aqui.",
         "metadata": {"synthetic": True}},
        {"role": "assistant", "content": resumo,
         "metadata": {"synthetic": True}},
    ]
    return bloco_resumo + recentes                 # fronteira de turno preservada nas recentes
```

Prompt de sumarização — o que precisa sobreviver: decisões tomadas, fatos que o
usuário declarou, preferências, IDs/valores retornados por tools. O que pode ser
descartado: saudações, texto de raciocínio intermediário, tool results já consumidos.

## Configuração

| Decisão | Padrão recomendado | Descrição |
|---|---|---|
| `manter_ultimos_n` | 3-6 turnos completos | Verbatim recente resolve follow-up ("conserta isso") |
| Gatilho de compactação | contagem de turnos OU teto de tokens | Tokens é mais preciso quando turnos variam muito de tamanho |
| Modelo do resumo | modelo pequeno/rápido | Sumarização não precisa da capacidade do modelo principal |
| System message | nunca entra na compactação | Sempre preservada — é a âncora de comportamento |
| Tool calls órfãos | nunca dividir um par tool_call/tool_result entre corte | API rejeita sequência incompleta |

## Exemplo de uso

```python
historico = compactar(sessao.mensagens, manter_ultimos_n=4, resumir=chamar_llm_resumo)
sessao.mensagens = historico
resposta = llm.create(messages=[system_prompt, *historico, nova_mensagem])
```

## Ver também

- [janela-de-contexto-e-gerenciamento-de-historico](../concepts/janela-de-contexto-e-gerenciamento-de-historico.md)
- [suite-de-regressao-de-prompts](suite-de-regressao-de-prompts.md)
