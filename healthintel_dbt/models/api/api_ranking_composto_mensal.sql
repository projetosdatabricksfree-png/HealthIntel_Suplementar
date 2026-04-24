{{
    config(
        materialized='table',
        tags=['score_v3'],
        post_hook=[
            "{{ criar_indice_api(this, 'competencia_id') }}",
            "{{ criar_indice_api(this, 'operadora_id') }}",
            "{{ criar_indice_api(this, 'score_v3_final') }}"
        ]
    )
}}

select
    r.operadora_id,
    r.competencia_id,
    r.registro_ans,
    r.nome,
    r.nome_fantasia,
    r.modalidade,
    r.uf_sede,
    r.score_v3_final,
    r.posicao_geral,
    r.posicao_por_modalidade,
    r.variacao_posicao_3m,
    r.versao_metodologia
from {{ ref('fat_ranking_composto_mensal') }} as r
