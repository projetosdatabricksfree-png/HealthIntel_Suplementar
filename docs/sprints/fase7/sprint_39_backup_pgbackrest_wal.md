# Sprint 39 — Backup Full, Diferencial e WAL Archive com pgBackRest

**Status:** Em validação operacional
**Fase:** Fase 7 — Storage Dinâmico, Particionamento Anual, Retenção e Backup
**Tag de saída prevista:** nenhuma intermediária (tag final da fase: `v4.2.0-dataops` ao fim da Sprint 40)
**Baseline congelado:** Fase 5 finalizada (`v3.8.0-gov`) + Sprints 34, 35, 36, 37, 38 da Fase 7. Particionamento anual e janela dinâmica já operacionais.
**Pré-requisitos:** Sprints 34–38 concluídas. Existe runtime PostgreSQL alvo (VPS) com volume dedicado para `pg_wal` e diretório de backup local.
**Schema novo:** nenhum schema criado. Tabela nova `plataforma.backup_execucao` no schema `plataforma` existente.
**Objetivo:** instalar e configurar **pgBackRest** como ferramenta oficial de backup do PostgreSQL na VPS, com full diário, diferencial a cada 6h, WAL archive contínuo (`archive_timeout=3600`), repositório local temporário e repositório externo S3-compatible com criptografia. Toda execução é auditada em `plataforma.backup_execucao`. Backup somente na VPS é explicitamente declarado como **não disaster recovery**.
**Critério de saída técnico:** pgBackRest instalado; `postgresql.conf` com `archive_mode=on`, `archive_command='pgbackrest --stanza=healthintel archive-push %p'`, `archive_timeout=3600`, `wal_level=replica`, `max_wal_senders>=2`; `pgbackrest.conf` com stanza `healthintel`, repositório 1 local (`repo1-path`), repositório 2 externo S3-compatible com `repo2-cipher-type=aes-256-cbc`; cron/systemd timer chamando `pgbackrest --stanza=healthintel backup --type=full` (1×/dia) e `--type=diff` (4×/dia); job de monitoramento que insere em `plataforma.backup_execucao` em cada execução.
**Critério de saída operacional:** `pgbackrest check --stanza=healthintel` zero erros; `pgbackrest info --stanza=healthintel` mostra ao menos 1 full + 4 diffs do dia; `select max(iniciado_em) from plataforma.backup_execucao where tipo='wal'` é < 1h; alerta operacional configurado para crescimento de `pg_wal`.

## Regra-mãe da Fase 7 (não negociável nesta sprint)

- [ ] Não alterar contrato de API.
- [ ] Não alterar semântica de modelos dbt.
- [ ] Toda execução de backup é registrada em `plataforma.backup_execucao` (auditoria obrigatória).
- [ ] Backup somente na mesma VPS **não é disaster recovery** — repositório externo S3-compatible é obrigatório antes de cliente pagante.
- [ ] Criptografia obrigatória no repositório externo (`repo*-cipher-type` + `repo*-cipher-pass`).
- [ ] Senhas/chaves nunca em git; entram via `.env` ou secret manager.
- [ ] Toda alteração de configuração PostgreSQL passa por revisão e tem rollback documentado.
- [ ] `pgbackrest check` deve passar **antes** de declarar backup operacional.

## Contrato Arquitetural da Sprint

| Item | Valor |
|------|-------|
| Camada criada | Operação de backup PostgreSQL com pgBackRest. |
| Schema físico | `plataforma` (tabela nova `backup_execucao`). |
| Configuração nova | `/etc/pgbackrest/pgbackrest.conf` (na VPS) + `postgresql.conf` ajustado. |
| Cron/timer | systemd timer ou cron com `OnCalendar`/`*/360min` para diff e diário 03:00 para full. |
| Repositório 1 (local) | `/var/lib/pgbackrest`, retenção full=2/diff=2 dias, WAL=48h ou limite de disco. |
| Repositório 2 (externo) | S3-compatible (Cloudflare R2, AWS S3, Backblaze B2, Wasabi), criptografia AES-256, retenção full=35/diff=7/WAL=35 dias. |
| Owner técnico | DBA/SRE HealthIntel. |
| Owner de negócio | Operação HealthIntel. |
| Classificação LGPD | Operacional crítico (contém dados ANS pseudonimizados; não contém PII além do já público). |
| Regra de publicação | Interna apenas. Backups nunca expostos externamente. |
| Regra de rollback | Reverter `postgresql.conf` (manter `archive_command` apontando para `cp /dev/null`), parar timers, manter `plataforma.backup_execucao` para auditoria. |

