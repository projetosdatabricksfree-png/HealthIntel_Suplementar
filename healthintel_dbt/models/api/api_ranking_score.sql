{{
    config(
        post_hook=[
            "{{ criar_indices(this, ['operadora_id']) }}",
            "{{ criar_indices(this, ['ranking_posicao']) }}"
        ]
    )
}}

with base as (
    select
        operadora_id,
        registro_ans,
        competencia,
        score_final,
        rating,
        versao_score,
        row_number() over (
            order by score_final desc nulls last, rating asc, competencia desc
        ) as ranking_posicao
    from {{ ref('fat_score_operadora_mensal') }}
)

select
    base.operadora_id,
    base.registro_ans,
    dim.nome,
    base.competencia,
    base.score_final,
    base.rating,
    base.ranking_posicao,
    base.versao_score
from base
left join {{ ref('dim_operadora_atual') }} as dim
    on base.registro_ans = dim.registro_ans
