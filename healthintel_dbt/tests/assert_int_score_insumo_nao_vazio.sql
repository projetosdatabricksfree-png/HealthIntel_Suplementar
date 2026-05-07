{{ config(
    tags=['core_ans', 'sib', 'score'],
    severity='error' if target.name == 'prod' else 'warn'
) }}

select count(*) as total
from {{ ref('int_score_insumo') }}
having count(*) = 0
