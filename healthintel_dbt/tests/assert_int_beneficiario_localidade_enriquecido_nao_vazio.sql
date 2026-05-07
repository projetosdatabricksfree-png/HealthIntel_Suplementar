{{ config(
    tags=['core_ans', 'sib', 'mercado'],
    severity='error' if target.name == 'prod' else 'warn'
) }}

select count(*) as total
from {{ ref('int_beneficiario_localidade_enriquecido') }}
having count(*) = 0
