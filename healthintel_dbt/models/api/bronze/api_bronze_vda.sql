{{
    config(
        materialized='view',
        tags=['bronze']
    )
}}

select *
from {{ source('bruto_ans', 'vda_operadora_mensal') }}
