{{
    config(
        materialized='table',
        tags=['delta_ans_100', 'ressarcimento_sus'],
        post_hook=[
            "{{ criar_indice_api(this, 'registro_ans') }}",
            "{{ criar_indice_api(this, 'competencia') }}",
            "{{ criar_indice_api(this, 'cd_municipio') }}"
        ]
    )
}}

select
    competencia,
    registro_ans,
    nu_abi,
    cd_municipio,
    nm_municipio,
    sg_uf,
    qt_beneficiarios,
    vl_ressarcimento,
    status_ressarcimento,
    _carregado_em
from {{ ref('stg_ressarcimento_beneficiario_abi') }}
