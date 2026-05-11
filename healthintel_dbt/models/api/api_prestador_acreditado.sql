{{
    config(
        materialized='table',
        tags=['delta_ans_100', 'rede_prestadores'],
        post_hook=[
            "{{ criar_indice_api(this, 'cnes') }}",
            "{{ criar_indice_api(this, 'cd_municipio') }}",
            "{{ criar_indice_api(this, 'sg_uf') }}"
        ]
    )
}}

select
    cnes,
    nm_prestador,
    cnpj,
    cd_municipio,
    nm_municipio,
    sg_uf,
    acreditadora,
    nivel_acreditacao,
    data_acreditacao,
    data_validade,
    _carregado_em
from {{ ref('stg_prestador_acreditado') }}
