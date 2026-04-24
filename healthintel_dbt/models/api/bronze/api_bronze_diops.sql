{{
    config(
        materialized='view',
        tags=['bronze']
    )
}}

select *
from {{ source('bruto_ans', 'diops_operadora_trimestral') }}
