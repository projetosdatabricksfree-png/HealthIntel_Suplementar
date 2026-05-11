{{
    config(
        materialized='table',
        tags=['delta_ans_100', 'regulatorios_complementares'],
        post_hook=[
            "{{ criar_indice_api(this, 'registro_ans') }}",
            "{{ criar_indice_api(this, 'competencia') }}"
        ]
    )
}}

select
    competencia,
    registro_ans,
    vl_peona,
    qt_beneficiarios_sus,
    indicador_utilizacao_sus,
    sg_uf,
    _carregado_em
from {{ ref('stg_peona_sus') }}
