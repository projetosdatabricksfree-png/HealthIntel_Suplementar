{{ config(
    tags=['core_ans', 'sib', 'mercado'],
    severity='error' if target.name == 'prod' else 'warn'
) }}

select count(*) as total
from {{ ref('int_metrica_municipio') }}
having count(*) = 0
