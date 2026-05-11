{{
    config(
        materialized='table',
        tags=['delta_ans_100', 'precificacao_ntrp'],
        post_hook=[
            "{{ criar_indice_api(this, 'registro_ans') }}",
            "{{ criar_indice_api(this, 'cd_municipio') }}"
        ]
    )
}}

select
    competencia,
    registro_ans,
    codigo_plano,
    cd_municipio,
    nm_municipio,
    sg_uf,
    area_comercializacao,
    _carregado_em
from {{ ref('stg_ntrp_area_comercializacao') }}
