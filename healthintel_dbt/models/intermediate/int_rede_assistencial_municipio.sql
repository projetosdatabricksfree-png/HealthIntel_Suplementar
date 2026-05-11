{{
    config(
        tags=['rede'],
        materialized='ephemeral'
    )
}}

with rede as (
    select *
    from {{ ref('stg_rede_assistencial') }}
),
beneficios as (
    select
        operadora_id,
        registro_ans,
        competencia,
        cd_municipio,
        sum(qt_beneficiario_ativo) as qt_beneficiario_ativo
    from {{ ref('fat_beneficiario_localidade') }}
    group by 1, 2, 3, 4
),
agregado as (
    select
        rede.competencia,
        operadora.operadora_id,
        rede.registro_ans,
        rede.cd_municipio,
        localidade.nm_municipio,
        localidade.sg_uf,
        localidade.nm_regiao,
        localidade.pop_estimada_ibge,
        localidade.porte_municipio,
        rede.segmento,
        sum(rede.qt_prestador) as qt_prestador,
        sum(rede.qt_especialidade_disponivel) as qt_especialidade_disponivel,
        coalesce(max(beneficios.qt_beneficiario_ativo), 0) as beneficiario_total,
        case
            when coalesce(max(beneficios.qt_beneficiario_ativo), 0) = 0 then 0
            else round(
                (sum(rede.qt_prestador)::numeric / nullif(max(beneficios.qt_beneficiario_ativo), 0))
                * 10000,
                2
            )
        end as qt_prestador_por_10k_beneficiarios
    from rede
    inner join {{ ref('dim_operadora_atual') }} as operadora
        on rede.registro_ans = operadora.registro_ans
    left join {{ ref('dim_localidade') }} as localidade
        on rede.cd_municipio = localidade.cd_municipio
    left join beneficios
        on rede.registro_ans = beneficios.registro_ans
        and rede.competencia = beneficios.competencia
        and rede.cd_municipio = beneficios.cd_municipio
    group by 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
),
parametrizado as (
    select
        agregado.*,
        case
            when coalesce(agregado.pop_estimada_ibge, 0) < 100000 then 'pequeno'
            when coalesce(agregado.pop_estimada_ibge, 0) < 500000 then 'medio'
            else 'grande'
        end as porte_parametrizado
    from agregado
)

select
    agregado.*,
    coalesce(parametro.limiar_prestador_por_10k, 0) as limiar_prestador_por_10k,
    coalesce(parametro.limiar_especialidade_por_10k, 0) as limiar_especialidade_por_10k,
    coalesce(agregado.qt_prestador > 0, false) as tem_cobertura,
    coalesce(agregado.qt_prestador_por_10k_beneficiarios >= coalesce(parametro.limiar_prestador_por_10k, 0), false) as cobertura_minima_atendida
from parametrizado as agregado
left join {{ ref('ref_parametro_rede') }} as parametro
    on agregado.segmento = parametro.segmento
    and agregado.porte_parametrizado = parametro.porte_municipio
