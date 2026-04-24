{{
    config(
        materialized='ephemeral',
        tags=['tiss', 'financeiro']
    )
}}

with tiss as (
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
),
diops as (
    select
        trimestre,
        registro_ans,
        receita_total
    from {{ ref('stg_diops') }}
)

select
    tiss.trimestre,
    tiss.registro_ans,
    tiss.operadora_id,
    tiss.nome,
    tiss.nome_fantasia,
    tiss.modalidade,
    tiss.uf_sede,
    tiss.grupo_procedimento,
    tiss.grupo_desc,
    tiss.subgrupo_procedimento,
    tiss.qt_procedimentos,
    tiss.qt_beneficiarios_distintos,
    tiss.valor_total as valor_tiss,
    diops.receita_total,
    round(
        case
            when coalesce(diops.receita_total, 0) = 0 then 0
            else (tiss.valor_total / nullif(diops.receita_total, 0)) * 100
        end,
        2
    ) as sinistralidade_grupo_pct,
    round(
        stddev_samp(
            case
                when coalesce(diops.receita_total, 0) = 0 then 0
                else (tiss.valor_total / nullif(diops.receita_total, 0)) * 100
            end
        ) over (partition by tiss.trimestre, tiss.registro_ans),
        2
    ) as desvio_padrao_sinistralidade,
    case
        when (
            case
                when coalesce(diops.receita_total, 0) = 0 then 0
                else (tiss.valor_total / nullif(diops.receita_total, 0)) * 100
            end
        ) > 80 then true
        else false
    end as flag_sinistralidade_alta
from tiss
inner join diops
    on diops.trimestre = tiss.trimestre
    and diops.registro_ans = tiss.registro_ans
