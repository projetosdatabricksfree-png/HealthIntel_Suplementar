{{
    config(
        materialized='table',
        tags=['rede']
    )
}}

with base as (
    select
        operadora_id,
        registro_ans,
        competencia,
        count(distinct cd_municipio) as qt_municipio_coberto,
        count(distinct sg_uf) as qt_uf_coberto,
        sum(case when tem_cobertura then 1 else 0 end) as qt_segmento_coberto,
        count(distinct cd_municipio) filter (where beneficiario_total > 0) as qt_municipio_com_beneficiario,
        count(distinct sg_uf) filter (where beneficiario_total > 0) as qt_uf_com_beneficiario
    from {{ ref('fat_cobertura_rede_municipio') }}
    group by 1, 2, 3
),
score_expr as (
    select
        base.*,
        (
            case
                when coalesce(qt_municipio_com_beneficiario, 0) = 0 then 0
                else (qt_municipio_coberto::numeric / qt_municipio_com_beneficiario) * 70
            end
            +
            case
                when coalesce(qt_uf_com_beneficiario, 0) = 0 then 0
                else (qt_uf_coberto::numeric / qt_uf_com_beneficiario) * 30
            end
        ) as score_rede_base
    from base
)

select
    operadora_id,
    registro_ans,
    competencia,
    qt_municipio_coberto,
    qt_uf_coberto,
    qt_segmento_coberto,
    qt_municipio_com_beneficiario,
    qt_uf_com_beneficiario,
    round(
        case
            when coalesce(qt_municipio_com_beneficiario, 0) = 0 then 0
            else ((qt_municipio_coberto::numeric / qt_municipio_com_beneficiario) * 100)
        end,
        2
    ) as pct_municipios_cobertos,
    round(
        case
            when coalesce(qt_uf_com_beneficiario, 0) = 0 then 0
            else ((qt_uf_coberto::numeric / qt_uf_com_beneficiario) * 100)
        end,
        2
    ) as pct_ufs_cobertos,
    {{ normalizar_0_100('score_expr.score_rede_base', 0, 100) }} as score_rede,
    'rede_v1' as versao_dataset
from score_expr
