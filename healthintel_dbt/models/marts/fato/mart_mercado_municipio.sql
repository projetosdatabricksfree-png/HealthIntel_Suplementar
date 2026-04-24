{{
    config(materialized='table', tags=['mart'])
}}

select
    mercado.cd_municipio,
    mercado.competencia,
    max(mercado.nm_municipio) as nome_municipio,
    max(mercado.sg_uf) as uf,
    sum(coalesce(mercado.beneficiario_total, 0)) as qt_beneficiarios_total,
    count(distinct mercado.registro_ans) as qt_operadoras_ativas,
    max(mercado.hhi_municipio) as hhi,
    max(oport.oportunidade_v2_score) as score_oportunidade,
    max(oport.total_beneficiarios) as populacao_alvo,
    max(oport.operadora_melhor_score_v2) as operadora_dominante
from {{ ref('fat_market_share_mensal') }} as mercado
left join {{ ref('fat_oportunidade_v2_municipio_mensal') }} as oport
    on oport.cd_municipio = mercado.cd_municipio
    and oport.competencia = mercado.competencia
group by 1, 2
