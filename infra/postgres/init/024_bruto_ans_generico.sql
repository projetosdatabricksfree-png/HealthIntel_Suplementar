create table if not exists bruto_ans.ans_arquivo_generico (
    id bigserial primary key,
    dataset_codigo text not null,
    familia text not null,
    url text not null,
    arquivo_origem text not null,
    hash_arquivo text not null,
    caminho_landing text not null,
    tipo_arquivo text,
    tamanho_bytes bigint,
    status_parser text not null default 'sem_parser',
    data_ingestao timestamptz not null default now()
);

create index if not exists ans_arquivo_generico_dataset_idx
    on bruto_ans.ans_arquivo_generico (dataset_codigo);

create index if not exists ans_arquivo_generico_hash_idx
    on bruto_ans.ans_arquivo_generico (hash_arquivo);
