{{
    config(
        unique_key=['operadora_id', 'trimestre'],
        incremental_strategy='delete+insert',
        on_schema_change='sync_all_columns',
        tags=['financeiro']
    )
}}

with base as (
    select *
    from {{ ref('int_financeiro_operadora_periodo') }}
),
parto_cesareo as (
    select
        {{ normalizar_registro_ans('cast(registro_ans as text)') }} as registro_ans,
        upper(trim(trimestre)) as trimestre,
        cast(parto_cesareo_pct as numeric(6,2)) as parto_cesareo_pct
    from {{ ref('ref_parto_cesareo') }}
)

select
    base.operadora_id,
    base.registro_ans,
    base.nome,
    base.nome_fantasia,
    base.modalidade,
    base.uf_sede,
    base.trimestre,
    base.cnpj,
    base.ativo_total,
    base.passivo_total,
    base.patrimonio_liquido,
    base.receita_total,
    base.despesa_total,
    base.resultado_periodo,
    base.resultado_operacional,
    base.provisao_tecnica,
    base.margem_solvencia_calculada,
    base.sinistro_total,
    base.contraprestacao_total,
    base.sinistralidade_bruta,
    base.ressarcimento_sus,
    base.evento_indenizavel,
    base.sinistralidade_liquida,
    base.taxa_sinistralidade_calculada,
    base.indice_sinistralidade,
    base.margem_liquida_pct,
    base.cobertura_provisao,
    base.resultado_operacional_bruto,
    base.score_indice_sinistralidade,
    base.score_margem_liquida,
    base.score_cobertura_provisao,
    base.score_resultado_normalizado,
    parto_cesareo.parto_cesareo_pct,
    round(
        (
            (coalesce(base.score_indice_sinistralidade, 0) * base_pesos.peso_indice_sinistralidade)
            + (coalesce(base.score_margem_liquida, 0) * base_pesos.peso_margem_liquida)
            + (coalesce(base.score_cobertura_provisao, 0) * base_pesos.peso_cobertura_provisao)
            + (coalesce(base.score_resultado_normalizado, 0) * base_pesos.peso_resultado_normalizado)
        ),
        2
    )::numeric(12,2) as score_financeiro_base,
    {{ classificar_rating_regulatorio('round(((coalesce(base.score_indice_sinistralidade, 0) * base_pesos.peso_indice_sinistralidade) + (coalesce(base.score_margem_liquida, 0) * base_pesos.peso_margem_liquida) + (coalesce(base.score_cobertura_provisao, 0) * base_pesos.peso_cobertura_provisao) + (coalesce(base.score_resultado_normalizado, 0) * base_pesos.peso_resultado_normalizado)), 2)') }} as rating_financeiro,
    base.versao_financeira
from base
left join parto_cesareo
    on base.registro_ans = parto_cesareo.registro_ans
    and base.trimestre = parto_cesareo.trimestre
cross join (
    select
        max(case when indicador = 'indice_sinistralidade' then cast(peso as numeric(10,4)) end) as peso_indice_sinistralidade,
        max(case when indicador = 'margem_liquida' then cast(peso as numeric(10,4)) end) as peso_margem_liquida,
        max(case when indicador = 'cobertura_provisao' then cast(peso as numeric(10,4)) end) as peso_cobertura_provisao,
        max(case when indicador = 'resultado_normalizado' then cast(peso as numeric(10,4)) end) as peso_resultado_normalizado
    from {{ ref('ref_indicador_financeiro') }}
) as base_pesos
