-- Sprint 39 / HIS-39.6 — Tabela de alertas operacionais de backup
--
-- Registra falhas detectadas pelo script pgbackrest_monitor.sh (HIS-39.6).
-- Cada linha representa um check com falha identificada em uma execução do monitor.
-- Não há relação de FK com backup_execucao — alertas são registros independentes.
--
-- APLICAÇÃO:
--   psql -U postgres -d healthintel -f infra/postgres/init/035_fase7_backup_alerta.sql
--
-- CONSULTAS ÚTEIS:
--   -- Alertas das últimas 24h por tipo:
--   SELECT check_tipo, severidade, mensagem, verificado_em
--   FROM plataforma.backup_alerta
--   WHERE verificado_em > now() - interval '24 hours'
--   ORDER BY verificado_em DESC;
--
--   -- Frequência de alertas por tipo (última semana):
--   SELECT check_tipo, severidade, COUNT(*) AS total
--   FROM plataforma.backup_alerta
--   WHERE verificado_em > now() - interval '7 days'
--   GROUP BY check_tipo, severidade ORDER BY total DESC;

CREATE TABLE IF NOT EXISTS plataforma.backup_alerta (
    id           bigserial    PRIMARY KEY,
    verificado_em timestamptz NOT NULL DEFAULT now(),
    check_tipo   text         NOT NULL CHECK (check_tipo IN (
                                  'wal_atraso',
                                  'full_atraso',
                                  'diff_atraso',
                                  'pg_wal_tamanho'
                              )),
    severidade   text         NOT NULL CHECK (severidade IN ('aviso', 'critico')),
    mensagem     text         NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_backup_alerta_lookup
    ON plataforma.backup_alerta (check_tipo, verificado_em DESC);

COMMENT ON TABLE plataforma.backup_alerta IS
    'Sprint 39 / HIS-39.6 — Alertas operacionais de backup pgBackRest registrados pelo pgbackrest_monitor.sh';

COMMENT ON COLUMN plataforma.backup_alerta.check_tipo IS
    'Tipo do check: wal_atraso | full_atraso | diff_atraso | pg_wal_tamanho';

COMMENT ON COLUMN plataforma.backup_alerta.severidade IS
    'aviso = alerta informativo; critico = requer ação imediata';
