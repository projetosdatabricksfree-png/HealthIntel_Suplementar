# Sprint 35 — Particionamento Anual por `competencia YYYYMM`

**Status:** Implementada com validações locais; não concluída automaticamente
**Fase:** Fase 7 — Storage Dinâmico, Particionamento Anual, Retenção e Backup
**Tag de saída prevista:** nenhuma intermediária (tag final da fase: `v4.2.0-dataops` ao fim da Sprint 40)
**Baseline congelado:** Fase 5 finalizada (`v3.8.0-gov`). Estrutura física PostgreSQL existente é migrada para particionamento anual sem alterar a coluna `competencia` nem renomear a tabela-mãe.
**Pré-requisito:** Sprint 34 concluída (tabela `plataforma.politica_dataset` populada). Datasets `grande_temporal` precisam estar marcados `particionar_por_ano=true`.
**Schema novo:** nenhum schema criado. Funções novas em `plataforma`. Tabela nova `plataforma.retencao_particao_log` no schema `plataforma` existente.
**Objetivo:** substituir o conceito de partição mensal das tabelas SIB pelo padrão anual `FOR VALUES FROM (YYYY01) TO ((YYYY+1)01)`, com criação determinística via funções SQL e cobertura por monitoramento de partição default. A coluna `competencia` permanece `YYYYMM` inteiro; somente o limite das partições muda.
**Critério de saída técnico:** três funções novas em `plataforma` (`calcular_janela_carga_anual`, `criar_particao_anual_competencia`, `preparar_particoes_janela_atual`); bootstrap SQL `infra/postgres/init/030_fase7_particionamento_anual.sql` cria as funções e migra `bruto_ans.sib_beneficiario_operadora` e `bruto_ans.sib_beneficiario_municipio` para particionamento anual com partições para `[ano_inicial, ano_preparado]`; partição default cria registro de auditoria em `plataforma.retencao_particao_log`; documento `docs/arquitetura/particionamento_anual_postgres.md` publicado.
**Critério de saída operacional:** `EXPLAIN (ANALYZE, VERBOSE, BUFFERS)` em queries do tipo `WHERE competencia BETWEEN 202601 AND 202612` sobre SIB mostra que apenas a partição anual correta foi lida (ex.: `bruto_ans.sib_beneficiario_operadora_2026`); nenhuma leitura em `_default`, `_2025` ou `_2027`; `select plataforma.preparar_particoes_janela_atual('bruto_ans','sib_beneficiario_operadora',2)` é idempotente; `dbt build` zero erros; nenhum modelo/DAG baseline alterado em sua semântica.

## Regra-mãe da Fase 7 (não negociável nesta sprint)

- [ ] Não alterar contrato de API.
- [ ] Não alterar semântica dos modelos dbt existentes (modelos continuam lendo `bruto_ans.sib_*` exatamente como faziam).
- [ ] Não renomear a tabela-mãe `bruto_ans.sib_beneficiario_operadora` nem `bruto_ans.sib_beneficiario_municipio`.
- [ ] Não alterar a coluna `competencia` (tipo, nome, formato `YYYYMM` inteiro permanece).
- [ ] Toda lógica nova entra em arquivo novo (bootstrap SQL `030_*`, funções novas, documento novo).
- [x] Nenhuma criação automática de partição mensal SIB pode existir na codebase após esta sprint.

## Contrato Arquitetural da Sprint

| Item | Valor |
|------|-------|
| Camada criada | Particionamento anual + governança de partição. |
| Schema físico | `bruto_ans` (tabelas-mãe existentes) + `plataforma` (funções novas + `retencao_particao_log`). |
| Funções novas | `plataforma.calcular_janela_carga_anual`, `plataforma.criar_particao_anual_competencia`, `plataforma.preparar_particoes_janela_atual`. |
| Tabela nova | `plataforma.retencao_particao_log`. |
| Tag dbt | nenhuma (mudança é física PostgreSQL, não dbt). |
| Materialização | DDL declarativa via bootstrap SQL. |
| Upstream permitido | Tabelas existentes `bruto_ans.sib_beneficiario_operadora`, `bruto_ans.sib_beneficiario_municipio`. |
| Downstream esperado | Sprint 36 (filtro de janela), Sprint 38 (criação de partição extra para histórico). |
| Owner técnico | Engenharia de dados + DBA HealthIntel. |
| Owner de negócio | Produto HealthIntel. |
| Classificação LGPD | Operacional/interna (estrutura de partição não contém dados pessoais). |
| Regra de publicação | Interna apenas. |
| Regra de rollback | `attach`/`detach` reversível: detach das partições anuais novas e re-criação das partições antigas a partir de backup `pgbackrest` da janela imediatamente anterior à execução. Documentar passo-a-passo em `docs/operacao/disaster_recovery.md`. |

