select
    registro_ans,
    trimestre,
    count(*) as quantidade
from {{ ref('api_regulatorio_operadora_trimestral') }}
group by registro_ans, trimestre
having count(*) > 1
