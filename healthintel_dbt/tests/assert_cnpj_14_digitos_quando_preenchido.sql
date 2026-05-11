{{ config(tags=['quality', 'documento']) }}

with documento as (
    select
'dq_cadop_documento' as modelo,
registro_ans as chave,
cnpj_normalizado
    from {{ ref('dq_cadop_documento') }}

    union all

    select
'dq_operadora_documento' as modelo,
registro_ans as chave,
cnpj_normalizado
    from {{ ref('dq_operadora_documento') }}

    union all

    select
'dq_cnes_documento' as modelo,
cnes as chave,
cnpj_normalizado
    from {{ ref('dq_cnes_documento') }}
)

select
    modelo,
    chave,
    cnpj_normalizado
from documento
where cnpj_normalizado is not null
  and length(cnpj_normalizado) <> 14