## Padrão obrigatório

| Padrão | Permitido | Proibido |
|--------|-----------|----------|
| Nome de partição anual | `bruto_ans.sib_beneficiario_operadora_2026` | `bruto_ans.sib_beneficiario_operadora_2026_01` |
| Limite de partição | `FOR VALUES FROM (202601) TO (202701)` | `FOR VALUES FROM (202601) TO (202602)` |
| Partição default | Existe e gera alerta quando recebe linhas | Não existir, ou silenciosa |
| Hardcode de ano | Proibido | Permitido |

## Histórias

### HIS-35.1 — Função de janela anual

- [ ] Criar função `plataforma.calcular_janela_carga_anual(p_anos_carga integer default 2, p_data_referencia date default current_date)` em `infra/postgres/init/030_fase7_particionamento_anual.sql`.
- [ ] Retornar tabela com `ano_vigente`, `ano_inicial`, `ano_final`, `ano_preparado`, `competencia_minima`, `competencia_maxima_exclusiva`.
- [x] Marcar como `language plpgsql stable`.
- [ ] Validar manualmente: `select * from plataforma.calcular_janela_carga_anual(2, date '2026-04-28')` deve retornar `ano_vigente=2026, ano_inicial=2025, ano_final=2026, ano_preparado=2027, competencia_minima=202501, competencia_maxima_exclusiva=202701`.
- [ ] Validar virada de ano: `select * from plataforma.calcular_janela_carga_anual(2, date '2027-01-02')` deve retornar `competencia_minima=202601, competencia_maxima_exclusiva=202801`.

### HIS-35.2 — Função para criar partição anual

- [ ] Criar função `plataforma.criar_particao_anual_competencia(p_schema text, p_tabela text, p_ano integer)` em `language plpgsql`.
- [ ] Calcular `v_inicio = (p_ano * 100) + 1` e `v_fim = ((p_ano + 1) * 100) + 1`.
- [ ] Executar `create table if not exists` para garantir idempotência.
- [ ] Nome físico padrão: `<schema>.<tabela>_<ano>` (ex.: `bruto_ans.sib_beneficiario_operadora_2026`).
- [ ] Registrar criação em `plataforma.retencao_particao_log` (ver HIS-35.4).
- [ ] Validar: `select plataforma.criar_particao_anual_competencia('bruto_ans','sib_beneficiario_operadora',2026)` cria tabela apenas na primeira chamada e é silencioso na segunda.

### HIS-35.3 — Função de preparação da janela atual

- [ ] Criar função `plataforma.preparar_particoes_janela_atual(p_schema text, p_tabela text, p_anos_carga integer default 2)` em `language plpgsql`.
- [ ] Internamente consultar `plataforma.calcular_janela_carga_anual(p_anos_carga)`.
- [ ] Iterar `for v_ano in r.ano_inicial..r.ano_preparado loop` chamando `criar_particao_anual_competencia`.
- [ ] Garantir que em 2026 sejam criadas as partições 2025, 2026 e 2027.
- [ ] Garantir idempotência ao ser chamada repetidas vezes.

### HIS-35.4 — Tabela de auditoria de partição

- [ ] Criar tabela `plataforma.retencao_particao_log`:

```sql
create table if not exists plataforma.retencao_particao_log (
    id bigserial primary key,
    schema_alvo text not null,
    tabela_alvo text not null,
    nome_particao text not null,
    acao text not null check (acao in ('criada','reaproveitada','destacada','removida','default_recebeu_linha')),
    competencia_inicio integer,
    competencia_fim_exclusivo integer,
    motivo text,
    executado_em timestamptz not null default now(),
    executado_por text not null default current_user
);
```

- [ ] Adicionar índice por `(schema_alvo, tabela_alvo, executado_em desc)`.

### HIS-35.5 — Migração das tabelas SIB para particionamento anual

