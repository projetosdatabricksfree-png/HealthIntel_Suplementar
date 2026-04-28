-- ================================================================
-- Fase 7 — Sprint 36: Janela Dinâmica de Carga na Ingestão
-- ================================================================
-- Auditoria operacional das decisões de janela de carga.
-- Idempotente e restrito ao schema plataforma.
-- ================================================================

create table if not exists plataforma.ingestao_janela_decisao (
    id bigserial primary key,
    dataset_codigo text not null references plataforma.politica_dataset(dataset_codigo),
    competencia integer not null,
    acao text not null
        check (
            acao in (
                'carregado',
                'ignorado_fora_janela',
                'rejeitado_historico_sem_flag',
                'ignorado_versao_antiga'
            )
        ),
    motivo text,
    janela_minima integer,
    janela_maxima_exclusiva integer,
    decidido_em timestamptz not null default now(),
    decidido_por text not null default current_user
);

create index if not exists ix_ingestao_janela_decisao_dataset_data
    on plataforma.ingestao_janela_decisao (dataset_codigo, decidido_em desc);

create index if not exists ix_ingestao_janela_decisao_acao
    on plataforma.ingestao_janela_decisao (acao);

create index if not exists ix_ingestao_janela_decisao_dataset_competencia
    on plataforma.ingestao_janela_decisao (dataset_codigo, competencia);

create or replace view plataforma.vw_ingestao_janela_resumo as
select
    dataset_codigo,
    acao,
    count(*)::bigint as quantidade,
    min(decidido_em) as primeira_decisao,
    max(decidido_em) as ultima_decisao,
    min(janela_minima) as menor_janela_minima,
    max(janela_maxima_exclusiva) as maior_janela_maxima_exclusiva
from plataforma.ingestao_janela_decisao
group by dataset_codigo, acao;

comment on table plataforma.ingestao_janela_decisao is
'Auditoria operacional de decisões de janela de carga. Não apagar registros. Histórico fora da janela padrão só deve ser carregado pela Sprint 38 com entitlement.';

comment on column plataforma.ingestao_janela_decisao.acao is
'carregado, ignorado_fora_janela, rejeitado_historico_sem_flag ou ignorado_versao_antiga.';
