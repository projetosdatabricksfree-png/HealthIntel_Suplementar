{{
    config(
        tags=['mdm_privado', 'subfatura', 'xref']
    )
}}

with origem as (
    select
        s.tenant_id,
        s.source_system,
        s.id_carga,
        s.numero_contrato_origem,
        s.numero_contrato_normalizado,
        s.codigo_subfatura_origem,
        s.codigo_subfatura_normalizado,
        sub.subfatura_master_id,
        sub.contrato_master_id
    from {{ ref('stg_cliente_subfatura') }} as s
    left join {{ ref('mdm_subfatura_master') }} as sub
        on s.tenant_id = sub.tenant_id
       and s.numero_contrato_normalizado = sub.numero_contrato_normalizado
       and s.codigo_subfatura_normalizado = sub.codigo_subfatura_normalizado
    where s.tenant_id is not null
      and s.numero_contrato_normalizado is not null
      and s.codigo_subfatura_normalizado is not null
)

select
    md5(concat_ws(
        '|',
        'xref_subfatura',
        tenant_id,
        coalesce(source_system, ''),
        coalesce(id_carga, '')
    )) as xref_subfatura_id,
    subfatura_master_id,
    contrato_master_id,
    tenant_id,
    coalesce(source_system, 'CLIENTE') as source_system,
    'stg_cliente_subfatura' as source_model,
    id_carga as source_key,
    codigo_subfatura_origem,
    codigo_subfatura_normalizado,
    numero_contrato_origem,
    numero_contrato_normalizado,
    false as is_primary_source,
    false as is_crosswalk_aprovado,
    current_timestamp as dt_processamento
from origem
