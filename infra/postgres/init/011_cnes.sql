create table if not exists bruto_ans.cnes_estabelecimento (
    competencia           text not null,
    cnes                  text not null,
    cnpj                  text,
    razao_social          text,
    nome_fantasia         text,
    sg_uf                 char(2),
    cd_municipio          text,
    nm_municipio          text,
    tipo_unidade          text,
    tipo_unidade_desc     text,
    esfera_administrativa text,
    vinculo_sus           boolean,
    leitos_existentes     integer,
    leitos_sus            integer,
    latitude              numeric(10,6),
    longitude             numeric(10,6),
    situacao              text,
    fonte_publicacao      text,
    _carregado_em         timestamptz not null default now(),
    _arquivo_origem       text not null,
    _lote_id              uuid not null,
    _layout_id            text not null,
    _layout_versao_id     text not null,
    _hash_arquivo         text not null,
    _hash_estrutura       text not null,
    _status_parse         text not null default 'ok'
) partition by range (competencia);

create table if not exists bruto_ans.cnes_estabelecimento_default
    partition of bruto_ans.cnes_estabelecimento default;

create index if not exists ix_cnes_competencia_cnes
    on bruto_ans.cnes_estabelecimento (competencia, cnes);
create index if not exists ix_cnes_municipio
    on bruto_ans.cnes_estabelecimento (cd_municipio);
create index if not exists ix_cnes_uf_tipo
    on bruto_ans.cnes_estabelecimento (sg_uf, tipo_unidade);
