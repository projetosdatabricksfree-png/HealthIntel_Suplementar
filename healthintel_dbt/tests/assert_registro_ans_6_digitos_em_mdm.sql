{{ config(tags=['quality', 'documento', 'mdm']) }}

with registro as (
    select
'dq_operadora_documento' as modelo,
registro_ans,
registro_ans_formato_valido
    from {{ ref('dq_operadora_documento') }}

    union all

    select
'dq_prestador_documento' as modelo,
registro_ans,
registro_ans_formato_valido
    from {{ ref('dq_prestador_documento') }}
)

select
    modelo,
    registro_ans
from registro
where not registro_ans_formato_valido
