{{
    config(
        materialized='table',
        schema='consumo_ans',
        tags=['delta_ans_100', 'tuss_oficial', 'consumo'],
        post_hook="{{ grant_select_to_cliente_reader() }}"
    )
}}

select
    codigo_tuss,
    descricao,
    versao_tuss,
    vigencia_inicio,
    grupo,
    subgrupo
from {{ ref('api_tuss_procedimento_vigente') }}
order by codigo_tuss
