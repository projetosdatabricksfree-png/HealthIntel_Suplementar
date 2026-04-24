{{
    config(
        materialized='table',
        tags=['prata', 'rede']
    )
}}

select
    metrica.*,
    {{ taxa_aprovacao_dataset('beneficiario_localidade', ref('int_metrica_municipio')) }} as taxa_aprovacao_lote
from {{ ref('int_metrica_municipio') }} as metrica
