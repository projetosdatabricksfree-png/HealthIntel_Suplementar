# Fase 8 — Relatório de Refatoração e Refinamento Geral

## 1. Objetivo

Este documento consolida uma análise crítica do repositório HealthIntel Suplementar para identificar refinamentos técnicos, operacionais e comerciais antes de avançar para homologação em VPS e venda assistida.

O foco é registrar oportunidades reais de ajuste com base no worktree atual, sem implementar refatorações, sem criar sprint artificial e sem marcar como concluído qualquer item que ainda não tenha validação operacional. A leitura prioriza aquilo que bloqueia dinheiro e homologação: API funcional, dbt consistente, ambiente reproduzível, backup/restore validado, proteção comercial e operação mínima.

## 2. Metodologia

### Diretórios e arquivos inspecionados

- Raiz do repositório: `README.md`, `Makefile`, `.gitignore`, `.pre-commit-config.yaml`, `.github/workflows/*`.
- API: `api/app`, `api/tests`, routers, services, schemas, middleware, dependências e configuração.
- Ingestão: `ingestao/app`, `ingestao/dags`, testes e scripts de carga.
- dbt/modelagem: `healthintel_dbt/dbt_project.yml`, `healthintel_dbt/models`, `healthintel_dbt/tests`, `healthintel_dbt/seeds`, `healthintel_dbt/macros`.
- Infraestrutura: `infra/docker-compose.yml`, `infra/nginx`, `infra/postgres/init`, `infra/pgbackrest`, `infra/systemd`.
- Operação e documentação: `docs`, `docs/runbooks`, `docs/operacao`, `docs/sprints/fase7`, `docs/sprints/fase8`, `docs/dbt_*`.
- Scripts e hard gates: `scripts`, `tests/hardgates`.
- Frontend: verificação da ausência física de `frontend/` e presença de arquivos rastreados no git.

### Comandos executados

| Comando | Resultado |
| --- | --- |
| `pwd` | Confirmou `/home/diegocosta/Documents/PROJETO/HealthIntel_Suplementar`. |
| `git status --short` | Mostrou sujeira pré-existente no worktree, incluindo deleções em `frontend/`, prompts da Fase 7 e arquivos novos de backup/operação. |
| `find . -maxdepth 3 -type f \| sort` | Inspecionou a estrutura geral. |
| `find . -maxdepth 4 -type f \( ... \) \| sort` | Listou arquivos Python, SQL, YAML, Markdown, Dockerfile, compose e Makefile. |
| `tree -L 4 -I ".git\|.venv\|venv\|__pycache__\|node_modules\|target\|dbt_packages\|.pytest_cache"` | Falhou: `tree` não está instalado no ambiente. |
| `rg -n "TODO\|FIXME\|HACK\|pass #\|NotImplemented\|raise NotImplementedError" ...` | Buscou marcadores de dívida técnica. |
| `rg -n "api_ans\|consumo_ans\|consumo_premium_ans\|bruto_ans\|stg_ans\|int_ans\|nucleo_ans" ...` | Verificou uso de schemas por API, ingestão, dbt e infra. |
| `rg -n "LIMIT\|OFFSET\|page\|page_size\|api_key\|rate" api` | Verificou paginação, API key e rate limit. |
| `rg -n "password\|secret\|token\|key" ...` | Verificou segredos, defaults e chaves locais. |
| `find healthintel_dbt/models -type f -name "*.sql" -size 0 -print` | Não encontrou models SQL vazios. |
| `find healthintel_dbt/models -type f -name "*.sql" -exec ... wc -l ...` | Não encontrou models SQL com menos de 5 linhas. |
| `find . -type f -name "*.py" ... wc -l ...` | Identificou módulos grandes, incluindo `ingestao/app/carregar_postgres.py` com 1464 linhas. |
| `make lint` | Passou: `All checks passed!`. |
| `make test` | Passou: `181 passed`. |
| `make dbt-compile` | Passou: compile de 182 models, 384 data tests, 22 sources e 14 exposures. |
| `make dbt-test` | Falhou: `202 errors`, principalmente por relações não materializadas em `api_ans`, `consumo_premium_ans`, `mdm_privado`, `stg_cliente` e `stg_ans`. |
| `make smoke` | Falhou: 5 endpoints retornaram `500`. |
| `make sql-lint` | Falhou: alvo usa `../.venv/bin/dbt` fora do diretório esperado. |
| `make smoke-pgbackrest` | Falhou localmente por ausência de `pgbackrest` e `psql`. |
| `docker compose -f infra/docker-compose.yml config` | Passou. |
| `bash -n scripts/backup/*.sh scripts/check_scaffold.sh scripts/run_load_test.sh tests/hardgates/*.sh` | Passou. |
| `make dag-parse` | Passou: sem erros de parse. |
| `docker compose -f infra/docker-compose.yml logs --tail=80 api` | Confirmou `UndefinedTableError` em relação `api_ans.api_rn623_lista_trimestral`. |

