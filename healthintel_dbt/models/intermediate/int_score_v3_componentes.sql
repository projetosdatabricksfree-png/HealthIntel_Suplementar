{{
    config(
        materialized='ephemeral',
        tags=['score_v3']
    )
}}

{%- set pesos = var('score_v3_pesos') -%}

with base as (
    select
        v2.operadora_id,
        v2.registro_ans,
        v2.nome,
        v2.nome_fantasia,
        v2.modalidade,
        v2.uf_sede,
        v2.competencia,
        v2.trimestre_financeiro,
        v2.score_core,
        v2.score_regulatorio,
        v2.score_financeiro_trimestral as score_financeiro,
        v2.score_v2 as score_v2_normalizado
    from {{ ref('fat_score_v2_operadora_mensal') }} as v2
),
rede as (
    select
        operadora_id,
        competencia,
        score_rede
    from {{ ref('fat_densidade_rede_operadora') }}
),
componente_estrutural as (
    select
        operadora_id,
        competencia,
        null::numeric(12,2) as score_estrutural
    from base
    group by 1, 2
)

select
    base.operadora_id,
    base.registro_ans,
    base.nome,
    base.nome_fantasia,
    base.modalidade,
    base.uf_sede,
    base.competencia as competencia_id,
    base.trimestre_financeiro,
    coalesce(base.score_core, base.score_v2_normalizado) as score_core,
    coalesce(base.score_regulatorio, base.score_v2_normalizado) as score_regulatorio,
    coalesce(base.score_financeiro, base.score_v2_normalizado) as score_financeiro,
    coalesce(rede.score_rede, base.score_v2_normalizado) as score_rede,
    componente_estrutural.score_estrutural,
    base.score_v2_normalizado,
    (
        base.score_core is not null
        and base.score_regulatorio is not null
        and base.score_financeiro is not null
        and rede.score_rede is not null
        and componente_estrutural.score_estrutural is not null
    ) as score_completo,
    round(
        (
            coalesce(base.score_core, base.score_v2_normalizado) * {{ pesos['core'] }}
            + coalesce(base.score_regulatorio, base.score_v2_normalizado) * {{ pesos['regulatorio'] }}
            + coalesce(base.score_financeiro, base.score_v2_normalizado) * {{ pesos['financeiro'] }}
            + coalesce(rede.score_rede, base.score_v2_normalizado) * {{ pesos['rede'] }}
            + coalesce(componente_estrutural.score_estrutural, base.score_v2_normalizado) * {{ pesos['estrutural'] }}
        )::numeric,
        2
    )::numeric(12,2) as score_v3_final,
    'v3.0' as versao_metodologia
from base
left join rede
    on rede.operadora_id = base.operadora_id
    and rede.competencia = base.competencia
left join componente_estrutural
    on componente_estrutural.operadora_id = base.operadora_id
    and componente_estrutural.competencia = base.competencia
