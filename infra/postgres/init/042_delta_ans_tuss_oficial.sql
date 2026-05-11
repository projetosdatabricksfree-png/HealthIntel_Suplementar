-- Sprint 41: Delta ANS 100% — TUSS Oficial
-- Fonte: /FTP/PDA/terminologia_unificada_saude_suplementar_TUSS/TUSS.zip
-- Separado do stg_tuss_terminologia existente (crosswalk sintético)

create table if not exists bruto_ans.tuss_terminologia_oficial (
    codigo_tuss varchar(20) not null,
    descricao text not null,
    versao_tuss varchar(20),
    vigencia_inicio date,
    vigencia_fim date,
    is_tuss_vigente boolean not null default false,
    grupo text,
    subgrupo text,
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
);

create index if not exists ix_tuss_oficial_codigo_tuss
    on bruto_ans.tuss_terminologia_oficial (codigo_tuss);
create index if not exists ix_tuss_oficial_codigo_versao
    on bruto_ans.tuss_terminologia_oficial (codigo_tuss, versao_tuss);
create index if not exists ix_tuss_oficial_vigente
    on bruto_ans.tuss_terminologia_oficial (is_tuss_vigente);
