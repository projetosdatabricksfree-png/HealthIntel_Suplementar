{{ config(tags=['delta_ans_100', 'precificacao_ntrp']) }}

with base as (
    select
        cast(
            nullif(regexp_replace(cast(competencia as text), '[^0-9]', '', 'g'), '')
            as integer
        )                                               as competencia,
        lpad(trim(coalesce(registro_ans, '')), 6, '0')  as registro_ans,
        upper(trim(coalesce(codigo_plano, '')))         as codigo_plano,
        lpad(regexp_replace(cast(coalesce(cd_municipio, '') as text), '[^0-9]', '', 'g'), 7, '0')
                                                        as cd_municipio,
        upper(trim(coalesce(nm_municipio, '')))         as nm_municipio,
        upper(trim(coalesce(sg_uf, '')))                as sg_uf,
        upper(trim(coalesce(area_comercializacao, ''))) as area_comercializacao,
        _carregado_em,
        _arquivo_origem,
        _lote_id
    from {{ source('bruto_ans', 'ntrp_area_comercializacao') }}
    where trim(coalesce(registro_ans, '')) != ''
)

select *
from base
where competencia is not null
