{{
    config(
        materialized='ephemeral',
        tags=['tiss']
    )
}}

with base as (
    select
        trimestre,
        registro_ans,
        grupo_procedimento,
        max(grupo_desc) as grupo_desc,
        max(subgrupo_procedimento) as subgrupo_procedimento,
        sum(coalesce(qt_procedimentos, 0)) as qt_procedimentos,
        sum(coalesce(qt_beneficiarios_distintos, 0)) as qt_beneficiarios_distintos,
        sum(coalesce(valor_total, 0)) as valor_total
    from {{ ref('stg_tiss_procedimento') }}
    group by 1, 2, 3
),
base_operadora as (
    select
        base.*,
        sum(base.qt_procedimentos) over (
            partition by base.trimestre, base.registro_ans
        ) as total_procedimentos_operadora
    from base
),
operadora as (
    select
        base_operadora.*,
        round(
            coalesce(
                base_operadora.valor_total / nullif(base_operadora.qt_procedimentos, 0),
                0
            ),
            2
        ) as valor_medio_por_procedimento,
        round(
            coalesce(
                (base_operadora.qt_procedimentos::numeric / nullif(base_operadora.total_procedimentos_operadora, 0)) * 100,
                0
            ),
            2
        ) as pct_procedimentos_por_grupo
    from base_operadora
),
operadora_snap as (
    select
        {{ normalizar_registro_ans('registro_ans') }} as registro_ans,
        nome,
        nome_fantasia,
        modalidade,
        uf_sede
    from {{ ref('snap_operadora') }}
    where dbt_valid_to is null
)

select
    operadora.trimestre,
    operadora.registro_ans,
    operadora.grupo_procedimento,
    operadora.grupo_desc,
    operadora.subgrupo_procedimento,
    operadora.qt_procedimentos,
    operadora.qt_beneficiarios_distintos,
    operadora.valor_total,
    operadora.valor_medio_por_procedimento,
    operadora.pct_procedimentos_por_grupo,
    operadora.total_procedimentos_operadora,
    operadora_dim.operadora_id,
    operadora_snap.nome,
    operadora_snap.nome_fantasia,
    operadora_snap.modalidade,
    operadora_snap.uf_sede
from operadora
inner join operadora_snap
    on operadora.registro_ans = operadora_snap.registro_ans
inner join {{ ref('dim_operadora_atual') }} as operadora_dim
    on operadora.registro_ans = operadora_dim.registro_ans
