{{
    config(
        materialized='table',
        tags=['prata'],
        post_hook=[
            "{{ criar_indice_api(this, 'registro_ans') }}",
            "{{ criar_indice_api(this, 'competencia') }}"
        ]
    )
}}

select
    stg.*,
    {{ taxa_aprovacao_dataset('vda', ref('stg_vda')) }} as taxa_aprovacao_lote
from {{ ref('stg_vda') }} as stg
