-- Sprint 39 / HIS-39.1 — Tabela de auditoria de execuções pgBackRest
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
