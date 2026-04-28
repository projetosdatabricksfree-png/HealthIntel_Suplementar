# Sprint 38 — Histórico Sob Demanda por Cliente

**Status:** Resolvida no MVP técnico. Entitlement, solicitação auditável, service FastAPI isolado, dependency testável, DAG de backfill controlado, smoke local em dry-run, documentação e runbook implementados. Itens comerciais pós-MVP permanecem documentados e não foram implementados nesta sprint.
**Fase:** Fase 7 — Storage Dinâmico, Particionamento Anual, Retenção e Backup
**Tag de saída prevista:** nenhuma intermediária (tag final da fase: `v4.2.0-dataops` ao fim da Sprint 40)
**Baseline congelado:** Fase 5 finalizada (`v3.8.0-gov`) + Sprints 34, 35, 36, 37 da Fase 7.
**Pré-requisitos validados:** `plataforma.politica_dataset`, `plataforma.calcular_janela_carga_anual`, `plataforma.criar_particao_anual_competencia`, `plataforma.cliente`.
**Schema novo:** nenhum schema criado. Tabelas novas em `plataforma`.

## Decisão Técnica

O MVP da Sprint 38 entrega controle operacional de histórico sob demanda sem criar endpoint admin público, sem billing detalhado e sem exportação completa. A aprovação é operacional via SQL/runbook ou helper interno. A FastAPI recebe apenas o service/dependency de entitlement e não passa a consultar schemas internos de dados.

## Regra-mãe da Fase 7

- [x] Não alterar contrato de API existente.
- [x] Não alterar modelos ou macros dbt.
- [x] Não duplicar base inteira por cliente.
- [x] Não permitir exportação completa por padrão.
- [x] Histórico só é liberado com entitlement ativo por cliente/dataset/faixa.
- [x] Backfill só processa `plataforma.solicitacao_historico` aprovada.
- [x] FastAPI não acessa `bruto_ans`, `nucleo_ans`, `consumo_premium_ans`, `mdm_ans` ou `mdm_privado`.
- [x] Admin endpoint, billing detalhado e rate limit avançado permanecem pós-MVP.

## Contrato Arquitetural

| Item | Valor |
|------|-------|
| Camada criada | Entitlement de histórico + solicitação auditável + backfill controlado |
| Schema físico | `plataforma` |
| Tabelas novas | `plataforma.cliente_dataset_acesso`, `plataforma.solicitacao_historico` |
| Service API | `api/app/services/historico_sob_demanda.py` |
| Dependency | `verificar_entitlement_historico` em `api/app/dependencia.py` |
| DAG | `ingestao/dags/dag_historico_sob_demanda.py` |
| Smoke | `make smoke-historico-sob-demanda` |
| Regra de publicação | Dados premium históricos continuam servidos por rotas/camadas API quando existirem; entitlement consulta apenas `plataforma.*` |
| Rollback | Marcar entitlement `ativo=false`; cancelar solicitações pendentes/aprovadas; dados materializados ficam inacessíveis sem entitlement |

## MVP Técnico

### HIS-38.1 — Tabelas de entitlement e solicitação

- [x] Criado `infra/postgres/init/033_fase7_historico_sob_demanda.sql`.
- [x] `plataforma.cliente_dataset_acesso` criada com FK real `cliente_id uuid references plataforma.cliente(id)`.
- [x] `plataforma.solicitacao_historico` criada com workflow `pendente`, `aprovada`, `em_execucao`, `concluida`, `rejeitada`, `cancelada`, `erro`.
- [x] Índice parcial único impede mais de um entitlement ativo por cliente/dataset.
- [x] Trigger `trg_cliente_dataset_acesso_atualizado_em` criada.

### HIS-38.2 — Service Python e dependency FastAPI

- [x] Criado `api/app/services/historico_sob_demanda.py`.
- [x] `consultar_entitlement` consulta apenas `plataforma.cliente_dataset_acesso`.
- [x] `competencia_na_janela_hot` usa `plataforma.calcular_janela_carga_anual` + `plataforma.politica_dataset`.
- [x] `validar_acesso_competencia` permite hot e bloqueia histórico sem entitlement.
- [x] `validar_paginacao_historica` bloqueia `limite > 1000` e `csv_completo`.
- [x] `aprovar_solicitacao_via_operacao` aprova solicitação e cria entitlement sem endpoint admin.
- [x] `verificar_entitlement_historico` adicionada em `api/app/dependencia.py`, sem aplicação automática em rotas existentes.

### HIS-38.3 — Backfill controlado

- [x] Criado `ingestao/app/historico_sob_demanda.py`.
- [x] Criada `ingestao/dags/dag_historico_sob_demanda.py` com schedule a cada 15 minutos e `max_active_runs=1`.
- [x] A DAG busca somente solicitação `aprovada`, marca `em_execucao`, valida política e cria partições anuais históricas via `plataforma.criar_particao_anual_competencia`.
- [x] Solicitação concluída não é reprocessada.
- [x] Dataset sem permissão histórica vira `erro` controlado.
- [x] Modo local `dry_run=true` validado por smoke; produção sem extractor real falha explicitamente, sem carga falsa.

### HIS-38.4 — Smoke do MVP

- [x] Criado `scripts/smoke_historico_sob_demanda.py`.
- [x] Criado target `make smoke-historico-sob-demanda`.
- [x] Smoke valida:
  - cliente padrão bloqueado em `202401`;
  - cliente premium permitido em `202401`;
  - cliente premium bloqueado fora da faixa em `202301`;
  - competência hot `202602` permitida sem entitlement histórico;
  - DAG/service em dry-run cria partição `bruto_ans.sib_beneficiario_operadora_2024`;
  - solicitação fica `concluida`.

