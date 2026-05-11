{{
    config(
        materialized='table',
        schema='consumo_premium_ans',
        tags=['consumo_premium', 'mdm_privado', 'exception'],
        post_hook=[
            "{{ criar_indice_api(this, 'tenant_id') }}",
            "{{ criar_indice_api(this, 'exception_type') }}"
        ]
    )
}}

-- Produto premium de inconsistência de contrato.
-- Exposição controlada e separada dos produtos principais.
-- Publica apenas exceções bloqueantes para análise de qualidade.

select
    contrato_master_id,
    tenant_id,
    exception_type,
    exception_severity,
    exception_message,
    is_blocking,
    resolved_at,
    resolved_by,
    resolution_comment,
    -- quality_score: 0 para exceções bloqueantes, indicando necessidade de correção
    0::numeric(5, 2) as quality_score_contrato,
    0::numeric(5, 2) as quality_score_publicacao,
    dt_processamento
from {{ ref('mdm_contrato_exception') }}
where is_blocking = true
