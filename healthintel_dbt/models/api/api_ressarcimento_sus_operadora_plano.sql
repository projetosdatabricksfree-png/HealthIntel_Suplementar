{{
    config(
        materialized='table',
        tags=['delta_ans_100', 'ressarcimento_sus'],
        post_hook=[
            "{{ criar_indice_api(this, 'registro_ans') }}",
            "{{ criar_indice_api(this, 'competencia') }}"
        ]
    )
}}

select
    competencia,
    registro_ans,
    codigo_plano,
    sum(qt_autorizacoes) as qt_autorizacoes,
    sum(vl_cobrado)      as vl_cobrado,
    sum(vl_pago)         as vl_pago,
    sum(vl_pendente)     as vl_pendente,
    max(status_cobranca) as status_cobranca,
    max(_carregado_em)   as _carregado_em
from {{ ref('stg_ressarcimento_sus_operadora_plano') }}
group by
    competencia,
    registro_ans,
    codigo_plano
