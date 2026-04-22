select *
from {{ ref('fat_score_regulatorio_operadora_mensal') }}
where score_regulatorio < 0
   or score_regulatorio > 100
