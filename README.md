# agent-travel

Assistente de viagens full-stack baseado em LLM, com dois fluxos de conversa independentes:

- **Planejador de Viagens:** pesquisa voos e hospedagens, monta roteiros e consolida o orçamento;
- **Agente de Milhas:** pesquisa bônus públicos de transferência Itaú/Livelo e estima o valor dos
  pontos.

O projeto é um MVP de recomendação. Ele não efetua compras, reservas, pagamentos ou
transferências. A busca na web é só o insumo: o assistente devolve no máximo duas opções
(principal e alternativa), com preço ou percentual somente quando o número aparece no trecho da
fonte. O restante fica como valor a confirmar no site oficial.

## Como funciona

```text
Frontend React/Vite
        │  POST + SSE (progresso das tools)
        ▼
     FastAPI
        │
        ▼
Loop compartilhado de LLM + tool-calling
        │
        ├── Planejador: voos, hospedagem, roteiro e orçamento
        └── Milhas: bônus de transferência e valor dos pontos
```

Cada agente possui prompt, conjunto de tools e sessões próprios. O núcleo compartilhado valida as
tool calls com Pydantic, executa os handlers e devolve resultados estruturados ao frontend. Fontes
de voos, hospedagem e bônus são filtradas (agregadores e companhias) antes da extração.

## Stack

- **Backend:** Python 3.11+, FastAPI, OpenAI SDK, Pydantic, DDGS, SQLite, pytest e Ruff;
- **Frontend:** React 19, TypeScript, Vite, Tailwind CSS e shadcn/ui;
- **Gerenciamento Python:** `uv`;
- **Gerenciamento frontend:** npm.

## Pré-requisitos

- Python 3.11 ou superior;
- `uv`;
- Node.js e npm;
- uma chave de API compatível com o cliente OpenAI.

## Configuração

Instale as dependências e crie os arquivos locais de ambiente:

```bash
uv sync --group dev
cp .env.example .env

npm --prefix frontend install
cp frontend/.env.example frontend/.env
```

Configure a chave do modelo no `.env`:

```dotenv
LLM_PROVIDER_API_KEY=sua-chave
LLM_MODEL=gpt-4o-mini
MAX_TOOL_ITERS=6
SESSION_TTL_SECONDS=3600
SESSION_DB_DIR=.data
```

O frontend usa `http://localhost:8000` como API por padrão. Para alterar:

```dotenv
VITE_API_BASE=http://localhost:8000
```

## Execução local

Em um terminal, inicie a API:

```bash
uv run uvicorn agent_travel.api.main:app --reload
```

Em outro terminal, inicie o frontend:

```bash
npm --prefix frontend run dev
```

Abra a URL informada pelo Vite no terminal. A documentação interativa da API fica disponível em
`http://localhost:8000/docs`.

O frontend guarda a sessão no `localStorage`. O backend persiste o histórico em SQLite em
`.data/` (ignorado pelo git), com TTL.

## API

| Método | Rota | Finalidade |
| --- | --- | --- |
| `GET` | `/health` | Verifica a saúde da API |
| `POST` | `/chat/{session_id}` | Envia uma mensagem ao Planejador de Viagens |
| `POST` | `/miles/query/{session_id}` | Envia uma mensagem ao Agente de Milhas |

As duas rotas de conversa recebem:

```json
{
  "mensagem": "Quero planejar uma viagem para Lisboa"
}
```

Com `Accept: application/json` (padrão), devolvem o texto do agente e os resultados das tools:

```json
{
  "texto": "...",
  "resultados": [
    {
      "ferramenta": "buscar_voos",
      "dados": []
    }
  ]
}
```

Com `Accept: text/event-stream`, emitem SSE com `tool_started`, `tool_finished` e `texto_final`.
O chat usa esse modo para mostrar o progresso (“Buscando voos…”) antes da resposta final.

## Estrutura principal

```text
src/agent_travel/
├── agents/          # Voos, hospedagem, roteiro e orçamento
├── api/             # FastAPI, rotas, schemas, SSE e erros
├── core/            # Configuração, sessões, registry e loop de tool-calling
├── milhas/          # Agente de Milhas independente
├── orchestrator/    # Planejador de Viagens
└── web_search/      # Busca DDGS, ranking de fontes e extração ancorada

frontend/src/
├── components/      # Chat, cards de resultado e componentes de UI
└── lib/             # Cliente HTTP, sessão local e utilitários
```

## Qualidade e testes

Backend:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

Frontend:

```bash
npm --prefix frontend run lint
npm --prefix frontend run build
```

O GitHub Actions (`.github/workflows/ci.yml`) executa os dois conjuntos em pull requests e na
`main`. Os testes do loop e da API usam clientes falsos, sem depender de uma chamada real ao LLM
ou à busca web.

## Limitações atuais

- As buscas usam resultados públicos do DDGS, não APIs de inventário de companhias ou hotéis;
- preço e bônus só entram no card se o número aparecer no trecho da fonte;
- disponibilidade e tarifa final precisam ser confirmados no site oficial;
- não há autenticação nem contas de usuário;
- o sistema recomenda opções, mas não conclui transações;
- ainda não há um plano de viagem persistido além do histórico do chat (escolher no card e
  manter um painel “Sua viagem” fica para a próxima evolução).

## Instruções para agentes de código

O [AGENTS.md](AGENTS.md) é a fonte canônica de contexto, arquitetura, convenções e validações do
repositório. O `CLAUDE.md` existe apenas como ponte para esse arquivo.