### Limitações da análise

- A análise não executou `dbt build` para evitar materialização de dados durante uma tarefa documental.
- Restore/PITR não foi testado; a validação permanece vinculada à Sprint 40.
- `pgbackrest` e `psql` não estavam disponíveis localmente, então o smoke de backup só pode ser validado em VPS ou ambiente operacional equivalente.
- A inspeção de `make smoke` depende do estado local atual dos containers e do banco já carregado.
- A pasta `frontend/` não existe no worktree atual, apesar de seus arquivos continuarem rastreados pelo git.

## 3. Sumário Executivo

| Área | Estado atual | Risco | Prioridade | Recomendação curta |
| --- | --- | --- | --- | --- |
| Estrutura do repositório | Organização principal existe, mas há sujeira forte no worktree e frontend rastreado como deletado. | Drift, ruído operacional e custo de manutenção. | P1 | Limpar escopo versionado e separar artefatos gerados/obsoletos. |
| API | Arquitetura FastAPI madura, mas smoke falha com endpoints comerciais `500`. | Bloqueia homologação e demo. | P0 | Materializar camada `api_ans` mínima e fazer `make smoke` passar. |
| Ingestão | Fluxos reais existem, com discovery, download, carga e auditoria parcial. | Execução em VPS ainda depende de amarração operacional. | P2 | Consolidar orquestração real e critérios de reprocessamento. |
| dbt/modelagem | Camadas medalhão e serviço estão desenhadas, compile passa, testes falham em massa. | Contrato de dados não validado. | P0 | Corrigir materialização mínima e ordem de execução antes da VPS. |
| Infraestrutura | Compose local funcional; hml/prod não materializados. | Ambiente de homologação não reproduzível com segurança. | P0 | Criar compose/env hml e hardening de segredos. |
| Segurança | API key, planos e roles existem, mas há defaults locais e rate limit com falha aberta. | Exposição comercial e anti-bulk incompleto. | P1 | Fechar proteção mínima antes de piloto pago. |
| Observabilidade | Healthchecks, logs em DB, auditorias e backup monitor existem parcialmente. | Falta evidência produtiva de métricas e alertas acionáveis. | P2 | Definir smoke, métricas, alertas e runbooks mínimos. |
| Frontend/comercial | `frontend/` não existe fisicamente; arquivos rastreados aparecem deletados. | Bloqueia experiência comercial própria. | P1 | Decidir remover oficialmente ou reconstruir MVP comercial. |
| Testes e CI | Lint/test/compile passam; dbt-test, sql-lint, smoke e backup smoke falham. | Hard gates inconsistentes. | P0 | Priorizar os gates que bloqueiam VPS. |
| Documentação | Documentação ampla existe, mas há artefatos gerados versionados e validações abertas. | Risco de documentação aspiracional e drift. | P2 | Reduzir ruído e manter docs ligadas a evidências. |

## 4. Diagnóstico por Área

### Estrutura do repositório

O repositório está organizado em áreas coerentes para um produto DaaS/API: `api`, `ingestao`, `healthintel_dbt`, `infra`, `docs`, `scripts`, `tests`, `testes`, `shared` e `mongo_layout_service`. A separação macro respeita a arquitetura esperada.

O principal problema estrutural é o estado do worktree: há alterações e arquivos não rastreados fora do escopo deste relatório, deleções de prompts da Fase 7 e uma ausência física de `frontend/` enquanto o git ainda rastreia 2355 arquivos nessa árvore, incluindo 2338 arquivos sob `frontend/node_modules`. Isso aumenta ruído em revisões, custo de contexto e risco de confundir deleção real com sujeira local.

Também há artefatos gerados de dbt versionados em `docs/dbt_catalog_*`, `docs/dbt_manifest_*` e `docs/dbt_docs_*`. Esses arquivos podem ser úteis como snapshot, mas tendem a gerar drift documental e consumir contexto sem melhorar a operação diária.

### API

