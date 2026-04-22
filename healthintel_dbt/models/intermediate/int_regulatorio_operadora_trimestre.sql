with chaves as (
    select
        trimestre,
        registro_ans
    from {{ ref('stg_igr') }}

    union

    select
        trimestre,
        registro_ans
    from {{ ref('stg_nip') }}

    union

    select
        trimestre,
        registro_ans
    from {{ ref('stg_rn623_lista') }}
),
rn623 as (
    select
        trimestre,
        registro_ans,
        max(case when tipo_lista = 'excelencia' then 1 else 0 end)::boolean as rn623_excelencia,
        max(case when tipo_lista = 'reducao' then 1 else 0 end)::boolean as rn623_reducao,
        max(total_nip) as total_nip_rn623,
        max(beneficiarios) as beneficiarios_rn623,
        max(igr) as igr_rn623,
        max(meta_igr) as meta_igr_rn623
    from {{ ref('stg_rn623_lista') }}
    group by trimestre, registro_ans
)

select
    chaves.registro_ans,
    chaves.trimestre,
    coalesce(igr.modalidade, nip.modalidade) as modalidade_referencia,
    igr.porte,
    igr.total_reclamacoes,
    coalesce(igr.beneficiarios, nip.beneficiarios, rn623.beneficiarios_rn623, 0) as beneficiarios,
    igr.igr,
    coalesce(igr.meta_igr, rn623.meta_igr_rn623) as meta_igr,
    coalesce(igr.atingiu_meta, false) as atingiu_meta_excelencia,
    nip.demandas_nip,
    nip.demandas_resolvidas,
    nip.taxa_intermediacao_resolvida,
    nip.taxa_resolutividade,
    coalesce(rn623.rn623_excelencia, false) as rn623_excelencia,
    coalesce(rn623.rn623_reducao, false) as rn623_reducao,
    coalesce(rn623.total_nip_rn623, nip.demandas_nip, igr.total_reclamacoes, 0) as total_nip_referencia
from chaves
left join {{ ref('stg_igr') }} as igr
    on chaves.trimestre = igr.trimestre
    and chaves.registro_ans = igr.registro_ans
left join {{ ref('stg_nip') }} as nip
    on chaves.trimestre = nip.trimestre
    and chaves.registro_ans = nip.registro_ans
left join rn623
    on chaves.trimestre = rn623.trimestre
    and chaves.registro_ans = rn623.registro_ans
