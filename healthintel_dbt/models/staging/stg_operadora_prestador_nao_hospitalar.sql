{{ config(tags=['delta_ans_100', 'rede_prestadores']) }}

with base as (
    select
        cast(
            nullif(regexp_replace(cast(competencia as text), '[^0-9]', '', 'g'), '')
            as integer
        )                                               as competencia,
        lpad(trim(coalesce(registro_ans, '')), 6, '0')  as registro_ans,
        lpad(regexp_replace(coalesce(cnes, ''), '[^0-9]', '', 'g'), 7, '0')
                                                        as cnes,
        upper(trim(coalesce(nm_prestador, '')))         as nm_prestador,
        lpad(regexp_replace(cast(coalesce(cd_municipio, '') as text), '[^0-9]', '', 'g'), 7, '0')
                                                        as cd_municipio,
        upper(trim(coalesce(sg_uf, '')))                as sg_uf,
        upper(trim(coalesce(tipo_servico, '')))         as tipo_servico,
        upper(trim(coalesce(tipo_vinculo, '')))         as tipo_vinculo,
        _carregado_em,
        _arquivo_origem,
        _lote_id
    from {{ source('bruto_ans', 'operadora_prestador_nao_hospitalar') }}
    where trim(coalesce(registro_ans, '')) != ''
)

select *
from base
where competencia is not null