## Histórias

### HIS-39.1 — Tabela `plataforma.backup_execucao`

- [x] Criar `infra/postgres/init/034_fase7_backup_execucao.sql`.
- [x] DDL:

```sql
create table if not exists plataforma.backup_execucao (
    id bigserial primary key,
    stanza text not null default 'healthintel',
    tipo text not null check (tipo in ('full','diff','incr','wal','check','info','restore_test')),
    repositorio text not null check (repositorio in ('repo1_local','repo2_externo')),
    iniciado_em timestamptz not null,
    finalizado_em timestamptz,
    duracao_segundos integer generated always as
        (case when finalizado_em is null then null else extract(epoch from (finalizado_em - iniciado_em))::int end) stored,
    status text not null check (status in ('sucesso','falha','em_execucao')),
    bytes_armazenados bigint,
    bytes_delta bigint,
    log_resumo text,
    erro text,
    executado_por text not null default current_user
);
create index if not exists ix_backup_execucao_lookup
    on plataforma.backup_execucao (stanza, tipo, iniciado_em desc);
```

### HIS-39.2 — Configuração `postgresql.conf`

- [x] Em `infra/postgres/conf/postgresql.fase7.conf` registrar:

```conf
wal_level = replica
archive_mode = on
archive_command = 'pgbackrest --stanza=healthintel archive-push %p'
archive_timeout = 3600
max_wal_senders = 4
wal_keep_size = 1GB
checkpoint_timeout = 5min
```

- [x] Documentar passo de aplicação (`include` no compose ou patch via `ALTER SYSTEM`).
- [x] Documentar advertência: `archive_timeout` muito curto aumenta volume; `3600` é o equilíbrio.

### HIS-39.3 — Configuração `pgbackrest.conf`

- [x] Criar `infra/pgbackrest/pgbackrest.conf` com:

```ini
[global]
process-max=2
log-level-console=info
log-level-file=detail
start-fast=y
compress-type=zst
compress-level=3

repo1-path=/var/lib/pgbackrest
repo1-retention-full-type=time
repo1-retention-full=2
repo1-retention-diff=2
# ATENÇÃO: repo1-retention-diff = quantidade de backups diferenciais retidos (não dias).
# O pgBackRest não oferece retention-diff-type=time. A retenção temporal de diffs
# é consequência da retenção temporal do full: diffs anteriores ao full mais antigo
# são descartados automaticamente.

repo2-type=s3
repo2-s3-endpoint=${PGBACKREST_REPO2_ENDPOINT}
repo2-s3-bucket=${PGBACKREST_REPO2_BUCKET}
repo2-s3-region=${PGBACKREST_REPO2_REGION}
repo2-s3-key=${PGBACKREST_REPO2_KEY}
repo2-s3-key-secret=${PGBACKREST_REPO2_KEY_SECRET}
repo2-cipher-type=aes-256-cbc
repo2-cipher-pass=${PGBACKREST_REPO2_CIPHER_PASS}
repo2-retention-full-type=time
repo2-retention-full=35
repo2-retention-diff=7
# ATENÇÃO: repo2-retention-diff = quantidade de backups diferenciais retidos, não dias.
# Não há retention-diff-type=time no pgBackRest.
# Diferencias anteriores ao full mais antigo retido são descartados automaticamente.

[healthintel]
pg1-path=${POSTGRES_DATA_DIR}
pg1-port=5432
pg1-user=postgres
```

- [x] Documentar variáveis em `.env.exemplo` (sem valores reais).
- [x] Documentar uso de secret manager em produção.

### HIS-39.4 — Stanza, init e check

- [x] Documentar comando único `pgbackrest --stanza=healthintel stanza-create` para inicialização.
- [x] Documentar `pgbackrest --stanza=healthintel check` como hardgate antes de aceitar backup como operacional.
- [x] Criar script `scripts/backup/pgbackrest_init.sh` que executa `stanza-create` + `check` + grava resultado em `plataforma.backup_execucao`.

### HIS-39.5 — Schedule de backup

- [x] Criar systemd timers em `infra/systemd/`:
  - `pgbackrest-full.service`/`.timer` — `OnCalendar=*-*-* 03:00:00`.
  - `pgbackrest-diff.service`/`.timer` — `OnCalendar=*-*-* 00,06,12,18:00:00`.
