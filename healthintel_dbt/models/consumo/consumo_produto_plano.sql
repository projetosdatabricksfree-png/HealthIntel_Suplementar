{{
    config(
        materialized='table',
        schema='consumo_ans',
        tags=['delta_ans_100', 'produto_plano', 'consumo'],
        post_hook="{{ grant_select_to_cliente_reader() }}"
    )
}}

select
    p.registro_ans,
    p.codigo_produto,
    p.nome_produto,
    p.segmentacao,
    p.tipo_contratacao,
    p.abrangencia_geografica,
    p.modalidade,
    p.uf_comercializacao,
    p.competencia,
    p.situacao_plano,
    p.data_situacao,
    p._carregado_em
from {{ ref('api_produto_plano') }} as p
