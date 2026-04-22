select
    operadora_id,
    competencia,
    count(*) as total_linhas
from {{ ref('fat_score_operadora_mensal') }}
group by 1, 2
having count(*) > 1
