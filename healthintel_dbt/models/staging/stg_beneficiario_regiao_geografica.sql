{{ config(tags=['delta_ans_100', 'beneficiarios_cobertura']) }}

with base as (
    select
        cast(
            nullif(regexp_replace(cast(competencia as text), '[^0-9]', '', 'g'), '')
            as integer
        )                                               as competencia,
        upper(trim(coalesce(cd_regiao, '')))            as cd_regiao,
        upper(trim(coalesce(nm_regiao, '')))            as nm_regiao,
        upper(trim(coalesce(sg_uf, '')))                as sg_uf,
        upper(trim(coalesce(tipo_plano, '')))           as tipo_plano,
        upper(trim(coalesce(segmentacao, '')))          as segmentacao,
        coalesce(cast(nullif(trim(cast(qt_beneficiarios as text)), '') as integer), 0)
                                                        as qt_beneficiarios,
        _carregado_em,
        _arquivo_origem,
        _lote_id
    from {{ source('bruto_ans', 'beneficiario_regiao_geografica') }}
)

select *
from base
where competencia is not null
