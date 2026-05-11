{{
    config(
        materialized='table',
        tags=['delta_ans_100', 'produto_plano'],
        post_hook=[
            "{{ criar_indice_api(this, 'registro_ans') }}",
            "{{ criar_indice_api(this, 'codigo_plano') }}",
            "{{ criar_indice_api(this, 'competencia') }}"
        ]
    )
}}

select
    h.registro_ans,
    h.codigo_plano,
    h.nome_plano,
    h.situacao,
    h.data_situacao,
    h.segmentacao,
    h.tipo_contratacao,
    h.abrangencia_geografica,
    h.uf,
    h.competencia,
    h._carregado_em
from {{ ref('stg_historico_plano') }} as h
order by h.registro_ans, h.competencia desc
