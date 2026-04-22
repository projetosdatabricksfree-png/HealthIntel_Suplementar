{{
    config(
        unique_key=['registro_ans', 'trimestre'],
        incremental_strategy='delete+insert',
        on_schema_change='sync_all_columns'
    )
}}

select
    base.registro_ans,
    base.trimestre,
    base.modalidade_referencia,
    base.porte,
    base.total_reclamacoes,
    base.beneficiarios,
    base.igr,
    base.meta_igr,
    base.atingiu_meta_excelencia,
    base.demandas_nip,
    base.demandas_resolvidas,
    base.taxa_intermediacao_resolvida,
    base.taxa_resolutividade,
    base.rn623_excelencia,
    base.rn623_reducao,
    base.total_nip_referencia,
    case
        when base.rn623_excelencia then 'baixo'
        when coalesce(base.taxa_intermediacao_resolvida, 0) >= 85 then 'moderado'
        when coalesce(base.igr, 0) >= coalesce(base.meta_igr, 999999) then 'alto'
        when coalesce(base.taxa_intermediacao_resolvida, 0) < 75 then 'alto'
        else 'moderado'
    end as faixa_risco_regulatorio
from {{ ref('int_regulatorio_operadora_trimestre') }} as base
