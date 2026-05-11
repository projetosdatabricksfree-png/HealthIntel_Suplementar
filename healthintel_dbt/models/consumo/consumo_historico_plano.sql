{{
    config(
        materialized='table',
        schema='consumo_ans',
        tags=['delta_ans_100', 'produto_plano', 'consumo'],
        post_hook="{{ grant_select_to_cliente_reader() }}"
    )
}}

select
    registro_ans,
    codigo_plano,
    nome_plano,
    situacao,
    data_situacao,
    segmentacao,
    tipo_contratacao,
    abrangencia_geografica,
    uf,
    competencia,
    _carregado_em
from {{ ref('api_historico_plano') }}
