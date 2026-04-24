{{
    config(
        materialized='view',
        tags=['bronze']
    )
}}

select *
from {{ source('bruto_ans', 'nip_operadora_trimestral') }}
