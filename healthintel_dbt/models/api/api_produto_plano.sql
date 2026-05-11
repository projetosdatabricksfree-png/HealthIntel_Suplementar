{{
    config(
        materialized='table',
        tags=['delta_ans_100', 'produto_plano'],
        post_hook=[
            "{{ criar_indice_api(this, 'registro_ans') }}",
            "{{ criar_indice_api(this, 'codigo_produto') }}",
            "{{ criar_indice_api(this, 'segmentacao') }}"
        ]
    )
}}

with produto as (
    select * from {{ ref('stg_produto_caracteristica') }}
),

historico as (
    select
        registro_ans,
        codigo_plano,
        situacao,
        data_situacao,
        segmentacao,
        competencia as competencia_historico
    from {{ ref('stg_historico_plano') }}
)

select
    p.registro_ans,
    p.codigo_produto,
    p.nome_produto,
    p.segmentacao,
    p.tipo_contratacao,
    p.abrangencia_geografica,
    p.cobertura_area,
    p.modalidade,
    p.uf_comercializacao,
    p.competencia,
    h.codigo_plano,
    h.situacao as situacao_plano,
    h.data_situacao,
    h.competencia_historico,
    p._carregado_em
from produto as p
left join historico as h
    on p.registro_ans = h.registro_ans
    and p.codigo_produto = h.codigo_plano
