{{
    config(
        materialized='table',
        schema='consumo_ans',
        tags=['delta_ans_100', 'tiss_subfamilias', 'consumo'],
        post_hook="{{ grant_select_to_cliente_reader() }}"
    )
}}

select
    'ambulatorial'    as tipo_tiss,
    competencia,
    registro_ans,
    sg_uf,
    tipo_evento,
    qt_eventos,
    vl_pago,
    vl_informado,
    null::integer     as qt_internacoes,
    null::integer     as qt_diarias,
    _carregado_em
from {{ ref('api_tiss_ambulatorial_operadora_mes') }}

union all

select
    'hospitalar'      as tipo_tiss,
    competencia,
    registro_ans,
    sg_uf,
    tipo_evento,
    null::integer     as qt_eventos,
    vl_pago,
    vl_informado,
    qt_internacoes,
    qt_diarias,
    _carregado_em
from {{ ref('api_tiss_hospitalar_operadora_mes') }}
