{{
    config(
        materialized='incremental',
        unique_key=['trimestre', 'registro_ans', 'grupo_procedimento'],
        incremental_strategy='delete+insert',
        on_schema_change='sync_all_columns',
        tags=['tiss']
    )
}}

with base as (
    select
        trimestre,
        registro_ans,
        operadora_id,
        nome,
        nome_fantasia,
        modalidade,
        uf_sede,
        grupo_procedimento,
        grupo_desc,
        subgrupo_procedimento,
        qt_procedimentos,
        qt_beneficiarios_distintos,
        valor_total,
        valor_medio_por_procedimento,
        pct_procedimentos_por_grupo,
        total_procedimentos_operadora
    from {{ ref('int_tiss_operadora_trimestre') }}
)

select
    base.trimestre,
    base.registro_ans,
    base.operadora_id,
    base.nome,
    base.nome_fantasia,
    base.modalidade,
    base.uf_sede,
    base.grupo_procedimento,
    base.grupo_desc,
    base.subgrupo_procedimento,
    base.qt_procedimentos,
    base.qt_beneficiarios_distintos,
    base.valor_total,
    base.valor_medio_por_procedimento as valor_medio,
    base.pct_procedimentos_por_grupo as pct_do_total_operadora,
    row_number() over (
        partition by base.trimestre, base.registro_ans
        order by base.valor_total desc nulls last, base.grupo_procedimento
    ) as rank_por_valor,
    'tiss_v1' as versao_dataset
from base
{% if is_incremental() %}
where base.trimestre in (
    select distinct trimestre
    from {{ ref('stg_tiss_procedimento') }}
    order by trimestre desc
    limit 2
)
{% endif %}