A API FastAPI está organizada em routers, services, schemas, middleware e core config. A camada HTTP é relativamente fina em vários endpoints e o acesso a dados fica concentrado em services. A maioria dos services de produto consulta `api_ans.*` e `plataforma.*`, o que está alinhado à diretriz de não consultar camadas intermediárias diretamente.

Há paginação e limites em endpoints comerciais, além de dependências para API key, plano e permissões. Porém, `make smoke` falha com 5 endpoints retornando `500`: `/v1/operadoras`, `/v1/operadoras/123456`, `/v1/operadoras/123456/score`, `/v1/operadoras/123456/regulatorio` e `/v1/regulatorio/rn623`. Os logs da API indicam `UndefinedTableError` para `api_ans.api_rn623_lista_trimestral`, evidenciando que a camada de serviço não está materializada no banco local usado pelo smoke.

O rate limit é aplicado manualmente por routers de produto, mas endpoints admin como `admin_billing` e `admin_layout` têm API key/plano sem rate limit explícito. Além disso, o middleware de rate limit falha aberto em exceções de Redis, o que é aceitável para disponibilidade local, mas fraco para proteção anti-bulk em piloto pago.

### Ingestão

A ingestão possui estrutura real para discovery, download, staging de arquivos, hash, registro em plataforma e carga genérica bronze. Há separação entre módulos de ELT, loaders, auditoria e scripts. O downloader registra arquivos e detecta duplicidade por hash, o que ajuda a idempotência.

Ainda há lacunas de operação em VPS: a orquestração entre scripts, Airflow, dbt e janelas de carga precisa ser fechada com evidência. Existem DAGs úteis como desenho operacional, mas a DAG mestre mensal e algumas DAGs ainda usam majoritariamente `EmptyOperator`, ou seja, não representam execução real fim a fim.

Módulos grandes como `ingestao/app/carregar_postgres.py` indicam alto acoplamento e custo de manutenção solo. O risco não é funcional imediato, mas a evolução futura de layout dinâmico, reprocessamento e auditoria tende a ficar cara se o módulo continuar concentrando responsabilidades demais.

### dbt/modelagem

O projeto dbt está bem separado em camadas: `stg_ans`, `int_ans`, `nucleo_ans`, `api_ans`, `consumo_ans`, `consumo_premium_ans`, `mdm` e `mdm_privado`. O `make dbt-compile` passa, o que indica que o grafo compila e que refs/sources estão sintaticamente coerentes.

O problema crítico é que `make dbt-test` falha com `202 errors`. A falha é majoritariamente causada por relações ausentes em schemas de serviço e consumo, incluindo `api_ans`, `consumo_premium_ans`, `mdm_privado`, `stg_cliente` e `stg_ans`. Isso significa que o contrato de dados não está materializado de forma compatível com os testes declarados.

Não foram encontrados models SQL vazios nem models com menos de 5 linhas em `healthintel_dbt/models`, o que reduz o risco de placeholders vazios na modelagem. Ainda assim, a diferença entre compile verde e testes vermelhos mostra que o hard gate relevante para homologação não é compile, mas build/test/smoke em banco com dados mínimos.

### Infraestrutura

`infra/docker-compose.yml` gera configuração válida e a stack local está funcional para Postgres, MongoDB, Redis, API, Nginx, Airflow, dbt e layout service. O Nginx atua como proxy para API e layout service, com headers básicos.

O compose atual é local/dev. Não foram encontrados compose/env materializados para hml/prod. Há defaults sensíveis em variáveis como senha de Postgres, Mongo, Airflow, `API_JWT_ADMIN_SECRET` e `LAYOUT_SERVICE_TOKEN`. A validação de configuração rejeita alguns defaults fora de local, mas a infraestrutura ainda permite subir com defaults locais se o ambiente não for tratado com disciplina.

Backup/DR já possui artefatos novos em `infra/pgbackrest`, `infra/postgres/conf`, `infra/systemd`, `scripts/backup` e docs operacionais, mas o hard gate local falhou por ausência de binários. A validade operacional depende de execução real em VPS ou ambiente equivalente.

### Segurança

Há fundação relevante: API keys, planos, governança de billing, segregação de schemas e roles, e grants específicos para `consumo_ans`. A API aplica verificação de chave e plano em endpoints comerciais e premium.

Os riscos principais são comerciais: chaves locais de admin/dev são semeadas em SQL, endpoints admin não têm rate limit explícito, e o rate limit falha aberto quando Redis está indisponível. Para um piloto pago, isso reduz a proteção contra exportação massiva, uso abusivo e teste de chaves.

