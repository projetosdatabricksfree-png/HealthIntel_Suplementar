create table if not exists bruto_ans.igr_operadora_trimestral (
    trimestre varchar(6) not null,
    registro_ans varchar(6) not null,
    modalidade text not null,
    porte text,
    total_reclamacoes integer not null default 0,
    beneficiarios bigint not null default 0,
    igr numeric(12,4) not null,
    meta_igr numeric(12,4),
    atingiu_meta boolean not null default false,
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

create index if not exists ix_igr_trimestre_registro
    on bruto_ans.igr_operadora_trimestral (trimestre, registro_ans);

create index if not exists ix_igr_registro
    on bruto_ans.igr_operadora_trimestral (registro_ans, _carregado_em desc);

create table if not exists bruto_ans.nip_operadora_trimestral (
    trimestre varchar(6) not null,
    registro_ans varchar(6) not null,
    modalidade text not null,
    demandas_nip integer not null default 0,
    demandas_resolvidas integer not null default 0,
    beneficiarios bigint not null default 0,
    taxa_intermediacao_resolvida numeric(8,4),
    taxa_resolutividade numeric(8,4),
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

create index if not exists ix_nip_trimestre_registro
    on bruto_ans.nip_operadora_trimestral (trimestre, registro_ans);

create index if not exists ix_nip_registro
    on bruto_ans.nip_operadora_trimestral (registro_ans, _carregado_em desc);

create table if not exists bruto_ans.rn623_lista_operadora_trimestral (
    trimestre varchar(6) not null,
    registro_ans varchar(6) not null,
    modalidade text not null,
    tipo_lista text not null,
    total_nip integer,
    beneficiarios bigint,
    igr numeric(12,4),
    meta_igr numeric(12,4),
    elegivel boolean not null default true,
    observacao text,
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

create index if not exists ix_rn623_trimestre_tipo
    on bruto_ans.rn623_lista_operadora_trimestral (trimestre, tipo_lista, registro_ans);

create table if not exists plataforma.publicacao_regulatoria (
    id uuid primary key,
    dataset text not null,
    competencia varchar(6) not null,
    versao_publicacao text not null,
    titulo_publicacao text not null,
    fonte_oficial text not null,
    url_publicacao text not null,
    formato_publicacao text not null,
    publicado_em date,
    coletado_em timestamptz not null default now(),
    hash_publicacao text not null,
    status text not null,
    observacao text,
    unique (dataset, competencia, versao_publicacao)
);

create index if not exists ix_publicacao_regulatoria_dataset_competencia
    on plataforma.publicacao_regulatoria (dataset, competencia, publicado_em desc);
