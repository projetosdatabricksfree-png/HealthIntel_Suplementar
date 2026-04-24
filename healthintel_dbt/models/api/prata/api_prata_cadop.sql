{{
    config(
        materialized='table',
        tags=['prata'],
        post_hook=[
            "{{ criar_indice_api(this, 'registro_ans') }}"
        ]
    )
}}

select
    stg.*,
    {{ taxa_aprovacao_dataset('cadop', ref('stg_cadop')) }} as taxa_aprovacao_lote
from {{ ref('stg_cadop') }} as stg
