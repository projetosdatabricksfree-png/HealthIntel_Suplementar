-- ================================================================
-- Fase 7 — Sprint 34: Política Dinâmica de Carga por Dataset
-- ================================================================
-- Este script cria a governança declarativa de carga no schema
-- plataforma. Nenhum modelo dbt, DAG ou API do baseline é alterado.
-- ================================================================

-- 1. Tabela principal: plataforma.politica_dataset
create table if not exists plataforma.politica_dataset (
    dataset_codigo text primary key,
    descricao text not null,
    classe_dataset text not null
        check (classe_dataset in ('grande_temporal','pequena_full_ate_5gb','referencia_versionada','snapshot_atual','historico_sob_demanda')),
    estrategia_carga text not null
        check (estrategia_carga in ('ano_vigente_mais_ano_anterior','full_ate_5gb','ultima_versao_vigente','snapshot_atual','historico_sob_demanda')),
    schema_destino text not null,
    tabela_destino text not null,
    coluna_competencia text,
    anos_carga_hot integer,
    limite_full_gb numeric(10,2),
    particionar_por_ano boolean not null default false,
    carregar_apenas_ultima_versao boolean not null default false,
    historico_sob_demanda boolean not null default true,
    ativo boolean not null default true,
    criado_em timestamptz not null default now(),
    atualizado_em timestamptz not null default now()
);

-- Índice por classe_dataset para consultas de política
create index if not exists ix_politica_dataset_classe
    on plataforma.politica_dataset (classe_dataset);

-- Índice por ativo para consultas de datasets ativos
create index if not exists ix_politica_dataset_ativo
    on plataforma.politica_dataset (ativo)
    where ativo = true;

-- Trigger para atualizar atualizado_em automaticamente
create or replace function plataforma.trgr_politica_dataset_atualizado_em()
returns trigger as $$
begin
    new.atualizado_em = now();
    return new;
end;
$$ language plpgsql;

drop trigger if exists trg_politica_dataset_atualizado_em on plataforma.politica_dataset;
create trigger trg_politica_dataset_atualizado_em
    before update on plataforma.politica_dataset
    for each row
    execute function plataforma.trgr_politica_dataset_atualizado_em();


-- 2. View de monitoramento de tamanho de dataset
create or replace view plataforma.vw_tamanho_dataset as
select
    pd.dataset_codigo,
    pd.descricao,
    pd.classe_dataset,
    pd.schema_destino,
    pd.tabela_destino,
    pd.limite_full_gb,
    coalesce(
        (
            select pg_total_relation_size(to_regclass(format('%I.%I', pd.schema_destino, pd.tabela_destino)))::numeric / 1e9
        ),
        0
    )::numeric(12,4) as tamanho_gb,
    case
        when pd.classe_dataset = 'pequena_full_ate_5gb'
             and coalesce(
                 (
                     select pg_total_relation_size(to_regclass(format('%I.%I', pd.schema_destino, pd.tabela_destino)))::numeric / 1e9
                 ),
                 0
             ) > pd.limite_full_gb
        then true
        else false
    end as acima_do_limite
from plataforma.politica_dataset pd
where pd.ativo = true;


-- 3. Tabela de recomendações de reclassificação
create table if not exists plataforma.reclassificacao_dataset_pendente (
    id bigserial primary key,
    dataset_codigo text not null references plataforma.politica_dataset(dataset_codigo),
    tamanho_gb numeric(12,4) not null,
    limite_full_gb numeric(10,2) not null,
    classe_atual text not null,
    classe_sugerida text not null
        check (classe_sugerida in ('grande_temporal','snapshot_atual','referencia_versionada','historico_sob_demanda')),
    motivo text not null,
    detectado_em timestamptz not null default now(),
    status text not null default 'pendente'
        check (status in ('pendente','aprovada','rejeitada','em_analise')),
    aprovado_em timestamptz,
    aprovado_por text,
    constraint ck_reclassificacao_classe_diferente
        check (classe_atual <> classe_sugerida)
);

create index if not exists ix_reclassificacao_pendente_status
    on plataforma.reclassificacao_dataset_pendente (status)
    where status in ('pendente','em_analise');

create unique index if not exists ux_reclassificacao_dataset_aberta
    on plataforma.reclassificacao_dataset_pendente (dataset_codigo)
    where status in ('pendente','em_analise','aprovada');


-- 4. Função auxiliar para calcular tamanho de tabela de um dataset
create or replace function plataforma.calcular_tamanho_tabela_dataset(p_dataset_codigo text)
returns numeric(12,4)
language plpgsql stable
as $$
declare
    v_schema text;
    v_tabela text;
    v_tamanho numeric;
