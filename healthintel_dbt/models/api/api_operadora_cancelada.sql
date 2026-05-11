{{
    config(
        materialized='table',
        tags=['delta_ans_100', 'rede_prestadores'],
        post_hook=[
            "{{ criar_indice_api(this, 'registro_ans') }}",
            "{{ criar_indice_api(this, 'sg_uf') }}"
        ]
    )
}}

select
    registro_ans,
    razao_social,
    cnpj,
    modalidade,
    data_cancelamento,
    motivo_cancelamento,
    sg_uf,
    _carregado_em
from {{ ref('stg_operadora_cancelada') }}
