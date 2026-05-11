-- Sprint 41: Delta ANS 100% — Precificação, NTRP e Reajustes
-- Subfamílias: área comercialização NTRP, painel precificação,
--              percentuais reajuste, NTRP/VCM/faixa etária,
--              valor comercial médio por município, faixa de preço

create table if not exists bruto_ans.ntrp_area_comercializacao (
    competencia integer,
    registro_ans varchar(6),
    codigo_plano varchar(20),
    cd_municipio varchar(7),
    nm_municipio text,
    sg_uf char(2),
    area_comercializacao text,
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
);

create index if not exists ix_ntrp_area_comercializacao_registro_ans
    on bruto_ans.ntrp_area_comercializacao (registro_ans);
create index if not exists ix_ntrp_area_comercializacao_municipio
    on bruto_ans.ntrp_area_comercializacao (cd_municipio);

create table if not exists bruto_ans.painel_precificacao (
    competencia integer,
    registro_ans varchar(6),
    codigo_plano varchar(20),
    segmentacao text,
    faixa_etaria text,
    sg_uf char(2),
    tipo_contratacao text,
    vl_mensalidade_media numeric(18, 2),
    vl_mensalidade_min numeric(18, 2),
    vl_mensalidade_max numeric(18, 2),
    qt_beneficiarios integer,
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
);

create index if not exists ix_painel_precificacao_registro_ans
    on bruto_ans.painel_precificacao (registro_ans, competencia);
create index if not exists ix_painel_precificacao_uf
    on bruto_ans.painel_precificacao (sg_uf, segmentacao);

create table if not exists bruto_ans.percentual_reajuste_agrupamento (
    competencia integer,
    registro_ans varchar(6),
    tipo_contratacao text,
    agrupamento text,
    percentual_reajuste numeric(10, 4),
    data_aplicacao date,
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
);

create index if not exists ix_percentual_reajuste_registro_ans
    on bruto_ans.percentual_reajuste_agrupamento (registro_ans, competencia);

create table if not exists bruto_ans.ntrp_vcm_faixa_etaria (
    competencia integer,
    registro_ans varchar(6),
    codigo_plano varchar(20),
    faixa_etaria text,
    sg_uf char(2),
    vcm numeric(18, 2),
    vl_minimo numeric(18, 2),
    vl_maximo numeric(18, 2),
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
);

create index if not exists ix_ntrp_vcm_faixa_etaria_registro_ans
    on bruto_ans.ntrp_vcm_faixa_etaria (registro_ans, competencia);

create table if not exists bruto_ans.valor_comercial_medio_municipio (
    competencia integer,
    cd_municipio varchar(7),
    nm_municipio text,
    sg_uf char(2),
    segmentacao text,
    faixa_etaria text,
    vcm_municipio numeric(18, 2),
    qt_planos integer,
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
);

create index if not exists ix_vcm_municipio_cd
    on bruto_ans.valor_comercial_medio_municipio (cd_municipio, competencia);

create table if not exists bruto_ans.faixa_preco (
    competencia integer,
    registro_ans varchar(6),
    codigo_plano varchar(20),
    faixa_etaria text,
    sg_uf char(2),
    vl_faixa_min numeric(18, 2),
    vl_faixa_max numeric(18, 2),
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
);

create index if not exists ix_faixa_preco_registro_ans
    on bruto_ans.faixa_preco (registro_ans, competencia);
