{{
    config(
        tags=['delta_ans_100', 'precificacao_ntrp']
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
        upper(trim(coalesce(faixa_etaria, '')))          as faixa_etaria,
        upper(trim(coalesce(sg_uf, '')))                 as sg_uf,
        upper(trim(coalesce(tipo_contratacao, '')))      as tipo_contratacao,
        cast(nullif(trim(cast(coalesce(vl_mensalidade_media, '0') as text)), '') as numeric(18, 2))
                                                         as vl_mensalidade_media,
        cast(nullif(trim(cast(coalesce(vl_mensalidade_min, '0') as text)), '') as numeric(18, 2))
                                                         as vl_mensalidade_min,
        cast(nullif(trim(cast(coalesce(vl_mensalidade_max, '0') as text)), '') as numeric(18, 2))
                                                         as vl_mensalidade_max,
        coalesce(cast(nullif(trim(cast(qt_beneficiarios as text)), '') as integer), 0)
                                                         as qt_beneficiarios,
        _carregado_em,
        _arquivo_origem,
        _lote_id
    from {{ source('bruto_ans', 'painel_precificacao') }}
    where trim(coalesce(registro_ans, '')) != ''
)

select *
from base
where competencia is not null
