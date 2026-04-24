select *
from {{ ref('consumo_score_operadora_mes') }}
where score_total is not null
  and (score_total < 0 or score_total > 100)
