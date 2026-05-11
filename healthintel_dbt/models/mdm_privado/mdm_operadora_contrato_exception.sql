{{
    config(
        tags=['mdm_privado', 'operadora', 'exception']
    )
}}

-- Exceção entre operadora pública (MDM) e contrato privado (tenant).
-- Ponte de auditoria: lista contratos privados que apontam para operadoras
-- não resolvidas ou divergentes do MDM público de operadora.

with contrato as (
    select
        contrato_master_id,
        tenant_id,
        operadora_master_id,
        registro_ans_canonico,
        cnpj_operadora_canonico,
        is_operadora_mdm_resolvida,
        has_excecao_bloqueante,
        mdm_status
    from {{ ref('mdm_contrato_master') }}
),

ex_nao_resolvida as (
    select
        contrato_master_id,
        tenant_id,
        operadora_master_id,
        'CONTRATO_OPERADORA_NAO_RESOLVIDA' as exception_type,
        'BLOCKING' as exception_severity,
        'Contrato privado não resolveu operadora_master_id no MDM público' as exception_message,
        true as is_blocking
    from contrato
    where is_operadora_mdm_resolvida = false
),

ex_cnpj as (
    select
        contrato_master_id,
        tenant_id,
        operadora_master_id,
        'CONTRATO_CNPJ_OPERADORA_DIVERGENTE_MDM' as exception_type,
        'BLOCKING' as exception_severity,
        'CNPJ do contrato diverge do CNPJ canônico do MDM público da operadora' as exception_message,
        true as is_blocking
    from contrato
    where is_operadora_mdm_resolvida = true
      and has_excecao_bloqueante = true
),

todas as (
    select * from ex_nao_resolvida
    union all
    select * from ex_cnpj
)

select
    contrato_master_id,
    tenant_id,
    operadora_master_id,
    exception_type,
    exception_severity,
    exception_message,
    is_blocking,
    null::timestamp as resolved_at,
    null::text      as resolved_by,
    null::text      as resolution_comment,
    current_timestamp as dt_processamento
from todas
