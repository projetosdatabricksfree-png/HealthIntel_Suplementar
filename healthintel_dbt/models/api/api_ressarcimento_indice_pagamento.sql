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
    indice_efetivo_pagamento,
    valor_total_cobrado,
    valor_total_pago,
    _carregado_em
from {{ ref('stg_ressarcimento_indice_pagamento') }}
