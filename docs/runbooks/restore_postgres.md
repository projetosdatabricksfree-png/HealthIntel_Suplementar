# Runbook — Restore PostgreSQL (full, diff, PITR)

## Quando usar

| Cenario | Tipo de restore |
|---------|----------------|
| Erro logico em tabela (delete acidental, dado corrompido) | PITR no timestamp anterior ao erro |
| Corrupcao parcial do cluster | latest (WAL replay completo) |
| Perda do cluster com VPS acessivel | latest a partir do repo1 |
| Perda da VPS | latest a partir do repo2 (S3) |
| Teste de DR / Sprint 40 | PITR para timestamp documentado |

## Pre-requisitos

- pgBackRest instalado na VPS (`which pgbackrest`)
- Stanza inicializada (`pgbackrest --stanza=healthintel check`)
- PostgreSQL **parado** antes de qualquer restore
- Cluster alvo com `PGDATA` vazio (restore nunca sobre producao ativa)
- Para repo2: variáveis `PGBACKREST_REPO2_*` carregadas de `/etc/healthintel/pgbackrest.env`

## Passo a passo

### 1. Identificar ponto de restauracao

```bash
# Ver todos os backups disponíveis (repo1 + repo2)
sudo -u postgres pgbackrest --stanza=healthintel info

# Verificar cobertura WAL em plataforma.backup_execucao
psql -U postgres -d healthintel -c "
  SELECT tipo, status, iniciado_em, finalizado_em
  FROM plataforma.backup_execucao
  WHERE tipo IN ('full', 'diff', 'wal', 'check')
  ORDER BY iniciado_em DESC
  LIMIT 20;
"
```

### 2. Parar PostgreSQL

```bash
sudo systemctl stop postgresql
# ou
sudo -u postgres pg_ctlcluster 16 main stop
```

Confirmar que está parado:

```bash
pg_isready -h /var/run/postgresql -U postgres && echo "AINDA ATIVO" || echo "OK: parado"
```

### 3. Limpar PGDATA (necessario para restore)

```bash
PGDATA=/var/lib/postgresql/16/main
sudo rm -rf "${PGDATA}"
sudo mkdir -p "${PGDATA}"
sudo chown postgres:postgres "${PGDATA}"
```

### 4a. Restore latest (WAL replay completo)

```bash
# A partir do repo1 (local)
sudo -u postgres bash scripts/backup/pgbackrest_restore.sh \
  --type=latest --repo=1 --confirm

# A partir do repo2 (S3 — usar quando VPS com repo1 for perdida)
sudo -u postgres bash scripts/backup/pgbackrest_restore.sh \
  --type=latest --repo=2 --confirm
```

### 4b. Restore PITR (para timestamp exato)

```bash
# Identificar o timestamp alvo (UTC-3 para Brasil)
# Exemplo: reverter erro logico ocorrido em 2026-05-06 às 14:30 BRT
sudo -u postgres bash scripts/backup/pgbackrest_restore.sh \
  --type=pitr \
  --target='2026-05-06 14:29:00-03' \
  --repo=1 \
  --confirm
```

### 5. Validar cluster restaurado

O script `pgbackrest_restore.sh` inicia o PostgreSQL automaticamente. Verificar:

```bash
# Conectividade
pg_isready -h /var/run/postgresql -U postgres

# Contagem de tabelas Core
psql -U postgres -d healthintel -c "
  SELECT table_schema, COUNT(*) AS tabelas
  FROM information_schema.tables
  WHERE table_schema IN ('api_ans', 'bruto_ans', 'plataforma')
  GROUP BY table_schema ORDER BY table_schema;
"

# Smoke da API (subir API em porta temporária antes de trocar tráfego)
SMOKE_BASE_URL=http://localhost:8080 python scripts/smoke_core.py

# Testes dbt
make dbt-test-core
```

### 6. Registrar evidencia

Apos o restore bem-sucedido, registrar RTO observado:

```bash
# Calcular RTO: tempo entre "backup mais recente" e "API validada"
# Preencher em docs/operacao/baseline_capacidade.md:

echo "Restore PITR executado em $(date --iso-8601=seconds)" \
  >> docs/operacao/baseline_capacidade.md
```

Verificar registro automático em `plataforma.backup_execucao`:

```sql
SELECT tipo, status, iniciado_em, finalizado_em, log_resumo
FROM plataforma.backup_execucao
WHERE tipo = 'restore_test'
ORDER BY iniciado_em DESC
LIMIT 5;
```

### 7. Promover para producao (apenas apos validacao completa)

Somente após o smoke + `make dbt-test-core` passarem:

```bash
# Redirecionar tráfego (Caddy / load balancer)
# Atualizar plataforma.backup_execucao com observacao
psql -U postgres -d healthintel -c "
  UPDATE plataforma.backup_execucao
  SET log_resumo = log_resumo || ' | promovido_producao_em=' || now()::text
  WHERE tipo = 'restore_test'
    AND status = 'sucesso'
    AND finalizado_em > now() - interval '2 hours';
"
```

## Restore a partir do repo2 (VPS perdida)

Quando a VPS original foi perdida:

```bash
# 1. Provisionar nova VPS equivalente (mesmo OS, PostgreSQL 16, pgBackRest)
# 2. Copiar /etc/healthintel/pgbackrest.env do cofre de segredos
# 3. Instalar pgbackrest.conf com repo2 ativo:
set -a; source /etc/healthintel/pgbackrest.env; set +a
envsubst < infra/pgbackrest/pgbackrest.conf > /etc/pgbackrest/pgbackrest.conf
chmod 640 /etc/pgbackrest/pgbackrest.conf; chown postgres:postgres /etc/pgbackrest/pgbackrest.conf

# 4. Verificar acesso ao repo2
sudo -u postgres pgbackrest --stanza=healthintel --repo=2 check

# 5. Restaurar
sudo -u postgres bash scripts/backup/pgbackrest_restore.sh \
  --type=latest --repo=2 --confirm

# 6. Validar e promover conforme passos 5-7 acima
```

## Checklist de evidencia (Sprint 40)

- [ ] Restore PITR executado em host isolado (nao VPS de producao)
- [ ] Timestamp alvo documentado e confirmado no cluster restaurado
- [ ] Smoke Core passou (`make smoke-core`)
- [ ] `dbt test --select tag:core_ans` passou
- [ ] Registro em `plataforma.backup_execucao` com `tipo='restore_test'` e `status='sucesso'`
- [ ] RTO observado registrado em `docs/operacao/baseline_capacidade.md`
- [ ] Restore do repo2 (S3) testado independentemente do repo1
- [ ] Resultado documentado em `docs/sprints/fase7/sprint_40_restore_pitr_release.md`

## Troubleshooting

| Erro | Causa provavel | Solucao |
|------|---------------|---------|
| `ERROR: unable to restore to target, try a later target` | WAL nao cobre o timestamp | Usar timestamp mais antigo ou `--type=latest` |
| `REPO [2]: status: error (no valid backups)` | repo2 sem backup full | Executar `setup_pgbackrest_repo2.sh` primeiro |
| `could not connect to server: No such file or directory` | PostgreSQL nao iniciou apos restore | Verificar `pg_lsclusters`; iniciar manualmente |
| `ERROR: restore backup set not found` | Backup expirado ou repositorio sem full | Usar `pgbackrest info` para ver o que esta disponivel |
| `cipher mismatch` | `PGBACKREST_REPO2_CIPHER_PASS` errado | Confirmar a senha do cofre de segredos |
