{{ config(materialized='table', schema='consumo_ans', tags=['consumo']) }}

select
    registro_ans,
    razao_social,
    modalidade,
    competencia,
    score_total,
    faixa_score,
    cast(null as integer) as posicao_geral,
    cast(null as integer) as posicao_por_modalidade,
    componente_core,
    componente_regulatorio,
    componente_financeiro,
    componente_rede,
    componente_estrutural,
    cast(null as numeric) as variacao_score_mom
from {{ ref('mart_score_operadora') }}
