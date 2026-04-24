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
    nome_fantasia,
    modalidade,
    uf_sede as uf,
    qt_beneficiarios,
    variacao_12m_pct,
    score_total,
    componente_core,
    componente_regulatorio,
    componente_financeiro,
    componente_rede,
    componente_estrutural,
    versao_metodologia
from {{ ref('mart_operadora_360') }}
