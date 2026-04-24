{{
    config(
        materialized='table',
        tags=['score_v3'],
        post_hook=[
            "{{ criar_indice_api(this, 'operadora_id') }}",
            "{{ criar_indice_api(this, 'competencia_id') }}",
            "{{ criar_indice_api(this, 'score_v3_final') }}"
        ]
    )
}}

select
    f.operadora_id,
    f.competencia_id,
    f.registro_ans,
    f.nome,
    f.nome_fantasia,
    f.modalidade,
    f.uf_sede,
    f.trimestre_financeiro,
    f.score_core,
    f.score_regulatorio,
    f.score_financeiro,
    f.score_rede,
    f.score_estrutural,
    f.score_completo,
    f.score_v3_final,
    f.versao_metodologia
from {{ ref('fat_score_v3_operadora_mensal') }} as f
