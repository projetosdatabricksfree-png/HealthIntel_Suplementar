{{
    config(
        materialized='table',
        tags=['regulatorio_v2']
    )
}}

{%- set pesos = var('score_regulatorio_pesos') -%}

with base as (
    select *
    from {{ ref('int_regulatorio_v2_operadora_trimestre') }}
),
base_calc as (
    select
        base.*,
        case
            when rn623_excelencia then 100
            when rn623_reducao then 80
            when total_nip_rn623 > 0 then 60
            else 50
        end as score_rn623,
        round(
            (
                coalesce(score_igr, 0) * {{ pesos['igr_peso'] }}
                + coalesce(score_nip, 0) * {{ pesos['nip_peso'] }}
                + case
                    when rn623_excelencia then 100
                    when rn623_reducao then 80
                    when total_nip_rn623 > 0 then 60
                    else 50
                end * {{ pesos['rn623_peso'] }}
                + coalesce(score_prudencial, 0) * {{ pesos['prudencial_peso'] }}
                + coalesce(score_taxa_resolutividade, 0) * {{ pesos['taxa_resolutividade_peso'] }}
            )::numeric,
            2
        ) as score_regulatorio_base
    from base
)
select
    operadora_id,
    registro_ans,
    nome,
    nome_fantasia,
    modalidade,
    uf_sede,
    competencia,
    score_igr,
    score_nip,
    score_rn623,
    score_prudencial,
    score_taxa_resolutividade,
    regime_especial_ativo,
    tipo_regime,
    situacao_inadequada,
    qt_portabilidade_entrada,
    qt_portabilidade_saida,
    saldo_portabilidade,
    score_regulatorio_base,
    case
        when regime_especial_ativo then least(39.99, score_regulatorio_base)
        else score_regulatorio_base
    end as score_regulatorio,
    case
        when regime_especial_ativo then case when score_regulatorio_base >= 30 then 'D' else 'E' end
        else {{ classificar_rating_regulatorio('score_regulatorio_base') }}
    end as rating,
    versao_regulatoria
from base_calc
