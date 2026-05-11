{{
    config(
        materialized='table',
        tags=['delta_ans_100', 'precificacao_ntrp'],
        post_hook=[
            "{{ criar_indice_api(this, 'registro_ans') }}",
            "{{ criar_indice_api(this, 'competencia') }}"
        ]
    )
}}

select
    competencia,
    registro_ans,
    tipo_contratacao,
    agrupamento,
    percentual_reajuste,
    data_aplicacao,
    _carregado_em
from {{ ref('stg_percentual_reajuste_agrupamento') }}
