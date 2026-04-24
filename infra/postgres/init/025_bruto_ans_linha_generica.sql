create table if not exists bruto_ans.ans_linha_generica (
    id bigserial primary key,
    dataset_codigo text not null,
    familia text not null,
    arquivo_origem text not null,
    hash_arquivo text not null,
    linha_origem integer not null,
    dados jsonb not null,
    data_ingestao timestamptz not null default now()
);

create index if not exists ans_linha_generica_dataset_idx
    on bruto_ans.ans_linha_generica (dataset_codigo);

create index if not exists ans_linha_generica_hash_idx
    on bruto_ans.ans_linha_generica (hash_arquivo);
