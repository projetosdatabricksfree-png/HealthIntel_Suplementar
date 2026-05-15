{{
    config(
        materialized='table',
        schema='consumo_ans',
        tags=['consumo'],
        post_hook="{{ grant_select_to_cliente_reader() }}"
    )
}}

select
    ano_base,
    registro_ans,
    idss_total,
    idqs,
    idga,
    idsm,
    idgr,
    faixa_idss,
    versao_metodologia,
    _carregado_em
from {{ ref('api_prata_idss') }}
