{{ config(materialized='view', schema='stg_ans', tags=['staging', 'generico']) }}

select
    dataset_codigo,
    familia,
    arquivo_origem,
    hash_arquivo,
    linha_origem,
    dados,
    data_ingestao
from {{ source('bruto_ans', 'ans_linha_generica') }}
