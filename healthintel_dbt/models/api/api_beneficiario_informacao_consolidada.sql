{{
    config(
        materialized='table',
        tags=['delta_ans_100', 'beneficiarios_cobertura'],
        post_hook=[
            "{{ criar_indice_api(this, 'competencia') }}",
            "{{ criar_indice_api(this, 'cd_municipio') }}",
            "{{ criar_indice_api(this, 'sg_uf') }}"
        ]
    )
}}

select
    competencia,
    sg_uf,
    cd_municipio,
    nm_municipio,
    segmentacao,
    tipo_contratacao,
    faixa_etaria,
    sexo,
    qt_beneficiarios,
    _carregado_em
from {{ ref('stg_beneficiario_informacao_consolidada') }}
