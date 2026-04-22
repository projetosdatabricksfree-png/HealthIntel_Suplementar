{{
    config(
        materialized='table',
        tags=['score_v2', 'financeiro_v2']
    )
}}

{%- set pesos = var('score_v2_pesos') -%}

with base as (
    select *
    from {{ ref('int_score_v2_componentes') }}
)

select
    operadora_id,
    registro_ans,
    nome,
    nome_fantasia,
    modalidade,
    uf_sede,
    competencia,
    trimestre_financeiro,
    score_core,
    score_regulatorio,
    score_financeiro_trimestral,
    inadimplente,
    saldo_devedor,
    valor_devido,
    valor_pago,
    situacao_cobranca,
    taxa_glosa_calculada,
    valor_glosa_total,
    valor_faturado_total,
    penalizacao_vda,
    penalizacao_glosa,
    greatest(0, 100 - (penalizacao_vda + penalizacao_glosa)) as score_penalizacoes,
    round(
        (
            (coalesce(score_core, 0) * {{ pesos['score_core_peso'] }})
            + (coalesce(score_regulatorio, 0) * {{ pesos['score_regulatorio_peso'] }})
            + (coalesce(score_financeiro_trimestral, 0) * {{ pesos['score_financeiro_peso'] }})
            + (greatest(0, 100 - (penalizacao_vda + penalizacao_glosa)) * {{ pesos['penalizacoes_peso'] }})
        )::numeric,
        2
    )::numeric(12,2) as score_v2_base,
    least(
        100,
        greatest(
            0,
            round(
                (
                    (coalesce(score_core, 0) * {{ pesos['score_core_peso'] }})
                    + (coalesce(score_regulatorio, 0) * {{ pesos['score_regulatorio_peso'] }})
                    + (coalesce(score_financeiro_trimestral, 0) * {{ pesos['score_financeiro_peso'] }})
                    + (greatest(0, 100 - (penalizacao_vda + penalizacao_glosa)) * {{ pesos['penalizacoes_peso'] }})
                )::numeric,
                2
            )
        )
    )::numeric(12,2) as score_v2,
    case
        when least(
            100,
            greatest(
                0,
                round(
                    (
                        (coalesce(score_core, 0) * {{ pesos['score_core_peso'] }})
                        + (coalesce(score_regulatorio, 0) * {{ pesos['score_regulatorio_peso'] }})
                        + (coalesce(score_financeiro_trimestral, 0) * {{ pesos['score_financeiro_peso'] }})
                        + (greatest(0, 100 - (penalizacao_vda + penalizacao_glosa)) * {{ pesos['penalizacoes_peso'] }})
                    )::numeric,
                    2
                )
            )
        ) >= 90 then 'A'
        when least(
            100,
            greatest(
                0,
                round(
                    (
                        (coalesce(score_core, 0) * {{ pesos['score_core_peso'] }})
                        + (coalesce(score_regulatorio, 0) * {{ pesos['score_regulatorio_peso'] }})
                        + (coalesce(score_financeiro_trimestral, 0) * {{ pesos['score_financeiro_peso'] }})
                        + (greatest(0, 100 - (penalizacao_vda + penalizacao_glosa)) * {{ pesos['penalizacoes_peso'] }})
                    )::numeric,
                    2
                )
            )
        ) >= 80 then 'B'
        when least(
            100,
            greatest(
                0,
                round(
                    (
                        (coalesce(score_core, 0) * {{ pesos['score_core_peso'] }})
                        + (coalesce(score_regulatorio, 0) * {{ pesos['score_regulatorio_peso'] }})
                        + (coalesce(score_financeiro_trimestral, 0) * {{ pesos['score_financeiro_peso'] }})
                        + (greatest(0, 100 - (penalizacao_vda + penalizacao_glosa)) * {{ pesos['penalizacoes_peso'] }})
                    )::numeric,
                    2
                )
            )
        ) >= 65 then 'C'
        when least(
            100,
            greatest(
                0,
                round(
                    (
                        (coalesce(score_core, 0) * {{ pesos['score_core_peso'] }})
                        + (coalesce(score_regulatorio, 0) * {{ pesos['score_regulatorio_peso'] }})
                        + (coalesce(score_financeiro_trimestral, 0) * {{ pesos['score_financeiro_peso'] }})
                        + (greatest(0, 100 - (penalizacao_vda + penalizacao_glosa)) * {{ pesos['penalizacoes_peso'] }})
                    )::numeric,
                    2
                )
            )
        ) >= 50 then 'D'
        else 'E'
    end as rating,
    'v2.0' as versao_metodologia
from base
