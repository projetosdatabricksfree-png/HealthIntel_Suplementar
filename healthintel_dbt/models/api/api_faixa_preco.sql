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
    codigo_plano,
    faixa_etaria,
    sg_uf,
    vl_faixa_min,
    vl_faixa_max,
    _carregado_em
from {{ ref('stg_faixa_preco') }}
