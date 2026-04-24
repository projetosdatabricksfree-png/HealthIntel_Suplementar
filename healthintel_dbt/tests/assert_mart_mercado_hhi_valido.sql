select *
from {{ ref('mart_mercado_municipio') }}
where hhi is not null
  and (hhi < 0 or hhi > 10000)
