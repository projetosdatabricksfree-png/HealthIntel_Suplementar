{{
    config(
        materialized='table',
        schema='consumo_ans',
        tags=['delta_ans_100', 'regulatorios_complementares', 'consumo'],
        post_hook="{{ grant_select_to_cliente_reader() }}"
    )
}}

with iap as (
    select
        competencia,
        registro_ans,
        'IAP'                                           as tipo_indicador,
        dimensao                                        as categoria,
        indicador,
        valor_indicador,
        pontuacao                                       as score,
        _carregado_em
    from {{ ref('api_iap') }}
),

pfa as (
    select
        competencia,
        registro_ans,
        'PFA'                                           as tipo_indicador,
        null::text                                      as categoria,
        indicador,
        valor_indicador,
        null::numeric(5, 2)                             as score,
        _carregado_em
    from {{ ref('api_pfa') }}
)

select * from iap
union all
select * from pfa