- [ ] Validar que `bruto_ans.sib_beneficiario_operadora` é particionada por RANGE em `competencia` (caso contrário, registrar passo de migração com criação de tabela espelho `_anual` + INSERT SELECT, dentro do mesmo bootstrap, controlado por flag manual; não automatizar destruição).
- [ ] Detach de partições mensais existentes (sem dropar dados; reanexar como tabelas livres em `bruto_ans._historico_mensal`).
- [ ] Criar partições anuais via `plataforma.preparar_particoes_janela_atual('bruto_ans','sib_beneficiario_operadora',2)`.
- [ ] Mesmo procedimento para `bruto_ans.sib_beneficiario_municipio`.
- [ ] Garantir que partição default existe e está nomeada `<tabela>_default`.
- [ ] Validar que linhas existentes foram realocadas para as partições anuais corretas (`select count(*), tableoid::regclass from bruto_ans.sib_beneficiario_operadora group by tableoid::regclass`).

### HIS-35.6 — Trigger de monitoramento da partição default

- [ ] Criar função `plataforma.alertar_default_particao()` em `language plpgsql` que insere registro em `plataforma.retencao_particao_log` com `acao='default_recebeu_linha'` quando uma linha cair na partição default.
- [ ] Aplicar trigger `after insert` na partição default de cada tabela particionada anualmente (`<tabela>_default`).
- [ ] Documentar que esse alerta indica competência fora da janela carregada — comportamento errado em 99% dos casos.

### HIS-35.7 — Documento arquitetural

- [ ] Criar `docs/arquitetura/particionamento_anual_postgres.md`.
- [ ] Documentar exemplo `FOR VALUES FROM (202601) TO (202701)` com referência à doc oficial PostgreSQL (limites inclusivos no início e exclusivos no fim).
- [ ] Documentar fluxo de virada de ano: em 2027, executar `preparar_particoes_janela_atual('bruto_ans','sib_beneficiario_operadora',2)` cria automaticamente 2028; remoção/destacamento de 2025 só após backup válido.
- [ ] Documentar como validar partition pruning via `EXPLAIN (ANALYZE, VERBOSE, BUFFERS)`.
- [ ] Método de validação: inspecionar o plano de execução para confirmar que apenas a partição anual correta foi lida. Exemplo obrigatório de comando e critério esperado:

```sql
EXPLAIN (ANALYZE, VERBOSE, BUFFERS)
SELECT count(*)
FROM bruto_ans.sib_beneficiario_operadora
WHERE competencia BETWEEN 202601 AND 202612;
```

**Critério esperado:**
- O plano deve ler somente `bruto_ans.sib_beneficiario_operadora_2026`.
- Não deve ler partições `_2025`, `_2027` ou `_default`.
- Se a partição default for lida, o hardgate falha.

- [ ] Anti-padrão: nunca usar `LIST` ou `HASH` partitioning para `competencia`. Apenas `RANGE`.

### HIS-35.8 — Validação de partition pruning

- [ ] Executar e capturar `EXPLAIN (ANALYZE, VERBOSE, BUFFERS) SELECT count(*) FROM bruto_ans.sib_beneficiario_operadora WHERE competencia BETWEEN 202601 AND 202612` e anexar saída ao documento arquitetural.
- [ ] Confirmar que apenas a partição `_2026` é lida.
- [ ] Confirmar que nenhuma partição `_2025`, `_2027` ou `_default` aparece no plano.
- [ ] Validar que `Buffers` mostra apenas buffers da partição correta.
- [ ] Critério de falha: se `_default` for lida, o hardgate falha e o particionamento precisa ser corrigido antes de prosseguir.

### HIS-35.9 — Pré-migração segura das partições SIB

Esta história é obrigatória **antes** de qualquer DDL destrutiva nas tabelas SIB existentes. Ela garante que a migração de partições mensais para anuais seja reversível, auditada e não corrompa dados.

- [ ] **Backup pré-migração:** executar `pgbackrest --stanza=healthintel backup --type=full` imediatamente antes da migração. Se a Sprint 39 ainda não foi executada e o pgBackRest não está disponível, realizar **dump físico/lógico emergencial** (ex.: `pg_dump` com compressão + `pg_basebackup`) e documentar explicitamente que este dump é temporário — será substituído pelo pgBackRest da Sprint 39.
- [ ] **Dry-run obrigatório:** executar toda a sequência de migração em um **cluster restaurado** ou **base clone** (via `pgbackrest restore` ou `pg_dump` + `pg_restore` em container espelho) antes de tocar produção.
- [ ] **Medição de volume pré-migração:** registrar o tamanho físico atual de cada tabela SIB e de cada partição mensal via:

