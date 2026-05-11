{{
    config(
        materialized='ephemeral',
        tags=['cnes', 'rede']
    )
}}

with cnes as (
    select
        competencia,
        cd_municipio,
        nm_municipio,
        sg_uf,
        nm_regiao,
        pop_estimada_ibge,
        porte_municipio,
        tipo_unidade,
        tipo_unidade_desc,
        total_estabelecimentos,
        total_leitos,
        total_leitos_sus,
        total_estabelecimentos_vinculo_sus,
        pct_leitos_sus,
        pct_vinculo_sus
    from {{ ref('int_cnes_municipio_resumo') }}
),
rede as (
    select
        competencia,
        cd_municipio,
        sum(coalesce(qt_prestador, 0)) as qt_prestador_rede,
        sum(coalesce(qt_especialidade_disponivel, 0)) as qt_especialidade_rede
    from {{ ref('fat_cobertura_rede_municipio') }}
    group by 1, 2
)

select
    cnes.competencia,
    cnes.cd_municipio,
    cnes.nm_municipio,
    cnes.sg_uf,
    cnes.nm_regiao,
    cnes.pop_estimada_ibge,
    cnes.porte_municipio,
    cnes.tipo_unidade,
    cnes.tipo_unidade_desc,
    cnes.total_estabelecimentos,
    cnes.total_leitos,
    cnes.total_leitos_sus,
    cnes.total_estabelecimentos_vinculo_sus,
    cnes.pct_leitos_sus,
    cnes.pct_vinculo_sus,
    coalesce(rede.qt_prestador_rede, 0) as qt_prestador_rede,
    coalesce(rede.qt_especialidade_rede, 0) as qt_especialidade_rede,
    cnes.total_estabelecimentos - coalesce(rede.qt_prestador_rede, 0) as gap_estabelecimentos_vs_rede,
    round(
        case
            when coalesce(rede.qt_prestador_rede, 0) = 0 then 100
            when cnes.total_estabelecimentos - coalesce(rede.qt_prestador_rede, 0) <= 0 then 0
            else (
                (cnes.total_estabelecimentos - coalesce(rede.qt_prestador_rede, 0))::numeric
                / nullif(rede.qt_prestador_rede, 0)
            ) * 100
        end,
        2
    ) as gap_pct,
    coalesce(cnes.total_estabelecimentos - coalesce(rede.qt_prestador_rede, 0)
            > greatest(10, cnes.total_estabelecimentos * 0.25), false) as flag_gap_critico
from cnes
left join rede
    on cnes.competencia = rede.competencia
    and cnes.cd_municipio = rede.cd_municipio
