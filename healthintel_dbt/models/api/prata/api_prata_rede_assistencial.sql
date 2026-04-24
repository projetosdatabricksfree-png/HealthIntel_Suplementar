{{
    config(
        materialized='table',
        tags=['prata'],
        post_hook=[
            "{{ criar_indice_api(this, 'registro_ans') }}",
            "{{ criar_indice_api(this, 'competencia') }}",
            "{{ criar_indice_api(this, 'cd_municipio') }}"
        ]
    )
}}

select
    stg.*,
    {{ taxa_aprovacao_dataset('rede_assistencial', ref('stg_rede_assistencial')) }} as taxa_aprovacao_lote
from {{ ref('stg_rede_assistencial') }} as stg
