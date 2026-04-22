select *
from {{ ref('fat_financeiro_operadora_trimestral') }}
where coalesce(sinistro_total, 0) < 0
   or coalesce(contraprestacao_total, 0) < 0
   or coalesce(provisao_tecnica, 0) < 0
