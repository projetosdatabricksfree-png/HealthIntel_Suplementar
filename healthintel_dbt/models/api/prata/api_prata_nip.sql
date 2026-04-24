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
    {{ taxa_aprovacao_dataset('nip', ref('stg_nip')) }} as taxa_aprovacao_lote
from {{ ref('stg_nip') }} as stg
