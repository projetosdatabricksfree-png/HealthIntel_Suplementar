{{
    config(
        tags=['mdm_privado', 'contrato', 'xref']
    )
}}

with origem as (
    select
        s.tenant_id,
        s.source_system,
        s.id_carga,
        s.numero_contrato_origem,
        s.numero_contrato_normalizado,
        s.registro_ans_origem,
        s.cnpj_operadora_origem,
        c.contrato_master_id
    from {{ ref('stg_cliente_contrato') }} s
    left join {{ ref('mdm_contrato_master') }} c
        on c.tenant_id = s.tenant_id
       and c.numero_contrato_normalizado = s.numero_contrato_normalizado
    where s.tenant_id is not null
      and s.numero_contrato_normalizado is not null
)

select
    md5(concat_ws(
        '|',
        'xref_contrato',
        tenant_id,
        coalesce(source_system, ''),
        coalesce(id_carga, '')
    )) as xref_contrato_id,
    contrato_master_id,
    tenant_id,
    coalesce(source_system, 'CLIENTE') as source_system,
    'stg_cliente_contrato' as source_model,
    id_carga as source_key,
    numero_contrato_origem,
    numero_contrato_normalizado,
    registro_ans_origem,
    cnpj_operadora_origem,
    false as is_primary_source,
    false as is_crosswalk_aprovado,
    current_timestamp as dt_processamento
from origem
