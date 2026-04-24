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
    cd_municipio,
    nome_municipio as municipio,
    uf,
    qt_beneficiarios_total as qt_beneficiarios,
    qt_operadoras_ativas as qt_operadoras,
    hhi,
    score_oportunidade,
    populacao_alvo,
    operadora_dominante
from {{ ref('mart_mercado_municipio') }}
