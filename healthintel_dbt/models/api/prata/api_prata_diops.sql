{{
    config(
        materialized='table',
        tags=['prata'],
        post_hook=[
            "{{ criar_indice_api(this, 'registro_ans') }}",
            "{{ criar_indice_api(this, 'trimestre') }}"
        ]
    )
}}

select
    stg.*,
    {{ taxa_aprovacao_dataset('diops', ref('stg_diops')) }} as taxa_aprovacao_lote
from {{ ref('stg_diops') }} as stg
