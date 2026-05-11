{{
    config(
        materialized='table',
        tags=['delta_ans_100', 'sip'],
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
    cd_municipio,
    nm_municipio,
    sg_uf,
    nm_regiao,
    tipo_assistencial,
    sum(qt_beneficiarios) as qt_beneficiarios,
    sum(qt_eventos)       as qt_eventos,
    avg(indicador_cobertura) as indicador_cobertura_medio,
    max(_carregado_em)    as _carregado_em
from {{ ref('stg_sip_mapa_assistencial') }}
group by
    competencia,
    registro_ans,
    cd_municipio,
    nm_municipio,
    sg_uf,
    nm_regiao,
    tipo_assistencial
