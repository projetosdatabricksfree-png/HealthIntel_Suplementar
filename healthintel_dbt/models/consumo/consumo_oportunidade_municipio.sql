{{ config(materialized='table', schema='consumo_ans', tags=['consumo']) }}

select
    cd_municipio,
    nome_municipio,
    uf,
    competencia,
    qt_beneficiarios_total,
    cast(null as numeric) as penetracao_pct,
    score_oportunidade,
    qt_operadoras_ativas,
    hhi,
    operadora_dominante
from {{ ref('mart_mercado_municipio') }}
