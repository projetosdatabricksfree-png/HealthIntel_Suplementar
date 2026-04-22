select *
from {{ ref('stg_cadop') }}
where length(registro_ans) <> 6
   or registro_ans !~ '^[0-9]{6}$'
