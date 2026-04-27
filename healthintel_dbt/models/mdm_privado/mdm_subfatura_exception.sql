{{
    config(
        tags=['mdm_privado', 'subfatura', 'exception']
    )
}}

with subfatura as (
    select
        subfatura_master_id,
        contrato_master_id,
        tenant_id,
        numero_contrato_normalizado,
        codigo_subfatura_normalizado,
        competencia,
        is_contrato_resolvido,
        has_excecao_bloqueante,
        mdm_status
    from {{ ref('mdm_subfatura_master') }}
),

dup_competencia as (
    select
        tenant_id,
        contrato_master_id,
        codigo_subfatura_normalizado,
        competencia,
        count(*) as ocorrencias
    from subfatura
    where contrato_master_id is not null
    group by tenant_id, contrato_master_id, codigo_subfatura_normalizado, competencia
    having count(*) > 1
),

ex_tenant as (
    select
        subfatura_master_id,
        contrato_master_id,
        tenant_id,
        'TENANT_AUSENTE' as exception_type,
        'BLOCKING' as exception_severity,
        'Subfatura sem tenant identificável' as exception_message,
        true as is_blocking
    from subfatura
    where tenant_id is null
),

ex_sem_contrato as (
    select
        subfatura_master_id,
        contrato_master_id,
        tenant_id,
        'SUBFATURA_SEM_CONTRATO' as exception_type,
        'BLOCKING' as exception_severity,
        'Subfatura não resolveu contrato_master_id' as exception_message,
        true as is_blocking
    from subfatura
    where is_contrato_resolvido = false
),

ex_dup as (
    select
        s.subfatura_master_id,
        s.contrato_master_id,
        s.tenant_id,
        'SUBFATURA_DUPLICADA_COMPETENCIA' as exception_type,
        'WARNING' as exception_severity,
        'Duplicidade de subfatura por contrato + código + competência' as exception_message,
        false as is_blocking
    from subfatura s
    inner join dup_competencia d
        on d.tenant_id = s.tenant_id
       and d.contrato_master_id = s.contrato_master_id
       and d.codigo_subfatura_normalizado = s.codigo_subfatura_normalizado
       and d.competencia is not distinct from s.competencia
),

todas as (
    select * from ex_tenant
    union all select * from ex_sem_contrato
    union all select * from ex_dup
)

select
    subfatura_master_id,
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
