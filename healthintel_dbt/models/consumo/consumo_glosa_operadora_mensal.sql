{{
    config(
        materialized='table',
        schema='consumo_ans',
        tags=['core_ans', 'regulatorios_complementares', 'consumo'],
        post_hook="{{ grant_select_to_cliente_reader() }}"
    )
}}

select
    api.registro_ans,
    api.competencia,
    api.tipo_glosa,
    api.qt_glosa,
    api.valor_glosa,
    api.valor_faturado,
    api.taxa_glosa_calculada,
    api.fonte_publicacao,
    api.versao_dataset
from {{ ref('api_glosa_operadora_mensal') }} as api
