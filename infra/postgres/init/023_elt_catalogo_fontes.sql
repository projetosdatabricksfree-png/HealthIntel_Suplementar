create extension if not exists pgcrypto;

create table if not exists plataforma.fonte_dado_ans (
    id bigserial primary key,
    dataset_codigo text not null,
    familia text not null,
    url text not null unique,
    diretorio_origem text,
    nome_arquivo text,
    extensao text,
    tipo_arquivo text,
    tamanho_bytes bigint,
    last_modified timestamptz,
    ativo boolean not null default true,
    prioridade integer not null default 100,
    escopo text not null default 'sector_core',
    status_catalogacao text not null default 'descoberto',
    descoberto_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now()
);

create table if not exists plataforma.arquivo_fonte_ans (
    id uuid primary key default gen_random_uuid(),
    fonte_id bigint references plataforma.fonte_dado_ans(id),
    dataset_codigo text not null,
    familia text not null,
    url text not null,
    caminho_landing text,
    nome_arquivo text,
    hash_arquivo text,
    tamanho_bytes bigint,
    last_modified_origem timestamptz,
    baixado_em timestamptz,
    status text not null default 'pendente',
    erro_mensagem text,
    tentativa integer not null default 0,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint arquivo_fonte_ans_status_ck check (
        status in (
            'pendente',
            'baixando',
            'baixado',
            'baixado_sem_parser',
            'carregado',
            'ignorado_duplicata',
            'erro_download',
            'erro_parser',
            'erro_carga'
        )
    )
);

create index if not exists fonte_dado_ans_familia_idx
    on plataforma.fonte_dado_ans (familia);

create index if not exists fonte_dado_ans_dataset_idx
    on plataforma.fonte_dado_ans (dataset_codigo);

create index if not exists arquivo_fonte_ans_hash_idx
    on plataforma.arquivo_fonte_ans (hash_arquivo);

create unique index if not exists arquivo_fonte_ans_hash_baixado_uq
    on plataforma.arquivo_fonte_ans (hash_arquivo)
    where status in ('baixado', 'carregado', 'baixado_sem_parser');
