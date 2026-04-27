{{
    config(
        post_hook=[
            "{{ criar_indice_api(this, 'competencia') }}",
            "{{ criar_indice_api(this, 'registro_ans') }}",
            "{{ criar_indice_api(this, 'operadora_master_id') }}"
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
        uf,
        qt_beneficiarios,
        variacao_12m_pct,
        score_total,
        componente_core,
        componente_regulatorio,
        componente_financeiro,
        componente_rede,
        componente_estrutural,
        versao_metodologia
    from {{ ref('consumo_operadora_360') }}
),

documento as (
    select
        registro_ans,
        registro_ans_formato_valido,
        cnpj_normalizado,
        cnpj_tamanho_valido,
        cnpj_digito_valido,
        cnpj_is_sequencia_invalida,
        documento_quality_status,
        motivo_invalidade_documento
    from {{ ref('dq_operadora_documento') }}
),

mdm as (
    select
        operadora_master_id,
        registro_ans_canonico,
        status_mdm,
        confidence_score
    from {{ ref('mdm_operadora_master') }}
)

select
    mdm.operadora_master_id,
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
    documento.cnpj_tamanho_valido,
    documento.cnpj_digito_valido,
    documento.cnpj_is_sequencia_invalida,
    documento.documento_quality_status,
    documento.motivo_invalidade_documento,
    -- is_cnpj_estrutural_valido: CNPJ tem tamanho 14, dígito válido e não é sequência repetida
    (
        documento.cnpj_tamanho_valido
        and documento.cnpj_digito_valido
        and not documento.cnpj_is_sequencia_invalida
    ) as is_cnpj_estrutural_valido,
    mdm.status_mdm,
    mdm.confidence_score as mdm_confidence_score,
    -- quality_score_documental: 100 se VALIDO na sprint 28, 50 se sequencia invalida, 20 se formato invalido, 0 c.c.
    least(100, greatest(0,
        case documento.documento_quality_status
            when 'VALIDO' then 100
            when 'SEQUENCIA_INVALIDA' then 50
            when 'INVALIDO_FORMATO' then 20
            else 0
        end
    ))::numeric(5, 2) as quality_score_documental,
    -- quality_score_mdm: herdado do confidence_score do MDM (já entre 0-100)
    least(100, greatest(0, mdm.confidence_score))::numeric(5, 2) as quality_score_mdm,
    -- quality_score_publicacao: placeholder para métricas de freshness e completude futuras
    100::numeric(5, 2) as quality_score_publicacao,
    current_timestamp as dt_processamento
from produto_base as base
inner join documento
    on base.registro_ans = documento.registro_ans
inner join mdm
    on base.registro_ans = mdm.registro_ans_canonico
where documento.documento_quality_status = 'VALIDO'
  and documento.registro_ans_formato_valido
  and documento.cnpj_digito_valido
  and mdm.operadora_master_id is not null