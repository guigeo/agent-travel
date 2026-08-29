Quero padronizar as instruções deste projeto para que Claude Code e Codex utilizem a mesma fonte de contexto e regras.

A partir de agora, o arquivo canônico deste projeto deve ser:

`AGENTS.md`

O arquivo `CLAUDE.md` deve existir apenas como uma ponte para o Claude Code, instruindo-o a ler e seguir o `AGENTS.md`.

Todo o conteúdo textual criado ou reorganizado nesta tarefa deve ficar em português, exceto:

- nomes de arquivos;
- nomes de tecnologias;
- comandos;
- trechos de código;
- nomes de bibliotecas;
- variáveis;
- termos técnicos que façam mais sentido no idioma original.

Analise SOMENTE o projeto atual. Não percorra projetos irmãos nem diretórios acima deste repositório.

## 1. Analise o estado atual

Verifique se existem:

- `AGENTS.md`
- `CLAUDE.md`

Leia integralmente os arquivos existentes antes de fazer qualquer alteração.

Também consulte, quando necessário para entender o projeto:

- `README.md`;
- documentação relevante;
- estrutura de diretórios;
- manifests de dependências;
- arquivos de configuração;
- scripts;
- configurações de Docker;
- CI/CD;
- comandos de teste, lint, build e execução.

Não faça alterações no código-fonte nesta tarefa.

---

## 2. Se existir somente `CLAUDE.md`

Leia integralmente o `CLAUDE.md`.

Crie um novo `AGENTS.md` migrando todo o contexto relevante existente no `CLAUDE.md`, incluindo:

- objetivo do projeto;
- contexto funcional;
- arquitetura;
- estrutura;
- comandos;
- tecnologias;
- padrões de desenvolvimento;
- convenções;
- restrições;
- decisões técnicas;
- workflows;
- instruções para agentes;
- informações importantes para manutenção e evolução do projeto.

Não descarte informações relevantes e não faça um resumo agressivo.

Organize o conteúdo quando isso melhorar a legibilidade, mas preserve o significado das instruções existentes.

Se o conteúdo original estiver em inglês, traduza para português sem alterar seu significado técnico.

Depois substitua o conteúdo do `CLAUDE.md` pelo seguinte:

```md
# Instruções do Claude Code

As instruções canônicas deste repositório estão mantidas no arquivo `AGENTS.md`.

Antes de iniciar qualquer tarefa:

1. Leia o `AGENTS.md` por completo.
2. Siga todas as instruções, convenções, decisões de arquitetura, fluxos de trabalho e restrições definidas nele.
3. Considere o `AGENTS.md` como a fonte de verdade deste repositório.
4. Se houver conflito entre este arquivo e o `AGENTS.md`, siga o `AGENTS.md`.

Não duplique neste arquivo as instruções específicas do projeto.
```

---

## 3. Se existir somente `AGENTS.md`

Leia integralmente o `AGENTS.md`.

Preserve todo o conteúdo relevante existente.

Se o arquivo estiver em inglês, traduza seu conteúdo para português, preservando:

- significado técnico;
- comandos;
- nomes de arquivos;
- nomes de tecnologias;
- termos específicos cuja tradução possa prejudicar a clareza.

Não simplifique ou reescreva o arquivo apenas por preferência de estilo.

Depois crie um `CLAUDE.md` contendo somente:

```md
# Instruções do Claude Code

As instruções canônicas deste repositório estão mantidas no arquivo `AGENTS.md`.

Antes de iniciar qualquer tarefa:

1. Leia o `AGENTS.md` por completo.
2. Siga todas as instruções, convenções, decisões de arquitetura, fluxos de trabalho e restrições definidas nele.
3. Considere o `AGENTS.md` como a fonte de verdade deste repositório.
4. Se houver conflito entre este arquivo e o `AGENTS.md`, siga o `AGENTS.md`.

Não duplique neste arquivo as instruções específicas do projeto.
```

---

