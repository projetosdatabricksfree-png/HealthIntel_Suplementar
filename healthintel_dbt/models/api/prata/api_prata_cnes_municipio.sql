{{
    config(
        materialized='table',
        tags=['prata', 'cnes'],
        post_hook=[
            "{{ criar_indice_api(this, 'competencia') }}",
            "{{ criar_indice_api(this, 'cd_municipio') }}",
            "{{ criar_indice_api(this, 'tipo_unidade') }}"
        ]
    )
}}

select
    cnes.*,
    'api_prata_cnes_municipio_v1' as versao_dataset,
    {{ taxa_aprovacao_dataset('cnes_estabelecimento', ref('stg_cnes_estabelecimento')) }} as taxa_aprovacao_lote
from {{ ref('int_cnes_municipio_resumo') }} as cnes
