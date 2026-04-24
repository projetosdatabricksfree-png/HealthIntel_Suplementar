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
    {{ taxa_aprovacao_dataset('sib_operadora', ref('stg_sib_operadora')) }} as taxa_aprovacao_lote
from {{ ref('stg_sib_operadora') }} as stg
