{{ config(materialized='view', schema='stg_ans', tags=['staging', 'generico']) }}

select
    dataset_codigo,
    familia,
    url,
    arquivo_origem,
    hash_arquivo,
    caminho_landing,
    tipo_arquivo,
    tamanho_bytes,
    status_parser,
    data_ingestao
from {{ source('bruto_ans', 'ans_arquivo_generico') }}
