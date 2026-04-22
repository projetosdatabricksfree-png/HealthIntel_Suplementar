select *
from {{ ref('fat_financeiro_operadora_trimestral') }}
where coalesce(sinistralidade_bruta, 0) < 0
   or coalesce(sinistralidade_bruta, 0) > 2
