create table if not exists bruto_ans.rede_prestador_municipio (
    competencia integer not null,
    registro_ans varchar(6) not null,
    cd_municipio varchar(7) not null,
    nm_municipio text,
    sg_uf char(2),
    segmento text not null,
    tipo_prestador text,
    qt_prestador integer,
    qt_especialidade_disponivel integer,
    fonte_publicacao text,
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
) partition by range (competencia);

create table if not exists bruto_ans.rede_prestador_municipio_default
    partition of bruto_ans.rede_prestador_municipio default;

create index if not exists ix_rede_prestador_competencia
    on bruto_ans.rede_prestador_municipio (competencia, registro_ans, cd_municipio, segmento);

create table if not exists plataforma.publicacao_rede (
    dataset text not null,
    competencia text not null,
    data_publicacao_ans date not null,
    versao_publicacao text not null,
    hash_sha256 text not null,
    observacao text,
    criado_em timestamptz not null default now(),
    primary key (dataset, competencia, versao_publicacao)
);
