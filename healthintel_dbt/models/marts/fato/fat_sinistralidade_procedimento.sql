{{
    config(
        materialized='incremental',
        unique_key=['trimestre', 'registro_ans', 'grupo_procedimento'],
        incremental_strategy='delete+insert',
        on_schema_change='sync_all_columns',
        tags=['tiss', 'financeiro']
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
        valor_tiss,
        receita_total,
        sinistralidade_grupo_pct,
        desvio_padrao_sinistralidade,
        flag_sinistralidade_alta
    from {{ ref('int_sinistralidade_procedimento') }}
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
    base.valor_tiss,
    base.receita_total,
    base.sinistralidade_grupo_pct,
    base.desvio_padrao_sinistralidade,
    base.flag_sinistralidade_alta,
    rank() over (
        partition by base.trimestre, base.registro_ans
        order by base.sinistralidade_grupo_pct desc nulls last, base.grupo_procedimento
    ) as rank_sinistralidade,
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
