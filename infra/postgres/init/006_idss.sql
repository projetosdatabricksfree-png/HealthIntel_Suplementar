create table if not exists bruto_ans.idss (
    ano_base integer not null,
    registro_ans varchar(6) not null,
    idss_total numeric(6,4) not null,
    idqs numeric(6,4) not null,
    idga numeric(6,4) not null,
    idsm numeric(6,4) not null,
    idgr numeric(6,4) not null,
    faixa_idss text,
    fonte_publicacao text,
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
);

create index if not exists ix_idss_ano_base_registro
    on bruto_ans.idss (ano_base, registro_ans);

create index if not exists ix_idss_registro
    on bruto_ans.idss (registro_ans, ano_base desc);

alter table if exists plataforma.versao_dataset
    add column if not exists hash_sha256 text;

-- sem unique index em (dataset, competencia): tabela é append-only (log de versões)
