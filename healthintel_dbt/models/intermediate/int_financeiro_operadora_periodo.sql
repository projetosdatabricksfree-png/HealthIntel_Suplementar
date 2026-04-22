{{
    config(materialized='ephemeral', tags=['financeiro'])
}}

with chaves as (
    select distinct registro_ans, trimestre
    from {{ ref('stg_diops') }}
    union
    select distinct registro_ans, trimestre
    from {{ ref('stg_fip') }}
),
base as (
    select
        d.operadora_id,
        d.registro_ans,
        d.nome,
        d.nome_fantasia,
        d.modalidade,
        d.uf_sede,
        k.trimestre
    from chaves as k
    inner join {{ ref('dim_operadora_atual') }} as d
        on d.registro_ans = k.registro_ans
),
diops as (
    select
        registro_ans,
        trimestre,
        cnpj,
        ativo_total,
        passivo_total,
        patrimonio_liquido,
        receita_total,
        despesa_total,
        resultado_periodo,
        resultado_operacional,
        provisao_tecnica,
        margem_solvencia_calculada,
        situacao_resultado
    from {{ ref('stg_diops') }}
),
fip as (
    select
        registro_ans,
        trimestre,
        modalidade,
        tipo_contratacao,
        sinistro_total,
        contraprestacao_total,
        sinistralidade_bruta,
        ressarcimento_sus,
        evento_indenizavel,
        sinistralidade_liquida,
        taxa_sinistralidade_calculada
    from {{ ref('stg_fip') }}
),
pesos as (
    select
        max(case when indicador = 'indice_sinistralidade' then cast(peso as numeric(10,4)) end) as peso_indice_sinistralidade,
        max(case when indicador = 'margem_liquida' then cast(peso as numeric(10,4)) end) as peso_margem_liquida,
        max(case when indicador = 'cobertura_provisao' then cast(peso as numeric(10,4)) end) as peso_cobertura_provisao,
        max(case when indicador = 'resultado_normalizado' then cast(peso as numeric(10,4)) end) as peso_resultado_normalizado,
        max(case when indicador = 'indice_sinistralidade' then cast(intervalo_minimo as numeric(18,4)) end) as minimo_indice_sinistralidade,
        max(case when indicador = 'indice_sinistralidade' then cast(intervalo_maximo as numeric(18,4)) end) as maximo_indice_sinistralidade,
        max(case when indicador = 'margem_liquida' then cast(intervalo_minimo as numeric(18,4)) end) as minimo_margem_liquida,
        max(case when indicador = 'margem_liquida' then cast(intervalo_maximo as numeric(18,4)) end) as maximo_margem_liquida,
        max(case when indicador = 'cobertura_provisao' then cast(intervalo_minimo as numeric(18,4)) end) as minimo_cobertura_provisao,
        max(case when indicador = 'cobertura_provisao' then cast(intervalo_maximo as numeric(18,4)) end) as maximo_cobertura_provisao,
        max(case when indicador = 'resultado_normalizado' then cast(intervalo_minimo as numeric(18,4)) end) as minimo_resultado_normalizado,
        max(case when indicador = 'resultado_normalizado' then cast(intervalo_maximo as numeric(18,4)) end) as maximo_resultado_normalizado
    from {{ ref('ref_indicador_financeiro') }}
),
base_harmonizada as (
    select
        base.operadora_id,
        base.registro_ans,
        base.nome,
        base.nome_fantasia,
        base.modalidade,
        base.uf_sede,
        base.trimestre,
        diops.cnpj,
        coalesce(diops.ativo_total, 0) as ativo_total,
        coalesce(diops.passivo_total, 0) as passivo_total,
        coalesce(diops.patrimonio_liquido, 0) as patrimonio_liquido,
        coalesce(diops.receita_total, 0) as receita_total,
        coalesce(diops.despesa_total, 0) as despesa_total,
        coalesce(diops.resultado_periodo, 0) as resultado_periodo,
        coalesce(diops.resultado_operacional, 0) as resultado_operacional,
        coalesce(diops.provisao_tecnica, 0) as provisao_tecnica,
        coalesce(diops.margem_solvencia_calculada, 0) as margem_solvencia_calculada,
        coalesce(diops.situacao_resultado, 'sem_resultado') as situacao_resultado,
        coalesce(fip.tipo_contratacao, 'nao_informada') as tipo_contratacao,
        coalesce(fip.sinistro_total, 0) as sinistro_total,
        coalesce(fip.contraprestacao_total, 0) as contraprestacao_total,
        coalesce(fip.sinistralidade_bruta, 0) as sinistralidade_bruta,
        coalesce(fip.ressarcimento_sus, 0) as ressarcimento_sus,
        coalesce(fip.evento_indenizavel, 0) as evento_indenizavel,
        coalesce(fip.sinistralidade_liquida, 0) as sinistralidade_liquida,
        coalesce(fip.taxa_sinistralidade_calculada, 0) as taxa_sinistralidade_calculada
    from base
    left join diops
        on base.registro_ans = diops.registro_ans
        and base.trimestre = diops.trimestre
    left join fip
        on base.registro_ans = fip.registro_ans
        and base.trimestre = fip.trimestre
),
metricas as (
    select
        *,
        case
            when contraprestacao_total = 0 then 0
            else sinistro_total / nullif(contraprestacao_total, 0)
        end as indice_sinistralidade,
        case
            when receita_total = 0 then 0
            else resultado_operacional / nullif(receita_total, 0) * 100
        end as margem_liquida_pct,
        case
            when sinistro_total = 0 then 0
            else provisao_tecnica / nullif(sinistro_total / 4, 0)
        end as cobertura_provisao,
        case
            when resultado_operacional is null then 0
            else resultado_operacional
        end as resultado_operacional_bruto
    from base_harmonizada
)

