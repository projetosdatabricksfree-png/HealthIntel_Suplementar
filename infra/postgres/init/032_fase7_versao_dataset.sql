-- ================================================================
-- Fase 7 — Sprint 37: Última Versão Vigente para
-- TUSS, ROL, DE-PARA, Prestadores e QUALISS
-- ================================================================
-- Manifesto auditável de versão vigente por dataset de referência
-- ou cadastro vigente. Apenas uma linha vigente por dataset_codigo.
-- Histórico antigo NÃO entra na carga padrão da VPS; será tratado
-- pela Sprint 38 (histórico sob demanda).
--
-- ATENÇÃO — colisão de nomes resolvida:
-- A tabela `plataforma.versao_dataset` JÁ EXISTE no baseline
-- (`002_bronze_operacional.sql`) com schema diferente — é um log
-- per-carga genérico (campos `dataset`, `competencia`, `registros`,
-- `status`, sem `vigente`, sem FK). Renomear ou alterar essa tabela
-- viola a Regra-mãe da Fase 7. Por isso esta sprint cria um
-- artefato NOVO: `plataforma.versao_dataset_vigente`. Conceitualmente
-- é o "manifesto" da versão vigente; a tabela antiga continua sendo
-- o log per-carga e segue intacta.
--
-- Regras absolutas (Regra-mãe Fase 7):
-- - Nenhum modelo dbt, macro, DAG aprovada ou contrato de API alterado.
-- - Toda execução de carga registra URL, hash, versão, publicação,
--   carga e metadados.
-- - Idempotente. Pode ser reexecutado sem efeitos colaterais.
-- ================================================================

create table if not exists plataforma.versao_dataset_vigente (
    id bigserial primary key,
    dataset_codigo text not null references plataforma.politica_dataset(dataset_codigo),
    versao text not null,
    url_fonte text not null,
    hash_arquivo text not null,
    publicado_em date,
    carregado_em timestamptz not null default now(),
    arquivo_bytes bigint,
    metadados jsonb,
    vigente boolean not null default true
);

-- Índice único parcial: garante apenas uma linha vigente por dataset.
create unique index if not exists ux_versao_dataset_vigente_dataset
    on plataforma.versao_dataset_vigente (dataset_codigo)
    where vigente = true;

-- Índices auxiliares de consulta.
create index if not exists ix_versao_dataset_vigente_lookup
    on plataforma.versao_dataset_vigente (dataset_codigo, carregado_em desc);

create index if not exists ix_versao_dataset_vigente_hash
    on plataforma.versao_dataset_vigente (dataset_codigo, hash_arquivo);

-- View agregada: versão vigente por dataset, com tempo desde a carga.
create or replace view plataforma.vw_versao_vigente as
select
    pd.dataset_codigo,
    pd.classe_dataset,
    pd.estrategia_carga,
    pd.carregar_apenas_ultima_versao,
    vd.versao,
    vd.publicado_em,
    vd.carregado_em,
    vd.url_fonte,
    vd.hash_arquivo,
    vd.arquivo_bytes,
    vd.metadados,
    extract(epoch from (now() - vd.carregado_em))::bigint as segundos_desde_carga
from plataforma.politica_dataset pd
left join plataforma.versao_dataset_vigente vd
    on vd.dataset_codigo = pd.dataset_codigo
   and vd.vigente = true
where pd.ativo = true
  and pd.classe_dataset in ('referencia_versionada', 'snapshot_atual');

comment on table plataforma.versao_dataset_vigente is
'Manifesto de versão vigente por dataset de referência ou cadastro vigente. '
'Apenas uma versão vigente por dataset_codigo (garantido por unique index parcial). '
'Histórico antigo não é carga padrão da VPS; será tratado como histórico sob demanda na Sprint 38. '
'NÃO confundir com `plataforma.versao_dataset` (baseline 002), que é log per-carga genérico.';

comment on column plataforma.versao_dataset_vigente.dataset_codigo is
'Chave para plataforma.politica_dataset. Determina classe e estratégia de carga.';

comment on column plataforma.versao_dataset_vigente.versao is
'Identificador da versão publicada (ex.: ano-mês, número de release ANS, vigência).';

comment on column plataforma.versao_dataset_vigente.url_fonte is
'URL ou caminho de origem do arquivo carregado.';

comment on column plataforma.versao_dataset_vigente.hash_arquivo is
'Hash criptográfico (sha256 padrão) do arquivo carregado. Usado para idempotência.';

comment on column plataforma.versao_dataset_vigente.publicado_em is
'Data de publicação oficial pela ANS, quando informada na fonte.';

comment on column plataforma.versao_dataset_vigente.carregado_em is
'Timestamp da carga local na VPS.';

comment on column plataforma.versao_dataset_vigente.arquivo_bytes is
'Tamanho do arquivo de origem em bytes, quando aplicável.';

comment on column plataforma.versao_dataset_vigente.metadados is
'Metadados livres em JSON (cabeçalhos, layout, observações operacionais).';

comment on column plataforma.versao_dataset_vigente.vigente is
'true indica a versão vigente usada na carga padrão. '
'Unique index parcial impede duas versões vigentes simultâneas por dataset.';

comment on view plataforma.vw_versao_vigente is
'Resumo da versão vigente por dataset de referência ou cadastro vigente. '
'Não exposta em FastAPI nem em consumo_*; uso interno apenas.';

