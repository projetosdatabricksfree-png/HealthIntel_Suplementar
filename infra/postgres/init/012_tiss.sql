create table if not exists bruto_ans.tiss_procedimento_trimestral (
    trimestre                   text not null,
    registro_ans                text not null,
    sg_uf                       char(2),
    grupo_procedimento          text,
    grupo_desc                  text,
    subgrupo_procedimento       text,
    qt_procedimentos            bigint,
    qt_beneficiarios_distintos  bigint,
    valor_total                 numeric(18,2),
    modalidade                  text,
    tipo_contratacao            text,
    fonte_publicacao            text,
    _carregado_em               timestamptz not null default now(),
    _arquivo_origem             text not null,
    _lote_id                    uuid not null,
    _layout_id                  text not null,
    _layout_versao_id           text not null,
    _hash_arquivo               text not null,
    _hash_estrutura             text not null,
    _status_parse               text not null default 'ok'
) partition by range (trimestre);

create table if not exists bruto_ans.tiss_procedimento_trimestral_default
    partition of bruto_ans.tiss_procedimento_trimestral default;

create index if not exists ix_tiss_trimestre_registro
    on bruto_ans.tiss_procedimento_trimestral (trimestre, registro_ans);
create index if not exists ix_tiss_grupo
    on bruto_ans.tiss_procedimento_trimestral (grupo_procedimento);
create index if not exists ix_tiss_uf
    on bruto_ans.tiss_procedimento_trimestral (sg_uf);
