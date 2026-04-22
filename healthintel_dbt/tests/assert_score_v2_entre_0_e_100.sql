{{ config(tags=['score_v2']) }}

select *
from {{ ref('fat_score_v2_operadora_mensal') }}
where score_v2 < 0
   or score_v2 > 100
