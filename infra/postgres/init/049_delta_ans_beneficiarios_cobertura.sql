-- Sprint 41: Delta ANS 100% — Beneficiários e Cobertura Complementares
-- Subfamílias: beneficiários por região geográfica,
--              informações consolidadas de beneficiários,
--              taxa de cobertura de planos
-- Sem conflito com SIB existente

create table if not exists bruto_ans.beneficiario_regiao_geografica (
    competencia integer,
    cd_regiao varchar(2),
    nm_regiao text,
    sg_uf char(2),
    tipo_plano text,
    segmentacao text,
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

create index if not exists ix_beneficiario_regiao_geografica_competencia
    on bruto_ans.beneficiario_regiao_geografica (competencia, sg_uf);

create table if not exists bruto_ans.beneficiario_informacao_consolidada (
    competencia integer,
    sg_uf char(2),
    cd_municipio varchar(7),
    nm_municipio text,
    segmentacao text,
    tipo_contratacao text,
    faixa_etaria text,
    sexo char(1),
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

create index if not exists ix_beneficiario_info_consolidada_competencia
    on bruto_ans.beneficiario_informacao_consolidada (competencia, sg_uf);
create index if not exists ix_beneficiario_info_consolidada_municipio
    on bruto_ans.beneficiario_informacao_consolidada (cd_municipio);

create table if not exists bruto_ans.taxa_cobertura_plano (
    competencia integer,
    sg_uf char(2),
    cd_municipio varchar(7),
    nm_municipio text,
    populacao_total integer,
    qt_beneficiarios integer,
    taxa_cobertura numeric(10, 4),
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
);

create index if not exists ix_taxa_cobertura_plano_competencia
    on bruto_ans.taxa_cobertura_plano (competencia, sg_uf);
create index if not exists ix_taxa_cobertura_plano_municipio
    on bruto_ans.taxa_cobertura_plano (cd_municipio);