begin
    select schema_destino, tabela_destino into v_schema, v_tabela
    from plataforma.politica_dataset
    where dataset_codigo = p_dataset_codigo;

    if v_schema is null then
        raise exception 'Dataset % nao encontrado em plataforma.politica_dataset', p_dataset_codigo;
    end if;

    select coalesce(pg_total_relation_size(to_regclass(format('%I.%I', v_schema, v_tabela)))::numeric / 1e9, 0)
    into v_tamanho;

    return v_tamanho::numeric(12,4);
end;
$$;


-- 5. Rotina operacional para registrar recomendações de reclassificação
create or replace function plataforma.registrar_reclassificacao_dataset_pendente()
returns integer
language plpgsql
as $$
declare
    v_total integer;
begin
    insert into plataforma.reclassificacao_dataset_pendente (
        dataset_codigo,
        tamanho_gb,
        limite_full_gb,
        classe_atual,
        classe_sugerida,
        motivo
    )
    select
        vw.dataset_codigo,
        vw.tamanho_gb,
        vw.limite_full_gb,
        vw.classe_dataset,
        case
            when pd.coluna_competencia is not null then 'grande_temporal'
            else 'snapshot_atual'
        end as classe_sugerida,
        format(
            'Dataset pequena_full_ate_5gb excedeu limite de %s GB com tamanho atual de %s GB; reclassificacao exige aprovacao manual.',
            vw.limite_full_gb,
            vw.tamanho_gb
        ) as motivo
    from plataforma.vw_tamanho_dataset vw
    join plataforma.politica_dataset pd
        on pd.dataset_codigo = vw.dataset_codigo
    where vw.classe_dataset = 'pequena_full_ate_5gb'
      and vw.acima_do_limite = true
      and not exists (
          select 1
          from plataforma.reclassificacao_dataset_pendente r
          where r.dataset_codigo = vw.dataset_codigo
            and r.status in ('pendente','em_analise','aprovada')
      );

    get diagnostics v_total = row_count;
    return v_total;
end;
$$;


-- ================================================================
-- 6. Carga inicial dos datasets (HIS-34.3)
-- ================================================================

