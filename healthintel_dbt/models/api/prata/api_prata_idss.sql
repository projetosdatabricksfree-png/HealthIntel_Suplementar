{{
    config(
        materialized='table',
        tags=['prata'],
        post_hook=[
            "{{ criar_indice_api(this, 'registro_ans') }}",
            "{{ criar_indice_api(this, 'ano_base') }}"
        ]
    )
}}

select
    stg.*,
    {{ taxa_aprovacao_dataset('idss', ref('stg_idss')) }} as taxa_aprovacao_lote
from {{ ref('stg_idss') }} as stg
