select *
from {{ ref('fat_score_regulatorio_operadora_mensal') }}
where regime_especial_ativo = true
  and score_regulatorio > 39.99
