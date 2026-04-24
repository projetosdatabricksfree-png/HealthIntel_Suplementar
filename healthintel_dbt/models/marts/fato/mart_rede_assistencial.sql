{{
    config(materialized='table', tags=['mart'])
}}

select
    rede.registro_ans,
    rede.cd_municipio,
    rede.competencia,
    op.nome as razao_social,
    rede.nm_municipio as nome_municipio,
    rede.sg_uf as uf,
    rede.segmento,
    rede.qt_prestador as qt_prestadores,
    dens.pct_municipios_cobertos as densidade_por_10k,
    gap.gap_absoluto as gap_leitos_cnes,
    gap.severidade_gap as classificacao_vazio
from {{ ref('fat_cobertura_rede_municipio') }} as rede
left join {{ ref('dim_operadora_atual') }} as op
    on op.registro_ans = rede.registro_ans
left join {{ ref('fat_densidade_rede_operadora') }} as dens
    on dens.registro_ans = rede.registro_ans
    and dens.competencia = rede.competencia
left join {{ ref('fat_cnes_rede_gap_municipio') }} as gap
    on gap.cd_municipio = rede.cd_municipio
    and gap.competencia = rede.competencia
