{{
    config(
        materialized='table',
        schema='consumo_ans',
        tags=['delta_ans_100', 'beneficiarios_cobertura', 'consumo'],
        post_hook="{{ grant_select_to_cliente_reader() }}"
    )
}}

select
    competencia,
    sg_uf,
    cd_municipio,
    nm_municipio,
    populacao_total,
    qt_beneficiarios,
    taxa_cobertura,
    _carregado_em
from {{ ref('api_taxa_cobertura_plano') }}
