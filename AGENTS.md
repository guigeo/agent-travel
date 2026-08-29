# AGENTS.md

## Visão Geral do Projeto

`agent-travel` é um MVP full-stack de assistência a viagens baseado em LLM. O produto oferece
dois fluxos de conversa independentes:

- o Planejador de Viagens pesquisa voos e hospedagens, monta roteiros e consolida orçamentos;
- o Agente de Milhas pesquisa bônus públicos de transferência de pontos Itaú/Livelo e calcula
  o valor estimado de uma transferência.

O sistema apenas recomenda opções. Não realiza compras, reservas, pagamentos ou transferências
de pontos. Os dados de voos, hospedagens e promoções vêm de busca pública na web e devem ser
tratados como referências sujeitas a alteração, sempre acompanhadas da fonte.

## Estrutura do Repositório

```text
.
├── src/agent_travel/
│   ├── agents/           # Tools e backends de voos, hospedagem, roteiro e orçamento
│   ├── api/              # Aplicação FastAPI, schemas, erros e rotas HTTP
│   ├── core/             # Configuração, cliente LLM, sessões, registry e loop de tool-calling
│   ├── milhas/           # Prompt, tools, backend e registry exclusivos do Agente de Milhas
│   ├── orchestrator/     # Prompt e registry do Planejador de Viagens
│   └── web_search/       # Adaptador da busca pública via DDGS
├── frontend/             # Aplicação React, TypeScript, Vite, Tailwind CSS e shadcn/ui
├── tests/                # Testes unitários, do loop e da API FastAPI
├── docs/                 # Documentação e instruções do projeto
├── pyproject.toml        # Manifesto Python e configuração de Ruff/pytest
└── uv.lock               # Lockfile das dependências Python
```

O diretório `.claude/` contém material legado de workflow, agentes auxiliares e Knowledge Base.
Consulte-o apenas quando a tarefa depender explicitamente desses recursos. Este `AGENTS.md` é a
fonte canônica das instruções gerais do repositório.

## Stack Tecnológica

### Backend

- Python 3.11 ou superior, gerenciado com `uv`;
- FastAPI e Uvicorn;
- OpenAI Python SDK para chat completions e function calling;
- Pydantic v2 e pydantic-settings;
- DDGS para busca pública na web;
- pytest para testes e Ruff para lint/formatação.

### Frontend

- React 19 e TypeScript;
- Vite;
- Tailwind CSS 4 e componentes shadcn/ui/Base UI;
- React Markdown para respostas textuais;
- Oxlint para lint.

## Ambiente de Desenvolvimento

Use `uv` para o ambiente Python. Não instale dependências Python globalmente nem use `pip` para
gerenciar este projeto.

Prepare o backend:

```bash
uv sync --group dev
cp .env.example .env
```

Variáveis disponíveis no `.env`:

- `LLM_PROVIDER_API_KEY`: chave usada pelo cliente OpenAI;
- `LLM_MODEL`: modelo utilizado, com padrão `gpt-4o-mini`;
- `MAX_TOOL_ITERS`: limite de iterações de tool-calling, com padrão `6`;
- `SESSION_TTL_SECONDS`: TTL das sessões em memória, com padrão `3600`.

Prepare o frontend:

```bash
npm --prefix frontend install
cp frontend/.env.example frontend/.env
```

`VITE_API_BASE` define a URL da API e, quando ausente, o frontend usa
`http://localhost:8000`.

Não leia, registre nem exponha valores dos arquivos `.env` em logs, documentação, commits ou
respostas.

## Comandos Comuns

Executar o backend em desenvolvimento:

```bash
uv run uvicorn agent_travel.api.main:app --reload
```

Executar o frontend em desenvolvimento:

```bash
npm --prefix frontend run dev
```

Executar os testes Python:

```bash
uv run pytest
```

Executar lint e verificar formatação do backend:

```bash
uv run ruff check .
uv run ruff format --check .
```

Aplicar formatação do backend quando a tarefa autorizar alterações de código:

```bash
uv run ruff format .
```

Executar lint, validação de tipos e build do frontend:

```bash
npm --prefix frontend run lint
npm --prefix frontend run build
```

O script `build` executa `tsc -b` antes do build do Vite e, portanto, também valida os tipos do
frontend. Não há um type checker separado configurado para o backend.

## Arquitetura

### Fluxos HTTP

- `GET /health`: verificação simples de saúde da API;
- `POST /chat/{session_id}`: conversa com o Planejador de Viagens;
- `POST /miles/query/{session_id}`: conversa com o Agente de Milhas.

O frontend cria identificadores de sessão independentes para cada aba. No backend, cada agente
também possui seu próprio `SessionStore`. As sessões ficam somente em memória, expiram por TTL e
não sobrevivem à reinicialização do processo.

### Motor compartilhado de LLM

`core/loop.py` implementa o loop reutilizável de tool-calling. Cada turno recebe um cliente LLM,
uma sessão, um `ToolRegistry`, um system prompt e a pergunta do usuário. O loop:

1. adiciona a pergunta ao histórico;
2. envia ao modelo o prompt, o histórico e os schemas das tools;
3. valida e executa as tool calls solicitadas;
4. devolve os resultados ao modelo até receber uma resposta final;
5. limita erros de tools, número de iterações e tamanho do histórico.

`core/tool_registry.py` associa cada nome de tool a um model Pydantic e a um handler. O model
gera o JSON Schema enviado ao LLM e valida os argumentos antes da execução. Handlers retornam
`ToolResult`; resultados com `ids` e `rows` são expostos pela API como dados estruturados para os
cards do frontend.

### Planejador de Viagens

`orchestrator/registry.py` registra quatro tools:

- `buscar_voos`;
- `buscar_hospedagem`;
- `montar_roteiro`;
- `calcular_orcamento`.

Voos e hospedagens usam `WebSearchClient` e retornam título, trecho e URL da fonte. O orçamento é
um cálculo determinístico. O roteiro faz uma chamada adicional ao LLM com um prompt específico.

### Agente de Milhas

`milhas/registry.py` registra:

- `buscar_bonus_vigente`;
- `calcular_valor_ponto`.

O módulo `milhas` deve permanecer independente de `orchestrator`: ele não deve importar nem
depender de destino, datas, orçamento ou sessão de planejamento. Essa separação é verificada por
teste.

### Frontend

`frontend/src/App.tsx` apresenta duas abas, cada uma com seu próprio chat. O cliente HTTP está em
`frontend/src/lib/api.ts`. `ResultRenderer` escolhe cards específicos conforme o nome da tool:

- listas com fontes para voos, hospedagens e bônus;
- card de orçamento;
- card de valor dos pontos.

Ao criar uma nova tool cujo resultado deva aparecer como card, mantenha o contrato da API e
adicione o renderer correspondente no frontend.

## Padrões de Desenvolvimento

- Todo texto novo específico do projeto deve ser escrito em português, preservando nomes de
  tecnologias, APIs, bibliotecas, arquivos, identificadores, comandos e termos técnicos cuja
  tradução prejudique a clareza.
- Use type hints nas assinaturas Python e models Pydantic para os argumentos das tools.
- Mantenha a lógica determinística em funções próprias; não delegue cálculos simples ao LLM.
- Informações atuais de voos, hospedagens e bônus devem vir das tools de busca e incluir
  `fonte_url`. Não invente preços, disponibilidade ou promoções.
- Preserve a proibição de realizar compras, reservas, pagamentos e transferências.
- Preserve registries, prompts e stores de sessão separados entre Planejador e Milhas.
- Para uma nova tool, siga o padrão existente: model `BaseModel`, handler que devolve
  `ToolResult` e registro explícito no registry do agente correto.
- Erros de domínio recuperáveis nas tools são representados por `ValueError` e convertidos pelo
  registry em payloads de erro para possível autocorreção do modelo.
- Preserve o formato RFC 9457 (`application/problem+json`) usado nos erros HTTP de validação.
- No frontend, reutilize os componentes existentes e o alias `@/` para imports de `src`.
- Não introduza uma dependência sem necessidade clara e atualização do manifesto e lockfile
  correspondentes.

## Testes e Validação

Os testes usam um `FakeClient` roteirizado para validar o comportamento do LLM sem chamadas
externas. Continue preferindo testes offline e backends falsos para manter a suíte determinística.

Antes de considerar uma alteração concluída, execute as validações proporcionais às áreas
alteradas:

- backend: `uv run ruff check .`, `uv run ruff format --check .` e `uv run pytest`;
- frontend: `npm --prefix frontend run lint` e `npm --prefix frontend run build`;
- contrato full-stack ou alterações compartilhadas: execute os dois conjuntos.

Não dependa da busca DDGS nem de uma API LLM real nos testes automatizados. Ao alterar o motor de
tool-calling, cubra resposta direta, tool call bem-sucedida, autocorreção após erro, limite de erros,
limite de iterações e preservação válida do histórico.

## Instruções para Agentes

- Leia este arquivo por completo antes de modificar o repositório.
- Analise somente este repositório; não percorra projetos irmãos ou diretórios acima dele.
- Preserve a arquitetura, os limites de produto e as convenções existentes.
- Prefira alterações pequenas, focadas e fáceis de revisar.
- Não modifique arquivos sem relação com a tarefa atual.
- Antes de criar uma abstração, procure padrões equivalentes no projeto.
- Evite duplicação e não refatore áreas não relacionadas apenas por preferência.
- Não assuma comportamentos que possam ser verificados no código ou na documentação.
- Não altere decisões de arquitetura sem necessidade explícita e validação correspondente.
- Preserve mudanças existentes do usuário no worktree.
- Nunca inclua segredos ou arquivos `.env` em commits.
- Utilize testes, lint, type checking e build aplicáveis antes de concluir a tarefa.