Também há defaults locais em compose e config. Mesmo que parte seja bloqueada por `ENVIRONMENT != local`, a homologação precisa de arquivos de ambiente e secrets materializados de forma explícita, sem depender de disciplina manual.

### Observabilidade

O projeto tem sinais positivos: healthchecks de API e infraestrutura, logs de requisição, tabelas de auditoria, registro de cargas e monitoramento de backup em `plataforma.backup_execucao` e `plataforma.backup_alerta`.

A lacuna é evidência produtiva. Não há prova de métricas e alertas acionáveis em hml/prod, nem evidência de que freshness, falhas de carga, consumo por cliente e backup disparem alerta operacional verificável. Para VPS, o mínimo deve ser smoke test repetível, logs acessíveis, alertas críticos de backup e runbook claro de resposta.

### Frontend/comercial

No worktree atual, `frontend/` não existe. Ao mesmo tempo, o git ainda rastreia 2355 arquivos nessa árvore, incluindo `node_modules`. Essa situação é pior que simplesmente "não ter frontend", porque cria um estado ambíguo: parece haver um produto web versionado, mas ele está deletado localmente.

Para o objetivo do HealthIntel, frontend não precisa virar dashboard analítico. Mas para venda assistida faltam, no mínimo, uma demo funcional, documentação de API publicável, onboarding de chave, planos/limites e uma página comercial simples ou alternativa operacional equivalente.

### Testes e CI

Os testes Python e lint estão saudáveis no ambiente atual: `make lint` passou e `make test` retornou `181 passed`. O parse de DAG também passou.

Os gates que realmente bloqueiam homologação estão vermelhos: `make dbt-test`, `make smoke`, `make sql-lint` e `make smoke-pgbackrest`. Há dois workflows de CI em `.github/workflows`, e um deles inicializa apenas parte dos SQLs antigos, sugerindo risco de drift entre CI e bootstrap atual.

### Documentação

A documentação é ampla e cobre sprints, operação, runbooks, dbt docs, catálogo e backup. O risco é excesso de material com estados diferentes de validação. A regra para as próximas mudanças deve ser simples: documentação operacional só deve afirmar como pronto aquilo que possui comando, evidência e ambiente.

Os documentos de backup e DR recentes são úteis, mas restore/PITR segue fora de prova até a Sprint 40. A Sprint 39 não deve ser tratada como concluída sem os hard gates reais.

## 5. Achados Críticos

### ACHADO-001 — Endpoints comerciais retornam 500 no smoke

- Prioridade: P0
- Área: API
- Arquivos relacionados: `api/app/routers/operadora.py`, `api/app/routers/regulatorio.py`, `api/app/services/operadora.py`, `api/app/services/regulatorio.py`, `healthintel_dbt/models/api`
- Evidência: `make smoke` falhou com 5 endpoints `500`: `/v1/operadoras`, `/v1/operadoras/123456`, `/v1/operadoras/123456/score`, `/v1/operadoras/123456/regulatorio` e `/v1/regulatorio/rn623`. Logs da API registraram `asyncpg.exceptions.UndefinedTableError: relation "api_ans.api_rn623_lista_trimestral" does not exist`.
- Impacto: Bloqueia homologação em VPS, demo funcional e piloto pago, porque os endpoints de valor comercial não respondem.
- Recomendação: Materializar o conjunto mínimo de modelos `api_ans` usado pelo smoke, carregar dados mínimos controlados e manter `make smoke` como hard gate obrigatório.
- Esforço estimado: Médio
- Risco se não corrigir: Subir uma API aparentemente saudável em `/saude`, mas quebrada nos endpoints que o cliente usaria.

### ACHADO-002 — `make dbt-test` não está verde

- Prioridade: P0
- Área: dbt/modelagem
- Arquivos relacionados: `healthintel_dbt/models`, `healthintel_dbt/tests`, `healthintel_dbt/dbt_project.yml`
- Evidência: `make dbt-test` falhou com `202 errors`, principalmente por relações ausentes em `api_ans`, `consumo_premium_ans`, `mdm_privado`, `stg_cliente` e `stg_ans`.
- Impacto: O contrato de dados não está validado. Compile verde não garante que tabelas, views e testes existam no banco usado pela operação.
- Recomendação: Definir build mínimo para homologação, corrigir ordem/materialização de models e só considerar dbt pronto quando `dbt build` ou combinação equivalente de run/test passar em banco limpo.
- Esforço estimado: Alto
- Risco se não corrigir: A API e a camada de consumo continuarão dependendo de relações que podem não existir após bootstrap.

### ACHADO-003 — `make sql-lint` está quebrado por caminho inválido

