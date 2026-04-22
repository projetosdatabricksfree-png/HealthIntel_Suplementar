with base as (
    select
        sib.competencia,
        sib.registro_ans,
        operadora.operadora_id,
        sib.beneficiario_medico,
        sib.beneficiario_odonto,
        sib.beneficiario_total,
        lag(sib.beneficiario_total, 12) over (
            partition by sib.registro_ans
            order by sib.competencia
        ) as beneficiario_total_12m_anterior,
        avg(sib.beneficiario_total) over (
            partition by sib.registro_ans
            order by sib.competencia
            rows between 11 preceding and current row
        ) as beneficiario_media_12m,
        stddev_samp(sib.beneficiario_total) over (
            partition by sib.registro_ans
            order by sib.competencia
            rows between 23 preceding and current row
        ) as volatilidade_24m
    from {{ ref('stg_sib_operadora') }} as sib
    inner join {{ ref('dim_operadora_atual') }} as operadora
        on sib.registro_ans = operadora.registro_ans
)

select
    operadora_id,
    registro_ans,
    competencia,
    beneficiario_medico,
    beneficiario_odonto,
    beneficiario_total,
    beneficiario_total_12m_anterior,
    beneficiario_media_12m,
    case
        when coalesce(beneficiario_total_12m_anterior, 0) = 0 then 0
        else round(
            ((beneficiario_total - beneficiario_total_12m_anterior)::numeric
            / beneficiario_total_12m_anterior) * 100,
            2
        )
    end as taxa_crescimento_12m,
    coalesce(round(volatilidade_24m::numeric, 2), 0) as volatilidade_24m
from base
