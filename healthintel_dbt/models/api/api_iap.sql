{{
    config(
        materialized='table',
        tags=['delta_ans_100', 'regulatorios_complementares'],
        post_hook=[
            "{{ criar_indice_api(this, 'registro_ans') }}",
            "{{ criar_indice_api(this, 'competencia') }}"
        ]
    )
}}

select
    competencia,
    registro_ans,
    dimensao,
    indicador,
    valor_indicador,
    peso_indicador,
    pontuacao,
    _carregado_em
from {{ ref('stg_iap') }}