```sql
SELECT
    relname AS particao,
    pg_size_pretty(pg_total_relation_size(oid)) AS tamanho,
    pg_total_relation_size(oid) AS tamanho_bytes
FROM pg_class
WHERE relkind = 'r'
  AND relname LIKE 'sib_beneficiario_operadora%'
ORDER BY relname;
```

- [ ] **Estimativa de lock:** documentar que `ALTER TABLE ... ATTACH PARTITION` e `DETACH PARTITION` exigem `ACCESS EXCLUSIVE LOCK` na tabela-mãe. Estimar duração com base no volume medido. Programar janela de downtime se necessário.
- [ ] **Validação de downtime esperado:** estimar em minutos o tempo de janela de manutenção baseado no dry-run. Se > 30 min em VPS, planejar execução em horário de baixa atividade.
- [ ] **Contagem antes/depois por competência:** capturar e armazenar em `plataforma.retencao_particao_log` (motivo = 'pre_migracao_contagem') a contagem de linhas por competência antes e depois da migração:

```sql
-- Antes
SELECT competencia, count(*)::bigint AS total
FROM bruto_ans.sib_beneficiario_operadora
GROUP BY competencia ORDER BY competencia;
```

- [ ] **Validação de soma/hash por amostragem:** após a migração, selecionar por amostragem 3 competências (início, meio, fim da janela) e comparar hash agregado (`md5(string_agg(linha::text, '' order by pk))`) entre a tabela original (pré-migração, preservada em dump) e a tabela particionada anual. Se houver divergência, abortar rollback.
- [ ] **Plano de rollback:** documentar passo-a-passo:
  1. Parar ingestão (Sprint 36 ainda não executada? Se sim, pausar DAGs).
  2. Detach partições anuais novas.
  3. Re-attach partições mensais originais (preservadas como tabelas livres em `bruto_ans._historico_mensal`).
  4. Restaurar de backup pgBackRest se attach falhar.
  5. Reativar ingestão e validar com `dbt test` + smoke API.
- [ ] **Proibição de dropar partições mensais antigas:** as partições mensais originais **não podem ser removidas** antes de:
  - backup válido confirmado;
  - contagem antes = contagem depois validada;
  - `dbt build --select tag:fato` zero erros;
  - smoke API dos endpoints derivados de SIB passa.
  Após validação, as partições mensais devem ser destacadas como tabelas livres em `bruto_ans._historico_mensal` (nunca droppedas sem backup externo).
- [ ] **Migração por tabela espelho:** se a tabela-mãe atual (`bruto_ans.sib_beneficiario_operadora`) não permitir conversão segura para particionamento anual (ex.: já é particionada com partições mensais e o `ALTER TABLE ... ATTACH` causaria conflito), **criar tabela espelho** `bruto_ans.sib_beneficiario_operadora_anual` com particionamento RANGE anual, `INSERT ... SELECT` a partir da tabela original, e depois renomear (swap atômico) com downtime mínimo.

**Hardgates da HIS-35.9:**

- [ ] `pgbackrest check` passa (ou dump emergencial existe e está documentado como temporário).
- [ ] Contagem total de linhas antes = contagem total de linhas depois (tolerância zero).
- [ ] Contagem por competência antes = contagem por competência depois para cada competência na janela (via query agrupada).
- [ ] Nenhuma linha em partição `_default` após a migração (`select count(*) from bruto_ans.sib_beneficiario_operadora_default` = 0).
- [ ] `dbt build --select tag:fato` zero erros (modelos SIB downstream intactos).
- [ ] `dbt test --select tag:fato` zero falhas.
- [ ] Smoke API SIB: `make smoke-sib` zero falhas (endpoints derivados respondendo).
- [ ] `pytest api/tests/integration/test_sib.py` zero falhas.
- [ ] Partições mensais originais preservadas em `bruto_ans._historico_mensal` (não droppedas).
- [ ] Hash por amostragem de 3 competências confere entre pré e pós-migração.
- [ ] Plano de rollback documentado em `docs/arquitetura/particionamento_anual_postgres.md`.

## Entregas esperadas

- [x] `infra/postgres/init/030_fase7_particionamento_anual.sql`
- [x] `docs/arquitetura/particionamento_anual_postgres.md`
- [x] Funções `plataforma.calcular_janela_carga_anual`, `plataforma.criar_particao_anual_competencia`, `plataforma.preparar_particoes_janela_atual`
- [x] Tabela `plataforma.retencao_particao_log`
- [x] Partições anuais materializadas em `bruto_ans.sib_beneficiario_operadora` e `bruto_ans.sib_beneficiario_municipio` (2025, 2026, 2027 em 2026)
- [x] Trigger de monitoramento da partição default

