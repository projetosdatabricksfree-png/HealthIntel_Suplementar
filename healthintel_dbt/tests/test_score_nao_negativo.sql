select *
from {{ ref('fat_score_operadora_mensal') }}
where score_final < 0
