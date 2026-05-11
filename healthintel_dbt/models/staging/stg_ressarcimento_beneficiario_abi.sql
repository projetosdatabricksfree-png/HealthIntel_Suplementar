{{ config(tags=['delta_ans_100', 'ressarcimento_sus']) }}

with base as (
    select
        cast(
            nullif(regexp_replace(cast(competencia as text), '[^0-9]', '', 'g'), '')
            as integer
        )                                               as competencia,
        lpad(trim(coalesce(registro_ans, '')), 6, '0')  as registro_ans,
        upper(trim(coalesce(nu_abi, '')))               as nu_abi,
        lpad(regexp_replace(cast(coalesce(cd_municipio, '') as text), '[^0-9]', '', 'g'), 7, '0')
                                                        as cd_municipio,
        upper(trim(coalesce(nm_municipio, '')))         as nm_municipio,
        upper(trim(coalesce(sg_uf, '')))                as sg_uf,
        coalesce(cast(nullif(trim(cast(qt_beneficiarios as text)), '') as integer), 0)
                                                        as qt_beneficiarios,
        cast(nullif(trim(cast(coalesce(vl_ressarcimento, '0') as text)), '') as numeric(18, 2))
                                                        as vl_ressarcimento,
        upper(trim(coalesce(status_ressarcimento, ''))) as status_ressarcimento,
        _carregado_em,
        _arquivo_origem,
        _lote_id
    from {{ source('bruto_ans', 'ressarcimento_beneficiario_abi') }}
    where trim(coalesce(registro_ans, '')) != ''
)

select *
from base
where competencia is not null
