{{
    config(materialized='ephemeral', tags=['regulatorio_v2'])
}}

with
chaves as (
    select distinct
registro_ans,
{{ trimestre_para_competencia('trimestre') }} as competencia
    from {{ ref('stg_igr') }}
    union
    select distinct
registro_ans,
{{ trimestre_para_competencia('trimestre') }} as competencia
    from {{ ref('stg_nip') }}
    union
    select distinct
registro_ans,
{{ trimestre_para_competencia('trimestre') }} as competencia
    from {{ ref('stg_rn623_lista') }}
    union
    select distinct
registro_ans,
trimestre as competencia
    from {{ ref('stg_regime_especial') }}
    union
    select distinct
registro_ans,
trimestre as competencia
    from {{ ref('stg_prudencial') }}
    union
    select distinct
registro_ans,
competencia
    from {{ ref('stg_portabilidade') }}
    union
    select distinct
registro_ans,
trimestre as competencia
    from {{ ref('stg_taxa_resolutividade') }}
),
base as (
    select
        d.operadora_id,
        d.registro_ans,
        k.competencia,
        d.nome,
        d.nome_fantasia,
        d.modalidade,
        d.uf_sede
    from chaves as k
    inner join {{ ref('dim_operadora_atual') }} as d
        on k.registro_ans = d.registro_ans
),
igr as (
    select
        registro_ans,
        {{ trimestre_para_competencia('trimestre') }} as competencia,
        cast({{ normalizar_0_100('100 - (coalesce(igr, 0) * 20)', 0, 100) }} as numeric(12,4)) as score_igr,
        coalesce(atingiu_meta, false) as atingiu_meta_excelencia,
        total_reclamacoes,
        beneficiarios,
        meta_igr
    from {{ ref('stg_igr') }}
),
nip as (
    select
        registro_ans,
        {{ trimestre_para_competencia('trimestre') }} as competencia,
        cast({{ normalizar_0_100('coalesce(taxa_intermediacao_resolvida, taxa_resolutividade, 0)', 0, 100) }} as numeric(12,4)) as score_nip,
        demandas_nip,
        demandas_resolvidas,
        taxa_intermediacao_resolvida,
        taxa_resolutividade
    from {{ ref('stg_nip') }}
),
rn623 as (
    select
        registro_ans,
        {{ trimestre_para_competencia('trimestre') }} as competencia,
        max(case when tipo_lista = 'excelencia' then 1 else 0 end)::boolean as rn623_excelencia,
        max(case when tipo_lista = 'reducao' then 1 else 0 end)::boolean as rn623_reducao,
        max(total_nip) as total_nip,
        max(beneficiarios) as beneficiarios,
        max(igr) as igr,
        max(meta_igr) as meta_igr
    from {{ ref('stg_rn623_lista') }}
    group by 1, 2
),
regime_especial as (
    select
        registro_ans,
        trimestre as competencia,
        max(case when ativo then 1 else 0 end)::boolean as regime_especial_ativo,
        max(tipo_regime) as tipo_regime,
        max(data_inicio) as data_inicio,
        max(data_fim) as data_fim
    from {{ ref('stg_regime_especial') }}
    group by 1, 2
),
prudencial as (
    select
        registro_ans,
        trimestre as competencia,
        max(margem_solvencia) as margem_solvencia,
        max(capital_minimo_requerido) as capital_minimo_requerido,
        max(capital_disponivel) as capital_disponivel,
        max(indice_liquidez) as indice_liquidez,
        max(situacao_prudencial) as situacao_prudencial,
        max(case when situacao_inadequada then 1 else 0 end)::boolean as situacao_inadequada,
        cast({{ normalizar_0_100('coalesce(max(indice_liquidez), 0) * 20', 0, 100) }} as numeric(12,4)) as score_prudencial
    from {{ ref('stg_prudencial') }}
    group by 1, 2
),
portabilidade as (
    select
        registro_ans,
        competencia,
        max(modalidade) as modalidade,
        max(modalidade_descricao) as modalidade_descricao,
        max(tipo_contratacao) as tipo_contratacao,
        sum(qt_portabilidade_entrada) as qt_portabilidade_entrada,
        sum(qt_portabilidade_saida) as qt_portabilidade_saida,
        sum(saldo_portabilidade) as saldo_portabilidade,
        cast(
            case
                when sum(qt_portabilidade_entrada) = 0 then 0
                else (sum(qt_portabilidade_saida)::numeric / nullif(sum(qt_portabilidade_entrada), 0)) * 100
            end as numeric(12,4)
        ) as taxa_saida_sobre_entrada
    from {{ ref('stg_portabilidade') }}
    group by 1, 2
),
taxa_resolutividade as (
    select
        registro_ans,
        trimestre as competencia,
        cast({{ normalizar_0_100('coalesce(taxa_resolutividade, 0)', 0, 100) }} as numeric(12,4)) as score_taxa_resolutividade,
        n_reclamacao_resolvida,
        n_reclamacao_total
    from {{ ref('stg_taxa_resolutividade') }}
)