## Validação esperada (hard gates)

Cada item abaixo precisa de evidência objetiva. Marcar `[x]` apenas após execução real.

- [x] `select * from plataforma.calcular_janela_carga_anual(2, date '2026-04-28')` retorna `ano_inicial=2025, ano_final=2026, ano_preparado=2027, competencia_minima=202501, competencia_maxima_exclusiva=202701`.
- [x] `select * from plataforma.calcular_janela_carga_anual(2, date '2027-01-02')` retorna `competencia_minima=202601, competencia_maxima_exclusiva=202801`.
- [ ] `select tableoid::regclass, count(*) from bruto_ans.sib_beneficiario_operadora group by tableoid::regclass` mostra apenas partições anuais (`_2025`, `_2026`, `_2027`, `_default`).
- [x] `EXPLAIN (ANALYZE, VERBOSE, BUFFERS) SELECT count(*) FROM bruto_ans.sib_beneficiario_operadora WHERE competencia BETWEEN 202601 AND 202612` mostra apenas `bruto_ans.sib_beneficiario_operadora_2026` sendo lida no plano. Sem leitura em `_2025`, `_2027` ou `_default`.
- [ ] Se `_default` for lida no `EXPLAIN (ANALYZE, VERBOSE, BUFFERS)`, o hardgate falha e o particionamento precisa ser corrigido.
- [x] `select plataforma.preparar_particoes_janela_atual('bruto_ans','sib_beneficiario_operadora',2)` é idempotente (segunda execução não cria partição duplicada).
- [x] `select count(*) from bruto_ans.sib_beneficiario_operadora_default` retorna `0` em janela hot. Se >0, registro correspondente em `plataforma.retencao_particao_log` com `acao='default_recebeu_linha'`.
- [ ] `dbt build --select tag:fato` zero erros (modelos SIB downstream continuam funcionando).
- [ ] `dbt test --select tag:fato` zero falhas.
- [x] `pytest api/tests/integration/test_*.py` zero falhas (endpoints SIB-derivados continuam respondendo).
- [ ] `git diff --stat v3.8.0-gov -- healthintel_dbt/models healthintel_dbt/macros api/app ingestao/dags` saída vazia (nenhum modelo/DAG baseline alterado por esta sprint).
- [x] `grep -rn '_2026_01\|_2026_02\|_2025_01' infra/postgres ingestao` retorna zero ocorrências (nenhuma referência a partição mensal sobrevive).

## Distinção Estado Atual vs Estado-Alvo

| Eixo | Estado atual | Estado-alvo da Sprint 35 |
|------|--------------|--------------------------|
| Padrão de partição | RANGE por `competencia` mensal (`_2024_01`, `_2024_02`, ...). | RANGE por `competencia` anual (`_2024`, `_2025`, ...). |
| Função de janela | Inexistente. | `plataforma.calcular_janela_carga_anual` disponível e stable. |
| Função de criação | Inexistente. | `plataforma.criar_particao_anual_competencia` + `preparar_particoes_janela_atual`. |
| Auditoria de partição | Inexistente. | `plataforma.retencao_particao_log` populada a cada criação/destacamento. |
| Partição default | Sem trigger. | Trigger de alerta integrada à `retencao_particao_log`. |
| Modelos dbt | Baseline `v3.8.0-gov`. | Idem (sem alteração). |
| Endpoints API | Baseline `v3.8.0-gov`. | Idem (sem alteração). |

## Anti-padrões explicitamente rejeitados nesta sprint

- Renomear `bruto_ans.sib_beneficiario_operadora` para `bruto_ans.sib_beneficiario_operadora_anual` (proibido — quebra modelos staging).
- Alterar tipo da coluna `competencia` para `date`/`text`.
- Criar partições mensais "como compatibilidade" — proibido.
- Dropar dados antigos sem backup `pgbackrest` válido (Sprint 39 ainda não executada).
- Usar `LIST` partitioning ou `HASH` partitioning sobre `competencia`.
- Hardcodar ano em código Python ou SQL (deve sempre vir de `plataforma.calcular_janela_carga_anual`).
- Marcar hardgates `[x]` antes de executar os comandos correspondentes.

## Resultado Esperado

