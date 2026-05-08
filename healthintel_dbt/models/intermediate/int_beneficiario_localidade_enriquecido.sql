with base as (
    select
        sib.competencia,
        sib.registro_ans,
        operadora.operadora_id,
        localidade.cd_municipio,
        sib.codigo_ibge,
        sib.municipio,
        sib.uf,
        coalesce(localidade.nm_municipio, nullif(upper(trim(sib.municipio)), ''), 'NAO_INFORMADO') as nm_municipio,
        coalesce(localidade.sg_uf, nullif(upper(trim(sib.uf)), ''), 'NA') as sg_uf,
        coalesce(localidade.nm_regiao, 'NAO_INFORMADA') as nm_regiao,
        sib.beneficiario_medico,
        sib.beneficiario_odonto,
        sib.beneficiario_total,
        sum(sib.beneficiario_total) over (
            partition by sib.codigo_ibge, sib.competencia
        ) as total_beneficiarios_municipio
    from {{ ref('stg_sib_municipio') }} as sib
    inner join {{ ref('dim_operadora_atual') }} as operadora
        on sib.registro_ans = operadora.registro_ans
    left join {{ ref('dim_localidade') }} as localidade
        on lpad(regexp_replace(cast(sib.codigo_ibge as text), '[^0-9]', '', 'g'), 7, '0') = localidade.cd_municipio
)

select
    competencia,
    operadora_id,
    registro_ans,
    cd_municipio,
    codigo_ibge,
    municipio,
    uf,
    nm_municipio,
    sg_uf,
    nm_regiao,
    beneficiario_medico,
    beneficiario_odonto,
    beneficiario_total,
    total_beneficiarios_municipio,
    case
        when coalesce(total_beneficiarios_municipio, 0) = 0 then 0
        else round(
            (beneficiario_total::numeric / total_beneficiarios_municipio) * 100,
            2
        )
    end as market_share_pct
from base
