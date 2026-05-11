{{
    config(
        materialized='table',
        schema='consumo_ans',
        tags=['delta_ans_100', 'produto_plano', 'consumo'],
        post_hook="{{ grant_select_to_cliente_reader() }}"
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
from {{ ref('api_plano_servico_opcional') }}
