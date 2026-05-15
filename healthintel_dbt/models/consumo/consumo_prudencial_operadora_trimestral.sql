{{
    config(
        materialized='table',
        schema='consumo_ans',
        tags=['core_ans', 'regulatorios_complementares', 'consumo'],
        post_hook="{{ grant_select_to_cliente_reader() }}"
    )
}}

select
    api.registro_ans,
    api.trimestre,
    api.margem_solvencia,
    api.capital_minimo_requerido,
    api.capital_disponivel,
    api.indice_liquidez,
    api.situacao_prudencial,
    api.situacao_inadequada,
    api.fonte_publicacao,
    api.versao_dataset
from {{ ref('api_prudencial_operadora_trimestral') }} as api