## 4. Se existirem `AGENTS.md` e `CLAUDE.md`

Leia integralmente os dois arquivos antes de alterar qualquer um deles.

Considere `AGENTS.md` como a nova fonte canônica de instruções.

Compare os conteúdos dos dois arquivos.

Se houver informações relevantes no `CLAUDE.md` que ainda não estejam representadas no `AGENTS.md`:

- incorpore essas informações ao `AGENTS.md`;
- preserve as informações já existentes;
- evite duplicações;
- não altere decisões técnicas apenas por preferência;
- não remova contexto válido;
- organize o conteúdo quando isso melhorar a compreensão.

Se algum dos arquivos estiver em inglês, traduza o conteúdo relevante para português.

Preserve sem tradução:

- comandos;
- código;
- caminhos;
- nomes de arquivos;
- nomes de tecnologias;
- nomes de APIs;
- identificadores;
- nomes de bibliotecas;
- termos técnicos quando a tradução não for natural.

Depois substitua o `CLAUDE.md` pelo arquivo mínimo:

```md
# Instruções do Claude Code

As instruções canônicas deste repositório estão mantidas no arquivo `AGENTS.md`.

Antes de iniciar qualquer tarefa:

1. Leia o `AGENTS.md` por completo.
2. Siga todas as instruções, convenções, decisões de arquitetura, fluxos de trabalho e restrições definidas nele.
3. Considere o `AGENTS.md` como a fonte de verdade deste repositório.
4. Se houver conflito entre este arquivo e o `AGENTS.md`, siga o `AGENTS.md`.

Não duplique neste arquivo as instruções específicas do projeto.
```

Se o `CLAUDE.md` não possuir nenhuma informação adicional relevante, apenas transforme-o nessa ponte mínima para o `AGENTS.md`.

---

## 5. Se não existir nem `AGENTS.md` nem `CLAUDE.md`

Analise o projeto atual antes de criar os arquivos.

Consulte o que estiver disponível, como:

- `README.md`;
- documentação;
- estrutura de diretórios;
- manifests de dependências;
- arquivos de configuração;
- scripts;
- Docker;
- CI/CD;
- código suficiente para compreender a arquitetura;
- testes;
- ferramentas de lint, type checking, build e execução.

Crie um `AGENTS.md` factual, útil e enxuto utilizando somente informações que possam ser verificadas no repositório.

Não invente regras, comandos, arquitetura ou tecnologias.

Use preferencialmente a seguinte estrutura:

```md
# AGENTS.md

## Visão Geral do Projeto

Descrição curta do objetivo do projeto, seu contexto e sua responsabilidade principal.

## Estrutura do Repositório

Principais diretórios e suas responsabilidades.

## Stack Tecnológica

Tecnologias, frameworks, linguagens, runtime, ferramentas e dependências principais.

## Ambiente de Desenvolvimento

Informações necessárias para preparar e executar o projeto localmente.

## Comandos Comuns

Comandos confirmados para:

- instalar dependências;
- executar o projeto;
- executar em modo de desenvolvimento;
- realizar build;
- executar testes;
- executar lint;
- formatar código;
- validar tipos;
- realizar outras validações existentes no projeto.

Não invente comandos que não estejam presentes ou claramente confirmados no repositório.

## Arquitetura

Resumo da arquitetura e dos principais fluxos observáveis no projeto.

Inclua somente informações que possam ser verificadas.

## Padrões de Desenvolvimento

Convenções, padrões e práticas identificadas no código e na documentação existente.

## Testes e Validação

Explique como uma alteração deve ser validada antes de uma tarefa ser considerada concluída.

## Instruções para Agentes

- Leia este arquivo antes de modificar o repositório.
- Preserve a arquitetura e as convenções existentes.
- Prefira alterações pequenas, focadas e fáceis de revisar.
- Não modifique arquivos sem relação com a tarefa atual.
- Não introduza novas dependências sem necessidade clara.
- Antes de criar uma nova abstração, procure padrões equivalentes já existentes no projeto.
- Evite duplicação de código.
- Não refatore áreas não relacionadas apenas por preferência.
- Utilize os testes, lint, type checking, build ou outras validações existentes no projeto antes de considerar uma tarefa concluída.
- Não assuma comportamentos que possam ser verificados diretamente no código ou na documentação.
- Quando houver dúvida relevante sobre uma decisão de arquitetura, preserve o comportamento atual em vez de inventar uma nova convenção.
```

