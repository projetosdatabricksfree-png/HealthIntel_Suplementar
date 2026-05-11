{{ config(tags=['delta_ans_100', 'precificacao_ntrp']) }}

with base as (
    select
        cast(
            nullif(regexp_replace(cast(competencia as text), '[^0-9]', '', 'g'), '')
            as integer
        )                                               as competencia,
        lpad(regexp_replace(cast(coalesce(cd_municipio, '') as text), '[^0-9]', '', 'g'), 7, '0')
                                                        as cd_municipio,
        upper(trim(coalesce(nm_municipio, '')))         as nm_municipio,
        upper(trim(coalesce(sg_uf, '')))                as sg_uf,
        upper(trim(coalesce(segmentacao, '')))          as segmentacao,
        upper(trim(coalesce(faixa_etaria, '')))         as faixa_etaria,
        cast(nullif(trim(cast(coalesce(vcm_municipio, '0') as text)), '') as numeric(18, 2))
                                                        as vcm_municipio,
        coalesce(cast(nullif(trim(cast(qt_planos as text)), '') as integer), 0)
                                                        as qt_planos,
        _carregado_em,
        _arquivo_origem,
        _lote_id
    from {{ source('bruto_ans', 'valor_comercial_medio_municipio') }}
)

select *
from base
where competencia is not null
  and cd_municipio != '0000000'
