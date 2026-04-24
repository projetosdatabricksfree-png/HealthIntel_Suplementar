{{
    config(
        materialized='table',
        tags=['fato_v3', 'score_v3']
    )
}}

with base as (
    select *
    from {{ ref('fat_score_v3_operadora_mensal') }}
),
posicao as (
    select
        base.*,
        rank() over (
            partition by base.competencia_id
            order by base.score_v3_final desc nulls last, base.operadora_id
        ) as posicao_geral,
        rank() over (
            partition by base.competencia_id, base.modalidade
            order by base.score_v3_final desc nulls last, base.operadora_id
        ) as posicao_por_modalidade
    from base
),
historico as (
    select
        posicao.*,
        lag(posicao_geral, 3) over (
            partition by posicao.operadora_id
            order by posicao.competencia_id
        ) as posicao_3m_anterior
    from posicao
)

select
    operadora_id,
    competencia_id,
    registro_ans,
    nome,
    nome_fantasia,
    modalidade,
    uf_sede,
    score_v3_final,
    posicao_geral,
    posicao_por_modalidade,
    posicao_3m_anterior,
    case
        when posicao_3m_anterior is null then null
        else posicao_3m_anterior - posicao_geral
    end as variacao_posicao_3m,
    versao_metodologia
from historico
