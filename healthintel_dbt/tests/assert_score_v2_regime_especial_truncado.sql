{{ config(tags=['score_v2']) }}

select
    s.*
from {{ ref('fat_score_v2_operadora_mensal') }} as s
inner join {{ ref('fat_score_regulatorio_operadora_mensal') }} as r
    on r.registro_ans = s.registro_ans
    and r.competencia = s.competencia
where r.regime_especial_ativo = true
  and r.score_regulatorio > 39.99
