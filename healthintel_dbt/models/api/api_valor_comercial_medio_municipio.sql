{{
    config(
        materialized='table',
        tags=['delta_ans_100', 'precificacao_ntrp'],
        post_hook=[
            "{{ criar_indice_api(this, 'cd_municipio') }}",
            "{{ criar_indice_api(this, 'competencia') }}",
            "{{ criar_indice_api(this, 'sg_uf') }}"
        ]
    )
}}

select
    competencia,
    cd_municipio,
    nm_municipio,
    sg_uf,
    segmentacao,
    faixa_etaria,
    vcm_municipio,
    qt_planos,
    _carregado_em
from {{ ref('stg_valor_comercial_medio_municipio') }}
