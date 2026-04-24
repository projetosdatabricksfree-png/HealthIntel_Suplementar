{{
    config(materialized='table', tags=['mart'])
}}

select
    score.registro_ans,
    score.competencia_id as competencia,
    score.nome as razao_social,
    score.modalidade,
    score.score_v3_final as score_total,
    case
        when score.score_v3_final >= 80 then 'Excelente'
        when score.score_v3_final >= 60 then 'Bom'
        when score.score_v3_final >= 40 then 'Regular'
        else 'Atencao'
    end as faixa_score,
    score.score_core as componente_core,
    score.score_regulatorio as componente_regulatorio,
    score.score_financeiro as componente_financeiro,
    score.score_rede as componente_rede,
    score.score_estrutural as componente_estrutural,
    score.versao_metodologia
from {{ ref('fat_score_v3_operadora_mensal') }} as score
