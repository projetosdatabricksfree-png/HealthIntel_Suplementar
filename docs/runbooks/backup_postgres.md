# Runbook — Backup e monitoramento pgBackRest (PostgreSQL)

## Objetivo

Diagnosticar e resolver falhas de backup, WAL archive e alertas operacionais do pgBackRest sem interromper o PostgreSQL.

## Passos de diagnóstico rápido

```bash
# 1. Status geral dos timers
systemctl list-timers pgbackrest-full.timer pgbackrest-diff.timer pgbackrest-monitor.timer

# 2. Logs dos últimos backups
journalctl -u pgbackrest-full.service -n 30
journalctl -u pgbackrest-diff.service -n 30
journalctl -u pgbackrest-monitor.service -n 30

# 3. Status do stanza e backups disponíveis
sudo -u postgres pgbackrest --stanza=healthintel info

# 4. Últimas execuções registradas
psql -U postgres -d healthintel -c "
  SELECT tipo, status, iniciado_em, duracao_segundos, bytes_armazenados, erro
  FROM plataforma.backup_execucao
  ORDER BY iniciado_em DESC LIMIT 10;"

# 5. Alertas ativos (últimas 2h)
psql -U postgres -d healthintel -c "
  SELECT check_tipo, severidade, mensagem, verificado_em
  FROM plataforma.backup_alerta
  WHERE verificado_em > now() - interval '2 hours'
  ORDER BY verificado_em DESC;"
```

## Falha de WAL archive

Sintoma: `journalctl -u pgbackrest-monitor.service` mostra `ALERTA wal_atraso`.

```bash
# Verificar estado do archiver
psql -U postgres -d healthintel -c "SELECT * FROM pg_stat_archiver;"

# Testar archive_command manualmente (substituir <wal-segment> pelo último arquivo em pg_wal)
ls /var/lib/postgresql/16/main/pg_wal/ | head -5

# Verificar conectividade com o repositório
sudo -u postgres pgbackrest --stanza=healthintel check

# Reiniciar archive_status corrompido (se last_failed_wal não limpar após correção)
psql -U postgres -d healthintel -c "SELECT pg_stat_reset_shared('archiver');"
```

## Falha de backup full

Sintoma: `journalctl -u pgbackrest-full.service` mostra erro ou `backup_execucao.status = 'falha'`.

```bash
# Ver erro completo do último full
psql -U postgres -d healthintel -c "
  SELECT erro, log_resumo FROM plataforma.backup_execucao
  WHERE tipo='full' ORDER BY iniciado_em DESC LIMIT 1;"

# Forçar backup full manual (aguarda conclusão, pode levar até 4h)
sudo systemctl start pgbackrest-full.service
# Ou diretamente:
sudo -u postgres pgbackrest --stanza=healthintel backup --type=full
```

## Falha de backup diff

Sintoma: `ALERTA diff_atraso` no monitor ou `status = 'falha'` em backup_execucao.

```bash
# Forçar diff manual
sudo systemctl start pgbackrest-diff.service
```

## pg_wal crescendo acima do limite

Sintoma: `ALERTA pg_wal_tamanho` no monitor.

```bash
# Ver tamanho atual
du -sh /var/lib/postgresql/16/main/pg_wal/

# Causa mais comum: archive_command falhando — WAL acumula enquanto archive não drena
# Verificar:
psql -U postgres -d healthintel -c "SELECT last_failed_wal, last_failed_time, failed_count FROM pg_stat_archiver;"

# Forçar checkpoint + archive dos WALs pendentes (após corrigir o archive_command):
psql -U postgres -d healthintel -c "CHECKPOINT;"
```

## Executar monitor manualmente

```bash
sudo -u postgres bash /opt/healthintel/scripts/backup/pgbackrest_monitor.sh
```

## Aplicar DDL de backup_alerta (primeira instalação ou rollback)

```bash
psql -U postgres -d healthintel -f infra/postgres/init/035_fase7_backup_alerta.sql
```

## Desativar monitoramento temporariamente

```bash
systemctl disable --now pgbackrest-monitor.timer
# Reativar:
systemctl enable --now pgbackrest-monitor.timer
```

## Critério de encerramento

- `systemctl list-timers` mostra os três timers com `NEXT` no futuro próximo.
- `pgbackrest --stanza=healthintel check` retorna exit 0.
- `plataforma.backup_alerta` sem novas linhas `critico` nas últimas 2h.
- `pg_stat_archiver.failed_count` estável (não cresce).
