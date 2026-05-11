-- Sprint 41: Delta ANS 100% — SIP (Sistema de Informações de Produtos)
-- Fonte: /FTP/PDA/SIP/

create table if not exists bruto_ans.sip_mapa_assistencial (
    competencia integer,
    registro_ans varchar(6),
    cd_municipio varchar(7),
    nm_municipio text,
    sg_uf char(2),
    nm_regiao text,
    tipo_assistencial text,
    qt_beneficiarios integer,
    qt_eventos integer,
    indicador_cobertura numeric(10, 4),
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
);

create index if not exists ix_sip_mapa_assistencial_registro_ans
    on bruto_ans.sip_mapa_assistencial (registro_ans);
create index if not exists ix_sip_mapa_assistencial_competencia
    on bruto_ans.sip_mapa_assistencial (competencia, registro_ans);
create index if not exists ix_sip_mapa_assistencial_municipio
    on bruto_ans.sip_mapa_assistencial (cd_municipio);
