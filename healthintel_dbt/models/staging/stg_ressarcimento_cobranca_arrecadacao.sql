{{ config(tags=['delta_ans_100', 'ressarcimento_sus']) }}

with base as (
    select
        cast(
            nullif(regexp_replace(cast(competencia as text), '[^0-9]', '', 'g'), '')
            as integer
        )                                               as competencia,
        lpad(trim(coalesce(registro_ans, '')), 6, '0')  as registro_ans,
        cast(nullif(trim(cast(coalesce(vl_cobrado, '0') as text)), '') as numeric(18, 2))
                                                        as vl_cobrado,
        cast(nullif(trim(cast(coalesce(vl_arrecadado, '0') as text)), '') as numeric(18, 2))
                                                        as vl_arrecadado,
        cast(nullif(trim(cast(coalesce(vl_inadimplente, '0') as text)), '') as numeric(18, 2))
                                                        as vl_inadimplente,
        coalesce(cast(nullif(trim(cast(qt_guias as text)), '') as integer), 0)
                                                        as qt_guias,
        _carregado_em,
        _arquivo_origem,
        _lote_id
    from {{ source('bruto_ans', 'ressarcimento_cobranca_arrecadacao') }}
    where trim(coalesce(registro_ans, '')) != ''
)

select *
from base
where competencia is not null
