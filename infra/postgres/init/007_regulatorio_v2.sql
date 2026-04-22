create table if not exists bruto_ans.regime_especial_operadora_trimestral (
    trimestre varchar(6) not null,
    registro_ans varchar(6) not null,
    tipo_regime text not null,
    data_inicio date not null,
    data_fim date,
    descricao text,
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

create table if not exists bruto_ans.regime_especial_operadora_trimestral_default
    partition of bruto_ans.regime_especial_operadora_trimestral default;

create index if not exists ix_regime_especial_trimestre_registro
    on bruto_ans.regime_especial_operadora_trimestral (trimestre, registro_ans);

create index if not exists ix_regime_especial_registro
    on bruto_ans.regime_especial_operadora_trimestral (registro_ans, trimestre desc);

create table if not exists bruto_ans.prudencial_operadora_trimestral (
    trimestre varchar(6) not null,
    registro_ans varchar(6) not null,
    margem_solvencia numeric(18,4),
    capital_minimo_requerido numeric(18,4),
    capital_disponivel numeric(18,4),
    indice_liquidez numeric(18,4),
    situacao_prudencial text,
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

create table if not exists bruto_ans.prudencial_operadora_trimestral_default
    partition of bruto_ans.prudencial_operadora_trimestral default;

create index if not exists ix_prudencial_trimestre_registro
    on bruto_ans.prudencial_operadora_trimestral (trimestre, registro_ans);

create index if not exists ix_prudencial_registro
    on bruto_ans.prudencial_operadora_trimestral (registro_ans, trimestre desc);

create table if not exists bruto_ans.portabilidade_operadora_mensal (
    competencia varchar(6) not null,
    registro_ans varchar(6) not null,
    modalidade text,
    tipo_contratacao text,
    qt_portabilidade_entrada integer not null default 0,
    qt_portabilidade_saida integer not null default 0,
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

create table if not exists bruto_ans.portabilidade_operadora_mensal_default
    partition of bruto_ans.portabilidade_operadora_mensal default;

create index if not exists ix_portabilidade_competencia_registro
    on bruto_ans.portabilidade_operadora_mensal (competencia, registro_ans);

create index if not exists ix_portabilidade_registro
    on bruto_ans.portabilidade_operadora_mensal (registro_ans, competencia desc);

create table if not exists bruto_ans.taxa_resolutividade_operadora_trimestral (
    trimestre varchar(6) not null,
    registro_ans varchar(6) not null,
    modalidade text,
    taxa_resolutividade numeric(12,4),
    n_reclamacao_resolvida integer not null default 0,
    n_reclamacao_total integer not null default 0,
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

create table if not exists bruto_ans.taxa_resolutividade_operadora_trimestral_default
    partition of bruto_ans.taxa_resolutividade_operadora_trimestral default;

create index if not exists ix_taxa_resolutividade_trimestre_registro
    on bruto_ans.taxa_resolutividade_operadora_trimestral (trimestre, registro_ans);

create index if not exists ix_taxa_resolutividade_registro
    on bruto_ans.taxa_resolutividade_operadora_trimestral (registro_ans, trimestre desc);
