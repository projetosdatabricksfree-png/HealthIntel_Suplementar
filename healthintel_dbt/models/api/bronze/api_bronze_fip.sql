{{
    config(
        materialized='view',
        tags=['bronze']
    )
}}

select *
from {{ source('bruto_ans', 'fip_operadora_trimestral') }}
