create table if not exists bruto_ans.diops_operadora_trimestral (
    trimestre varchar(6) not null,
    registro_ans varchar(6) not null,
    cnpj varchar(14) not null,
    ativo_total numeric(18,4),
    passivo_total numeric(18,4),
    patrimonio_liquido numeric(18,4),
    receita_total numeric(18,4),
    despesa_total numeric(18,4),
    resultado_periodo numeric(18,4),
    provisao_tecnica numeric(18,4),
    margem_solvencia_calculada numeric(18,4),
    fonte_publicacao text,
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
) partition by range (trimestre);

create table if not exists bruto_ans.diops_operadora_trimestral_default
    partition of bruto_ans.diops_operadora_trimestral default;

create index if not exists ix_diops_trimestre_registro
    on bruto_ans.diops_operadora_trimestral (trimestre, registro_ans);

create index if not exists ix_diops_registro
    on bruto_ans.diops_operadora_trimestral (registro_ans, trimestre desc);

create table if not exists bruto_ans.fip_operadora_trimestral (
    trimestre varchar(6) not null,
    registro_ans varchar(6) not null,
    modalidade text,
    tipo_contratacao text,
    sinistro_total numeric(18,4),
    contraprestacao_total numeric(18,4),
    sinistralidade_bruta numeric(12,4),
    ressarcimento_sus numeric(18,4),
    evento_indenizavel numeric(18,4),
    fonte_publicacao text,
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
) partition by range (trimestre);

create table if not exists bruto_ans.fip_operadora_trimestral_default
    partition of bruto_ans.fip_operadora_trimestral default;

create index if not exists ix_fip_trimestre_registro
    on bruto_ans.fip_operadora_trimestral (trimestre, registro_ans);

create index if not exists ix_fip_registro
    on bruto_ans.fip_operadora_trimestral (registro_ans, trimestre desc);

create table if not exists plataforma.publicacao_financeira (
    id bigserial primary key,
    dataset text not null,
    trimestre varchar(6) not null,
    data_publicacao_ans date,
    data_carga timestamptz not null default now(),
    versao_publicacao text not null,
    hash_sha256 text not null,
    observacao text,
    unique (dataset, trimestre, versao_publicacao)
);

create index if not exists ix_publicacao_financeira_dataset_trimestre
    on plataforma.publicacao_financeira (dataset, trimestre, data_publicacao_ans desc);
