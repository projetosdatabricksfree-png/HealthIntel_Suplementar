{{
    config(
        materialized='table',
        schema='consumo_ans',
        tags=['consumo'],
        post_hook="{{ grant_select_to_cliente_reader() }}"
    )
}}

select
    competencia,
    registro_ans,
    razao_social,
    modalidade,
    score_total,
    faixa_score,
    componente_core,
    componente_regulatorio,
    componente_financeiro,
    componente_rede,
    componente_estrutural,
    versao_metodologia
from {{ ref('mart_score_operadora') }}