- Prioridade: P0
- Área: Testes e CI
- Arquivos relacionados: `Makefile`, `healthintel_dbt`
- Evidência: `make sql-lint` falhou com `/bin/bash: line 1: ../.venv/bin/dbt: No such file or directory`. O alvo executa `../.venv/bin/dbt` fora do diretório em que esse caminho é válido.
- Impacto: Um hard gate de qualidade SQL não é executável no ambiente local, reduzindo confiança antes de merge/homologação.
- Recomendação: Ajustar o alvo para executar dbt/sqlfluff a partir do diretório correto ou usar caminho absoluto/variável consistente com os demais alvos dbt.
- Esforço estimado: Baixo
- Risco se não corrigir: SQL inválido ou fora do padrão pode avançar porque o gate está quebrado, não porque passou.

### ACHADO-004 — Não há compose/env materializados para hml/prod

- Prioridade: P0
- Área: Infraestrutura
- Arquivos relacionados: `infra/docker-compose.yml`, `.env.exemplo`, `api/app/core/config.py`, `infra/nginx/nginx.conf`
- Evidência: Apenas `infra/docker-compose.yml` local foi encontrado. O compose usa defaults locais como `POSTGRES_PASSWORD=healthintel`, Airflow `admin/admin`, `API_JWT_ADMIN_SECRET=trocar_em_producao` e token local do layout service.
- Impacto: A homologação em VPS fica manual, frágil e sujeita a subir com credenciais ou comportamento de desenvolvimento.
- Recomendação: Criar overlay ou compose específico de hml, `.env.hml.exemplo`, política de secrets, volumes persistentes, healthchecks e checklist de bootstrap.
- Esforço estimado: Médio
- Risco se não corrigir: VPS insegura, difícil de reproduzir e sem fronteira clara entre dev, hml e produção.

### ACHADO-005 — Backup/DR ainda não está validado em ambiente operacional

- Prioridade: P0
- Área: Observabilidade e operação
- Arquivos relacionados: `scripts/backup/smoke_pgbackrest.sh`, `infra/pgbackrest/pgbackrest.conf`, `docs/operacao/backup_retencao_postgres.md`, `docs/operacao/disaster_recovery.md`, `docs/sprints/fase7/sprint_40_restore_pitr_release.md`
- Evidência: `make smoke-pgbackrest` falhou localmente por ausência de `pgbackrest` e `psql`. Restore/PITR permanece planejado para a Sprint 40.
- Impacto: Backup documentado sem restore validado não fecha DR nem permite promessa segura para cliente pagante.
- Recomendação: Validar em VPS com `pgbackrest check`, evidência de repo2, full/diff/WAL dentro das janelas e restore/PITR testado conforme Sprint 40.
- Esforço estimado: Médio
- Risco se não corrigir: Perda de dados ou indisponibilidade sem caminho comprovado de recuperação.

### ACHADO-006 — `frontend/` está ausente, mas continua rastreado

- Prioridade: P1
- Área: Frontend/comercial
- Arquivos relacionados: `frontend/`, `git ls-files frontend/**`
- Evidência: `find frontend ...` retornou `No such file or directory`, mas `git ls-files 'frontend/**' | wc -l` retornou `2355`, incluindo `2338` arquivos em `frontend/node_modules`.
- Impacto: O repositório fica em estado ambíguo e sem superfície comercial própria validável.
- Recomendação: Decidir formalmente entre remover o frontend do produto versionado ou reconstruir um MVP comercial mínimo sem `node_modules` rastreado.
- Esforço estimado: Médio
- Risco se não corrigir: Revisões e deploys continuarão confundindo sujeira de worktree com decisão de produto.

### ACHADO-007 — Endpoints admin sem rate limit explícito e chaves locais semeadas

- Prioridade: P1
- Área: Segurança
- Arquivos relacionados: `api/app/routers/admin_billing.py`, `api/app/routers/admin_layout.py`, `infra/postgres/init/003_api_comercial.sql`, `infra/postgres/init/004_billing_governanca.sql`
- Evidência: Routers admin usam `validar_api_key` e `verificar_plano`, mas não chamam `aplicar_rate_limit`. SQLs de bootstrap semeiam chaves locais/admin para desenvolvimento.
- Impacto: A área administrativa fica menos protegida contra abuso e erro operacional em ambiente de piloto.
- Recomendação: Aplicar rate limit explícito nos endpoints admin, separar seeds locais de seeds hml/prod e bloquear chaves dev fora de ambiente local.
- Esforço estimado: Baixo
- Risco se não corrigir: Uso indevido de endpoints administrativos e exposição acidental de chaves de desenvolvimento.

