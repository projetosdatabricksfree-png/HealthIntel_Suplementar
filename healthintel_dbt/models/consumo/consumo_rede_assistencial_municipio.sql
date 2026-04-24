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
    registro_ans,
    razao_social,
    segmento,
    qt_prestadores,
    densidade_por_10k,
    gap_leitos_cnes,
    classificacao_vazio
from {{ ref('mart_rede_assistencial') }}
