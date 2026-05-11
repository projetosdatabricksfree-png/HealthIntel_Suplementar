{{
    config(
        tags=['delta_ans_100', 'sip']
    )
}}

with base as (
    select
        cast(
            nullif(regexp_replace(cast(competencia as text), '[^0-9]', '', 'g'), '')
            as integer
        )                                               as competencia,
        lpad(trim(coalesce(registro_ans, '')), 6, '0')  as registro_ans,
        lpad(regexp_replace(cast(coalesce(cd_municipio, '') as text), '[^0-9]', '', 'g'), 7, '0')
                                                        as cd_municipio,
        upper(trim(coalesce(nm_municipio, '')))         as nm_municipio,
        upper(trim(coalesce(sg_uf, '')))                as sg_uf,
        upper(trim(coalesce(nm_regiao, '')))            as nm_regiao,
        upper(trim(coalesce(tipo_assistencial, '')))    as tipo_assistencial,
        coalesce(cast(nullif(trim(cast(qt_beneficiarios as text)), '') as integer), 0) as qt_beneficiarios,
        coalesce(cast(nullif(trim(cast(qt_eventos as text)), '') as integer), 0) as qt_eventos,
        cast(nullif(trim(cast(coalesce(indicador_cobertura, '0') as text)), '') as numeric(10, 4))
                                                        as indicador_cobertura,
        _carregado_em,
        _arquivo_origem,
        _lote_id
    from {{ source('bruto_ans', 'sip_mapa_assistencial') }}
    where trim(coalesce(registro_ans, '')) != ''
)

select *
from base
where competencia is not null
