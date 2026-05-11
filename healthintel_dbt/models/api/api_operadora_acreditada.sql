{{
    config(
        materialized='table',
        tags=['delta_ans_100', 'rede_prestadores'],
        post_hook=[
            "{{ criar_indice_api(this, 'registro_ans') }}"
        ]
    )
}}

select
    registro_ans,
    razao_social,
    acreditadora,
    nivel_acreditacao,
    data_acreditacao,
    data_validade,
    _carregado_em
from {{ ref('stg_operadora_acreditada') }}