-- ================================================================
-- Tabelas Bronze versionadas — carga real da Sprint 37
-- ================================================================
-- Estas tabelas são o ponto de integração dos fluxos reais de carga
-- vigente. Elas mantêm apenas a versão vigente por padrão, controlada
-- por `plataforma.versao_dataset_vigente` e pelo helper Python
-- `ingestao.app.carga_versao_vigente`.
--
-- O desenho preserva Bronze como espelho técnico: campos canônicos
-- mínimos para uso operacional + payload original em `dados`.
-- ================================================================

create table if not exists bruto_ans.tuss_procedimento (
    id bigserial primary key,
    codigo_procedimento text not null,
    descricao text,
    grupo text,
    subgrupo text,
    capitulo text,
    versao_dataset text not null,
    url_fonte text not null,
    hash_arquivo text not null,
    arquivo_origem text not null,
    linha_origem integer not null,
    dados jsonb not null default '{}'::jsonb,
    carregado_em timestamptz not null default now()
);

create unique index if not exists ux_tuss_procedimento_codigo_versao
    on bruto_ans.tuss_procedimento (codigo_procedimento, versao_dataset);

create index if not exists ix_tuss_procedimento_versao
    on bruto_ans.tuss_procedimento (versao_dataset);

create table if not exists bruto_ans.rol_procedimento (
    id bigserial primary key,
    codigo_procedimento text not null,
    descricao text,
    segmento text,
    obrigatorio_medico text,
    obrigatorio_odonto text,
    versao_dataset text not null,
    url_fonte text not null,
    hash_arquivo text not null,
    arquivo_origem text not null,
    linha_origem integer not null,
    dados jsonb not null default '{}'::jsonb,
    carregado_em timestamptz not null default now()
);

create unique index if not exists ux_rol_procedimento_codigo_versao
    on bruto_ans.rol_procedimento (codigo_procedimento, versao_dataset);

create index if not exists ix_rol_procedimento_versao
    on bruto_ans.rol_procedimento (versao_dataset);

create table if not exists bruto_ans.depara_sip_tuss (
    id bigserial primary key,
    codigo_procedimento_tuss text not null,
    codigo_procedimento_sip text not null,
    descricao text,
    versao_dataset text not null,
    url_fonte text not null,
    hash_arquivo text not null,
    arquivo_origem text not null,
    linha_origem integer not null,
    dados jsonb not null default '{}'::jsonb,
    carregado_em timestamptz not null default now()
);

create unique index if not exists ux_depara_sip_tuss_codigo_versao
    on bruto_ans.depara_sip_tuss (
        codigo_procedimento_tuss,
        codigo_procedimento_sip,
        versao_dataset
    );

create index if not exists ix_depara_sip_tuss_versao
    on bruto_ans.depara_sip_tuss (versao_dataset);

create table if not exists bruto_ans.prestador_cadastral (
    id bigserial primary key,
    codigo_prestador text not null,
    cnes text,
    cnpj text,
    razao_social text,
    nome_fantasia text,
    sg_uf text,
    cd_municipio text,
    versao_dataset text not null,
    url_fonte text not null,
    hash_arquivo text not null,
    arquivo_origem text not null,
    linha_origem integer not null,
    dados jsonb not null default '{}'::jsonb,
    carregado_em timestamptz not null default now()
);

create unique index if not exists ux_prestador_cadastral_codigo_versao
    on bruto_ans.prestador_cadastral (codigo_prestador, versao_dataset);

create index if not exists ix_prestador_cadastral_versao
    on bruto_ans.prestador_cadastral (versao_dataset);

create table if not exists bruto_ans.prestador_cadastral_snapshot_anterior
    (like bruto_ans.prestador_cadastral including defaults);

create index if not exists ix_prestador_cadastral_snapshot_anterior_versao
    on bruto_ans.prestador_cadastral_snapshot_anterior (versao_dataset);

create table if not exists bruto_ans.qualiss (
    id bigserial primary key,
    identificador_qualiss text not null,
    codigo_prestador text,
    cnes text,
    cnpj text,
    atributo_qualidade text,
    resultado text,
    versao_dataset text not null,
    url_fonte text not null,
    hash_arquivo text not null,
    arquivo_origem text not null,
    linha_origem integer not null,
    dados jsonb not null default '{}'::jsonb,
    carregado_em timestamptz not null default now()
);

create unique index if not exists ux_qualiss_identificador_versao
    on bruto_ans.qualiss (identificador_qualiss, versao_dataset);

create index if not exists ix_qualiss_versao
    on bruto_ans.qualiss (versao_dataset);

create table if not exists bruto_ans.qualiss_snapshot_anterior
    (like bruto_ans.qualiss including defaults);

create index if not exists ix_qualiss_snapshot_anterior_versao
    on bruto_ans.qualiss_snapshot_anterior (versao_dataset);

comment on table bruto_ans.tuss_procedimento is
'Bronze da TUSS de procedimentos carregada apenas na versão vigente por padrão.';

comment on table bruto_ans.rol_procedimento is
'Bronze do ROL de procedimentos carregado apenas na versão vigente por padrão.';

comment on table bruto_ans.depara_sip_tuss is
'Bronze do DE-PARA SIP/TUSS carregado apenas na versão vigente por padrão.';

comment on table bruto_ans.prestador_cadastral is
'Bronze do snapshot atual de prestadores cadastrais; histórico padrão não é materializado.';

comment on table bruto_ans.qualiss is
'Bronze do snapshot atual QUALISS; histórico padrão não é materializado.';
