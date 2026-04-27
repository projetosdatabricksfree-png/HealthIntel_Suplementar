{{
    config(
        post_hook=[
            "{{ criar_indice_api(this, 'competencia') }}",
            "{{ criar_indice_api(this, 'registro_ans') }}",
            "{{ criar_indice_api(this, 'uf') }}"
        ]
    )
}}

with produto_base as (
    select
        competencia,
        registro_ans,
        razao_social,
        nome_fantasia,
        modalidade,
        uf_sede as uf,
        qt_beneficiarios,
        variacao_12m_pct,
        score_total,
        componente_core,
        componente_regulatorio,
        componente_financeiro,
        componente_rede,
        componente_estrutural,
        versao_metodologia
    from {{ ref('mart_operadora_360') }}
),

documento as (
    select
        registro_ans,
        registro_ans_formato_valido,
        cnpj_normalizado,
        cnpj_digito_valido,
        documento_quality_status,
        motivo_invalidade_documento
    from {{ ref('dq_operadora_documento') }}
)

select
    base.competencia,
    base.registro_ans,
    base.razao_social,
    base.nome_fantasia,
    base.modalidade,
    base.uf,
    base.qt_beneficiarios,
    base.variacao_12m_pct,
    base.score_total,
    base.componente_core,
    base.componente_regulatorio,
    base.componente_financeiro,
    base.componente_rede,
    base.componente_estrutural,
    base.versao_metodologia,
    documento.cnpj_normalizado,
    documento.registro_ans_formato_valido,
    documento.cnpj_digito_valido,
    documento.documento_quality_status,
    documento.motivo_invalidade_documento,
    100::numeric(5, 2) as quality_score_documental
from produto_base as base
inner join documento
    on documento.registro_ans = base.registro_ans
where documento.documento_quality_status = 'VALIDO'
  and documento.registro_ans_formato_valido
  and documento.cnpj_digito_valido
