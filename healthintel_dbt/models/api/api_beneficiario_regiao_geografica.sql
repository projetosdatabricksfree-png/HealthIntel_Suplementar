{{
    config(
        materialized='table',
        tags=['delta_ans_100', 'beneficiarios_cobertura'],
        post_hook=[
            "{{ criar_indice_api(this, 'competencia') }}",
            "{{ criar_indice_api(this, 'sg_uf') }}"
        ]
    )
}}

select
    competencia,
    cd_regiao,
    nm_regiao,
    sg_uf,
    tipo_plano,
    segmentacao,
    sum(qt_beneficiarios)                               as qt_beneficiarios,
    max(_carregado_em)                                  as _carregado_em
from {{ ref('stg_beneficiario_regiao_geografica') }}
group by competencia, cd_regiao, nm_regiao, sg_uf, tipo_plano, segmentacao
