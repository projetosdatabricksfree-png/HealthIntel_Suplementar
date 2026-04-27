{{
    config(
        tags=['mdm_privado', 'contrato', 'exception']
    )
}}

with contrato as (
    select
        contrato_master_id,
        tenant_id,
        numero_contrato_normalizado,
        registro_ans_canonico,
        cnpj_operadora_canonico,
        is_operadora_mdm_resolvida,
        is_cnpj_operadora_estrutural_valido,
        has_excecao_bloqueante,
        mdm_status,
        mdm_confidence_score
    from {{ ref('mdm_contrato_master') }}
),

duplicidade as (
    select
        tenant_id,
        numero_contrato_normalizado,
        count(*) as ocorrencias
    from contrato
    group by tenant_id, numero_contrato_normalizado
    having count(*) > 1
),

ex_tenant as (
    select
        contrato_master_id,
        tenant_id,
        'TENANT_AUSENTE' as exception_type,
        'BLOCKING' as exception_severity,
        'Contrato sem tenant identificável' as exception_message,
        true as is_blocking
    from contrato
    where tenant_id is null
),

ex_sem_operadora as (
    select
        contrato_master_id,
        tenant_id,
        'CONTRATO_SEM_OPERADORA_MDM' as exception_type,
        'BLOCKING' as exception_severity,
        'Contrato não resolveu operadora_master_id no MDM público' as exception_message,
        true as is_blocking
    from contrato
    where is_operadora_mdm_resolvida = false
),

ex_cnpj_divergente as (
    select
        contrato_master_id,
        tenant_id,
        'CONTRATO_CNPJ_OPERADORA_DIVERGENTE_MDM' as exception_type,
        'BLOCKING' as exception_severity,
        'CNPJ informado no contrato diverge do CNPJ canônico do MDM público' as exception_message,
        true as is_blocking
    from contrato
    where has_excecao_bloqueante = true
      and is_operadora_mdm_resolvida = true
),

ex_duplicado as (
    select
        c.contrato_master_id,
        c.tenant_id,
        'CONTRATO_DUPLICADO_TENANT' as exception_type,
        'BLOCKING' as exception_severity,
        'Mesmo número de contrato duplicado no tenant sem crosswalk aprovado' as exception_message,
        true as is_blocking
    from contrato c
    inner join duplicidade d using (tenant_id, numero_contrato_normalizado)
),

todas as (
    select * from ex_tenant
    union all select * from ex_sem_operadora
    union all select * from ex_cnpj_divergente
    union all select * from ex_duplicado
)

select
    contrato_master_id,
    tenant_id,
    exception_type,
    exception_severity,
    exception_message,
    is_blocking,
    null::timestamp as resolved_at,
    null::text      as resolved_by,
    null::text      as resolution_comment,
    current_timestamp as dt_processamento
from todas
