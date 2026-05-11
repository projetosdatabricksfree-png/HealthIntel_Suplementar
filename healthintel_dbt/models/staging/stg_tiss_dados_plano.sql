{{
    config(
        tags=['delta_ans_100', 'tiss_subfamilias']
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
        upper(trim(coalesce(segmentacao, '')))           as segmentacao,
        upper(trim(coalesce(tipo_contratacao, '')))      as tipo_contratacao,
        coalesce(cast(nullif(trim(cast(qt_beneficiarios as text)), '') as integer), 0)
                                                         as qt_beneficiarios,
        coalesce(cast(nullif(trim(cast(qt_eventos as text)), '') as integer), 0)
                                                         as qt_eventos,
        cast(nullif(trim(cast(coalesce(vl_pago, '0') as text)), '') as numeric(18, 2))
                                                         as vl_pago,
        _carregado_em,
        _arquivo_origem,
        _lote_id
    from {{ source('bruto_ans', 'tiss_dados_plano') }}
    where trim(coalesce(registro_ans, '')) != ''
)

select *
from base
where competencia is not null
