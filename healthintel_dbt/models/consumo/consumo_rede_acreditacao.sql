{{
    config(
        materialized='table',
        schema='consumo_ans',
        tags=['delta_ans_100', 'rede_prestadores', 'consumo'],
        post_hook="{{ grant_select_to_cliente_reader() }}"
    )
}}

select
    'operadora'                                         as tipo_acreditado,
    registro_ans,
    null::varchar(7)                                    as cnes,
    null::text                                          as nm_prestador,
    acreditadora,
    nivel_acreditacao,
    data_acreditacao,
    data_validade,
    _carregado_em
from {{ ref('api_operadora_acreditada') }}

union all

select
    'prestador'                                         as tipo_acreditado,
    null::varchar(6)                                    as registro_ans,
    cnes,
    nm_prestador,
    acreditadora,
    nivel_acreditacao,
    data_acreditacao,
    data_validade,
    _carregado_em
from {{ ref('api_prestador_acreditado') }}
