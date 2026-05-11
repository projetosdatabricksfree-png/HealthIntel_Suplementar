-- Sprint 41: Delta ANS 100% — TISS Subfamílias Oficiais
-- Fontes: /FTP/PDA/TISS/AMBULATORIAL/, /HOSPITALAR/, /DADOS_DE_PLANOS/
-- Retenção nas tabelas API/consumo: 24 meses (histórico completo em R2)

create table if not exists bruto_ans.tiss_ambulatorial (
    competencia integer not null,
    registro_ans varchar(6) not null,
    cd_municipio varchar(7),
    nm_municipio text,
    sg_uf char(2),
    tipo_evento text,
    qt_eventos integer,
    vl_pago numeric(18, 2),
    vl_informado numeric(18, 2),
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
) partition by range (competencia);

create table if not exists bruto_ans.tiss_ambulatorial_default
    partition of bruto_ans.tiss_ambulatorial default;

create index if not exists ix_tiss_ambulatorial_competencia
    on bruto_ans.tiss_ambulatorial (competencia, registro_ans);

create table if not exists bruto_ans.tiss_hospitalar (
    competencia integer not null,
    registro_ans varchar(6) not null,
    cd_municipio varchar(7),
    nm_municipio text,
    sg_uf char(2),
    tipo_evento text,
    qt_internacoes integer,
    qt_diarias integer,
    vl_pago numeric(18, 2),
    vl_informado numeric(18, 2),
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
) partition by range (competencia);

create table if not exists bruto_ans.tiss_hospitalar_default
    partition of bruto_ans.tiss_hospitalar default;

create index if not exists ix_tiss_hospitalar_competencia
    on bruto_ans.tiss_hospitalar (competencia, registro_ans);

create table if not exists bruto_ans.tiss_dados_plano (
    competencia integer not null,
    registro_ans varchar(6) not null,
    codigo_plano varchar(20),
    segmentacao text,
    tipo_contratacao text,
    qt_beneficiarios integer,
    qt_eventos integer,
    vl_pago numeric(18, 2),
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
) partition by range (competencia);

create table if not exists bruto_ans.tiss_dados_plano_default
    partition of bruto_ans.tiss_dados_plano default;

create index if not exists ix_tiss_dados_plano_competencia
    on bruto_ans.tiss_dados_plano (competencia, registro_ans);
