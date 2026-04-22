select *
from {{ ref('api_rn623_lista_trimestral') }}
where tipo_lista not in ('excelencia', 'reducao')
