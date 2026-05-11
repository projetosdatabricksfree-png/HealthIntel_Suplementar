select
registro_ans,
competencia,
count(*) as total
from {{ ref('mart_operadora_360') }}
group by 1, 2
having count(*) > 1
