{{
    config(
        post_hook=[
            "{{ criar_indice_api(this, 'registro_ans') }}",
            "{{ criar_indice_api(this, 'registro_ans, competencia') }}"
        ],
        tags=['financeiro_v2']
    )
}}

with vda as (
    select
        operadora_id,
        registro_ans,
        competencia,
        valor_devido,
        valor_pago,
        saldo_devedor,
        situacao_cobranca,
        data_vencimento,
        inadimplente,
        meses_inadimplente_consecutivos,
        versao_dataset
    from {{ ref('fat_vda_operadora_mensal') }}
),
glosa as (
    select
        operadora_id,
        registro_ans,
        competencia,
        sum(coalesce(qt_glosa, 0)) as qt_glosa,
        sum(coalesce(valor_glosa, 0)) as valor_glosa,
        sum(coalesce(valor_faturado, 0)) as valor_faturado,
        max(taxa_glosa_calculada) as taxa_glosa_calculada,
        max(severidade_glosa) as severidade_glosa,
        string_agg(distinct tipo_glosa, ', ' order by tipo_glosa) as tipos_glosa,
        max(versao_dataset) as versao_dataset
    from {{ ref('fat_glosa_operadora_mensal') }}
    group by 1, 2, 3
)

select
    d.operadora_id,
    d.registro_ans,
    d.nome,
    d.nome_fantasia,
    d.modalidade,
    d.uf_sede,
    vda.competencia,
    {{ competencia_para_trimestre('vda.competencia') }} as trimestre_referencia,
    financeiro.ativo_total,
    financeiro.passivo_total,
    financeiro.patrimonio_liquido,
    financeiro.receita_total,
    financeiro.despesa_total,
    financeiro.resultado_periodo,
    financeiro.resultado_operacional,
    financeiro.provisao_tecnica,
    financeiro.margem_solvencia_calculada,
    financeiro.sinistro_total,
    financeiro.contraprestacao_total,
    financeiro.sinistralidade_bruta,
    financeiro.ressarcimento_sus,
    financeiro.evento_indenizavel,
    financeiro.sinistralidade_liquida,
    financeiro.taxa_sinistralidade_calculada,
    financeiro.indice_sinistralidade,
    financeiro.margem_liquida_pct,
    financeiro.cobertura_provisao,
    financeiro.resultado_operacional_bruto,
    financeiro.score_financeiro_base,
    financeiro.rating_financeiro,
    vda.valor_devido as vda_valor_devido,
    vda.valor_pago as vda_valor_pago,
    vda.saldo_devedor as vda_saldo_devedor,
    vda.situacao_cobranca as vda_situacao_cobranca,
    vda.inadimplente as vda_inadimplente,
    vda.meses_inadimplente_consecutivos as vda_meses_inadimplente_consecutivos,
    vda.data_vencimento as vda_data_vencimento,
    glosa.qt_glosa,
    glosa.valor_glosa,
    glosa.valor_faturado,
    glosa.taxa_glosa_calculada as glosa_taxa_glosa_calculada,
    glosa.severidade_glosa,
    glosa.tipos_glosa,
    coalesce(vda.versao_dataset, glosa.versao_dataset, financeiro.versao_financeira) as versao_dataset
from vda
inner join {{ ref('dim_operadora_atual') }} as d
    on d.registro_ans = vda.registro_ans
left join glosa
    on glosa.operadora_id = d.operadora_id
    and glosa.competencia = vda.competencia
left join lateral (
    select
        financeiro_base.ativo_total,
        financeiro_base.passivo_total,
        financeiro_base.patrimonio_liquido,
        financeiro_base.receita_total,
        financeiro_base.despesa_total,
        financeiro_base.resultado_periodo,
        financeiro_base.resultado_operacional,
        financeiro_base.provisao_tecnica,
        financeiro_base.margem_solvencia_calculada,
        financeiro_base.sinistro_total,
        financeiro_base.contraprestacao_total,
        financeiro_base.sinistralidade_bruta,
        financeiro_base.ressarcimento_sus,
        financeiro_base.evento_indenizavel,
        financeiro_base.sinistralidade_liquida,
        financeiro_base.taxa_sinistralidade_calculada,
        financeiro_base.indice_sinistralidade,
        financeiro_base.margem_liquida_pct,
        financeiro_base.cobertura_provisao,
        financeiro_base.resultado_operacional_bruto,
        financeiro_base.score_financeiro_base,
        financeiro_base.rating_financeiro,
        financeiro_base.versao_financeira
    from {{ ref('fat_financeiro_operadora_trimestral') }} as financeiro_base
    where financeiro_base.operadora_id = d.operadora_id
      and financeiro_base.trimestre <= {{ competencia_para_trimestre('vda.competencia') }}
    order by financeiro_base.trimestre desc
    limit 1
) as financeiro on true
