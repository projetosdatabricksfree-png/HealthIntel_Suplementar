{{
    config(
        materialized='view',
        tags=['bronze']
    )
}}

select *
from {{ source('bruto_ans', 'sib_beneficiario_operadora') }}
