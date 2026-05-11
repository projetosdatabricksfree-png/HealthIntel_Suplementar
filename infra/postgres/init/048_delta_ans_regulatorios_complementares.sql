-- Sprint 41: Delta ANS 100% — Regulatórios Complementares
-- Subfamílias: penalidades, garantia atendimento, PEONA SUS, PROMOPREV,
--              RPC, IAP, PFA, programa de qualificação institucional
-- RPC: retenção 24 meses nas tabelas API/consumo

create table if not exists bruto_ans.penalidade_operadora (
    competencia integer,
    registro_ans varchar(6),
    nu_processo varchar(30),
    tipo_penalidade text,
    descricao_infracao text,
    vl_multa numeric(18, 2),
    data_penalidade date,
    status_penalidade text,
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
);

create index if not exists ix_penalidade_operadora_registro_ans
    on bruto_ans.penalidade_operadora (registro_ans);
create index if not exists ix_penalidade_operadora_competencia
    on bruto_ans.penalidade_operadora (competencia);

create table if not exists bruto_ans.monitoramento_garantia_atendimento (
    competencia integer,
    registro_ans varchar(6),
    tipo_garantia text,
    qt_ocorrencias integer,
    qt_resolvidas integer,
    qt_pendentes integer,
    prazo_medio_resolucao numeric(10, 2),
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
);

create index if not exists ix_garantia_atendimento_registro_ans
    on bruto_ans.monitoramento_garantia_atendimento (registro_ans, competencia);

create table if not exists bruto_ans.peona_sus (
    competencia integer,
    registro_ans varchar(6),
    vl_peona numeric(18, 2),
    qt_beneficiarios_sus integer,
    indicador_utilizacao_sus numeric(10, 4),
    sg_uf char(2),
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
);

create index if not exists ix_peona_sus_registro_ans
    on bruto_ans.peona_sus (registro_ans, competencia);

create table if not exists bruto_ans.promoprev (
    competencia integer,
    registro_ans varchar(6),
    tipo_programa text,
    qt_beneficiarios_programa integer,
    vl_investimento numeric(18, 2),
    indicador_participacao numeric(10, 4),
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
);

create index if not exists ix_promoprev_registro_ans
    on bruto_ans.promoprev (registro_ans, competencia);

create table if not exists bruto_ans.rpc (
    competencia integer not null,
    registro_ans varchar(6) not null,
    cd_municipio varchar(7),
    sg_uf char(2),
    tipo_reclamacao text,
    qt_reclamacoes integer,
    qt_resolvidas integer,
    indice_resolucao numeric(10, 4),
    nota_rpc numeric(5, 2),
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
) partition by range (competencia);

create table if not exists bruto_ans.rpc_default
    partition of bruto_ans.rpc default;

create index if not exists ix_rpc_competencia
    on bruto_ans.rpc (competencia, registro_ans);

create table if not exists bruto_ans.iap (
    competencia integer,
    registro_ans varchar(6),
    dimensao text,
    indicador text,
    valor_indicador numeric(10, 4),
    peso_indicador numeric(5, 2),
    pontuacao numeric(5, 2),
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
);

create index if not exists ix_iap_registro_ans
    on bruto_ans.iap (registro_ans, competencia);

create table if not exists bruto_ans.pfa (
    competencia integer,
    registro_ans varchar(6),
    indicador text,
    valor_indicador numeric(18, 4),
    meta numeric(18, 4),
    status_meta text,
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
);

create index if not exists ix_pfa_registro_ans
    on bruto_ans.pfa (registro_ans, competencia);

create table if not exists bruto_ans.programa_qualificacao_institucional (
    competencia integer,
    registro_ans varchar(6),
    nivel_qualificacao text,
    pontuacao_qualificacao numeric(5, 2),
    data_avaliacao date,
    status_qualificacao text,
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
);

create index if not exists ix_programa_qualificacao_registro_ans
    on bruto_ans.programa_qualificacao_institucional (registro_ans, competencia);
