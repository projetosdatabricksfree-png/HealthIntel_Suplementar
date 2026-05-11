{{ config(tags=['delta_ans_100', 'ressarcimento_sus']) }}

with base as (
    select
        cast(
            nullif(regexp_replace(cast(competencia as text), '[^0-9]', '', 'g'), '')
            as integer
        )                                               as competencia,
        lpad(trim(coalesce(registro_ans, '')), 6, '0')  as registro_ans,
        upper(trim(coalesce(nu_hc, '')))                as nu_hc,
        cast(nullif(trim(cast(coalesce(vl_hc, '0') as text)), '') as numeric(18, 2))
                                                        as vl_hc,
        upper(trim(coalesce(status_hc, '')))            as status_hc,
        upper(trim(coalesce(fase_cobranca, '')))        as fase_cobranca,
        _carregado_em,
        _arquivo_origem,
        _lote_id
    from {{ source('bruto_ans', 'ressarcimento_hc') }}
    where trim(coalesce(registro_ans, '')) != ''
)

select *
from base
where competencia is not null
