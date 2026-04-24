create extension if not exists pgcrypto;

create table if not exists plataforma.lote_ingestao (
    id uuid primary key default gen_random_uuid(),
    dataset text not null,
    competencia text,
    arquivo_origem text not null,
    hash_arquivo text not null,
    tamanho_bytes bigint,
    total_linhas_raw integer,
    total_aprovadas integer,
    total_quarentena integer,
    status text not null default 'iniciado',
    erro_mensagem text,
    iniciado_em timestamptz default now(),
    concluido_em timestamptz,
    dag_run_id text,
    versao_layout text,
    checksum_layout text,
    tentativa integer not null default 1,
    id_lote_original uuid references plataforma.lote_ingestao(id),
    origem_execucao text not null default 'airflow',
    constraint lote_ingestao_status_ck check (
        status in (
            'iniciado',
            'processando',
            'sucesso',
            'sucesso_com_alertas',
            'ignorado_duplicata',
            'erro'
        )
    )
);

create index if not exists lote_ingestao_dataset_competencia_idx
    on plataforma.lote_ingestao (dataset, competencia);

create index if not exists lote_ingestao_hash_arquivo_idx
    on plataforma.lote_ingestao (hash_arquivo);

create unique index if not exists lote_ingestao_hash_arquivo_sucesso_uq
    on plataforma.lote_ingestao (hash_arquivo)
    where status in ('sucesso', 'sucesso_com_alertas');
