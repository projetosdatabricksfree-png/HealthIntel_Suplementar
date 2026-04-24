{{
    config(
        materialized='table',
        tags=['prata']
    )
}}

select
    int_op.*,
    {{ taxa_aprovacao_dataset('beneficiario_operadora', ref('int_beneficiario_operadora_enriquecido')) }} as taxa_aprovacao_lote
from {{ ref('int_beneficiario_operadora_enriquecido') }} as int_op
