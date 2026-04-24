{{
    config(
        materialized='table',
        tags=['prata', 'tiss'],
        post_hook=[
            "{{ criar_indice_api(this, 'trimestre') }}",
            "{{ criar_indice_api(this, 'registro_ans') }}",
            "{{ criar_indice_api(this, 'grupo_procedimento') }}",
            "{{ criar_indice_api(this, 'cd_procedimento_tuss') }}"
        ]
    )
}}

select
    tiss.*,
    tiss.grupo_procedimento as cd_procedimento_tuss,
    {{ taxa_aprovacao_dataset('tiss_procedimento', ref('int_tiss_operadora_trimestre')) }} as taxa_aprovacao_lote
from {{ ref('int_tiss_operadora_trimestre') }} as tiss
