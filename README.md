# agent-travel

Assistente de viagens full-stack baseado em LLM, com dois fluxos de conversa independentes:

- **Planejador de Viagens:** pesquisa voos e hospedagens, monta roteiros e consolida o orçamento;
- **Agente de Milhas:** pesquisa bônus públicos de transferência Itaú/Livelo e estima o valor dos
  pontos.

O projeto é um MVP de recomendação. Ele não efetua compras, reservas, pagamentos ou
transferências. Resultados de voos, hospedagens e promoções vêm de busca pública na web e incluem
links para conferência na fonte.

## Como funciona

```text
Frontend React/Vite
        │
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
tool calls com Pydantic, executa os handlers e devolve resultados estruturados ao frontend.

## Stack

- **Backend:** Python 3.11+, FastAPI, OpenAI SDK, Pydantic, DDGS, pytest e Ruff;
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

E devolvem o texto do agente acompanhado dos resultados estruturados produzidos pelas tools:

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

## Estrutura principal

```text
src/agent_travel/
├── agents/          # Voos, hospedagem, roteiro e orçamento
├── api/             # FastAPI, rotas, schemas e erros
├── core/            # Configuração, sessões, registry e loop de tool-calling
├── milhas/          # Agente de Milhas independente
├── orchestrator/    # Planejador de Viagens
└── web_search/      # Busca pública via DDGS

frontend/src/
├── components/      # Chat, cards de resultado e componentes de UI
└── lib/             # Cliente HTTP e utilitários
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

Os testes do loop e da API usam clientes falsos, sem depender de uma chamada real ao LLM ou à
busca web.

## Limitações atuais

- As buscas usam resultados públicos do DDGS, não APIs de inventário de companhias ou hotéis;
- preços e disponibilidade precisam ser confirmados no site oficial;
- as sessões ficam em memória e são perdidas quando a API reinicia;
- não há autenticação nem persistência de usuários;
- o sistema recomenda opções, mas não conclui transações.

## Instruções para agentes de código

O [AGENTS.md](AGENTS.md) é a fonte canônica de contexto, arquitetura, convenções e validações do
repositório. O `CLAUDE.md` existe apenas como ponte para esse arquivo.
