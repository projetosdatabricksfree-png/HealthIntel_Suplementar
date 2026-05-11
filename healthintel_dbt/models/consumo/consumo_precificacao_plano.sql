{{
    config(
        materialized='table',
        schema='consumo_ans',
        tags=['delta_ans_100', 'precificacao_ntrp', 'consumo'],
        post_hook="{{ grant_select_to_cliente_reader() }}"
    )
}}

select
    competencia,
    registro_ans,
    codigo_plano,
    segmentacao,
    faixa_etaria,
    sg_uf,
    tipo_contratacao,
    vl_mensalidade_media,
    vl_mensalidade_min,
    vl_mensalidade_max,
    qt_beneficiarios,
    _carregado_em
from {{ ref('api_painel_precificacao') }}
