{{
    config(
        materialized='table',
        tags=['delta_ans_100', 'produto_plano'],
        post_hook=[
            "{{ criar_indice_api(this, 'registro_ans') }}",
            "{{ criar_indice_api(this, 'codigo_plano') }}"
        ]
    )
}}

select
    registro_ans,
    codigo_plano,
    codigo_servico,
    descricao_servico,
    tipo_servico,
    competencia,
    _carregado_em
from {{ ref('stg_plano_servico_opcional') }}
order by registro_ans, codigo_plano, codigo_servico
