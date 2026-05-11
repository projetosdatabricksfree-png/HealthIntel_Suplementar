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
    on rede.registro_ans = op.registro_ans
left join {{ ref('fat_densidade_rede_operadora') }} as dens
    on rede.registro_ans = dens.registro_ans
    and rede.competencia = dens.competencia
left join {{ ref('fat_cnes_rede_gap_municipio') }} as gap
    on rede.cd_municipio = gap.cd_municipio
    and rede.competencia = gap.competencia
