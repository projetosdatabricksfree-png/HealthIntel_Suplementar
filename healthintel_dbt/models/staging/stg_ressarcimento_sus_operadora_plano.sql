{{
    config(
        tags=['delta_ans_100', 'ressarcimento_sus']
    )
}}

with base as (
    select
        cast(
            nullif(regexp_replace(cast(competencia as text), '[^0-9]', '', 'g'), '')
            as integer
        )                                               as competencia,
        lpad(trim(coalesce(registro_ans, '')), 6, '0')  as registro_ans,
        trim(coalesce(codigo_plano, ''))                 as codigo_plano,
        coalesce(cast(nullif(trim(cast(qt_autorizacoes as text)), '') as integer), 0)
                                                         as qt_autorizacoes,
        cast(nullif(trim(cast(coalesce(vl_cobrado, '0') as text)), '') as numeric(18, 2))
                                                         as vl_cobrado,
        cast(nullif(trim(cast(coalesce(vl_pago, '0') as text)), '') as numeric(18, 2))
                                                         as vl_pago,
        cast(nullif(trim(cast(coalesce(vl_pendente, '0') as text)), '') as numeric(18, 2))
                                                         as vl_pendente,
        upper(trim(coalesce(status_cobranca, '')))       as status_cobranca,
        _carregado_em,
        _arquivo_origem,
        _lote_id
    from {{ source('bruto_ans', 'ressarcimento_sus_operadora_plano') }}
    where trim(coalesce(registro_ans, '')) != ''
)

select *
from base
where competencia is not null
