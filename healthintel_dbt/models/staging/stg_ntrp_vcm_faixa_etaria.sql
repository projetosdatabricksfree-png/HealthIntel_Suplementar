{{ config(tags=['delta_ans_100', 'precificacao_ntrp']) }}

with base as (
    select
        cast(
            nullif(regexp_replace(cast(competencia as text), '[^0-9]', '', 'g'), '')
            as integer
        )                                               as competencia,
        lpad(trim(coalesce(registro_ans, '')), 6, '0')  as registro_ans,
        upper(trim(coalesce(codigo_plano, '')))         as codigo_plano,
        upper(trim(coalesce(faixa_etaria, '')))         as faixa_etaria,
        upper(trim(coalesce(sg_uf, '')))                as sg_uf,
        cast(nullif(trim(cast(coalesce(vcm, '0') as text)), '') as numeric(18, 2))
                                                        as vcm,
        cast(nullif(trim(cast(coalesce(vl_minimo, '0') as text)), '') as numeric(18, 2))
                                                        as vl_minimo,
        cast(nullif(trim(cast(coalesce(vl_maximo, '0') as text)), '') as numeric(18, 2))
                                                        as vl_maximo,
        _carregado_em,
        _arquivo_origem,
        _lote_id
    from {{ source('bruto_ans', 'ntrp_vcm_faixa_etaria') }}
    where trim(coalesce(registro_ans, '')) != ''
)

select *
from base
where competencia is not null
