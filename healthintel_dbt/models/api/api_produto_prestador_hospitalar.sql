{{
    config(
        materialized='table',
        tags=['delta_ans_100', 'rede_prestadores'],
        post_hook=[
            "{{ criar_indice_api(this, 'registro_ans') }}",
            "{{ criar_indice_api(this, 'cnes') }}",
            "{{ criar_indice_api(this, 'cd_municipio') }}"
        ]
    )
}}

select
    competencia,
    registro_ans,
    codigo_produto,
    cnes,
    nm_prestador,
    cd_municipio,
    sg_uf,
    tipo_vinculo,
    _carregado_em
from {{ ref('stg_produto_prestador_hospitalar') }}