### HIS-38.5 — Documentação e runbook

- [x] Criado `docs/arquitetura/historico_sob_demanda_cliente.md`.
- [x] Criado `docs/runbooks/abrir_historico_premium.md`.
- [x] Documentado que histórico não é estendido automaticamente: faixa caduca e exige novo entitlement.

## Pós-MVP Comercial — Não Implementado Nesta Sprint

- [ ] Endpoint admin público (`api/app/routers/admin_historico.py`).
- [ ] Schemas admin (`api/app/schemas/admin_historico.py`).
- [ ] Coluna `historico_solicitacao_id` em `plataforma.log_uso`.
- [ ] Billing-close com rubrica histórica.
- [ ] Rate limit avançado 5x.
- [ ] UI/admin.
- [ ] Exportação completa controlada por `permite_exportacao=true`.

## Entregas

- [x] `infra/postgres/init/033_fase7_historico_sob_demanda.sql`
- [x] `api/app/services/historico_sob_demanda.py`
- [x] `api/app/dependencia.py`
- [x] `ingestao/app/historico_sob_demanda.py`
- [x] `ingestao/dags/dag_historico_sob_demanda.py`
- [x] `api/tests/integration/test_historico_sob_demanda.py`
- [x] `ingestao/tests/test_dag_historico_sob_demanda.py`
- [x] `scripts/smoke_historico_sob_demanda.py`
- [x] `docs/arquitetura/historico_sob_demanda_cliente.md`
- [x] `docs/runbooks/abrir_historico_premium.md`
- [x] `Makefile`

## Hardgates

- [x] Bootstrap 033 aplicado sem erro.
- [x] `api/tests/integration/test_historico_sob_demanda.py`: 8/8 passando.
- [x] `ingestao/tests/test_dag_historico_sob_demanda.py`: 5/5 passando.
- [x] `make smoke-historico-sob-demanda`: passou em dry-run local.
- [x] `make dag-parse`: 0 erros.
- [x] `.venv/bin/pytest ingestao/tests/ -v`: 86/86 passando.
- [x] `.venv/bin/pytest api/tests/integration/ -v`: 40/40 passando.
- [x] `.venv/bin/pytest testes/regressao/test_endpoints_fase4.py testes/regressao/test_endpoints_fase5.py -v`: 8/8 passando.
- [x] `.venv/bin/ruff check .`: sem erros.
- [x] `git diff --check`: sem erros.
- [x] `git diff --name-only -- healthintel_dbt/models healthintel_dbt/macros`: saída vazia.
- [x] Grep de acesso interno indevido no service/dependency: zero ocorrências.
- [x] Grep `permitir_historico=True` em `ingestao/dags ingestao/app scripts`: zero ocorrências em fluxo padrão.
- [x] `select count(*) from plataforma.solicitacao_historico where status='concluida'`: `1` ou mais após smoke.
- [x] `select to_regclass('bruto_ans.sib_beneficiario_operadora_2024')`: partição histórica existe.

## Resultado Esperado

Sprint 38 entrega o MVP técnico de histórico sob demanda: entitlement por cliente/dataset/faixa, solicitação auditável, validação de acesso hot vs histórico, backfill controlado com partição anual histórica sob demanda e smoke local independente de download real da ANS. A base não é duplicada por cliente, exportação completa permanece bloqueada e rotas existentes não mudam contrato. A comercialização plena depende dos itens pós-MVP listados.

## Evidências de Execução Local — 2026-04-28

- `docker compose -f infra/docker-compose.yml exec -T postgres psql -v ON_ERROR_STOP=1 -U healthintel -d healthintel < infra/postgres/init/033_fase7_historico_sob_demanda.sql`: 0 erros.
- `\dt plataforma.cliente_dataset_acesso` e `\dt plataforma.solicitacao_historico`: tabelas existem.
- `.venv/bin/pytest api/tests/integration/test_historico_sob_demanda.py -v`: `8 passed`.
- `.venv/bin/pytest ingestao/tests/test_dag_historico_sob_demanda.py -v`: `5 passed`.
- `make smoke-historico-sob-demanda`: passou; `padrao_bloqueado=True`, `premium_permitido=True`, `fora_faixa_bloqueado=True`, `hot_permitido=True`, `particao_2024=True`, `solicitacao_concluida=True`.
- `make dag-parse`: 0 erros; saída `Errors: {}`.
- `.venv/bin/pytest ingestao/tests/ -v`: `86 passed in 7.68s`.
- `docker compose -f infra/docker-compose.yml exec -T redis redis-cli FLUSHDB && .venv/bin/pytest api/tests/integration/ -v`: `40 passed in 1.29s`.
- `.venv/bin/pytest testes/regressao/test_endpoints_fase4.py testes/regressao/test_endpoints_fase5.py -v`: `8 passed in 0.68s`.
- `.venv/bin/ruff check .`: `All checks passed!`.
- `git diff --check`: saída vazia.
- `git diff --name-only -- healthintel_dbt/models healthintel_dbt/macros`: saída vazia.
- `grep -rn "bruto_ans\|nucleo_ans\|consumo_premium_ans\|mdm_ans\|mdm_privado" api/app/services/historico_sob_demanda.py api/app/dependencia.py`: zero ocorrências.
- `grep -rn "permitir_historico=True" ingestao/dags ingestao/app scripts`: zero ocorrências em fluxo padrão.
- `select count(*) from plataforma.solicitacao_historico where status='concluida'`: retornou `1` ou mais após smoke.
- `select to_regclass('bruto_ans.sib_beneficiario_operadora_2024')`: retornou `bruto_ans.sib_beneficiario_operadora_2024`.
