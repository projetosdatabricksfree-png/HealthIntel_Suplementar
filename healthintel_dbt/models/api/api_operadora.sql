{{
    config(
        post_hook=[
            "{{ criar_indice_api(this, 'registro_ans') }}",
            "{{ criar_indice_api(this, 'uf_sede') }}"
        ]
    )
}}

with score_atual as (
    select
        registro_ans,
        competencia,
        score_final,
        rating,
        versao_score,
        row_number() over (
            partition by registro_ans
            order by competencia desc
        ) as rn
    from {{ ref('fat_score_operadora_mensal') }}
)

select
    d.registro_ans,
    d.nome,
    d.nome_fantasia,
    d.modalidade,
    d.uf_sede,
    s.competencia as competencia_referencia,
    s.score_final,
    s.rating,
    s.versao_score
from {{ ref('dim_operadora_atual') }} as d
left join score_atual as s
    on d.registro_ans = s.registro_ans
    and s.rn = 1
