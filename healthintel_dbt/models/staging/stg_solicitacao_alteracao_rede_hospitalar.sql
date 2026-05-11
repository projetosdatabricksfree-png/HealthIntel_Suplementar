{{ config(tags=['delta_ans_100', 'rede_prestadores']) }}

with base as (
    select
        cast(
            nullif(regexp_replace(cast(competencia as text), '[^0-9]', '', 'g'), '')
            as integer
        )                                               as competencia,
        lpad(trim(coalesce(registro_ans, '')), 6, '0')  as registro_ans,
        upper(trim(coalesce(nu_solicitacao, '')))       as nu_solicitacao,
        upper(trim(coalesce(tipo_alteracao, '')))       as tipo_alteracao,
        lpad(regexp_replace(coalesce(cnes, ''), '[^0-9]', '', 'g'), 7, '0')
                                                        as cnes,
        upper(trim(coalesce(nm_prestador, '')))         as nm_prestador,
        lpad(regexp_replace(cast(coalesce(cd_municipio, '') as text), '[^0-9]', '', 'g'), 7, '0')
                                                        as cd_municipio,
        upper(trim(coalesce(sg_uf, '')))                as sg_uf,
        cast(nullif(trim(cast(data_solicitacao as text)), '') as date)
                                                        as data_solicitacao,
        upper(trim(coalesce(status_solicitacao, '')))   as status_solicitacao,
        _carregado_em,
        _arquivo_origem,
        _lote_id
    from {{ source('bruto_ans', 'solicitacao_alteracao_rede_hospitalar') }}
    where trim(coalesce(registro_ans, '')) != ''
)

select *
from base
where competencia is not null
