select
    registro_ans,
    competencia,
    count(*) as total_linhas
from {{ ref('api_score_operadora_mensal') }}
group by 1, 2
having count(*) > 1
