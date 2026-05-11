{{ config(tags=['delta_ans_100', 'regulatorios_complementares']) }}

with base as (
    select
        cast(
            nullif(regexp_replace(cast(competencia as text), '[^0-9]', '', 'g'), '')
            as integer
        )                                               as competencia,
        lpad(trim(coalesce(registro_ans, '')), 6, '0')  as registro_ans,
        upper(trim(coalesce(nu_processo, '')))          as nu_processo,
        upper(trim(coalesce(tipo_penalidade, '')))      as tipo_penalidade,
        upper(trim(coalesce(descricao_infracao, '')))   as descricao_infracao,
        cast(nullif(trim(cast(coalesce(vl_multa, '0') as text)), '') as numeric(18, 2))
                                                        as vl_multa,
        cast(nullif(trim(cast(data_penalidade as text)), '') as date)
                                                        as data_penalidade,
        upper(trim(coalesce(status_penalidade, '')))    as status_penalidade,
        _carregado_em,
        _arquivo_origem,
        _lote_id
    from {{ source('bruto_ans', 'penalidade_operadora') }}
    where trim(coalesce(registro_ans, '')) != ''
)

select *
from base
where competencia is not null
