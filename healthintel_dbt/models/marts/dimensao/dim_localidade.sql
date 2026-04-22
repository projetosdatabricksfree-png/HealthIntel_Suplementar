with base as (
    select distinct
        lpad(regexp_replace(cast(municipio.codigo_ibge as text), '[^0-9]', '', 'g'), 7, '0') as cd_municipio,
        upper(trim(coalesce(seed.nm_municipio, municipio.municipio))) as nm_municipio,
        upper(trim(coalesce(seed.sg_uf, municipio.uf))) as sg_uf,
        upper(trim(coalesce(seed.nm_regiao, 'NAO_INFORMADA'))) as nm_regiao,
        coalesce(pop.pop_estimada, 0) as pop_estimada_ibge,
        coalesce(pop.ano_referencia, 2024) as ano_referencia_populacao,
        case
            when coalesce(pop.pop_estimada, 0) < 100000 then 'pequeno'
            when coalesce(pop.pop_estimada, 0) < 500000 then 'medio'
            else 'grande'
        end as porte_municipio
    from {{ ref('stg_sib_municipio') }} as municipio
    left join {{ ref('ref_municipio_ibge') }} as seed
        on cast(seed.codigo_ibge as text) = lpad(regexp_replace(cast(municipio.codigo_ibge as text), '[^0-9]', '', 'g'), 7, '0')
    left join {{ ref('ref_populacao_municipio') }} as pop
        on cast(pop.cd_municipio as text) = lpad(regexp_replace(cast(municipio.codigo_ibge as text), '[^0-9]', '', 'g'), 7, '0')
)

select *
from base
