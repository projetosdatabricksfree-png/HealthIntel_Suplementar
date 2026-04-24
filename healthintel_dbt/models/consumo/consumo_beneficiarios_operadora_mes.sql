{{ config(materialized='table', schema='consumo_ans', tags=['consumo']) }}

select
    ben.registro_ans,
    op.nome as razao_social,
    op.modalidade,
    ben.competencia,
    ben.qt_beneficiario_ativo as qt_beneficiarios,
    ben.taxa_crescimento_12m as variacao_12m_pct
from {{ ref('fat_beneficiario_operadora') }} as ben
left join {{ ref('dim_operadora_atual') }} as op
    on op.registro_ans = ben.registro_ans
