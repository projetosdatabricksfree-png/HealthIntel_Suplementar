{{
    config(
        unique_key=['operadora_id', 'competencia_id'],
        incremental_strategy='delete+insert',
        on_schema_change='sync_all_columns'
    )
}}

select
    operadora.operadora_id,
    nip.registro_ans,
    nip.trimestre as competencia_id,
    nip.trimestre,
    nip.modalidade,
    nip.demandas_nip as n_reclamacao_total,
    nip.demandas_resolvidas as n_reclamacao_resolvida,
    case
        when coalesce(nip.demandas_nip, 0) = 0 then 0
        else round((nip.demandas_resolvidas::numeric / nip.demandas_nip) * 100, 2)
    end as taxa_resolucao,
    case
        when coalesce(nip.beneficiarios, 0) = 0 then 0
        else round((nip.demandas_nip::numeric / nip.beneficiarios) * 1000, 4)
    end as indice_reclamacao_por_beneficiario
from {{ ref('stg_nip') }} as nip
inner join {{ ref('dim_operadora_atual') }} as operadora
    on nip.registro_ans = operadora.registro_ans
{% if is_incremental() %}
where nip.trimestre in (
    select trimestre
    from {{ ref('stg_nip') }}
    order by trimestre desc
    limit 3
)
{% endif %}
