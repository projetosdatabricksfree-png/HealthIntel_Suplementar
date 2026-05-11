{{
    config(
        materialized='table',
        tags=['delta_ans_100', 'tuss_oficial'],
        post_hook=[
            "{{ criar_indice_api(this, 'codigo_tuss') }}",
            "{{ criar_indice_api(this, 'grupo') }}"
        ]
    )
}}

select
    codigo_tuss,
    descricao,
    versao_tuss,
    vigencia_inicio,
    vigencia_fim,
    is_tuss_vigente,
    grupo,
    subgrupo,
    _carregado_em
from {{ ref('stg_tuss_terminologia_oficial') }}
where is_tuss_vigente = true