### ACHADO-008 — Rate limit falha aberto quando Redis está indisponível

- Prioridade: P1
- Área: Segurança
- Arquivos relacionados: `api/app/middleware/rate_limit.py`, `api/app/core/redis.py`
- Evidência: `aplicar_rate_limit` captura `Exception` e executa `return`, permitindo a requisição quando Redis falha.
- Impacto: Em degradação de Redis, a proteção anti-bulk deixa de existir justamente quando a operação está instável.
- Recomendação: Definir política por ambiente: fail-open apenas local/dev, fail-closed ou limite conservador em hml/prod, com métrica/alerta de falha do Redis.
- Esforço estimado: Baixo
- Risco se não corrigir: Cliente ou atacante pode extrair volume alto de dados durante falha de Redis.

### ACHADO-009 — DAG mestre e algumas DAGs ainda são desenho, não orquestração real

- Prioridade: P2
- Área: Ingestão
- Arquivos relacionados: `ingestao/dags/dag_mestre_mensal.py`, `ingestao/dags/dag_anual_idss.py`, `ingestao/dags`
- Evidência: DAGs usam majoritariamente `EmptyOperator`, enquanto outras DAGs já possuem BashOperator e chamadas reais para scripts/dbt.
- Impacto: A visão operacional mensal pode parecer completa, mas não executa o fluxo real fim a fim.
- Recomendação: Converter o caminho mínimo de carga para tarefas reais, mantendo DAGs conceituais separadas ou claramente marcadas como desenho.
- Esforço estimado: Médio
- Risco se não corrigir: Homologação dependerá de execução manual e operadores podem confiar em DAGs que não carregam dados.

### ACHADO-010 — Acoplamento alto em módulos grandes e duplicidade de sessão DB

- Prioridade: P2
- Área: Qualidade de código
- Arquivos relacionados: `ingestao/app/carregar_postgres.py`, `api/app/core/database.py`, `api/app/database.py`, `api/app/services/meta.py`, `api/app/services/billing.py`
- Evidência: `ingestao/app/carregar_postgres.py` possui 1464 linhas. Existem dois pontos de abstração de banco na API (`core/database.py` e `database.py`). Services como `meta.py` e `billing.py` também são grandes.
- Impacto: Manutenção solo fica mais lenta, mudanças têm maior risco colateral e o custo de contexto para LLM aumenta.
- Recomendação: Refatorar por responsabilidade após estabilizar P0: conexão DB única na API, carga Postgres dividida por parsing/DDL/copy/auditoria e services separados por caso de uso.
- Esforço estimado: Alto
- Risco se não corrigir: Cada ajuste de ingestão ou billing exigirá leitura extensa e tenderá a introduzir regressões.

### ACHADO-011 — Artefatos gerados de dbt docs/manifest estão versionados

- Prioridade: P2/P3
- Área: Documentação
- Arquivos relacionados: `docs/dbt_catalog_v1.0.0.json`, `docs/dbt_catalog_v2.0.0.json`, `docs/dbt_manifest_v1.0.0.json`, `docs/dbt_manifest_v2.0.0.json`, `docs/dbt_docs_v1.0.0.html`, `docs/dbt_docs_v2.0.0.html`
- Evidência: `git ls-files 'docs/dbt_*'` lista manifest, catalog e HTML versionados.
- Impacto: Aumenta drift documental, ruído de diff e custo de contexto. Pode confundir snapshot histórico com estado atual.
- Recomendação: Definir política: manter apenas releases publicados e mover artefatos gerados para storage/CI, ou documentar claramente sua finalidade.
- Esforço estimado: Baixo
- Risco se não corrigir: Decisões futuras podem usar manifest antigo como fonte de verdade.

### ACHADO-012 — Observabilidade existe parcialmente, mas falta evidência produtiva

- Prioridade: P2
- Área: Observabilidade
- Arquivos relacionados: `api/app/main.py`, `docs/operacao/slo_mvp.md`, `infra/postgres/init/034_fase7_backup_execucao.sql`, `infra/postgres/init/035_fase7_backup_alerta.sql`, `scripts/backup`
- Evidência: Existem healthchecks, logs em DB, SLO documental e monitoramento de backup, mas não foi encontrada evidência de métricas/alertas produtivos executados em hml/prod.
- Impacto: Falhas de ingestão, freshness, consumo abusivo ou backup podem demorar a ser percebidas.
- Recomendação: Definir alertas mínimos para API indisponível, smoke vermelho, dbt/carga falha, backup crítico e consumo anômalo por cliente.
- Esforço estimado: Médio
- Risco se não corrigir: O produto pode falhar silenciosamente em ambiente de cliente.

