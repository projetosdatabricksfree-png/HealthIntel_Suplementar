{{
    config(materialized='table', tags=['mart'])
}}

select
    ben.registro_ans,
    ben.competencia,
    op.nome as razao_social,
    op.nome_fantasia,
    op.modalidade,
    op.uf_sede,
    ben.qt_beneficiario_ativo as qt_beneficiarios,
    ben.taxa_crescimento_12m as variacao_12m_pct,
    score.score_v3_final as score_total,
    score.score_core as componente_core,
    score.score_regulatorio as componente_regulatorio,
    score.score_financeiro as componente_financeiro,
    score.score_rede as componente_rede,
    score.score_estrutural as componente_estrutural,
    score.versao_metodologia
from {{ ref('fat_beneficiario_operadora') }} as ben
left join {{ ref('dim_operadora_atual') }} as op
    on op.registro_ans = ben.registro_ans
left join {{ ref('fat_score_v3_operadora_mensal') }} as score
    on score.registro_ans = ben.registro_ans
    and score.competencia_id = ben.competencia