insert into plataforma.politica_dataset (
    dataset_codigo,
    descricao,
    classe_dataset,
    estrategia_carga,
    schema_destino,
    tabela_destino,
    coluna_competencia,
    anos_carga_hot,
    limite_full_gb,
    particionar_por_ano,
    carregar_apenas_ultima_versao,
    historico_sob_demanda,
    ativo
)
values
    -- Grande temporal: ano vigente + ano anterior.
    ('sib_operadora', 'SIB beneficiários por operadora', 'grande_temporal', 'ano_vigente_mais_ano_anterior', 'bruto_ans', 'sib_beneficiario_operadora', 'competencia', 2, null, true, false, true, true),
    ('sib_municipio', 'SIB beneficiários por município', 'grande_temporal', 'ano_vigente_mais_ano_anterior', 'bruto_ans', 'sib_beneficiario_municipio', 'competencia', 2, null, true, false, true, true),
    ('tiss_producao', 'TISS produção por procedimento trimestral', 'grande_temporal', 'ano_vigente_mais_ano_anterior', 'bruto_ans', 'tiss_procedimento_trimestral', 'trimestre', 2, null, true, false, true, true),
    ('vda', 'VDA - valor devido à ANS mensal', 'grande_temporal', 'ano_vigente_mais_ano_anterior', 'bruto_ans', 'vda_operadora_mensal', 'competencia', 2, null, true, false, true, true),
    ('glosa', 'Glosa mensal por operadora', 'grande_temporal', 'ano_vigente_mais_ano_anterior', 'bruto_ans', 'glosa_operadora_mensal', 'competencia', 2, null, true, false, true, true),
    ('portabilidade', 'Portabilidade de carências mensal', 'grande_temporal', 'ano_vigente_mais_ano_anterior', 'bruto_ans', 'portabilidade_operadora_mensal', 'competencia', 2, null, true, false, true, true),
    ('rede_prestador', 'Rede assistencial por operadora e município', 'grande_temporal', 'ano_vigente_mais_ano_anterior', 'bruto_ans', 'rede_prestador_municipio', 'competencia', 2, null, true, false, true, true),

    -- Pequena full até 5 GB.
    ('cadop', 'CADOP - dados cadastrais das operadoras', 'pequena_full_ate_5gb', 'full_ate_5gb', 'bruto_ans', 'cadop', null, null, 5.00, false, false, false, true),
    ('idss', 'IDSS - índice de desempenho da saúde suplementar', 'pequena_full_ate_5gb', 'full_ate_5gb', 'bruto_ans', 'idss', null, null, 5.00, false, false, false, true),
    ('igr', 'IGR - índice de garantia de retorno', 'pequena_full_ate_5gb', 'full_ate_5gb', 'bruto_ans', 'igr_operadora_trimestral', null, null, 5.00, false, false, false, true),
    ('nip', 'NIP - notificação de intermediação preliminar', 'pequena_full_ate_5gb', 'full_ate_5gb', 'bruto_ans', 'nip_operadora_trimestral', null, null, 5.00, false, false, false, true),
    -- Regime especial é cadastral, mas preserva snapshot histórico crítico regulatório; permanece full enquanto <= 5 GB.
    ('regime_especial', 'Regime especial de direção fiscal/técnica', 'pequena_full_ate_5gb', 'full_ate_5gb', 'bruto_ans', 'regime_especial_operadora_trimestral', null, null, 5.00, false, false, false, true),
    ('prudencial', 'Prudencial ANS', 'pequena_full_ate_5gb', 'full_ate_5gb', 'bruto_ans', 'prudencial_operadora_trimestral', null, null, 5.00, false, false, false, true),
    ('lista_excelencia_reducao', 'Lista de excelência e redução RN 623/2024', 'pequena_full_ate_5gb', 'full_ate_5gb', 'bruto_ans', 'rn623_lista_operadora_trimestral', null, null, 5.00, false, false, false, true),
    ('taxa_resolutividade', 'Taxa de resolutividade por operadora', 'pequena_full_ate_5gb', 'full_ate_5gb', 'bruto_ans', 'taxa_resolutividade_operadora_trimestral', null, null, 5.00, false, false, false, true),
    ('diops', 'DIOPS - demonstrações contábeis trimestrais', 'pequena_full_ate_5gb', 'full_ate_5gb', 'bruto_ans', 'diops_operadora_trimestral', null, null, 5.00, false, false, false, true),
    ('fip', 'FIP - série financeira trimestral', 'pequena_full_ate_5gb', 'full_ate_5gb', 'bruto_ans', 'fip_operadora_trimestral', null, null, 5.00, false, false, false, true),
    ('ans_arquivo_generico', 'Metadados de arquivos ANS sem parser dedicado', 'pequena_full_ate_5gb', 'full_ate_5gb', 'bruto_ans', 'ans_arquivo_generico', null, null, 5.00, false, false, false, true),
    ('dimensoes_ibge', 'Dimensões IBGE (UF, município, população)', 'pequena_full_ate_5gb', 'full_ate_5gb', 'ref_ans', 'ref_municipio_ibge', null, null, 5.00, false, false, false, true),

    -- Referência versionada: apenas última versão vigente.
    ('tuss_procedimento', 'TUSS - tabela de procedimentos', 'referencia_versionada', 'ultima_versao_vigente', 'ref_ans', 'ref_tuss', null, null, null, false, true, false, true),
    ('tuss_material_opme', 'TUSS - materiais e OPME', 'referencia_versionada', 'ultima_versao_vigente', 'bruto_ans', 'tuss_material_opme', null, null, null, false, true, false, true),
    ('tuss_medicamento', 'TUSS - medicamentos', 'referencia_versionada', 'ultima_versao_vigente', 'bruto_ans', 'tuss_medicamento', null, null, null, false, true, false, true),
    ('depara_sip_tuss', 'DE-PARA SIP/TUSS', 'referencia_versionada', 'ultima_versao_vigente', 'bruto_ans', 'depara_sip_tuss', null, null, null, false, true, false, true),
    ('rol_procedimento', 'ROL - rol de procedimentos ANS', 'referencia_versionada', 'ultima_versao_vigente', 'ref_ans', 'ref_rol_procedimento', null, null, null, false, true, false, true),

    -- Snapshot atual: substituição completa a cada carga.
    ('prestador_cadastral', 'Prestadores cadastrais - rede vigente', 'snapshot_atual', 'snapshot_atual', 'bruto_ans', 'prestador_cadastral', null, null, null, false, true, false, true),
    ('qualiss', 'QUALISS - qualificação de prestadores', 'snapshot_atual', 'snapshot_atual', 'bruto_ans', 'qualiss', null, null, null, false, true, false, true),
    ('cnes_estabelecimento', 'CNES - estabelecimentos de saúde', 'snapshot_atual', 'snapshot_atual', 'bruto_ans', 'cnes_estabelecimento', null, null, null, false, false, false, true),

    -- Histórico sob demanda: sem carga padrão na janela hot.
    ('ans_linha_generica', 'Linhas JSONB ANS sem parser dedicado', 'historico_sob_demanda', 'historico_sob_demanda', 'bruto_ans', 'ans_linha_generica', null, null, null, false, false, true, true)
on conflict (dataset_codigo) do update set
    descricao = excluded.descricao,
    classe_dataset = excluded.classe_dataset,
    estrategia_carga = excluded.estrategia_carga,
    schema_destino = excluded.schema_destino,
    tabela_destino = excluded.tabela_destino,
    coluna_competencia = excluded.coluna_competencia,
    anos_carga_hot = excluded.anos_carga_hot,
    limite_full_gb = excluded.limite_full_gb,
    particionar_por_ano = excluded.particionar_por_ano,
    carregar_apenas_ultima_versao = excluded.carregar_apenas_ultima_versao,
    historico_sob_demanda = excluded.historico_sob_demanda,
    ativo = excluded.ativo;