Depois crie também:

```md
# Instruções do Claude Code

As instruções canônicas deste repositório estão mantidas no arquivo `AGENTS.md`.

Antes de iniciar qualquer tarefa:

1. Leia o `AGENTS.md` por completo.
2. Siga todas as instruções, convenções, decisões de arquitetura, fluxos de trabalho e restrições definidas nele.
3. Considere o `AGENTS.md` como a fonte de verdade deste repositório.
4. Se houver conflito entre este arquivo e o `AGENTS.md`, siga o `AGENTS.md`.

Não duplique neste arquivo as instruções específicas do projeto.
```

---

## 6. Regras de segurança da alteração

Nesta tarefa:

- trabalhe somente neste projeto;
- não percorra projetos irmãos;
- não altere arquivos fora do repositório atual;
- não altere código-fonte;
- não altere dependências;
- não faça refatorações;
- não implemente features;
- não corrija bugs não relacionados;
- não altere configurações funcionais do projeto;
- não execute comandos destrutivos;
- não altere `.git`;
- não altere configurações globais do Git;
- não faça `git push`;
- não faça commit automaticamente;
- não delete informações relevantes;
- não sobrescreva um `AGENTS.md` existente sem antes lê-lo;
- preserve instruções específicas e úteis do projeto;
- não invente contexto que não possa ser confirmado.

Se houver conflito entre `AGENTS.md` e `CLAUDE.md`, analise o contexto existente e preserve no `AGENTS.md` a informação mais específica, atual e coerente com o estado real do projeto.

---

## 7. Critérios de qualidade do `AGENTS.md`

O resultado não deve ser apenas uma documentação genérica.

O `AGENTS.md` deve ajudar efetivamente um agente de código a trabalhar neste repositório.

Priorize informações como:

- como o projeto é organizado;
- onde novas funcionalidades normalmente devem ser implementadas;
- como executar e validar alterações;
- padrões já adotados;
- dependências importantes;
- arquitetura;
- integrações;
- restrições;
- comportamentos que devem ser preservados;
- decisões técnicas existentes.

Evite preencher o arquivo com informações óbvias ou genéricas que não agreguem contexto real ao agente.

---

## 8. Git e revisão final

Depois das alterações:

1. Execute `git status`.
2. Execute `git diff -- AGENTS.md CLAUDE.md`.
3. Revise as alterações realizadas.
4. Confirme que nenhuma informação relevante foi perdida.
5. Confirme que não houve alteração em arquivos além de `AGENTS.md` e `CLAUDE.md`.
6. Informe resumidamente:
   - qual era a situação inicial;
   - o que foi migrado;
   - o que foi criado;
   - o que foi traduzido;
   - se houve merge entre informações;
   - se existe algum ponto que merece revisão manual.

Não faça commit automaticamente.

Ao final, sugira uma mensagem de commit curta e adequada.

Exemplo:

```text
chore: padroniza instruções dos agentes
```

---

## Estado final esperado

O projeto deve terminar com:

```text
projeto/
├── AGENTS.md      # fonte canônica de contexto e instruções
├── CLAUDE.md      # ponte do Claude Code para o AGENTS.md
└── ...
```

Fluxo esperado:

```text
Claude Code
    ↓
CLAUDE.md
    ↓
AGENTS.md
```

```text
Codex
    ↓
AGENTS.md
```

O `AGENTS.md` deve ser a única fonte de verdade das instruções específicas do projeto.

Execute agora a análise e a padronização deste projeto.