## 6. Backlog de Refinamento

| ID | Prioridade | Área | Ação recomendada | Arquivos afetados | Esforço | Dependência | Critério de aceite |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REF-001 | P0 | API/dbt | Materializar modelos mínimos `api_ans` exigidos pelo smoke. | `healthintel_dbt/models/api`, `api/app/services/*` | Médio | Banco local/hml limpo | `make smoke` passa sem endpoint `500`. |
| REF-002 | P0 | dbt | Corrigir `make dbt-test` com build/test em ordem reprodutível. | `healthintel_dbt/models`, `healthintel_dbt/tests`, `Makefile` | Alto | REF-001 | `make dbt-test` passa ou há target mínimo documentado e verde para hml. |
| REF-003 | P0 | Testes | Corrigir caminho do `make sql-lint`. | `Makefile` | Baixo | Nenhuma | `make sql-lint` executa no ambiente local sem erro de caminho. |
| REF-004 | P0 | Infra | Criar compose/env de hml com secrets obrigatórios e defaults locais bloqueados. | `infra/docker-compose*.yml`, `.env.hml.exemplo`, docs runbook | Médio | Política de secrets | `docker compose config` passa para hml e não contém segredos default. |
| REF-005 | P0 | Backup/DR | Validar pgBackRest, repo2, full/diff/WAL e restore/PITR. | `scripts/backup`, `infra/pgbackrest`, `docs/operacao`, Sprint 40 | Médio | VPS ou ambiente equivalente | Evidência de `make smoke-pgbackrest` e restore/PITR testado. |
| REF-006 | P1 | Frontend/comercial | Decidir destino de `frontend/` e remover `node_modules` rastreado ou reconstruir MVP. | `frontend`, `.gitignore`, docs comerciais | Médio | Decisão de produto | Worktree sem deleções massivas e sem `node_modules` versionado. |
| REF-007 | P1 | Segurança | Aplicar rate limit a endpoints admin. | `api/app/routers/admin_billing.py`, `api/app/routers/admin_layout.py` | Baixo | Redis operacional | Teste cobre limite em endpoint admin. |
| REF-008 | P1 | Segurança | Definir política fail-open/fail-closed do rate limit por ambiente. | `api/app/middleware/rate_limit.py`, `api/app/core/config.py` | Baixo | REF-004 | Em hml/prod, falha de Redis não libera bulk sem alerta. |
| REF-009 | P1 | Comercial | Criar pacote mínimo de venda assistida com docs de API, plano, limites e onboarding. | `docs`, possível frontend/comercial | Médio | REF-001, REF-004 | Cliente piloto recebe chave, limites e endpoints documentados. |
| REF-010 | P2 | Airflow | Converter DAG mestre mínima em orquestração real ou marcar como conceitual. | `ingestao/dags/dag_mestre_mensal.py`, DAGs relacionadas | Médio | Carga mínima definida | DAG executa caminho mínimo ou deixa explícito que é apenas desenho. |
| REF-011 | P2 | Ingestão | Separar `carregar_postgres.py` por responsabilidades. | `ingestao/app/carregar_postgres.py` | Alto | P0 estabilizados | Testes de ingestão continuam passando após extração incremental. |
| REF-012 | P2 | API | Consolidar abstrações de banco da API. | `api/app/core/database.py`, `api/app/database.py` | Médio | Testes API verdes | Um único padrão documentado de sessão/pool. |
| REF-013 | P2 | Observabilidade | Definir alertas mínimos de API, dbt, carga, backup e consumo. | `docs/operacao`, scripts, infra futura | Médio | REF-004 | Runbook lista alerta, consulta e ação para cada falha crítica. |
| REF-014 | P2/P3 | Documentação | Definir política para artefatos `docs/dbt_*`. | `docs/dbt_*`, `.gitignore`, CI/docs | Baixo | Decisão de release docs | Manifest/catalog não geram drift ou ficam claramente versionados por release. |

## 7. Plano Enxuto para Homologação em VPS