select
    base.operadora_id,
    base.registro_ans,
    base.nome,
    base.nome_fantasia,
    base.modalidade,
    base.uf_sede,
    base.competencia,
    coalesce(igr.score_igr, 0) as score_igr,
    coalesce(nip.score_nip, 0) as score_nip,
    coalesce(rn623.rn623_excelencia, false) as rn623_excelencia,
    coalesce(rn623.rn623_reducao, false) as rn623_reducao,
    coalesce(regime_especial.regime_especial_ativo, false) as regime_especial_ativo,
    coalesce(regime_especial.tipo_regime, 'sem_regime') as tipo_regime,
    coalesce(prudencial.situacao_inadequada, false) as situacao_inadequada,
    coalesce(prudencial.score_prudencial, 0) as score_prudencial,
    coalesce(taxa_resolutividade.score_taxa_resolutividade, 0) as score_taxa_resolutividade,
    coalesce(portabilidade.qt_portabilidade_entrada, 0) as qt_portabilidade_entrada,
    coalesce(portabilidade.qt_portabilidade_saida, 0) as qt_portabilidade_saida,
    coalesce(portabilidade.saldo_portabilidade, 0) as saldo_portabilidade,
    coalesce(portabilidade.taxa_saida_sobre_entrada, 0) as taxa_saida_sobre_entrada,
    coalesce(nip.demandas_nip, 0) as demandas_nip,
    coalesce(nip.demandas_resolvidas, 0) as demandas_resolvidas,
    coalesce(nip.taxa_intermediacao_resolvida, 0) as taxa_intermediacao_resolvida,
    coalesce(nip.taxa_resolutividade, 0) as taxa_resolutividade,
    coalesce(igr.atingiu_meta_excelencia, false) as atingiu_meta_excelencia,
    coalesce(igr.total_reclamacoes, 0) as total_reclamacoes,
    coalesce(igr.beneficiarios, 0) as beneficiarios,
    coalesce(rn623.total_nip, 0) as total_nip_rn623,
    coalesce(rn623.meta_igr, igr.meta_igr, 0) as meta_igr,
    coalesce(igr.meta_igr, 0) as meta_igr_igr,
    coalesce(igr.beneficiarios, 0) as beneficiarios_igr,
    coalesce(prudencial.margem_solvencia, 0) as margem_solvencia,
    coalesce(prudencial.capital_minimo_requerido, 0) as capital_minimo_requerido,
    coalesce(prudencial.capital_disponivel, 0) as capital_disponivel,
    coalesce(prudencial.indice_liquidez, 0) as indice_liquidez,
    'regulatorio_v2' as versao_regulatoria
from base
left join igr
    on base.registro_ans = igr.registro_ans
    and base.competencia = igr.competencia
left join nip
    on base.registro_ans = nip.registro_ans
    and base.competencia = nip.competencia
left join rn623
    on base.registro_ans = rn623.registro_ans
    and base.competencia = rn623.competencia
left join regime_especial
    on base.registro_ans = regime_especial.registro_ans
    and base.competencia = regime_especial.competencia
left join prudencial
    on base.registro_ans = prudencial.registro_ans
    and base.competencia = prudencial.competencia
left join portabilidade
    on base.registro_ans = portabilidade.registro_ans
    and base.competencia = portabilidade.competencia
left join taxa_resolutividade
    on base.registro_ans = taxa_resolutividade.registro_ans
    and base.competencia = taxa_resolutividade.competencia
