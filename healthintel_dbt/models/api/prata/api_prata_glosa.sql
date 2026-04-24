{{
    config(
        materialized='table',
        tags=['prata'],
        post_hook=[
            "{{ criar_indice_api(this, 'registro_ans') }}",
            "{{ criar_indice_api(this, 'competencia') }}",
            "{{ criar_indice_api(this, 'tipo_glosa') }}"
        ]
    )
}}

select
    stg.*,
    {{ taxa_aprovacao_dataset('glosa', ref('stg_glosa')) }} as taxa_aprovacao_lote
from {{ ref('stg_glosa') }} as stg
