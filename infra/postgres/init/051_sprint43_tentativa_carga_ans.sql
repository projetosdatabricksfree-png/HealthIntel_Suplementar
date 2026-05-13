-- Sprint 43 — auditoria granular de tentativa de carga ANS
--
-- Complementa plataforma.lote_ingestao (granularidade de lote) e
-- plataforma.arquivo_fonte_ans (granularidade de arquivo) com uma camada
-- por execução de task Airflow / por tentativa de carga individual.
--
-- Cada DAG/task registra início, eventos intermediários e final, inclusive
-- quando não há novos arquivos ou a fonte está indisponível — visando
-- responder "o que aconteceu na carga deste dataset hoje?" mesmo quando
-- não houve sucesso material.
--
-- Idempotente: pode ser reaplicada sem efeito colateral.

create extension if not exists pgcrypto;

create table if not exists plataforma.tentativa_carga_ans (
    id bigserial primary key,
    tentativa_id uuid not null default gen_random_uuid(),
    dag_id text,
    task_id text,
    run_id text,
    dominio text not null,
    dataset_codigo text not null,
    fonte_url text,
    arquivo_nome text,
    arquivo_hash text,
    competencia integer,
    periodo_inicio date,
    periodo_fim date,
    status text not null,
    motivo text,
    linhas_lidas bigint default 0,
    linhas_validas bigint default 0,
    linhas_invalidas bigint default 0,
    linhas_inseridas bigint default 0,
    linhas_atualizadas bigint default 0,
    linhas_ignoradas bigint default 0,
    tabela_destino text,
    erro_tipo text,
    erro_mensagem text,
    lote_ingestao_id uuid references plataforma.lote_ingestao(id) on delete set null,
    arquivo_fonte_ans_id uuid references plataforma.arquivo_fonte_ans(id) on delete set null,
    iniciado_em timestamptz not null default now(),
    finalizado_em timestamptz,
    duracao_ms bigint,
    created_at timestamptz not null default now(),
    constraint tentativa_carga_ans_status_ck check (
        status in (
            'INICIADO',
            'SEM_NOVOS_ARQUIVOS',
            'ARQUIVO_JA_CARREGADO',
            'BAIXADO',
            'VALIDADO',
            'CARREGADO',
            'CARREGADO_SEM_LINHAS',
            'CARREGADO_SEM_CHAVE',
            'IGNORADO_DUPLICATA',
            'FONTE_INDISPONIVEL',
            'LAYOUT_NAO_MAPEADO',
            'ERRO_DOWNLOAD',
            'ERRO_PARSE',
            'ERRO_VALIDACAO',
            'ERRO_CARGA',
            'ERRO_DBT',
            'FINALIZADO'
        )
    )
);

create index if not exists tentativa_carga_ans_dataset_idx
    on plataforma.tentativa_carga_ans (dataset_codigo, status, iniciado_em desc);

create index if not exists tentativa_carga_ans_dag_idx
    on plataforma.tentativa_carga_ans (dag_id, run_id, task_id);

create index if not exists tentativa_carga_ans_dominio_idx
    on plataforma.tentativa_carga_ans (dominio, iniciado_em desc);

create index if not exists tentativa_carga_ans_hash_idx
    on plataforma.tentativa_carga_ans (arquivo_hash)
    where arquivo_hash is not null;

create index if not exists tentativa_carga_ans_tentativa_id_idx
    on plataforma.tentativa_carga_ans (tentativa_id);

comment on table plataforma.tentativa_carga_ans is
    'Sprint 43 — auditoria granular por task Airflow. Toda tentativa de '
    'carga (mesmo sem novos arquivos) é registrada aqui. Complementa '
    'lote_ingestao (lote) e arquivo_fonte_ans (arquivo) via FK opcional.';

comment on column plataforma.tentativa_carga_ans.tentativa_id is
    'Identificador estável da tentativa; permite múltiplos eventos '
    '(INICIADO → VALIDADO → CARREGADO → FINALIZADO) com mesmo UUID.';

comment on column plataforma.tentativa_carga_ans.status is
    'Status do evento. Ver constraint tentativa_carga_ans_status_ck para '
    'lista completa. Status terminais conclusivos da Sprint 43: CARREGADO, '
    'SEM_NOVOS_ARQUIVOS, ARQUIVO_JA_CARREGADO, IGNORADO_DUPLICATA, '
    'FONTE_INDISPONIVEL, LAYOUT_NAO_MAPEADO, CARREGADO_SEM_LINHAS, '
    'CARREGADO_SEM_CHAVE, ERRO_* (família).';
