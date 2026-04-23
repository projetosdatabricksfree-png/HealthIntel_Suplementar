with competencias as (
    select distinct competencia from {{ ref('stg_sib_operadora') }}
    union
    select distinct competencia from {{ ref('stg_sib_municipio') }}
)

select
    competencia,
    {{ competencia_para_data("competencia") }} as competencia_data,
    extract(year from {{ competencia_para_data("competencia") }})::integer as ano,
    extract(month from {{ competencia_para_data("competencia") }})::integer as mes,
    to_char({{ competencia_para_data("competencia") }}, 'YYYY-MM') as competencia_label
from competencias
