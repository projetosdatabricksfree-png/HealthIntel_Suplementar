{{ config(tags=['delta_ans_100', 'precificacao_ntrp']) }}

with base as (
    select
        cast(
            nullif(regexp_replace(cast(competencia as text), '[^0-9]', '', 'g'), '')
            as integer
        )                                               as competencia,
        lpad(trim(coalesce(registro_ans, '')), 6, '0')  as registro_ans,
        upper(trim(coalesce(tipo_contratacao, '')))     as tipo_contratacao,
        upper(trim(coalesce(agrupamento, '')))          as agrupamento,
        cast(nullif(trim(cast(coalesce(percentual_reajuste, '0') as text)), '') as numeric(10, 4))
                                                        as percentual_reajuste,
        cast(nullif(trim(cast(data_aplicacao as text)), '') as date)
                                                        as data_aplicacao,
        _carregado_em,
        _arquivo_origem,
        _lote_id
    from {{ source('bruto_ans', 'percentual_reajuste_agrupamento') }}
    where trim(coalesce(registro_ans, '')) != ''
)

select *
from base
where competencia is not null
