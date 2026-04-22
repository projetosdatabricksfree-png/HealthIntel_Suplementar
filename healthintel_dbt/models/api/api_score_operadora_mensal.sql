{{
    config(
        post_hook=[
            "{{ criar_indice_api(this, 'registro_ans') }}",
            "{{ criar_indice_api(this, 'registro_ans, competencia') }}"
        ]
    )
}}

select
    f.registro_ans,
    f.competencia,
    d.nome,
    d.nome_fantasia,
    d.modalidade,
    d.uf_sede,
    d.municipio_sede,
    f.score_final,
    f.rating,
    f.score_crescimento,
    f.score_qualidade,
    f.score_estabilidade,
    f.score_presenca,
    f.versao_score
from {{ ref('fat_score_operadora_mensal') }} as f
inner join {{ ref('dim_operadora_atual') }} as d
    on f.registro_ans = d.registro_ans
