{{
    config(
        materialized='table',
        tags=['prata']
    )
}}

select
    int_op.*,
    crec.taxa_crescimento_12m,
    crec.beneficiario_total_12m_anterior,
    crec.beneficiario_media_12m,
    {{ taxa_aprovacao_dataset('beneficiario_operadora', ref('int_beneficiario_operadora_enriquecido')) }} as taxa_aprovacao_lote
from {{ ref('int_beneficiario_operadora_enriquecido') }} as int_op
left join {{ ref('int_crescimento_operadora_12m') }} as crec
    on crec.operadora_id = int_op.operadora_id
    and crec.registro_ans = int_op.registro_ans
    and crec.competencia = int_op.competencia
