{{
    config(
        materialized='table',
        tags=['delta_ans_100', 'precificacao_ntrp'],
        post_hook=[
            "{{ criar_indice_api(this, 'registro_ans') }}",
            "{{ criar_indice_api(this, 'sg_uf') }}",
            "{{ criar_indice_api(this, 'competencia') }}"
        ]
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
from {{ ref('stg_painel_precificacao') }}
