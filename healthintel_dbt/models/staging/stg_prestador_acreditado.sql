{{ config(tags=['delta_ans_100', 'rede_prestadores']) }}

with base as (
    select
        lpad(regexp_replace(coalesce(cnes, ''), '[^0-9]', '', 'g'), 7, '0')
                                                        as cnes,
        upper(trim(coalesce(nm_prestador, '')))         as nm_prestador,
        regexp_replace(coalesce(cnpj, ''), '[^0-9]', '', 'g') as cnpj,
        lpad(regexp_replace(cast(coalesce(cd_municipio, '') as text), '[^0-9]', '', 'g'), 7, '0')
                                                        as cd_municipio,
        upper(trim(coalesce(nm_municipio, '')))         as nm_municipio,
        upper(trim(coalesce(sg_uf, '')))                as sg_uf,
        upper(trim(coalesce(acreditadora, '')))         as acreditadora,
        upper(trim(coalesce(nivel_acreditacao, '')))    as nivel_acreditacao,
        cast(nullif(trim(cast(data_acreditacao as text)), '') as date)
                                                        as data_acreditacao,
        cast(nullif(trim(cast(data_validade as text)), '') as date)
                                                        as data_validade,
        row_number() over (
            partition by lpad(regexp_replace(coalesce(cnes, ''), '[^0-9]', '', 'g'), 7, '0')
            order by _carregado_em desc
        )                                               as rn,
        _carregado_em,
        _arquivo_origem,
        _lote_id
    from {{ source('bruto_ans', 'prestador_acreditado') }}
    where trim(coalesce(cnes, '')) != ''
)

select *
from base
where rn = 1
