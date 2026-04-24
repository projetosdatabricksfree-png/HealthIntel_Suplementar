{{
    config(
        materialized='table',
        tags=['prata', 'cnes', 'rede'],
        post_hook=[
            "{{ criar_indice_api(this, 'competencia') }}",
            "{{ criar_indice_api(this, 'cd_municipio') }}",
            "{{ criar_indice_api(this, 'tipo_unidade') }}"
        ]
    )
}}

select
    gap.*,
    cast(null as varchar(6)) as registro_ans,
    {{ taxa_aprovacao_dataset('cnes_estabelecimento', ref('fat_cnes_rede_gap_municipio')) }} as taxa_aprovacao_lote
from {{ ref('fat_cnes_rede_gap_municipio') }} as gap
