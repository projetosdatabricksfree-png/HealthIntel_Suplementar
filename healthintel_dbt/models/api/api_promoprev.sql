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
    tipo_programa,
    qt_beneficiarios_programa,
    vl_investimento,
    indicador_participacao,
    _carregado_em
from {{ ref('stg_promoprev') }}
