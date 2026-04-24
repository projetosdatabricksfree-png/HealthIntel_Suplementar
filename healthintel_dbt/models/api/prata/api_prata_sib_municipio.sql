{{
    config(
        materialized='table',
        tags=['prata'],
        post_hook=[
            "{{ criar_indice_api(this, 'codigo_ibge') }}",
            "{{ criar_indice_api(this, 'competencia') }}"
        ]
    )
}}

select
    stg.*,
    {{ taxa_aprovacao_dataset('sib_municipio', ref('stg_sib_municipio')) }} as taxa_aprovacao_lote
from {{ ref('stg_sib_municipio') }} as stg
