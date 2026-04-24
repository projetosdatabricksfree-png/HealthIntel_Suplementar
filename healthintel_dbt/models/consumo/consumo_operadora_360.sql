{{ config(materialized='table', schema='consumo_ans', tags=['consumo']) }}

select *
from {{ ref('mart_operadora_360') }}
