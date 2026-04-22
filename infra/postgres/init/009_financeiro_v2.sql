create table if not exists bruto_ans.vda_operadora_mensal (
    competencia varchar(6) not null,
    registro_ans varchar(6) not null,
    valor_devido numeric(18,4),
    valor_pago numeric(18,4),
    saldo_devedor numeric(18,4),
    situacao_cobranca text,
    data_vencimento date,
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

create table if not exists bruto_ans.vda_operadora_mensal_default
    partition of bruto_ans.vda_operadora_mensal default;

create index if not exists ix_vda_competencia_registro
    on bruto_ans.vda_operadora_mensal (competencia, registro_ans);

create index if not exists ix_vda_registro_competencia
    on bruto_ans.vda_operadora_mensal (registro_ans, competencia desc);

create table if not exists bruto_ans.glosa_operadora_mensal (
    competencia varchar(6) not null,
    registro_ans varchar(6) not null,
    tipo_glosa text not null,
    qt_glosa integer,
    valor_glosa numeric(18,4),
    valor_faturado numeric(18,4),
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

create table if not exists bruto_ans.glosa_operadora_mensal_default
    partition of bruto_ans.glosa_operadora_mensal default;

create index if not exists ix_glosa_competencia_registro
    on bruto_ans.glosa_operadora_mensal (competencia, registro_ans, tipo_glosa);

create index if not exists ix_glosa_registro_competencia
    on bruto_ans.glosa_operadora_mensal (registro_ans, competencia desc);

create table if not exists plataforma.publicacao_financeira_v2 (
    id bigserial primary key,
    dataset text not null,
    competencia varchar(6) not null,
    data_publicacao_ans date,
    data_carga timestamptz not null default now(),
    versao_publicacao text not null,
    hash_sha256 text not null,
    observacao text,
    unique (dataset, competencia, versao_publicacao)
);

create index if not exists ix_publicacao_financeira_v2_dataset_competencia
    on plataforma.publicacao_financeira_v2 (dataset, competencia, data_publicacao_ans desc);