1. Criar ambiente hml/prod mínimo: compose ou overlay específico, `.env.hml.exemplo`, volumes persistentes, rede, Nginx e healthchecks.
2. Remover dependência de defaults locais: exigir secrets reais para Postgres, Mongo, Redis, Airflow, API admin e layout service.
3. Corrigir hard gates locais: `make sql-lint`, `make dbt-test` ou target mínimo equivalente, e `make smoke`.
4. Materializar carga mínima: banco limpo com bootstrap SQL, dbt run/build do subconjunto necessário e dados suficientes para endpoints comerciais.
5. Proteger API: API key obrigatória nos endpoints comerciais, rate limit também em admin, limite de paginação e política anti-bulk por ambiente.
6. Validar backup/restore: executar `make smoke-pgbackrest` na VPS, validar repo2 e realizar restore/PITR da Sprint 40.
7. Operar com evidência: registrar logs, smoke, freshness mínima, alerta de backup crítico e runbook de resposta.
8. Documentar subida: runbook de hml com comandos exatos, variáveis obrigatórias, rollback e critérios de aceite.

Critério mínimo para considerar VPS homologável: `docker compose config` hml sem segredos default, API saudável, `make smoke` verde, dbt mínimo verde, backup validado com repo2 e restore/PITR testado.

## 8. Plano Enxuto para Venda Assistida

1. Definir demo funcional com poucos endpoints de alto valor: operadora, score, regulatório/RN623 e metadados.
2. Usar dataset limitado e versionado, suficiente para demonstrar valor sem abrir exportação massiva.
3. Publicar documentação objetiva da API: autenticação, limites, paginação, exemplos de request/response e erros.
4. Criar onboarding manual de cliente piloto: geração de chave, plano, limites, contato e termos de uso.
5. Implementar limites anti-bulk mínimos: page size máximo, rate limit por chave, logs de consumo por cliente e bloqueio de abuso.
6. Preparar proposta comercial simples: escopo do piloto, SLA experimental, datasets cobertos, preço, duração e critérios de sucesso.
7. Garantir operação mínima: smoke diário, backup validado, canal de suporte e runbook de incidentes.

Critério mínimo para piloto pago: endpoints da demo sem `500`, chave por cliente, limites aplicados, documentação entregue e capacidade comprovada de restaurar o banco.

## 9. Riscos de Continuar Desenvolvendo Sem Refatorar

- Risco técnico: novas features podem se apoiar em relações dbt inexistentes, aumentando a distância entre compile, teste e execução real.
- Risco operacional: subir VPS sem compose/env hml e sem restore validado cria ambiente manual, frágil e difícil de recuperar.
- Risco comercial: `make smoke` vermelho impede demo confiável e reduz credibilidade com cliente piloto.
- Risco de segurança: rate limit falhando aberto e defaults locais aumentam exposição a bulk e erro de configuração.
- Risco financeiro: continuar ampliando escopo sem fechar API mínima vendável posterga receita e aumenta custo de manutenção.
- Risco de manutenção solo: módulos grandes e documentação extensa demais aumentam o custo de mudança e o custo de contexto em LLM.
- Risco documental: artefatos gerados e sprints com validações abertas podem dar aparência de maturidade maior que a evidência real.

## 10. Conclusão

| Dimensão | Nota | Leitura objetiva | O que falta para subir 10 pontos |
| --- | --- | --- | --- |
| Maturidade técnica | 68/100 | Há arquitetura coerente, testes Python verdes, dbt compile e separação de camadas, mas gates de dados e smoke estão vermelhos. | Fazer `make dbt-test` e `make smoke` passarem no ambiente padrão, corrigir `make sql-lint` e reduzir os maiores acoplamentos. |
| Prontidão para homologação VPS | 42/100 | A stack local sobe e o compose valida, mas faltam hml/prod, secrets, dbt materializado, smoke verde e backup/restore validado. | Criar compose/env hml, fechar gates P0 e validar pgBackRest com restore/PITR. |
| Prontidão para piloto pago | 38/100 | O produto tem base comercial de API key/plano, mas endpoints principais falham e proteção anti-bulk ainda é insuficiente. | Entregar demo API estável, documentação de cliente, limites por chave e onboarding manual. |
| Prontidão para enterprise | 24/100 | Ainda não há evidência de operação, segurança, DR, observabilidade e governança no nível enterprise. | Estabilizar VPS, formalizar SLO/alertas, auditar secrets/roles, validar DR e criar trilha de consumo por cliente. |

A próxima ação recomendada é corrigir o hard gate mínimo de homologação: materializar o dbt mínimo, fazer `make smoke` passar, corrigir `make sql-lint`, criar compose/env hml e validar backup/restore. Esse caminho prioriza capacidade de operar e vender antes de refatorações estruturais maiores.
