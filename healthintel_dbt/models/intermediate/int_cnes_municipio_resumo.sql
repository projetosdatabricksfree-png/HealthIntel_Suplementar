{{
    config(
        materialized='ephemeral',
        tags=['cnes']
    )
}}

with base as (
    select *
    from {{ ref('stg_cnes_estabelecimento') }}
),
agregado as (
    select
        competencia,
        cd_municipio,
        tipo_unidade,
        max(tipo_unidade_desc) as tipo_unidade_desc,
        count(*) as total_estabelecimentos,
        sum(coalesce(leitos_existentes, 0)) as total_leitos,
        sum(coalesce(leitos_sus, 0)) as total_leitos_sus,
        sum(case when vinculo_sus then 1 else 0 end) as total_estabelecimentos_vinculo_sus,
        round(
            coalesce(
                (sum(coalesce(leitos_sus, 0))::numeric / nullif(sum(coalesce(leitos_existentes, 0)), 0)) * 100,
                0
            ),
            2
        ) as pct_leitos_sus,
        round(
            coalesce(
                (sum(case when vinculo_sus then 1 else 0 end)::numeric / nullif(count(*), 0)) * 100,
                0
            ),
            2
        ) as pct_vinculo_sus
    from base
    group by 1, 2, 3
)

select
    agregado.competencia,
    agregado.cd_municipio,
    localidade.nm_municipio,
    localidade.sg_uf,
    localidade.nm_regiao,
    localidade.pop_estimada_ibge,
    localidade.porte_municipio,
    agregado.tipo_unidade,
    agregado.tipo_unidade_desc,
    agregado.total_estabelecimentos,
    agregado.total_leitos,
    agregado.total_leitos_sus,
    agregado.total_estabelecimentos_vinculo_sus,
    agregado.pct_leitos_sus,
    agregado.pct_vinculo_sus
from agregado
left join {{ ref('dim_localidade') }} as localidade
    on localidade.cd_municipio = agregado.cd_municipio
