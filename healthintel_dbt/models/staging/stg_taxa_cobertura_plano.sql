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
        coalesce(cast(nullif(trim(cast(populacao_total as text)), '') as integer), 0)
                                                        as populacao_total,
        coalesce(cast(nullif(trim(cast(qt_beneficiarios as text)), '') as integer), 0)
                                                        as qt_beneficiarios,
        cast(nullif(trim(cast(coalesce(taxa_cobertura, '0') as text)), '') as numeric(10, 4))
                                                        as taxa_cobertura,
        _carregado_em,
        _arquivo_origem,
        _lote_id
    from {{ source('bruto_ans', 'taxa_cobertura_plano') }}
)

select *
from base
where competencia is not null
  and cd_municipio != '0000000'
