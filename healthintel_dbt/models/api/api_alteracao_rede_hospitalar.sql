{{
    config(
        materialized='table',
        tags=['delta_ans_100', 'rede_prestadores'],
        post_hook=[
            "{{ criar_indice_api(this, 'registro_ans') }}",
            "{{ criar_indice_api(this, 'competencia') }}",
            "{{ criar_indice_api(this, 'cnes') }}"
        ]
    )
}}

select
    competencia,
    registro_ans,
    nu_solicitacao,
    tipo_alteracao,
    cnes,
    nm_prestador,
    cd_municipio,
    sg_uf,
    data_solicitacao,
    status_solicitacao,
    _carregado_em
from {{ ref('stg_solicitacao_alteracao_rede_hospitalar') }}
