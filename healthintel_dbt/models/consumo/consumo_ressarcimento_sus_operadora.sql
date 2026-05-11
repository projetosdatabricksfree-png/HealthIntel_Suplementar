{{
    config(
        materialized='table',
        schema='consumo_ans',
        tags=['delta_ans_100', 'ressarcimento_sus', 'consumo'],
        post_hook="{{ grant_select_to_cliente_reader() }}"
    )
}}

select
    competencia,
    registro_ans,
    sum(qt_autorizacoes) as qt_autorizacoes_total,
    sum(vl_cobrado)      as vl_cobrado_total,
    sum(vl_pago)         as vl_pago_total,
    sum(vl_pendente)     as vl_pendente_total
from {{ ref('api_ressarcimento_sus_operadora_plano') }}
group by competencia, registro_ans
