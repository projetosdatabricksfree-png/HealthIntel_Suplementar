{{
    config(materialized='table', tags=['mart'])
}}

select
    tiss.registro_ans,
    tiss.grupo_procedimento as cd_procedimento_tuss,
    tiss.trimestre,
    tiss.nome as razao_social,
    tiss.grupo_desc,
    tiss.subgrupo_procedimento,
    tiss.qt_procedimentos,
    tiss.valor_total as vl_total,
    tiss.valor_medio as custo_medio_procedimento,
    sin.sinistralidade_grupo_pct as sinistralidade_pct,
    tiss.rank_por_valor
from {{ ref('fat_tiss_procedimento_operadora') }} as tiss
left join {{ ref('fat_sinistralidade_procedimento') }} as sin
    on tiss.registro_ans = sin.registro_ans
    and tiss.trimestre = sin.trimestre
    and tiss.grupo_procedimento = sin.grupo_procedimento
