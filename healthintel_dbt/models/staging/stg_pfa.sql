{{ config(tags=['delta_ans_100', 'regulatorios_complementares']) }}

with base as (
    select
        cast(
            nullif(regexp_replace(cast(competencia as text), '[^0-9]', '', 'g'), '')
            as integer
        )                                               as competencia,
        lpad(trim(coalesce(registro_ans, '')), 6, '0')  as registro_ans,
        upper(trim(coalesce(indicador, '')))             as indicador,
        cast(nullif(trim(cast(coalesce(valor_indicador, '0') as text)), '') as numeric(18, 4))
                                                         as valor_indicador,
        cast(nullif(trim(cast(coalesce(meta, '0') as text)), '') as numeric(18, 4))
                                                         as meta,
        upper(trim(coalesce(status_meta, '')))           as status_meta,
        _carregado_em,
        _arquivo_origem,
        _lote_id
    from {{ source('bruto_ans', 'pfa') }}
    where trim(coalesce(registro_ans, '')) != ''
)

select *
from base
where competencia is not null
