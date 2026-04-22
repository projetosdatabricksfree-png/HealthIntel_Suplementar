with base as (
    select
        ioc.operadora_id,
        ioc.registro_ans,
        ioc.competencia,
        ioc.nome,
        ioc.nome_fantasia,
        ioc.modalidade,
        ioc.uf_sede,
        ioc.municipio_sede,
        ioc.cnpj,
        sib.beneficiario_total,
        lag(sib.beneficiario_total) over (
            partition by ioc.registro_ans
            order by ioc.competencia
        ) as beneficiario_total_anterior,
        max(sib.beneficiario_total) over (
            partition by ioc.competencia
        ) as max_beneficiario_competencia
    from {{ ref('int_operadora_competencia') }} as ioc
    inner join {{ ref('stg_sib_operadora') }} as sib
        on ioc.registro_ans = sib.registro_ans
        and ioc.competencia = sib.competencia
),
insumos as (
    select
        operadora_id,
        registro_ans,
        competencia,
        nome,
        nome_fantasia,
        modalidade,
        uf_sede,
        municipio_sede,
        cnpj,
        beneficiario_total,
        beneficiario_total_anterior,
        least(
            100.0,
            greatest(
                0.0,
                case
                    when beneficiario_total_anterior is null or beneficiario_total_anterior = 0 then 75.0
                    else 70.0 + (
                        ((beneficiario_total - beneficiario_total_anterior)::numeric / beneficiario_total_anterior)
                        * 100.0
                    )
                end
            )
        )::numeric(10,2) as score_crescimento,
        (
            (
                case when nome is not null and nome <> '' then 25 else 0 end
            ) + (
                case when modalidade is not null and modalidade <> '' then 25 else 0 end
            ) + (
                case when uf_sede is not null and uf_sede <> '' then 25 else 0 end
            ) + (
                case when cnpj is not null and length(cnpj) = 14 then 25 else 0 end
            )
        )::numeric(10,2) as score_qualidade,
        least(
            100.0,
            greatest(
                0.0,
                case
                    when beneficiario_total_anterior is null or beneficiario_total_anterior = 0 then 80.0
                    else 100.0 - (
                        abs(beneficiario_total - beneficiario_total_anterior)::numeric
                        / beneficiario_total_anterior
                    ) * 100.0
                end
            )
        )::numeric(10,2) as score_estabilidade,
        least(
            100.0,
            greatest(
                0.0,
                case
                    when coalesce(max_beneficiario_competencia, 0) = 0 then 0.0
                    else 20.0 + (
                        (beneficiario_total::numeric / max_beneficiario_competencia) * 80.0
                    )
                end
            )
        )::numeric(10,2) as score_presenca
from base
)

select * from insumos
