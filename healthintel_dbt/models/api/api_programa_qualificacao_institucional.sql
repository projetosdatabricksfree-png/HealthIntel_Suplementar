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
    nivel_qualificacao,
    pontuacao_qualificacao,
    data_avaliacao,
    status_qualificacao,
    _carregado_em
from {{ ref('stg_programa_qualificacao_institucional') }}
