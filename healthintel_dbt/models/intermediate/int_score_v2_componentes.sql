{{
    config(materialized='ephemeral', tags=['financeiro_v2', 'score_v2'])
}}

with chaves as (
    select distinct
registro_ans,
competencia
    from {{ ref('fat_score_operadora_mensal') }}
    union
    select distinct
registro_ans,
competencia
    from {{ ref('fat_score_regulatorio_operadora_mensal') }}
    union
    select distinct
registro_ans,
competencia
    from {{ ref('fat_vda_operadora_mensal') }}
    union
    select distinct
registro_ans,
competencia
    from {{ ref('fat_glosa_operadora_mensal') }}
),
base as (
    select
        d.operadora_id,
        d.registro_ans,
        d.nome,
        d.nome_fantasia,
        d.modalidade,
        d.uf_sede,
        k.competencia,
        {{ competencia_para_trimestre('k.competencia') }} as trimestre_financeiro
    from chaves as k
    inner join {{ ref('dim_operadora_atual') }} as d
        on k.registro_ans = d.registro_ans
),
score_core as (
    select
        operadora_id,
        competencia,
        score_final as score_core
    from {{ ref('fat_score_operadora_mensal') }}
),
score_regulatorio as (
    select
        operadora_id,
        competencia,
        score_regulatorio
    from {{ ref('fat_score_regulatorio_operadora_mensal') }}
),
financeiro as (
    select
        base.operadora_id,
        base.competencia,
        coalesce(fin.score_financeiro_base, 0) as score_financeiro_trimestral,
        coalesce(fin.versao_financeira, 'financeiro_v1') as versao_financeiro
    from base
    left join lateral (
        select
            financeiro_base.score_financeiro_base,
            financeiro_base.versao_financeira
        from {{ ref('fat_financeiro_operadora_trimestral') }} as financeiro_base
        where financeiro_base.operadora_id = base.operadora_id
          and financeiro_base.trimestre <= base.trimestre_financeiro
        order by financeiro_base.trimestre desc
        limit 1
    ) as fin on true
),
vda as (
    select
        operadora_id,
        competencia,
        inadimplente,
        saldo_devedor,
        valor_devido,
        valor_pago,
        situacao_cobranca,
        'vda_v1' as versao_dataset
    from {{ ref('fat_vda_operadora_mensal') }}
),
glosa as (
    select
        operadora_id,
        competencia,
        max(taxa_glosa_calculada) as taxa_glosa_calculada,
        sum(coalesce(valor_glosa, 0)) as valor_glosa_total,
        sum(coalesce(valor_faturado, 0)) as valor_faturado_total,
        'glosa_v1' as versao_dataset
    from {{ ref('fat_glosa_operadora_mensal') }}
    group by operadora_id, competencia
)

select
    base.operadora_id,
    base.registro_ans,
    base.nome,
    base.nome_fantasia,
    base.modalidade,
    base.uf_sede,
    base.competencia,
    base.trimestre_financeiro,
    coalesce(score_core.score_core, 0) as score_core,
    coalesce(score_regulatorio.score_regulatorio, 0) as score_regulatorio,
    financeiro.score_financeiro_trimestral,
    coalesce(vda.inadimplente, false) as inadimplente,
    coalesce(vda.saldo_devedor, 0) as saldo_devedor,
    coalesce(vda.valor_devido, 0) as valor_devido,
    coalesce(vda.valor_pago, 0) as valor_pago,
    coalesce(vda.situacao_cobranca, 'nao_informada') as situacao_cobranca,
    coalesce(glosa.taxa_glosa_calculada, 0) as taxa_glosa_calculada,
    coalesce(glosa.valor_glosa_total, 0) as valor_glosa_total,
    coalesce(glosa.valor_faturado_total, 0) as valor_faturado_total,
    case
        when coalesce(vda.inadimplente, false) then 5
        else 0
    end as penalizacao_vda,
    case
        when coalesce(glosa.taxa_glosa_calculada, 0) > {{ var('taxa_glosa_limite', 0.15) }} then 3
        else 0
    end as penalizacao_glosa,
    coalesce(vda.versao_dataset, 'vda_v1') as versao_vda,
    coalesce(glosa.versao_dataset, 'glosa_v1') as versao_glosa,
    financeiro.versao_financeiro
from base
left join score_core
    on base.operadora_id = score_core.operadora_id
    and base.competencia = score_core.competencia
left join score_regulatorio
    on base.operadora_id = score_regulatorio.operadora_id
    and base.competencia = score_regulatorio.competencia
left join vda
    on base.operadora_id = vda.operadora_id
    and base.competencia = vda.competencia
left join glosa
    on base.operadora_id = glosa.operadora_id
    and base.competencia = glosa.competencia
left join financeiro
    on base.operadora_id = financeiro.operadora_id
    and base.competencia = financeiro.competencia
