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
    vl_cobrado,
    vl_arrecadado,
    vl_inadimplente,
    qt_guias,
    _carregado_em
from {{ ref('stg_ressarcimento_cobranca_arrecadacao') }}
