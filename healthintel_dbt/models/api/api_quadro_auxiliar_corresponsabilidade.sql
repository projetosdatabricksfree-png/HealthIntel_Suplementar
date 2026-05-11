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
    tipo_corresponsabilidade,
    percentual_corresponsabilidade,
    valor_corresponsabilidade,
    descricao,
    competencia,
    _carregado_em
from {{ ref('stg_quadro_auxiliar_corresponsabilidade') }}
order by registro_ans, codigo_plano
