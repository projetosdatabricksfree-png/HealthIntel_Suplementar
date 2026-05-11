{{ config(tags=['delta_ans_100', 'regulatorios_complementares']) }}

with base as (
    select
        cast(
            nullif(regexp_replace(cast(competencia as text), '[^0-9]', '', 'g'), '')
            as integer
        )                                               as competencia,
        lpad(trim(coalesce(registro_ans, '')), 6, '0')  as registro_ans,
        upper(trim(coalesce(dimensao, '')))              as dimensao,
        upper(trim(coalesce(indicador, '')))             as indicador,
        cast(nullif(trim(cast(coalesce(valor_indicador, '0') as text)), '') as numeric(10, 4))
                                                         as valor_indicador,
        cast(nullif(trim(cast(coalesce(peso_indicador, '0') as text)), '') as numeric(5, 2))
                                                         as peso_indicador,
        cast(nullif(trim(cast(coalesce(pontuacao, '0') as text)), '') as numeric(5, 2))
                                                         as pontuacao,
        _carregado_em,
        _arquivo_origem,
        _lote_id
    from {{ source('bruto_ans', 'iap') }}
    where trim(coalesce(registro_ans, '')) != ''
)

select *
from base
where competencia is not null
