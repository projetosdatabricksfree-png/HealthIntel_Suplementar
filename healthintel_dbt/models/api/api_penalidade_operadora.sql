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
    nu_processo,
    tipo_penalidade,
    descricao_infracao,
    vl_multa,
    data_penalidade,
    status_penalidade,
    _carregado_em
from {{ ref('stg_penalidade_operadora') }}
