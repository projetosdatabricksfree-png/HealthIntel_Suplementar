-- scripts/capacidade/snapshot_postgres.sql
-- Captura o tamanho do banco, schemas e tabelas

\echo '=== SNAPSHOT POSTGRESQL ==='

\echo '--- TAMANHO POR SCHEMA ---'
SELECT
    table_schema as schema_name,
    pg_size_pretty(sum(pg_total_relation_size(quote_ident(table_schema) || '.' || quote_ident(table_name)))) as tamanho_total
FROM information_schema.tables
WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
GROUP BY table_schema
ORDER BY sum(pg_total_relation_size(quote_ident(table_schema) || '.' || quote_ident(table_name))) DESC;

\echo ''
\echo '--- TOP 30 MAIORES TABELAS ---'
SELECT
    schemaname || '.' || relname as tabela,
    pg_size_pretty(pg_total_relation_size(relid)) as tamanho_total,
    n_live_tup as aprox_linhas
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(relid) DESC
LIMIT 30;

\echo ''
\echo '--- TOP 30 MAIORES ÍNDICES ---'
SELECT
    schemaname || '.' || indexrelname as indice,
    relname as tabela,
    pg_size_pretty(pg_relation_size(indexrelid)) as tamanho
FROM pg_stat_user_indexes
ORDER BY pg_relation_size(indexrelid) DESC
LIMIT 30;

\echo ''
\echo '--- STATUS POLÍTICA DATASET (vw_tamanho_dataset) ---'
SELECT * FROM plataforma.vw_tamanho_dataset;
