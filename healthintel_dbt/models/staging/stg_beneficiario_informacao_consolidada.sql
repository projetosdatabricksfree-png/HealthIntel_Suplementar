{{ config(tags=['delta_ans_100', 'beneficiarios_cobertura']) }}

with base as (
    select
        cast(
            nullif(regexp_replace(cast(competencia as text), '[^0-9]', '', 'g'), '')
            as integer
        )                                               as competencia,
        upper(trim(coalesce(sg_uf, '')))                as sg_uf,
        lpad(regexp_replace(cast(coalesce(cd_municipio, '') as text), '[^0-9]', '', 'g'), 7, '0')
                                                        as cd_municipio,
        upper(trim(coalesce(nm_municipio, '')))         as nm_municipio,
        upper(trim(coalesce(segmentacao, '')))          as segmentacao,
        upper(trim(coalesce(tipo_contratacao, '')))     as tipo_contratacao,
        upper(trim(coalesce(faixa_etaria, '')))         as faixa_etaria,
        upper(trim(coalesce(sexo, '')))                 as sexo,
        coalesce(cast(nullif(trim(cast(qt_beneficiarios as text)), '') as integer), 0)
                                                        as qt_beneficiarios,
        _carregado_em,
        _arquivo_origem,
        _lote_id
    from {{ source('bruto_ans', 'beneficiario_informacao_consolidada') }}
)

select *
from base
where competencia is not null
  and cd_municipio != '0000000'