- [x] Cada serviço chama wrapper `scripts/backup/pgbackrest_run.sh --type=<tipo>` que:
  - insere `iniciado_em` em `plataforma.backup_execucao`;
  - executa `pgbackrest --stanza=healthintel backup --type=<tipo>`;
  - lê stdout/stderr e captura métricas (`bytes_armazenados`, `bytes_delta` via `pgbackrest info --output=json`);
  - atualiza `finalizado_em`, `status`, `bytes_*`, `log_resumo`/`erro`.
- [x] Garantir que `pgbackrest archive-push` é chamado pelo PostgreSQL (não pelo timer). Apenas registrar `tipo='wal'` em `plataforma.backup_execucao` quando archive-push for executado (via gatilho de monitoramento).

### HIS-39.6 — Monitoramento e alertas

- [x] Criar exportador simples (ou script de cron) que verifica:
  - último `wal` com `iniciado_em > now() - interval '1 hour'`;
  - tamanho do diretório `pg_wal` (alerta se > 5 GB ou > limite operacional);
  - último `full` com `iniciado_em > now() - interval '26 hours'`;
  - último `diff` com `iniciado_em > now() - interval '7 hours'`.
- [x] Integrar com `prometheus`/`alertmanager` se disponível, ou registrar em `plataforma.backup_alerta`.
- [x] Documentar runbook curto `docs/runbooks/backup_postgres.md`.

### HIS-39.7 — Documentação e DR explícito

- [x] Criar `docs/operacao/backup_retencao_postgres.md` com matriz de retenção.
- [x] A matriz de retenção no documento deve separar explicitamente três tipos de retenção:

**Retenção por tempo (repositório local — repo1):**
| Tipo | Parâmetro | Valor | Unidade |
|------|-----------|-------|---------|
| Full | `repo1-retention-full-type=time` / `repo1-retention-full` | 2 | dias |
| Diff | `repo1-retention-diff` | 2 | quantidade (backups retidos) |
| WAL | `archive_timeout=3600` + monitoramento | 48h ou limite de disco | horas |

**Retenção por tempo (repositório externo — repo2):**
| Tipo | Parâmetro | Valor | Unidade |
|------|-----------|-------|---------|
| Full | `repo2-retention-full-type=time` / `repo2-retention-full` | 35 | dias |
| Diff | `repo2-retention-diff` | 7 | quantidade (backups retidos) |
| WAL/PITR | `repo2-retention-full-type=time` cobre WAL | 35 | dias |

**Retenção por quantidade (aplicável a diffs em ambos os repositórios):**
| Item | Parâmetro | Valor | Observação |
|------|-----------|-------|------------|
| Diff local | `repo1-retention-diff` | 2 | quantidade, não dias |
| Diff externo | `repo2-retention-diff` | 7 | quantidade, não dias |

**Retenção de WAL / PITR:**
| Item | Repositório | Período | Observação |
|------|-------------|---------|------------|
| WAL archive local | repo1 | 48h | Limitado por disco; descartado junto com full antigo |
| WAL archive externo | repo2 | 35 dias | Coberto pela retenção temporal do full (`repo2-retention-full-type=time` = 35 dias) |
| PITR externo | repo2 | 35 dias | Permite restore point-in-time dentro da janela de 35 dias |

**Linhas-guia:**
- `repo*-retention-full-type=time` define retenção temporal (dias) para fulls.
- `repo*-retention-diff` define **quantidade** de diffs retidos, não tempo. Diffs anteriores ao full mais antigo retido são descartados automaticamente.
- A retenção de WAL está vinculada à retenção do full mais antigo: o pgBackRest descarta WALs mais antigos que o full base de retenção.
- O PITR máximo possível é igual ao período de retenção do full mais antigo + cobertura contínua de WAL dentro desse período.

- [x] Criar `docs/operacao/disaster_recovery.md` com regra: "backup somente local não é DR; recomendar storage externo S3-compatible antes de cliente pagante".
- [x] Documentar RPO alvo: 1h. RTO alvo MVP: até 8h.
- [x] Documentar custo aproximado mensal por GB nos provedores S3-compatible candidatos.
- [x] Atualizar `docs/sprints/fase7/README.md` linkando para os novos documentos.

### HIS-39.8 — Testes/validações

- [x] Criar smoke `scripts/backup/smoke_pgbackrest.sh` que:
  - executa `pgbackrest check`;
  - inspeciona última linha de `plataforma.backup_execucao` por tipo;
  - falha se algum critério acima estiver vermelho.
