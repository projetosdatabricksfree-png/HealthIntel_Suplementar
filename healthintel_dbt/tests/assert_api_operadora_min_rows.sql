{{ config(tags=['core_ans', 'api', 'operadora'], severity='error') }}

select count(*) as total
from {{ ref('api_operadora') }}
having count(*) = 0
