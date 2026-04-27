{{
    config(
        tags=['mdm_privado', 'prestador', 'exception']
    )
}}

-- Reservada para versão futura de contratos com prestador associado.
-- Hoje a entrada física de bruto_cliente.contrato não carrega prestador,
-- portanto retornamos linhas zero com estrutura válida (V9).

with vazio as (
    select
        null::text      as contrato_master_id,
        null::text      as prestador_master_id,
        null::text      as tenant_id,
        null::text      as exception_type,
        null::text      as exception_severity,
        null::text      as exception_message,
        null::boolean   as is_blocking,
        null::timestamp as resolved_at,
        null::text      as resolved_by,
        null::text      as resolution_comment,
        null::timestamp as dt_processamento
    where false
)

select
    contrato_master_id,
    tenant_id,
    prestador_master_id,
    exception_type,
    exception_severity,
    exception_message,
    is_blocking,
    resolved_at,
    resolved_by,
    resolution_comment,
    coalesce(dt_processamento, current_timestamp) as dt_processamento
from vazio
