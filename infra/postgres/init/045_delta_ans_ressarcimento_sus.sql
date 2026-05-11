-- Sprint 41: Delta ANS 100% — Ressarcimento ao SUS
-- Subfamílias: ABI, operadora/plano, HC, cobrança/arrecadação,
--              índice de efetivo pagamento

create table if not exists bruto_ans.ressarcimento_beneficiario_abi (
    competencia integer,
    registro_ans varchar(6),
    nu_abi varchar(20),
    cd_municipio varchar(7),
    nm_municipio text,
    sg_uf char(2),
    qt_beneficiarios integer,
    vl_ressarcimento numeric(18, 2),
    status_ressarcimento text,
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
);

create index if not exists ix_ressarcimento_abi_registro_ans
    on bruto_ans.ressarcimento_beneficiario_abi (registro_ans);
create index if not exists ix_ressarcimento_abi_competencia
    on bruto_ans.ressarcimento_beneficiario_abi (competencia);

create table if not exists bruto_ans.ressarcimento_sus_operadora_plano (
    competencia integer,
    registro_ans varchar(6),
    codigo_plano varchar(20),
    qt_autorizacoes integer,
    vl_cobrado numeric(18, 2),
    vl_pago numeric(18, 2),
    vl_pendente numeric(18, 2),
    status_cobranca text,
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
);

create index if not exists ix_ressarcimento_sus_operadora_plano_registro_ans
    on bruto_ans.ressarcimento_sus_operadora_plano (registro_ans, competencia);

create table if not exists bruto_ans.ressarcimento_hc (
    competencia integer,
    registro_ans varchar(6),
    nu_hc varchar(20),
    vl_hc numeric(18, 2),
    status_hc text,
    fase_cobranca text,
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
);

create index if not exists ix_ressarcimento_hc_registro_ans
    on bruto_ans.ressarcimento_hc (registro_ans);
create index if not exists ix_ressarcimento_hc_competencia
    on bruto_ans.ressarcimento_hc (competencia);

create table if not exists bruto_ans.ressarcimento_cobranca_arrecadacao (
    competencia integer,
    registro_ans varchar(6),
    vl_cobrado numeric(18, 2),
    vl_arrecadado numeric(18, 2),
    vl_inadimplente numeric(18, 2),
    qt_guias integer,
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
);

create index if not exists ix_ressarcimento_cobranca_registro_ans
    on bruto_ans.ressarcimento_cobranca_arrecadacao (registro_ans, competencia);

create table if not exists bruto_ans.ressarcimento_indice_pagamento (
    competencia integer,
    registro_ans varchar(6),
    indice_efetivo_pagamento numeric(10, 4),
    valor_total_cobrado numeric(18, 2),
    valor_total_pago numeric(18, 2),
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
);

create index if not exists ix_ressarcimento_indice_registro_ans
    on bruto_ans.ressarcimento_indice_pagamento (registro_ans, competencia);