Sprint 35 entrega o particionamento anual obrigatório da Fase 7. Tabelas SIB passam a ser organizadas por ano calendário (`_2025`, `_2026`, `_2027`), o sistema cria automaticamente as partições da janela vigente + ano preparado, e a coluna `competencia` permanece `YYYYMM` inteiro. Funções `plataforma.*` ficam disponíveis para serem chamadas pelas Sprints 36 (janela dinâmica) e 38 (histórico sob demanda). Nenhum modelo dbt nem endpoint API do baseline `v3.8.0-gov` é alterado em sua semântica.

## Evidências de execução local — 2026-04-28

### Pré-check

- `plataforma.politica_dataset`: `sib_operadora` e `sib_municipio` existem como `grande_temporal` com `particionar_por_ano=true`.
- `pg_class`: `bruto_ans.sib_beneficiario_operadora` e `bruto_ans.sib_beneficiario_municipio` têm `relkind='p'`.
- `pg_inherits`: antes do bootstrap, ambas as tabelas tinham apenas partição `_default`.
- `count(*)` nas defaults antes do bootstrap: `0` para operadora e `0` para município.

### Bootstrap aplicado

Comando:

```bash
docker compose -f infra/docker-compose.yml exec -T postgres psql -v ON_ERROR_STOP=1 -U healthintel -d healthintel < infra/postgres/init/030_fase7_particionamento_anual.sql
```

Resultado: `CREATE TABLE`, `CREATE INDEX`, `CREATE FUNCTION`, triggers criadas e chamadas a `plataforma.preparar_particoes_janela_atual` concluídas sem erro.

### Banco

- `SELECT * FROM plataforma.calcular_janela_carga_anual(2, date '2026-04-28')`: `2026 | 2025 | 2026 | 2027 | 202501 | 202701`.
- `SELECT * FROM plataforma.calcular_janela_carga_anual(2, date '2027-01-02')`: `2027 | 2026 | 2027 | 2028 | 202601 | 202801`.
- `SELECT * FROM plataforma.calcular_janela_carga_anual(0, date '2026-04-28')`: erro esperado `p_anos_carga deve ser maior ou igual a 1`.
- `pg_inherits` para SIB operadora: `_default`, `_2025`, `_2026`, `_2027`.
- `pg_inherits` para SIB município: `_default`, `_2025`, `_2026`, `_2027`.
- Segunda execução de `preparar_particoes_janela_atual('bruto_ans','sib_beneficiario_operadora',2)`: sem erro; log de operadora registrou `criada=3` e `reaproveitada=3`.
- `SELECT count(*) FROM bruto_ans.sib_beneficiario_operadora_default`: `0`.

### Pruning

Comando:

```sql
EXPLAIN (ANALYZE, VERBOSE, BUFFERS)
SELECT count(*)
FROM bruto_ans.sib_beneficiario_operadora
WHERE competencia BETWEEN 202601 AND 202612;
```

Evidência: plano executou `Index Only Scan` somente em `bruto_ans.sib_beneficiario_operadora_2026`. Não apareceram `_2025`, `_2027` nem `_default`.

### Testes e lint

- `cd healthintel_dbt && DBT_LOG_PATH=/tmp/healthintel_dbt_logs DBT_TARGET_PATH=/tmp/healthintel_dbt_target ../.venv/bin/dbt parse`: exit code `0`.
- `.venv/bin/pytest ingestao/tests/test_particionamento_anual.py -v`: `12 passed`.
- `.venv/bin/pytest ingestao/tests/ -v`: `29 passed`.
- `.venv/bin/pytest api/tests/ -v`: `62 passed`.
- `.venv/bin/ruff check .`: `All checks passed!`.

### Baseline e limitações

- `git diff --name-only -- healthintel_dbt/models healthintel_dbt/macros api/app`: saída vazia.
- `git diff --name-only -- ingestao/dags`: apenas `ingestao/dags/dag_criar_particao_mensal.py`.
- `grep -rn "_2026_01\|_2026_02\|_2025_01\|FOR VALUES FROM (202601) TO (202602)" infra/postgres ingestao`: zero ocorrências.
- `v3.8.0-gov` ausente neste clone: `fatal: Needed a single revision`; baseline validado por diff explícito de paths protegidos.
- `pgBackRest` permanece fora do escopo e previsto para Sprint 39; não foi executado backup full.
- Banco local SIB permanece sem linhas nas tabelas SIB; validação de migração real por volume, hash e downtime fica pendente para ambiente com dados.
- A DAG `dag_criar_particao_mensal.py` manteve nome legado por compatibilidade, removeu criação mensal SIB e preservou criação mensal de `plataforma.log_uso`, que é log operacional fora do escopo de `competencia` SIB.
