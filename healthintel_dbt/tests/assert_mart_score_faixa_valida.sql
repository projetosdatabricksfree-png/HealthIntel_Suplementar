select *
from {{ ref('mart_score_operadora') }}
where score_total is not null
  and (score_total < 0 or score_total > 100)