- [x] Smoke é parte do `make smoke-pgbackrest` (alvo novo no `Makefile`).

## Entregas esperadas

- [x] `infra/postgres/init/034_fase7_backup_execucao.sql`
- [x] `infra/postgres/conf/postgresql.fase7.conf`
- [x] `infra/pgbackrest/pgbackrest.conf` (template)
- [x] `infra/systemd/pgbackrest-full.service` + `.timer`
- [x] `infra/systemd/pgbackrest-diff.service` + `.timer`
- [x] `scripts/backup/pgbackrest_init.sh`
- [x] `scripts/backup/pgbackrest_run.sh`
- [x] `scripts/backup/smoke_pgbackrest.sh`
- [x] Alvo `make smoke-pgbackrest`
- [x] `docs/operacao/backup_retencao_postgres.md`
- [x] `docs/operacao/disaster_recovery.md`
- [x] `docs/runbooks/backup_postgres.md`
- [x] `.env.exemplo` com variáveis `PGBACKREST_REPO2_*`

## Validação esperada (hard gates)

- [ ] `pgbackrest --stanza=healthintel check` zero erros.
- [ ] `pgbackrest --stanza=healthintel info --output=json` mostra ao menos 1 full do dia e ao menos 4 diffs do dia (após 24h de operação).
- [ ] `select max(iniciado_em) from plataforma.backup_execucao where tipo='wal'` retorna timestamp < 1h.
- [ ] `select count(*) from plataforma.backup_execucao where tipo='full' and status='sucesso' and iniciado_em > now() - interval '26 hours'` >= 1.
- [ ] `select count(*) from plataforma.backup_execucao where tipo='diff' and status='sucesso' and iniciado_em > now() - interval '24 hours'` >= 4.
- [ ] `pgbackrest --stanza=healthintel info` mostra repositório 2 (externo) com pelo menos 1 full nos últimos 35 dias.
- [ ] Alerta de `pg_wal` configurado: simulação artificial (escrever 6 GB) dispara alerta em até 5 min.
- [ ] `make smoke-pgbackrest` zero falhas.
- [ ] `git diff --stat v3.8.0-gov -- healthintel_dbt/models healthintel_dbt/macros api/app` saída vazia.
- [ ] `pytest api/tests/integration/` zero falhas (PostgreSQL continua respondendo normalmente sob `archive_mode=on`).
- [ ] Documento `docs/operacao/disaster_recovery.md` cita explicitamente que backup somente local não é DR.

## Distinção Estado Atual vs Estado-Alvo

| Eixo | Estado atual | Estado-alvo da Sprint 39 |
|------|--------------|--------------------------|
| Backup | Não há backup operacional contínuo. | pgBackRest com full diário + diff 6h + WAL archive contínuo. |
| WAL archive | Inexistente. | `archive_mode=on`, `archive_timeout=3600`. |
| Repositório | Inexistente. | Repo1 local + Repo2 externo S3-compatible criptografado. |
| Auditoria | Inexistente. | `plataforma.backup_execucao` populada por wrapper. |
| Alerta | Inexistente. | Alerta de WAL atrasado e crescimento de `pg_wal`. |
| Documentação DR | Inexistente. | `disaster_recovery.md` declara explicitamente que backup local não é DR. |
| Modelos dbt / API | Baseline `v3.8.0-gov`. | Idem. |

## Anti-padrões explicitamente rejeitados nesta sprint

- Subir backup sem `pgbackrest check` aprovado.
- Configurar `archive_command='cp ... /local'` em vez de pgBackRest.
- Reduzir `archive_timeout` abaixo de 600s sem justificativa documentada.
- Confiar em backup local apenas para clientes pagantes (proibido).
- Comprometer chaves/secrets em git (proibido).
- Pular criptografia no repositório externo.
- Marcar hardgates `[x]` antes de executar os comandos correspondentes.

## Resultado Esperado

Sprint 39 entrega o backup operacional do PostgreSQL na VPS: pgBackRest com full diário, diferencial a cada 6h, WAL archive contínuo, repositórios local e externo S3-compatible com criptografia, retenção alinhada à política da Fase 7, auditoria em `plataforma.backup_execucao` e alertas operacionais. Backup deixa de ser teórico e vira a base sobre a qual a Sprint 40 (restore + PITR + release `v4.2.0-dataops`) se sustenta.
