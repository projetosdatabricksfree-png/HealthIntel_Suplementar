{{
    config(
        post_hook=[
            "{{ criar_indice_api(this, 'competencia') }}",
            "{{ criar_indice_api(this, 'registro_ans') }}",
            "{{ criar_indice_api(this, 'uf') }}"
        ]
    )
}}

select
    operadora_master_id,
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
    versao_metodologia,
    cnpj_normalizado,
    registro_ans_formato_valido,
    cnpj_digito_valido,
    documento_quality_status,
    motivo_invalidade_documento,
    status_mdm,
    mdm_confidence_score,
    quality_score_documental
from {{ ref('consumo_premium_operadora_360_validado') }}
