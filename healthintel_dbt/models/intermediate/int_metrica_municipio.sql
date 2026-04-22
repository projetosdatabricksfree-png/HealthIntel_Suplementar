with base as (
    select
        localidade.cd_municipio,
        localidade.nm_municipio,
        localidade.sg_uf,
        localidade.nm_regiao,
        localidade.competencia,
        localidade.operadora_id,
        localidade.registro_ans,
        localidade.municipio,
        localidade.uf,
        localidade.beneficiario_total,
        localidade.total_beneficiarios_municipio,
        localidade.market_share_pct / 100.0 as market_share,
        {{ calcular_hhi('localidade.market_share_pct / 100.0', 'localidade.cd_municipio, localidade.competencia') }} as hhi_municipio
    from {{ ref('int_beneficiario_localidade_enriquecido') }} as localidade
)

select
    cd_municipio,
    nm_municipio,
    sg_uf,
    nm_regiao,
    competencia,
    operadora_id,
    registro_ans,
    municipio,
    uf,
    beneficiario_total,
    total_beneficiarios_municipio,
    round(market_share * 100, 2) as market_share_pct,
    hhi_municipio,
    case
        when hhi_municipio >= 2500 then 'alta'
        when hhi_municipio >= 1500 then 'media'
        else 'baixa'
    end as concentracao_mercado
from base
