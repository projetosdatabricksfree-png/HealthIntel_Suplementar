{{
    config(
        materialized='table',
        tags=['delta_ans_100', 'ressarcimento_sus'],
        post_hook=[
            "{{ criar_indice_api(this, 'registro_ans') }}",
            "{{ criar_indice_api(this, 'competencia') }}"
        ]
    )
}}

select
    competencia,
    registro_ans,
    nu_hc,
    vl_hc,
    status_hc,
    fase_cobranca,
    _carregado_em
from {{ ref('stg_ressarcimento_hc') }}