select
    metricas.operadora_id,
    metricas.registro_ans,
    metricas.nome,
    metricas.nome_fantasia,
    metricas.modalidade,
    metricas.uf_sede,
    metricas.trimestre,
    metricas.cnpj,
    metricas.ativo_total,
    metricas.passivo_total,
    metricas.patrimonio_liquido,
    metricas.receita_total,
    metricas.despesa_total,
    metricas.resultado_periodo,
    metricas.resultado_operacional,
    metricas.provisao_tecnica,
    metricas.margem_solvencia_calculada,
    metricas.sinistro_total,
    metricas.contraprestacao_total,
    metricas.sinistralidade_bruta,
    metricas.ressarcimento_sus,
    metricas.evento_indenizavel,
    metricas.sinistralidade_liquida,
    metricas.taxa_sinistralidade_calculada,
    metricas.tipo_contratacao,
    metricas.indice_sinistralidade,
    metricas.margem_liquida_pct,
    metricas.cobertura_provisao,
    metricas.resultado_operacional_bruto,
    case
        when metricas.contraprestacao_total = 0 then 0
        else (
            100
            - cast(
                {{ normalizar_0_100('metricas.indice_sinistralidade', 'pesos.minimo_indice_sinistralidade', 'pesos.maximo_indice_sinistralidade') }}
                as numeric(12,4)
            )
        )
    end as score_indice_sinistralidade,
    cast(
        {{ normalizar_0_100('metricas.margem_liquida_pct', 'pesos.minimo_margem_liquida', 'pesos.maximo_margem_liquida') }}
        as numeric(12,4)
    ) as score_margem_liquida,
    cast(
        {{ normalizar_0_100('metricas.cobertura_provisao', 'pesos.minimo_cobertura_provisao', 'pesos.maximo_cobertura_provisao') }}
        as numeric(12,4)
    ) as score_cobertura_provisao,
    cast(
        {{ normalizar_0_100('metricas.resultado_operacional_bruto', 'pesos.minimo_resultado_normalizado', 'pesos.maximo_resultado_normalizado') }}
        as numeric(12,4)
    ) as score_resultado_normalizado,
    'financeiro_v1' as versao_financeira
from metricas
cross join pesos
